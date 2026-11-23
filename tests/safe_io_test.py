# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
"""Regression: output symlinks (x.html / x.pdf) must never be written through."""

import pytest

from md_to_pdf.batch import batch_convert
from md_to_pdf.cli import convert_md_to_pdf
from md_to_pdf.safe_io import atomic_write

CANARY = "canary"


@pytest.fixture
def repo(tmp_path):
    """docs/x.md plus x.html and x.pdf symlinks pointing at a canary file."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "x.md").write_text("# Hi\n\n```\nssh-ed25519 AAAA\n```\n")
    canary = tmp_path / "canary"
    canary.write_text(CANARY)
    (docs / "x.html").symlink_to(canary)
    (docs / "x.pdf").symlink_to(canary)
    return docs, canary


def test_atomic_write_refuses_symlink(tmp_path):
    (tmp_path / "t").write_text(CANARY)
    (tmp_path / "l").symlink_to(tmp_path / "t")
    with pytest.raises(ValueError):
        atomic_write(tmp_path / "l", "x")
    assert (tmp_path / "t").read_text() == CANARY


def test_atomic_write_replaces_regular_file(tmp_path):
    atomic_write(tmp_path / "f", b"a")
    atomic_write(tmp_path / "f", "b")
    assert (tmp_path / "f").read_bytes() == b"b"
    assert [p.name for p in tmp_path.iterdir()] == ["f"]


def test_single_file_cli_does_not_follow_symlinks(repo):
    docs, canary = repo
    with pytest.raises(Exception, match="symlink"):  # PDF sink, wrapped by html2pdf
        convert_md_to_pdf(str(docs / "x.md"))
    assert canary.read_text() == CANARY


def test_keep_html_does_not_follow_symlink(repo):
    docs, canary = repo
    (docs / "x.pdf").unlink()
    with pytest.raises(ValueError):
        convert_md_to_pdf(str(docs / "x.md"), keep_html=True)
    assert canary.read_text() == CANARY


def test_batch_does_not_follow_symlinks(repo):
    docs, canary = repo
    batch_convert([str(docs)])
    assert canary.read_text() == CANARY


def test_normal_conversion_leaves_only_pdf(tmp_path):
    (tmp_path / "ok.md").write_text("# Hi\n")
    pdf = convert_md_to_pdf(str(tmp_path / "ok.md"))
    assert pdf.read_bytes().startswith(b"%PDF")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ok.md", "ok.pdf"]
