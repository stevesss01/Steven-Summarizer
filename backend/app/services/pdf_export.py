"""Render an analysis report (markdown) as a formatted A4 PDF."""

from __future__ import annotations

import io
from datetime import date
from xml.sax.saxutils import escape

from markdown_it import MarkdownIt
from markdown_it.token import Token
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ACCENT = colors.HexColor("#1D4ED8")
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#6B7280")
RULE = colors.HexColor("#E5E7EB")
TABLE_HEADER_BG = colors.HexColor("#F3F4F6")

MARGIN = 20 * mm
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

STYLES = {
    "title": ParagraphStyle(
        "title", fontName=FONT_BOLD, fontSize=20, leading=25, textColor=TEXT, spaceAfter=4
    ),
    "h2": ParagraphStyle(
        "h2",
        fontName=FONT_BOLD,
        fontSize=11.5,
        leading=15,
        textColor=ACCENT,
        spaceBefore=12,
        spaceAfter=4,
    ),
    "h3": ParagraphStyle(
        "h3", fontName=FONT_BOLD, fontSize=10.5, leading=14, textColor=TEXT, spaceBefore=8
    ),
    "body": ParagraphStyle(
        "body",
        fontName=FONT,
        fontSize=10,
        leading=14.5,
        textColor=TEXT,
        alignment=TA_LEFT,
        spaceAfter=4,
    ),
    "cell": ParagraphStyle("cell", fontName=FONT, fontSize=9, leading=12, textColor=TEXT),
    "cell_head": ParagraphStyle(
        "cell_head", fontName=FONT_BOLD, fontSize=9, leading=12, textColor=TEXT
    ),
    "meta": ParagraphStyle("meta", fontName=FONT, fontSize=9, leading=12, textColor=MUTED),
}

_md = MarkdownIt("commonmark", {"html": False}).enable("table")


_SUBSTITUTES = str.maketrans(
    {"≤": "<=", "≥": ">=", "→": "->", "←": "<-", "≈": "~", "✓": "", "✔": "", "×": "x"}
)


def _plain(text: str) -> str:
    """Replace characters the built-in PDF fonts cannot draw."""
    text = text.translate(_SUBSTITUTES)
    return text.encode("cp1252", errors="replace").decode("cp1252")


def _safe(text: str) -> str:
    """Escape text for ReportLab paragraph markup."""
    return _plain(escape(text))


def _inline(token: Token | None) -> str:
    """Convert an inline token's children to ReportLab paragraph markup."""
    if token is None or not token.children:
        return _safe(token.content) if token else ""

    out: list[str] = []
    for child in token.children:
        kind = child.type
        if kind == "text":
            out.append(_safe(child.content))
        elif kind == "code_inline":
            out.append(f'<font face="Courier">{_safe(child.content)}</font>')
        elif kind == "strong_open":
            out.append("<b>")
        elif kind == "strong_close":
            out.append("</b>")
        elif kind == "em_open":
            out.append("<i>")
        elif kind == "em_close":
            out.append("</i>")
        elif kind == "link_open":
            href = _safe(str(child.attrs.get("href", "")))
            out.append(f'<link href="{href}" color="#1D4ED8">')
        elif kind == "link_close":
            out.append("</link>")
        elif kind in ("softbreak", "hardbreak"):
            out.append("<br/>")
    return "".join(out)


