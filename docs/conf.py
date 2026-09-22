"""Sphinx configuration for LexNeedle's public documentation."""

from __future__ import annotations

from importlib.metadata import version as distribution_version

project = "LexNeedle"
copyright = "2026, crootman"
author = "crootman"
release = distribution_version("lexneedle")

extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.doctest"]
templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_theme = "furo"
html_title = "LexNeedle"
html_static_path: list[str] = []
autodoc_typehints = "description"
myst_enable_extensions = ["colon_fence"]
doctest_global_setup = "from lexneedle import Matcher"
