#!/usr/bin/env python3
"""
add_utf8_bom.py

示例脚本：为指定文件自动补齐 UTF-8 BOM，以满足 PDX 引擎的编码要求。

用法：
    python tools/add_utf8_bom.py path/to/file1 path/to/file2 ...
    # 或者直接在目标目录内执行（无参数时默认处理当前工作目录）
    python tools/add_utf8_bom.py

脚本会：
    - 逐个读取目标文件的字节流；
    - 若缺失 UTF-8 BOM（EF BB BF），则自动添加；
    - 若已存在 BOM，则跳过并提示；
    - 输出处理结果摘要，便于在批量运行后核对日志。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"
ALLOWED_SUFFIXES = {".yml", ".yaml", ".txt"}


def ensure_bom(path: Path) -> bool:
    if not path.exists():
        return False
    data = path.read_bytes()
    if data.startswith(BOM):
        return False
    path.write_bytes(BOM + data)
    return True


def contains_setup(path: Path) -> bool:
    return any("setup" in part.lower() for part in path.parts)


def iter_target_files(paths: list[str]) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    missing: list[Path] = []

    for raw in paths:
        target = Path(raw).resolve()
        if not target.exists():
            missing.append(target)
            continue

        if target.is_file():
            if contains_setup(target):
                continue
            if target.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            files.append(target)
            continue

        for root, dirnames, filenames in os.walk(target):
            root_path = Path(root)
            if contains_setup(root_path):
                dirnames[:] = []
                continue
            for name in filenames:
                file_path = root_path / name
                if contains_setup(file_path):
                    continue
                if file_path.suffix.lower() not in ALLOWED_SUFFIXES:
                    continue
                files.append(file_path)

    return files, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="为文件补齐 UTF-8 BOM（缺省处理当前工作目录）。"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="需要处理的文件路径，留空则处理当前工作目录。",
    )
    args = parser.parse_args(argv)

    input_paths = args.files or ["."]
    targets, missing = iter_target_files(input_paths)

    seen: set[Path] = set()
    changed: list[Path] = []
    for path in targets:
        if path in seen:
            continue
        seen.add(path)
        if ensure_bom(path):
            changed.append(path)

    for path in missing:
        print(f"[缺失] 文件/目录不存在：{path}")

    for path in changed:
        print(f"[修正] 已补齐 BOM：{path}")

    if not targets:
        print("[完成] 未找到可处理文件。")
    elif not missing and not changed:
        print("[完成] 未发现需要修正的文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

