import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import sys
import os
import time


def _app_dir():
    """Dossier du .exe en mode frozen, dossier courant sinon."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()


# ── Couleurs & polices ────────────────────────────────────────────────────────
BG          = "#1e1e2e"
BG2         = "#2a2a3d"
ACCENT1     = "#7c3aed"   # violet  – Deezer → YouTube
ACCENT2     = "#0ea5e9"   # bleu    – YouTube → MP3
ACCENT3     = "#10b981"   # vert    – Excel  → MP3
FG          = "#f1f5f9"
FG2         = "#94a3b8"
FONT        = ("Segoe UI", 11)
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_H2     = ("Segoe UI", 14, "bold")
FONT_SMALL  = ("Segoe UI", 9)


def make_scrollable(parent, bg=None, padx=36, pady=20):
    """Retourne un Frame scrollable à l'intérieur de parent."""
    if bg is None:
        bg = BG
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, bg=bg, padx=padx, pady=pady)
    win = canvas.create_window((0, 0), window=body, anchor="nw")

    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    body.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    return body



# ── Redirection stdout vers le widget texte ───────────────────────────────────
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


# ── Application principale ────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Playlist Manager")
        self.geometry("780x580")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Conteneur unique dont on swap le contenu
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_home()

    # ── Navigation ──────────────────────────────────────────────────────────
    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear()
        HomePage(self.container, self)

    def show_detail(self, mode):
        self.clear()
        DetailPage(self.container, self, mode)

    def show_json_help(self, back_mode):
        self.clear()
        JsonHelpPage(self.container, self, back_mode)

    def show_deezer_id_help(self, back_mode):
        self.clear()
        DeezerIdHelpPage(self.container, self, back_mode)


# ── Page d'accueil ────────────────────────────────────────────────────────────
class HomePage(tk.Frame):
    CARDS = [
        {
            "mode":    "deezer",
            "color":   ACCENT1,
            "icon":    "🎵",
            "title":   "Deezer  →  YouTube",
            "desc":    "Importe une playlist Deezer\ndans ta bibliothèque YouTube",
        },
        {
            "mode":    "youtube",
            "color":   ACCENT2,
            "icon":    "▶",
            "title":   "YouTube  →  MP3",
            "desc":    "Télécharge une playlist YouTube\net convertit chaque vidéo en MP3",
        },
        {
            "mode":    "excel",
            "color":   ACCENT3,
            "icon":    "📊",
            "title":   "Excel  →  MP3",
            "desc":    "Télécharge les musiques dans\nl'ordre défini dans un fichier Excel",
        },
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Playlist Manager", font=FONT_TITLE,
                 bg=BG, fg=FG).pack(pady=(40, 6))
        tk.Label(self, text="Choisissez une action", font=FONT,
                 bg=BG, fg=FG2).pack(pady=(0, 36))

        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack()

        for card in self.CARDS:
            self._make_card(cards_frame, card)

    def _make_card(self, parent, card):
        color  = card["color"]
        frame  = tk.Frame(parent, bg=color, cursor="hand2",
                          padx=24, pady=20, bd=0)
        frame.pack(side="left", padx=14)

        tk.Label(frame, text=card["icon"], font=("Segoe UI", 28),
                 bg=color, fg="white").pack()
        tk.Label(frame, text=card["title"], font=FONT_H2,
                 bg=color, fg="white").pack(pady=(6, 4))
        tk.Label(frame, text=card["desc"], font=FONT_SMALL,
                 bg=color, fg="white", justify="center").pack()

        # Clic sur n'importe quel enfant → ouvre la page détail
        for widget in [frame] + frame.winfo_children():
            widget.bind("<Button-1>", lambda e, m=card["mode"]: self.app.show_detail(m))

        # Hover
        def on_enter(e, f=frame, c=color):
            f.configure(bg=_lighten(c))
            for w in f.winfo_children():
                w.configure(bg=_lighten(c))

        def on_leave(e, f=frame, c=color):
            f.configure(bg=c)
            for w in f.winfo_children():
                w.configure(bg=c)

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        for w in frame.winfo_children():
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)


