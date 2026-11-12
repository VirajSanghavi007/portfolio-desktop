"""Unit: single behaviours, with the clock and clipboard mocked."""
import pytest

from conftest import visible_view

FAKE_CLIP_OK = "window.__clip=[]; Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__clip.push(t);return Promise.resolve()}}});"
FAKE_CLIP_FAIL = "Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('no'))}});"


@pytest.mark.parametrize("when,bar_date,bar_time,w_time,w_date", [
    ("2026-11-12T09:41:00", "Thu 12 Nov", "9:41 AM", "09:41", "Thursday\nNovember 12"),
    ("2026-11-12T00:05:00", "Thu 12 Nov", "12:05 AM", "00:05", "Thursday\nNovember 12"),
    ("2026-03-01T18:30:00", "Sun 1 Mar", "6:30 PM", "18:30", "Sunday\nMarch 1"),
    ("2026-03-01T12:00:00", "Sun 1 Mar", "12:00 PM", "12:00", "Sunday\nMarch 1"),
])
def test_clock_formats(open_page, when, bar_date, bar_time, w_time, w_date):
    page = open_page(fixed_time=when)
    assert page.inner_text("#bar-date") == bar_date
    assert page.inner_text("#bar-time") == bar_time
    assert page.inner_text("#w-time") == w_time
    assert page.eval_on_selector("#w-date", "e => e.innerHTML") == w_date.replace("\n", "<br>")


@pytest.mark.parametrize("view,crumb", [
    ("about", "About me"), ("work", "Selected work"), ("resume", "Résumé"), ("contact", "Get in touch"), ("overview", "Overview"),
])
def test_sidebar_switches_view(page, view, crumb):
    page.click(f'.side .nav button[data-view="{view}"]')
    assert visible_view(page) == [view]
    assert page.inner_text("#crumb") == crumb
    current = page.eval_on_selector_all(".side .nav button[aria-current]", "bs => bs.map(b => b.dataset.view)")
    assert current == [view]
    assert page.evaluate("location.hash") == ("" if view == "overview" else "#" + view)


def test_unknown_hash_falls_back_to_overview(open_page):
    page = open_page(hash_="#nope")
    assert visible_view(page) == ["overview"]
    assert page.inner_text("#crumb") == "Overview"


def test_hash_opens_view(open_page):
    page = open_page(hash_="#resume")
    assert visible_view(page) == ["resume"]


def test_copy_email_uses_clipboard(open_page):
    page = open_page(init_script=FAKE_CLIP_OK, hash_="#contact")
    page.click("#copy-email")
    page.wait_for_function("window.__clip.length === 1")
    assert page.evaluate("window.__clip") == ["hello@alex.example"]
    assert page.inner_text("#toast") == "Copied hello@alex.example"


def test_copy_email_falls_back_to_selection(open_page):
    page = open_page(init_script=FAKE_CLIP_FAIL, hash_="#contact")
    page.click("#copy-email")
    page.wait_for_function("getSelection().toString().length > 0")
    assert page.evaluate("getSelection().toString()") == "hello@alex.example"
    assert "selected" in page.inner_text("#toast")


def test_form_submit_shows_honest_note(open_page):
    page = open_page(hash_="#contact")
    page.fill("#f-name", "Sam Rivera")
    page.fill("#f-text", "Hi")
    page.click("#msg-form button[type=submit]")
    note = page.inner_text("#form-note")
    assert note.startswith("Thanks, Sam.")
    assert "doesn't send anything" in note
    assert page.evaluate("location.hash") == "#contact"  # no navigation


def test_form_needs_fields(open_page):
    page = open_page(hash_="#contact")
    page.click("#msg-form button[type=submit]")
    assert page.inner_text("#form-note") == ""


def test_music_toast_cycles(page):
    page.click('.dock [data-cmd="music"]')
    first = page.inner_text("#toast")
    page.click('.dock [data-cmd="music"]')
    second = page.inner_text("#toast")
    page.click('.dock [data-cmd="music"]')
    assert first != second
    assert page.inner_text("#toast") == first
    assert page.is_visible("#toast.show")


def test_trash_toast(page):
    page.click('.dock [data-cmd="trash"]')
    assert page.inner_text("#toast").startswith("Trash is empty")


def test_palette_filters(page):
    page.keyboard.press("Control+k")
    assert page.is_visible("#palette")
    assert page.locator("#palette-list li").count() == 10
    page.fill("#palette-input", "EMAIL")
    assert page.locator("#palette-list li span").all_inner_texts() == ["Copy email address"]
    assert "Nothing matches" not in page.inner_text("#palette-list")
    page.fill("#palette-input", "zzz")
    assert page.locator("#palette-list li").count() == 0
    assert "Nothing matches" in page.inner_text("#palette-list")


def test_palette_arrow_keys_wrap(page):
    page.keyboard.press("Control+k")
    sel = lambda: page.eval_on_selector_all("#palette-list li", "ls => ls.findIndex(l => l.getAttribute('aria-selected') === 'true')")
    assert sel() == 0
    page.keyboard.press("ArrowUp")
    assert sel() == 9
    page.keyboard.press("ArrowDown")
    assert sel() == 0
    page.keyboard.press("ArrowDown")
    assert sel() == 1


def test_palette_escape_and_backdrop_close(page):
    page.keyboard.press("Control+k")
    page.keyboard.press("Escape")
    assert page.is_hidden("#palette")
    page.keyboard.press("Control+k")
    page.mouse.click(10, 860)  # backdrop
    assert page.is_hidden("#palette")
    page.keyboard.press("Control+k")
    page.keyboard.press("Control+k")  # toggles closed
    assert page.is_hidden("#palette")
