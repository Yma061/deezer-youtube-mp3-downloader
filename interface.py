import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import sys
import os
import time
import json


def _app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()


# ── Thèmes ────────────────────────────────────────────────────────────────────
_THEMES = {
    "dark":  {"BG": "#1e1e2e", "BG2": "#2a2a3d", "FG": "#f1f5f9", "FG2": "#94a3b8",
              "LOG_BG": "#0f0f1a", "LOG_FG": "#a0f0a0"},
    "light": {"BG": "#f0f0f8", "BG2": "#dcdcec", "FG": "#1a1a2e", "FG2": "#555577",
              "LOG_BG": "#e8ffe8", "LOG_FG": "#1a5c1a"},
}
_current_theme = "dark"
BG = _THEMES["dark"]["BG"];  BG2 = _THEMES["dark"]["BG2"]
FG = _THEMES["dark"]["FG"];  FG2 = _THEMES["dark"]["FG2"]
LOG_BG = _THEMES["dark"]["LOG_BG"]; LOG_FG = _THEMES["dark"]["LOG_FG"]

ACCENT1 = "#7c3aed"
ACCENT2 = "#0ea5e9"
ACCENT3 = "#10b981"
FONT       = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_H2    = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 9)


def _apply_theme(name):
    global BG, BG2, FG, FG2, LOG_BG, LOG_FG, _current_theme
    _current_theme = name
    t = _THEMES[name]
    BG = t["BG"]; BG2 = t["BG2"]; FG = t["FG"]; FG2 = t["FG2"]
    LOG_BG = t["LOG_BG"]; LOG_FG = t["LOG_FG"]


def _lighten(hex_color, amount=30):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = min(r+amount, 255), min(g+amount, 255), min(b+amount, 255)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Historique ────────────────────────────────────────────────────────────────
def _history_path():
    return os.path.join(_app_dir(), "history.json")