class _Builder:
    def __init__(self, tokens: list[Token], width: float) -> None:
        self.tokens = tokens
        self.width = width
        self.i = 0

    def build(self) -> list:
        flow: list = []
        while self.i < len(self.tokens):
            flow.extend(self._block())
        return flow

    def _next_inline(self) -> Token | None:
        # The inline token follows its *_open token.
        token = self.tokens[self.i + 1] if self.i + 1 < len(self.tokens) else None
        return token if token is not None and token.type == "inline" else None

    def _skip_to(self, close_type: str) -> None:
        depth = 0
        open_type = close_type.replace("_close", "_open")
        while self.i < len(self.tokens):
            t = self.tokens[self.i].type
            if t == open_type:
                depth += 1
            elif t == close_type:
                depth -= 1
                if depth == 0:
                    self.i += 1
                    return
            self.i += 1

    def _block(self) -> list:
        token = self.tokens[self.i]
        kind = token.type

        if kind == "heading_open":
            text = _inline(self._next_inline())
            self.i += 3
            if token.tag == "h1":
                return [Paragraph(text, STYLES["title"])]
            if token.tag == "h2":
                return [
                    Paragraph(text.upper(), STYLES["h2"]),
                    HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4),
                ]
            return [Paragraph(text, STYLES["h3"])]

        if kind == "paragraph_open":
            text = _inline(self._next_inline())
            self.i += 3
            return [Paragraph(text, STYLES["body"])]

        if kind in ("bullet_list_open", "ordered_list_open"):
            return [self._list(kind)]

        if kind == "table_open":
            return [self._table()]

        if kind == "hr":
            self.i += 1
            return [
                HRFlowable(width="100%", thickness=0.6, color=RULE, spaceBefore=6, spaceAfter=6)
            ]

        if kind in ("fence", "code_block"):
            self.i += 1
            text = _safe(token.content).replace("\n", "<br/>")
            return [Paragraph(f'<font face="Courier">{text}</font>', STYLES["body"])]

        self.i += 1
        return []

    def _list(self, kind: str) -> ListFlowable:
        ordered = kind == "ordered_list_open"
        close_type = kind.replace("_open", "_close")
        start = int(self.tokens[self.i].attrs.get("start", 1) or 1) if ordered else 1
        self.i += 1

        items: list[ListItem] = []
        while self.i < len(self.tokens) and self.tokens[self.i].type != close_type:
            if self.tokens[self.i].type == "list_item_open":
                self.i += 1
                content: list = []
                while self.tokens[self.i].type != "list_item_close":
                    content.extend(self._block())
                self.i += 1
                items.append(ListItem(content or [Spacer(1, 0)], leftIndent=16, bulletColor=ACCENT))
            else:
                self.i += 1
        self.i += 1

        options = (
            {"bulletType": "1", "start": start, "bulletFormat": "%s."}
            if ordered
            else {
                "bulletType": "bullet",
                "start": "\u2022",
            }
        )
        return ListFlowable(
            items,
            bulletFontName=FONT_BOLD if ordered else FONT,
            bulletFontSize=9.5,
            bulletColor=ACCENT,
            leftIndent=16,
            spaceAfter=4,
            **options,
        )

    def _table(self) -> Table:
        rows: list[list[Paragraph]] = []
        row: list[Paragraph] = []
        in_head = False
        while self.tokens[self.i].type != "table_close":
            t = self.tokens[self.i]
            if t.type == "thead_open":
                in_head = True
            elif t.type == "thead_close":
                in_head = False
            elif t.type == "tr_open":
                row = []
            elif t.type == "tr_close":
                rows.append(row)
            elif t.type in ("th_open", "td_open"):
                style = STYLES["cell_head"] if in_head or t.type == "th_open" else STYLES["cell"]
                row.append(Paragraph(_inline(self._next_inline()), style))
            self.i += 1
        self.i += 1

        cols = max((len(r) for r in rows), default=1)
        rows = [r + [Paragraph("", STYLES["cell"])] * (cols - len(r)) for r in rows]
        # Size columns by their longest text, within sensible bounds.
        weights = [
            min(max(max(len(r[c].getPlainText()) for r in rows), 6), 60) for c in range(cols)
        ]
        total = sum(weights)
        widths = [self.width * w / total for w in weights]
        table = Table(rows, colWidths=widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
                    ("GRID", (0, 0), (-1, -1), 0.5, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table


def _canvas_factory(header: str, footer: str):
    class NumberedCanvas(canvas.Canvas):
        """Two-pass canvas so every page can show "Page x of y"."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pages: list[dict] = []

        def showPage(self):  # noqa: N802 (ReportLab API)
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                self._decorate(total)
                super().showPage()
            super().save()

        def _decorate(self, total: int) -> None:
            width, height = A4
            self.setFont(FONT, 8)
            self.setFillColor(MUTED)
            self.drawString(MARGIN, height - 12 * mm, header)
            self.drawRightString(
                width - MARGIN, height - 12 * mm, date.today().strftime("%d %b %Y")
            )
            self.setStrokeColor(RULE)
            self.setLineWidth(0.5)
            self.line(MARGIN, height - 14 * mm, width - MARGIN, height - 14 * mm)
            self.drawString(MARGIN, 10 * mm, footer)
            self.drawRightString(width - MARGIN, 10 * mm, f"Page {self._pageNumber} of {total}")

    return NumberedCanvas


def render_report_pdf(markdown: str, *, title: str, source_name: str | None = None) -> bytes:
    """Return PDF bytes for a markdown report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + 4 * mm,
        bottomMargin=MARGIN,
        title=title,
        author="Steven-Summarizer",
    )

    story: list = []
    if source_name:
        story.append(Paragraph(f"Source: {_safe(source_name)}", STYLES["meta"]))
        story.append(Spacer(1, 6))

    tokens = _md.parse(markdown)
    flow = _Builder(tokens, doc.width).build()
    # Keep each section heading with its first block.
    grouped: list = []
    i = 0
    while i < len(flow):
        if isinstance(flow[i], Paragraph) and flow[i].style.name == "h2" and i + 2 < len(flow):
            grouped.append(KeepTogether(flow[i : i + 3]))
            i += 3
        else:
            grouped.append(flow[i])
            i += 1
    story.extend(grouped)

    header = _plain(f"Steven-Summarizer  |  {title}")
    footer = "Generated by Steven-Summarizer. AI output: verify important details."
    doc.build(story, canvasmaker=_canvas_factory(header, footer))
    return buffer.getvalue()
