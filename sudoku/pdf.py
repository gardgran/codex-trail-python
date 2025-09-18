"""Helpers for exporting Sudoku puzzles to PDF files."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _board_to_lines(board: Sequence[Sequence[int]]) -> list[str]:
    lines: list[str] = []
    for row_idx, row in enumerate(board):
        parts: list[str] = []
        for col_idx, value in enumerate(row):
            if col_idx and col_idx % 3 == 0:
                parts.append("|")
            parts.append(str(value) if value else ".")
        lines.append(" ".join(parts))
        if row_idx % 3 == 2 and row_idx != 8:
            lines.append("")
    return lines


def _build_text_stream(title: str, difficulty: str, puzzle_lines: Iterable[str], solution_lines: Iterable[str]) -> bytes:
    y_position = 780
    line_height = 16
    segments = [
        "BT\n",
        "/F1 18 Tf\n",
        f"1 0 0 1 72 {y_position} Tm\n({_escape_pdf_text(title)}) Tj\n",
    ]

    y_position -= 30
    segments.append("/F1 12 Tf\n")
    segments.append(f"1 0 0 1 72 {y_position} Tm\n(Difficulty: {_escape_pdf_text(difficulty)}) Tj\n")

    y_position -= 24
    segments.append(f"1 0 0 1 72 {y_position} Tm\n(Puzzle:) Tj\n")

    for line in puzzle_lines:
        if line:
            y_position -= line_height
            segments.append(f"1 0 0 1 72 {y_position} Tm\n({_escape_pdf_text(line)}) Tj\n")
        else:
            y_position -= line_height // 2

    y_position -= 24
    segments.append(f"1 0 0 1 72 {y_position} Tm\n(Solution:) Tj\n")

    for line in solution_lines:
        if line:
            y_position -= line_height
            segments.append(f"1 0 0 1 72 {y_position} Tm\n({_escape_pdf_text(line)}) Tj\n")
        else:
            y_position -= line_height // 2

    segments.append("ET\n")
    return "".join(segments).encode("utf-8")


def _build_pdf_document(content_stream: bytes) -> bytes:
    parts: list[bytes] = []
    offsets: list[int] = [0]
    current_length = 0

    def append(data: bytes) -> None:
        nonlocal current_length
        parts.append(data)
        current_length += len(data)

    def add_object(obj_number: int, body: bytes) -> None:
        nonlocal current_length
        offsets.append(current_length)
        obj_header = f"{obj_number} 0 obj\n".encode("ascii")
        obj_footer = b"\nendobj\n"
        append(obj_header + body + obj_footer)

    append(b"%PDF-1.4\n")

    add_object(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    add_object(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add_object(
        3,
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    )
    add_object(4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    stream_header = f"<< /Length {len(content_stream)} >>\nstream\n".encode("ascii")
    stream_body = stream_header + content_stream + b"\nendstream"
    add_object(5, stream_body)

    xref_offset = current_length
    xref_entries = len(offsets)
    xref_lines = ["xref\n", f"0 {xref_entries}\n", "0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref_lines.append(f"{offset:010} 00000 n \n")
    append("".join(xref_lines).encode("ascii"))

    trailer = (
        "trailer\n"
        f"<< /Size {xref_entries} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n"
        "%%EOF\n"
    )
    append(trailer.encode("ascii"))

    return b"".join(parts)


def export_puzzle_to_pdf(path: str | Path, puzzle: Sequence[Sequence[int]], solution: Sequence[Sequence[int]], difficulty: str) -> Path:
    """Write the puzzle and solution to ``path`` and return the resulting :class:`Path`."""

    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    puzzle_lines = _board_to_lines(puzzle)
    solution_lines = _board_to_lines(solution)
    content_stream = _build_text_stream("Sudoku Puzzle", difficulty, puzzle_lines, solution_lines)
    pdf_bytes = _build_pdf_document(content_stream)
    path_obj.write_bytes(pdf_bytes)
    return path_obj