def load_history():
    try:
        with open(_history_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(entry):
    history = load_history()
    history.insert(0, entry)
    history = history[:10]
    with open(_history_path(), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ── Scrollable ────────────────────────────────────────────────────────────────
def make_scrollable(parent, padx=36, pady=20):
    canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    body = tk.Frame(canvas, bg=BG, padx=padx, pady=pady)
    win = canvas.create_window((0, 0), window=body, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    body.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return body


# ── Redirection stdout ────────────────────────────────────────────────────────
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")
        self.widget.update()

    def flush(self):
        pass


# ── Application ───────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Playlist Manager")
        self.geometry("1050x680")
        self.resizable(True, True)
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._page  = "home"
        self._mode  = None
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.show_home()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def toggle_theme(self):
        new = "light" if _current_theme == "dark" else "dark"
        _apply_theme(new)
        self.configure(bg=BG)
        self.container.configure(bg=BG)
        if   self._page == "home":              self.show_home()
        elif self._page == "streaming_select":  self.show_streaming_select()
        elif self._page == "detail":            self.show_detail(self._mode)
        elif self._page == "json_help":         self.show_json_help(self._mode)
        elif self._page == "deezer_help":       self.show_deezer_id_help(self._mode)

    def show_home(self):
        self._page = "home"; self.clear()
        HomePage(self.container, self)

    def show_detail(self, mode):
        self._page = "detail"; self._mode = mode; self.clear()
        DetailPage(self.container, self, mode)

    def show_json_help(self, back_mode):
        self._page = "json_help"; self._mode = back_mode; self.clear()
        JsonHelpPage(self.container, self, back_mode)

    def show_streaming_select(self):
        self._page = "streaming_select"; self.clear()
        StreamingSelectPage(self.container, self)

    def show_deezer_id_help(self, back_mode):
        self._page = "deezer_help"; self._mode = back_mode; self.clear()
        DeezerIdHelpPage(self.container, self, back_mode)


# ── Page d'accueil ────────────────────────────────────────────────────────────
class HomePage(tk.Frame):
    CARDS = [
        {"mode": "streaming", "color": ACCENT1, "icon": "🎵",
         "title": "Streaming  →  YouTube",
         "desc":  "Importe une playlist Deezer ou Spotify\ndans ta bibliothèque YouTube"},
        {"mode": "youtube", "color": ACCENT2, "icon": "▶",
         "title": "YouTube  →  MP3",
         "desc":  "Télécharge une playlist YouTube\net convertit chaque vidéo en MP3"},
        {"mode": "excel",   "color": ACCENT3, "icon": "📊",
         "title": "Excel  →  MP3",
         "desc":  "Télécharge les musiques dans\nl'ordre défini dans un fichier Excel"},
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app = app
        self._build()

    def _build(self):
        # ── Barre du haut ────────────────────────────────────────────────────
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(12, 0))
        icon = "☀" if _current_theme == "dark" else "🌙"
        tk.Button(top, text=f"{icon} Thème", font=FONT_SMALL,
                  bg=BG2, fg=FG, bd=0, cursor="hand2",
                  activebackground=_lighten(BG2), activeforeground=FG,
                  padx=10, pady=4, command=self.app.toggle_theme
                  ).pack(side="right")

        tk.Label(self, text="Playlist Manager", font=FONT_TITLE,
                 bg=BG, fg=FG).pack(pady=(20, 4))
        tk.Label(self, text="Choisissez une action", font=FONT,
                 bg=BG, fg=FG2).pack(pady=(0, 28))

        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack()
        for card in self.CARDS:
            self._make_card(cards_frame, card)

        # ── Historique ───────────────────────────────────────────────────────
        history = load_history()
        if history:
            tk.Frame(self, bg=FG2, height=1).pack(fill="x", padx=40, pady=(28, 0))
            tk.Label(self, text="Téléchargements récents", font=FONT_H2,
                     bg=BG, fg=FG2).pack(pady=(10, 4))
            for entry in history[:5]:
                mode_colors = {"deezer": ACCENT1, "spotify": ACCENT_SPOTIFY, "soundcloud": ACCENT_SOUNDCLOUD, "applemusic": ACCENT_APPLE, "youtube": ACCENT2, "excel": ACCENT3}
                color = mode_colors.get(entry.get("mode", ""), FG2)
                row = tk.Frame(self, bg=BG)
                row.pack(fill="x", padx=60, pady=2)
                tk.Label(row, text="●", font=FONT_SMALL, bg=BG, fg=color,
                         width=2).pack(side="left")
                name = entry.get("name", "—")
                count = entry.get("count", "?")
                date = entry.get("date", "")
                path = entry.get("path", "")
                tk.Label(row, text=f"{name}  ({count} titres)  —  {date}",
                         font=FONT_SMALL, bg=BG, fg=FG2).pack(side="left")
                if path and os.path.isdir(path):
                    tk.Button(row, text="📂", font=FONT_SMALL, bg=BG, fg=FG2,
                              bd=0, cursor="hand2",
                              command=lambda p=path: os.startfile(p)
                              ).pack(side="right")

    def _make_card(self, parent, card):
        color = card["color"]
        frame = tk.Frame(parent, bg=color, cursor="hand2", padx=24, pady=20, bd=0)
        frame.pack(side="left", padx=14)
        tk.Label(frame, text=card["icon"], font=("Segoe UI", 28), bg=color, fg="white").pack()
        tk.Label(frame, text=card["title"], font=FONT_H2,   bg=color, fg="white").pack(pady=(6,4))
        tk.Label(frame, text=card["desc"],  font=FONT_SMALL, bg=color, fg="white",
                 justify="center").pack()
        def _on_click(e, m=card["mode"]):
            if m == "streaming":
                self.app.show_streaming_select()
            else:
                self.app.show_detail(m)
        for w in [frame] + frame.winfo_children():
            w.bind("<Button-1>", _on_click)

        def on_enter(e, f=frame, c=color):
            f.configure(bg=_lighten(c))
            for w in f.winfo_children(): w.configure(bg=_lighten(c))
        def on_leave(e, f=frame, c=color):
            f.configure(bg=c)
            for w in f.winfo_children(): w.configure(bg=c)
        frame.bind("<Enter>", on_enter); frame.bind("<Leave>", on_leave)
        for w in frame.winfo_children():
            w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave)


# ── Page sélection plateforme streaming ──────────────────────────────────────
ACCENT_SPOTIFY     = "#1db954"
ACCENT_SOUNDCLOUD  = "#ff5500"
ACCENT_APPLE       = "#fc3c44"

class StreamingSelectPage(tk.Frame):
    CARDS = [
        {"mode": "deezer",  "color": ACCENT1,       "icon": "🎵",
         "title": "Deezer  →  YouTube",
         "desc":  "Importe une playlist Deezer\ndans ta bibliothèque YouTube"},
        {"mode": "spotify",     "color": ACCENT_SPOTIFY,    "icon": "🟢",
         "title": "Spotify  →  YouTube",
         "desc":  "Importe une playlist Spotify\ndans ta bibliothèque YouTube"},
        {"mode": "soundcloud", "color": ACCENT_SOUNDCLOUD, "icon": "☁",
         "title": "SoundCloud  →  YouTube",
         "desc":  "Importe une playlist SoundCloud\ndans ta bibliothèque YouTube"},
        {"mode": "applemusic", "color": ACCENT_APPLE,      "icon": "🍎",
         "title": "Apple Music  →  YouTube",
         "desc":  "Importe une playlist Apple Music\ndans ta bibliothèque YouTube"},
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=ACCENT1, pady=16)
        header.pack(fill="x")
        tk.Button(header, text="← Retour", font=FONT_SMALL,
                  bg=ACCENT1, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(ACCENT1), activeforeground="white",
                  command=self.app.show_home).pack(side="left", padx=16)
        tk.Label(header, text="Streaming  →  YouTube", font=FONT_H2,
                 bg=ACCENT1, fg="white").pack(side="left", padx=8)
        icon = "☀" if _current_theme == "dark" else "🌙"
        tk.Button(header, text=icon, font=FONT_SMALL,
                  bg=ACCENT1, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(ACCENT1),
                  command=self.app.toggle_theme).pack(side="right", padx=16)

        tk.Label(self, text="Choisissez votre plateforme", font=FONT,
                 bg=BG, fg=FG2).pack(pady=(40, 28))

        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack()
        for card in self.CARDS:
            self._make_card(cards_frame, card)

    def _make_card(self, parent, card):
        color = card["color"]
        frame = tk.Frame(parent, bg=color, cursor="hand2", padx=26, pady=20, bd=0)
        frame.pack(side="left", padx=14)
        tk.Label(frame, text=card["icon"], font=("Segoe UI", 32), bg=color, fg="white").pack()
        tk.Label(frame, text=card["title"], font=FONT_H2,    bg=color, fg="white").pack(pady=(8, 4))
        tk.Label(frame, text=card["desc"],  font=FONT_SMALL, bg=color, fg="white",
                 justify="center").pack()
        for w in [frame] + frame.winfo_children():
            w.bind("<Button-1>", lambda e, m=card["mode"]: self.app.show_detail(m))

        def on_enter(e, f=frame, c=color):
            f.configure(bg=_lighten(c))
            for w in f.winfo_children(): w.configure(bg=_lighten(c))
        def on_leave(e, f=frame, c=color):
            f.configure(bg=c)
            for w in f.winfo_children(): w.configure(bg=c)
        frame.bind("<Enter>", on_enter); frame.bind("<Leave>", on_leave)
        for w in frame.winfo_children():
            w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave)


# ── Config des modes ──────────────────────────────────────────────────────────
MODES = {
    "deezer": {
        "color": ACCENT1, "title": "Deezer  →  YouTube",
        "what": ("Récupère tous les titres d'une playlist Deezer et les importe "
                 "automatiquement dans une nouvelle playlist YouTube sur ton compte Google."),
        "needs": [
            "L'ID de ta playlist Deezer  (ex : 14838804003)",
            "Une connexion internet",
            "Au premier lancement : connexion à ton compte Google dans le navigateur",
            "✅  Connexion mémorisée — tu n'auras à te connecter qu'une seule fois.",
            "⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.",
            "⚠  Pour 190 titres (~28 500 unités), l'import devra être étalé sur 3 jours.",
            "✅  Reprise automatique : relancez avec le même ID, l'import reprend là où il s'est arrêté.",
        ],
        "inputs": [
            {"label": "ID de la playlist Deezer", "key": "deezer_id",
             "placeholder": "ex : 14838804003"},
        ],
        "run": "run_deezer",
    },
    "spotify": {
        "color": ACCENT_SPOTIFY, "title": "Spotify  →  YouTube",
        "what": ("Récupère tous les titres d'une playlist Spotify et les importe "
                 "automatiquement dans une nouvelle playlist YouTube sur ton compte Google."),
        "needs": [
            "L'URL de ta playlist Spotify  (ex : https://open.spotify.com/playlist/...)",
            "La playlist doit être publique",
            "Une connexion internet",
            "Au premier lancement : connexion à ton compte Google dans le navigateur",
            "✅  Connexion mémorisée — tu n'auras à te connecter qu'une seule fois.",
            "⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.",
            "✅  Reprise automatique : relancez avec la même URL, l'import reprend là où il s'est arrêté.",
        ],
        "inputs": [
            {"label": "URL de la playlist Spotify", "key": "spotify_url",
             "placeholder": "https://open.spotify.com/playlist/..."},
        ],
        "run": "run_spotify",
    },
    "soundcloud": {
        "color": ACCENT_SOUNDCLOUD, "title": "SoundCloud  →  YouTube",
        "what": ("Récupère tous les titres d'une playlist SoundCloud publique et les importe "
                 "automatiquement dans une nouvelle playlist YouTube sur ton compte Google."),
        "needs": [
            "L'URL de ta playlist SoundCloud  (ex : https://soundcloud.com/user/sets/playlist)",
            "La playlist doit être publique",
            "Une connexion internet",
            "Au premier lancement : connexion à ton compte Google dans le navigateur",
            "✅  Connexion mémorisée — tu n'auras à te connecter qu'une seule fois.",
            "⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.",
            "✅  Reprise automatique : relancez avec la même URL, l'import reprend là où il s'est arrêté.",
        ],
        "inputs": [
            {"label": "URL de la playlist SoundCloud", "key": "soundcloud_url",
             "placeholder": "https://soundcloud.com/user/sets/playlist"},
        ],
        "run": "run_soundcloud",
    },
    "applemusic": {
        "color": ACCENT_APPLE, "title": "Apple Music  →  YouTube",
        "what": ("Récupère tous les titres d'une playlist Apple Music publique et les importe "
                 "automatiquement dans une nouvelle playlist YouTube sur ton compte Google. "
                 "Aucun compte développeur Apple requis."),
        "needs": [
            "L'URL de ta playlist Apple Music  (ex : https://music.apple.com/fr/playlist/...)",
            "La playlist doit être publique",
            "Une connexion internet",
            "Au premier lancement : connexion à ton compte Google dans le navigateur",
            "✅  Connexion mémorisée — tu n'auras à te connecter qu'une seule fois.",
            "⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.",
            "✅  Reprise automatique : relancez avec la même URL, l'import reprend là où il s'est arrêté.",
        ],
        "inputs": [
            {"label": "URL de la playlist Apple Music", "key": "apple_url",
             "placeholder": "https://music.apple.com/fr/playlist/..."},
        ],
        "run": "run_applemusic",
    },
    "youtube": {
        "color": ACCENT2, "title": "YouTube  →  MP3",
        "what": ("Télécharge toutes les vidéos d'une playlist YouTube et les convertit "
                 "en fichiers MP3 (192 kbps), classés dans un dossier portant le nom "
                 "de la playlist. Les fichiers sont numérotés dans l'ordre de la playlist."),
        "needs": ["L'URL complète de la playlist YouTube", "Une connexion internet"],
        "inputs": [
            {"label": "URL de la playlist YouTube", "key": "yt_url",
             "placeholder": "https://www.youtube.com/playlist?list=..."},
        ],
        "run": "run_youtube",
    },
    "excel": {
        "color": ACCENT3, "title": "Excel  →  MP3",
        "what": ("Lit un fichier Excel contenant une liste de titres, recherche chaque "
                 "chanson sur YouTube et la télécharge en MP3 dans l'ordre du fichier. "
                 "Une pause automatique est appliquée entre chaque titre."),
        "needs": ["Un fichier Excel avec les titres musicaux", "Une connexion internet"],
        "inputs": [
            {"label": "Fichier Excel", "key": "excel_path",
             "placeholder": "Clique sur Parcourir...", "browse": True,
             "filetypes": [("Excel", "*.xlsx *.xls"), ("Tous", "*.*")]},
            {"label": "Nom de la playlist", "key": "playlist_name",
             "placeholder": "ex : 1er mai 2026"},
        ],
        "run": "run_excel",
    },
}


# ── Page détail ───────────────────────────────────────────────────────────────
class DetailPage(tk.Frame):
    def __init__(self, parent, app, mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app  = app
        self.mode = mode
        self.cfg  = MODES[mode]
        self.vars = {}
        self._excel_sheet_var  = tk.StringVar()
        self._excel_col_var    = tk.StringVar(value="E")
        self._excel_row_var    = tk.StringVar(value="7")
        self._excel_opts_frame = None
        self._dest_path        = None
        self._failed_tracks    = []
        self._build()

    def _build(self):
        color = self.cfg["color"]

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=color, pady=16)
        header.pack(fill="x")
        tk.Button(header, text="← Retour", font=FONT_SMALL,
                  bg=color, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(color), activeforeground="white",
                  command=self.app.show_home).pack(side="left", padx=16)
        tk.Label(header, text=self.cfg["title"], font=FONT_H2,
                 bg=color, fg="white").pack(side="left", padx=8)
        icon = "☀" if _current_theme == "dark" else "🌙"
        tk.Button(header, text=icon, font=FONT_SMALL,
                  bg=color, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(color),
                  command=self.app.toggle_theme).pack(side="right", padx=16)

        # ── Corps scrollable ─────────────────────────────────────────────────
        body = make_scrollable(self)
        self._body = body

        tk.Label(body, text="Ce que ça fait", font=FONT_H2,
                 bg=BG, fg=color, anchor="w").pack(fill="x")
        tk.Label(body, text=self.cfg["what"], font=FONT,
                 bg=BG, fg=FG, wraplength=900, justify="left",
                 anchor="w").pack(fill="x", pady=(4, 14))

        tk.Label(body, text="Ce dont vous avez besoin", font=FONT_H2,
                 bg=BG, fg=color, anchor="w").pack(fill="x")
        for item in self.cfg["needs"]:
            tk.Label(body, text=f"  •  {item}", font=FONT,
                     bg=BG, fg=FG2, anchor="w").pack(fill="x")

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=16)

        for inp in self.cfg["inputs"]:
            self._make_input(body, inp)

        # ── Bouton Lancer ────────────────────────────────────────────────────
        self.btn_launch = tk.Button(body, text="  Lancer le script  ", font=FONT_H2,
                                    bg=color, fg="white", bd=0, cursor="hand2",
                                    activebackground=_lighten(color), activeforeground="white",
                                    pady=10, command=self._launch)
        self.btn_launch.pack(pady=(16, 0))

        # ── Section progression ───────────────────────────────────────────────
        self.progress_frame = tk.Frame(body, bg=BG2, padx=16, pady=14)
        self.lbl_status  = tk.Label(self.progress_frame, text="", font=FONT_H2, bg=BG2, fg=FG)
        self.lbl_status.pack(anchor="w")
        self.progressbar = ttk.Progressbar(self.progress_frame, orient="horizontal",
                                           mode="determinate", length=900)
        self.progressbar.pack(fill="x", pady=(8, 4))
        row_info = tk.Frame(self.progress_frame, bg=BG2)
        row_info.pack(fill="x")
        self.lbl_count   = tk.Label(row_info, text="", font=FONT, bg=BG2, fg=FG)
        self.lbl_count.pack(side="left")
        self.lbl_eta     = tk.Label(row_info, text="", font=FONT, bg=BG2, fg=FG2)
        self.lbl_eta.pack(side="right")
        self.lbl_current = tk.Label(self.progress_frame, text="", font=FONT_SMALL,
                                    bg=BG2, fg=FG2, anchor="w")
        self.lbl_current.pack(fill="x", pady=(4, 0))

        # Boutons fin (cachés)
        self._btn_row = tk.Frame(self.progress_frame, bg=BG2)
        self._btn_row.pack(fill="x", pady=(8, 0))

        self.btn_open_folder = tk.Button(
            self._btn_row, text="📂 Ouvrir le dossier", font=FONT,
            bg=color, fg="white", bd=0, cursor="hand2",
            activebackground=_lighten(color), activeforeground="white",
            padx=12, pady=6,
            command=self._open_folder)

        self.btn_retry = tk.Button(
            self._btn_row, text="🔄 Réessayer les titres manquants", font=FONT,
            bg="#dc2626", fg="white", bd=0, cursor="hand2",
            activebackground="#ef4444", activeforeground="white",
            padx=12, pady=6,
            command=self._retry_failed)

        # ── Zone de log ──────────────────────────────────────────────────────
        self.log = scrolledtext.ScrolledText(
            body, height=6, font=("Consolas", 9),
            bg=LOG_BG, fg=LOG_FG, state="disabled", bd=0, relief="flat")
        self.log.pack(fill="x", pady=(12, 0))

    # ── Inputs ───────────────────────────────────────────────────────────────
    def _make_input(self, parent, inp):
        tk.Label(parent, text=inp["label"], font=FONT,
                 bg=BG, fg=FG, anchor="w").pack(fill="x", pady=(6, 0))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")

        var = tk.StringVar()
        self.vars[inp["key"]] = var

        entry = tk.Entry(row, textvariable=var, font=FONT,
                         bg=BG2, fg=FG, insertbackground=FG, relief="flat", bd=6)
        entry.insert(0, inp["placeholder"])
        entry.configure(fg=FG2)

        def on_focus_in(e, ph=inp["placeholder"], v=var, en=entry):
            if v.get() == ph:
                en.delete(0, tk.END); en.configure(fg=FG)

        def on_focus_out(e, ph=inp["placeholder"], v=var, en=entry):
            if not v.get():
                en.insert(0, ph); en.configure(fg=FG2)

        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.pack(side="left", fill="x", expand=True, ipady=4)

        if inp.get("browse"):
            color = self.cfg["color"]
            filetypes = inp.get("filetypes", [("Tous", "*.*")])
            tk.Button(row, text="Parcourir...", font=FONT_SMALL,
                      bg=color, fg="white", bd=0, cursor="hand2",
                      activebackground=_lighten(color),
                      command=lambda v=var, en=entry, ft=filetypes: self._browse(v, en, ft)
                      ).pack(side="left", padx=(6, 0), ipady=4, ipadx=6)

        if inp.get("key") == "client_secret":
            tk.Button(parent, text="Comment obtenir ce fichier ?",
                      font=FONT_SMALL, bg=BG, fg=ACCENT1, bd=0, cursor="hand2",
                      activebackground=BG, activeforeground=_lighten(ACCENT1),
                      command=lambda: self.app.show_json_help(self.mode)
                      ).pack(anchor="w", pady=(2, 0))

        if inp.get("key") == "deezer_id":
            tk.Button(parent, text="Comment obtenir cet ID ?",
                      font=FONT_SMALL, bg=BG, fg=ACCENT1, bd=0, cursor="hand2",
                      activebackground=BG, activeforeground=_lighten(ACCENT1),
                      command=lambda: self.app.show_deezer_id_help(self.mode)
                      ).pack(anchor="w", pady=(2, 0))

        if inp.get("key") == "excel_path":
            # Zone dynamique feuille / colonne / ligne (visible après sélection)
            self._excel_opts_frame = tk.Frame(parent, bg=BG)
            # Feuille
            r1 = tk.Frame(self._excel_opts_frame, bg=BG)
            r1.pack(fill="x", pady=(6, 0))
            tk.Label(r1, text="Feuille", font=FONT, bg=BG, fg=FG,
                     width=10, anchor="w").pack(side="left")
            self._sheet_combo = ttk.Combobox(r1, textvariable=self._excel_sheet_var,
                                             state="readonly", font=FONT, width=24)
            self._sheet_combo.pack(side="left")
            # Colonne + première ligne
            r2 = tk.Frame(self._excel_opts_frame, bg=BG)
            r2.pack(fill="x", pady=(4, 0))
            tk.Label(r2, text="Colonne", font=FONT, bg=BG, fg=FG,
                     width=10, anchor="w").pack(side="left")
            tk.Entry(r2, textvariable=self._excel_col_var, font=FONT,
                     bg=BG2, fg=FG, insertbackground=FG,
                     relief="flat", bd=6, width=6).pack(side="left")
            tk.Label(r2, text="   1ère ligne de données", font=FONT,
                     bg=BG, fg=FG2).pack(side="left", padx=(12, 4))
            tk.Entry(r2, textvariable=self._excel_row_var, font=FONT,
                     bg=BG2, fg=FG, insertbackground=FG,
                     relief="flat", bd=6, width=6).pack(side="left")

    def _browse(self, var, entry, filetypes=None):
        if filetypes is None:
            filetypes = [("Tous", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry.configure(fg=FG)
            var.set(path)
            if self.mode == "excel":
                self._load_excel_sheets(path)

    def _load_excel_sheets(self, path):
        try:
            from download_from_excel import get_sheets
            sheets = get_sheets(path)
            self._sheet_combo["values"] = sheets
            # Pré-sélectionne "Deezer" si présente, sinon la première
            self._excel_sheet_var.set("Deezer" if "Deezer" in sheets else sheets[0])
            if self._excel_opts_frame:
                self._excel_opts_frame.pack(fill="x")
        except Exception:
            pass

    def _get(self, key):
        val = self.vars[key].get().strip()
        ph  = next((i["placeholder"] for i in self.cfg["inputs"] if i["key"] == key), "")
        return "" if val == ph else val

    # ── Progression ──────────────────────────────────────────────────────────
    def _show_progress(self, total):
        self._start_time = time.time()
        self._prog_total = total
        self.progressbar.configure(maximum=total, value=0)
        self.lbl_status.configure(text="En cours...")
        self.lbl_count.configure(text=f"0 / {total} musiques")
        self.lbl_eta.configure(text="Calcul en cours...")
        self.lbl_current.configure(text="")
        self.btn_open_folder.pack_forget()
        self.btn_retry.pack_forget()
        self.progress_frame.pack(fill="x", pady=(16, 0), before=self.log)
        self.btn_launch.configure(state="disabled")

    def update_progress(self, done, current=""):
        def _ui():
            self.progressbar.configure(value=done)
            self.lbl_count.configure(text=f"{done} / {self._prog_total} musiques")
            if current:
                self.lbl_current.configure(text=f"En cours : {current}")
            elapsed = time.time() - self._start_time
            if done > 0:
                eta_sec = int(elapsed / done * (self._prog_total - done))
                if eta_sec < 60:
                    eta_str = "moins d'une minute"
                elif eta_sec < 3600:
                    eta_str = f"{eta_sec // 60} min restante(s)"
                else:
                    h, m = divmod(eta_sec // 60, 60)
                    eta_str = f"{h}h {m:02d}min restante(s)"
                self.lbl_eta.configure(text=eta_str)
            if done >= self._prog_total:
                self.lbl_status.configure(text="Terminé !")
                self.lbl_eta.configure(text="")
                self.lbl_current.configure(text="")
                self.btn_launch.configure(state="normal")
                # Bouton ouvrir dossier
                if self._dest_path and os.path.isdir(self._dest_path):
                    self.btn_open_folder.pack(side="left", padx=(0, 8))
                # Bouton retry si titres manquants
                if self._failed_tracks:
                    self.btn_retry.pack(side="left")
                # Notification
                self.winfo_toplevel().bell()
                self.winfo_toplevel().lift()
                self.winfo_toplevel().attributes("-topmost", True)
                self.after(500, lambda: self.winfo_toplevel().attributes("-topmost", False))
        self.after(0, _ui)

    def _open_folder(self):
        if self._dest_path and os.path.isdir(self._dest_path):
            os.startfile(self._dest_path)

    def _retry_failed(self):
        if not self._failed_tracks:
            return
        name = self._get("playlist_name") or "playlist"
        out  = os.path.join(_app_dir(), "playlists")
        # Extraire les titres depuis "001 - Titre"
        tracks = []
        for line in self._failed_tracks:
            parts = line.split(" - ", 1)
            tracks.append(parts[1].strip() if len(parts) > 1 else line.strip())
        self._failed_tracks = []
        self.btn_retry.pack_forget()
        self.after(0, lambda t=len(tracks): self._show_progress(t))

        def do_retry():
            from download_from_excel import download_tracks

            def on_progress(done, _, current):
                self.update_progress(done, current)

            sys.stdout = TextRedirector(self.log)
            print(f"\nRelance de {len(tracks)} titre(s) manquant(s)...")
            _, failed = download_tracks(tracks, out, name, on_progress=on_progress)
            self._failed_tracks = failed
            self.update_progress(len(tracks), "")

        threading.Thread(target=do_retry, daemon=True).start()

    # ── Lancement ────────────────────────────────────────────────────────────
    def _launch(self):
        sys.stdout = TextRedirector(self.log)
        self._start_time = time.time()
        self._prog_total = 0
        self._dest_path  = None
        self._failed_tracks = []
        threading.Thread(target=getattr(self, self.cfg["run"]), daemon=True).start()

    def run_deezer(self):
        deezer_id = self._get("deezer_id")
        if not deezer_id:
            print("Erreur : veuillez entrer un ID de playlist Deezer."); return
        if not deezer_id.isdigit():
            print("Erreur : l'ID Deezer doit être un nombre (ex : 14838804003)."); return
        try:
            from deezer import get_deezer_tracks
            from youtube import get_youtube_service, create_playlist, add_videos, QuotaExceededError

            progress_file = os.path.join(_app_dir(), f"progression_{deezer_id}.json")
            progress = {}
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)

            print("Récupération des titres Deezer...")
            tracks = get_deezer_tracks(deezer_id)
            total  = len(tracks)
            print(f"{total} morceaux récupérés.")

            start_index = progress.get("completed", 0)
            playlist_id = progress.get("playlist_id_yt")

            youtube = get_youtube_service()

            if start_index > 0:
                print(f"\n Reprise détectée — {start_index}/{total} titres déjà ajoutés.")
                print(f" L'import reprend à partir du titre {start_index + 1}.\n")
            else:
                print("Création de la playlist YouTube...")
                playlist_id = create_playlist(youtube, "Importée depuis Deezer")
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id, "completed": 0, "total": total}, f)

            self.after(0, lambda t=total: self._show_progress(t))

            def save_progress(completed):
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id, "completed": completed, "total": total}, f)
                track_name = tracks[completed-1] if completed <= len(tracks) else ""
                self.update_progress(completed, track_name)

            print("Ajout des vidéos...")
            try:
                add_videos(youtube, playlist_id, tracks,
                           start_index=start_index, on_success=save_progress)
                os.remove(progress_file)
                print(f"\n{'─'*50}")
                print("Import terminé ! Tous les titres ont été ajoutés.")
                print("Retrouvez votre playlist dans votre bibliothèque YouTube.")
                save_history({"mode": "deezer", "name": f"Deezer {deezer_id}",
                              "count": total, "date": _today(), "path": ""})
            except QuotaExceededError as e:
                done = int(str(e))
                print(f"\n{'─'*50}")
                print(f"⚠  Limite quotidienne YouTube atteinte après {done} titres.")
                print(f"   Il reste {total-done} titre(s). Relancez demain avec le même ID.")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_spotify(self):
        import re
        url = self._get("spotify_url")
        if not url:
            print("Erreur : veuillez entrer une URL de playlist Spotify."); return
        match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
        if not match:
            print("Erreur : URL de playlist Spotify invalide."); return
        playlist_id = match.group(1)

        try:
            from spotify import get_spotify_tracks
            from youtube import get_youtube_service, create_playlist, add_videos, QuotaExceededError

            progress_file = os.path.join(_app_dir(), f"progression_spotify_{playlist_id}.json")
            progress = {}
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)

            print("Récupération des titres Spotify...")
            tracks = get_spotify_tracks(url)
            total  = len(tracks)
            print(f"{total} morceaux récupérés.")

            start_index = progress.get("completed", 0)
            playlist_id_yt = progress.get("playlist_id_yt")

            youtube = get_youtube_service()

            if start_index > 0:
                print(f"\n Reprise détectée — {start_index}/{total} titres déjà ajoutés.")
                print(f" L'import reprend à partir du titre {start_index + 1}.\n")
            else:
                print("Création de la playlist YouTube...")
                playlist_id_yt = create_playlist(youtube, "Importée depuis Spotify")
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": 0, "total": total}, f)

            self.after(0, lambda t=total: self._show_progress(t))

            def save_progress(completed):
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": completed, "total": total}, f)
                track_name = tracks[completed-1] if completed <= len(tracks) else ""
                self.update_progress(completed, track_name)

            print("Ajout des vidéos...")
            try:
                add_videos(youtube, playlist_id_yt, tracks,
                           start_index=start_index, on_success=save_progress)
                os.remove(progress_file)
                print(f"\n{'─'*50}")
                print("Import terminé ! Tous les titres ont été ajoutés.")
                print("Retrouvez votre playlist dans votre bibliothèque YouTube.")
                save_history({"mode": "spotify", "name": f"Spotify {playlist_id}",
                              "count": total, "date": _today(), "path": ""})
            except QuotaExceededError as e:
                done = int(str(e))
                print(f"\n{'─'*50}")
                print(f"⚠  Limite quotidienne YouTube atteinte après {done} titres.")
                print(f"   Il reste {total-done} titre(s). Relancez demain avec la même URL.")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_applemusic(self):
        import re
        url = self._get("apple_url")
        if not url:
            print("Erreur : veuillez entrer une URL de playlist Apple Music."); return
        if "music.apple.com" not in url:
            print("Erreur : URL Apple Music invalide."); return

        playlist_id = re.sub(r'[^a-zA-Z0-9]', '_', url.split("music.apple.com/")[-1])[:40]

        try:
            from applemusic import get_applemusic_tracks
            from youtube import get_youtube_service, create_playlist, add_videos, QuotaExceededError

            progress_file = os.path.join(_app_dir(), f"progression_apple_{playlist_id}.json")
            progress = {}
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)

            print("Récupération des titres Apple Music...")
            tracks = get_applemusic_tracks(url)
            total  = len(tracks)
            print(f"{total} morceaux récupérés.")

            start_index    = progress.get("completed", 0)
            playlist_id_yt = progress.get("playlist_id_yt")

            youtube = get_youtube_service()

            if start_index > 0:
                print(f"\n Reprise détectée — {start_index}/{total} titres déjà ajoutés.")
                print(f" L'import reprend à partir du titre {start_index + 1}.\n")
            else:
                print("Création de la playlist YouTube...")
                playlist_id_yt = create_playlist(youtube, "Importée depuis Apple Music")
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": 0, "total": total}, f)

            self.after(0, lambda t=total: self._show_progress(t))

            def save_progress(completed):
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": completed, "total": total}, f)
                track_name = tracks[completed-1] if completed <= len(tracks) else ""
                self.update_progress(completed, track_name)

            print("Ajout des vidéos...")
            try:
                add_videos(youtube, playlist_id_yt, tracks,
                           start_index=start_index, on_success=save_progress)
                os.remove(progress_file)
                print(f"\n{'─'*50}")
                print("Import terminé ! Tous les titres ont été ajoutés.")
                print("Retrouvez votre playlist dans votre bibliothèque YouTube.")
                save_history({"mode": "applemusic", "name": f"Apple {playlist_id[:25]}",
                              "count": total, "date": _today(), "path": ""})
            except QuotaExceededError as e:
                done = int(str(e))
                print(f"\n{'─'*50}")
                print(f"⚠  Limite quotidienne YouTube atteinte après {done} titres.")
                print(f"   Il reste {total-done} titre(s). Relancez demain avec la même URL.")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_soundcloud(self):
        import re
        url = self._get("soundcloud_url")
        if not url:
            print("Erreur : veuillez entrer une URL de playlist SoundCloud."); return
        if "soundcloud.com" not in url:
            print("Erreur : URL SoundCloud invalide."); return

        playlist_id = re.sub(r'[^a-zA-Z0-9]', '_', url.split("soundcloud.com/")[-1])

        try:
            from soundcloud import get_soundcloud_tracks
            from youtube import get_youtube_service, create_playlist, add_videos, QuotaExceededError

            progress_file = os.path.join(_app_dir(), f"progression_soundcloud_{playlist_id}.json")
            progress = {}
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)

            print("Récupération des titres SoundCloud...")
            tracks = get_soundcloud_tracks(url)
            total  = len(tracks)
            print(f"{total} morceaux récupérés.")

            start_index    = progress.get("completed", 0)
            playlist_id_yt = progress.get("playlist_id_yt")

            youtube = get_youtube_service()

            if start_index > 0:
                print(f"\n Reprise détectée — {start_index}/{total} titres déjà ajoutés.")
                print(f" L'import reprend à partir du titre {start_index + 1}.\n")
            else:
                print("Création de la playlist YouTube...")
                playlist_id_yt = create_playlist(youtube, "Importée depuis SoundCloud")
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": 0, "total": total}, f)

            self.after(0, lambda t=total: self._show_progress(t))

            def save_progress(completed):
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump({"playlist_id_yt": playlist_id_yt, "completed": completed, "total": total}, f)
                track_name = tracks[completed-1] if completed <= len(tracks) else ""
                self.update_progress(completed, track_name)

            print("Ajout des vidéos...")
            try:
                add_videos(youtube, playlist_id_yt, tracks,
                           start_index=start_index, on_success=save_progress)
                os.remove(progress_file)
                print(f"\n{'─'*50}")
                print("Import terminé ! Tous les titres ont été ajoutés.")
                print("Retrouvez votre playlist dans votre bibliothèque YouTube.")
                save_history({"mode": "soundcloud", "name": f"SoundCloud {playlist_id[:30]}",
                              "count": total, "date": _today(), "path": ""})
            except QuotaExceededError as e:
                done = int(str(e))
                print(f"\n{'─'*50}")
                print(f"⚠  Limite quotidienne YouTube atteinte après {done} titres.")
                print(f"   Il reste {total-done} titre(s). Relancez demain avec la même URL.")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_youtube(self):
        url = self._get("yt_url")
        if not url:
            print("Erreur : veuillez entrer une URL de playlist YouTube."); return
        try:
            from youtube_to_mp3 import download_and_convert_playlist

            def on_progress(done, total, current):
                if total and self._prog_total == 0:
                    self.after(0, lambda t=total: self._show_progress(t))
                self.update_progress(done, current)

            dest = os.path.join(_app_dir(), "playlists")
            download_and_convert_playlist(url, output_folder=dest, on_progress=on_progress)
            self._dest_path = dest
            dest_abs = os.path.abspath(dest)
            print(f"\n{'─'*50}")
            print(f"Terminé ! Vos MP3 sont disponibles ici :\n{dest_abs}")
            save_history({"mode": "youtube", "name": url[:60],
                          "count": self._prog_total, "date": _today(), "path": dest_abs})
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_excel(self):
        path = self._get("excel_path")
        name = self._get("playlist_name")
        if not path:
            print("Erreur : veuillez sélectionner un fichier Excel."); return
        if not name:
            print("Erreur : veuillez entrer un nom de playlist."); return

        sheet    = self._excel_sheet_var.get() or "Deezer"
        col_str  = self._excel_col_var.get().strip().upper()
        col_num  = (ord(col_str) - ord('A') + 1) if len(col_str) == 1 else 5
        try:
            first_row = int(self._excel_row_var.get())
        except ValueError:
            first_row = 7

        try:
            from download_from_excel import get_tracks_from_excel, download_tracks
            print(f"Lecture du fichier Excel (feuille '{sheet}', colonne {col_str}, ligne {first_row})...")
            tracks = get_tracks_from_excel(path, sheet, col_num, first_row)
            total  = len(tracks)
            print(f"{total} titres trouvés.")
            self.after(0, lambda t=total: self._show_progress(t))

            def on_progress(done, _, current):
                self.update_progress(done, current)

            out  = os.path.join(_app_dir(), "playlists")
            dest = os.path.join(out, name)
            _, failed = download_tracks(tracks, out, name, on_progress=on_progress)
            self._dest_path     = dest
            self._failed_tracks = failed
            self.update_progress(total, "")
            dest_abs = os.path.abspath(dest)
            print(f"\n{'─'*50}")
            print(f"Terminé ! Vos MP3 sont disponibles ici :\n{dest_abs}")
            save_history({"mode": "excel", "name": name,
                          "count": total, "date": _today(), "path": dest_abs})
        except Exception as e:
            print(f"ERREUR : {e}")


