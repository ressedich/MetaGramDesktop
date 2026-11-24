#!/usr/bin/env python3
"""Rebrand AyuGram Desktop sources as MetaGram Desktop.

Re-runnable: run it after every merge from upstream AyuGram.
Only user-visible names are changed; internal identifiers (ayu:: namespace,
file names, settings keys) stay as-is so upstream merges keep working.
Copyright headers and LICENSE are kept, as GPL requires.

Usage: python metagram/rebrand.py   (from the repository root)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (file, old, new) exact replacements. A file is skipped if `new` is already there.
EXACT = [
    # app name, exe name, data folder
    ("Telegram/SourceFiles/core/version.h",
     'constexpr auto AppNameOld = "AyuGram for Windows"_cs;',
     'constexpr auto AppNameOld = "MetaGram for Windows"_cs;'),
    ("Telegram/SourceFiles/core/version.h",
     'constexpr auto AppName = "AyuGram Desktop"_cs;',
     'constexpr auto AppName = "MetaGram Desktop"_cs;'),
    ("Telegram/SourceFiles/core/version.h",
     'constexpr auto AppFile = "AyuGram"_cs;',
     'constexpr auto AppFile = "MetaGram"_cs;'),
    ("Telegram/CMakeLists.txt",
     'set(bundle_identifier "one.ayugram.AyuGramDesktop$<$<CONFIG:Debug>:Debug>")',
     'set(bundle_identifier "one.metagram.MetaGramDesktop$<$<CONFIG:Debug>:Debug>")'),
    ("Telegram/CMakeLists.txt",
     'set(bundle_identifier "one.ayugram.AyuGramDesktop")',
     'set(bundle_identifier "one.metagram.MetaGramDesktop")'),
    ("Telegram/CMakeLists.txt",
     'set(output_name "AyuGram")',
     'set(output_name "MetaGram")'),
    ("Telegram/CMakeLists.txt",
     'OR NOT "${output_name}" STREQUAL "AyuGram")',
     'OR NOT "${output_name}" STREQUAL "MetaGram")'),
    # installer
    ("Telegram/build/setup.iss",
     '#define MyAppShortName "AyuGram"', '#define MyAppShortName "MetaGram"'),
    ("Telegram/build/setup.iss",
     '#define MyAppName "AyuGram Desktop"', '#define MyAppName "MetaGram Desktop"'),
    ("Telegram/build/setup.iss",
     '#define MyAppURL "https://github.com/AyuGram"',
     '#define MyAppURL "https://github.com/ressedich/MetaGramDesktop"'),
    ("Telegram/build/setup.iss",
     '#define MyAppExeName "AyuGram.exe"', '#define MyAppExeName "MetaGram.exe"'),
    # Windows taskbar / notifications identity
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     'L"AyuGram.AyuGramDesktop.Store"', 'L"MetaGram.MetaGramDesktop.Store"'),
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     'L"AyuGram.AyuGramDesktop";', 'L"MetaGram.MetaGramDesktop";'),
    ("Telegram/SourceFiles/core/application.cpp",
     '.shortAppName = u"AyuGram"_q,', '.shortAppName = u"MetaGram"_q,'),
    ("Telegram/SourceFiles/core/application.cpp",
     'u"https://github.com/AyuGram/AyuGramDesktop/releases"_q',
     'u"https://github.com/ressedich/MetaGramDesktop/releases"_q'),
    # tray menu
    ("Telegram/SourceFiles/tray.cpp",
     '.replace("Telegram", "AyuGram");', '.replace("Telegram", "MetaGram");'),
    ("Telegram/SourceFiles/history/history_item_helpers.cpp",
     '.replace("Telegram", "AyuGram")', '.replace("Telegram", "MetaGram")'),
    # About box: own name, keep credit to AyuGram
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     'box->setTitle(rpl::single(u"AyuGram Desktop"_q));',
     'box->setTitle(rpl::single(u"MetaGram Desktop"_q));'),
    # settings header
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     'QString("AyuGram Desktop v")', 'QString("MetaGram Desktop v")'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     '.title = rpl::single(QString("AyuGram")),',
     '.title = rpl::single(QString("MetaGram")),'),
    # main menu footer
    ("Telegram/SourceFiles/window/window_main_menu.cpp",
     'u"AyuGram Desktop"_q,', 'u"MetaGram Desktop"_q,'),
    # crash window
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'u"AyuGram"_q : title', 'u"MetaGram"_q : title'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'Could not start AyuGram Desktop!', 'Could not start MetaGram Desktop!'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'u"Last time AyuGram Desktop was not closed properly."_q);',
     'u"Last time MetaGram Desktop was not closed properly."_q);'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'horizontalAdvance(u"Last time AyuGram Desktop was not closed properly."_q)',
     'horizontalAdvance(u"Last time MetaGram Desktop was not closed properly."_q)'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'Last time AyuGram Desktop crashed :(', 'Last time MetaGram Desktop crashed :('),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'GET THE LATEST VERSION OF AYUGRAM DESKTOP', 'GET THE LATEST VERSION OF METAGRAM DESKTOP'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'u"https://github.com/AyuGram/AyuGramDesktop"_q',
     'u"https://github.com/ressedich/MetaGramDesktop"_q'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'u"AyuGram Crash Report"_q', 'u"MetaGram Crash Report"_q'),
    # updater helper exe names
    ("Telegram/SourceFiles/_other/updater_win.cpp",
     'updateTo + L"AyuGram.exe") && exeName != L"AyuGram.exe"',
     'updateTo + L"MetaGram.exe") && exeName != L"MetaGram.exe"'),
    ("Telegram/SourceFiles/_other/updater_win.cpp",
     'exeName = L"AyuGram.exe";', 'exeName = L"MetaGram.exe";'),
    # Translations downloaded at runtime still say AyuGram: rename on load,
    # but keep our own texts and the lines that credit the original project.
    ("Telegram/SourceFiles/ayu/ayu_lang.cpp",
     'auto val = json.value(brokenKey).toString().replace(qsl("&amp;"), qsl("&"));',
     'auto val = json.value(brokenKey).toString().replace(qsl("&amp;"), qsl("&"));{NL}'
     '\t\tif (brokenKey.startsWith(qsl("SettingsWatermark"))'
     ' || brokenKey.startsWith(qsl("FirstLaunchAlert"))'
     ' || brokenKey.startsWith(qsl("IntroAbout"))) {{NL}'
     '\t\t\tcontinue; // MetaGram: keep texts from lang.strings{NL}'
     '\t\t}{NL}'
     '\t\tif (!brokenKey.startsWith(qsl("SupporterPopup"))'
     ' && !brokenKey.startsWith(qsl("OfficialResourcePopup"))'
     ' && !brokenKey.startsWith(qsl("ExteraChatsAlert"))) {{NL}'
     '\t\t\tval = val.replace(qsl("AyuGram"), qsl("MetaGram"));{NL}'
     '\t\t}'),
]

# Shortcut / pinned-taskbar names on Windows.
REGEX = [
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     r'u"AyuGram( Desktop| for Windows)?/AyuGram\.lnk"_q', None),
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     r'u"AyuGram(Alpha)?\.lnk"_q', None),
    ("Telegram/SourceFiles/ayu/utils/windows_utils.cpp",
     r'AyuGram( Desktop)?(/AyuGram)?\.lnk', None),
]

# Strings in lang.strings whose text we write ourselves.
LANG_OVERRIDES = {
    "ayu_SettingsWatermark":
        "MetaGram is based on AyuGram by Radolyn Labs.",
    "ayu_FirstLaunchAlert":
        "MetaGram is **free** software based on AyuGram. "
        "You assume **full responsibility** for using this application with your account.",
    "ayu_IntroAbout":
        "Welcome to MetaGram Desktop.\\nMake Telegram your own.",
}
# Keys that credit the original project: leave them alone.
LANG_KEEP = {"ayu_SupporterPopup", "ayu_OfficialResourcePopup", "ayu_ExteraChatsAlert"}


def read(path):
    raw = path.read_bytes()
    return raw.decode("utf-8")


def write(path, text):
    path.write_bytes(text.encode("utf-8"))


def ayu_to_meta(match):
    return match.group(0).replace("AyuGram", "MetaGram")


def main():
    errors = []
    files = {}

    def get(rel):
        if rel not in files:
            files[rel] = read(ROOT / rel)
        return files[rel]

    for rel, old, new in EXACT:
        text = get(rel)
        new = new.replace("{NL}", "\r\n" if "\r\n" in text else "\n")
        if new in text:
            continue
        if old in text:
            files[rel] = text.replace(old, new)
        else:
            errors.append(f"{rel}: pattern not found: {old}")

    for rel, pattern, _ in REGEX:
        text = get(rel)
        files[rel] = re.sub(pattern, ayu_to_meta, text)

    rel = "Telegram/Resources/langs/lang.strings"
    lines = get(rel).split("\n")
    for i, line in enumerate(lines):
        m = re.match(r'^"(ayu_[^"]+)" = "(.*)";(\r?)$', line)
        if not m:
            continue
        key, value, cr = m.groups()
        if key in LANG_OVERRIDES:
            value = LANG_OVERRIDES[key]
        elif key not in LANG_KEEP:
            value = value.replace("AyuGram", "MetaGram")
        lines[i] = f'"{key}" = "{value}";{cr}'
    files[rel] = "\n".join(lines)

    if errors:
        print("\n".join(errors))
        print("Upstream changed these lines: update metagram/rebrand.py.")
        return 1

    changed = 0
    for rel, text in files.items():
        if read(ROOT / rel) != text:
            write(ROOT / rel, text)
            changed += 1
            print(f"rebranded {rel}")
    print(f"done, {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
