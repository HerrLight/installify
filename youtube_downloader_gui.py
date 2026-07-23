"""
INSTALLIFY - Minimalist YouTube Downloader
Framework: PySide6
Download Engine: yt-dlp (with EJS n-challenge solver)
"""

import sys
import os
import re
import random
import urllib.request

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSettings, QSize, QPointF, QRectF,
    QPropertyAnimation, QEasingCurve, Property
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QProgressBar, QFileDialog, QMessageBox,
    QFrame, QStackedWidget, QButtonGroup, QToolButton, QAbstractButton,
    QScrollArea, QCheckBox, QSlider
)
from PySide6.QtGui import (
    QPixmap, QPainter, QPainterPath, QFont, QColor, QPen, QLinearGradient, QBrush, QPalette
)

import qtawesome as qta
import yt_dlp


# ----------------------------------------------------------------------
#  TRANSLATION STRINGS
# ----------------------------------------------------------------------
STRINGS = {
    "Deutsch": {
        "nav_home": "Startseite",
        "nav_settings": "Einstellungen",
        "nav_about": "Über",
        "placeholder_url": "Link hier einfügen...",
        "btn_paste": "Link aus Zwischenablage einfügen",
        "chip_mp4": "mp4 video",
        "chip_mp3": "mp3 audio",
        "no_image": "kein\nbild",
        "preview_placeholder": "Link einfügen für Info",
        "preview_fetching": "Lade Infos...",
        "status_ready": "bereit.",
        "status_connecting": "verbinde...",
        "status_done": "fertig!",
        "status_error": "Download-Fehler.",
        "btn_download": "Download starten",
        "btn_wait": "bitte warten...",
        "settings_title": "Einstellungen",
        "cat_general": "Allgemein",
        "cat_paths": "Pfade & Engine",
        "lbl_design": "Design",
        "lbl_lang": "Sprache",
        "lbl_subtitles": "Untertitel einbetten",
        "lbl_metadata": "Medien-Tags einbetten",
        "lbl_skip": "Vorhandene Dateien überspringen",
        "lbl_tmpl": "Dateinamen-Vorlage",
        "lbl_parallel": "Paralleles Limit",
        "heading_paths": "Pfade & Executables",
        "lbl_ffmpeg": "FFmpeg-Pfad",
        "ph_ffmpeg": "Standard (im System-PATH gesucht)",
        "lbl_video_folder": "videos (mp4)",
        "lbl_audio_folder": "audio (mp3)",
        "lbl_cookies": "browser cookies (yt-dlp)",
        "about_title": "über installify",
        "about_q1": "was ist installify?",
        "about_a1": "installify lädt Video und Audio von YouTube in der gewünschten Qualität herunter — als MP4 zum Bearbeiten oder MP3 zum Anhören.",
        "about_q2": "wie funktioniert es?",
        "about_a2": "installify nutzt yt-dlp im Hintergrund, um Video- und Audio-Streams herunterzuladen, zusammenzufügen und bei Bedarf in MP3 zu konvertieren.",
        "about_q3": "codec-kompatibilität",
        "about_a3": "Standardmäßig bevorzugt installify den H.264-Codec, damit deine Videos problemlos in Schnittprogramme wie Premiere Pro importiert werden können.",
        "err_invalid_url": "Bitte gib einen gültigen YouTube-Link ein.",
        "err_folder": "Zielordner konnte nicht erstellt werden:",
        "succ_download": "Erfolgreich heruntergeladen!",
        "overlay_title": "Playlist-Einträge",
        "btn_select_all": "Alle auswählen",
        "btn_deselect_all": "Alle abwählen",
        "btn_download_selected": "Ausgewählte herunterladen",
    },
    "English": {
        "nav_home": "Home",
        "nav_settings": "Settings",
        "nav_about": "About",
        "placeholder_url": "paste link here...",
        "btn_paste": "Paste link from clipboard",
        "chip_mp4": "mp4 video",
        "chip_mp3": "mp3 audio",
        "no_image": "no\nimage",
        "preview_placeholder": "paste link to fetch info",
        "preview_fetching": "fetching info...",
        "status_ready": "ready.",
        "status_connecting": "connecting...",
        "status_done": "done!",
        "status_error": "download error.",
        "btn_download": "start download",
        "btn_wait": "please wait...",
        "settings_title": "Settings",
        "cat_general": "General",
        "cat_paths": "Paths & Engine",
        "lbl_design": "Theme",
        "lbl_lang": "Language",
        "lbl_subtitles": "Embed subtitles",
        "lbl_metadata": "Embed media tags",
        "lbl_skip": "Skip existing files",
        "lbl_tmpl": "Filename template",
        "lbl_parallel": "Parallel limit",
        "heading_paths": "Paths & Executables",
        "lbl_ffmpeg": "FFmpeg path",
        "ph_ffmpeg": "Default (searched in System PATH)",
        "lbl_video_folder": "videos (mp4)",
        "lbl_audio_folder": "audio (mp3)",
        "lbl_cookies": "browser cookies (yt-dlp)",
        "about_title": "about installify",
        "about_q1": "what is installify?",
        "about_a1": "installify downloads video and audio from youtube in the quality you need — as mp4 for editing or mp3 for listening.",
        "about_q2": "how does it work?",
        "about_a2": "installify relies on yt-dlp under the hood to fetch video and audio streams, merge them, and convert them if requested.",
        "about_q3": "codec compatibility",
        "about_a3": "By default, installify prefers the h.264 codec so your videos import seamlessly into video editors like premiere pro.",
        "err_invalid_url": "Please enter a valid YouTube link.",
        "err_folder": "Could not create target directory:",
        "succ_download": "Successfully downloaded!",
        "overlay_title": "Playlist Items",
        "btn_select_all": "Select All",
        "btn_deselect_all": "Deselect All",
        "btn_download_selected": "Download Selected",
    }
}


# ----------------------------------------------------------------------
#  HELPER FUNCTIONS
# ----------------------------------------------------------------------
def make_icon(name, color="#dcdcdc", color_on=None):
    if color_on:
        return qta.icon(name, color=color, color_on=color_on)
    return qta.icon(name, color=color)


def rounded_pixmap(pixmap: QPixmap, radius: int) -> QPixmap:
    size = pixmap.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.transparent)
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return rounded


# ----------------------------------------------------------------------
#  METADATA WORKER
# ----------------------------------------------------------------------
class MetadataWorker(QThread):
    metadata_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self, url, request_id, cookie_browser=None):
        super().__init__()
        self.url = url
        self.request_id = request_id
        self.cookie_browser = cookie_browser

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": "in_playlist",
            }
            if self.cookie_browser and self.cookie_browser != "none":
                ydl_opts["cookiesfrombrowser"] = (self.cookie_browser,)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            is_playlist = info.get("_type") == "playlist" or "entries" in info

            if is_playlist:
                entries = []
                for entry in info.get("entries", []):
                    if entry:
                        entries.append({
                            "title": entry.get("title", "Unknown Video"),
                            "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            "duration": entry.get("duration"),
                        })

                self.metadata_signal.emit({
                    "request_id": self.request_id,
                    "is_playlist": True,
                    "playlist_title": info.get("title", "Playlist"),
                    "entries": entries,
                })
            else:
                title = info.get("title", "Unknown Title")
                duration = info.get("duration")
                uploader = info.get("uploader", "")

                thumbnail_url = info.get("thumbnail")
                if not thumbnail_url:
                    thumbnails = info.get("thumbnails") or []
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get("url")

                thumbnail_bytes = None
                if thumbnail_url:
                    try:
                        with urllib.request.urlopen(thumbnail_url, timeout=8) as resp:
                            thumbnail_bytes = resp.read()
                    except Exception:
                        thumbnail_bytes = None

                self.metadata_signal.emit({
                    "request_id": self.request_id,
                    "is_playlist": False,
                    "title": title,
                    "duration": duration,
                    "uploader": uploader,
                    "thumbnail_bytes": thumbnail_bytes,
                })

        except Exception as e:
            self.error_signal.emit(str(e))


