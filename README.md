<div align="center">

# ⚛ Installify

**Download YouTube videos and music. Clean, fast, dead simple.**

Paste a link, pick a format, done. No accounts, no ads, no telemetry — fully open source.

[![License: MIT](https://img.shields.io/badge/license-MIT-e6231e.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-e6231e.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-e6231e.svg)](#installation)

</div>

> ⚠️ **Requires FFmpeg.** Proton uses [FFmpeg](https://ffmpeg.org/download.html) to merge video/audio and convert to MP3 — it won't download anything without it. Grab a build from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (Windows: the [gyan.dev builds](https://www.gyan.dev/ffmpeg/builds/) are the easiest) and make sure `ffmpeg` is on your system `PATH`.

---

## What it does

Proton is a small desktop app that wraps [yt-dlp](https://github.com/yt-dlp/yt-dlp) in a clean, dark-mode UI. Paste a YouTube link, see the thumbnail and title instantly, pick MP4 or MP3, and hit download — everything runs locally on your machine.

- **MP4 & MP3, one click** — switch formats with a single toggle, no separate tools
- **Pick your quality** — 1080p down to 480p for video, 320kbps or 192kbps for audio, or just leave it on "best"
- **Editor-friendly by default** — videos download as H.264 out of the box, so they open cleanly in Premiere Pro and older editors, no re-encoding required
- **Videos and audio, sorted** — set a fixed folder for MP4s and another for MP3s once, Proton remembers even after a restart
- **See before you download** — paste a link and the thumbnail, title and channel show up instantly
- **Runs entirely on your machine** — no accounts, no cloud processing, no telemetry



## Installation

### Prerequisites

- [ffmpeg](https://ffmpeg.org/download.html) — **required**, used to merge video/audio and convert to MP3. On Windows, grab a build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/), unzip it, and add the `bin` folder to your system `PATH`
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) — required for yt-dlp's EJS challenge solver, must be on your `PATH`

### Run from source

```bash
git clone https://github.com/<your-username>/proton.git
cd proton
pip install -r requirements.txt
python youtube_downloader_gui.py
```

### Build a standalone Windows .exe

```bash
pip install pyinstaller pillow
pyinstaller --onefile --windowed --name Proton --icon=proton.ico --add-data "proton.ico;." --collect-data qtawesome youtube_downloader_gui.py
```

The finished executable lands in `dist/Proton.exe`. `--collect-data qtawesome` is required — without it the icon font Proton relies on won't be bundled and every icon will render blank.

## Configuration

Everything lives under the **settings** tab and is saved automatically between restarts:

| Setting | What it does |
|---|---|
| Storage paths | Fixed folders for MP4 and MP3 downloads |
| Video codec | H.264 (compatible, default) or best-available (may be AV1) |
| Cookies from browser | Uses your logged-in browser's cookies to get around YouTube's bot detection |

## Built with

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the actual download engine
- [PySide6](https://doc.qt.io/qtforpython/) — the UI framework
- [qtawesome](https://github.com/spyder-ide/qtawesome) — icon set

## Contributing

Issues and pull requests are welcome. If you're planning a bigger change, opening an issue first to discuss it is appreciated but not required.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it.

---

<div align="center">
made by light with ❤
</div>
