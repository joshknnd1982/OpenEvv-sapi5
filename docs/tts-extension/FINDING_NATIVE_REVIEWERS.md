# Finding native reviewers

A practical note for the human (playbook Phase 7, step 6). Claude contacts no one on your behalf; this
says where to look and what to send. Native review comes after Phase 9 (D82): nothing waits for it.

## What a reviewer is asked to do

Open one packet (`docs/tts-extension/review_packets/<tag>/index.html`, or the folder zipped), listen
for about 20 to 40 minutes, and fill in `feedback.toml` with any text editor. No phonetics is needed.
The checklist (`CHECKLIST.md` in the packet) is written for a non-specialist. A review is recorded
only with the reviewer's name (or a stable pseudonym), the date, their native variety and their
consent to be named (`engine/review/ingest_feedback.py`).

## Who makes a good reviewer

- Someone who **grew up speaking the variety** and still speaks it daily. For a dialect or accent,
  where they grew up matters more than where they live now: the packet says which region and speaker
  group the pack aims at, and the reviewer should match it.
- Two or three reviewers per language are far better than one: people disagree, and one person's
  "that is wrong" may be their own local usage. The ingest records each review separately.
- A linguist or a language teacher who is also a native speaker is ideal for the single-sound items,
  but not needed for the words and sentences.

## Where to look

1. **University linguistics departments and phonetics labs** in the region of the variety. Graduate
   students often take on small, clearly bounded listening tasks, sometimes for course credit or a
   small fee. Write to the department's general address and ask that it be passed on; say exactly how
   long it takes and that it is unpaid or paid.
2. **Language and dialect societies, heritage and cultural organisations** for the language or the
   region (for a minority language these are often the best-connected people there are).
3. **Online communities** of speakers: the language's subreddit or regional subreddit, Discord servers
   for learners and speakers, language-exchange apps, and the communities of open speech projects
   (Mozilla Common Voice has a community per language, people who already volunteer to help speech
   technology; the eSpeak NG project's issue tracker has contributors for many of its languages).
4. **Wikipedia and Wiktionary editors** of that language's edition: many are careful native speakers
   with an interest in how the language is written and said.
5. **Paid panels** (participant-recruitment platforms used by researchers) when volunteers are scarce:
   you can filter by first language and country. Pay at least the platform's fair-pay guidance.
6. **People you know**: a colleague, a neighbour, a friend of a friend. A careful amateur is better
   than no review.

## What to send (a short message you can adapt)

> I am improving a free, open-source text-to-speech voice for **<language / variety>**. Could you
> spend about 30 minutes listening to some words and sentences it says and telling me what sounds
> wrong? No technical knowledge is needed: there is a short checklist and a form to fill in. With your
> permission your name would be recorded as the reviewer; you can also use a pseudonym. The voice is
> synthetic and will not sound like a person; I want to know whether it sounds like **<variety>**.

Attach the packet folder (zipped) or a link to it, and say when you would like it back.

## Good practice

- Do not tell the reviewer which version of an A/B item is the "new" one: the packet does not say.
- Never push a reviewer to agree; "I don't know" is a useful answer.
- Ask before writing anyone's name into the project. The form has `consent_to_name`; without "yes"
  nothing is recorded.
- Keep the filled form: the ingest copies it into `docs/tts-extension/review/feedback/<tag>/`.
- A reviewer's corrections go back into the pack only through the usual route: a cited source or a
  measurement for every dialect feature (AUTHENTICITY.md, "Anti-caricature").
