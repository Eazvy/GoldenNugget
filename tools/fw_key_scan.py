#!/usr/bin/env python3
"""Scan a dyld shared cache for preference-key-like strings and attribute
every hit to the dylib that contains it.

This is the extraction half of the firmware reverse-engineering workflow:

    fw_key_scan.py  <cache> [--shard .01] [--out new_keys.txt]
        strings  ->  image attribution  ->  diff vs the known key set

"Known" = everything GoldenNugget already writes (registry.py SPECS +
known_keys_data.py) plus the keys the iOS 27.0 analysis already catalogued
(docs/data/springboard_candidates_by_category.txt,
docs/data/springboard_accessor_key_pairs.txt). Anything left over is a
candidate for the next round of on-device verification.

Patterns cover the families the tweak registry uses:

    SB* / SBF*            SpringBoard preference keys
    UISolarium* / Solarium*   Liquid Glass renderer keys
    UIViewGlass* / *Glass*    UIKit glass keys
    Calistoga*            DesignLibrary glass recipes
    com.apple.SwiftUI.* / com.apple.UIKit.*   framework UserDefaults keys
    AM*                   Ambient (StandBy) keys

Usage
    python tools/fw_key_scan.py <cache> [more caches...] --out out.txt
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# key-like literals, ordered so the most specific family wins
PATTERNS = [
    r"com\.apple\.SwiftUI\.[A-Za-z0-9_]{2,63}",
    r"com\.apple\.UIKit\.[A-Za-z0-9_]{2,63}",
    r"UISolarium[A-Za-z0-9_]{2,63}",
    r"Solarium[A-Z][A-Za-z0-9_]{2,63}",
    r"UIViewGlass[A-Za-z0-9_]{2,63}",
    r"Calistoga[A-Za-z0-9_]{2,63}",
    r"SBDisable[A-Z][A-Za-z0-9_]{2,63}",
    r"SB[A-Z][A-Za-z0-9_]{4,63}",
    r"SBF[A-Z][A-Za-z0-9_]{2,63}",
    r"AM[A-Z][A-Za-z0-9_]{5,63}",
    r"[A-Z][A-Za-z0-9]*Glass[A-Za-z0-9_]{2,63}",
]
PATTERN = re.compile("|".join(f"(?:{p})" for p in PATTERNS))

# strings that match a pattern but are not preference keys. Only applied to
# strings that do NOT start with a known key family prefix - a new
# "SBDisableIconFlyInAnimation" must survive the filter.
NOISE = re.compile(
    r"^(Alert|Error|Warning|Notification|DidChange|Update|Animation|"
    r"Transition|Effect|Color|Font|Image|Icon|View|Controller|Button|Label|"
    r"Gesture|Recognizer|Layout|Constraint|Stack|Scroll|Section|Header|Footer|"
    r"Cell|Row|Item|Model|Manager|Service|Session|Request|Response|Task|Job|"
    r"Option|Setting|Preference|Domain|Bundle|Path|File|Folder|Directory|URL|"
    r"UUID|Date|Time|Timer|Counter|Index|Count|Size|Width|Height|Origin|Frame|"
    r"Point|Rect|Edge|Inset|Margin|Padding|Spacing|Alignment|Axis|Direction|"
    r"Orientation|Position|Location|Region|Zone|Area|Bounds|Content|Context|"
    r"State|Mode|Style|Theme|Appearance|Behavior|Action|Activity|Event|Signal|"
    r"Root|Key|Keys|Value|Values)s?$",
)
FAMILY_PREFIXES = ("SB", "SBF", "UISolarium", "Solarium", "UIViewGlass",
                   "Calistoga", "AM", "com.apple.")


def looks_like_key(text: str) -> bool:
    if text.startswith(FAMILY_PREFIXES):
        return True
    return not NOISE.match(text)


def parse_header(path: Path):
    """(mappings, images) from the cache header - same layout the other
    tools use (dyld_cache_lookup.py)."""
    with open(path, "rb") as fh:
        head = fh.read(0x200)
        mapping_off, mapping_cnt = struct.unpack_from("<II", head, 0x10)
        text_off, text_cnt = struct.unpack_from("<QQ", head, 0x88)
        fh.seek(mapping_off)
        raw = fh.read(mapping_cnt * 32)
        mappings = []
        for i in range(mapping_cnt):
            addr, size, foff = struct.unpack_from("<QQQ", raw, i * 32)[:3]
            mappings.append((addr, size, foff))
        fh.seek(text_off)
        raw = fh.read(text_cnt * 32)
        images = []
        for i in range(text_cnt):
            load_addr, text_size, poff = struct.unpack_from("<QII", raw, i * 32 + 16)
            fh.seek(poff)
            buf = bytearray()
            while True:
                c = fh.read(1)
                if not c or c == b"\0":
                    break
                buf += c
            images.append((load_addr, text_size, buf.decode("utf-8", "replace")))
    images.sort()
    return mappings, images


def owner_of(mappings, images, file_offset: int) -> str:
    """Attribute a file offset to its dylib.

    ``images`` is sorted by load address; a linear scan per hit is too slow
    when a cache yields millions of matches, so the lookup is a bisect.
    """
    addr = None
    for m_addr, m_size, m_foff in mappings:
        if m_foff <= file_offset < m_foff + m_size:
            addr = m_addr + (file_offset - m_foff)
            break
    if addr is None:
        return "<?>"
    lo, hi = 0, len(images)
    while lo < hi:
        mid = (lo + hi) // 2
        if images[mid][0] <= addr:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return "<?>"
    load_addr, text_size, path = images[lo - 1]
    if load_addr <= addr < load_addr + text_size:
        return path
    return "<?>"


def scan(cache: Path, mappings, images) -> dict:
    """grep -abo the cache, attribute each hit. {string: {image: count}}.

    Plain ERE alternation - no ``(?:...)``: toybox/BSD grep -E does not
    understand PCRE groups and silently returns nothing.

    STREAMING, never capture_output: a 2 GB cache matches tens of millions
    of times; buffering the whole grep output (plus splitlines) costs tens
    of GB of RAM. We read one match line at a time and keep only the
    distinct-string counts.
    """
    alternation = "|".join(PATTERNS)
    env = dict(os.environ, LC_ALL="C")
    hits: dict[str, dict[str, int]] = {}
    matches = 0
    proc = subprocess.Popen(
        ["grep", "-aboE", alternation, str(cache)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        env=env, bufsize=1 << 20)
    assert proc.stdout is not None
    with proc.stdout:
        for raw in proc.stdout:  # one "offset:match" line at a time
            offset_s, _sep, text = raw.partition(b":")
            try:
                offset = int(offset_s)
            except ValueError:
                continue
            text = text.strip().decode("utf-8", "replace")
            if not PATTERN.fullmatch(text):
                continue
            if not looks_like_key(text):
                continue
            matches += 1
            img = owner_of(mappings, images, offset)
            hits.setdefault(text, {}).setdefault(img, 0)
            hits[text][img] += 1
    proc.wait()
    print(f"  {matches:,} matches, {len(hits)} key-like strings")
    return hits


def known_keys() -> set:
    """Every key GoldenNugget already knows about, from repo sources."""
    keys: set[str] = set()
    # registry specs
    try:
        sys.path.insert(0, str(REPO))
        from src.tweaks.registry import SPECS
        for spec in SPECS:
            if spec.key:
                keys.add(spec.key)
    except Exception as error:  # PySide6 missing, etc.
        print(f"  (registry import failed: {error})", file=sys.stderr)
    # the generated known-keys table
    try:
        from batter_builder.known_keys_data import PATHS as KNOWN
        for path_keys in KNOWN.values():
            keys.update(path_keys)
    except Exception:
        pass
    # prior 27.0 analysis files
    for name in ("docs/data/springboard_candidates_by_category.txt",
                 "docs/data/springboard_accessor_key_pairs.txt",
                 "docs/data/registry_plist_channels.txt"):
        path = REPO / name
        if path.exists():
            keys.update(re.findall(r"[A-Za-z0-9_.]{6,}", path.read_text(errors="replace")))
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("caches", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    known = known_keys()
    print(f"known keys: {len(known)}")

    all_hits: dict[str, dict[str, int]] = {}
    for cache in args.caches:
        print(f"scanning {cache.name} ({cache.stat().st_size / 2**30:.1f} GiB) ...")
        mappings, images = parse_header(cache)
        hits = scan(cache, mappings, images)
        for text, images_hit in hits.items():
            for img, count in images_hit.items():
                all_hits.setdefault(text, {}).setdefault(img, 0)
                all_hits[text][img] += count
        print(f"  {len(hits)} key-like strings")

    new = {t: imgs for t, imgs in all_hits.items() if t not in known}
    print(f"\ntotal distinct: {len(all_hits)}   new (not in repo): {len(new)}")

    lines = []
    for text in sorted(new, key=lambda t: (-sum(new[t].values()), t)):
        total = sum(new[text].values())
        imgs = ", ".join(f"{img} x{c}" for img, c in
                         sorted(new[text].items(), key=lambda kv: -kv[1]))
        lines.append(f"{text}\t{total}\t{imgs}")
    report = "\n".join(lines)

    if args.out:
        args.out.write_text(report + "\n")
        print(f"written: {args.out}")
    else:
        print(report[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