# ----------------------------------------------------------------------
#  DOWNLOAD WORKER
# ----------------------------------------------------------------------
class DownloadWorker(QThread):
    progress_signal = Signal(int)
    status_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, urls, output_folder, mode, quality, config=None):
        super().__init__()
        self.urls = urls if isinstance(urls, list) else [urls]
        self.output_folder = output_folder
        self.mode = mode
        self.quality = quality
        self.config = config or {}

    def _progress_hook(self, d):
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                percent = int(downloaded / total * 100)
                self.progress_signal.emit(percent)
            self.status_signal.emit("downloading...")
        elif status == "finished":
            self.progress_signal.emit(100)
            self.status_signal.emit("processing...")

    def _postprocessor_hook(self, d):
        status = d.get("status")
        if status == "started":
            self.status_signal.emit("converting...")
        elif status == "finished":
            self.status_signal.emit("done!")

    def _build_format_and_postprocessors(self):
        postprocessors = []

        if self.mode == "MP4":
            height = None
            if "Default" not in self.quality and "Standard" not in self.quality:
                height = self.quality.replace("p", "").strip()

            if self.config.get("prefer_h264", True):
                if height:
                    fmt = (
                        f"bestvideo[vcodec^=avc1][height<={height}]+bestaudio/"
                        f"best[vcodec^=avc1][height<={height}]/"
                        f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                    )
                else:
                    fmt = (
                        "bestvideo[vcodec^=avc1]+bestaudio/best[vcodec^=avc1]/"
                        "bestvideo+bestaudio/best"
                    )
            else:
                if height:
                    fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                else:
                    fmt = "bestvideo+bestaudio/best"

            merge_format = "mp4"
        else:  # MP3
            fmt = "bestaudio/best"
            merge_format = None
            if "Default" in self.quality or "Standard" in self.quality:
                bitrate = "320"
            else:
                bitrate = self.quality.replace("kbps", "").strip()
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            })

        if self.config.get("embed_metadata", True):
            postprocessors.append({"key": "FFmpegMetadata"})

        if self.config.get("embed_subtitles", False):
            postprocessors.append({"key": "FFmpegEmbedSubtitle"})

        return fmt, merge_format, postprocessors

    def run(self):
        try:
            fmt, merge_format, postprocessors = self._build_format_and_postprocessors()

            tmpl = self.config.get("filename_template", "%(title)s")
            if not tmpl.endswith(".%(ext)s"):
                tmpl += ".%(ext)s"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(self.output_folder, tmpl),
                "js_runtimes": {"node": {}},
                "remote_components": {"ejs:github"},
                "progress_hooks": [self._progress_hook],
                "postprocessor_hooks": [self._postprocessor_hook],
                "postprocessors": postprocessors,
                "noprogress": True,
                "quiet": True,
                "no_warnings": True,
                "overwrites": not self.config.get("skip_existing", False),
                "concurrent_fragment_downloads": self.config.get("parallel_limit", 2),
            }

            ffmpeg_path = self.config.get("ffmpeg_path", "").strip()
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            cookie_browser = self.config.get("cookie_browser")
            if cookie_browser and cookie_browser != "none":
                ydl_opts["cookiesfrombrowser"] = (cookie_browser,)

            if self.config.get("embed_subtitles", False):
                ydl_opts["writesubtitles"] = True
                ydl_opts["subtitleslangs"] = ["en", "de"]

            if merge_format:
                ydl_opts["merge_output_format"] = merge_format

            total_items = len(self.urls)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for idx, url in enumerate(self.urls, 1):
                    if total_items > 1:
                        self.status_signal.emit(f"downloading {idx}/{total_items}...")
                    else:
                        self.status_signal.emit("connecting...")
                    ydl.download([url])

            self.progress_signal.emit(100)
            self.status_signal.emit("done!")
            self.finished_signal.emit(True, f"Successfully downloaded {total_items} file(s)!")

        except Exception as e:
            self.finished_signal.emit(False, str(e))


# ----------------------------------------------------------------------
#  PARTICLE SYSTEM
# ----------------------------------------------------------------------
class ParticleSystem:
    PARTICLE_COUNT = 7

    def __init__(self):
        self.enabled = True
        self.color = QColor(255, 255, 255)
        self._w = 900
        self._h = 650
        self.particles = [self._make_particle(randomize=True) for _ in range(self.PARTICLE_COUNT)]

    def _make_particle(self, randomize=False):
        speed = random.uniform(1.1, 2.4)
        vx = speed
        vy = speed * random.uniform(0.35, 0.6)
        length = random.uniform(36, 80)
        alpha = random.randint(35, 80)
        if randomize:
            x = random.uniform(0, self._w)
            y = random.uniform(0, self._h)
        else:
            x = random.uniform(-length, 0)
            y = random.uniform(-40, self._h * 0.5)
        return {"x": x, "y": y, "vx": vx, "vy": vy, "length": length, "alpha": alpha}

    def advance(self, width, height):
        if width:
            self._w = width
        if height:
            self._h = height
        if not self.enabled:
            return
        for i, p in enumerate(self.particles):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] - p["length"] > self._w or p["y"] - p["length"] > self._h:
                self.particles[i] = self._make_particle()

    def paint(self, painter):
        if not self.enabled:
            return
        painter.setRenderHint(QPainter.Antialiasing)
        for p in self.particles:
            x, y = p["x"], p["y"]
            length, alpha = p["length"], p["alpha"]
            vx, vy = p["vx"], p["vy"]
            norm = (vx ** 2 + vy ** 2) ** 0.5 or 1
            dx, dy = vx / norm, vy / norm
            tail_x = x - dx * length
            tail_y = y - dy * length

            gradient = QLinearGradient(x, y, tail_x, tail_y)
            gradient.setColorAt(0.0, QColor(self.color.red(), self.color.green(), self.color.blue(), alpha))
            gradient.setColorAt(1.0, QColor(self.color.red(), self.color.green(), self.color.blue(), 0))
            painter.setPen(QPen(QBrush(gradient), 1.3))
            painter.drawLine(QPointF(x, y), QPointF(tail_x, tail_y))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self.color.red(), self.color.green(), self.color.blue(), min(alpha + 50, 150)))
            painter.drawEllipse(QPointF(x, y), 1.2, 1.2)


# ----------------------------------------------------------------------
#  GRID PAGE
# ----------------------------------------------------------------------
class GridPage(QWidget):
    GRID_SIZE = 28

    def __init__(self, particle_system=None, parent=None):
        super().__init__(parent)
        self.particle_system = particle_system
        self.bg_color = QColor("#000000")
        self.line_color = QColor(255, 255, 255, 10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)

        pen = QPen(self.line_color)
        pen.setWidth(1)
        painter.setPen(pen)
        for x in range(0, self.width(), self.GRID_SIZE):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), self.GRID_SIZE):
            painter.drawLine(0, y, self.width(), y)

        if self.particle_system:
            self.particle_system.paint(painter)

        painter.end()
        super().paintEvent(event)


# ----------------------------------------------------------------------
#  UI BUTTON CUSTOM WIDGETS
# ----------------------------------------------------------------------
class NavButton(QToolButton):
    def __init__(self, icon_name, label, parent=None):
        super().__init__(parent)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(label)
        self.setFixedSize(48, 48)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setIcon(make_icon(icon_name, color="#6b6b6b", color_on="#000000"))
        self.setIconSize(QSize(19, 19))


class ChipButton(QPushButton):
    def __init__(self, icon_name, label, parent=None):
        super().__init__(f"  {label}", parent)
        self.setObjectName("Chip")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self.setIcon(make_icon(icon_name, color="#8a8a8a", color_on="#000000"))
        self.setIconSize(QSize(14, 14))


