"""
Mobile entry point (BeeWare/Toga) for the Book of Mormon app.

This module reuses existing logic from list_parser.py and leaves my_gui.py unchanged.
"""

from __future__ import annotations

import json
import math
import os
import struct
import threading
import tempfile
import traceback
import urllib.parse
import urllib.request
import zlib

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from list_parser import (
    TITLES_OF_CHRIST_FILEPATH,
    book_of_mormon_parser,
    counts_per_book,
    get_chosen_titles_of_christ,
    title_counter,
    titles_of_christ_parser,
)

BOOK_NAMES = [
    "1 Nephi",
    "2 Nephi",
    "Jacob",
    "Enos",
    "Jarom",
    "Omni",
    "Words of Mormon",
    "Mosiah",
    "Alma",
    "Helaman",
    "3 Nephi",
    "4 Nephi",
    "Mormon",
    "Ether",
    "Moroni",
]

PIE_COLORS = [
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
    "#9C755F",
    "#BAB0AC",
]


class BookOfMormonMobileApp(toga.App):
    def startup(self):
        try:
            self.verses = {}
            self.counts = {}
            self.instances = {}
            self.counts_by_book = {}
            self.ref_to_verse_text = {}
            self.is_loading = True

            self.search_input = toga.TextInput(placeholder="Search word or phrase...", style=Pack(flex=1))
            self.title_input = toga.TextInput(placeholder="Title (e.g., jesus christ)", style=Pack(flex=1))
            self.pie_amount_input = toga.TextInput(value="20", placeholder="Pie slices (5-30)", style=Pack(width=130))
            self.search_input.readonly = False
            self.title_input.readonly = False
            self.pie_amount_input.readonly = False
            self.status_label = toga.Label("Loading data, please wait...", style=Pack(margin_bottom=6))
            self.output = toga.MultilineTextInput(
                value="App started.",
                readonly=True,
                style=Pack(height=140, margin_top=10),
            )
            self.chart_title_label = toga.Label("Chart: none", style=Pack(margin_top=10, margin_bottom=6))
            self.chart_image_view = toga.ImageView(style=Pack(height=280, margin_bottom=8))
            self.chart_output = toga.MultilineTextInput(
                value="Chart details will appear here.",
                readonly=True,
                style=Pack(height=180, margin_bottom=12),
            )
            self._chart_image = None
            self._chart_job_token = 0

            self.search_button = toga.Button("Search", on_press=self.on_search, style=Pack(margin_left=8))
            self.stats_button = toga.Button("Title Stats", on_press=self.on_title_stats, style=Pack(margin_left=8))
            self.line_button = toga.Button("Line Chart", on_press=self.on_line_chart, style=Pack(margin_left=8))
            self.pie_button = toga.Button("Pie Chart", on_press=self.on_pie_chart, style=Pack(margin_left=8))
            self._set_action_buttons_enabled(False)

            search_row = toga.Box(
                children=[self.search_input, self.search_button],
                style=Pack(direction=ROW, margin_bottom=8),
            )
            title_row = toga.Box(
                children=[self.title_input, self.stats_button, self.line_button],
                style=Pack(direction=ROW, margin_bottom=8),
            )
            pie_row = toga.Box(
                children=[self.pie_amount_input, self.pie_button],
                style=Pack(direction=ROW),
            )

            main_box = toga.Box(
                children=[
                    toga.Label("Book of Mormon Mobile", style=Pack(margin_bottom=6, font_size=16)),
                    self.status_label,
                    search_row,
                    title_row,
                    pie_row,
                    self.output,
                    self.chart_title_label,
                    self.chart_image_view,
                    self.chart_output,
                ],
                style=Pack(direction=COLUMN, margin=10, flex=1),
            )
            scroll = toga.ScrollContainer(horizontal=False, style=Pack(flex=1))
            scroll.content = main_box

            self.main_window = toga.MainWindow(title=self.formal_name)
            self.main_window.content = scroll
            self.main_window.show()

            loader = threading.Thread(target=self._load_data_worker, daemon=True)
            loader.start()
        except Exception:
            fallback = traceback.format_exc()
            self.main_window = toga.MainWindow(title=self.formal_name)
            self.main_window.content = toga.Box(
                children=[toga.Label("Startup failure:\n" + fallback, style=Pack(margin=10))],
                style=Pack(direction=COLUMN),
            )
            self.main_window.show()

    def _set_action_buttons_enabled(self, enabled: bool):
        self.search_button.enabled = enabled
        self.stats_button.enabled = enabled
        self.line_button.enabled = enabled
        self.pie_button.enabled = enabled

    def _restore_input_focus(self):
        for field in (self.search_input, self.title_input, self.pie_amount_input):
            try:
                field.focus()
                return
            except Exception:
                continue

    def _load_data_worker(self):
        try:
            verses = book_of_mormon_parser()
            all_titles = titles_of_christ_parser(TITLES_OF_CHRIST_FILEPATH)
            counts, instances = title_counter(verses, all_titles)
            counts_by_book = counts_per_book(instances)
            ref_to_verse_text = {verse_ref: verse_text for verse_text, verse_ref in verses.items()}
            self.loop.call_soon_threadsafe(
                self._on_data_loaded,
                verses,
                counts,
                instances,
                counts_by_book,
                ref_to_verse_text,
                None,
            )
        except Exception as exc:
            self.loop.call_soon_threadsafe(
                self._on_data_loaded,
                {},
                {},
                {},
                {},
                {},
                str(exc),
            )

    def _on_data_loaded(self, verses, counts, instances, counts_by_book, ref_to_verse_text, error_message):
        if error_message:
            self.status_label.text = "Load failed."
            self.output.value = f"Failed to load data:\n{error_message}"
            self.is_loading = False
            return

        self.verses = verses
        self.counts = counts
        self.instances = instances
        self.counts_by_book = counts_by_book
        self.ref_to_verse_text = ref_to_verse_text
        self.is_loading = False
        self._set_action_buttons_enabled(True)
        self.status_label.text = "Ready."
        self.output.value = "Ready. Use Search, Title Stats, Line Chart, or Pie Chart."

    def on_search(self, widget):
        if self.is_loading:
            self.output.value = "Still loading data. Please wait..."
            return

        term = (self.search_input.value or "").strip().lower()
        if not term:
            self.output.value = "Enter a search term."
            return

        verses_with_search_term = []
        _, search_instances = title_counter(self.verses, [term])
        if term in search_instances:
            for ref in search_instances[term]:
                verse_text = self.ref_to_verse_text.get(ref)
                if verse_text is not None:
                    verses_with_search_term.append((verse_text, ref))

        if not verses_with_search_term:
            self.output.value = f'No matches for "{term}".'
            return

        lines = [f'Found {len(verses_with_search_term)} matches for "{term}"', ""]
        for verse_text, verse_ref in verses_with_search_term[:100]:
            lines.append(f"{verse_ref}")
            lines.append(f"{verse_text}")
            lines.append("")
        if len(verses_with_search_term) > 100:
            lines.append("Showing first 100 matches.")
        self.output.value = "\n".join(lines)

    def on_title_stats(self, widget):
        if self.is_loading:
            self.output.value = "Still loading data. Please wait..."
            return

        title = (self.title_input.value or "").strip().lower()
        if not title:
            self.output.value = "Enter a title."
            return

        total = self.counts.get(title, 0)
        if total == 0:
            self.output.value = f'"{title}" was not found.'
            return

        per_book = self.counts_by_book.get(title, [])
        lines = [f'Title: "{title}"', f"Total count: {total}", ""]
        for name, count in zip(BOOK_NAMES, per_book):
            lines.append(f"{name}: {count}")
        self.output.value = "\n".join(lines)

    def on_line_chart(self, widget):
        if self.is_loading:
            self.output.value = "Still loading data. Please wait..."
            return

        title = (self.title_input.value or "").strip().lower()
        if not title:
            self.output.value = "Enter a title for the line chart."
            return

        values = self.counts_by_book.get(title, [])
        if not values:
            self.output.value = f'"{title}" was not found.'
            return

        self._chart_job_token += 1
        token = self._chart_job_token
        self.line_button.enabled = False
        self.pie_button.enabled = False
        self.output.value = "Rendering line chart..."
        self.status_label.text = "Rendering chart..."
        values_copy = list(values)
        threading.Thread(
            target=self._line_chart_worker,
            args=(token, title, values_copy),
            daemon=True,
        ).start()

    def on_pie_chart(self, widget):
        if self.is_loading:
            self.output.value = "Still loading data. Please wait..."
            return

        amount_raw = (self.pie_amount_input.value or "20").strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            self.output.value = "Pie slices must be an integer."
            return
        amount = max(5, min(30, amount))

        chosen_titles = [t.strip().lower() for t in get_chosen_titles_of_christ() if t.strip()]
        filtered = {t: self.counts[t] for t in chosen_titles if t in self.counts}
        if not filtered:
            filtered = dict(sorted(self.counts.items(), key=lambda item: item[1], reverse=True)[:amount])
        else:
            filtered = dict(sorted(filtered.items(), key=lambda item: item[1], reverse=True)[:amount])

        if not filtered:
            self.output.value = "No data for pie chart."
            return

        self._chart_job_token += 1
        token = self._chart_job_token
        self.line_button.enabled = False
        self.pie_button.enabled = False
        self.output.value = "Rendering pie chart..."
        self.status_label.text = "Rendering chart..."
        filtered_copy = dict(filtered)
        threading.Thread(
            target=self._pie_chart_worker,
            args=(token, filtered_copy, amount),
            daemon=True,
        ).start()

    def _line_chart_worker(self, token: int, title: str, values: list[int]):
        try:
            chart_text = self._build_line_chart_text(title, values)
            image_path = self._build_line_chart_image(title, values)
            error = None
        except Exception as exc:
            chart_text = ""
            image_path = None
            error = str(exc)
        self.loop.call_soon_threadsafe(
            self._on_chart_ready,
            token,
            f"Line Chart: {title}",
            chart_text,
            image_path,
            error,
        )

    def _pie_chart_worker(self, token: int, filtered: dict[str, int], amount: int):
        try:
            chart_text = self._build_pie_chart_text(filtered, amount)
            image_path = self._build_pie_chart_image(filtered, amount)
            error = None
        except Exception as exc:
            chart_text = ""
            image_path = None
            error = str(exc)
        self.loop.call_soon_threadsafe(
            self._on_chart_ready,
            token,
            "Pie Chart",
            chart_text,
            image_path,
            error,
        )

    def _on_chart_ready(
        self,
        token: int,
        title: str,
        chart_text: str,
        image_path: str | None,
        error: str | None,
    ):
        if token != self._chart_job_token:
            return
        self.line_button.enabled = True
        self.pie_button.enabled = True
        self.status_label.text = "Ready."
        if error:
            self.output.value = f"Could not render chart:\n{error}"
            return
        self._render_chart(title, chart_text, image_path=image_path)

    def _render_chart(self, title: str, chart_text: str, image_path: str | None = None):
        try:
            self.chart_title_label.text = f"Chart: {title}"
            if image_path and os.path.exists(image_path):
                self._chart_image = toga.Image(image_path)
                self.chart_image_view.image = self._chart_image
            else:
                self.chart_image_view.image = None
            self.chart_output.value = chart_text
            if image_path:
                self.output.value = f"Rendered {title} image below."
            else:
                self.output.value = f"Rendered {title} details below (image unavailable)."
            self._restore_input_focus()
        except Exception as exc:
            self.output.value = f"Could not render chart:\n{exc}"

    def _build_line_chart_text(self, title: str, values: list[int]) -> str:
        max_val = max(values) if values else 1
        max_val = max(max_val, 1)
        lines = [f'Line Chart: "{title}"', ""]
        for name, val in zip(BOOK_NAMES, values):
            bar_len = max(1, int((val / max_val) * 30)) if val > 0 else 0
            bar = "#" * bar_len
            lines.append(f"{name:<18} | {bar:<30} {val}")
        return "\n".join(lines)

    def _build_pie_chart_text(self, chart_data: dict[str, int], amount: int) -> str:
        items = list(chart_data.items())
        total = sum(v for _, v in items) or 1
        lines = [f"Pie Chart ({amount} slices)", ""]
        for name, value in items:
            pct = (value / total) * 100.0
            lines.append(f"{name.title():<22} {value:>5} ({pct:>5.1f}%)")
        return "\n".join(lines)

    def _quickchart_png(self, chart_config: dict, filename: str) -> str | None:
        try:
            config_json = json.dumps(chart_config, separators=(",", ":"))
            query = urllib.parse.urlencode(
                {
                    "width": "900",
                    "height": "520",
                    "format": "png",
                    "backgroundColor": "white",
                    "c": config_json,
                }
            )
            url = f"https://quickchart.io/chart?{query}"
            out_path = os.path.join(tempfile.gettempdir(), filename)
            with urllib.request.urlopen(url, timeout=6) as response:
                data = response.read()
            with open(out_path, "wb") as fh:
                fh.write(data)
            return out_path
        except Exception:
            return None

    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))

    def _png_chunk(self, chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack("!I", len(data))
            + chunk_type
            + data
            + struct.pack("!I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    def _write_png_rgb(self, path: str, width: int, height: int, pixels: bytearray):
        raw = bytearray()
        stride = width * 3
        for y in range(height):
            raw.append(0)  # filter type
            start = y * stride
            raw.extend(pixels[start : start + stride])
        compressed = zlib.compress(bytes(raw), level=6)
        png = bytearray(b"\x89PNG\r\n\x1a\n")
        ihdr = struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)
        png.extend(self._png_chunk(b"IHDR", ihdr))
        png.extend(self._png_chunk(b"IDAT", compressed))
        png.extend(self._png_chunk(b"IEND", b""))
        with open(path, "wb") as fh:
            fh.write(png)

    def _local_pie_png(self, chart_data: dict[str, int]) -> str:
        width, height = 900, 520
        pixels = bytearray([255] * (width * height * 3))

        def set_px(x: int, y: int, rgb: tuple[int, int, int]):
            if 0 <= x < width and 0 <= y < height:
                i = (y * width + x) * 3
                pixels[i] = rgb[0]
                pixels[i + 1] = rgb[1]
                pixels[i + 2] = rgb[2]

        items = list(chart_data.items())
        total = sum(v for _, v in items) or 1
        colors = [self._hex_to_rgb(PIE_COLORS[i % len(PIE_COLORS)]) for i in range(len(items))]
        boundaries = []
        running = 0.0
        for _, value in items:
            running += (value / total) * 360.0
            boundaries.append(running)

        cx, cy, radius = 240, 260, 170
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy > radius * radius:
                    continue
                angle = (math.degrees(math.atan2(dy, dx)) + 450.0) % 360.0
                idx = 0
                while idx < len(boundaries) and angle > boundaries[idx]:
                    idx += 1
                idx = min(idx, len(colors) - 1)
                set_px(x, y, colors[idx])

        # simple legend blocks on right side
        lx, ly = 520, 70
        for i, color in enumerate(colors[:12]):
            y0 = ly + i * 28
            for y in range(y0, y0 + 18):
                for x in range(lx, lx + 18):
                    set_px(x, y, color)

        out_path = os.path.join(tempfile.gettempdir(), "bom_pie_chart_local.png")
        self._write_png_rgb(out_path, width, height, pixels)
        return out_path

    def _local_line_png(self, values: list[int]) -> str:
        width, height = 900, 520
        pixels = bytearray([255] * (width * height * 3))

        def set_px(x: int, y: int, rgb: tuple[int, int, int]):
            if 0 <= x < width and 0 <= y < height:
                i = (y * width + x) * 3
                pixels[i] = rgb[0]
                pixels[i + 1] = rgb[1]
                pixels[i + 2] = rgb[2]

        def line(x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]):
            dx = abs(x1 - x0)
            sx = 1 if x0 < x1 else -1
            dy = -abs(y1 - y0)
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                set_px(x0, y0, rgb)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sx
                if e2 <= dx:
                    err += dx
                    y0 += sy

        black = (50, 50, 50)
        blue = (11, 132, 243)
        left, right, top, bottom = 70, 40, 40, 90
        w = width - left - right
        h = height - top - bottom
        line(left, top, left, height - bottom, black)
        line(left, height - bottom, width - right, height - bottom, black)

        ymax = max(values) if values else 1
        ymax = max(ymax, 1)
        pts = []
        for i, v in enumerate(values):
            x = left + int(w * i / (len(values) - 1 if len(values) > 1 else 1))
            y = top + int(h * (1 - (v / ymax)))
            pts.append((x, y))
        for i in range(1, len(pts)):
            line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], blue)
        for x, y in pts:
            for oy in range(-2, 3):
                for ox in range(-2, 3):
                    set_px(x + ox, y + oy, blue)

        out_path = os.path.join(tempfile.gettempdir(), "bom_line_chart_local.png")
        self._write_png_rgb(out_path, width, height, pixels)
        return out_path

    def _build_pie_chart_image(self, chart_data: dict[str, int], amount: int) -> str | None:
        items = list(chart_data.items())
        labels = [name.title() for name, _ in items]
        values = [value for _, value in items]
        chart_config = {
            "type": "pie",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "data": values,
                        "backgroundColor": PIE_COLORS * ((len(values) // len(PIE_COLORS)) + 1),
                    }
                ],
            },
            "options": {
                "plugins": {"legend": {"position": "right"}},
                "title": {"display": True, "text": f"Pie Chart ({amount} slices)"},
            },
        }
        remote = self._quickchart_png(chart_config, "bom_pie_chart.png")
        if remote:
            return remote
        return self._local_pie_png(chart_data)

    def _build_line_chart_image(self, title: str, values: list[int]) -> str | None:
        chart_config = {
            "type": "line",
            "data": {
                "labels": BOOK_NAMES,
                "datasets": [
                    {
                        "label": title.title(),
                        "data": values,
                        "borderColor": "#0B84F3",
                        "backgroundColor": "#0B84F3",
                        "fill": False,
                        "pointRadius": 4,
                        "tension": 0.2,
                    }
                ],
            },
            "options": {
                "plugins": {"legend": {"display": False}},
                "title": {"display": True, "text": f'Line Chart: "{title}"'},
                "scales": {"y": {"beginAtZero": True}},
            },
        }
        remote = self._quickchart_png(chart_config, "bom_line_chart.png")
        if remote:
            return remote
        return self._local_line_png(values)


def main():
    return BookOfMormonMobileApp("Book of Mormon Mobile", "org.example.bookofmormonmobile")
