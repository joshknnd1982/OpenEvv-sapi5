#include "text_codec.h"

#include <windows.h>

namespace evv {

std::string encode_text(const wchar_t* text, size_t length, unsigned codepage)
{
    std::wstring w;
    w.reserve(length + 8);
    for (size_t i = 0; i < length; ++i) {
        const wchar_t c = text[i];
        switch (c) {
        case 0x00AD: // soft hyphen
        case 0x200B: case 0x200C: case 0x200D: case 0x200E: case 0x200F: // zero-width, marks
        case 0x2060: case 0xFEFF:
            continue;
        case 0x00A0: case 0x2007: case 0x202F: // no-break spaces
        case 0x2028: case 0x2029:              // line and paragraph separators
            w.push_back(L' ');
            continue;
        case 0x2018: case 0x2019: case 0x201A: case 0x201B: case 0x2032:
            w.push_back(L'\'');
            continue;
        case 0x201C: case 0x201D: case 0x201E: case 0x201F: case 0x2033:
            w.push_back(L'"');
            continue;
        case 0x2010: case 0x2011: case 0x2012: case 0x2212: // hyphens and minus
            w.push_back(L'-');
            continue;
        case 0x2013: case 0x2014: case 0x2015: // en and em dashes: a pause, not a word
            w.append(L" - ");
            continue;
        case 0x2026: // ellipsis
            w.append(L"...");
            continue;
        default:
            break;
        }
        if (c < 0x20 || c == 0x7F || (c >= 0x80 && c < 0xA0)) {
            w.push_back(L' '); // tabs, line breaks, C0/C1 controls
            continue;
        }
        // Lone surrogate halves cannot be converted; a pair is kept whole.
        if (c >= 0xD800 && c <= 0xDBFF) {
            if (i + 1 < length && text[i + 1] >= 0xDC00 && text[i + 1] <= 0xDFFF) {
                w.push_back(c);
                w.push_back(text[++i]);
            } else {
                w.push_back(L' ');
            }
            continue;
        }
        if (c >= 0xDC00 && c <= 0xDFFF) {
            w.push_back(L' ');
            continue;
        }
        w.push_back(c);
    }
    if (w.empty()) return {};

    const int n = static_cast<int>(w.size());
    std::string out;
    if (codepage == CP_UTF8) {
        const int need = WideCharToMultiByte(CP_UTF8, 0, w.data(), n, nullptr, 0, nullptr, nullptr);
        out.resize(static_cast<size_t>(need > 0 ? need : 0));
        if (need > 0) WideCharToMultiByte(CP_UTF8, 0, w.data(), n, out.data(), need, nullptr, nullptr);
        return out;
    }
    // Best fit is left on: it turns an accented letter the code set lacks into
    // its plain letter, which is what a listener wants to hear.
    const int need = WideCharToMultiByte(codepage, 0, w.data(), n, nullptr, 0, " ", nullptr);
    if (need <= 0) {
        // An unknown code page: keep what is plain ASCII.
        for (wchar_t c : w) out.push_back(c < 128 ? static_cast<char>(c) : ' ');
        return out;
    }
    out.resize(static_cast<size_t>(need));
    WideCharToMultiByte(codepage, 0, w.data(), n, out.data(), need, " ", nullptr);
    // A NUL would end the engine's string early.
    for (char& ch : out) {
        if (ch == '\0') ch = ' ';
    }
    return out;
}

// Only the characters each module was measured to render as silence when
// spoken alone (tools/evv_chars): the hyphen everywhere, '<' outside English,
// and nearly all ASCII punctuation in Japanese, whose module names none.
std::wstring symbol_name(wchar_t c, const std::wstring& tag)
{
    const std::wstring lang = tag.substr(0, 2);
    if (lang == L"en") {
        if (c == L'-') return L"dash";
        return {};
    }
    if (lang == L"de") {
        if (c == L'-') return L"Bindestrich";
        if (c == L'<') return L"kleiner als";
        return {};
    }
    if (lang == L"es") {
        if (c == L'-') return L"guion";
        if (c == L'<') return L"menor que";
        return {};
    }
    if (lang == L"fr") {
        if (c == L'-') return L"tiret";
        if (c == L'<') return L"inférieur à";
        return {};
    }
    if (lang == L"it") {
        if (c == L'-') return L"trattino";
        if (c == L'<') return L"minore di";
        return {};
    }
    if (lang == L"pl") {
        if (c == L'-') return L"myślnik";
        if (c == L'<') return L"mniejszy niż";
        return {};
    }
    if (lang == L"ja") {
        // Katakana readings, which the romanizer takes without a dictionary.
        switch (c) {
        case L'!': return L"エクスクラメーション"; // エクスクラメーション
        case L'"': return L"ダブルクォート";                   // ダブルクォート
        case L'#': return L"シャープ";                                     // シャープ
        case L'$': return L"ドル";                                                 // ドル
        case L'%': return L"パーセント";                               // パーセント
        case L'\'': return L"アポストロフィ";                  // アポストロフィ
        case L'(': return L"カッコ";                                           // カッコ
        case L')': return L"カッコトジ";                               // カッコトジ
        case L'*': return L"アスタリスク";                         // アスタリスク
        case L'+': return L"プラス";                                           // プラス
        case L',': return L"カンマ";                                           // カンマ
        case L'-': return L"マイナス";                                     // マイナス
        case L'.': return L"ピリオド";                                     // ピリオド
        case L'/': return L"スラッシュ";                               // スラッシュ
        case L':': return L"コロン";                                           // コロン
        case L';': return L"セミコロン";                               // セミコロン
        case L'<': return L"ショウナリ";                               // ショウナリ
        case L'=': return L"イコール";                                     // イコール
        case L'>': return L"ダイナリ";                                     // ダイナリ
        case L'?': return L"クエスチョン";                         // クエスチョン
        case L'[': return L"カクカッコ";                               // カクカッコ
        case L'\\': return L"バックスラッシュ";            // バックスラッシュ
        case L']': return L"カクカッコトジ";                   // カクカッコトジ
        case L'^': return L"キャレット";                               // キャレット
        case L'_': return L"アンダーバー";                         // アンダーバー
        case L'`': return L"バッククォート";                   // バッククォート
        case L'{': return L"ナミカッコ";                               // ナミカッコ
        case L'|': return L"タテセン";                                     // タテセン
        case L'}': return L"ナミカッコトジ";                   // ナミカッコトジ
        case L'~': return L"チルダ";                                           // チルダ
        default: return {};
        }
    }
    return {};
}

} // namespace evv