class SettingsCategoryButton(QPushButton):
    def __init__(self, icon_name, label, parent=None):
        super().__init__(f"   {label}", parent)
        self.setObjectName("SettingsCategory")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(42)
        self.setIcon(make_icon(icon_name, color="#8a8a8a", color_on="#e6231e"))
        self.setIconSize(QSize(15, 15))
        self.setStyleSheet("text-align: left;")


class IconToggleSwitch(QAbstractButton):
    def __init__(self, icon_name="fa5s.check", parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._pos = 0.0

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 26)

        self._anim = QPropertyAnimation(self, b"knobPos", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.toggled.connect(self._animate_to)

    def _animate_to(self, checked):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def setChecked(self, checked):
        super().setChecked(checked)
        self._pos = 1.0 if checked else 0.0
        self.update()

    def _get_knob_pos(self):
        return self._pos

    def _set_knob_pos(self, value):
        self._pos = value
        self.update()

    knobPos = Property(float, _get_knob_pos, _set_knob_pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        t = self._pos
        track_rect = self.rect().adjusted(0, 0, -1, -1)
        radius = track_rect.height() / 2.0

        off_color = QColor(36, 36, 36)
        on_color = QColor(180, 28, 24)
        track_color = QColor(
            int(off_color.red() + (on_color.red() - off_color.red()) * t),
            int(off_color.green() + (on_color.green() - off_color.green()) * t),
            int(off_color.blue() + (on_color.blue() - off_color.blue()) * t),
        )

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, radius, radius)

        knob_d = track_rect.height() - 6
        knob_y = track_rect.top() + 3
        min_x = track_rect.left() + 3
        max_x = track_rect.right() - 3 - knob_d
        knob_x = min_x + (max_x - min_x) * t

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(232, 232, 232))
        painter.drawEllipse(QRectF(knob_x, knob_y, knob_d, knob_d))

        icon_color = "#e6231e" if t > 0.5 else "#7a7a7a"
        icon_size = int(knob_d * 0.55)
        icon_pixmap = make_icon(self._icon_name, color=icon_color).pixmap(icon_size, icon_size)
        icon_x = knob_x + (knob_d - icon_pixmap.width()) / 2.0
        icon_y = knob_y + (knob_d - icon_pixmap.height()) / 2.0
        painter.drawPixmap(int(icon_x), int(icon_y), icon_pixmap)

        painter.end()


