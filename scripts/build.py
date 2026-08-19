#!/usr/bin/env python3
"""
Build the public syllabus pages from the editable masters.

This runs automatically (see .github/workflows/build.yml) every time a file
under masters/ is pushed to the repository. For each masters/<slug>-master.html
it produces a clean, read-only <slug>.html at the repo root: the editing
control panel, scripts, and instructor-only placeholder notes are removed,
and a small "back to dashboard" link is added. It also refreshes the
"Last edit" date shown for that course on index.html.

You should not need to edit this file. If you add a third course, just add
masters/<new-slug>-master.html and add a matching data-course="<new-slug>"
span to index.html — this script picks up any *-master.html file it finds.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTERS_DIR = ROOT / "masters"
INDEX = ROOT / "index.html"

BACKNAV_CSS = """
  .backnav{
    max-width:var(--measure,8.5in);
    margin:0 auto;
    padding:14px 0 0;
    font-family:var(--font-body, 'Source Sans 3', sans-serif);
  }
  .backnav a{
    display:inline-flex;
    align-items:center;
    gap:6px;
    font-size:13px;
    font-weight:600;
    color:var(--primary,#1C3557);
    text-decoration:none;
    padding:6px 10px;
    border-radius:6px;
    transition:background .15s ease;
  }
  .backnav a:hover{background:var(--soft,#EFF3F8)}
  @media print{ .backnav{display:none} }
"""

BACKNAV_HTML = '<div class="backnav"><a href="index.html">&larr; All courses</a></div>\n'


def drop_element(html: str, opening_pattern: str, tag: str) -> str:
    """Remove an element and its contents, honouring nesting of the same tag."""
    m = re.search(opening_pattern, html)
    while m:
        start = m.start()
        i = m.end()
        depth = 1
        open_re = re.compile(r"<%s\b" % tag)
        close_re = re.compile(r"</%s>" % tag)
        while depth and i < len(html):
            no = open_re.search(html, i)
            nc = close_re.search(html, i)
            if not nc:
                break
            if no and no.start() < nc.start():
                depth += 1
                i = no.end()
            else:
                depth -= 1
                i = nc.end()
        html = html[:start] + html[i:]
        m = re.search(opening_pattern, html)
    return html


def clean_todo(html: str) -> str:
    """Drop bracketed instructor-only notes; unwrap real content that was
    typed into a placeholder so it renders as plain text."""
    out, i = [], 0
    for m in re.finditer(r'<span class="todo">(.*?)</span>', html, re.S):
        inner = m.group(1)
        out.append(html[i:m.start()])
        if not inner.lstrip().startswith("["):
            out.append(inner)
        i = m.end()
    out.append(html[i:])
    return "".join(out)


def clean_dd(m: re.Match) -> str:
    """Strip the red placeholder styling the browser leaves behind when text
    is typed directly over a template placeholder."""
    inner = m.group(1)
    inner = re.sub(r"</?font[^>]*>", "", inner)
    inner = re.sub(r'<span style="background-color:[^"]*">(.*?)</span>', r"\1", inner, flags=re.S)
    inner = re.sub(r"</?b>", "", inner)
    return "<dd>%s</dd>" % inner.strip()


def fix_day_row(m: re.Match) -> str:
    """Repair calendar rows that got tangled during manual editing — e.g. a
    description typed inside the date span, or a second class="day" span
    used for the description. Without this, such a row silently renders in
    the bold date style instead of as date + normal text."""
    row = m.group(0)

    m2 = re.match(r'<p><span class="day">([^<]*)<span[^>]*>(.*?)</span></span>(.*?)</p>', row, re.S)
    if m2:
        date = m2.group(1).replace("&nbsp;", " ").strip()
        rest = m2.group(2).strip()
        tail = re.sub(r"^<span[^>]*>|</span>$", "", m2.group(3).strip())
        body = (rest + " " + tail).strip()
        return '<p><span class="day">%s</span><span>%s</span></p>' % (date, body)

    m3 = re.match(r'<p><span class="day">([^<]*)</span><span class="day">(.*?)</span>(.*?)</p>', row, re.S)
    if m3:
        date = m3.group(1).replace("&nbsp;", " ").strip()
        rest = re.sub(r"<span[^>]*>|</span>", "", m3.group(2)).replace("&nbsp;", " ").strip()
        tail = re.sub(r"<span[^>]*>|</span>", "", m3.group(3)).strip()
        body = (rest + " " + tail).strip().rstrip("<br>")
        return '<p><span class="day">%s</span><span>%s</span></p>' % (date, body)

    return row


def strip_master(html: str) -> str:
    html = drop_element(html, r'<aside id="panel"', "aside")
    html = drop_element(html, r'<button id="panelToggle"', "button")
    html = drop_element(html, r'<div id="moveUI"', "div")
    html = drop_element(html, r'<div id="moveHint"', "div")
    for tag in ("span", "button", "div", "aside"):
        html = drop_element(html, r'<%s[^>]*class="[^"]*no-print[^"]*"' % tag, tag)
    html = drop_element(html, r"<script\b", "script")

    html = clean_todo(html)
    html = re.sub(r'\s*contenteditable="(true|false)"', "", html)
    html = html.replace('<body class="panel-open">', "<body>")
    html = re.sub(r"<dd>(.*?)</dd>", clean_dd, html, flags=re.S)
    html = re.sub(r'<p><span class="day">.*?</p>', fix_day_row, html, flags=re.S)
    html = re.sub(r'<span class="day">([^<]*?)(?:&nbsp;|\s)+</span>', r'<span class="day">\1</span>', html)
    html = re.sub(r"\n?<!-- =+ CONTROL PANEL =+ -->\n?", "\n", html)
    html = re.sub(r'<div id="moveUI".*?</body>', "</body>", html, flags=re.S)

    # drop the "EDITABLE MASTER —" prefix from the browser tab title
    html = re.sub(r"<title>EDITABLE MASTER\s*[—-]\s*(.*?)</title>", r"<title>\1</title>", html)

    # add the small link back to the dashboard
    html = html.replace("</style>", BACKNAV_CSS + "</style>", 1)
    html = re.sub(r"(<body[^>]*>)", r"\1\n" + BACKNAV_HTML, html, count=1)

    html = re.sub(r"[ \t]+\n", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html


def update_dashboard_date(slug: str, today_str: str) -> None:
    if not INDEX.exists():
        return
    text = INDEX.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<span class="dep-updated"[^>]*data-course="%s"[^>]*>\s*'
        r'<span class="term-label">Last edit</span>)([^<]*)' % re.escape(slug)
    )
    new_text, n = pattern.subn(lambda m: m.group(1) + today_str, text)
    if n:
        INDEX.write_text(new_text, encoding="utf-8")
        print(f"  dashboard: updated Last edit date for {slug}")
    else:
        print(f"  dashboard: no data-course=\"{slug}\" row found — skipped date update")


def main() -> None:
    if not MASTERS_DIR.exists():
        print("No masters/ folder found — nothing to build.")
        return

    masters = sorted(MASTERS_DIR.glob("*-master.html"))
    if not masters:
        print("No *-master.html files found in masters/ — nothing to build.")
        return

    today_str = datetime.now(timezone.utc).strftime("%b ") + str(
        int(datetime.now(timezone.utc).strftime("%d"))
    )

    for master_path in masters:
        slug = master_path.name[: -len("-master.html")]
        html = master_path.read_text(encoding="utf-8")
        clean = strip_master(html)
        out_path = ROOT / f"{slug}.html"
        out_path.write_text(clean, encoding="utf-8")
        print(f"built {out_path.name} from masters/{master_path.name}")
        update_dashboard_date(slug, today_str)


if __name__ == "__main__":
    main()
