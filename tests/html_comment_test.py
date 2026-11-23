# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
"""Regression: HTML comments are dropped, not shown as text, when raw HTML is escaped."""

from md_to_pdf.md2html import convert


def test_html_comment_is_not_rendered(tmp_path):
    md = tmp_path / "a.md"
    md.write_text("<!--\nhidden note\n-->\n\n# T\n\nbody <b>x</b>\n")
    html = convert(md)
    assert "hidden note" not in html
    assert "&lt;b&gt;" in html
