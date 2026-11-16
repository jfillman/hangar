#!/usr/bin/env python3
"""Spec Sheet: build a navigable, Hangar-styled spec page from one structured Markdown file.

    python3 build_spec.py <spec.md> <out.html>

Source format (see SPEC-FORMAT.md beside this file):
  - YAML-like front matter between --- lines: title, program, board (Strip Board URL), source (original doc URL), updated.
  - Text before the first `## ` is the lead.
  - `## Heading` starts a section. `{#slug}` at the end of a heading pins its anchor.
  - `### ID · Title` (ID like R-1, G-ARGO-10, A-9) inside a section is a work package. The line right under it may be
    `<!-- pkg status=done wave=W1 strip=W-8 depends=R-1,R-2 -->`. Any other `###` is a plain sub-heading.
  - Everything else is CommonMark with tables.
Needs: markdown-it-py (`markdown_it`).
"""
import html, json, re, sys
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")
RESERVED = {"settings", "sidebar", "customize", "upgrade", "downloads"}
PKG_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[a-z]?\d*)\s*(?:·|:|—|-)\s*(.+)$")
META_RE = re.compile(r"^<!--\s*pkg\s+(.*?)\s*-->\s*$")
STATUS = {  # status word -> (label, tone)
    "done": ("Done", "good"), "live": ("Live", "good"), "built": ("Built", "good"), "verified": ("Verified", "good"),
    "in-progress": ("In progress", "sky"), "review": ("In review", "sky"), "draft": ("Draft", "sky"),
    "proposal": ("Proposal", ""), "not-started": ("Not started", ""), "later": ("Later", ""),
    "unverified": ("Unverified", "amber"), "blocked": ("Blocked", "bad"), "owner": ("Owner step", "amber"),
    "dropped": ("Dropped", ""), "superseded": ("Superseded", ""),
}


def slugify(text, used):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    s = s[:60].strip("-")
    if s in RESERVED or s.startswith("comment-"):
        s = "s-" + s
    base, n = s, 2
    while s in used:
        s = f"{base}-{n}"; n += 1
    used.add(s)
    return s


def parse(text):
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1); meta[k.strip()] = v.strip()
            body = text[end + 5:]
    lines = body.splitlines()
    lead, sections, cur, sub, in_code = [], [], None, None, False
    used = set()
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith("## "):
            title = line[3:].strip()
            m = re.search(r"\s*\{#([a-z0-9-]+)\}\s*$", title)
            sid = None
            if m:
                sid, title = m.group(1), title[:m.start()].strip()
                used.add(sid)
            cur = {"title": title, "id": sid or slugify(title, used), "intro": [], "subs": []}
            sections.append(cur); sub = None
            continue
        if not in_code and line.startswith("### ") and cur is not None:
            title = line[4:].strip()
            plain = re.sub(r"[`*_]", "", title)
            m = PKG_RE.match(plain)
            sub = {"title": title, "lines": [], "pkg": None}
            if m:
                pid = m.group(1)
                sub["pkg"] = {"id": pid, "name": re.sub(r"^\S+\s*(?:·|:|—|-)\s*", "", title, count=1), "status": "", "wave": "", "strip": "", "depends": ""}
                sub["id"] = slugify(pid, used)
            else:
                sub["id"] = slugify(plain, used)
            cur["subs"].append(sub)
            continue
        if cur is None:
            lead.append(line)
        elif sub is None:
            cur["intro"].append(line)
        else:
            mm = META_RE.match(line.strip())
            if mm and sub["pkg"] is not None and not any(l.strip() for l in sub["lines"]):
                for kv in mm.group(1).split():
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        if k in sub["pkg"]:
                            sub["pkg"][k] = v
                continue
            sub["lines"].append(line)
    return meta, "\n".join(lead), sections


def render_md(text):
    out = md.render(text)
    out = out.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    return out


def inline(text):
    return md.renderInline(text)


def chip(status):
    if not status:
        return ""
    label, tone = STATUS.get(status, (status.replace("-", " ").capitalize(), ""))
    return f'<span class="chip {tone}" data-status="{html.escape(status)}">{html.escape(label)}</span>'


