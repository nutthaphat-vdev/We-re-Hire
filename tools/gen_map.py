#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_map.py — สร้าง INDEX_MAP.md จาก index.html

ใช้ทำอะไร:
    index.html เป็นไฟล์เดียว 6000+ บรรทัด · script ก้อนเดียว 4000 บรรทัด
    ทุกครั้งที่จะแก้อะไร ต้อง grep เดา keyword ก่อน — เสียเวลาและพลาดได้
    ไฟล์นี้สแกนโครงสร้างทั้งไฟล์ออกมาเป็นแผนที่ + เลขบรรทัด อ่านครั้งเดียวรู้หมด

วิธีใช้:
    python tools/gen_map.py                 # เขียนทับ INDEX_MAP.md
    python tools/gen_map.py --check         # เช็คว่า map ตรงกับโค้ดไหม (exit 1 ถ้าไม่ตรง)
    python tools/gen_map.py --src other.html --out OTHER_MAP.md

สำคัญ:
    - ไฟล์นี้ READ-ONLY ต่อ index.html · ไม่มี write path ไปแตะ source เลย
    - INDEX_MAP.md เป็นไฟล์ throwaway — ลบทิ้ง regenerate ใหม่ได้เสมอ
    - COUPLING_MAP.md เป็นคนละไฟล์ เขียนด้วยมือ · สคริปต์นี้ไม่แตะ
"""

import re
import sys
import argparse
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BKK = timezone(timedelta(hours=7))


# ── helpers ────────────────────────────────────────────────────────────

def line_of(src: str, idx: int) -> int:
    """แปลง char index -> เลขบรรทัด (1-based)"""
    return src.count('\n', 0, idx) + 1


def scan_blocks(src: str):
    """หา <style> / <script> block พร้อมช่วงบรรทัด

    หมายเหตุ: ใช้ non-greedy regex · <style> ที่อยู่ใน template literal ของ JS
    จะถูกนับด้วย — เป็นเรื่องปกติของไฟล์นี้ (modal บาง modal ฝัง CSS ไว้ใน string)
    เลยแยก flag `in_js` ไว้ให้เห็นว่าก้อนไหนอยู่ใน script
    """
    blocks = []
    for m in re.finditer(r'<(style|script)\b([^>]*)>(.*?)</\1>', src, re.S):
        tag = m.group(1)
        attrs = (m.group(2) or '').strip()
        body = m.group(3)
        blocks.append({
            'tag': tag,
            'attrs': attrs,
            'start': line_of(src, m.start()),
            'end': line_of(src, m.end()),
            'lines': body.count('\n'),
            'chars': len(body),
        })
    # ทำเครื่องหมายก้อนที่ซ้อนอยู่ในก้อน script อื่น
    scripts = [b for b in blocks if b['tag'] == 'script']
    for b in blocks:
        b['in_js'] = any(
            s is not b and s['start'] < b['start'] and b['end'] < s['end']
            for s in scripts
        )
    return blocks


def scan_sections(src: str):
    """หา section comment แบบ  // ─── NAME ─────"""
    out = []
    for m in re.finditer(r'^[ \t]*//[ \t]*[─-]{3,}[ \t]*(.+?)[ \t]*[─-]{3,}[ \t]*$',
                         src, re.M):
        out.append({'line': line_of(src, m.start()), 'name': m.group(1).strip()})
    return out


def scan_functions(src: str):
    """หา function declaration ระดับบนสุด (ไม่รวม arrow fn / method)"""
    fns = []
    pat = re.compile(r'^[ \t]{0,4}(async[ \t]+)?function[ \t]+(\w+)[ \t]*\(([^)]*)\)', re.M)
    for m in pat.finditer(src):
        fns.append({
            'line': line_of(src, m.start()),
            'name': m.group(2),
            'args': re.sub(r'\s+', ' ', m.group(3)).strip(),
            'is_async': bool(m.group(1)),
        })
    # ช่วงบรรทัดโดยประมาณ = ถึงบรรทัดก่อน function ถัดไป
    for i, f in enumerate(fns):
        f['end'] = (fns[i + 1]['line'] - 1) if i + 1 < len(fns) else None
    return fns


