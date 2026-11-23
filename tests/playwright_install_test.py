import sys
from unittest.mock import MagicMock, patch
import pytest
from md_to_pdf import html2pdf


def test_missing_chromium_triggers_install(tmp_path):
    html_file = tmp_path / "test.html"
    pdf_file = tmp_path / "test.pdf"
    html_file.write_text("<!DOCTYPE html><html><body>Test</body></html>")

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.pdf.return_value = b"%PDF-1.4..."

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.side_effect = [
        Exception("Executable doesn't exist at /path/to/chromium"),
        mock_browser,
    ]

    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_playwright
    mock_cm.__exit__.return_value = None

    with patch("md_to_pdf.html2pdf.sync_playwright", return_value=mock_cm), \
         patch("subprocess.run") as mock_run:
        result = html2pdf.html_to_pdf_with_links(html_file, pdf_file)

        assert mock_run.call_count == 1
        assert mock_run.call_args[0][0] == [sys.executable, "-m", "playwright", "install", "chromium"]
        assert mock_run.call_args[1].get("check") is True
        assert mock_playwright.chromium.launch.call_count == 2
        assert result == pdf_file.absolute()


def test_other_launch_error_does_not_install_and_propagates(tmp_path):
    html_file = tmp_path / "test.html"
    pdf_file = tmp_path / "test.pdf"
    html_file.write_text("<!DOCTYPE html><html><body>Test</body></html>")

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.side_effect = Exception("Out of memory")

    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_playwright
    mock_cm.__exit__.return_value = None

    with patch("md_to_pdf.html2pdf.sync_playwright", return_value=mock_cm), \
         patch("subprocess.run") as mock_run:
        with pytest.raises(Exception, match="Out of memory"):
            html2pdf.html_to_pdf_with_links(html_file, pdf_file)

        mock_run.assert_not_called()
        assert mock_playwright.chromium.launch.call_count == 1