def build(src, template):
    meta, lead, sections = parse(src)
    pkgs, nav, main = [], [], []
    for s in sections:
        items = []
        body = [f'<section id="{s["id"]}" class="sec"><h2><a class="anchor" href="#{s["id"]}" aria-label="Link to this section">#</a>{inline(s["title"])}</h2>']
        if "\n".join(s["intro"]).strip():
            body.append(f'<div class="prose">{render_md(chr(10).join(s["intro"]))}</div>')
        for sub in s["subs"]:
            content = render_md("\n".join(sub["lines"]))
            if sub["pkg"]:
                p = sub["pkg"]; p["anchor"] = sub["id"]; p["section"] = s["title"]; pkgs.append(p)
                metas = []
                if p["wave"]: metas.append(f'<span class="tagm">wave {html.escape(p["wave"])}</span>')
                if p["strip"]: metas.append(f'<span class="tagm">board {html.escape(p["strip"])}</span>')
                if p["depends"]: metas.append(f'<span class="tagm">needs {html.escape(p["depends"].replace(",", ", "))}</span>')
                body.append(
                    f'<details class="pkg" id="{sub["id"]}" data-status="{html.escape(p["status"])}" data-text="{html.escape((p["id"] + " " + p["name"]).lower())}">'
                    f'<summary><span class="pid">{html.escape(p["id"])}</span><span class="pname">{inline(p["name"])}</span>'
                    f'<span class="pmeta">{"".join(metas)}{chip(p["status"])}</span></summary>'
                    f'<div class="prose">{content}</div>'
                    f'<p class="plink"><a href="#{sub["id"]}">Link to {html.escape(p["id"])}</a></p></details>')
                items.append((sub["id"], p["id"], p["status"], True))
            else:
                body.append(f'<h3 id="{sub["id"]}"><a class="anchor" href="#{sub["id"]}" aria-label="Link to this heading">#</a>{inline(sub["title"])}</h3><div class="prose">{content}</div>')
                items.append((sub["id"], re.sub(r"[`*_]", "", sub["title"]), "", False))
        body.append("</section>")
        main.append("".join(body))
        li = "".join(
            f'<li class="{"np" if is_pkg else "ns"}" data-status="{html.escape(st)}"><a href="#{i}">{html.escape(t)}</a></li>'
            for i, t, st, is_pkg in items)
        nav.append(f'<li><a class="nsec" href="#{s["id"]}">{html.escape(re.sub(r"[`*_]", "", s["title"]))}</a>{("<ul>" + li + "</ul>") if li else ""}</li>')

    counts = {}
    for p in pkgs:
        counts[p["status"] or "unset"] = counts.get(p["status"] or "unset", 0) + 1
    order = [k for k in STATUS if k in counts] + [k for k in counts if k not in STATUS]
    filt = "".join(f'<button type="button" class="filt" data-f="{html.escape(k)}">{html.escape(STATUS.get(k, (k.capitalize(), ""))[0])} <b>{counts[k]}</b></button>' for k in order)
    rows = "".join(
        f'<tr data-status="{html.escape(p["status"])}" data-text="{html.escape((p["id"] + " " + re.sub(r"[`*_]", "", p["name"])).lower())}">'
        f'<td class="mono"><a href="#{p["anchor"]}">{html.escape(p["id"])}</a></td><td>{inline(p["name"])}</td>'
        f'<td>{chip(p["status"])}</td><td class="mono">{html.escape(p["wave"])}</td><td class="mono">{html.escape(p["strip"])}</td></tr>'
        for p in pkgs)
    index = (f'<section id="package-index" class="sec"><h2><a class="anchor" href="#package-index" aria-label="Link to this section">#</a>Work packages</h2>'
             f'<div class="filters" role="group" aria-label="Filter packages by status">{filt}'
             f'<input id="pkgq" class="search" type="text" placeholder="Filter by id or word" aria-label="Filter packages"></div>'
             f'<div class="tbl"><table id="pkgtable"><thead><tr><th>Id</th><th>Package</th><th>Status</th><th>Wave</th><th>Board</th></tr></thead><tbody>{rows}</tbody></table></div>'
             f'<p class="note" id="pkgnone" hidden>No package matches that filter.</p></section>') if pkgs else ""
    links = []
    if meta.get("board"): links.append(f'<a href="{html.escape(meta["board"])}" target="_blank" rel="noopener">Strip Board</a>')
    if meta.get("source"): links.append(f'<a href="{html.escape(meta["source"])}" target="_blank" rel="noopener">Original document</a>')
    done = sum(counts.get(k, 0) for k in ("done", "live", "built", "verified"))
    summary = f'{len(pkgs)} work packages · {done} done or live' if pkgs else ""
    page = (template
            .replace("{{TITLE}}", html.escape(meta.get("title", "Spec")))
            .replace("{{PROGRAM}}", html.escape(meta.get("program", "")))
            .replace("{{UPDATED}}", html.escape(meta.get("updated", "")))
            .replace("{{SUMMARY}}", html.escape(summary))
            .replace("{{LINKS}}", " · ".join(links))
            .replace("{{LEAD}}", render_md(lead) if lead.strip() else "")
            .replace("{{NAV}}", ('<li><a class="nsec" href="#package-index">Work packages</a></li>' if pkgs else "") + "".join(nav))
            .replace("{{INDEX}}", index)
            .replace("{{MAIN}}", "".join(main)))
    return page, {"sections": len(sections), "packages": len(pkgs), "counts": counts}


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    src = open(sys.argv[1], encoding="utf-8").read()
    template = open(os.path.join(here, "spec-template.html"), encoding="utf-8").read()
    page, stats = build(src, template)
    open(sys.argv[2], "w", encoding="utf-8").write(page)
    print(json.dumps(stats))
