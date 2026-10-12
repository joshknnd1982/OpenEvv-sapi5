# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Josh Kennedy
"""Tests of the pack loader: inheritance as DESIGN.md 6.3 says it, the stops it promises, and the
round trip of today's files. Run:  python engine/packs/test_packs.py   (Python 3.10 needs tomli)
"""
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import packfmt as F  # noqa: E402
import overrides as O  # noqa: E402
import packlib as L  # noqa: E402

PARENT = '''
[pack]
tag = "pa"
name = "Parent"
kind = "language"
format = 1
[engine]
reader = "espeak:xx/pa"
template = "dedx"
realization = "legacy"
[files]
eol = "lf"
[ini.Language]
Tag = "pa"
Name = "Parent"
Template = "dedx"
Order = "300"
[ini.Frontend]
Voice = "xx/pa"
Map = "phonemes.map"
Sounds = "sounds.map"
[ini.Voice1]
Name = "Adult Male 1"
Params = "0,50,65,30,0,0,50,92"
[sounds]
line = [
  { kind = "comment", key = "c1", text = "# head" },
  { kind = "directive", name = "template", value = "dedx" },
  { kind = "blank", key = "b1" },
  { kind = "sound", id = "s1", keys = { f2 = 88 }, note = "a" },
  { kind = "sound", id = "s2", keys = { dur = 40 }, note = "b" },
  { kind = "map", name = "a", to = "a=s1" },
  { kind = "map", name = "b", to = "b=s2" },
]
[phonemes]
line = [
  { kind = "map", name = "@pa:a", to = "A", note = "a" },
]
[sample]
text = "one"
'''

CHILD = '''
[pack]
tag = "ch"
name = "Child"
kind = "dialect"
extends = "pa"
format = 1
[engine]
reader = "espeak:xx/ch"
[ini.Language]
Tag = "ch"
Name = "Child"
Order = "301"
[ini.Frontend]
Voice = "xx/ch"
[sounds]
remove = ["s2", "b"]
line = [
  { kind = "sound", id = "s1", keys = { f2 = 90, f3 = 70 }, note = "a" },
  { kind = "sound", id = "s3", keys = { vot = 30 }, note = "k", after = "s1" },
  { kind = "map", name = "k", to = "k=s3" },
]
[sample]
text = "two"
'''


def write(root, tag, text):
    os.makedirs(os.path.join(root, tag), exist_ok=True)
    with open(os.path.join(root, tag, "pack.toml"), "w", encoding="utf-8") as f:
        f.write(text)