# ── Page détail ───────────────────────────────────────────────────────────────
MODES = {
    "deezer": {
        "color":  ACCENT1,
        "title":  "Deezer  →  YouTube",
        "what":   (
            "Récupère tous les titres d'une playlist Deezer et les importe "
            "automatiquement dans une nouvelle playlist YouTube sur ton compte Google."
        ),
        "needs": [
            "L'ID de ta playlist Deezer  (ex : 14838804003)",
            "Ton fichier client_secret.json  (Google Cloud Console → API YouTube Data v3 → OAuth 2.0)",
            "Une connexion internet",
            "⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.",
            "⚠  Pour 190 titres (~28 500 unités), l'import devra être étalé sur 3 jours.",
            "✅  Reprise automatique : si le quota est atteint, relancez le script le lendemain avec le même ID — il reprendra exactement là où il s'est arrêté.",
        ],
        "inputs": [
            {"label": "ID de la playlist Deezer", "key": "deezer_id",
             "placeholder": "ex : 14838804003"},
            {"label": "Fichier client_secret.json", "key": "client_secret",
             "placeholder": "Clique sur Parcourir...", "browse": True,
             "filetypes": [("JSON", "*.json"), ("Tous", "*.*")]},
        ],
        "run": "run_deezer",
    },
    "youtube": {
        "color":  ACCENT2,
        "title":  "YouTube  →  MP3",
        "what":   (
            "Télécharge toutes les vidéos d'une playlist YouTube et les convertit "
            "en fichiers MP3 (192 kbps), classés dans un dossier portant le nom "
            "de la playlist. Les fichiers sont numérotés dans l'ordre de la playlist."
        ),
        "needs": [
            "L'URL complète de la playlist YouTube",
            "Une connexion internet",
        ],
        "inputs": [
            {"label": "URL de la playlist YouTube", "key": "yt_url",
             "placeholder": "https://www.youtube.com/playlist?list=..."},
        ],
        "run": "run_youtube",
    },
    "excel": {
        "color":  ACCENT3,
        "title":  "Excel  →  MP3",
        "what":   (
            "Lit un fichier Excel contenant une liste de titres (colonne E, "
            "feuille 'Deezer'), recherche chaque chanson sur YouTube et la "
            "télécharge en MP3 dans l'ordre du fichier. Une pause automatique "
            "est appliquée entre chaque titre pour éviter les blocages."
        ),
        "needs": [
            "Un fichier Excel avec les titres dans la colonne E (feuille 'Deezer')",
            "Une connexion internet",
        ],
        "inputs": [
            {"label": "Fichier Excel", "key": "excel_path",
             "placeholder": "Clique sur Parcourir...", "browse": True},
            {"label": "Nom de la playlist", "key": "playlist_name",
             "placeholder": "ex : 1er mai 2026"},
        ],
        "run": "run_excel",
    },
}


