# MetaGram Desktop

[ English | [Русский](README-RU.md) ]

A desktop Telegram client focused on privacy and customization.

## Features

- Ghost mode: don't send read receipts, hide your online status and typing
- Saves deleted messages
- Message edit history
- Font, appearance and chat customization
- Streamer mode, message filters and more

## Download

Builds for Windows (x64) are made by GitHub Actions: open the
[Actions](https://github.com/ressedich/MetaGramDesktop/actions) tab, pick the
latest successful **MetaGram Windows** run and download the
**MetaGram-Windows-x64** archive. The app is portable, no installer needed.

## Building

The Windows build is described in
[`.github/workflows/metagram-win.yml`](.github/workflows/metagram-win.yml).
User-visible branding is applied by [`metagram/rebrand.py`](metagram/rebrand.py).

## License

MetaGram Desktop is free software licensed under the
[GNU GPL v3](LICENSE). Copyright notices of the original authors are kept in
the source files.