def scan_pages(src: str):
    """หา <div class="page" id="page-*"> + mount point ข้างใน"""
    pages = []
    for m in re.finditer(r'<div[^>]*\bid="(page-[\w-]+)"[^>]*>', src):
        pid = m.group(1)
        start = line_of(src, m.start())
        pages.append({'id': pid, 'line': start, 'key': pid[len('page-'):]})

    # หา container ที่ JS ใช้ innerHTML ลงไป (mount point) ในช่วงของแต่ละหน้า
    lines = src.split('\n')
    # หน้าสุดท้ายต้องไม่กินไปถึง EOF — ตัดที่ <script> ก้อนแรกที่อยู่หลัง page แรก
    tail = len(lines)
    if pages:
        m = re.search(r'<script\b(?![^>]*\bsrc=)', src[
            src.find(f'id="{pages[0]["id"]}"'):])
        if m:
            tail = line_of(src, src.find(f'id="{pages[0]["id"]}"') + m.start()) - 1
    for i, p in enumerate(pages):
        end = pages[i + 1]['line'] - 1 if i + 1 < len(pages) else tail
        chunk = '\n'.join(lines[p['line'] - 1:end])
        ids = re.findall(r'<div[^>]*\bid="(\w+)"[^>]*>\s*</div>', chunk)
        ids += re.findall(r'<div[^>]*\bid="(\w+Content)"', chunk)
        p['mounts'] = sorted(set(i for i in ids if not i.startswith('page-')))
        p['end'] = end
    return pages


def scan_showpage_routes(src: str, fns):
    """อ่านตัว showPage() ว่าหน้าไหน trigger loader ตัวไหน — นี่คือ router จริงของแอป"""
    sp = next((f for f in fns if f['name'] == 'showPage'), None)
    if not sp:
        return {}
    lines = src.split('\n')
    body = '\n'.join(lines[sp['line'] - 1: (sp['end'] or len(lines))])
    routes = {}
    known = {f['name'] for f in fns}
    for bl in body.split('\n'):
        m = re.search(r"name\s*===\s*'([\w-]+)'", bl)
        if not m:
            continue
        key = m.group(1)
        rest = bl[m.end():]
        for c in re.finditer(r'\b(\w+)\s*\(', rest):
            if c.group(1) in known:
                routes.setdefault(key, []).append(c.group(1))
    return routes


def scan_endpoints(src: str):
    """หา API call — api('METHOD', path) และ fetch(API + ...)"""
    eps = {}
    for m in re.finditer(r"""api\(\s*['"](\w+)['"]\s*,\s*[`'"]([^`'"]+)""", src):
        key = (m.group(1).upper(), re.sub(r'\$\{[^}]+\}', ':x', m.group(2)))
        eps.setdefault(key, []).append(line_of(src, m.start()))
    for m in re.finditer(r"fetch\(\s*API\s*\+\s*[`'\"]([^`'\"]+)", src):
        key = ('FETCH', re.sub(r'\$\{[^}]+\}', ':x', m.group(1)))
        eps.setdefault(key, []).append(line_of(src, m.start()))
    return eps


def scan_state(src: str, blocks):
    """หา global mutable state + timer handle (ตัวที่ทำให้เกิด coupling ข้ามหน้า)"""
    script_ranges = [(b['start'], b['end']) for b in blocks
                     if b['tag'] == 'script' and not b['in_js']]

    def in_script(l):
        return any(a < l < b for a, b in script_ranges)

    state = []
    for m in re.finditer(r'^[ \t]{0,2}(let|var)[ \t]+([\w$]+)[ \t]*(=[^;\n]{0,70})?', src, re.M):
        l = line_of(src, m.start())
        if in_script(l):
            state.append({'line': l, 'kind': m.group(1), 'name': m.group(2),
                          'init': (m.group(3) or '').strip().lstrip('=').strip()})

    timers = []
    for m in re.finditer(r'([\w$.]+)\s*=\s*set(Interval|Timeout)\(\s*([\w$]+)?', src):
        timers.append({'line': line_of(src, m.start()), 'handle': m.group(1),
                       'kind': m.group(2), 'fn': m.group(3) or '(inline)'})
    clears = []
    for m in re.finditer(r'clear(?:Interval|Timeout)\(\s*([\w$.]+)\s*\)', src):
        clears.append({'line': line_of(src, m.start()), 'handle': m.group(1)})
    return state, timers, clears


def scan_reassigned_fns(src: str, fns):
    """หา function ที่ถูก monkey-patch ทับภายหลัง (`name = function`)
    อันตรายมาก: แก้ที่ตัวประกาศเดิมแล้วพฤติกรรมจริงไม่เปลี่ยน"""
    names = {f['name'] for f in fns}
    out = []
    for m in re.finditer(r'^[ \t]{0,4}([\w$]+)\s*=\s*(async\s+)?function\b', src, re.M):
        if m.group(1) in names:
            out.append({'line': line_of(src, m.start()), 'name': m.group(1)})
    return out


def call_sites(src: str, name: str):
    return [line_of(src, m.start()) for m in re.finditer(r'\b' + re.escape(name) + r'\s*\(', src)]


# ── render ─────────────────────────────────────────────────────────────