class Inheritance(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        write(self.root, "pa", PARENT)
        write(self.root, "ch", CHILD)

    def tearDown(self):
        shutil.rmtree(self.root)

    def build(self, tag="ch"):
        flat, origin = L.resolve(tag, self.root)
        return flat, origin, L.compile_pack(flat)

    def test_tables_merge_key_by_key_and_plain_values_replace(self):
        flat, origin, _ = self.build()
        self.assertEqual(flat["ini"]["Language"], {"Tag": "ch", "Name": "Child", "Template": "dedx", "Order": "301"})
        self.assertEqual(flat["ini"]["Voice1"]["Params"], "0,50,65,30,0,0,50,92")  # inherited, untouched
        self.assertEqual(flat["sample"]["text"], "two")
        self.assertEqual(origin["ini.Language.Template"], "pa")
        self.assertEqual(origin["ini.Language.Name"], "ch")

    def test_lines_replace_in_place_insert_after_and_remove(self):
        flat, origin, files = self.build()
        keys = [F.line_key(x) for x in flat["sounds"]["line"]]
        self.assertEqual(keys, ["c1", "template", "b1", "s1", "s3", "a", "k"])
        self.assertEqual(flat["sounds"]["line"][3]["keys"], {"f2": "90", "f3": "70"})
        self.assertEqual(origin["sounds.s1"], "ch")
        self.assertEqual(origin["sounds.template"] if "sounds.template" in origin else "pa", "pa")
        text = files["sounds.map"].decode()
        self.assertIn("sound s3 vot=30", text)
        self.assertNotIn("sound s2", text)

    def test_the_parent_is_not_changed_by_its_child(self):
        self.build()
        flat, _, _ = self.build("pa")
        self.assertEqual(flat["sounds"]["line"][3]["keys"], {"f2": "88"})

    def test_reset_drops_everything_inherited(self):
        write(self.root, "ch", CHILD.replace('remove = ["s2", "b"]', "reset = true\nremove = []").replace(
            'after = "s1"', ''))
        flat, _, _ = self.build()
        self.assertEqual([F.line_key(x) for x in flat["sounds"]["line"]], ["s1", "s3", "k"])

    def test_remove_dotted_key(self):
        write(self.root, "ch", CHILD + '\n[ini.Voice1]\nName = "x"\n')
        text = CHILD.replace("[pack]", 'remove = ["ini.Voice1.Params"]\n[pack]', 1)
        write(self.root, "ch", text)
        flat, _, _ = self.build()
        self.assertNotIn("Params", flat["ini"]["Voice1"])

    def test_cycle_missing_parent_and_unknown_things_stop_the_build(self):
        write(self.root, "pa", PARENT.replace('kind = "language"', 'kind = "language"\nextends = "ch"'))
        with self.assertRaisesRegex(L.PackError, "cycle"):
            L.resolve("ch", self.root)
        write(self.root, "pa", PARENT)
        write(self.root, "ch", CHILD.replace('extends = "pa"', 'extends = "zz"'))
        with self.assertRaisesRegex(L.PackError, "no pack.toml"):
            L.resolve("ch", self.root)
        write(self.root, "ch", CHILD.replace("[files]", "[files]"))
        for bad, rx in (
            (CHILD.replace('format = 1', 'format = 1\ncolour = "red"'), "unknown"),
            (CHILD.replace('remove = ["s2", "b"]', 'remove = ["s9"]'), "no such line"),
            (CHILD.replace('after = "s1"', 'after = "s9"'), "not there"),
            (CHILD.replace('kind = "dialect"', 'kind = "tongue"'), "kind"),
            (CHILD.replace('tag = "ch"\nname', 'tag = "zz"\nname'), "folder says"),
            (CHILD.replace('{ kind = "map", name = "k", to = "k=s3" }', '{ kind = "map", name = "k", to = "k", colour = 1 }'), "unknown fields"),
            (CHILD.replace('Voice = "xx/ch"', 'Voice = 7'), "string"),
        ):
            write(self.root, "ch", bad)
            with self.assertRaisesRegex(L.PackError, rx):
                L.resolve("ch", self.root)

    def test_a_remove_of_a_key_the_parent_lacks_stops_the_build(self):
        write(self.root, "ch", CHILD.replace("[pack]", 'remove = ["ini.Voice9.Name"]\n[pack]', 1))
        with self.assertRaisesRegex(L.PackError, "no such key"):
            L.resolve("ch", self.root)

    def test_disagreeing_files_stop_the_build(self):
        write(self.root, "ch", CHILD.replace('Voice = "xx/ch"', 'Voice = "xx/other"'))
        with self.assertRaisesRegex(L.PackError, "reader"):
            L.compile_pack(L.resolve("ch", self.root)[0])
        write(self.root, "ch", CHILD.replace('reader = "espeak:xx/ch"', 'reader = "espeak:xx/ch"\ntemplate = "itix"'))
        with self.assertRaisesRegex(L.PackError, "template"):
            L.compile_pack(L.resolve("ch", self.root)[0])

    def test_two_lines_of_one_key_stop_the_build(self):
        write(self.root, "ch", CHILD.replace('{ kind = "map", name = "k", to = "k=s3" },',
                                              '{ kind = "map", name = "k", to = "k=s3" },\n  { kind = "map", name = "k", to = "k" },'))
        with self.assertRaisesRegex(L.PackError, "two lines"):
            L.resolve("ch", self.root)


OVERRIDE = '''
[[override]]
sound = "a"
phonemes = ["a"]
state = "%s"
recordings = ["x/u1"]
[override.formants.f1]
v = %s
tag = "measured"
ref = "hillenbrand1995"
n = 12
speakers = 1
evidence = "measured/x.json"
[override.formants.f2]
v = 1300.0
tag = "literature"
ref = "hillenbrand1995"
'''


class Overrides(unittest.TestCase):
    """[[override]] (overrides.py): inherited field by field, never realised while proposed."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        write(self.root, "pa", PARENT + OVERRIDE % ("proposed", "700.0"))
        write(self.root, "ch", CHILD + OVERRIDE.split("[override.formants.f2]")[0] % ("proposed", "650.0"))

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_a_child_changes_only_the_fields_it_names(self):
        flat, origin = L.resolve("ch", self.root)
        f = flat["override"]["a"]["formants"]
        self.assertEqual((f["f1"]["v"], f["f2"]["v"]), (650.0, 1300.0))
        self.assertEqual(origin["override.a"], "ch")
        # each value knows its own pack (the validator finds its evidence file there)
        self.assertEqual((origin["override.a.formants.f1"], origin["override.a.formants.f2"]), ("ch", "pa"))

    def test_proposed_overrides_reach_only_a_scratch_build(self):
        flat, _ = L.resolve("pa", self.root)
        plain = L.compile_pack(flat)["sounds.map"].decode()
        self.assertEqual(plain, L.compile_pack(dict(flat, override={}))["sounds.map"].decode())
        made = L.compile_pack(flat, include_proposed=True)["sounds.map"].decode()
        own = O.chassis("dedx")["a"]["f"]
        line = [x for x in made.splitlines() if x.startswith("sound s3 ")][0]
        self.assertIn("f1=%d" % round(70000.0 / own[0]), line)
        self.assertIn("f2=%d" % round(130000.0 / own[1]), line)
        self.assertIn("a=s3", made)
        self.assertIn("sound s1 f2=88", made)  # the old sound stays for whatever else uses it

    def test_applied_overrides_are_built(self):
        write(self.root, "pa", PARENT + OVERRIDE % ("applied", "700.0"))
        flat, _ = L.resolve("pa", self.root)
        self.assertIn("a=s3", L.compile_pack(flat)["sounds.map"].decode())

    def test_a_value_without_provenance_or_recordings_stops_the_build(self):
        write(self.root, "pa", PARENT + (OVERRIDE % ("proposed", "700.0")).replace('tag = "literature"\n', ""))
        self.assertRaises(L.PackError, L.resolve, "pa", self.root)
        write(self.root, "pa", PARENT + (OVERRIDE % ("proposed", "700.0")).replace('recordings = ["x/u1"]\n', ""))
        self.assertRaises(L.PackError, L.resolve, "pa", self.root)

    def test_a_ratio_out_of_range_stops_the_build(self):
        write(self.root, "pa", PARENT + OVERRIDE % ("applied", "5000.0"))
        flat, _ = L.resolve("pa", self.root)
        self.assertRaises(L.PackError, L.compile_pack, flat)


MASTER_LINES = '''  { kind = "map", name = "@mp:a", to = "a=s1", note = "a" },
  { kind = "map", name = "@mp:a2", to = "a=s2", note = "a" },
  { kind = "map", name = "@mp:k", to = "k", note = "k" },
  { kind = "map", name = "@mp:x", to = "x=s2", note = "x" },
  { kind = "map", name = "@mp:ts", to = "T", note = "ts" },
  { kind = "map", name = "ː", to = "-" },
  { kind = "map", name = "a", to = "a=s1" },'''

MASTER_BLOCK = '''
[master.ipa]
"@mp:a" = "a"
"@mp:a2" = "a̪"
"@mp:k" = "kʼ"
"@mp:x" = "x"
"@mp:ts" = "tsʰ"
[master.kind]
"@mp:a" = "v"
"@mp:a2" = "v"
"@mp:k" = "c"
"@mp:x" = "c"
"@mp:ts" = "c"
[master.fallback]
"@mp:x" = "a test fault"
'''

MASTER = PARENT.replace('tag = "pa"', 'tag = "mp"').replace('Tag = "pa"', 'Tag = "mp"').replace(
    'reader = "espeak:xx/pa"', 'reader = "espeak:xx/mp"').replace('Voice = "xx/pa"', 'Voice = "xx/mp"').replace(
    'realization = "legacy"', 'realization = "master"').replace(
    '  { kind = "map", name = "a", to = "a=s1" },\n  { kind = "map", name = "b", to = "b=s2" },',
    MASTER_LINES) + MASTER_BLOCK


class Master(unittest.TestCase):
    """realization = "master" (master.py, to_master.py): the IPA master table's sounds, by rule."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        write(self.root, "mp", MASTER)

    def tearDown(self):
        shutil.rmtree(self.root)

    def build(self):
        import master as M
        M._memo.clear()
        flat, _ = L.resolve("mp", self.root)
        return L.compile_pack(flat)["sounds.map"].decode()

    def lines(self, text):
        return {w[0]: w[1] for w in (x.split(None, 1) for x in text.splitlines()) if len(w) == 2}

    def sound(self, text, sid):
        return [x for x in text.splitlines() if x.startswith("sound %s " % sid)][0]

    def test_a_master_pack_built_twice_is_identical(self):
        self.assertEqual(self.build(), self.build())

    def test_every_phoneme_is_said_by_the_table_and_none_is_silent(self):
        text = self.build()
        got = self.lines(text)
        for k in ("@mp:a", "@mp:k", "@mp:ts", "a"):
            to = got[k].split("#")[0].split()
            self.assertTrue(to and to != ["-"], k)
            self.assertTrue(all(not w.endswith("=s1") and not w.endswith("=s2") for w in to), (k, to))
        # the ejective, and the aspirated affricate on the template's own affricate, from the table's marks
        self.assertRegex(text, r"(?m)^sound m\d+ .*ej=\d+.*# kʼ: U\+006B\+U\+02BC; values ")
        self.assertRegex(got["@mp:ts"], r"^T=m\d+")
        self.assertRegex(self.sound(text, got["@mp:ts"].split("=")[1].split()[0]), r"vot=\d+")
        # a mark alone is said as nothing, as before
        self.assertEqual(got["ː"].strip(), "-")
        # every sound line names its table entries and its values' provenance
        for x in text.splitlines():
            if x.startswith("sound m"):
                self.assertRegex(x, r"# .*: U\+[0-9A-F]{4}.*; values (literature|derived|measured|estimated|created|approximate) \d")

    def test_a_fault_keeps_its_legacy_line_marked(self):
        text = self.build()
        got = self.lines(text)
        self.assertTrue(got["@mp:x"].startswith("x=s2"))
        self.assertIn("[legacy-fallback: a test fault]", got["@mp:x"])
        self.assertIn("sound s2 dur=40", text)   # the legacy sound it names is kept

    def test_two_phonemes_the_table_says_alike_are_kept_apart(self):
        got = self.lines(self.build())
        # a̪: the dental mark means nothing on a vowel, so the table says it as a; its legacy line differs
        self.assertTrue(got["@mp:a2"].startswith("a=s2"), got["@mp:a2"])
        self.assertIn("[kept-apart: kept apart from @mp:a", got["@mp:a2"])

    def test_an_override_still_applies_on_top(self):
        write(self.root, "mp", MASTER + (OVERRIDE % ("applied", "700.0")).replace('phonemes = ["a"]', 'phonemes = ["@mp:a"]'))
        text = self.build()
        got = self.lines(text)
        phone, sid = got["@mp:a"].split()[0].split("=")
        own = O.chassis("dedx")[phone]["f"]
        line = self.sound(text, sid)
        self.assertIn("f1=%d" % round(70000.0 / own[0]), line)
        self.assertIn("(override, applied)", line)

    def test_the_check_passes_a_good_pack_and_fails_a_silent_phoneme(self):
        import to_master as TM
        self.assertEqual(TM.check(self.root), 0)
        write(self.root, "mp", MASTER.replace('name = "@mp:x", to = "x=s2"', 'name = "@mp:x", to = "-"'))
        self.assertEqual(TM.check(self.root), 1)

    def test_a_legacy_pack_is_not_touched_and_native_and_template_packs_are_refused(self):
        import to_master as TM
        with open(L.pack_path("af"), "rb") as f:
            before = f.read()
        tables = TM.dump_tables()
        # a real write, into a scratch copy: packs/af is left as it was, the copy is switched
        rep = TM.convert("af", tables, {}, {}, "2026-01-01", out=self.root)
        self.assertGreater(rep["counts"].get("table", 0) + rep["counts"].get("composed", 0), 50)
        with open(L.pack_path("af"), "rb") as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(L.resolve("af", self.root)[0]["engine"]["realization"], "master")
        import build_packs
        self.assertEqual(build_packs.check(["af"]), 0)
        for tag, what in (("enus", "native"), ("dedx", "template")):
            with self.assertRaisesRegex(L.PackError, what):
                TM.convert(tag, tables, {}, {}, "2026-01-01", dry=True)

class Templates(unittest.TestCase):
    """The table on every template, not only dedx (Phase 12, D97: Q53's carriers, the voicing rule)."""
    TEMPLATES = ("dedx", "engx", "enux", "esex", "esux", "frfx", "itix")

    def setUp(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "ipa"))
        import adapter as A
        import table as T
        self.A, self.t = A, T.load()

    def test_no_consonant_is_carried_by_a_vowel_or_by_a_phone_the_template_lacks(self):
        # a phone's name is the module's own: `x` is a velar fricative on dedx and ə on engx (Q53)
        for tm in self.TEMPLATES:
            phones, measured = self.A.module_phones(tm), self.A.chassis(tm)
            for sid, e in self.t.sounds.items():
                if e.get("kind") != "base" or e["features"].get("class") != "consonant":
                    continue
                car = self.A.realize(self.t, sid, tm)["carrier"]
                if car.startswith("<"):
                    continue
                self.assertIn(car, measured, (tm, e["ipa"], car))
                self.assertNotEqual((phones.get(car) or {}).get("class"), "vowel", (tm, e["ipa"], car))

    def test_a_voiceless_and_a_voiced_fricative_are_two_sounds_on_every_template(self):
        by = self.t.by_ipa()
        for tm in self.TEMPLATES:
            for a, b in (("χ", "ʁ"), ("x", "ɣ"), ("ç", "ʝ"), ("s", "z"), ("f", "v")):
                ra, rb = (self.A.realize(self.t, by[c], tm) for c in (a, b))
                self.assertNotEqual((ra["carrier"], ra["keys"]), (rb["carrier"], rb["keys"]), (tm, a, b))

    def test_a_template_with_its_own_phone_for_the_letter_says_it_with_it_and_lays_no_construction_on_it(self):
        # ʝ is dedx's ç (X) voiced by an engine key; esex has its own ʝ (Y)
        r = self.A.realize(self.t, self.t.by_ipa()["ʝ"], "esex")
        self.assertEqual(r["carrier"], "Y")
        self.assertNotIn("voi", r["keys"])
        self.assertEqual(self.A.realize(self.t, self.t.by_ipa()["ʝ"], "dedx")["carrier"], "X")

    def test_a_choice_the_table_states_for_a_template_is_kept(self):
        # r on itix: its own trill measured short of the table's targets, so the table names l there
        # (carrier_on, Phase 12) and the trill is the layer's, as on dedx
        r = self.A.realize(self.t, self.t.by_ipa()["r"], "itix")
        self.assertEqual(r["carrier"], "l")
        self.assertIn("trate", r["keys"])