class DetailPage(tk.Frame):
    def __init__(self, parent, app, mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app   = app
        self.mode  = mode
        self.cfg   = MODES[mode]
        self.vars  = {}
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

        # ── Corps scrollable ─────────────────────────────────────────────────
        body = make_scrollable(self)

        # Ce que ça fait
        tk.Label(body, text="Ce que ça fait", font=FONT_H2,
                 bg=BG, fg=color, anchor="w").pack(fill="x")
        tk.Label(body, text=self.cfg["what"], font=FONT,
                 bg=BG, fg=FG, wraplength=680, justify="left",
                 anchor="w").pack(fill="x", pady=(4, 14))

        # Prérequis
        tk.Label(body, text="Ce dont vous avez besoin", font=FONT_H2,
                 bg=BG, fg=color, anchor="w").pack(fill="x")
        for item in self.cfg["needs"]:
            tk.Label(body, text=f"  •  {item}", font=FONT,
                     bg=BG, fg=FG2, anchor="w").pack(fill="x")

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=16)

        # Champs de saisie
        for inp in self.cfg["inputs"]:
            self._make_input(body, inp)

        # ── Bouton Lancer ────────────────────────────────────────────────────
        self.btn_launch = tk.Button(body, text="  Lancer le script  ", font=FONT_H2,
                                    bg=color, fg="white", bd=0, cursor="hand2",
                                    activebackground=_lighten(color), activeforeground="white",
                                    pady=10, command=self._launch)
        self.btn_launch.pack(pady=(16, 0))

        # ── Section progression (cachée au départ) ───────────────────────────
        self.progress_frame = tk.Frame(body, bg=BG2, padx=16, pady=14)

        self.lbl_status = tk.Label(self.progress_frame, text="", font=FONT_H2,
                                   bg=BG2, fg=FG)
        self.lbl_status.pack(anchor="w")

        self.progressbar = ttk.Progressbar(self.progress_frame, orient="horizontal",
                                           mode="determinate", length=680)
        self.progressbar.pack(fill="x", pady=(8, 4))

        row_info = tk.Frame(self.progress_frame, bg=BG2)
        row_info.pack(fill="x")

        self.lbl_count = tk.Label(row_info, text="", font=FONT,
                                  bg=BG2, fg=FG)
        self.lbl_count.pack(side="left")

        self.lbl_eta = tk.Label(row_info, text="", font=FONT,
                                bg=BG2, fg=FG2)
        self.lbl_eta.pack(side="right")

        self.lbl_current = tk.Label(self.progress_frame, text="", font=FONT_SMALL,
                                    bg=BG2, fg=FG2, anchor="w")
        self.lbl_current.pack(fill="x", pady=(4, 0))

        # ── Zone de log ──────────────────────────────────────────────────────
        self.log = scrolledtext.ScrolledText(
            body, height=6, font=("Consolas", 9),
            bg="#0f0f1a", fg="#a0f0a0", state="disabled",
            bd=0, relief="flat"
        )
        self.log.pack(fill="x", pady=(12, 0))

    def _make_input(self, parent, inp):
        tk.Label(parent, text=inp["label"], font=FONT,
                 bg=BG, fg=FG, anchor="w").pack(fill="x", pady=(6, 0))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")

        var = tk.StringVar()
        self.vars[inp["key"]] = var

        entry = tk.Entry(row, textvariable=var, font=FONT,
                         bg=BG2, fg=FG, insertbackground=FG,
                         relief="flat", bd=6)
        entry.insert(0, inp["placeholder"])
        entry.configure(fg=FG2)

        def on_focus_in(e, ph=inp["placeholder"], v=var, en=entry):
            if v.get() == ph:
                en.delete(0, tk.END)
                en.configure(fg=FG)

        def on_focus_out(e, ph=inp["placeholder"], v=var, en=entry):
            if not v.get():
                en.insert(0, ph)
                en.configure(fg=FG2)

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
                      font=FONT_SMALL, bg=BG, fg=ACCENT1,
                      bd=0, cursor="hand2", activebackground=BG,
                      activeforeground=_lighten(ACCENT1),
                      command=lambda: self.app.show_json_help(self.mode)
                      ).pack(anchor="w", pady=(2, 0))

        if inp.get("key") == "deezer_id":
            tk.Button(parent, text="Comment obtenir cet ID ?",
                      font=FONT_SMALL, bg=BG, fg=ACCENT1,
                      bd=0, cursor="hand2", activebackground=BG,
                      activeforeground=_lighten(ACCENT1),
                      command=lambda: self.app.show_deezer_id_help(self.mode)
                      ).pack(anchor="w", pady=(2, 0))

    def _browse(self, var, entry, filetypes=None):
        if filetypes is None:
            filetypes = [("Tous", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry.configure(fg=FG)
            var.set(path)

    def _get(self, key):
        val = self.vars[key].get().strip()
        placeholder = next(
            (i["placeholder"] for i in self.cfg["inputs"] if i["key"] == key), ""
        )
        return "" if val == placeholder else val

    # ── Progression ──────────────────────────────────────────────────────────
    def _show_progress(self, total):
        self._start_time   = time.time()
        self._prog_total   = total
        self.progressbar.configure(maximum=total, value=0)
        self.lbl_status.configure(text="En cours...")
        self.lbl_count.configure(text=f"0 / {total} musiques")
        self.lbl_eta.configure(text="Calcul en cours...")
        self.lbl_current.configure(text="")
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
        self.after(0, _ui)

    # ── Lancement ────────────────────────────────────────────────────────────
    def _launch(self):
        sys.stdout = TextRedirector(self.log)
        self._start_time = time.time()
        self._prog_total = 0
        threading.Thread(target=getattr(self, self.cfg["run"]),
                         daemon=True).start()

    def run_deezer(self):
        import json
        deezer_id     = self._get("deezer_id")
        client_secret = self._get("client_secret")
        if not deezer_id:
            print("Erreur : veuillez entrer un ID de playlist Deezer.")
            return
        if not client_secret:
            print("Erreur : veuillez sélectionner votre fichier client_secret.json.")
            return
        try:
            from deezer import get_deezer_tracks
            from youtube import get_youtube_service, create_playlist, add_videos

            progress_file = os.path.join(_app_dir(), f"progression_{deezer_id}.json")
            progress = {}
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)

            print("Récupération des titres Deezer...")
            tracks = get_deezer_tracks(deezer_id)
            total = len(tracks)
            print(f"{total} morceaux récupérés.")

            start_index = progress.get("completed", 0)
            playlist_id = progress.get("playlist_id_yt")

            print("Connexion à YouTube (une fenêtre va s'ouvrir dans le navigateur)...")
            youtube = get_youtube_service(client_secret)

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
                track_name = tracks[completed - 1] if completed <= len(tracks) else ""
                self.update_progress(completed, track_name)

            from youtube import QuotaExceededError
            print("Ajout des vidéos...")
            try:
                add_videos(youtube, playlist_id, tracks,
                           start_index=start_index, on_success=save_progress)
                os.remove(progress_file)
                print(f"\n{'─'*50}")
                print("Import terminé ! Tous les titres ont été ajoutés.")
                print("Retrouvez votre playlist dans votre bibliothèque YouTube.")
            except QuotaExceededError as e:
                done = int(str(e))
                remaining = total - done
                print(f"\n{'─'*50}")
                print(f"⚠  Limite quotidienne YouTube atteinte après {done} titres.")
                print(f"   Il reste {remaining} titre(s) à importer.")
                print(f"   Relancez le script demain avec le même ID Deezer :")
                print(f"   l'import reprendra automatiquement au titre {done + 1}.")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_youtube(self):
        url = self._get("yt_url")
        if not url:
            print("Erreur : veuillez entrer une URL de playlist YouTube.")
            return
        try:
            from youtube_to_mp3 import download_and_convert_playlist

            def on_progress(done, total, current):
                if total and self._prog_total == 0:
                    self.after(0, lambda t=total: self._show_progress(t))
                self.update_progress(done, current)

            dest = os.path.join(_app_dir(), "playlists")
            download_and_convert_playlist(url, output_folder=dest, on_progress=on_progress)
            dest_abs = os.path.abspath(dest)
            print(f"\n{'─'*50}")
            print(f"Terminé ! Vos MP3 sont disponibles ici :")
            print(f"{dest_abs}")
        except Exception as e:
            print(f"ERREUR : {e}")

    def run_excel(self):
        path = self._get("excel_path")
        name = self._get("playlist_name")
        if not path:
            print("Erreur : veuillez sélectionner un fichier Excel.")
            return
        if not name:
            print("Erreur : veuillez entrer un nom de playlist.")
            return
        try:
            from download_from_excel import get_tracks_from_excel, download_tracks
            print("Lecture du fichier Excel...")
            tracks = get_tracks_from_excel(path, "Deezer", 5, 7)
            total = len(tracks)
            print(f"{total} titres trouvés.")
            self.after(0, lambda t=total: self._show_progress(t))

            def on_progress(done, _, current):
                self.update_progress(done, current)

            out = os.path.join(_app_dir(), "playlists")
            dest = os.path.join(out, name)
            download_tracks(tracks, out, name, on_progress=on_progress)
            self.update_progress(total, "")
            dest_abs = os.path.abspath(dest)
            print(f"\n{'─'*50}")
            print(f"Terminé ! Vos MP3 sont disponibles ici :")
            print(f"{dest_abs}")
        except Exception as e:
            print(f"ERREUR : {e}")


# ── Page d'aide client_secret.json ───────────────────────────────────────────
STEPS = [
    (
        "Étape 1 — Créer un projet Google Cloud",
        [
            "Ouvre ton navigateur et va sur  console.cloud.google.com",
            "Connecte-toi avec ton compte Google.",
            "Clique sur le menu déroulant en haut à gauche (à côté du logo Google Cloud).",
            "Clique sur « Nouveau projet », donne-lui un nom (ex : PlaylistManager) et valide.",
        ]
    ),
    (
        "Étape 2 — Activer l'API YouTube Data v3",
        [
            "Dans le menu de gauche, clique sur « API et services » → « Bibliothèque ».",
            "Dans la barre de recherche, tape  YouTube Data API v3.",
            "Clique sur le résultat puis sur le bouton bleu « Activer ».",
        ]
    ),
    (
        "Étape 3 — Configurer l'écran de consentement OAuth",
        [
            "Dans le menu de gauche, clique sur « API et services » → « Écran de consentement OAuth ».",
            "Choisis « Externe » puis clique sur « Créer ».",
            "Remplis uniquement le champ « Nom de l'application » (ex : PlaylistManager) et ton e-mail.",
            "Clique sur « Enregistrer et continuer » jusqu'à la fin (les autres étapes sont optionnelles).",
        ]
    ),
    (
        "Étape 4 — Créer les identifiants OAuth 2.0",
        [
            "Dans le menu de gauche, clique sur « API et services » → « Identifiants ».",
            "Clique sur « + Créer des identifiants » → « ID client OAuth ».",
            "Dans « Type d'application », choisis « Application de bureau ».",
            "Donne un nom (ex : PlaylistManager Desktop) puis clique sur « Créer ».",
        ]
    ),
    (
        "Étape 5 — Télécharger le fichier JSON",
        [
            "Une fenêtre apparaît avec ton Client ID et ton Client Secret.",
            "Clique sur « Télécharger le fichier JSON » (icône de téléchargement).",
            "Le fichier téléchargé s'appelle quelque chose comme  client_secret_xxx.json.",
            "Tu peux le renommer en  client_secret.json  pour plus de clarté.",
            "Sélectionne ce fichier dans l'application via le bouton « Parcourir... ».",
        ]
    ),
]


class JsonHelpPage(tk.Frame):
    def __init__(self, parent, app, back_mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app       = app
        self.back_mode = back_mode
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=ACCENT1, pady=16)
        header.pack(fill="x")

        tk.Button(header, text="← Retour", font=FONT_SMALL,
                  bg=ACCENT1, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(ACCENT1), activeforeground="white",
                  command=lambda: self.app.show_detail(self.back_mode)
                  ).pack(side="left", padx=16)

        tk.Label(header, text="Comment obtenir le fichier client_secret.json",
                 font=FONT_H2, bg=ACCENT1, fg="white").pack(side="left", padx=8)

        # ── Corps scrollable ─────────────────────────────────────────────────
        body = make_scrollable(self)

        # ── Étapes ──────────────────────────────────────────────────────────
        for i, (title, substeps) in enumerate(STEPS, start=1):
            # Numéro + titre
            num_frame = tk.Frame(body, bg=ACCENT1, padx=10, pady=4)
            num_frame.pack(fill="x", pady=(14, 0))
            tk.Label(num_frame, text=title, font=FONT_H2,
                     bg=ACCENT1, fg="white").pack(side="left")

            # Sous-étapes
            for sub in substeps:
                row = tk.Frame(body, bg=BG)
                row.pack(fill="x", padx=10, pady=2)
                tk.Label(row, text="→", font=FONT, bg=BG, fg=ACCENT1,
                         width=2).pack(side="left", anchor="n")
                tk.Label(row, text=sub, font=FONT, bg=BG, fg=FG,
                         wraplength=620, justify="left", anchor="w"
                         ).pack(side="left", fill="x", expand=True)

        # ── Note finale ──────────────────────────────────────────────────────
        tk.Frame(body, bg=FG2, height=1).pack(fill="x", pady=16)
        tk.Label(body,
                 text="Ce fichier est personnel et lié à ton compte Google.\nNe le partage pas et ne le publie pas en ligne.",
                 font=FONT, bg=BG, fg=FG2, justify="left"
                 ).pack(anchor="w")


# ── Page d'aide ID Deezer ─────────────────────────────────────────────────────
DEEZER_STEPS = [
    (
        "Méthode 1 — Depuis l'application Deezer (PC / Mac)",
        [
            "Ouvre Deezer sur ton ordinateur et connecte-toi.",
            "Dans la barre de gauche, clique sur la playlist que tu veux importer.",
            "Regarde l'URL dans la barre d'adresse de ton navigateur.",
            "L'ID est le nombre à la fin de l'URL.",
            "Exemple :  deezer.com/playlist/14838804003  →  ID = 14838804003",
        ]
    ),
    (
        "Méthode 2 — Depuis le navigateur web",
        [
            "Va sur  deezer.com  et connecte-toi.",
            "Clique sur la playlist souhaitée dans ta bibliothèque.",
            "Dans la barre d'adresse, l'URL ressemble à :  https://www.deezer.com/fr/playlist/14838804003",
            "Copie uniquement le nombre à la fin (ici : 14838804003).",
            "Colle ce nombre dans le champ « ID de la playlist Deezer ».",
        ]
    ),
    (
        "La playlist doit être publique ou vous en être le propriétaire",
        [
            "Si la playlist est privée et ne vous appartient pas, le script ne pourra pas y accéder.",
            "Pour rendre une playlist publique : clic droit sur la playlist → Modifier → décocher « Privée ».",
        ]
    ),
]


class DeezerIdHelpPage(tk.Frame):
    def __init__(self, parent, app, back_mode):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.app       = app
        self.back_mode = back_mode
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=ACCENT1, pady=16)
        header.pack(fill="x")

        tk.Button(header, text="← Retour", font=FONT_SMALL,
                  bg=ACCENT1, fg="white", bd=0, cursor="hand2",
                  activebackground=_lighten(ACCENT1), activeforeground="white",
                  command=lambda: self.app.show_detail(self.back_mode)
                  ).pack(side="left", padx=16)

        tk.Label(header, text="Comment obtenir l'ID de la playlist Deezer",
                 font=FONT_H2, bg=ACCENT1, fg="white").pack(side="left", padx=8)

        # ── Corps scrollable ─────────────────────────────────────────────────
        body = make_scrollable(self)

        for title, substeps in DEEZER_STEPS:
            num_frame = tk.Frame(body, bg=ACCENT1, padx=10, pady=4)
            num_frame.pack(fill="x", pady=(14, 0))
            tk.Label(num_frame, text=title, font=FONT_H2,
                     bg=ACCENT1, fg="white").pack(side="left")

            for sub in substeps:
                row = tk.Frame(body, bg=BG)
                row.pack(fill="x", padx=10, pady=2)
                tk.Label(row, text="→", font=FONT, bg=BG, fg=ACCENT1,
                         width=2).pack(side="left", anchor="n")
                tk.Label(row, text=sub, font=FONT, bg=BG, fg=FG,
                         wraplength=640, justify="left", anchor="w"
                         ).pack(side="left", fill="x", expand=True)

        # ── Exemple visuel ───────────────────────────────────────────────────
        tk.Frame(body, bg=FG2, height=1).pack(fill="x", pady=16)
        tk.Label(body, text="Exemple d'URL :", font=FONT, bg=BG, fg=FG2).pack(anchor="w")
        tk.Label(body,
                 text="https://www.deezer.com/fr/playlist/  14838804003",
                 font=("Consolas", 11), bg=BG2, fg=ACCENT3,
                 padx=12, pady=8
                 ).pack(fill="x", pady=(4, 0))
        tk.Label(body,
                 text="                                      ↑ c'est cet ID qu'il faut copier",
                 font=("Consolas", 9), bg=BG, fg=FG2
                 ).pack(anchor="w")


# ── Utilitaire couleur ────────────────────────────────────────────────────────
def _lighten(hex_color, amount=30):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = min(r + amount, 255), min(g + amount, 255), min(b + amount, 255)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Point d'entrée ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
