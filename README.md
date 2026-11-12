# portfolio-desktop

A one-page portfolio laid out like a desktop: a menu bar, a Finder-style window with a sidebar,
desktop icons, a clock widget, a sticky note and a dock. Plain HTML, CSS and JavaScript in a
single file (`index.html`), no build step.

The name "Alex", the projects (Forma, Sonder) and the contact address are placeholders. Swap in
your own text before publishing.

## Features

- Sidebar views (Overview, About, Work, Résumé, Contact), with links that use the URL hash (`#work`)
- Command palette: Ctrl/Cmd + K, arrow keys, Enter, Escape
- Draggable windows on desktop; the layout stacks on phones
- Copy-email button with a select-the-text fallback; the contact form says it does not send yet

## Run

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8000
```

## Tests

Playwright tests run in your installed Chrome (they skip if Chrome cannot start):

```bash
python -m pytest -n 20 tests
```

- `tests/test_smoke.py`: loads at desktop and phone width, no errors, no sideways scroll
- `tests/test_unit.py`: clock format, view switching, clipboard, form, palette
- `tests/test_integration.py`: palette, windows, dock and desktop icons together, dragging