def _today():
    import datetime
    return datetime.date.today().strftime("%d/%m/%Y")


# ── Pages d'aide ──────────────────────────────────────────────────────────────
def _help_header(page, color, title, back_cmd):
    header = tk.Frame(page, bg=color, pady=16)
    header.pack(fill="x")
    tk.Button(header, text="← Retour", font=FONT_SMALL,
              bg=color, fg="white", bd=0, cursor="hand2",
              activebackground=_lighten(color), activeforeground="white",
              command=back_cmd).pack(side="left", padx=16)
    tk.Label(header, text=title, font=FONT_H2,
             bg=color, fg="white").pack(side="left", padx=8)


def _help_steps(body, steps, color):
    for title, substeps in steps:
        f = tk.Frame(body, bg=color, padx=10, pady=4)
        f.pack(fill="x", pady=(14, 0))
        tk.Label(f, text=title, font=FONT_H2, bg=color, fg="white").pack(side="left")
        for sub in substeps:
            row = tk.Frame(body, bg=BG)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text="→", font=FONT, bg=BG, fg=color,
                     width=2).pack(side="left", anchor="n")
            tk.Label(row, text=sub, font=FONT, bg=BG, fg=FG,
                     wraplength=850, justify="left", anchor="w"
                     ).pack(side="left", fill="x", expand=True)


