import esper
import pygame as pg

from core.components import Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import save_data, theme
from game.modules.data import holotape_reader
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState, menu_right_column_left, render_text
from utils.logger import logger
from utils.settings import config

_RIGHT_COLUMN_LEFT = menu_right_column_left()
_RIGHT_COLUMN_TOP = 92
_ROW_HEIGHT = 33

_HOLOTAPE_TEXT_RECT = pg.Rect(
    _RIGHT_COLUMN_LEFT, _RIGHT_COLUMN_TOP,
    config.WIDTH - UI_MARGIN - _RIGHT_COLUMN_LEFT, config.HEIGHT - _RIGHT_COLUMN_TOP - 55)

# A page with no <menu> at all (a dead end in the source XML -- e.g. one
# entry in the shipped System_Calibration test fixture) always gets this
# synthetic fallback instead, so there's never a page confirm can't escape.
_FALLBACK_MENU = [holotape_reader.HolotapeMenuItem(target="Exit", label="[< Back]")]

# None while browsing the top-level holotape list; once a title is
# confirmed, holds which holotape/page is open plus whatever static_text
# is currently "stuck" (see _show_page). Module-level like RADIO's/MAP's
# own singleton state, since HOLOTAPES is a single always-registered node.
_reader_state = {"folder": None, "page_index": 0, "static_text": ""}
_holotape_folders: list = []
_holotape_menu_ent = None
_holotape_text_ent = None


def register(pipboy):
    create_node("data", "DATA")
    _register_quests()
    _register_stats()
    _register_holotapes()


def _register_quests():
    color = theme.draw_color
    quests = save_data.quests
    titles = [f"{q.get('title', '?')} ({q.get('status', '?')})" for q in quests]

    obj_font = ResourceLoader.get_font("MONOFONTO", 24)
    max_objectives = max((len(q.get("objectives", [])) for q in quests), default=0)
    obj_ents = [
        esper.create_entity(
            Position(_RIGHT_COLUMN_LEFT, 0), Renderable(visible=False), Layer(5), Dirty(1), OwnedBy("data.quests"))
        for _ in range(max_objectives)
    ]

    def refresh(index):
        objectives = quests[index].get("objectives", []) if index < len(quests) else []
        for row_index, ent in enumerate(obj_ents):
            renderable = esper.component_for_entity(ent, Renderable)
            if row_index < len(objectives):
                renderable.image = render_text(obj_font, f"- {objectives[row_index]}", color)
                renderable.visible = True
                esper.component_for_entity(ent, Position).y = _RIGHT_COLUMN_TOP + row_index * _ROW_HEIGHT
            else:
                renderable.visible = False
            esper.component_for_entity(ent, Dirty).state = 1

    menu_state = MenuState(items=titles, on_change=refresh)
    create_node("data.quests", "QUESTS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), menu_state,
    ])

    refresh(0)


def _register_stats():
    # No dedicated gameplay-stats model exists yet (see the follow-up
    # content plan) -- shows what's already real (player progression)
    # rather than inventing placeholder counters.
    player = save_data.player
    items = [
        f"LEVEL: {player.level}",
        f"TOTAL XP: {player.total_exp}",
        f"NEXT LEVEL XP: {player.next_level_xp}",
    ]
    create_node("data.stats", "STATS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=items),
    ])


def _register_holotapes():
    global _holotape_menu_ent, _holotape_text_ent

    _holotape_folders.extend(holotape_reader.list_holotape_folders())

    menu_state = MenuState(items=_holotape_titles(), max_items=9, on_confirm=_on_holotape_confirm)
    _holotape_menu_ent = create_node("data.holotapes", "HOLOTAPES", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), menu_state,
    ])
    _holotape_text_ent = esper.create_entity(
        Position(_HOLOTAPE_TEXT_RECT.left, _HOLOTAPE_TEXT_RECT.top), Renderable(image=_render_holotape_text("")),
        Layer(5), Dirty(1), OwnedBy("data.holotapes"))

    esper.set_handler("node_resumed", _on_holotapes_resumed)


def _holotape_titles() -> list:
    titles = []
    for folder in _holotape_folders:
        tape = holotape_reader.load_holotape(folder)
        titles.append(tape.title if tape else folder)
    return titles