class RoundTrip(unittest.TestCase):
    def test_each_line_kind_survives_in_both_map_formats(self):
        sounds = ("# a comment\n\ntemplate dedx\naccent f0=own range=90\nwhwords first wie wat\nsays C t S\n"
                  "sound s1 tap=1 tapms=24 hold=60 f1=122 f2=111 f3=77 # ɾ\n"
                  "sound s2 f2=88                           # βχ\n"
                  "a                a=s1\n@af:@            @               # ə\n")
        for fmt in ("sounds", "phonemes"):
            rec, eol = F.parse_map(sounds, fmt)
            self.assertEqual(F.render_map(rec, eol, fmt), sounds, fmt)

    def test_a_line_that_will_not_round_trip_is_kept_as_it_is(self):
        text = "a   b   c   d  #  odd\n"
        rec, eol = F.parse_map(text, "sounds")
        self.assertEqual(F.render_map(rec, eol, "sounds"), text)

    def test_ini_round_trip_with_crlf(self):
        text = "; head\r\n\r\n[Language]\r\nTag=x\r\n; note\r\nName=X\r\n\r\n[Voice1]\r\nName=A\r\n\r\n"
        ini, eol = F.parse_ini(text)
        self.assertEqual(F.render_ini(ini, eol), text)


class Shipped(unittest.TestCase):
    """The packs in packs/ against the folders in languages/ (build_packs.py check says the same, with counts)."""

    def test_every_pack_builds_to_the_folder_it_came_from(self):
        import build_packs
        self.assertEqual(build_packs.check([]), 0)


