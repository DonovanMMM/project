"""
Mobile entry point (BeeWare/Toga) for the Book of Mormon app.

This module reuses existing logic from list_parser.py and leaves my_gui.py unchanged.
"""

from __future__ import annotations

import html
import math
import threading
import traceback

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
                style=Pack(height=220, margin_top=10),
            )
            self.chart_title_label = toga.Label("Chart: none", style=Pack(margin_top=10, margin_bottom=6))
            self.chart_webview = toga.WebView(style=Pack(height=340, flex=1))

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
                    self.chart_webview,
                ],
                style=Pack(direction=COLUMN, margin=10, flex=1),
            )

            self.main_window = toga.MainWindow(title=self.formal_name)
            self.main_window.content = main_box
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

    def _set_chart_content(self, webview: toga.WebView, html_doc: str):
        # Try multiple base URLs for Android WebView compatibility.
        for base_url in ("https://example.invalid/", "about:blank", ""):
            try:
                webview.set_content(base_url, html_doc)
                return
            except TypeError:
                continue
            except Exception:
                continue
        raise RuntimeError("Could not render chart content in WebView")

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

        html_doc = self._build_line_chart_html(title, values)
        self._render_chart_inline(f"Line Chart: {title}", html_doc)

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

        html_doc = self._build_pie_chart_html(filtered, amount)
        self._render_chart_inline("Pie Chart", html_doc)

    def _render_chart_inline(self, title: str, html_doc: str):
        try:
            self.chart_title_label.text = f"Chart: {title}"
            self._set_chart_content(self.chart_webview, html_doc)
            self.output.value = f"Rendered {title} below."
            self._restore_input_focus()
        except Exception as exc:
            self.output.value = f"Could not render chart:\n{exc}"

    def _build_line_chart_html(self, title: str, values: list[int]) -> str:
        width = 1000
        height = 560
        left = 80
        right = 40
        top = 50
        bottom = 120
        plot_w = width - left - right
        plot_h = height - top - bottom
        ymax = max(values) if values else 1
        ymax = max(ymax, 1)

        points = []
        labels = []
        for i, val in enumerate(values):
            x = left + (plot_w * i / (len(values) - 1 if len(values) > 1 else 1))
            y = top + plot_h * (1 - (val / ymax))
            points.append((x, y, val))
            labels.append((x, BOOK_NAMES[i]))

        polyline = " ".join(f"{x:.2f},{y:.2f}" for x, y, _ in points)
        circles = "\n".join(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#0B84F3" />'
            f'<text x="{x:.2f}" y="{y-10:.2f}" font-size="12" text-anchor="middle">{val}</text>'
            for x, y, val in points
        )
        xlabels = "\n".join(
            f'<text x="{x:.2f}" y="{height-70}" font-size="12" text-anchor="end" transform="rotate(-35 {x:.2f},{height-70})">{html.escape(name)}</text>'
            for x, name in labels
        )

        return f"""<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Line Chart</title>
</head>
<body style="font-family: Arial; margin: 0; padding: 12px; background: #ffffff;">
<h3 style="margin:0 0 8px 0;">Line Chart: {html.escape(title)}</h3>
<svg viewBox="0 0 {width} {height}" width="100%" height="auto">
  <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333" stroke-width="2" />
  <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333" stroke-width="2" />
  <polyline fill="none" stroke="#0B84F3" stroke-width="3" points="{polyline}" />
  {circles}
  {xlabels}
</svg>
</body></html>"""

    def _build_pie_chart_html(self, chart_data: dict[str, int], amount: int) -> str:
        items = list(chart_data.items())
        total = sum(v for _, v in items) or 1
        cx = 260
        cy = 260
        radius = 180
        current_angle = -90.0
        slices = []
        legend = []
        for idx, (name, value) in enumerate(items):
            frac = value / total
            sweep = 360.0 * frac
            start = math.radians(current_angle)
            end = math.radians(current_angle + sweep)
            x1 = cx + radius * math.cos(start)
            y1 = cy + radius * math.sin(start)
            x2 = cx + radius * math.cos(end)
            y2 = cy + radius * math.sin(end)
            large_arc = 1 if sweep > 180 else 0
            color = PIE_COLORS[idx % len(PIE_COLORS)]
            path = (
                f"M {cx},{cy} L {x1:.2f},{y1:.2f} "
                f"A {radius},{radius} 0 {large_arc},1 {x2:.2f},{y2:.2f} Z"
            )
            slices.append(f'<path d="{path}" fill="{color}" stroke="#fff" stroke-width="1"/>')
            pct = round((value / total) * 100, 1)
            legend.append(
                f'<div style="margin-bottom:6px;"><span style="display:inline-block;width:12px;height:12px;background:{color};margin-right:6px;"></span>'
                f'{html.escape(name.title())}: {value} ({pct}%)</div>'
            )
            current_angle += sweep
        legend_html = "\n".join(legend)
        slices_svg = "\n".join(slices)

        return f"""<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pie Chart</title>
</head>
<body style="font-family: Arial; margin: 0; padding: 12px; background: #ffffff;">
<h3 style="margin:0 0 8px 0;">Pie Chart ({amount} slices)</h3>
<div style="display:block;">
  <svg viewBox="0 0 520 520" width="100%" height="auto" style="max-width:520px;">
    {slices_svg}
  </svg>
  <div style="font-size:14px; line-height:1.25; margin-top:10px;">
    {legend_html}
  </div>
</div>
</body></html>"""


def main():
    return BookOfMormonMobileApp("Book of Mormon Mobile", "org.example.bookofmormonmobile")
