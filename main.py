import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

import db
from news import NEWS
from styles import (apply_theme, track, BG, BG_CARD, BG_ALT, BG_INPUT, BG_HOVER,
                    BORDER, ACCENT, SUCCESS, INFO, WARNING, TEXT, TEXT_DIM,
                    FONT_DISPLAY, FONT_H1, FONT_H2, FONT_H3, FONT_BODY,
                    FONT_SMALL, FONT_TINY, FONT_NUM)


TEAM_COLORS = {
    "red bull racing": "#3671C6", "mercedes": "#00D2BE", "ferrari": "#E10600",
    "mclaren": "#FF8000", "aston martin": "#229971", "alpine": "#FF87BC",
    "williams": "#64C4FF", "haas": "#9BA3A8", "sauber": "#52E252",
    "racing bulls": "#6692FF", "alphatauri": "#6692FF",
}
FALLBACK_COLORS = ("#7F8CFF", "#4ECDC4", "#F7B32B", "#E8743B", "#9B7EDE", "#3DA5D9")


def lighten(hex_color, amount=0.18):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    f = lambda v: min(255, int(v + (255 - v) * amount))
    return f"#{f(r):02X}{f(g):02X}{f(b):02X}"


def darken(hex_color, amount=0.15):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    f = lambda v: max(0, int(v * (1 - amount)))
    return f"#{f(r):02X}{f(g):02X}{f(b):02X}"


def team_color(team):
    key = (team or "").strip().lower()
    if key in TEAM_COLORS:
        return TEAM_COLORS[key]
    return FALLBACK_COLORS[sum(map(ord, key)) % len(FALLBACK_COLORS)]


def initials(name):
    parts = [p for p in (name or "").split() if p]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else \
        (parts[0][:2].upper() if parts else "?")


def _placeholder(box, text, accent):
    im = Image.new("RGB", box, BG_INPUT)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, box[0] - 1, box[1] - 1], outline=BORDER)
    d.rectangle([0, box[1] - 3, box[0], box[1]], fill=accent)
    try:
        font = ImageFont.truetype("seguisb.ttf", int(box[1] * 0.28))
    except Exception:
        font = ImageFont.load_default()
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    d.text(((box[0] - (x1 - x0)) / 2 - x0, (box[1] - (y1 - y0)) / 2 - y0),
           text, font=font, fill=TEXT_DIM)
    return ImageTk.PhotoImage(im)


