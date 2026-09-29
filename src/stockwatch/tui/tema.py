"""Tema visual neutro, em tons de cinza (UX_UI.md, "Tema")."""

from textual.theme import Theme

TEMA_NEUTRO = Theme(
    name="stockwatch-neutro",
    primary="#8C8C8C",
    secondary="#6E6E6E",
    accent="#B4B4B4",
    foreground="#DADADA",
    background="#1C1C1C",
    surface="#242424",
    panel="#2E2E2E",
    success="#7FA36B",
    warning="#D4A94E",
    error="#D9534F",
    dark=True,
)
