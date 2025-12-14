#!/usr/bin/env python3
"""Set religion=tungusic_shamanism for tribesman pops with specific cultures

Scans main_menu/setup/start/06_pops.txt and for every define_pop={ ... }
where type=tribesman and culture is one of the target cultures, ensures
religion=tungusic_shamanism is present (replacing any existing religion).
Creates a backup file with .bak extension before modifying.
"""
from pathlib import Path
import re

TARGET_FILE = Path("main_menu/setup/start/06_pops.txt")
BACKUP_FILE = TARGET_FILE.with_suffix(TARGET_FILE.suffix + ".bak")
TARGET_CULTURES = {"jurchen_culture", "oroqen_culture", "solon_culture"}


def process(text: str) -> str:
    # Pattern to match a define_pop block including nested braces (simple approach)
    # We'll parse by finding 'define_pop={' and then consuming until matching '}' at same depth.
    out = []
    i = 0
    n = len(text)
    pattern = re.compile(r"define_pop\s*=\s*{")
    while i < n:
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break
        start = m.start()
        out.append(text[i:start])
        # Find block starting from the opening brace
        j = m.end()
        depth = 1
        while j < n and depth > 0:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        block = text[start:j]
        new_block = process_block(block)
        out.append(new_block)
        i = j
    return "".join(out)


def process_block(block: str) -> str:
    # Check type and culture
    # Use regex to find key=value pairs (keys are word chars and underscores)
    pairs = {k: v for k, v in re.findall(r"(\w+)\s*=\s*([^\s\}]+)", block)}
    type_val = pairs.get("type")
    if type_val in {"tribesman", "tribesmen"} and pairs.get("culture") in TARGET_CULTURES:
        # Replace or add religion
        if re.search(r"\breligion\s*=", block):
            block = re.sub(r"\breligion\s*=\s*[^\s\}]+", "religion=tungusic_shamanism", block)
        else:
            # insert before the closing brace of the define_pop block
            block = block.rstrip()
            if block.endswith('}'):
                block = block[:-1] + "\n	religion=tungusic_shamanism\n}"
    return block


if __name__ == '__main__':
    text = TARGET_FILE.read_text(encoding='utf-8')
    BACKUP_FILE.write_text(text, encoding='utf-8')
    new_text = process(text)
    if new_text == text:
        print("No changes necessary.")
    else:
        TARGET_FILE.write_text(new_text, encoding='utf-8')
        print(f"Updated {TARGET_FILE} (backup saved to {BACKUP_FILE})")