def img_fit(path, box, text="?", accent=ACCENT):
    box = (max(1, box[0]), max(1, box[1]))
    im = None
    if path and os.path.exists(path):
        try:
            im = Image.open(path).convert("RGB")
        except Exception:
            im = None
    if im is None:
        return _placeholder(box, text, accent)
    im.thumbnail(box, Image.LANCZOS)
    canvas = Image.new("RGB", box, BG_INPUT)
    canvas.paste(im, ((box[0] - im.width) // 2, (box[1] - im.height) // 2))
    return ImageTk.PhotoImage(canvas)


def btn(p, t, cmd, c=ACCENT, w=None):
    kw = {"width": w} if w else {}
    b = tk.Button(p, text=t, command=cmd, bg=c, fg="white", relief="flat",
                  bd=0, padx=14, pady=7, cursor="hand2", font=FONT_H3,
                  activebackground=lighten(c), activeforeground="white", **kw)
    b.bind("<Enter>", lambda e: b.config(bg=lighten(c)))
    b.bind("<Leave>", lambda e: b.config(bg=c))
    b.bind("<ButtonPress-1>", lambda e: b.config(bg=darken(c)))
    b.bind("<ButtonRelease-1>", lambda e: b.config(bg=lighten(c)))
    return b


def entry(p, var=None):
    kw = {"textvariable": var} if var else {}
    return tk.Entry(p, bg=BG_INPUT, fg=TEXT, insertbackground=TEXT, relief="flat",
                    bd=0, font=FONT_BODY, highlightthickness=1,
                    highlightbackground=BORDER, **kw)


def card(p, **pack_kw):
    f = tk.Frame(p, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
    f.pack(**pack_kw)
    return f


def card_title(p, text, right=None):
    h = tk.Frame(p, bg=BG_CARD)
    h.pack(fill="x", padx=14, pady=(12, 8))
    tk.Label(h, text=text, bg=BG_CARD, fg=TEXT, font=FONT_H2).pack(side="left")
    if right is not None:
        right.pack(side="right")
    return h



DIGITS = set("0123456789")
TEXT_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                 "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                 " -'.")

LIMITS = {"name": 40, "team": 30, "country": 30, "number": 2, "points": 5,
          "search": 40}


def only_text(limit):
    return lambda s: len(s) <= limit and all(c in TEXT_CHARS for c in s)


def only_digits(limit):
    return lambda s: len(s) <= limit and all(c in DIGITS for c in s)


def only_search(s):
    return len(s) <= LIMITS["search"] and all(
        c in TEXT_CHARS or c in DIGITS for c in s)


def clean(s):
    return " ".join(s.split())




class Field(tk.Frame):

    def __init__(self, parent, label, limit, check, bg=BG):
        super().__init__(parent, bg=bg)
        self.limit = limit

        top = tk.Frame(self, bg=bg)
        top.pack(fill="x")
        tk.Label(top, text=track(label.upper()), bg=bg, fg=TEXT_DIM,
                 font=FONT_TINY).pack(side="left")
        self.count_lbl = tk.Label(top, text=f"0/{limit}", bg=bg, fg=TEXT_DIM,
                                  font=FONT_TINY)
        self.count_lbl.pack(side="right")

        self.var = tk.StringVar()
        self.var.trace_add("write", lambda *a: self._count())
        self.entry = entry(self, self.var)
        self.entry.configure(validate="key",
                             validatecommand=(self.register(check), "%P"))
        self.entry.bind("<FocusIn>", lambda e: self.entry.config(highlightbackground=INFO))
        self.entry.bind("<FocusOut>", lambda e: self.entry.config(
            highlightbackground=ACCENT if self.msg.cget("text") else BORDER))
        self.entry.pack(fill="x", ipady=6, pady=(2, 0))

        self.msg = tk.Label(self, text="", bg=bg, fg=ACCENT,
                            font=FONT_TINY, anchor="w", height=1)
        self.msg.pack(fill="x")

    def _count(self):
        n = len(self.var.get())
        self.count_lbl.config(text=f"{n}/{self.limit}",
                              fg=ACCENT if n >= self.limit * 0.9 else TEXT_DIM)

    def get(self):
        return clean(self.var.get())

    def set(self, v):
        self.var.set("" if v is None else str(v))

    def error(self, text=""):
        self.msg.config(text=text)
        self.entry.config(highlightbackground=ACCENT if text else BORDER)

    def clear_error(self):
        self.error()

    def focus(self):
        self.entry.focus_set()
        self.entry.icursor("end")


class Dialog(tk.Toplevel):
    F = [("Имя", "name", "text"), ("Команда", "team", "text"),
         ("Номер", "number", "digits"), ("Страна", "country", "text"),
         ("Очки", "points", "digits")]

    def __init__(self, parent, title, save, d=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.save_cb = save
        self.img_path = d["image_path"] if d and d["image_path"] else ""
        self.name = (d["name"] if d else "") or ""

        tk.Frame(self, bg=ACCENT, height=4).pack(fill="x")
        tk.Label(self, text=title, bg=BG, fg=TEXT,
                 font=FONT_H1).pack(pady=(14, 2))
        tk.Label(self, text="Заполните карточку пилота", bg=BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack()

        self.fields = {}
        for lbl, key, kind in self.F:
            limit = LIMITS[key]
            check = only_digits(limit) if kind == "digits" else only_text(limit)
            fld = Field(self, lbl, limit, check)
            fld.pack(fill="x", padx=24, pady=(7, 0))
            if d and d[key] is not None:
                fld.set(d[key])
            self.fields[key] = fld

        tk.Label(self, text=track("ФОТО"), bg=BG, fg=TEXT_DIM,
                 font=FONT_TINY).pack(anchor="w", padx=24, pady=(10, 0))
        self.pv = tk.Label(self, bg=BG_INPUT, bd=0)
        self.pv.pack(padx=24, pady=(4, 0), fill="x")

        row = tk.Frame(self, bg=BG)
        row.pack(pady=8)
        btn(row, "Выбрать файл", self.pick, INFO).pack(side="left", padx=4)
        btn(row, "Убрать", lambda: self.set_img(""), BG_HOVER).pack(side="left", padx=4)

        btn(self, "Сохранить", self.ok, SUCCESS).pack(fill="x", padx=24, pady=(4, 20))

        self.bind("<Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy).
        self.resizable(False, False)
        self.update_idletasks()
        self.grab_set()
        self.fields["name"].focus()
        self.refresh()

    def set_img(self, p):
        self.img_path = p
        self.refresh()

    def refresh(self):
        i = img_fit(self.img_path, (390, 130), initials(self.name) or "?", INFO)
        self.pv.config(image=i)
        self.pv.image = i

    def pick(self):
        p = filedialog.askopenfilename(
            parent=self, filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if p:
            self.set_img(p)

    def ok(self):
        for f in self.fields.values():
            f.clear_error()

        name = self.fields["name"].get()
        team = self.fields["team"].get()
        country = self.fields["country"].get()
        num_s = self.fields["number"].get()
        pts_s = self.fields["points"].get()

        if len(name) < 2:
            return self._bad("name", "Имя: минимум 2 символа")
        if len(team) < 2:
            return self._bad("team", "Команда: минимум 2 символа")
        if num_s and not 1 <= int(num_s) <= 99:
            return self._bad("number", "Номер: от 1 до 99")
        if pts_s and int(pts_s) > 99999:
            return self._bad("points", "Очки: максимум 99999")

        self.save_cb(name, team, int(num_s) if num_s else 0, country,
                     int(pts_s) if pts_s else 0, self.img_path)
        self.destroy()

    def _bad(self, key, msg):
        self.fields[key].error(msg)
        self.fields[key].focus()
        return "break"



class App:
    COLS = [("pos", "#", 46), ("name", "Пилот", 190), ("team", "Команда", 175),
            ("number", "№", 56), ("country", "Страна", 150), ("points", "Очки", 90)]

    def __init__(self, root):
        self.root = root
        root.title("F1 Dashboard — база пилотов")
        root.geometry("1280x820")
        root.minsize(1060, 680)
        root.configure(bg=BG)

        db.init_db()
        self.sid = None
        self.sort = ("points", True)
        self._search_job = None
        self._fit_job = None

        apply_theme(root)
        self._header()
        self._body()
        self._keys()
        self.clear_preview()
        self.refresh()
        self.root.update_idletasks()
        self._fit_scrollbars()


    def _header(self):
        h = tk.Frame(self.root, bg=BG_CARD, height=72)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Frame(h, bg=ACCENT, width=5).pack(side="left", fill="y")

        title = tk.Frame(h, bg=BG_CARD)
        title.pack(side="left", padx=18)
        tk.Label(title, text=track("F1 DASHBOARD"), bg=BG_CARD, fg=TEXT,
                 font=FONT_DISPLAY).pack(anchor="w")
        tk.Label(title, text="база пилотов и статистика", bg=BG_CARD,
                 fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        self.stats = tk.Frame(h, bg=BG_CARD)
        self.stats.pack(side="right", padx=22)

    def _render_stats(self, stats=None):
        for c in self.stats.winfo_children():
            c.destroy()
        drivers, teams, points = stats or db.get_stats()
        for i, (value, caption) in enumerate(((drivers, track("пилотов")),
                                              (teams, track("команд")),
                                              (points, track("очков")))):
            if i:
                tk.Frame(self.stats, bg=BORDER, width=1,
                         height=28).pack(side="left", padx=16)
            cell = tk.Frame(self.stats, bg=BG_CARD)
            cell.pack(side="left")
            tk.Label(cell, text=str(value), bg=BG_CARD, fg=TEXT,
                     font=("Segoe UI Semibold", 16)).pack()
            tk.Label(cell, text=caption, bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_TINY).pack()

    def _body(self):
        b = tk.Frame(self.root, bg=BG)
        b.pack(fill="both", expand=True, padx=14, pady=14)

        left = tk.Frame(b, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self._toolbar(left)
        self._table(left)

        right = tk.Frame(b, bg=BG, width=390)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._preview(right)
        self._news(right)

    def _toolbar(self, p):
        f = card(p, fill="x", pady=(0, 12))
        r = tk.Frame(f, bg=BG_CARD)
        r.pack(fill="x", padx=12, pady=11)

        tk.Label(r, text=track("поиск"), bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_TINY).pack(side="left")

        self.var_s = tk.StringVar()
        self.var_s.trace_add("write", self._on_search)
        self.search = entry(r, self.var_s)
        self.search.configure(validate="key",
                              validatecommand=(self.root.register(only_search), "%P"))
        self.search.bind("<FocusIn>", lambda e: self.search.config(highlightbackground=INFO))
        self.search.bind("<FocusOut>", lambda e: self.search.config(highlightbackground=BORDER))
        self.search.pack(side="left", fill="x", expand=True, ipady=6, padx=8)

        self.var_t = tk.StringVar(value="Все команды")
        self.cmb = ttk.Combobox(r, textvariable=self.var_t, state="readonly",
                                style="F1.TCombobox", width=20,
                                values=db.get_teams())
        self.cmb.pack(side="left", padx=(0, 8))
        self.cmb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        btn(r, "Сброс", self.reset, BG_HOVER).pack(side="left")

    def _table(self, p):
        f = card(p, fill="both", expand=True)
        self.cnt = tk.Label(f, text="", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL)
        card_title(f, "Пилоты", self.cnt)

        holder = tk.Frame(f, bg=BG_CARD)
        holder.pack(fill="both", expand=True, padx=14)
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            holder, columns=[c[0] for c in self.COLS], show="headings",
            style="F1.Treeview", selectmode="browse")
        for key, title, width in self.COLS:
            self.tree.heading(key, text=track(title),
                              command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=width, anchor="center",
                             stretch=(key == "name"))
        self.tree.tag_configure("odd", background=BG_ALT)
        self.tree.tag_configure("even", background=BG_CARD)
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(holder, style="F1.Vertical.TScrollbar",
                            orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(holder, style="F1.Horizontal.TScrollbar",
                            orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.vsb, self.hsb = vsb, hsb
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.bind("<<TreeviewSelect>>", self.select)
        self.tree.bind("<Double-1>", lambda e: self.edit())
        self.tree.bind("<Configure>",
                       lambda e: self.root.after_idle(self._schedule_fit),
                       add="+")

        self.empty = tk.Label(holder, bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY,
                              text="Ничего не найдено\n\nПопробуйте изменить поиск "
                                   "или сбросить фильтры")
        self.empty.place(relx=0.5, rely=0.5, anchor="center")

        bar = tk.Frame(f, bg=BG_CARD)
        bar.pack(fill="x", padx=14, pady=12)
        btn(bar, "Добавить", self.add, SUCCESS).pack(side="left")
        btn(bar, "Изменить", self.edit, INFO).pack(side="left", padx=8)
        btn(bar, "Удалить", self.delete, ACCENT).pack(side="left")
        hints = "   ·   ".join(track(t) for t in
                               ("двойной клик — изменить", "del — удалить",
                                "ctrl+f — поиск"))
        tk.Label(bar, text=hints, bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_TINY).pack(side="right")

    def _preview(self, p):
        f = card(p, fill="x", pady=(0, 12))
        card_title(f, "Карточка пилота")

        self.accent = tk.Frame(f, bg=BG_HOVER, height=3)
        self.accent.pack(fill="x")

        self.pv = tk.Label(f, bg=BG_INPUT, bd=0)
        self.pv.pack(fill="x", padx=14, pady=(0, 0))

        info = tk.Frame(f, bg=BG_CARD)
        info.pack(fill="x", padx=14, pady=(12, 14))

        self.nm = tk.Label(info, text="—", bg=BG_CARD, fg=TEXT, font=FONT_H1,
                           anchor="w")
        self.nm.pack(fill="x")
        self.tm = tk.Label(info, text="Выберите пилота в таблице", bg=BG_CARD,
                           fg=TEXT_DIM, font=FONT_BODY, anchor="w")
        self.tm.pack(fill="x", pady=(3, 10))

        tk.Frame(info, bg=BORDER, height=1).pack(fill="x", pady=(0, 12))

        row = tk.Frame(info, bg=BG_CARD)
        row.pack(fill="x")
        self.stat_num = self._stat(row, "номер", "—")
        self.stat_pts = self._stat(row, "очки", "—", color=TEXT)
        self.stat_country = self._stat(row, "страна", "—")

    @staticmethod
    def _stat(parent, caption, value, color=TEXT_DIM):
        cell = tk.Frame(parent, bg=BG_CARD)
        cell.pack(side="left", fill="x", expand=True)
        tk.Label(cell, text=track(caption), bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_TINY).pack(anchor="w")
        lbl = tk.Label(cell, text=value, bg=BG_CARD, fg=color,
                       font=FONT_NUM, anchor="w")
        lbl.pack(anchor="w", pady=(2, 0))
        return lbl

    def _news(self, p):
        f = card(p, fill="both", expand=True)
        card_title(f, "Новости")

        wrap = tk.Frame(f, bg=BG_CARD)
        wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        # grid, а не pack: при pack канва забирала всю ширину и полоса схлопывалась
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(wrap, bg=BG_CARD, highlightthickness=0,
                                borderwidth=0)
        vsb = ttk.Scrollbar(wrap, style="F1.Vertical.TScrollbar",
                            orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns", padx=(6, 0))

        inner = tk.Frame(self.canvas, bg=BG_CARD)
        self._news_inner = inner
        self._news_win = self.canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(
                             self._news_win, width=e.width))

        for w in (self.canvas, inner):
            w.bind("<MouseWheel>", self._news_scroll)
            w.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
            w.bind("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

        for item in NEWS:
            self._news_card(inner, item)

    def _news_scroll(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")
        return "break"

    def _news_card(self, parent, item):
        w = tk.Frame(parent, bg=BG_INPUT, highlightthickness=1,
                     highlightbackground=BG_INPUT)
        w.pack(fill="x", pady=(0, 10))
        tint = []

        top = tk.Frame(w, bg=BG_INPUT)
        top.pack(fill="x", padx=10, pady=(9, 0))
        tint.append(top)

        tag_colors = {"Гонка": ACCENT, "Техника": INFO, "Трансферы": SUCCESS,
                      "Регламент": WARNING, "Интервью": "#9B7EDE",
                      "Команды": "#4ECDC4"}
        tk.Label(top, text=f" {track(item['tag'])} ",
                 bg=tag_colors.get(item["tag"], ACCENT),
                 fg="white", font=("Segoe UI Semibold", 8)).pack(side="left")
        date = tk.Label(top, text=item.get("date", ""), bg=BG_INPUT, fg=TEXT_DIM,
                        font=FONT_TINY)
        date.pack(side="right")
        tint.append(date)

        title = tk.Label(w, text=item["title"], bg=BG_INPUT, fg=TEXT,
                         wraplength=310, font=FONT_H3,
                         justify="left", anchor="w")
        title.pack(fill="x", padx=10, pady=(7, 0))
        tint.append(title)

        body = tk.Label(w, text=item["text"], bg=BG_INPUT, fg=TEXT_DIM,
                        wraplength=310, font=FONT_SMALL, justify="left",
                        anchor="w")
        body.pack(fill="x", padx=10, pady=(4, 10))
        tint.append(body)

        for target in (w, top, title, body, date):
            target.bind("<MouseWheel>", self._news_scroll)
            target.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
            target.bind("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

        def tint_all(color):
            for target in tint:
                target.config(bg=color)

        w.bind("<Enter>", lambda e: (tint_all(lighten(BG_INPUT)),
                                     w.config(highlightbackground=BORDER)))
        w.bind("<Leave>", lambda e: (tint_all(BG_INPUT),
                                     w.config(highlightbackground=BG_INPUT)))


    def _keys(self):
        r = self.root
        r.bind("<Control-f>", lambda e: (self.search.focus_set(),
                                         self.search.selection_range(0, "end")))
        r.bind("<Control-F>", lambda e: (self.search.focus_set(),
                                         self.search.selection_range(0, "end")))
        r.bind("<Control-n>", lambda e: self.add())
        r.bind("<Delete>", lambda e: self.delete())
        r.bind("<Escape>", lambda e: self.reset())
        self.tree.bind("<Delete>", lambda e: self.delete())
        self.tree.bind("<Return>", lambda e: self.edit())


    def _on_search(self, *_):
        if self._search_job:
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(200, self.refresh)

    def sort_by(self, key):
        self.sort = (key, not self.sort[1]) if self.sort[0] == key else (key, True)
        arrow = " ▼" if self.sort[1] else " ▲"
        for k, title, _ in self.COLS:
            self.tree.heading(k, text=track(title) + (arrow if k == key else ""))
        self.refresh()

    def _fit_scrollbars(self):
        self._fit_job = None
        need_v = bool(self.tree.get_children()) and self.tree.yview()[1] < 0.999
        need_h = self.tree.xview()[1] < 0.999
        self._toggle_bar(self.vsb, need_v)
        self._toggle_bar(self.hsb, need_h)

    def _schedule_fit(self):
        if self._fit_job:
            self.root.after_cancel(self._fit_job)
        self._fit_job = self.root.after(60, self._fit_scrollbars)

    @staticmethod
    def _toggle_bar(bar, show):
        if show and not bar.winfo_ismapped():
            bar.grid()
        elif not show and bar.winfo_ismapped():
            bar.grid_remove()

    def refresh(self, *_):
        self._search_job = None
        stats = db.get_stats()
        self._render_stats(stats)

        rows = db.fetch_all(self.var_s.get().strip(), self.var_t.get())
        key, desc = self.sort
        rows = sorted(rows,
                      key=lambda d: (d[key] is None, "" if d[key] is None else d[key]),
                      reverse=desc)

        selected = self.sid
        for i in self.tree.get_children():
            self.tree.delete(i)

        for pos, d in enumerate(rows, start=1):
            self.tree.insert(
                "", "end", iid=str(d["id"]),
                values=(pos, d["name"], d["team"], d["number"] or "—",
                        d["country"] or "—", d["points"] or 0),
                tags=("odd",) if pos % 2 == 0 else ("even",))

        teams = db.get_teams()
        self.cmb["values"] = teams
        if self.var_t.get() not in teams:
            self.var_t.set("Все команды")

        self.cnt.config(text=f"{len(rows)} из {stats[0]}")
        if rows:
            self.empty.place_forget()
        else:
            self.empty.place(relx=0.5, rely=0.5, anchor="center")

        if selected and self.tree.exists(str(selected)):
            self.tree.selection_set(str(selected))
            self.tree.see(str(selected))
        elif selected:
            # строка исчезла из выборки — не оставляем «призрак» выделения
            self.sid = None
            self.clear_preview()
        elif not rows:
            self.clear_preview()

        self.root.after_idle(self._schedule_fit)

    def reset(self):
        if self._search_job:
            self.root.after_cancel(self._search_job)
            self._search_job = None
        self.var_s.set("")
        self.var_t.set("Все команды")
        self.refresh()

    # это для выделения надо

    def select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        self.sid = int(sel[0])
        d = db.get_driver(self.sid)
        if not d:
            return

        color = team_color(d["team"])
        self.accent.config(bg=color)
        photo = img_fit(d["image_path"], (360, 190), initials(d["name"]), color)
        self.pv.config(image=photo)
        self.pv.image = photo

        self.nm.config(text=d["name"])
        self.tm.config(text=f"{d['team']}", fg=color)
        self.stat_num.config(text=str(d["number"] or "—"))
        self.stat_pts.config(text=str(d["points"] or 0))
        self.stat_country.config(text=d["country"] or "—")

    def clear_preview(self):
        photo = img_fit(None, (360, 190), "?", BG_HOVER)
        self.pv.config(image=photo)
        self.pv.image = photo
        self.accent.config(bg=BG_HOVER)
        self.nm.config(text="—", fg=TEXT)
        self.tm.config(text="Выберите пилота в таблице", fg=TEXT_DIM)
        self.stat_num.config(text="—")
        self.stat_pts.config(text="—")
        self.stat_country.config(text="—")


    def add(self):
        Dialog(self.root, "Новый пилот", self._save_add)

    def _save_add(self, *args):
        db.add_driver(*args)
        self.refresh()
        ids = self.tree.get_children()
        if ids:
            newest = max(ids, key=int)
            self.tree.selection_set(newest)
            self.tree.see(newest)

    def edit(self):
        if not self.sid:
            return messagebox.showwarning("F1", "Сначала выберите пилота в таблице",
                                          parent=self.root)
        d = db.get_driver(self.sid)
        if not d:
            return messagebox.showwarning("F1", "Пилот больше не существует",
                                          parent=self.root)
        Dialog(self.root, "Редактирование", self._save_edit, d)

    def _save_edit(self, *args):
        db.update_driver(self.sid, *args)
        self.refresh()
        self.tree.selection_set(str(self.sid))
        self.select()

    def delete(self):
        if not self.sid:
            return messagebox.showwarning("F1", "Сначала выберите пилота в таблице",
                                          parent=self.root)
        d = db.get_driver(self.sid)
        if not d:
            return
        if not messagebox.askyesno(
                "Удаление", f"Удалить пилота «{d['name']}»?\nДействие необратимо.",
                parent=self.root):
            return
        db.delete_driver(self.sid)
        self.sid = None
        self.clear_preview()
        self.refresh()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