class Teeth(unittest.TestCase):
    """The check must see a change: break a copy of a shipped pack on purpose and it must differ."""

    def test_a_changed_value_in_a_copy_is_seen(self):
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.join(ROOT, "packs", "af"), os.path.join(tmp, "af"))
            path = os.path.join(tmp, "af", "pack.toml")
            text = open(path, encoding="utf-8").read()
            self.assertIn('Order = "201"', text)
            open(path, "w", encoding="utf-8", newline="\n").write(text.replace('Order = "201"', 'Order = "999"'))
            flat, _ = L.resolve("af", tmp)
            made = L.compile_pack(flat)["language.ini"]
            had = open(os.path.join(ROOT, "languages", "af", "language.ini"), "rb").read()
            self.assertNotEqual(made, had)
            self.assertEqual(made.replace(b"999", b"201").replace(b"\r\n", b"\n"), had.replace(b"\r\n", b"\n"))
        finally:
            shutil.rmtree(tmp)

    def test_a_child_that_inherits_is_the_parent_built_over(self):
        for child, parent in (("ru-cl", "ru"), ("ps-x-yusufzai", "ps"), ("mn-f", "mn")):
            c, origin = L.resolve(child)
            p, _ = L.resolve(parent)
            self.assertEqual(c["pack"]["extends"], parent)
            same = sum(1 for k, v in origin.items() if v == parent)
            self.assertGreater(same, 100, child)  # most of it is the parent's own
            self.assertNotEqual(c["ini"]["Language"]["Tag"], p["ini"]["Language"]["Tag"])


