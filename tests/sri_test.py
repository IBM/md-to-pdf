# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
"""Mermaid script tag carries a well-formed Subresource Integrity attribute."""

import re

from md_to_pdf.md2html import MERMAID_SRI, MERMAID_VERSION, create_html_document


def test_mermaid_script_has_sri():
    assert re.fullmatch(r"sha384-[A-Za-z0-9+/]{64}", MERMAID_SRI)
    html = create_html_document("t", "<p>x</p>")
    assert (
        f'<script src="https://unpkg.com/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js" '
        f'integrity="{MERMAID_SRI}" crossorigin="anonymous"></script>'
    ) in html