STEPS_JSON = [
    ("Étape 1 — Créer un projet Google Cloud", [
        "Ouvre ton navigateur et va sur  console.cloud.google.com",
        "Connecte-toi avec ton compte Google.",
        "Clique sur le menu déroulant en haut à gauche (à côté du logo Google Cloud).",
        "Clique sur « Nouveau projet », donne-lui un nom (ex : PlaylistManager) et valide.",
    ]),
    ("Étape 2 — Activer l'API YouTube Data v3", [
        "Dans le menu de gauche, clique sur « API et services » → « Bibliothèque ».",
        "Dans la barre de recherche, tape  YouTube Data API v3.",
        "Clique sur le résultat puis sur le bouton bleu « Activer ».",
    ]),
    ("Étape 3 — Configurer l'écran de consentement OAuth", [
        "Dans le menu de gauche, clique sur « API et services » → « Écran de consentement OAuth ».",
        "Choisis « Externe » puis clique sur « Créer ».",
        "Remplis uniquement le champ « Nom de l'application » (ex : PlaylistManager) et ton e-mail.",
        "Clique sur « Enregistrer et continuer » jusqu'à la fin.",
    ]),
    ("Étape 4 — Créer les identifiants OAuth 2.0", [
        "Dans le menu de gauche, clique sur « API et services » → « Identifiants ».",
        "Clique sur « + Créer des identifiants » → « ID client OAuth ».",
        "Dans « Type d'application », choisis « Application de bureau ».",
        "Donne un nom (ex : PlaylistManager Desktop) puis clique sur « Créer ».",
    ]),
    ("Étape 5 — Télécharger le fichier JSON", [
        "Une fenêtre apparaît avec ton Client ID et ton Client Secret.",
        "Clique sur « Télécharger le fichier JSON » (icône de téléchargement).",
        "Le fichier s'appelle quelque chose comme  client_secret_xxx.json.",
        "Tu peux le renommer en  client_secret.json  pour plus de clarté.",
        "Sélectionne ce fichier dans l'application via le bouton « Parcourir... ».",
    ]),
]

