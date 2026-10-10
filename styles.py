"""Цвета и стили приложения."""

# Палитра (тёмная тема в стиле F1)
BG          = "#15151E"   # основной фон (как у F1 TV)
BG_CARD     = "#1F1F2B"   # фон карточек
BG_ALT      = "#232334"   # чередование строк таблицы
BG_INPUT    = "#2A2A3A"   # фон полей ввода
BG_HOVER    = "#33334A"

ACCENT      = "#E10600"   # фирменный красный F1
ACCENT_HOV  = "#FF1E1E"
SUCCESS     = "#00C853"
INFO        = "#2979FF"
WARNING     = "#FFAB00"

TEXT        = "#FFFFFF"
TEXT_DIM    = "#A0A0B0"
BORDER      = "#33334A"

FONT_DISPLAY = ("Segoe UI Semibold", 19)   # крупный заголовок окна
FONT_H1      = ("Segoe UI Semibold", 16)   # имя пилота
FONT_H2      = ("Segoe UI Semibold", 12)   # заголовки карточек
FONT_H3      = ("Segoe UI Semibold", 10)   # подзаголовки, кнопки
FONT_BODY    = ("Segoe UI", 10)            # основной текст
FONT_SMALL   = ("Segoe UI", 9)             # вторичный текст
FONT_TINY    = ("Segoe UI", 8)             # подписи, счётчики
FONT_NUM     = ("Segoe UI Semibold", 14)   # числовые показатели


def track(text, sp=" "):
    """Разрядка: тонкий пробел между символами — для мелких заглавных подписей.
    Tk не умеет letter-spacing, поэтому вставляем тонкие пробелы вручную."""
    return sp.join(text)


def apply_theme(root):
    from tkinter import ttk

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "F1.Treeview",
        background=BG_CARD,
        foreground=TEXT,
        fieldbackground=BG_CARD,
        borderwidth=0,
        relief="flat",
        lightcolor=BG_CARD,      # убирает рамку вокруг таблицы
        darkcolor=BG_CARD,
        bordercolor=BG_CARD,
        rowheight=32,
        font=FONT_BODY,
    )
    style.configure(
        "F1.Treeview.Heading",
        background=BG_INPUT,
        foreground=TEXT_DIM,
        relief="flat",
        font=("Segoe UI Semibold", 9),
        padding=(8, 10),
    )
    style.map(
        "F1.Treeview.Heading",
        background=[("active", ACCENT)],
        foreground=[("active", "#FFFFFF")],
    )
    style.map(
        "F1.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#FFFFFF")],
    )

    style.configure(
        "F1.TCombobox",
        fieldbackground=BG_INPUT,
        background=BG_INPUT,
        foreground=TEXT,
        arrowcolor=TEXT,
        borderwidth=0,
        padding=6,
    )
    style.map(
        "F1.TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        foreground=[("readonly", TEXT)],
    )

    style.configure(
        "F1.Vertical.TScrollbar",
        background=BG_INPUT,
        troughcolor=BG_CARD,
        bordercolor=BG_CARD,     # без этого clam рисует светлую рамку
        borderwidth=0,
        arrowcolor=TEXT_DIM,
        arrowsize=11,
        gripcount=0,
        width=12,
    )
    style.map(
        "F1.Vertical.TScrollbar",
        background=[("active", ACCENT), ("pressed", ACCENT)],
        arrowcolor=[("active", TEXT)],
    )

    style.configure(
        "F1.Horizontal.TScrollbar",
        background=BG_INPUT,
        troughcolor=BG_CARD,
        bordercolor=BG_CARD,
        borderwidth=0,
        arrowcolor=TEXT_DIM,
        arrowsize=11,
        gripcount=0,
        height=12,
    )
    style.map(
        "F1.Horizontal.TScrollbar",
        background=[("active", ACCENT), ("pressed", ACCENT)],
        arrowcolor=[("active", TEXT)],
    )

    # Выпадающий список комбобокса (иначе остаётся светлым на тёмной теме)
    root.option_add("*TCombobox*Listbox.background", BG_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox.font", FONT_BODY)

    style.configure(
        "F1.TNotebook",
        background=BG,
        borderwidth=0,
    )

    style.configure(
        "F1.TNotebook.Tab",
        background=BG_CARD,
        foreground=TEXT_DIM,
        padding=[20, 10],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )

    style.map(
        "F1.TNotebook.Tab",
        background=[("selected", ACCENT)],
        foreground=[("selected", TEXT)],
    )