# ----------------------------------------------------------------------
#  IN-APP PLAYLIST OVERLAY
# ----------------------------------------------------------------------
class PlaylistOverlay(QFrame):
    confirm_signal = Signal(list)
    close_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OverlayBg")
        self.hide()

        self.checkboxes = []

        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedSize(540, 440)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        header_row = QHBoxLayout()
        self.title_label = QLabel("Playlist Items")
        self.title_label.setObjectName("SectionHeading")

        close_btn = QPushButton()
        close_btn.setObjectName("IconButton")
        close_btn.setIcon(make_icon("fa5s.times", color="#8a8a8a"))
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.hide_overlay)

        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        card_layout.addLayout(header_row)

        action_row = QHBoxLayout()
        self.btn_all = QPushButton("Select All")
        self.btn_all.setObjectName("Chip")
        self.btn_all.clicked.connect(lambda: self._set_all_checked(True))

        self.btn_none = QPushButton("Deselect All")
        self.btn_none.setObjectName("Chip")
        self.btn_none.clicked.connect(lambda: self._set_all_checked(False))

        action_row.addWidget(self.btn_all)
        action_row.addWidget(self.btn_none)
        action_row.addStretch()
        card_layout.addLayout(action_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("OverlayScroll")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(8)
        self.scroll_area.setWidget(self.scroll_content)

        card_layout.addWidget(self.scroll_area, stretch=1)

        self.confirm_btn = QPushButton("Download Selected")
        self.confirm_btn.setObjectName("PrimaryButton")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.clicked.connect(self._on_confirm)

        card_layout.addWidget(self.confirm_btn)
        outer_layout.addWidget(self.card)

    def update_texts(self, lang):
        s = STRINGS.get(lang, STRINGS["Deutsch"])
        self.btn_all.setText(s["btn_select_all"])
        self.btn_none.setText(s["btn_deselect_all"])
        self.confirm_btn.setText(s["btn_download_selected"])

    def load_playlist(self, title, entries):
        self.title_label.setText(f"Playlist: {title}")
        
        for cb, _ in self.checkboxes:
            cb.deleteLater()
        self.checkboxes.clear()

        for entry in entries:
            dur_str = ""
            if entry.get("duration"):
                m, s = divmod(int(entry["duration"]), 60)
                dur_str = f" ({m}:{s:02d})"

            cb = QCheckBox(f"{entry['title']}{dur_str}")
            cb.setChecked(True)
            self.scroll_layout.addWidget(cb)
            self.checkboxes.append((cb, entry["url"]))

        self.show()
        self.raise_()

    def hide_overlay(self):
        self.hide()
        self.close_signal.emit()

    def _set_all_checked(self, checked):
        for cb, _ in self.checkboxes:
            cb.setChecked(checked)

    def _on_confirm(self):
        selected_urls = [url for cb, url in self.checkboxes if cb.isChecked()]
        if not selected_urls:
            QMessageBox.warning(self, "Warning", "Please select at least one video.")
            return
        self.hide()
        self.confirm_signal.emit(selected_urls)


# ----------------------------------------------------------------------
#  MAIN APP
# ----------------------------------------------------------------------
class InstallifyApp(QWidget):

    QUALITY_MP4 = ["Best Quality (Default)", "1080p", "720p", "480p"]
    QUALITY_MP3 = ["Best Quality (Default)", "320 kbps", "192 kbps"]
    COOKIE_BROWSERS = ["firefox", "chrome", "edge", "brave", "none"]
    THEME_OPTIONS = ["System", "Dark", "Light"]
    LANG_OPTIONS = ["Deutsch", "English"]

    def __init__(self):
        super().__init__()
        self.worker = None
        self.metadata_worker = None
        self.metadata_request_id = 0
        self.selected_playlist_urls = None

        self.settings = QSettings("InstallifyApps", "InstallifyDownloader")

        default_video_folder = os.path.join(os.path.expanduser("~"), "Videos")
        default_audio_folder = os.path.join(os.path.expanduser("~"), "Music")
        
        # Load Settings
        self.current_lang = self.settings.value("appearance/language", "Deutsch")
        self.current_theme = self.settings.value("appearance/theme", "Dark")
        self.mp4_folder = self.settings.value("paths/mp4_folder", default_video_folder)
        self.mp3_folder = self.settings.value("paths/mp3_folder", default_audio_folder)
        self.prefer_h264 = self.settings.value("advanced/prefer_h264", True, type=bool)
        self.cookie_browser = self.settings.value("advanced/cookie_browser", "firefox")

        # Configs
        self.ffmpeg_path = self.settings.value("advanced/ffmpeg_path", "")
        self.embed_subtitles = self.settings.value("dl/embed_subtitles", False, type=bool)
        self.embed_metadata = self.settings.value("dl/embed_metadata", True, type=bool)
        self.skip_existing = self.settings.value("dl/skip_existing", False, type=bool)
        self.filename_template = self.settings.value("dl/filename_template", "%(title)s")
        self.parallel_limit = self.settings.value("dl/parallel_limit", 2, type=int)

        self.particle_system = ParticleSystem()
        self.particle_system.enabled = self.settings.value("appearance/particles_enabled", True, type=bool)

        self.setWindowTitle("Installify")
        self.setMinimumSize(920, 680)

        self.page_grids = []

        self._build_ui()
        self._apply_theme(self.current_theme)
        self._retranslate_ui()

        self.overlay = PlaylistOverlay(self)
        self.overlay.confirm_signal.connect(self._on_playlist_selected)
        self.overlay.update_texts(self.current_lang)

        self._particle_timer = QTimer(self)
        self._particle_timer.setInterval(40)
        self._particle_timer.timeout.connect(self._advance_particles)
        self._particle_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.size())

    # ==================================================================
    #  UI BUILD
    # ==================================================================
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")
        
        self.page_home = self._build_home_page()
        self.page_settings = self._build_settings_page()
        self.page_about = self._build_about_page()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_about)
        
        root.addWidget(self.stack, stretch=1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(96)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 24, 0, 18)
        layout.setSpacing(6)

        brand = QLabel()
        brand.setPixmap(make_icon("fa5s.atom", color="#e6231e").pixmap(28, 28))
        brand.setObjectName("BrandMark")
        brand.setAlignment(Qt.AlignCenter)
        layout.addWidget(brand, alignment=Qt.AlignHCenter)
        layout.addSpacing(18)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_home = NavButton("fa5s.home", "home")
        self.nav_settings = NavButton("fa5s.cog", "settings")
        self.nav_about = NavButton("fa5s.info-circle", "about")

        for i, btn in enumerate((self.nav_home, self.nav_settings, self.nav_about)):
            self.nav_group.addButton(btn, i)
            layout.addWidget(btn, alignment=Qt.AlignHCenter)

        self.nav_home.setChecked(True)
        self.nav_group.idClicked.connect(self._on_nav_changed)

        layout.addStretch()

        particles_enabled = self.particle_system.enabled
        self.particle_toggle = IconToggleSwitch("fa5s.meteor")
        self.particle_toggle.setChecked(particles_enabled)
        self.particle_toggle.setToolTip("Toggle particle effects")
        self.particle_toggle.toggled.connect(self._on_particles_toggled)
        layout.addWidget(self.particle_toggle, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)

        footer = QLabel("made by\nlight ❤")
        footer.setObjectName("SidebarFooter")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer, alignment=Qt.AlignHCenter)

        return sidebar

    def _on_nav_changed(self, index):
        self.stack.setCurrentIndex(index)

    def _on_particles_toggled(self, checked):
        self.particle_system.enabled = checked
        current = self.stack.currentWidget()
        if current:
            current.update()
        self.settings.setValue("appearance/particles_enabled", checked)

    def _advance_particles(self):
        current = self.stack.currentWidget()
        if not current:
            return
        self.particle_system.advance(current.width(), current.height())
        current.update()

    # ==================================================================
    #  HOME PAGE
    # ==================================================================
    def _build_home_page(self):
        page = GridPage(self.particle_system)
        self.page_grids.append(page)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)

        center = QVBoxLayout()
        center.setSpacing(0)
        center.setAlignment(Qt.AlignHCenter)

        hero_icon = QLabel()
        hero_icon.setPixmap(make_icon("fa5s.atom", color="#e6231e").pixmap(64, 64))
        hero_icon.setObjectName("HeroIcon")
        hero_icon.setAlignment(Qt.AlignCenter)
        center.addWidget(hero_icon, alignment=Qt.AlignHCenter)

        hero_title = QLabel("installify")
        hero_title.setObjectName("HeroTitle")
        hero_title.setAlignment(Qt.AlignCenter)
        center.addWidget(hero_title, alignment=Qt.AlignHCenter)

        hero_sub = QLabel("v1.0")
        hero_sub.setObjectName("HeroSub")
        hero_sub.setAlignment(Qt.AlignCenter)
        center.addWidget(hero_sub, alignment=Qt.AlignHCenter)

        center.addSpacing(36)

        url_card = QFrame()
        url_card.setObjectName("Card")
        url_card.setFixedWidth(560)
        url_card_layout = QVBoxLayout(url_card)
        url_card_layout.setContentsMargins(20, 20, 20, 20)
        url_card_layout.setSpacing(16)

        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setObjectName("PillInput")
        self.url_input.setFixedHeight(46)
        self.url_input.addAction(make_icon("fa5s.link", color="#6b6b6b"), QLineEdit.LeadingPosition)
        self.url_input.textChanged.connect(self._on_url_changed)
        
        self.paste_btn = QPushButton()
        self.paste_btn.setObjectName("IconButton")
        self.paste_btn.setIcon(make_icon("fa5s.paste", color="#dcdcdc"))
        self.paste_btn.setIconSize(QSize(16, 16))
        self.paste_btn.setFixedSize(46, 46)
        self.paste_btn.setCursor(Qt.PointingHandCursor)
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        
        url_row.addWidget(self.url_input, stretch=1)
        url_row.addWidget(self.paste_btn)
        url_card_layout.addLayout(url_row)

        options_row = QHBoxLayout()
        options_row.setSpacing(10)

        self.format_group = QButtonGroup(self)
        self.format_group.setExclusive(True)
        self.chip_mp4 = ChipButton("fa5s.film", "mp4 video")
        self.chip_mp3 = ChipButton("fa5s.music", "mp3 audio")
        self.chip_mp4.setChecked(True)
        self.format_group.addButton(self.chip_mp4, 0)
        self.format_group.addButton(self.chip_mp3, 1)
        self.format_group.idClicked.connect(self._on_format_changed)

        self.quality_combo = QComboBox()
        self.quality_combo.setObjectName("PillCombo")
        self.quality_combo.setFixedHeight(38)
        self.quality_combo.addItems(self.QUALITY_MP4)

        options_row.addWidget(self.chip_mp4)
        options_row.addWidget(self.chip_mp3)
        options_row.addStretch()
        options_row.addWidget(self.quality_combo)
        url_card_layout.addLayout(options_row)

        center.addWidget(url_card, alignment=Qt.AlignHCenter)
        center.addSpacing(20)

        preview_card = QFrame()
        preview_card.setObjectName("Card")
        preview_card.setFixedWidth(560)
        preview_layout = QHBoxLayout(preview_card)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(14)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setObjectName("Thumbnail")
        self.thumbnail_label.setFixedSize(140, 79)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)

        preview_text_col = QVBoxLayout()
        preview_text_col.setSpacing(4)
        self.preview_title_label = QLabel()
        self.preview_title_label.setObjectName("PreviewTitle")
        self.preview_title_label.setWordWrap(True)
        self.preview_meta_label = QLabel("")
        self.preview_meta_label.setObjectName("PreviewMeta")
        preview_text_col.addWidget(self.preview_title_label)
        preview_text_col.addWidget(self.preview_meta_label)
        preview_text_col.addStretch()

        preview_layout.addWidget(self.thumbnail_label)
        preview_layout.addLayout(preview_text_col, stretch=1)
        center.addWidget(preview_card, alignment=Qt.AlignHCenter)
        center.addSpacing(20)

        status_card = QFrame()
        status_card.setObjectName("Card")
        status_card.setFixedWidth(560)
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(12)

        self.status_label = QLabel()
        self.status_label.setObjectName("StatusLabel")
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("Progress")
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)

        self.download_btn = QPushButton()
        self.download_btn.setObjectName("PrimaryButton")
        self.download_btn.setIcon(make_icon("fa5s.download", color="#ffffff"))
        self.download_btn.setIconSize(QSize(16, 16))
        self.download_btn.setFixedHeight(48)
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.clicked.connect(self._start_download)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.download_btn)

        center.addWidget(status_card, alignment=Qt.AlignHCenter)

        outer.addLayout(center)
        outer.addStretch(2)

        self.metadata_timer = QTimer()
        self.metadata_timer.setSingleShot(True)
        self.metadata_timer.setInterval(700)
        self.metadata_timer.timeout.connect(self._fetch_metadata)

        return page

    def _on_format_changed(self, index):
        self.quality_combo.clear()
        if index == 0:  # MP4
            self.quality_combo.addItems(self.QUALITY_MP4)
        else:  # MP3
            self.quality_combo.addItems(self.QUALITY_MP3)

    # ==================================================================
    #  SETTINGS PAGE
    # ==================================================================
    def _build_settings_page(self):
        page = GridPage(self.particle_system)
        self.page_grids.append(page)
        layout = QHBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(36)

        inner_nav_col = QVBoxLayout()
        inner_nav_col.setSpacing(6)

        self.settings_title = QLabel()
        self.settings_title.setObjectName("PageTitle")
        inner_nav_col.addWidget(self.settings_title)
        inner_nav_col.addSpacing(10)

        self.settings_group = QButtonGroup(self)
        self.settings_group.setExclusive(True)
        self.cat_paths = SettingsCategoryButton("fa5s.cog", "Allgemein")
        self.cat_advanced = SettingsCategoryButton("fa5s.folder", "Pfade & Engine")
        self.cat_paths.setChecked(True)
        self.cat_paths.setFixedWidth(220)
        self.cat_advanced.setFixedWidth(220)
        self.settings_group.addButton(self.cat_paths, 0)
        self.settings_group.addButton(self.cat_advanced, 1)

        inner_nav_col.addWidget(self.cat_paths)
        inner_nav_col.addWidget(self.cat_advanced)
        inner_nav_col.addStretch()

        nav_container = QWidget()
        nav_container.setLayout(inner_nav_col)
        nav_container.setFixedWidth(220)
        layout.addWidget(nav_container)

        self.settings_stack = QStackedWidget()
        self.settings_stack.addWidget(self._build_general_panel())
        self.settings_stack.addWidget(self._build_paths_panel())
        layout.addWidget(self.settings_stack, stretch=1)

        self.settings_group.idClicked.connect(self.settings_stack.setCurrentIndex)

        return page

    def _build_general_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        panel = QWidget()
        v = QVBoxLayout(panel)
        v.setSpacing(14)
        v.setAlignment(Qt.AlignTop)

        # 1. Design Combo
        row_design = QHBoxLayout()
        self.lbl_design = QLabel()
        self.lbl_design.setObjectName("SectionHeading")
        self.combo_design = QComboBox()
        self.combo_design.setObjectName("PillCombo")
        self.combo_design.setFixedWidth(180)
        self.combo_design.addItems(self.THEME_OPTIONS)
        
        idx_t = self.combo_design.findText(self.current_theme)
        if idx_t >= 0:
            self.combo_design.setCurrentIndex(idx_t)
        self.combo_design.currentTextChanged.connect(self._on_theme_changed)

        row_design.addWidget(self.lbl_design)
        row_design.addStretch()
        row_design.addWidget(self.combo_design)
        v.addLayout(row_design)

        # 2. Sprache Combo
        row_lang = QHBoxLayout()
        self.lbl_lang = QLabel()
        self.lbl_lang.setObjectName("SectionHeading")
        self.combo_lang = QComboBox()
        self.combo_lang.setObjectName("PillCombo")
        self.combo_lang.setFixedWidth(180)
        self.combo_lang.addItems(self.LANG_OPTIONS)

        idx_l = self.combo_lang.findText(self.current_lang)
        if idx_l >= 0:
            self.combo_lang.setCurrentIndex(idx_l)
        self.combo_lang.currentTextChanged.connect(self._on_language_changed)

        row_lang.addWidget(self.lbl_lang)
        row_lang.addStretch()
        row_lang.addWidget(self.combo_lang)
        v.addLayout(row_lang)

        def create_toggle_row(label_widget, default_state, callback):
            row = QHBoxLayout()
            label_widget.setObjectName("SectionHeading")
            toggle = IconToggleSwitch("fa5s.check")
            toggle.setChecked(default_state)
            toggle.toggled.connect(callback)
            row.addWidget(label_widget)
            row.addStretch()
            row.addWidget(toggle)
            return row

        # Toggles
        self.lbl_subtitles = QLabel()
        self.lbl_metadata = QLabel()
        self.lbl_skip = QLabel()

        v.addLayout(create_toggle_row(self.lbl_subtitles, self.embed_subtitles, self._on_embed_subtitles_toggled))
        v.addLayout(create_toggle_row(self.lbl_metadata, self.embed_metadata, self._on_embed_metadata_toggled))
        v.addLayout(create_toggle_row(self.lbl_skip, self.skip_existing, self._on_skip_existing_toggled))

        # Dateinamen-Vorlage
        row_tmpl = QHBoxLayout()
        self.lbl_tmpl = QLabel()
        self.lbl_tmpl.setObjectName("SectionHeading")
        self.input_tmpl = QLineEdit(self.filename_template)
        self.input_tmpl.setObjectName("PillInput")
        self.input_tmpl.setFixedWidth(200)
        self.input_tmpl.textChanged.connect(self._on_tmpl_changed)
        row_tmpl.addWidget(self.lbl_tmpl)
        row_tmpl.addStretch()
        row_tmpl.addWidget(self.input_tmpl)
        v.addLayout(row_tmpl)

        # Paralleles Limit
        row_par = QHBoxLayout()
        self.lbl_parallel = QLabel()
        self.lbl_parallel.setObjectName("SectionHeading")
        self.lbl_par_val = QLabel(str(self.parallel_limit))
        self.lbl_par_val.setObjectName("SectionDesc")
        
        self.slider_par = QSlider(Qt.Horizontal)
        self.slider_par.setRange(1, 10)
        self.slider_par.setValue(self.parallel_limit)
        self.slider_par.setFixedWidth(140)
        self.slider_par.valueChanged.connect(self._on_parallel_slider_changed)

        row_par.addWidget(self.lbl_parallel)
        row_par.addStretch()
        row_par.addWidget(self.lbl_par_val)
        row_par.addWidget(self.slider_par)
        v.addLayout(row_par)

        v.addStretch()
        scroll.setWidget(panel)
        return scroll

    def _on_theme_changed(self, theme_text):
        self.current_theme = theme_text
        self.settings.setValue("appearance/theme", theme_text)
        self._apply_theme(theme_text)

    def _on_language_changed(self, lang_text):
        self.current_lang = lang_text
        self.settings.setValue("appearance/language", lang_text)
        self._retranslate_ui()
        self.overlay.update_texts(lang_text)

    def _on_embed_subtitles_toggled(self, checked):
        self.embed_subtitles = checked
        self.settings.setValue("dl/embed_subtitles", checked)

    def _on_embed_metadata_toggled(self, checked):
        self.embed_metadata = checked
        self.settings.setValue("dl/embed_metadata", checked)

    def _on_skip_existing_toggled(self, checked):
        self.skip_existing = checked
        self.settings.setValue("dl/skip_existing", checked)

    def _on_tmpl_changed(self, text):
        self.filename_template = text
        self.settings.setValue("dl/filename_template", text)

    def _on_parallel_slider_changed(self, value):
        self.parallel_limit = value
        self.lbl_par_val.setText(str(value))
        self.settings.setValue("dl/parallel_limit", value)

    def _build_paths_panel(self):
        panel = QWidget()
        v = QVBoxLayout(panel)
        v.setSpacing(16)
        v.setAlignment(Qt.AlignTop)

        self.heading_paths = QLabel()
        self.heading_paths.setObjectName("SectionHeading")
        v.addWidget(self.heading_paths)

        # FFmpeg-Pfad
        self.lbl_ffmpeg = QLabel()
        self.lbl_ffmpeg.setObjectName("FieldLabel")
        v.addWidget(self.lbl_ffmpeg)

        ffmpeg_row = QHBoxLayout()
        ffmpeg_row.setSpacing(8)
        self.ffmpeg_display = QLineEdit(self.ffmpeg_path)
        self.ffmpeg_display.setObjectName("PillInput")
        self.ffmpeg_display.setFixedHeight(42)
        self.ffmpeg_display.textChanged.connect(self._on_ffmpeg_text_changed)

        btn_clear_ffmpeg = QPushButton()
        btn_clear_ffmpeg.setObjectName("IconButton")
        btn_clear_ffmpeg.setIcon(make_icon("fa5s.times", color="#8a8a8a"))
        btn_clear_ffmpeg.setFixedSize(42, 42)
        btn_clear_ffmpeg.setCursor(Qt.PointingHandCursor)
        btn_clear_ffmpeg.clicked.connect(self._clear_ffmpeg_path)

        btn_browse_ffmpeg = QPushButton()
        btn_browse_ffmpeg.setObjectName("IconButton")
        btn_browse_ffmpeg.setIcon(make_icon("fa5s.folder-open", color="#dcdcdc"))
        btn_browse_ffmpeg.setFixedSize(42, 42)
        btn_browse_ffmpeg.setCursor(Qt.PointingHandCursor)
        btn_browse_ffmpeg.clicked.connect(self._choose_ffmpeg_path)

        ffmpeg_row.addWidget(self.ffmpeg_display, stretch=1)
        ffmpeg_row.addWidget(btn_clear_ffmpeg)
        ffmpeg_row.addWidget(btn_browse_ffmpeg)
        v.addLayout(ffmpeg_row)

        v.addSpacing(10)

        # Video folder
        self.lbl_video_folder = QLabel()
        self.lbl_video_folder.setObjectName("FieldLabel")
        v.addWidget(self.lbl_video_folder)
        video_row = QHBoxLayout()
        video_row.setSpacing(10)
        self.mp4_folder_display = QLineEdit(self.mp4_folder)
        self.mp4_folder_display.setObjectName("PillInput")
        self.mp4_folder_display.setReadOnly(True)
        self.mp4_folder_display.setFixedHeight(42)
        self.mp4_folder_btn = QPushButton()
        self.mp4_folder_btn.setObjectName("IconButton")
        self.mp4_folder_btn.setIcon(make_icon("fa5s.folder-open", color="#dcdcdc"))
        self.mp3_folder_btn_fixed = False
        self.mp4_folder_btn.setFixedSize(42, 42)
        self.mp4_folder_btn.setCursor(Qt.PointingHandCursor)
        self.mp4_folder_btn.clicked.connect(lambda: self._choose_folder("MP4"))
        video_row.addWidget(self.mp4_folder_display, stretch=1)
        video_row.addWidget(self.mp4_folder_btn)
        v.addLayout(video_row)

        # Audio folder
        self.lbl_audio_folder = QLabel()
        self.lbl_audio_folder.setObjectName("FieldLabel")
        v.addWidget(self.lbl_audio_folder)
        audio_row = QHBoxLayout()
        audio_row.setSpacing(10)
        self.mp3_folder_display = QLineEdit(self.mp3_folder)
        self.mp3_folder_display.setObjectName("PillInput")
        self.mp3_folder_display.setReadOnly(True)
        self.mp3_folder_display.setFixedHeight(42)
        self.mp3_folder_btn = QPushButton()
        self.mp3_folder_btn.setObjectName("IconButton")
        self.mp3_folder_btn.setIcon(make_icon("fa5s.folder-open", color="#dcdcdc"))
        self.mp3_folder_btn.setFixedSize(42, 42)
        self.mp3_folder_btn.setCursor(Qt.PointingHandCursor)
        self.mp3_folder_btn.clicked.connect(lambda: self._choose_folder("MP3"))
        audio_row.addWidget(self.mp3_folder_display, stretch=1)
        audio_row.addWidget(self.mp3_folder_btn)
        v.addLayout(audio_row)

        v.addSpacing(10)

        # Cookie browser
        self.lbl_cookies = QLabel()
        self.lbl_cookies.setObjectName("FieldLabel")
        v.addWidget(self.lbl_cookies)

        self.cookie_combo = QComboBox()
        self.cookie_combo.setObjectName("PillCombo")
        self.cookie_combo.setFixedHeight(42)
        self.cookie_combo.addItems(self.COOKIE_BROWSERS)
        
        current_browser = self.cookie_browser if self.cookie_browser else "none"
        idx = self.cookie_combo.findText(current_browser)
        if idx >= 0:
            self.cookie_combo.setCurrentIndex(idx)
            
        self.cookie_combo.currentTextChanged.connect(self._on_cookie_browser_changed)
        v.addWidget(self.cookie_combo)

        v.addStretch()
        return panel

    def _on_ffmpeg_text_changed(self, text):
        self.ffmpeg_path = text
        self.settings.setValue("advanced/ffmpeg_path", text)

    def _choose_ffmpeg_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "FFmpeg Executable", "", "Executables (*.exe);;All Files (*)"
        )
        if file_path:
            folder_or_path = os.path.dirname(file_path) if file_path.endswith(".exe") else file_path
            self.ffmpeg_path = folder_or_path
            self.ffmpeg_display.setText(folder_or_path)
            self.settings.setValue("advanced/ffmpeg_path", folder_or_path)

    def _clear_ffmpeg_path(self):
        self.ffmpeg_path = ""
        self.ffmpeg_display.setText("")
        self.settings.setValue("advanced/ffmpeg_path", "")

    def _on_cookie_browser_changed(self, text):
        self.cookie_browser = "none" if text == "none" else text
        self.settings.setValue("advanced/cookie_browser", self.cookie_browser)

    # ==================================================================
    #  ABOUT PAGE
    # ==================================================================
    def _build_about_page(self):
        page = GridPage(self.particle_system)
        self.page_grids.append(page)
        v = QVBoxLayout(page)
        v.setContentsMargins(48, 48, 48, 48)
        v.setSpacing(20)
        v.setAlignment(Qt.AlignTop)

        self.about_title = QLabel()
        self.about_title.setObjectName("PageTitle")
        v.addWidget(self.about_title)

        self.about_q1 = QLabel()
        self.about_q1.setObjectName("SectionHeading")
        self.about_a1 = QLabel()
        self.about_a1.setObjectName("SectionDesc")
        self.about_a1.setWordWrap(True)

        self.about_q2 = QLabel()
        self.about_q2.setObjectName("SectionHeading")
        self.about_a2 = QLabel()
        self.about_a2.setObjectName("SectionDesc")
        self.about_a2.setWordWrap(True)

        self.about_q3 = QLabel()
        self.about_q3.setObjectName("SectionHeading")
        self.about_a3 = QLabel()
        self.about_a3.setObjectName("SectionDesc")
        self.about_a3.setWordWrap(True)

        v.addWidget(self.about_q1)
        v.addWidget(self.about_a1)
        v.addSpacing(6)

        v.addWidget(self.about_q2)
        v.addWidget(self.about_a2)
        v.addSpacing(6)

        v.addWidget(self.about_q3)
        v.addWidget(self.about_a3)
        v.addSpacing(6)

        v.addStretch()

        footer = QLabel("installify v1.0 — made by light with ❤")
        footer.setObjectName("SidebarFooter")
        v.addWidget(footer)

        return page

    # ==================================================================
    #  TRANSLATION & THEME LOGIC
    # ==================================================================
    def _retranslate_ui(self):
        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])

        self.nav_home.setToolTip(s["nav_home"])
        self.nav_settings.setToolTip(s["nav_settings"])
        self.nav_about.setToolTip(s["nav_about"])

        self.url_input.setPlaceholderText(s["placeholder_url"])
        self.paste_btn.setToolTip(s["btn_paste"])
        self.chip_mp4.setText(f"  {s['chip_mp4']}")
        self.chip_mp3.setText(f"  {s['chip_mp3']}")
        
        if not self.thumbnail_label.pixmap():
            self.thumbnail_label.setText(s["no_image"])
            
        if self.preview_title_label.text() in [STRINGS["Deutsch"]["preview_placeholder"], STRINGS["English"]["preview_placeholder"], ""]:
            self.preview_title_label.setText(s["preview_placeholder"])
            
        self.status_label.setText(s["status_ready"])
        self.download_btn.setText(s["btn_download"])

        self.settings_title.setText(s["settings_title"])
        self.cat_paths.setText(f"   {s['cat_general']}")
        self.cat_advanced.setText(f"   {s['cat_paths']}")
        self.lbl_design.setText(s["lbl_design"])
        self.lbl_lang.setText(s["lbl_lang"])
        self.lbl_subtitles.setText(s["lbl_subtitles"])
        self.lbl_metadata.setText(s["lbl_metadata"])
        self.lbl_skip.setText(s["lbl_skip"])
        self.lbl_tmpl.setText(s["lbl_tmpl"])
        self.lbl_parallel.setText(s["lbl_parallel"])

        self.heading_paths.setText(s["heading_paths"])
        self.lbl_ffmpeg.setText(s["lbl_ffmpeg"])
        self.ffmpeg_display.setPlaceholderText(s["ph_ffmpeg"])
        self.lbl_video_folder.setText(s["lbl_video_folder"])
        self.lbl_audio_folder.setText(s["lbl_audio_folder"])
        self.lbl_cookies.setText(s["lbl_cookies"])

        self.about_title.setText(s["about_title"])
        self.about_q1.setText(s["about_q1"])
        self.about_a1.setText(s["about_a1"])
        self.about_q2.setText(s["about_q2"])
        self.about_a2.setText(s["about_a2"])
        self.about_q3.setText(s["about_q3"])
        self.about_a3.setText(s["about_a3"])

    def _apply_theme(self, theme_mode):
            if theme_mode == "System":
                app = QApplication.instance()
                is_dark = app.palette().color(QPalette.Window).value() < 128
            elif theme_mode == "Light":
                is_dark = False
            else:  # Dark
                is_dark = True

            if is_dark:
                bg_main = "#000000"
                bg_sidebar = "#000000"
                border_sidebar = "#161616"
                card_bg = "#0a0a0a"
                card_border = "#1c1c1c"
                input_bg = "#131313"
                input_border = "#262626"
                text_main = "#d8d8d8"
                text_title = "#f2f2f2"
                text_sub = "#6b6b6b"
                chip_bg = "#101010"
                chip_border = "#242424"
                chip_text = "#8a8a8a"
                # Im Dark Mode: Hellgrau als Akzent
                chip_checked_bg = "#e8e8e8"
                chip_checked_text = "#000000"
                nav_active_bg = "#e8e8e8"
                grid_bg = QColor("#000000")
                grid_line = QColor(255, 255, 255, 10)
                particle_color = QColor(255, 255, 255)
            else:
                bg_main = "#f5f5f7"
                bg_sidebar = "#ffffff"
                border_sidebar = "#e0e0e8"
                card_bg = "#ffffff"
                card_border = "#e2e2e8"
                input_bg = "#f0f0f4"
                input_border = "#d0d0d8"
                text_main = "#222222"
                text_title = "#000000"
                text_sub = "#777777"
                chip_bg = "#ffffff"
                chip_border = "#d5d5de"
                chip_text = "#555555"
                # Im Light Mode: Schickes Installify-Rot statt Schwarz!
                chip_checked_bg = "#e6231e"
                chip_checked_text = "#ffffff"
                nav_active_bg = "#feebe8"  # Sanftes Rot-Highlight für die Sidebar
                grid_bg = QColor("#f5f5f7")
                grid_line = QColor(0, 0, 0, 12)
                particle_color = QColor(180, 180, 180)

            for grid in self.page_grids:
                grid.bg_color = grid_bg
                grid.line_color = grid_line
                grid.update()

            self.particle_system.color = particle_color

            # Icons dynamisch an das Farbschema der Sidebar anpassen
            nav_icon_color_on = "#000000" if is_dark else "#e6231e"
            self.nav_home.setIcon(make_icon("fa5s.home", color="#6b6b6b", color_on=nav_icon_color_on))
            self.nav_settings.setIcon(make_icon("fa5s.cog", color="#6b6b6b", color_on=nav_icon_color_on))
            self.nav_about.setIcon(make_icon("fa5s.info-circle", color="#6b6b6b", color_on=nav_icon_color_on))

            stylesheet = f"""
                QWidget {{
                    background-color: {bg_main};
                    color: {text_main};
                    font-family: 'Cascadia Code', 'JetBrains Mono', Consolas, 'Courier New', monospace;
                    font-size: 13px;
                }}

                QFrame#OverlayBg {{
                    background-color: rgba(0, 0, 0, 0.55);
                }}

                /* ---------- SIDEBAR ---------- */
                QFrame#Sidebar {{
                    background-color: {bg_sidebar};
                    border-right: 1px solid {border_sidebar};
                }}
                QLabel#BrandMark {{
                    font-size: 26px;
                    color: #e6231e;
                }}
                QLabel#SidebarFooter {{
                    font-size: 10px;
                    color: {text_sub};
                    line-height: 140%;
                }}

                QToolButton#NavButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 12px;
                }}
                QToolButton#NavButton:hover {{
                    background-color: {input_bg};
                }}
                QToolButton#NavButton:checked {{
                    background-color: {nav_active_bg};
                }}

                /* ---------- CONTENT AREA ---------- */
                QStackedWidget#ContentArea {{
                    background-color: {bg_main};
                }}

                QLabel#HeroIcon {{
                    margin-bottom: 6px;
                }}
                QLabel#HeroTitle {{
                    font-size: 28px;
                    font-weight: 800;
                    color: {text_title};
                    letter-spacing: 4px;
                }}
                QLabel#HeroSub {{
                    font-size: 11px;
                    color: {text_sub};
                    margin-bottom: 4px;
                }}

                QFrame#Card {{
                    background-color: {card_bg};
                    border: 1px solid {card_border};
                    border-radius: 16px;
                }}

                QLineEdit#PillInput {{
                    background-color: {input_bg};
                    border: 1px solid {input_border};
                    border-radius: 23px;
                    padding: 0 18px;
                    color: {text_main};
                    font-size: 13px;
                    selection-background-color: #e6231e;
                }}
                QLineEdit#PillInput:focus {{
                    border: 1px solid #e6231e;
                }}

                QPushButton#IconButton {{
                    background-color: {input_bg};
                    border: 1px solid {input_border};
                    border-radius: 12px;
                }}
                QPushButton#IconButton:hover {{
                    border: 1px solid #e6231e;
                }}

                QPushButton#Chip {{
                    background-color: {chip_bg};
                    border: 1px solid {chip_border};
                    border-radius: 19px;
                    padding: 0 16px;
                    color: {chip_text};
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton#Chip:hover {{
                    border: 1px solid #e6231e;
                }}
                QPushButton#Chip:checked {{
                    background-color: {chip_checked_bg};
                    border: 1px solid {chip_checked_bg};
                    color: {chip_checked_text};
                }}

                QComboBox#PillCombo {{
                    background-color: {chip_bg};
                    border: 1px solid {chip_border};
                    border-radius: 19px;
                    padding: 0 14px;
                    color: {text_main};
                    font-size: 12px;
                }}
                QComboBox#PillCombo:hover {{
                    border: 1px solid #e6231e;
                }}

                QSlider::groove:horizontal {{
                    border: 1px solid {input_border};
                    height: 6px;
                    background: {input_bg};
                    border-radius: 3px;
                }}
                QSlider::sub-page:horizontal {{
                    background: #e6231e;
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: {chip_checked_bg};
                    border: none;
                    width: 14px;
                    margin-top: -4px;
                    margin-bottom: -4px;
                    border-radius: 7px;
                }}

                QLabel#Thumbnail {{
                    background-color: {input_bg};
                    border: 1px solid {input_border};
                    border-radius: 10px;
                    color: {text_sub};
                    font-size: 10px;
                }}
                QLabel#PreviewTitle {{
                    font-size: 13px;
                    font-weight: 700;
                    color: {text_main};
                }}
                QLabel#PreviewMeta {{
                    font-size: 11px;
                    color: {text_sub};
                }}

                QLabel#StatusLabel {{
                    font-size: 12px;
                    color: {text_sub};
                }}
                QProgressBar#Progress {{
                    background-color: {input_bg};
                    border: 1px solid {input_border};
                    border-radius: 10px;
                    text-align: center;
                    color: {text_main};
                    font-size: 11px;
                }}
                QProgressBar#Progress::chunk {{
                    background-color: #e6231e;
                    border-radius: 10px;
                }}

                QPushButton#PrimaryButton {{
                    background-color: #e6231e;
                    color: #ffffff;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 700;
                }}
                QPushButton#PrimaryButton:hover {{
                    background-color: #ff2e28;
                }}
                QPushButton#PrimaryButton:pressed {{
                    background-color: #c81c17;
                }}

                /* ---------- SETTINGS / ABOUT ---------- */
                QLabel#PageTitle {{
                    font-size: 22px;
                    font-weight: 800;
                    color: {text_title};
                    letter-spacing: 1px;
                    margin-bottom: 6px;
                }}
                QLabel#SectionHeading {{
                    font-size: 13px;
                    font-weight: 700;
                    color: {text_main};
                }}
                QLabel#SectionDesc {{
                    font-size: 12px;
                    color: {text_sub};
                }}
                QLabel#FieldLabel {{
                    font-size: 11px;
                    font-weight: 700;
                    color: {text_sub};
                    text-transform: lowercase;
                    letter-spacing: 0.5px;
                    margin-top: 8px;
                }}

                QPushButton#SettingsCategory {{
                    background-color: transparent;
                    border: none;
                    border-radius: 10px;
                    color: {text_sub};
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton#SettingsCategory:hover {{
                    background-color: {input_bg};
                    color: {text_main};
                }}
                QPushButton#SettingsCategory:checked {{
                    background-color: {card_bg};
                    color: {text_title};
                    border: 1px solid {card_border};
                }}

                QScrollArea#OverlayScroll {{
                    border: 1px solid {card_border};
                    background: {input_bg};
                    border-radius: 8px;
                }}
                QCheckBox {{
                    color: {text_main};
                    font-size: 12px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
            """
            self.setStyleSheet(stylesheet)

    # ==================================================================
    #  DOWNLOAD & METADATA LOGIC
    # ==================================================================
    def _paste_from_clipboard(self):
        clipboard_text = QApplication.clipboard().text().strip()
        if clipboard_text:
            self.url_input.setText(clipboard_text)

    def _on_url_changed(self, text):
        self.selected_playlist_urls = None
        self._reset_preview()
        self.metadata_timer.stop()
        if self._validate_url(text):
            self.metadata_timer.start()

    def _reset_preview(self):
        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
        self.thumbnail_label.setPixmap(QPixmap())
        self.thumbnail_label.setText(s["no_image"])
        self.preview_title_label.setText(s["preview_placeholder"])
        self.preview_meta_label.setText("")

    def _fetch_metadata(self):
        url = self.url_input.text().strip()
        if not self._validate_url(url):
            return

        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
        self.preview_title_label.setText(s["preview_fetching"])
        self.preview_meta_label.setText("")

        self.metadata_request_id += 1
        current_id = self.metadata_request_id

        self.metadata_worker = MetadataWorker(url, current_id, self.cookie_browser)
        self.metadata_worker.metadata_signal.connect(self._on_metadata_ready)
        self.metadata_worker.error_signal.connect(self._on_metadata_error)
        self.metadata_worker.start()

    def _on_metadata_ready(self, data):
        if data.get("request_id") != self.metadata_request_id:
            return

        if data.get("is_playlist"):
            playlist_title = data.get("playlist_title", "Playlist")
            entries = data.get("entries", [])
            self.preview_title_label.setText(f"Playlist: {playlist_title}")
            self.preview_meta_label.setText(f"{len(entries)} items found")
            self.thumbnail_label.setText("playlist")

            self.overlay.load_playlist(playlist_title, entries)
        else:
            self.preview_title_label.setText(data.get("title", "Unknown Title"))

            duration = data.get("duration")
            uploader = data.get("uploader", "")
            meta_parts = []
            if uploader:
                meta_parts.append(uploader)
            if duration:
                minutes, seconds = divmod(int(duration), 60)
                meta_parts.append(f"{minutes}:{seconds:02d}")
            self.preview_meta_label.setText(" • ".join(meta_parts))

            thumbnail_bytes = data.get("thumbnail_bytes")
            if thumbnail_bytes:
                pixmap = QPixmap()
                pixmap.loadFromData(thumbnail_bytes)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        140, 79, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                    )
                    self.thumbnail_label.setText("")
                    self.thumbnail_label.setPixmap(rounded_pixmap(scaled, 10))
                else:
                    s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
                    self.thumbnail_label.setText(s["no_image"])
            else:
                s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
                self.thumbnail_label.setText(s["no_image"])

    def _on_playlist_selected(self, urls):
        self.selected_playlist_urls = urls
        self.preview_meta_label.setText(f"Selected: {len(urls)} video(s)")

    def _on_metadata_error(self, message):
        self.preview_title_label.setText("failed to fetch info")
        self.preview_meta_label.setText("")

    def _validate_url(self, url):
        pattern = r"(https?://)?(www\.)?(youtube\.com/|youtu\.be/)[\w-]+"
        return bool(re.match(pattern, url.strip()))

    def _choose_folder(self, mode):
        current_folder = self.mp4_folder if mode == "MP4" else self.mp3_folder
        folder = QFileDialog.getExistingDirectory(
            self, f"Select folder for {mode}", current_folder
        )
        if not folder:
            return

        if mode == "MP4":
            self.mp4_folder = folder
            self.mp4_folder_display.setText(folder)
            self.settings.setValue("paths/mp4_folder", folder)
        else:
            self.mp3_folder = folder
            self.mp3_folder_display.setText(folder)
            self.settings.setValue("paths/mp3_folder", folder)

    def _start_download(self):
        url = self.url_input.text().strip()
        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])

        if not url or not self._validate_url(url):
            self._show_error(s["err_invalid_url"])
            return

        download_targets = self.selected_playlist_urls if self.selected_playlist_urls else url

        mode = "MP4" if self.chip_mp4.isChecked() else "MP3"
        quality = self.quality_combo.currentText()
        target_folder = self.mp4_folder if mode == "MP4" else self.mp3_folder

        try:
            os.makedirs(target_folder, exist_ok=True)
        except OSError as e:
            self._show_error(f"{s['err_folder']}\n{e}")
            return

        self._set_ui_busy(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(s["status_connecting"])

        config = {
            "prefer_h264": self.prefer_h264,
            "cookie_browser": self.cookie_browser,
            "ffmpeg_path": self.ffmpeg_path,
            "embed_subtitles": self.embed_subtitles,
            "embed_metadata": self.embed_metadata,
            "skip_existing": self.skip_existing,
            "filename_template": self.filename_template,
            "parallel_limit": self.parallel_limit,
        }

        self.worker = DownloadWorker(
            download_targets, target_folder, mode, quality, config=config
        )
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.status_signal.connect(self.status_label.setText)
        self.worker.finished_signal.connect(self._on_download_finished)
        self.worker.start()

    def _on_download_finished(self, success, message):
        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
        self._set_ui_busy(False)
        if success:
            self.status_label.setText(s["status_done"])
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", s["succ_download"])
        else:
            self.status_label.setText(s["status_error"])
            self.progress_bar.setValue(0)
            self._show_error(f"Something went wrong:\n\n{message}")

    def _set_ui_busy(self, busy):
        s = STRINGS.get(self.current_lang, STRINGS["Deutsch"])
        self.download_btn.setEnabled(not busy)
        self.url_input.setEnabled(not busy)
        self.paste_btn.setEnabled(not busy)
        self.chip_mp4.setEnabled(not busy)
        self.chip_mp3.setEnabled(not busy)
        self.quality_combo.setEnabled(not busy)
        self.download_btn.setText(s["btn_wait"] if busy else s["btn_download"])

    def _show_error(self, text):
        QMessageBox.critical(self, "Error", text)


# ----------------------------------------------------------------------
#  ENTRY POINT
# ----------------------------------------------------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "InstallifyApps.InstallifyDownloader.1.0"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)

    icon_path = resource_path("installify.ico")
    if os.path.exists(icon_path):
        from PySide6.QtGui import QIcon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    window = InstallifyApp()
    if os.path.exists(icon_path):
        window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()