def build(src_path: Path) -> str:
    src = src_path.read_text(encoding='utf-8')
    total = src.count('\n') + 1
    digest = hashlib.sha256(src.encode('utf-8')).hexdigest()[:12]

    blocks = scan_blocks(src)
    sections = scan_sections(src)
    fns = scan_functions(src)
    pages = scan_pages(src)
    routes = scan_showpage_routes(src, fns)
    eps = scan_endpoints(src)
    state, timers, clears = scan_state(src, blocks)
    patched = scan_reassigned_fns(src, fns)

    fn_by_name = {f['name']: f for f in fns}
    o = []
    w = o.append

    w(f"# INDEX_MAP — แผนที่ `{src_path.name}`")
    w("")
    w("> 🤖 **ไฟล์นี้ generate อัตโนมัติ — ห้ามแก้ด้วยมือ**  ")
    w("> regenerate: `python tools/gen_map.py` · เช็คว่าเก่ายัง: `python tools/gen_map.py --check`  ")
    w("> ส่วนที่เขียนด้วยมือ (coupling / กับดัก) อยู่ที่ **`COUPLING_MAP.md`** — สคริปต์ไม่แตะไฟล์นั้น")
    w("")
    w(f"- generated: `{datetime.now(BKK).strftime('%Y-%m-%d %H:%M')}` (BKK)")
    w(f"- source: `{src_path.name}` · **{total:,} บรรทัด** · sha256 `{digest}`")
    w(f"- {len(fns)} functions · {len(pages)} pages · {len(eps)} endpoints")
    w("")
    w("---")
    w("")

    # ── layout
    w("## 🗺️ Layout ของไฟล์")
    w("")
    w("| ช่วงบรรทัด | คืออะไร |")
    w("|---|---|")
    html_start = 1
    for b in sorted(blocks, key=lambda x: x['start']):
        if b['in_js']:
            continue
        if b['start'] > html_start:
            w(f"| {html_start}–{b['start']-1} | HTML markup |")
        label = '**JS (ก้อนหลัก)**' if b['tag'] == 'script' and b['lines'] > 500 else \
                ('JS' if b['tag'] == 'script' else 'CSS')
        attrs = f" `{b['attrs'][:60]}`" if b['attrs'] else ''
        w(f"| {b['start']}–{b['end']} | {label}{attrs} · {b['lines']:,} บรรทัด |")
        html_start = b['end'] + 1
    if html_start <= total:
        w(f"| {html_start}–{total} | HTML markup |")
    w("")

    nested = [b for b in blocks if b['in_js']]
    if nested:
        w(f"> ⚠️ มี `<style>` **{len(nested)} ก้อน** ฝังอยู่ใน template literal ของ JS "
          f"(บรรทัด {', '.join(str(b['start']) for b in nested)}) — "
          "แก้ CSS ของ modal พวกนี้ต้องแก้ในสตริง ไม่ใช่ใน `<style>` ด้านบน")
        w("")

    # ── sections
    w("## 📑 Section ใน JS")
    w("")
    w("| บรรทัด | Section |")
    w("|---|---|")
    for s in sections:
        w(f"| {s['line']} | {s['name']} |")
    w("")

    # ── pages
    w("## 📄 หน้า (page) → ตัวโหลด → mount point")
    w("")
    w("`showPage(key)` คือ router · มันซ่อน `.page` ทุกตัวแล้วโชว์ `#page-<key>` "
      "จากนั้นเรียก loader ตามตาราง")
    w("")
    w("| page id | บรรทัด | key ที่ส่งให้ showPage | loader | mount point (JS เขียน innerHTML ลงตรงนี้) |")
    w("|---|---|---|---|---|")
    for p in pages:
        loaders = routes.get(p['key'], [])
        lstr = ' · '.join(
            f"`{n}()` @{fn_by_name[n]['line']}" if n in fn_by_name else f"`{n}()`"
            for n in loaders
        ) or '—'
        mounts = ' '.join(f"`#{m}`" for m in p['mounts']) or '—'
        w(f"| `{p['id']}` | {p['line']}–{p['end']} | `{p['key']}` | {lstr} | {mounts} |")
    w("")

    # ── functions by section
    w("## 🔧 Functions")
    w("")
    bounds = [(s['line'], s['name']) for s in sections]

    def sect_of(line):
        cur = '(ก่อน section แรก)'
        for l, n in bounds:
            if l <= line:
                cur = n
            else:
                break
        return cur

    grouped = {}
    for f in fns:
        grouped.setdefault(sect_of(f['line']), []).append(f)

    for sect, items in grouped.items():
        w(f"### {sect}")
        w("")
        w("| บรรทัด | function |")
        w("|---|---|")
        for f in items:
            a = 'async ' if f['is_async'] else ''
            rng = f"{f['line']}–{f['end']}" if f['end'] else str(f['line'])
            w(f"| {rng} | {a}`{f['name']}({f['args']})` |")
        w("")

    # ── state
    w("## 🌐 Global state")
    w("")
    w("> ตัวแปรพวกนี้อยู่นอก function = ทุกหน้าใช้ร่วมกัน · "
      "**แก้ function ที่เขียนตัวไหน ต้องไล่ดูทุกตัวที่อ่านมันด้วย**")
    w("")
    w("| บรรทัด | ตัวแปร | ค่าเริ่มต้น | ถูกอ้างถึง (บรรทัด) |")
    w("|---|---|---|---|")
    for s in state:
        refs = [l for l in call_sites(src, s['name'])] or []
        allrefs = [line_of(src, m.start())
                   for m in re.finditer(r'\b' + re.escape(s['name']) + r'\b', src)]
        shown = ', '.join(str(x) for x in allrefs[:12])
        more = f" …(+{len(allrefs)-12})" if len(allrefs) > 12 else ''
        init = (s['init'][:40] + '…') if len(s['init']) > 40 else s['init']
        w(f"| {s['line']} | `{s['name']}` | `{init or '—'}` | {shown}{more} |")
    w("")

    # ── timers
    w("## ⏱️ Timer / Polling")
    w("")
    w("| ตั้งที่บรรทัด | handle | ชนิด | เรียก | เคลียร์ที่บรรทัด |")
    w("|---|---|---|---|---|")
    for tm in timers:
        cl = [str(c['line']) for c in clears if c['handle'] == tm['handle']]
        mark = ', '.join(cl) if cl else '**⚠️ ไม่เคยเคลียร์**'
        w(f"| {tm['line']} | `{tm['handle']}` | set{tm['kind']} | `{tm['fn']}` | {mark} |")
    w("")

    # ── monkey patch
    if patched:
        w("## 🐒 Function ที่ถูกเขียนทับภายหลัง (monkey patch)")
        w("")
        w("> 🔴 **อ่านก่อนแก้:** ตัวประกาศเดิมกับตัวที่ทำงานจริง**คนละตัว** · "
          "แก้ที่ `function foo()` เฉยๆ จะไม่มีผลกับ wrapper")
        w("")
        w("| function | ประกาศเดิม | ถูกเขียนทับที่ |")
        w("|---|---|---|")
        for p in patched:
            orig = fn_by_name.get(p['name'], {}).get('line', '?')
            w(f"| `{p['name']}` | {orig} | **{p['line']}** |")
        w("")

    # ── endpoints
    w("## 🔌 Backend endpoints ที่ frontend เรียก")
    w("")
    w("`:x` = ส่วนที่เป็นตัวแปร (template literal)")
    w("")
    w("| method | path | เรียกที่บรรทัด |")
    w("|---|---|---|")
    for (method, path), ls in sorted(eps.items(), key=lambda kv: kv[0][1]):
        w(f"| {method} | `{path}` | {', '.join(str(x) for x in sorted(set(ls)))} |")
    w("")

    w("---")
    w("")
    w(f"_generated by `tools/gen_map.py` · source sha256 `{digest}`_")
    return '\n'.join(o) + '\n'


