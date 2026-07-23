#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="md-to-pdf",
    version="1.6.0",
    author="md-to-pdf Team",
    author_email="rene.auberger@de.ibm.com",
    description="Professional Markdown to PDF converter with Mermaid diagrams, clickable links, and page orientation control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ibm.com/technology-garage-dach/md-to-pdf",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "playwright>=1.40.0",
        "markdown>=3.5.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "md2pdf=md_to_pdf.cli:main",
            "md2html=md_to_pdf.md2html:main",
            "html2pdf=md_to_pdf.html2pdf:main",
            "md2pdf-batch=md_to_pdf.batch:main",
        ],
    },
    include_package_data=True,
)

# Made with Bob
