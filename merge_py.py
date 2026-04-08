#!/usr/bin/env python3
from pathlib import Path
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Собрать все .py файлы дерева в один файл с разделителями"
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Корень дерева (по умолчанию текущая директория)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="all_code.py.txt",
        help="Имя выходного файла",
    )
    parser.add_argument(
        "-s",
        "--separator",
        default="#" * 80,
        help="Строка-разделитель между файлами",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_path = Path(args.output).resolve()
    sep = "\n\n" + args.separator + "\n\n"

    py_files = sorted(
        p for p in root.rglob("*.py")
        if p.is_file() and p.name != "__init__.py"
    )

    with out_path.open("w", encoding="utf-8") as out:
        first = True
        for p in py_files:
            if not first:
                out.write(sep)
            first = False

            rel = p.relative_to(root)
            out.write(f"# FILE: {rel}\n\n")
            out.write(p.read_text(encoding="utf-8", errors="replace"))
            if not p.read_text(encoding="utf-8", errors="replace").endswith("\n"):
                out.write("\n")

if __name__ == "__main__":
    main()