def _on_holotapes_resumed(key):
    # Reopening HOLOTAPES (from another DATA tab, or a different top-level
    # tab entirely) always lands back on the title list -- same "transient
    # session state resets on tab-away" rule MAP already uses for its
    # cursor/pan/zoom. This also means a dead-end page (one with no <menu>
    # at all, besides the _FALLBACK_MENU catch below) is never truly
    # stuck -- switching away and back always recovers.
    if key == "data.holotapes" and _reader_state["folder"] is not None:
        _exit_holotape()


def _wrap_text(font, text: str, max_width: int) -> list:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _render_holotape_text(text: str) -> pg.Surface:
    image = pg.Surface(_HOLOTAPE_TEXT_RECT.size)
    image.fill(theme.bg_color)
    if not text:
        return image

    font = ResourceLoader.get_font("MONOFONTO", 24)
    color = theme.draw_color
    line_height = font.get_height() + 4
    y = 0
    for paragraph in text.split("\n"):
        if not paragraph:
            y += line_height
            continue
        for line in _wrap_text(font, paragraph, _HOLOTAPE_TEXT_RECT.width):
            if y + line_height > _HOLOTAPE_TEXT_RECT.height:
                return image
            image.blit(font.render(line, True, color), (0, y))
            y += line_height
    return image


def _set_holotape_text(text: str):
    esper.component_for_entity(_holotape_text_ent, Renderable).image = _render_holotape_text(text)
    esper.component_for_entity(_holotape_text_ent, Dirty).state = 1


def _set_holotape_menu(items: list):
    menu_state = esper.component_for_entity(_holotape_menu_ent, MenuState)
    menu_state.items = items
    menu_state.selected = 0
    menu_state.index = 0
    esper.component_for_entity(_holotape_menu_ent, Dirty).state = 1


def _current_page_menu(tape, page):
    return page.menu or _FALLBACK_MENU


def _show_page(page_index: int):
    tape = holotape_reader.load_holotape(_reader_state["folder"])
    if tape is None or not (0 <= page_index < len(tape.pages)):
        return
    page = tape.pages[page_index]
    _reader_state["page_index"] = page_index
    if page.static_text:
        # Sticky: once a page sets its own header text, later pages that
        # don't redefine it keep showing the last one -- matches a real
        # terminal session (Edwins_Terminal/bedford_station only set
        # static_text on their very first page, but the ROBCO letterhead
        # should stay up while reading their later pages too).
        _reader_state["static_text"] = page.static_text

    text = _reader_state["static_text"] + (f"\n{page.dynamic_text}" if page.dynamic_text else "")
    _set_holotape_text(text)
    _set_holotape_menu([item.label for item in _current_page_menu(tape, page)])


def _enter_holotape(folder: str):
    tape = holotape_reader.load_holotape(folder)
    if tape is None or not tape.pages:
        return
    _reader_state["folder"] = folder
    _reader_state["static_text"] = ""
    _show_page(0)


def _exit_holotape():
    _reader_state["folder"] = None
    _reader_state["static_text"] = ""
    _set_holotape_menu(_holotape_titles())
    _set_holotape_text("")


def _play_holotape_audio(folder: str, filename: str):
    if not config.SOUND_ENABLED:
        return
    key = f"holotape_{folder}_{filename}"
    try:
        ResourceLoader.add_sound(key, holotape_reader.audio_path(folder, filename)).play()
    except Exception as exc:
        logger.debug(f"Failed to play holotape audio {folder}/{filename}: {exc}")


def _on_holotape_confirm(selected_index: int):
    if _reader_state["folder"] is None:
        # Browsing the top-level list -- confirm opens that holotape.
        if 0 <= selected_index < len(_holotape_folders):
            _enter_holotape(_holotape_folders[selected_index])
        return

    tape = holotape_reader.load_holotape(_reader_state["folder"])
    page = tape.pages[_reader_state["page_index"]]
    items = _current_page_menu(tape, page)
    if not (0 <= selected_index < len(items)):
        return

    target = items[selected_index].target
    if target == "Exit":
        _exit_holotape()
    elif target.isdigit():
        _show_page(int(target))
    else:
        _play_holotape_audio(_reader_state["folder"], target)
