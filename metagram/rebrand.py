#!/usr/bin/env python3
"""Rebrand AyuGram Desktop sources as MetaGram Desktop.

Re-runnable: run it after every merge from upstream AyuGram.
Only user-visible names and links are changed; internal identifiers
(ayu:: namespace, file names, settings keys) stay as-is so upstream merges
keep working. Copyright headers in the sources and LICENSE are kept, and the
About box keeps the GPL notice, as the GPL requires.

Usage: python metagram/rebrand.py   (from the repository root)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REPO = "https://github.com/ressedich/MetaGramDesktop"
# Where the "channel" / "chat" buttons lead.
CHANNEL_LINK = "https://i.pinimg.com/736x/f6/e0/5a/f6e05a37fe706a45a3adcb31c79e5130.jpg"

# (file, old, new) exact replacements; {NL} is the file's line ending.
# A replacement is skipped if `new` is already in the file.
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
     '#define MyAppURL "https://github.com/AyuGram"', f'#define MyAppURL "{REPO}"'),
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
     f'u"{REPO}/releases"_q'),
    # tray menu, unsupported-message text
    ("Telegram/SourceFiles/tray.cpp",
     '.replace("Telegram", "AyuGram");', '.replace("Telegram", "MetaGram");'),
    ("Telegram/SourceFiles/history/history_item_helpers.cpp",
     '.replace("Telegram", "AyuGram")', '.replace("Telegram", "MetaGram")'),
    ("Telegram/SourceFiles/history/history_item_helpers.cpp",
     'u"https://t.me/AyuGramReleases"_q', f'u"{CHANNEL_LINK}"_q'),
    # About box: own name and repo; GPL notice stays
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     'box->setTitle(rpl::single(u"AyuGram Desktop"_q));',
     'box->setTitle(rpl::single(u"MetaGram Desktop"_q));'),
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     '"https://github.com/AyuGram/AyuGramDesktop/blob/dev/LICENSE"',
     f'"{REPO}/blob/dev/LICENSE"'),
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     '"https://github.com/AyuGram/AyuGramDesktop")),',
     f'"{REPO}")),'),
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     'rpl::single(QString("@AyuGramReleases")),',
     'rpl::single(QString("MetaGram")),'),
    ("Telegram/SourceFiles/boxes/about_box.cpp",
     '\t\t\tcontroller->showPeerByLink(Window::PeerByLinkInfo{{NL}'
     '\t\t\t\t.usernameOrId = QString("ayugramreleases"),{NL}'
     '\t\t\t});',
     f'\t\t\tFile::OpenUrl(u"{CHANNEL_LINK}"_q);'),
    # MetaGram settings page
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     'QString("AyuGram Desktop v")', 'QString("MetaGram Desktop v")'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     '.title = rpl::single(QString("AyuGram")),',
     '.title = rpl::single(QString("MetaGram")),'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     '\t\t.label = rpl::single(QString("@ayugram")),{NL}'
     '\t\t.onClick = [=] {{NL}'
     '\t\t\tcontroller->showPeerByLink(Window::PeerByLinkInfo{{NL}'
     '\t\t\t\t.usernameOrId = QString("ayugram"),{NL}'
     '\t\t\t});',
     '\t\t.label = rpl::single(QString("@metagram")),{NL}'
     '\t\t.onClick = [=] {{NL}'
     f'\t\t\tQDesktopServices::openUrl(QString("{CHANNEL_LINK}"));'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     '\t\t.label = rpl::single(QString("@ayugramchat")),{NL}'
     '\t\t.onClick = [=] {{NL}'
     '\t\t\tcontroller->showPeerByLink(Window::PeerByLinkInfo{{NL}'
     '\t\t\t\t.usernameOrId = QString("ayugramchat"),{NL}'
     '\t\t\t});',
     '\t\t.label = rpl::single(QString("@metagramchat")),{NL}'
     '\t\t.onClick = [=] {{NL}'
     f'\t\t\tQDesktopServices::openUrl(QString("{CHANNEL_LINK}"));'),
    # main menu footer
    ("Telegram/SourceFiles/window/window_main_menu.cpp",
     'u"AyuGram Desktop"_q,', 'u"MetaGram Desktop"_q,'),
    ("Telegram/SourceFiles/window/window_main_menu.cpp",
     'u"https://ayugram.one"_q', f'u"{REPO}"_q'),
    # previews in Appearance settings
    ("Telegram/SourceFiles/ayu/ui/components/message_preview.cpp",
     'u"AyuGram Releases"_q', 'u"MetaGram Releases"_q'),
    ("Telegram/SourceFiles/ayu/ui/components/avatar_corners_preview.cpp",
     'u"AyuGram Releases"_q', 'u"MetaGram Releases"_q'),
    ("Telegram/SourceFiles/ayu/ui/components/avatar_corners_preview.cpp",
     'setCursor(Qt::PointingHandCursor);{NL}\tresolveChannel();',
     'setCursor(Qt::PointingHandCursor);'),
    ("Telegram/SourceFiles/ayu/ui/components/avatar_corners_preview.cpp",
     '#include "apiwrap.h"',
     '#include "apiwrap.h"{NL}#include "core/file_utilities.h"'),
    ("Telegram/SourceFiles/ayu/ui/components/avatar_corners_preview.cpp",
     '\t\t_controller->showPeerByLink(Window::PeerByLinkInfo{{NL}'
     '\t\t\t.usernameOrId = u"AyuGramReleases"_q,{NL}'
     '\t\t});',
     f'\t\tFile::OpenUrl(u"{CHANNEL_LINK}"_q);'),
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
     'u"https://github.com/AyuGram/AyuGramDesktop"_q', f'u"{REPO}"_q'),
    ("Telegram/SourceFiles/core/crash_report_window.cpp",
     'u"AyuGram Crash Report"_q', 'u"MetaGram Crash Report"_q'),
    # updater helper exe names
    ("Telegram/SourceFiles/_other/updater_win.cpp",
     'updateTo + L"AyuGram.exe") && exeName != L"AyuGram.exe"',
     'updateTo + L"MetaGram.exe") && exeName != L"MetaGram.exe"'),
    ("Telegram/SourceFiles/_other/updater_win.cpp",
     'exeName = L"AyuGram.exe";', 'exeName = L"MetaGram.exe";'),
    # Translations downloaded at runtime still say AyuGram: rename on load,
    # and keep our own texts for a few keys.
    ("Telegram/SourceFiles/ayu/ayu_lang.cpp",
     'auto val = json.value(brokenKey).toString().replace(qsl("&amp;"), qsl("&"));',
     'auto val = json.value(brokenKey).toString().replace(qsl("&amp;"), qsl("&"))'
     '.replace(qsl("AyuGram"), qsl("MetaGram"));{NL}'
     '\t\tif (brokenKey.startsWith(qsl("SettingsWatermark"))'
     ' || brokenKey.startsWith(qsl("FirstLaunchAlert"))'
     ' || brokenKey.startsWith(qsl("IntroAbout"))) {{NL}'
     '\t\t\tcontinue; // MetaGram: keep texts from lang.strings{NL}'
     '\t\t}'),
]

# (file, regex, replacement) for blocks removed entirely.
REGEX = [
    # Windows shortcut / pinned-taskbar names
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     r'u"AyuGram( Desktop| for Windows)?/AyuGram\.lnk"_q', None),
    ("Telegram/SourceFiles/platform/win/windows_app_user_model_id.cpp",
     r'u"AyuGram(Alpha)?\.lnk"_q', None),
    ("Telegram/SourceFiles/ayu/utils/windows_utils.cpp",
     r'AyuGram( Desktop)?(/AyuGram)?\.lnk', None),
    # Translate (Crowdin) and Documentation buttons point to AyuGram sites
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     r'\tbuilder\.addButton\(\{\r?\n\t\t\.id = u"ayu/crowdin"_q,.*?\n\t\}\);\r?\n', ''),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_main.cpp",
     r'\tbuilder\.addButton\(\{\r?\n\t\t\.id = u"ayu/website"_q,.*?\n\t\}\);\r?\n', ''),
]

# (file, literal): "AyuGram" -> "MetaGram" inside this exact literal.
RENAME_IN = [
    ("Telegram/Resources/winrc/Telegram.rc", 'VALUE "FileDescription", "AyuGram Desktop"'),
    ("Telegram/Resources/winrc/Telegram.rc", 'VALUE "ProductName", "AyuGram Desktop"'),
    ("Telegram/Resources/winrc/Updater.rc", 'VALUE "FileDescription", "AyuGram Desktop Updater"'),
    ("Telegram/Resources/winrc/Updater.rc", 'VALUE "ProductName", "AyuGram Desktop"'),
    ("Telegram/SourceFiles/_other/startup_task_win.cpp", '(directory + L"\\\\AyuGram.exe")'),
    ("Telegram/SourceFiles/platform/win/specific_win.cpp", '+ "\\\\AyuGram.lnk";'),
    ("Telegram/SourceFiles/ayu/features/filters/filters_utils.cpp", 'titlePart.setBody("AyuGram Filters");'),
    ("Telegram/SourceFiles/ayu/ui/context_menu/context_menu.cpp", '.text = u"AyuGram"_q,'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_ayu.cpp", '.title = u"AyuGram"_q,'),
    ("Telegram/SourceFiles/ayu/ui/settings/settings_ayu.cpp", 'return rpl::single(QString("AyuGram"));'),
    ("Telegram/SourceFiles/core/crash_reports.cpp", '"AyuGram Desktop launch was not finished properly :( "'),
    ("Telegram/SourceFiles/core/launcher.cpp", 'QApplication::setApplicationName(u"AyuGramDesktop"_q);'),
    ("Telegram/SourceFiles/export/output/export_output_html.cpp", '"of AyuGram Desktop. Please update the application.")'),
    ("Telegram/SourceFiles/intro/intro_widget.cpp", 'QString("AyuGram Desktop v%1")'),
    ("Telegram/SourceFiles/settings/sections/settings_notifications.cpp", 'elided(u"AyuGram Desktop"_q,'),
    ("Telegram/SourceFiles/window/notifications_manager_default.cpp", 'TextWithEntities{ u"AyuGram Desktop"_q }'),
    ("Telegram/SourceFiles/window/main_window.cpp", 'setTitle((user.isEmpty() ? u"AyuGram"_q : user)'),
    ("Telegram/SourceFiles/platform/linux/main_window_linux.cpp", 'lt_telegram, u"AyuGram"_q),'),
    ("Telegram/SourceFiles/platform/linux/main_window_linux.cpp", '\t\t\tu"AyuGram"_q),'),
    ("Telegram/SourceFiles/platform/mac/global_menu_mac.mm", 'u"About AyuGram"_q,'),
    ("Telegram/SourceFiles/platform/mac/global_menu_mac.mm", 'addMenu(u"AyuGram"_q)'),
    ("Telegram/SourceFiles/platform/mac/window_title_mac.mm", 'p.drawText(titleRect, u"AyuGram"_q, style::al_center);'),
]
EXACT += [(f, s, s.replace("AyuGram", "MetaGram")) for f, s in RENAME_IN]
EXACT += [
    ("Telegram/SourceFiles/core/update_checker.cpp",
     'return "https://t.me/AyuGramReleases";', f'return "{CHANNEL_LINK}";'),
    # Only the MetaGram icon exists: ignore any saved alternative icon.
    ("Telegram/SourceFiles/ayu/ayu_settings.cpp",
     's._appIcon = j.value("appIcon", defaults._appIcon.current());',
     's._appIcon = defaults._appIcon.current(); // MetaGram: single app icon'),
    ("Telegram/CMakeLists.txt",
     'ALTERNATE_APPICON_NAMES "AppIcon-Alt AppIcon-Discord AppIcon-Spotify AppIcon-Extera '
     'AppIcon-Nothing AppIcon-Bard AppIcon-Yaplus AppIcon-Win95 AppIcon-Chibi AppIcon-Chibi2 AppIcon-Extera2"',
     'ALTERNATE_APPICON_NAMES ""'),
]

# Alternative app icons (AyuGram artwork) are removed; their files are deleted from git.
ALT_ICONS = "alt|bard|chibi|chibi2|discord|extera|extera2|nothing|spotify|win95|yaplus"
REGEX += [
    ("Telegram/Resources/qrc/ayu/ayu.qrc",
     rf'[ \t]*<file alias="art/ayu/({ALT_ICONS})/[^"]+">[^<]+</file>\r?\n', ''),
    ("Telegram/SourceFiles/ayu/ui/components/icon_picker.cpp",
     rf'\tAyuAssets::({ALT_ICONS.upper()})_ICON,\r?\n', ''),
    ("Telegram/CMakeLists.txt",
     r'(set\(ayugram_icons\r?\n\s+Default\r?\n)(\s+(Alt|Discord|Spotify|Extera|Nothing|Bard|Yaplus'
     r'|Win95|Chibi|Chibi2|Extera2)\r?\n)+', r'\1'),
    # hide the icon picker in Appearance settings
    ("Telegram/SourceFiles/ayu/ui/settings/settings_appearance.cpp",
     r'\tbuilder\.addSubsectionTitle\(\{\r?\n\t\t\.id = u"ayu/appIcon"_q,.*?\n\t\}\);\r?\n\r?\n'
     r'\tbuilder\.add\(\[\]\(const WidgetContext &ctx\) -> SectionBuilder::WidgetToAdd \{\r?\n'
     r'\t\treturn \{\r?\n\t\t\t\.widget = object_ptr<IconPicker>\(ctx\.container\),.*?\n\t\}\);\r?\n\r?\n', ''),
]

# Strings in lang.strings whose text we write ourselves.
LANG_OVERRIDES = {
    "ayu_SettingsWatermark": "MetaGram Desktop",
    "ayu_FirstLaunchAlert":
        "MetaGram is **free** software. "
        "You assume **full responsibility** for using this application with your account.",
    "ayu_IntroAbout": "Welcome to MetaGram Desktop.\\nMake Telegram your own.",
}


def ayu_to_meta(match):
    return match.group(0).replace("AyuGram", "MetaGram")


def main():
    errors = []
    files = {}

    def get(rel):
        if rel not in files:
            files[rel] = (ROOT / rel).read_bytes().decode("utf-8")
        return files[rel]

    for rel, old, new in EXACT:
        text = get(rel)
        nl = "\r\n" if "\r\n" in text else "\n"
        old = old.replace("{NL}", nl)
        new = new.replace("{NL}", nl)
        if new in text:
            continue
        if old in text:
            files[rel] = text.replace(old, new)
        else:
            errors.append(f"{rel}: pattern not found: {old!r}")

    for rel, pattern, repl in REGEX:
        text = get(rel)
        if repl is None:
            files[rel] = re.sub(pattern, ayu_to_meta, text)
        else:
            files[rel] = re.sub(pattern, repl, text, flags=re.S)

    rel = "Telegram/Resources/langs/lang.strings"
    lines = get(rel).split("\n")
    for i, line in enumerate(lines):
        m = re.match(r'^"(ayu_[^"]+)" = "(.*)";(\r?)$', line)
        if not m:
            continue
        key, value, cr = m.groups()
        value = LANG_OVERRIDES.get(key, value.replace("AyuGram", "MetaGram"))
        lines[i] = f'"{key}" = "{value}";{cr}'
    files[rel] = "\n".join(lines)

    if errors:
        print("\n".join(errors))
        print("Upstream changed these lines: update metagram/rebrand.py.")
        return 1

    changed = 0
    for rel, text in files.items():
        path = ROOT / rel
        if path.read_bytes().decode("utf-8") != text:
            path.write_bytes(text.encode("utf-8"))
            changed += 1
            print(f"rebranded {rel}")
    print(f"done, {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