# ── main ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=str(ROOT / 'index.html'))
    ap.add_argument('--out', default=str(ROOT / 'INDEX_MAP.md'))
    ap.add_argument('--check', action='store_true',
                    help='ไม่เขียนไฟล์ · exit 1 ถ้า map ไม่ตรงกับโค้ดปัจจุบัน')
    args = ap.parse_args()

    src_path = Path(args.src)
    out_path = Path(args.out)
    if not src_path.exists():
        print(f"✗ ไม่พบ {src_path}", file=sys.stderr)
        return 2

    content = build(src_path)

    if args.check:
        if not out_path.exists():
            print(f"✗ ยังไม่มี {out_path.name} — รัน `python tools/gen_map.py` ก่อน")
            return 1
        old = out_path.read_text(encoding='utf-8')
        # เทียบเฉพาะ sha ของ source — timestamp ต่างกันไม่นับ
        new_sha = re.search(r'sha256 `(\w+)`', content).group(1)
        old_sha_m = re.search(r'sha256 `(\w+)`', old)
        if old_sha_m and old_sha_m.group(1) == new_sha:
            print(f"✓ {out_path.name} ตรงกับ {src_path.name} (sha {new_sha})")
            return 0
        print(f"✗ {out_path.name} เก่าแล้ว — รัน `python tools/gen_map.py` เพื่ออัปเดต")
        return 1

    out_path.write_text(content, encoding='utf-8')
    print(f"✓ เขียน {out_path.name} แล้ว ({content.count(chr(10)):,} บรรทัด)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
