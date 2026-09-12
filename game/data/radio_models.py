"""RADIO's data shapes, shared by the shipped catalog (assets/data/
radio_stations.json, radio_profiles.json -- see game/data/catalog.py) and
the user's own save-data additions (SaveData.custom_radios -- see
game/data/store.py), so both sources validate against the exact same
model and documentation lives here instead of a "_comment" field
scattered across the JSON files themselves."""
from typing import Optional

from pydantic import BaseModel, Field


class RadioStation(BaseModel):
    """One RADIO station -- shown in the STATIONS/TUNER/SIGNAL submodule
    matching its `source` (see game/modules/radio/__init__.py).

    `source` is one of:
      - "local": loops a file at `path`, relative to assets/sounds/radio/.
      - "youtube": downloads `url` once via yt-dlp into save/radio_cache/,
        then plays that cached copy on every subsequent tune-in.
      - "stream": plays `url` live, directly, and never caches it -- same
        shape the online directory check (game/modules/radio/directory.py)
        produces automatically.
      - "tuner": a stub for real FM/AM hardware, gated by
        config.LOCAL_RADIO_AVAILABLE -- `frequency` is documentation for
        when a real receiver gets wired up, not read by anything yet.

    `profile` picks a distortion profile from radio_profiles.json by key,
    defaulting to "clean" (no distortion) when omitted. `description`, if
    set, shows below the waveform panel while this station is playing.
    """
    title: str
    source: str
    url: Optional[str] = None
    path: Optional[str] = None
    profile: Optional[str] = None
    frequency: Optional[str] = None
    description: Optional[str] = None


class RadioProfile(BaseModel):
    """A RADIO distortion profile: an ffmpeg audio filter chain (empty
    `filters` = no distortion) applied to the decode pipeline, so the live
    waveform naturally reflects whatever's actually audible rather than a
    separate pre-filter signal. `waveform_enabled=False` turns the
    waveform off entirely for this profile (some distortion makes it
    unreadable noise anyway)."""
    label: str
    filters: list[str] = Field(default_factory=list)
    waveform_enabled: bool = True
