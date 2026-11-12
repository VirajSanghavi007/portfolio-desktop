"""Integration: multi-step flows across palette, windows, dock and desktop icons in real Chrome."""
from conftest import visible_view


def test_each_test_gets_fresh_state(open_page):
    """Proves the shared browser is safe: a change in one context does not leak into the next."""
    a = open_page()
    a.click('.side .nav button[data-view="work"]')
    a.click('[data-close="note-win"]')
    b = open_page()
    assert visible_view(b) == ["overview"]
    assert b.is_visible("#note-win")


def test_palette_enter_opens_view(page):
    page.keyboard.press("Control+k")
    page.fill("#palette-input", "résumé")
    page.keyboard.press("Enter")
    assert page.is_hidden("#palette")
    assert visible_view(page) == ["resume"]


def test_palette_click_shows_note(page):
    page.click('[data-close="note-win"]')
    assert page.is_hidden("#note-win")
    assert "Note hidden" in page.inner_text("#toast")
    page.click(".foot-l button")
    page.click("#palette-list li:has-text('little update')")
    assert page.is_visible("#note-win")


def test_close_main_window_then_reopen_from_dock(page):
    page.click('#main-win [data-close="main-win"]')
    assert page.is_hidden("#main-win")
    assert "Window closed" in page.inner_text("#toast")
    page.click('.dock [data-view="contact"]')
    assert page.is_visible("#main-win")
    assert visible_view(page) == ["contact"]


def test_desktop_icons_route(page):
    for label, view in [("Projects", "work"), ("Playground", "about"), ("Résumé.pdf", "resume"), ("Say hello", "contact")]:
        page.click(f".right .icon:has-text('{label}')")
        assert visible_view(page) == [view], label


def test_cta_buttons_and_back_home(page):
    page.click("text=Explore my work")
    assert visible_view(page) == ["work"]
    page.click(".crumbs button")
    assert visible_view(page) == ["overview"]
    page.click(".ctas .btn-ghost")
    assert visible_view(page) == ["contact"]
    page.click('#main-win .l-g')
    assert visible_view(page) == ["overview"]


def test_hashchange_routes(page):
    page.evaluate("location.hash = '#about'")
    page.wait_for_function("!document.querySelector('[data-for=about]').hidden")
    assert visible_view(page) == ["about"]


def test_drag_window_on_desktop(page):
    box = page.locator("#note-win").bounding_box()
    bar = page.locator("#note-win .titlebar .name")
    b = bar.bounding_box()
    page.mouse.move(b["x"] + 5, b["y"] + 5)
    page.mouse.down()
    page.mouse.move(b["x"] - 95, b["y"] - 45, steps=5)
    page.mouse.up()
    after = page.locator("#note-win").bounding_box()
    assert round(after["x"] - box["x"]) == -100
    assert round(after["y"] - box["y"]) == -50
    assert int(page.eval_on_selector("#note-win", "w => w.style.zIndex")) > 10
    assert "front" in page.get_attribute("#note-win", "class")


def test_no_drag_on_phone(open_page):
    page = open_page(width=390, height=844)
    bar = page.locator("#note-win .titlebar .name")
    bar.scroll_into_view_if_needed()
    b = bar.bounding_box()
    page.mouse.move(b["x"] + 5, b["y"] + 5)
    page.mouse.down()
    page.mouse.move(b["x"] - 60, b["y"] - 40, steps=5)
    page.mouse.up()
    assert page.eval_on_selector("#note-win", "w => w.style.transform") == ""
