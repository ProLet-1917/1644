from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from openpyxl import load_workbook


EXCEL_PATH = Path("eu5_1644人物三围 v0.1.xlsx")
TARGET_PATH = Path("main_menu/setup/start/99_1644_05_characters.txt")


@dataclass(frozen=True)
class StatBlock:
    adm: Optional[int]
    dip: Optional[int]
    mil: Optional[int]

    @classmethod
    def from_row(cls, row: Sequence[Optional[object]], indexes: Dict[str, int]) -> Optional["StatBlock"]:
        def pull(key: str) -> Optional[int]:
            idx = indexes.get(key)
            if idx is None:
                return None
            raw = row[idx]
            if raw is None:
                return None
            if isinstance(raw, (int, float)):
                return int(raw)
            text = str(raw).strip()
            if not text:
                return None
            return int(float(text))

        adm = pull("adm")
        dip = pull("dip")
        mil = pull("mil")
        if adm is None and dip is None and mil is None:
            return None
        return cls(adm=adm, dip=dip, mil=mil)


def load_stats() -> Dict[str, StatBlock]:
    workbook = load_workbook(EXCEL_PATH, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) < 3:
        raise RuntimeError("Excel 数据量不足，无法解析。")

    header_row = rows[1]
    index_map: Dict[str, int] = {}
    for idx, header in enumerate(header_row):
        if header is None:
            continue
        header = str(header).strip()
        if header == "adm(行政)":
            index_map["adm"] = idx
        elif header == "dip（外交）":
            index_map["dip"] = idx
        elif header == "mil（军事）":
            index_map["mil"] = idx
        elif header == "script":
            index_map["script"] = idx

    required = {"adm", "dip", "mil", "script"}
    missing = required - index_map.keys()
    if missing:
        raise RuntimeError(f"缺少必要列：{missing}")

    mapping: Dict[str, StatBlock] = {}
    for row in rows[2:]:
        script_cell = row[index_map["script"]]
        if script_cell is None:
            continue
        script = str(script_cell).strip()
        if not script:
            continue
        stats = StatBlock.from_row(row, index_map)
        if stats is None:
            continue
        mapping[script] = stats
    return mapping


def rewrite_character_file(stats_map: Dict[str, StatBlock]) -> None:
    content = TARGET_PATH.read_text(encoding="utf-8").splitlines()
    result: List[str] = []
    i = 0

    def process_block(block_lines: List[str], identifier: str) -> List[str]:
        stats = stats_map.get(identifier)
        if not stats:
            return block_lines

        clean_lines: List[str] = []
        for line in block_lines:
            stripped = line.strip()
            if stripped.startswith("adm =") or stripped.startswith("dip =") or stripped.startswith("mil ="):
                continue
            clean_lines.append(line)

        insert_position = len(clean_lines) - 1  # default before closing brace
        for idx, line in enumerate(clean_lines):
            stripped = line.strip()
            if stripped.startswith("religion ="):
                insert_position = idx + 1
        if insert_position >= len(clean_lines):
            insert_position = len(clean_lines) - 1

        stat_entries: List[Tuple[str, Optional[int]]] = [
            ("adm", stats.adm),
            ("dip", stats.dip),
            ("mil", stats.mil),
        ]
        stat_lines = [
            f"\t\t\t{key} = {value}"
            for key, value in stat_entries
            if value is not None
        ]
        if not stat_lines:
            return block_lines
        clean_lines[insert_position:insert_position] = stat_lines
        return clean_lines

    while i < len(content):
        line = content[i]
        stripped = line.lstrip()
        if stripped.startswith("#") or not stripped.startswith("chi_"):
            result.append(line)
            i += 1
            continue

        if stripped.endswith("= {"):
            identifier = stripped.split("=")[0].strip()
            block: List[str] = [line]
            i += 1
            brace_depth = 1
            while i < len(content):
                block_line = content[i]
                block.append(block_line)
                brace_depth += block_line.count("{")
                brace_depth -= block_line.count("}")
                i += 1
                if brace_depth == 0:
                    break
            processed = process_block(block, identifier)
            result.extend(processed)
        else:
            result.append(line)
            i += 1

    TARGET_PATH.write_text("\n".join(result) + "\n", encoding="utf-8")


def main() -> None:
    stats_map = load_stats()
    rewrite_character_file(stats_map)


if __name__ == "__main__":
    main()