class ExtraFolder(unittest.TestCase):
    """EVV_PACKS_EXTRA: a test pack outside packs/ may extend a shipped pack, never replaces one, and
    is not listed (so `build_packs.py check` does not see it)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = os.environ.get("EVV_PACKS_EXTRA")
        os.environ["EVV_PACKS_EXTRA"] = self.tmp

    def tearDown(self):
        if self.old is None:
            os.environ.pop("EVV_PACKS_EXTRA", None)
        else:
            os.environ["EVV_PACKS_EXTRA"] = self.old
        shutil.rmtree(self.tmp)

    def test_a_pack_found_only_there_extends_a_shipped_one(self):
        shutil.copytree(os.path.join(ROOT, "packs", "mn-f"), os.path.join(self.tmp, "mn-x-t"))
        path = os.path.join(self.tmp, "mn-x-t", "pack.toml")
        text = open(path, encoding="utf-8").read().replace('tag = "mn-f"', 'tag = "mn-x-t"')
        open(path, "w", encoding="utf-8", newline="\n").write(text)
        self.assertEqual(L.pack_path("mn-x-t"), path)
        self.assertEqual([d["pack"]["tag"] for d in L.chain_of("mn-x-t")], ["mn", "mn-x-t"])
        self.assertNotIn("mn-x-t", L.list_tags())

    def test_packs_of_packs_wins(self):
        os.makedirs(os.path.join(self.tmp, "af"))
        open(os.path.join(self.tmp, "af", "pack.toml"), "w").write("broken")
        self.assertEqual(L.pack_path("af"), os.path.join(L.packs_dir(), "af", "pack.toml"))
        L.read_pack("af")


if __name__ == "__main__":
    unittest.main(verbosity=2)
