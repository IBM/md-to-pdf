# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
"""Regression: literal placeholder-like text must not be replaced by real blocks."""

from md_to_pdf.md2html import convert

DOC = (
    "# T\n\nLiteral __CODE_BLOCK_0__ and __MERMAID_BLOCK_0__ here.\n\n"
    "```\nreal code\n```\n\n```mermaid\ngraph TD\n  A[Alpha] --> B[Beta]\n```\n"
)


def _convert(tmp_path, text):
    md = tmp_path / "a.md"
    md.write_text(text)
    return convert(md)


def test_literal_placeholder_text_unchanged(tmp_path):
    html = _convert(tmp_path, DOC)
    assert "__CODE_BLOCK_0__" in html
    assert "__MERMAID_BLOCK_0__" in html
    assert html.count("real code") == 1
    assert html.count('class="mermaid-container"') == 1


def test_nul_in_input_is_stripped(tmp_path):
    html = _convert(tmp_path, "# T\n\nfoo\x00CODE_BLOCK_0\x00bar\n\n```\nreal code\n```\n")
    assert "\x00" not in html
    assert html.count("real code") == 1
    assert "fooCODE_BLOCK_0bar" in html