STEPS_DEEZER = [
    ("Méthode 1 — Depuis l'application Deezer (PC / Mac)", [
        "Ouvre Deezer sur ton ordinateur et connecte-toi.",
        "Dans la barre de gauche, clique sur la playlist que tu veux importer.",
        "Regarde l'URL dans la barre d'adresse de ton navigateur.",
        "L'ID est le nombre à la fin de l'URL.",
        "Exemple :  deezer.com/playlist/14838804003  →  ID = 14838804003",
    ]),
    ("Méthode 2 — Depuis le navigateur web", [
        "Va sur  deezer.com  et connecte-toi.",
        "Clique sur la playlist souhaitée dans ta bibliothèque.",
        "Dans la barre d'adresse, l'URL ressemble à :  https://www.deezer.com/fr/playlist/14838804003",
        "Copie uniquement le nombre à la fin (ici : 14838804003).",
        "Colle ce nombre dans le champ « ID de la playlist Deezer ».",
    ]),
    ("La playlist doit être publique ou vous en être le propriétaire", [
        "Si la playlist est privée et ne vous appartient pas, le script ne pourra pas y accéder.",
        "Pour rendre une playlist publique : clic droit → Modifier → décocher « Privée ».",
    ]),
]


class JsonHelpPage(tk.Frame):
    def __init__(self, parent, app, back_mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        _help_header(self, ACCENT1, "Comment obtenir le fichier client_secret.json",
                     lambda: app.show_detail(back_mode))
        body = make_scrollable(self)
        _help_steps(body, STEPS_JSON, ACCENT1)
        tk.Frame(body, bg=FG2, height=1).pack(fill="x", pady=16)
        tk.Label(body,
                 text="Ce fichier est personnel et lié à ton compte Google.\nNe le partage pas et ne le publie pas en ligne.",
                 font=FONT, bg=BG, fg=FG2, justify="left").pack(anchor="w")


class DeezerIdHelpPage(tk.Frame):
    def __init__(self, parent, app, back_mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        _help_header(self, ACCENT1, "Comment obtenir l'ID de la playlist Deezer",
                     lambda: app.show_detail(back_mode))
        body = make_scrollable(self)
        _help_steps(body, STEPS_DEEZER, ACCENT1)
        tk.Frame(body, bg=FG2, height=1).pack(fill="x", pady=16)
        tk.Label(body, text="Exemple d'URL :", font=FONT, bg=BG, fg=FG2).pack(anchor="w")
        tk.Label(body,
                 text="https://www.deezer.com/fr/playlist/  14838804003",
                 font=("Consolas", 11), bg=BG2, fg=ACCENT3,
                 padx=12, pady=8).pack(fill="x", pady=(4, 0))
        tk.Label(body,
                 text="                                      ↑ c'est cet ID qu'il faut copier",
                 font=("Consolas", 9), bg=BG, fg=FG2).pack(anchor="w")


# ── Point d'entrée ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
