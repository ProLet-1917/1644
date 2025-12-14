#!/usr/bin/env python3
"""Update nobles culture for locations where only nobles are jurchen

For each location block in main_menu/setup/start/06_pops.txt:
- If the only pops that have culture=jurchen_culture are those with type=nobles (one or more),
  and at least one pop with culture=mongolian_culture or culture=tumed_culture exists,
  then sum sizes of pops of mongolian/tumed inside that location and set the
  culture of the nobles pop(s) (that were jurchen) to the culture with larger total size.

Creates a backup before applying changes.
"""
from pathlib import Path
import re

TARGET_FILE = Path("main_menu/setup/start/06_pops.txt")
BACKUP_FILE = TARGET_FILE.with_suffix(TARGET_FILE.suffix + ".nobles.bak")

MONGO = "mongolian_culture"
TUMED = "tumed_culture"
JURCHEN = "jurchen_culture"


def find_matching_brace(text: str, start_idx: int) -> int:
    j = start_idx
    depth = 0
    n = len(text)
    while j < n:
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return -1


def process(text: str) -> (str, int):
    pattern = re.compile(r"([^^\s=\n][^=\n]*)\s*=\s*{")
    i = 0
    n = len(text)
    out = []
    changed = 0
    while True:
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break
        start = m.start()
        out.append(text[i:start])
        block_start = m.end() - 1  # position of '{'
        block_end = find_matching_brace(text, block_start)
        if block_end == -1:
            # malformed, append rest
            out.append(text[start:])
            break
        block = text[start:block_end]
        new_block, did_change = process_location_block(block)
        if did_change:
            changed += 1
        out.append(new_block)
        i = block_end
    return "".join(out), changed


def process_location_block(block: str) -> (str, bool):
    # Find define_pop blocks inside this location block
    pops = []  # list of tuples (start_idx, end_idx, block_text)
    idx = 0
    while True:
        m = re.search(r"define_pop\s*=\s*{", block[idx:])
        if not m:
            break
        s = idx + m.start()
        brace_start = idx + m.end() - 1
        e = find_matching_brace(block, brace_start)
        if e == -1:
            break
        e = e  # e is absolute index in block
        pop_block = block[s:e]
        pops.append((s, e, pop_block))
        idx = e

    # Parse pop attributes
    parsed = []
    for s, e, pb in pops:
        attrs = {k: v for k, v in re.findall(r"(\w+)\s*=\s*([^\s\}]+)", pb)}
        size = float(attrs.get("size", "0"))
        parsed.append({"s": s, "e": e, "text": pb, "attrs": attrs, "size": size})

    # Count cultures
    total_jurchen = sum(1 for p in parsed if p["attrs"].get("culture") == JURCHEN)
    nobles_jurchen = sum(1 for p in parsed if p["attrs"].get("type") == "nobles" and p["attrs"].get("culture") == JURCHEN)
    if total_jurchen == 0 or nobles_jurchen == 0:
        return block, False
    if total_jurchen != nobles_jurchen:
        # Some non-nobles have jurchen culture; condition fails
        return block, False

    # Check presence of mongolian or tumed pops and sum sizes
    sum_mongo = sum(p["size"] for p in parsed if p["attrs"].get("culture") == MONGO)
    sum_tumed = sum(p["size"] for p in parsed if p["attrs"].get("culture") == TUMED)
    if sum_mongo == 0 and sum_tumed == 0:
        return block, False

    # Choose culture: mongolian if tie
    target_culture = MONGO if sum_mongo >= sum_tumed else TUMED

    # Modify nobles pop(s) that have jurchen culture
    new_block = block
    offset = 0
    modified = False
    for p in parsed:
        if p["attrs"].get("type") == "nobles" and p["attrs"].get("culture") == JURCHEN:
            # replace culture value within p["text"]
            pb = p["text"]
            new_pb = re.sub(r"(culture\s*=\s*)" + re.escape(JURCHEN), r"\1" + target_culture, pb)
            if new_pb != pb:
                # replace in new_block at the adjusted indices
                s = p["s"] + offset
                e = p["e"] + offset
                new_block = new_block[:s] + new_pb + new_block[e:]
                offset += len(new_pb) - (p["e"] - p["s"])
                modified = True
    return new_block, modified


if __name__ == '__main__':
    text = TARGET_FILE.read_text(encoding='utf-8')
    BACKUP_FILE.write_text(text, encoding='utf-8')
    new_text, changed = process(text)
    if changed == 0:
        print("No locations changed.")
    else:
        TARGET_FILE.write_text(new_text, encoding='utf-8')
        print(f"Updated {changed} location(s) in {TARGET_FILE} (backup: {BACKUP_FILE})")
