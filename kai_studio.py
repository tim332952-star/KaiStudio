from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tkinter import PhotoImage, StringVar, Tk, messagebox, ttk


APP_ROOT = Path(__file__).resolve().parent
PYAPPS_ROOT = APP_ROOT.parent


DEFAULT_THEME = {
    "window_background": "#001F3F",
    "panel_background": "#001F3F",
    "preview_text_background": "#060E1F",
    "text": "#EDF2F7",
    "title": "#FFD700",
    "accent": "#3399FF",
}


@dataclass(frozen=True)
class KaiApp:
    title: str
    folder: str
    script: str
    icon: str
    description: str

    @property
    def app_dir(self) -> Path:
        return PYAPPS_ROOT / self.folder

    @property
    def script_path(self) -> Path:
        return self.app_dir / self.script


KAI_APPS = (
    KaiApp(
        title="Kai Job Finder",
        folder="KaiJobFinder",
        script="main.py",
        icon="job_finder.png",
        description="Search, score, and review job opportunities.",
    ),
    KaiApp(
        title="Kai Job Application Tracker",
        folder="KaiJobApplicationTracker",
        script="Main.py",
        icon="application_tracker.png",
        description="Track applications, companies, stages, and follow-ups.",
    ),
    KaiApp(
        title="Kai Recruitment Screener",
        folder="KaiRecruitmentScreener",
        script="main.py",
        icon="recruitment_screener.png",
        description="Screen candidates and generate ranked reports.",
    ),
    KaiApp(
        title="Kai Resume Builder Studio",
        folder="KaiResumeBuilderStudio",
        script="app.py",
        icon="resume_builder.png",
        description="Build, tailor, and export resume versions.",
    ),
)


def load_theme() -> dict[str, str]:
    theme = dict(DEFAULT_THEME)
    theme_path = APP_ROOT / "app_config" / "theme.json"
    if theme_path.exists():
        with theme_path.open("r", encoding="utf-8") as file:
            theme.update(json.load(file))
    return theme


def app_python(app_dir: Path) -> str:
    for candidate in (
        app_dir / ".venv" / "Scripts" / "pythonw.exe",
        app_dir / ".venv" / "Scripts" / "python.exe",
        APP_ROOT / ".venv" / "Scripts" / "pythonw.exe",
        APP_ROOT / ".venv" / "Scripts" / "python.exe",
    ):
        if candidate.exists():
            return str(candidate)
    return sys.executable


class KaiStudio:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.theme = load_theme()
        self.images: dict[str, PhotoImage] = {}
        self.status = StringVar(value="Ready")

        self.configure_window()
        self.configure_styles()
        self.build_layout()

    def configure_window(self) -> None:
        self.root.title("Kai Studio")
        self.root.geometry("860x520")
        self.root.minsize(760, 460)
        self.root.configure(bg=self.theme["window_background"])

        icon_path = APP_ROOT / "logo.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

    def configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        bg = self.theme["window_background"]
        panel = self.theme["panel_background"]
        surface = self.theme["preview_text_background"]
        text = self.theme["text"]
        title = self.theme["title"]
        accent = self.theme["accent"]

        style.configure(".", background=bg, foreground=text, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("Shell.TFrame", background=bg)
        style.configure("Header.TLabel", background=bg, foreground=title, font=("Segoe UI", 24, "bold"))
        style.configure("Subheader.TLabel", background=bg, foreground=text, font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=surface, foreground=text, padding=(12, 8))
        style.configure("Tile.TFrame", background=panel, relief="solid", borderwidth=1)
        style.configure("TileTitle.TLabel", background=panel, foreground=title, font=("Segoe UI", 13, "bold"))
        style.configure("TileText.TLabel", background=panel, foreground=text, font=("Segoe UI", 9))
        style.configure("Launch.TButton", background=accent, foreground="#FFFFFF", padding=(12, 8))
        style.map(
            "Launch.TButton",
            background=[("active", title), ("pressed", title)],
            foreground=[("active", "#000000"), ("pressed", "#000000")],
        )

    def build_layout(self) -> None:
        shell = ttk.Frame(self.root, style="Shell.TFrame", padding=24)
        shell.pack(fill="both", expand=True)

        ttk.Label(shell, text="Kai Studio", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            shell,
            text="Launch your Kai job search, tracking, screening, and resume tools.",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(4, 20))

        grid = ttk.Frame(shell)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1, uniform="apps")
        grid.columnconfigure(1, weight=1, uniform="apps")
        grid.rowconfigure(0, weight=1, uniform="apps")
        grid.rowconfigure(1, weight=1, uniform="apps")

        for index, app in enumerate(KAI_APPS):
            self.add_app_tile(grid, app, index // 2, index % 2)

        ttk.Label(self.root, textvariable=self.status, style="Status.TLabel").pack(fill="x", side="bottom")

    def add_app_tile(self, parent: ttk.Frame, app: KaiApp, row: int, column: int) -> None:
        tile = ttk.Frame(parent, style="Tile.TFrame", padding=18)
        tile.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        tile.columnconfigure(1, weight=1)

        icon = self.load_icon(app.icon)
        if icon is not None:
            ttk.Label(tile, image=icon, background=self.theme["panel_background"]).grid(
                row=0,
                column=0,
                rowspan=3,
                sticky="n",
                padx=(0, 14),
            )

        ttk.Label(tile, text=app.title, style="TileTitle.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(tile, text=app.description, style="TileText.TLabel", wraplength=280).grid(
            row=1,
            column=1,
            sticky="new",
            pady=(6, 14),
        )
        ttk.Button(
            tile,
            text="Launch",
            style="Launch.TButton",
            command=lambda selected=app: self.launch_app(selected),
        ).grid(row=2, column=1, sticky="w")

    def load_icon(self, file_name: str) -> PhotoImage | None:
        icon_path = APP_ROOT / "assets" / file_name
        if not icon_path.exists():
            return None

        image = PhotoImage(file=str(icon_path))
        self.images[file_name] = image
        return image

    def launch_app(self, app: KaiApp) -> None:
        if not app.app_dir.exists():
            self.show_error(app, f"App folder was not found: {app.app_dir}")
            return
        if not app.script_path.exists():
            self.show_error(app, f"Entry script was not found: {app.script_path}")
            return

        try:
            subprocess.Popen(
                [app_python(app.app_dir), str(app.script_path)],
                cwd=str(app.app_dir),
                close_fds=True,
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            )
        except OSError as exc:
            self.show_error(app, str(exc))
            return

        self.status.set(f"Launched {app.title}")

    def show_error(self, app: KaiApp, detail: str) -> None:
        self.status.set(f"Could not launch {app.title}")
        messagebox.showerror("Launch failed", f"{app.title} could not be started.\n\n{detail}")


def main() -> None:
    root = Tk()
    KaiStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
