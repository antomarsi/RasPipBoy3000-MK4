"""Parses assets/holotapes/<folder>/holotape.xml -- a small Fallout-
terminal-style hypertext format, ported as-is from the zapwizard/pypboy
project's own holotape assets rather than invented here. Each holotape is
a tree of <page> elements (addressed by sibling index, 0-based) with:

- <static_text>: shown once a page defines it, and stays shown on every
  later page until a different page overrides it (matches how a real
  terminal's letterhead stays on screen through a whole session) -- see
  DATA's own "sticky" handling of this in game/modules/data/__init__.py.
- <dynamic_text>: that page's actual content (quest/journal flavor text,
  or a description of what's on this page).
- <menu><item page="...">[label]</item>...</menu>: each item's `page`
  attribute is either "Exit" (leave the reader), a page index (jump
  there), or a filename ending in an audio extension (play that clip --
  see game/modules/data/__init__.py's _play_holotape_audio(), which uses
  pygame's own mixer rather than RADIO's streaming ffmpeg pipeline, since
  these are short one-shot clips, not continuous playback).

A <console> tag appears in one shipped file (bedford_station) -- in the
original pypboy hardware build it drives a real GPIO relay (physical
spotlights wired to their prop). There's no matching hardware here, so
it's intentionally never parsed/acted on.

Literal "\\n" sequences in the source text (an authoring convention, not
real newlines) are unescaped to real newlines when parsed.
"""
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

from utils.logger import logger
from utils.settings import config


@dataclass
class HolotapeMenuItem:
    target: str
    label: str


@dataclass
class HolotapePage:
    static_text: Optional[str] = None
    dynamic_text: Optional[str] = None
    menu: list = field(default_factory=list)  # list[HolotapeMenuItem]


@dataclass
class Holotape:
    folder: str
    title: str
    kind: str
    pages: list  # list[HolotapePage]


_cache: dict = {}  # folder -> Holotape, parsed at most once per run


def list_holotape_folders() -> list:
    """Every subfolder of HOLOTAPES_FOLDER that actually has a
    holotape.xml, sorted for a stable menu order."""
    if not os.path.isdir(config.HOLOTAPES_FOLDER):
        return []
    return sorted(
        name for name in os.listdir(config.HOLOTAPES_FOLDER)
        if os.path.isfile(os.path.join(config.HOLOTAPES_FOLDER, name, "holotape.xml"))
    )


def _unescape(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    text = raw.replace("\\n", "\n").strip("\n")
    return text or None


def load_holotape(folder: str) -> Optional[Holotape]:
    """Parses (and caches) `folder`'s holotape.xml, or returns None if it's
    missing/malformed -- never raises, so one bad holotape can't crash the
    whole HOLOTAPES list."""
    if folder in _cache:
        return _cache[folder]

    path = os.path.join(config.HOLOTAPES_FOLDER, folder, "holotape.xml")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        logger.debug(f"Failed to parse holotape {folder!r}: {exc}")
        return None

    metadata = root.find("metadata")
    title = ((metadata.findtext("title") if metadata is not None else None) or folder).strip()
    kind = ((metadata.findtext("type") if metadata is not None else None) or "").strip()

    pages = []
    for page_el in root.findall("page"):
        menu = [
            HolotapeMenuItem(target=item_el.get("page", "Exit"), label=(item_el.text or "").strip())
            for item_el in page_el.findall("menu/item")
        ]
        pages.append(HolotapePage(
            static_text=_unescape(page_el.findtext("static_text")),
            dynamic_text=_unescape(page_el.findtext("dynamic_text")),
            menu=menu,
        ))

    holotape = Holotape(folder=folder, title=title, kind=kind, pages=pages)
    _cache[folder] = holotape
    return holotape


def audio_path(folder: str, filename: str) -> str:
    """Path relative to ASSETS_FOLDER, for ResourceLoader.add_sound()."""
    return os.path.join("holotapes", folder, filename)
