
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import shutil
import os
import sys
import json
import hashlib

from ui_patcher import build_ui
from builder import CLGBuilder
from moves import RYX_MOVES, RYX_CUSTOM_MOVES


APP_DIR = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
ROOT = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "USF4-TrialEditor"
CONFIG = ROOT / "config.json"
CLG_REL = Path("patch_ae2_tu2/battle/chara/RYX/RYX_swan.clg")
HUD_REL = Path("patch_ae2_tu3/ui/trial_mode/trial_tasks.emz")
MENU_REL = Path("patch_ae2_tu2/ui/ultra_trial_mode/ultra_trial_menu.emz")

KNOWN = {
    HUD_REL: "8f2fc64fefe7b72a4555d4eb93bdda49fc0e6b9f74bb21a0eb98876f72afd677",
    CLG_REL: "ae002c4febe8f8c195833f04c8e9334a3028e0189257d08721a8b12c962c7add",
    MENU_REL: "63ee74b3dd593e5575b826b023f405da2cf50b3824bbbabb5d1bca00bd7f4a24",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def configure(root):
    global ORIGINAL, OUTPUT, GAME_FILE, UI_FILES
    ROOT.mkdir(parents=True, exist_ok=True)
    try:
        saved = json.loads(CONFIG.read_text(encoding="utf-8"))
        game = Path(saved["game_dir"])
    except (OSError, ValueError, KeyError, TypeError):
        game = None
    rels = (CLG_REL, HUD_REL, MENU_REL)
    while game is None or not all((game / rel).is_file() for rel in rels):
        selected = filedialog.askdirectory(parent=root, title="Select the USF4 game installation folder")
        if not selected:
            return False
        game = Path(selected).resolve()
        if not all((game / rel).is_file() for rel in rels):
            messagebox.showerror("Invalid folder", "Required USF4 files were not found. Select the game root.", parent=root)
            game = None
    key = hashlib.sha256(str(game.resolve()).casefold().encode()).hexdigest()[:16]
    backup_dir = ROOT / "backups" / key
    # Never replace an existing backup. Check all sources before copying.
    sources = []
    for rel in rels:
        target = backup_dir / rel
        source = target if target.exists() else game / rel
        if rel in KNOWN and digest(source) != KNOWN[rel]:
            raise ValueError(f"Original file verification failed: {source}\nRestore the original game file before setup. Do not overwrite existing backups.")
        sources.append((source, target))
    for source, target in sources:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as out:
                out.write(source.read_bytes())
    ORIGINAL = backup_dir / CLG_REL
    OUTPUT = ROOT / "working" / "RYX_swan.clg"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    GAME_FILE = game / CLG_REL
    patch_dir = Path(getattr(sys, "_MEIPASS", APP_DIR)) / "patches"
    if APP_DIR.name.lower() == "tools" and not getattr(sys, "frozen", False):
        patch_dir = APP_DIR.parent / "patches"
    UI_FILES = [
        (backup_dir / HUD_REL, patch_dir, game / HUD_REL),
        (backup_dir / MENU_REL, patch_dir, game / MENU_REL),
    ]
    CONFIG.write_text(json.dumps({"game_dir": str(game)}, indent=2), encoding="utf-8")
    return True

MOVE_NAMES = {
    # Standing normals
    "st_lp": "Standing Light Punch",
    "st_hp": "Standing Heavy Punch",
    "st_mk": "Standing Medium Kick",
    "st_mp": "Standing Medium Punch",
    "st_lk": "Standing Light Kick",
    "st_hk": "Standing Heavy Kick",

    # Crouching normals
    "cr_lp": "Crouching Light Punch",
    "cr_mp": "Crouching Medium Punch",
    "cr_hp": "Crouching Heavy Punch",
    "cr_lk": "Crouching Light Kick",
    "cr_mk": "Crouching Medium Kick",
    "cr_hk": "Crouching Heavy Kick",

    # Jumping normals
    "j_mp": "Jumping Medium Punch",
    "j_mk": "Jumping Medium Kick",
    "j_hk": "Jumping Heavy Kick",
    "j_lp": "Jumping Light Punch",
    "j_hp": "Jumping Heavy Punch",
    "j_lk": "Jumping Light Kick",

    # Hadoken
    "hadoken": "Hadoken",
    "lp_hadoken": "Light Hadoken",
    "mp_hadoken": "Medium Hadoken",
    "hp_hadoken": "Heavy Hadoken",
    "ex_hadoken": "EX Hadoken",

    # Ryusokyaku
    "ryusokyaku": "Ryusokyaku",
    "lk_ryusokyaku": "Light Ryusokyaku",
    "mk_ryusokyaku": "Medium Ryusokyaku",
    "hk_ryusokyaku": "Heavy Ryusokyaku",
    "ex_ryusokyaku": "EX Ryusokyaku",

    # Tatsumaki
    "tatsu": "Tatsumaki Senpukyaku",
    "lk_tatsu": "Light Tatsumaki Senpukyaku",
    "mk_tatsu": "Medium Tatsumaki Senpukyaku",
    "hk_tatsu": "Heavy Tatsumaki Senpukyaku",
    "ex_tatsu": "EX Tatsumaki Senpukyaku",
    "air_tatsu": "Airborne Tatsumaki Senpukyaku",

    # Shoryuken
    "shoryuken": "Shoryuken",
    "lp_shoryuken": "Light Shoryuken",
    "mp_shoryuken": "Medium Shoryuken",
    "hp_shoryuken": "Heavy Shoryuken",

    # Unique attacks
    "senbukyaku": "Senbukyaku",
    "target_combo": "Target Combo",

    # Focus
    "focus_attack": "Focus Attack",
    "ex_focus_cancel": "EX Focus Cancel",
    "ex_red_focus": "EX Red Focus Attack",

    # Super and Ultras
    "raging_demon": "Raging Demon",
    "metsu_hadoken": "Metsu Hadoken",
    "messatsu_goshoryu": "Messatsu Goshoryu",
}

ULTRA_OPTIONS = {
    "Ultra I - Metsu Hadoken": 0,
    "Ultra II - Messatsu Goshoryu": 1
}

STANCE_OPTIONS = {
    "Standing": 0,
    "Crouching": 1,
    "Jumping": 2
}



class TrialEditor:

    def __init__(self, root):

        self.root = root
        self.root.title("USF4 Trial Editor - Evil Ryu")
        self.root.geometry("1000x720")
        self.root.minsize(850, 650)

        self.builder = CLGBuilder(ORIGINAL)
        self.current_trial = 1

        self.moves = {
            **RYX_MOVES,
            **RYX_CUSTOM_MOVES
        }
        self.display_to_id = {
            MOVE_NAMES.get(key, key): key
            for key in self.moves
        }

        self.project_path = None
        self.create_ui()
        self.refresh_trials()

        self.trial_list.selection_set(0)
        self.refresh_combo()

    def create_ui(self):

        style = ttk.Style()
        style.theme_use("clam")

        header = ttk.Frame(self.root, padding=15)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="USF4 Trial Editor",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Evil Ryu | RYX | 24 Trials"
        ).pack(anchor="w")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # Left panel: Trial selection

        left = ttk.LabelFrame(
            main, text="Trials", padding=8
        )
        left.pack(side="left", fill="y")

        self.trial_list = tk.Listbox(
            left,
            width=22,
            height=1,
            font=("Segoe UI", 11),
            exportselection=False
        )

        trial_scroll = ttk.Scrollbar(
        left,
        orient="vertical",
        command=self.trial_list.yview
        )

        trial_scroll.pack(side="right", fill="y")

        self.trial_list.config(
        yscrollcommand=trial_scroll.set
        )

        self.trial_list.pack(
        side="left",
        fill="both",
        expand=True
        )

        self.trial_list.bind(
            "<<ListboxSelect>>",
            self.select_trial
        )

        # Right panel: Combo editor

        right = ttk.Frame(main, padding=(12, 0))
        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.trial_title = ttk.Label(
            right,
            font=("Segoe UI", 15, "bold")
        )
        self.trial_title.pack(anchor="w", pady=5)
        settings = ttk.LabelFrame(
        right, text="Trial Settings", padding=8
        )
        settings.pack(fill="x", pady=5)

        settings.columnconfigure(0, weight=1)
        settings.columnconfigure(1, weight=1)

        ttk.Label(settings, text="Ultra Selection").grid(
            row=0, column=0, sticky="w"
        )

        ttk.Label(settings, text="Opponent Stance").grid(
            row=0, column=1, sticky="w"
        )

        self.ultra_picker = ttk.Combobox(
            settings,
            values=list(ULTRA_OPTIONS),
            state="readonly"
        )

        self.ultra_picker.grid(
            row=1, column=0, sticky="ew", padx=(0, 5)
        )

        self.stance_picker = ttk.Combobox(
            settings,
            values=list(STANCE_OPTIONS),
            state="readonly"
        )

        self.stance_picker.grid(
            row=1, column=1, sticky="ew"
        )

        self.ultra_picker.bind(
            "<<ComboboxSelected>>", self.update_settings
        )

        self.stance_picker.bind(
            "<<ComboboxSelected>>", self.update_settings
        )

        self.combo_list = tk.Listbox(
            right,
            height=1,
            font=("Segoe UI", 12),
            exportselection=False
        )
        self.combo_list.pack(fill="both", expand=True)

        controls = ttk.Frame(right)
        controls.pack(fill="x", pady=8)

        ttk.Button(
            controls, text="Move Up",
            command=lambda: self.reorder(-1)
        ).pack(side="left", padx=2)

        ttk.Button(
            controls, text="Move Down",
            command=lambda: self.reorder(1)
        ).pack(side="left", padx=2)

        ttk.Button(
            controls, text="Remove",
            command=self.remove_move
        ).pack(side="left", padx=2)

        ttk.Button(
            controls, text="Reset Trial",
            command=self.reset_trial
        ).pack(side="right", padx=2)

        # Move selection

        ttk.Label(
            right, text="Move Library"
        ).pack(anchor="w")

        self.move_picker = ttk.Combobox(
            right,
            values=list(self.display_to_id.keys()),
            state="readonly",
            font=("Segoe UI", 11)
        )

        self.move_picker.pack(fill="x", pady=5)
        self.move_picker.set("Standing Heavy Punch")

        move_controls = ttk.Frame(right)
        move_controls.pack(fill="x")

        ttk.Button(
            move_controls,
            text="Add Move",
            command=self.add_move
        ).pack(side="left", padx=2)

        ttk.Button(
            move_controls,
            text="Replace Selected",
            command=self.replace_move
        ).pack(side="left", padx=2)

        # Bottom toolbar: reserve space before the expanding editor.
        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(side="bottom", fill="x", before=main)

        project_buttons = ttk.Frame(bottom)
        project_buttons.pack(fill="x", pady=(0, 5))
        for label, command in [("New Project", self.new_project),
                               ("Open Project", self.open_project),
                               ("Save Project", self.save_project)]:
            ttk.Button(project_buttons, text=label, command=command).pack(side="left", padx=4)

        trial_buttons = ttk.Frame(bottom)
        trial_buttons.pack(fill="x", pady=(0, 5))
        for label, command in [
            ("Export CLG", self.export),
            ("Install to Game", self.install),
            ("Restore Original Trials", self.restore),
        ]:
            ttk.Button(trial_buttons, text=label, command=command).pack(side="left", padx=4)

        ui_buttons = ttk.Frame(bottom)
        ui_buttons.pack(fill="x")
        ttk.Button(ui_buttons, text="Install Expanded UI", command=self.install_ui).pack(side="left", padx=4)
        ttk.Button(ui_buttons, text="Restore Original UI", command=self.restore_ui).pack(side="left", padx=4)

        ttk.Label(
            bottom,
            text="Note: Install Expanded UI for trials with more than 8 moves (max. 16 displayed).",
            foreground="#8A6200", font=("Segoe UI", 10),
            wraplength=780, padding=(4, 5)
        ).pack(fill="x")

        self.status = tk.StringVar(value="Ready")
        ttk.Label(bottom, textvariable=self.status, padding=(4, 2)).pack(fill="x")

    def project_data(self):
        trials = []
        for n in range(1, 25):
            commands = []
            for move in self.builder.combos[n]:
                if isinstance(move, dict):
                    key = next((k for k, v in RYX_CUSTOM_MOVES.items() if v == move), None)
                    if key is None:
                        raise ValueError("Unknown custom move")
                    commands.append({"custom": key})
                else:
                    commands.append({"original": list(move)})
            trials.append({"number": n, "moves": commands,
                           "ultra": self.builder.ultras[n],
                           "stance": self.builder.stances[n]})
        return {"format": "USF4-TrialEditor", "version": 1,
                "character": "RYX", "source_sha256": KNOWN[CLG_REL],
                "trials": trials}

    def save_project(self):
        path = filedialog.asksaveasfilename(parent=self.root,
            defaultextension=".json", filetypes=[("Trial List", "*.json")],
            initialfile=self.project_path.name if self.project_path else "Evil-Ryu.json")
        if not path:
            return
        try:
            target = Path(path)
            data = json.dumps(self.project_data(), indent=2)
            target.write_text(data, encoding="utf-8")
            self.project_path = target
            self.status.set(f"Saved project: {target.name}")
        except Exception as error:
            messagebox.showerror("Save failed", str(error), parent=self.root)

    def open_project(self):
        path = filedialog.askopenfilename(parent=self.root,
            filetypes=[("Trial List", "*.json")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if (data["format"], data["version"], data["character"], data["source_sha256"]) != (
                    "USF4-TrialEditor", 1, "RYX", KNOWN[CLG_REL]):
                raise ValueError("Unsupported project format or game version")
            candidate = CLGBuilder(ORIGINAL)
            counts = {n: len(c) for n, c in candidate.combos.items()}
            trials = data["trials"]
            if len(trials) != 24 or {t["number"] for t in trials} != set(range(1, 25)):
                raise ValueError("Project must contain all 24 trials exactly once")
            for t in trials:
                n = t["number"]
                if type(n) is not int or type(t["ultra"]) is not int or t["ultra"] not in (0, 1) or type(t["stance"]) is not int or t["stance"] not in (0, 1, 2):
                    raise ValueError("Invalid trial settings")
                commands = []
                for entry in t["moves"]:
                    if set(entry) == {"custom"}:
                        commands.append(RYX_CUSTOM_MOVES[entry["custom"]])
                    elif set(entry) == {"original"}:
                        a, b = entry["original"]
                        if type(a) is not int or type(b) is not int or a not in counts or not 1 <= b <= counts[a]:
                            raise ValueError("Invalid original move reference")
                        commands.append((a, b))
                    else:
                        raise ValueError("Invalid move entry")
                if not commands:
                    raise ValueError("Empty trial")
                candidate.combos[n] = commands
                candidate.ultras[n] = t["ultra"]
                candidate.stances[n] = t["stance"]
            if not messagebox.askyesno("Open Project", "Replace the current editor contents? Save any changes first.", parent=self.root):
                return
            self.builder = candidate
            self.project_path = Path(path)
            self.current_trial = 1
            self.refresh_combo()
            self.status.set(f"Opened project: {self.project_path.name}")
        except Exception as error:
            messagebox.showerror("Open failed", str(error), parent=self.root)

    def new_project(self):
        if not messagebox.askyesno("New Project", "Reset all editor trials? Save any changes first.", parent=self.root):
            return
        self.builder = CLGBuilder(ORIGINAL)
        self.project_path = None
        self.current_trial = 1
        self.refresh_combo()

    def install_ui(self):
        self.patch_ui(restore=False)

    def restore_ui(self):
        self.patch_ui(restore=True)

    def patch_ui(self, restore=False):
        action = "Restore Original UI" if restore else "Install Expanded UI"
        if not messagebox.askyesno(action, f"Make sure USF4 is closed.\n\n{action}?"):
            return
        backups = {}
        changed = []
        try:
            prepared = {}
            for original, patch_dir, destination in UI_FILES:
                if not destination.is_file():
                    raise FileNotFoundError(destination)
                backups[destination] = destination.read_bytes()
                prepared[destination] = original.read_bytes() if restore else build_ui(original, patch_dir)
                if restore and hashlib.sha256(prepared[destination]).hexdigest() != KNOWN[HUD_REL if destination.name == "trial_tasks.emz" else MENU_REL]:
                    raise ValueError(f"Backup verification failed: {original}")
            for destination, data in prepared.items():
                changed.append(destination)
                destination.write_bytes(data)
        except Exception as error:
            failures = []
            for destination in reversed(changed):
                try:
                    destination.write_bytes(backups[destination])
                except Exception as rollback_error:
                    failures.append(str(rollback_error))
            detail = str(error)
            if failures:
                detail += "\nRollback failed: " + "; ".join(failures)
            messagebox.showerror("UI Patch Failed", detail)
            return
        self.status.set(f"{action} successful")
        messagebox.showinfo("Success", f"{action} successful!")

    def move_name(self, move):

        # Match custom definitions
        if isinstance(move, dict):

            for name, definition in RYX_CUSTOM_MOVES.items():
                if move == definition:
                    return name

        # Match original command text
        else:

            trial, position = move

            command = self.builder.original.get_command(
                trial, position
            )

            for name, reference in RYX_MOVES.items():

                source = self.builder.original.get_command(
                    *reference
                )

                if command["strings"] == source["strings"]:
                    return name

            return f"Original {trial}:{position}"

        return "Unknown move"

    def refresh_trials(self):

        self.trial_list.delete(0, tk.END)

        for trial, combo in self.builder.combos.items():

            self.trial_list.insert(
                tk.END,
                f"Trial {trial:02}   ({len(combo)} moves)"
            )

        self.trial_list.selection_set(
            self.current_trial - 1
        )
        self.trial_list.see(self.current_trial - 1)

    def refresh_combo(self, update_trials=True):
        self.refresh_settings()

        combo = self.builder.combos[self.current_trial]

        self.trial_title.config(
            text=f"Trial {self.current_trial} - {len(combo)} moves"
        )

        self.combo_list.delete(0, tk.END)

        for i, move in enumerate(combo, start=1):

            move_id = self.move_name(move)
            name = MOVE_NAMES.get(move_id, move_id)

            self.combo_list.insert(
                tk.END,
                f"{i:02}. {name}"
            )

        if update_trials:
            self.refresh_trials()

        total = sum(
            len(c) for c in self.builder.combos.values()
        )

        self.status.set(
            f"{len(self.moves)} available moves | "
            f"{total} total commands"
        )

    def select_trial(self, event=None):

        selection = self.trial_list.curselection()

        if selection:

            self.current_trial = selection[0] + 1
            self.refresh_combo(update_trials=False)

    def selected_move(self):

        selection = self.combo_list.curselection()

        if selection:
            return selection[0]

        return None

    def add_move(self):

        name = self.display_to_id[self.move_picker.get()]

        combo = self.builder.combos[self.current_trial]

        combo.append(self.moves[name])

        self.auto_ultra(name)
        self.refresh_combo()

        self.combo_list.selection_set(len(combo) - 1)

    def replace_move(self):

        index = self.selected_move()

        if index is None:
            return

        name = self.display_to_id[self.move_picker.get()]

        self.builder.combos[self.current_trial][index] = (
            self.moves[name]
        )

        self.auto_ultra(name)
        self.refresh_combo()
        self.combo_list.selection_set(index)

    def remove_move(self):

        index = self.selected_move()

        if index is None:
            return

        combo = self.builder.combos[self.current_trial]

        if len(combo) <= 1:

            messagebox.showwarning(
                "Invalid Combo",
                "A trial must contain at least one move."
            )
            return

        combo.pop(index)

        self.refresh_combo()

        self.combo_list.selection_set(
            min(index, len(combo) - 1)
        )

    def reorder(self, direction):

        index = self.selected_move()

        if index is None:
            return

        combo = self.builder.combos[self.current_trial]

        target = index + direction

        if not 0 <= target < len(combo):
            return

        combo[index], combo[target] = (
            combo[target], combo[index]
        )

        self.refresh_combo()
        self.combo_list.selection_set(target)

    def reset_trial(self):

        self.builder.reset_trial(self.current_trial)
        self.refresh_combo()

    def export(self):

        try:

            self.builder.save(OUTPUT)

            self.status.set(f"Exported: {OUTPUT}")

            messagebox.showinfo(
                "Export Successful",
                str(OUTPUT)
            )

        except Exception as error:

            messagebox.showerror(
                "Export Failed", str(error)
            )

    def install(self):

        if not messagebox.askyesno(
            "Install Modification",
            "Make sure USF4 is closed.\n\n"
            "Install the current trial set?"
        ):
            return

        try:

            self.builder.save(OUTPUT)
            shutil.copy2(OUTPUT, GAME_FILE)

            self.status.set("Modification installed")

            messagebox.showinfo(
                "Success",
                "Custom trials installed!"
            )

        except Exception as error:

            messagebox.showerror(
                "Installation Failed", str(error)
            )

    def restore(self):

        if not messagebox.askyesno(
            "Restore Original",
            "Make sure USF4 is closed.\n\n"
            "Restore the original Evil Ryu trials?"
        ):
            return

        try:

            shutil.copy2(ORIGINAL, GAME_FILE)

            self.status.set("Original game file restored")

            messagebox.showinfo(
                "Success",
                "Original trials restored!"
            )

        except Exception as error:

            messagebox.showerror(
                "Restore Failed", str(error)
            )
    
    def update_settings(self, event=None):
        self.builder.ultras[self.current_trial] = (
            ULTRA_OPTIONS[self.ultra_picker.get()]
        )

        self.builder.stances[self.current_trial] = (
            STANCE_OPTIONS[self.stance_picker.get()]
        )

    def refresh_settings(self):
        ultra = self.builder.ultras[self.current_trial]
        stance = self.builder.stances[self.current_trial]

        for name, value in ULTRA_OPTIONS.items():
            if value == ultra:
                self.ultra_picker.set(name)
                break

        for name, value in STANCE_OPTIONS.items():
            if value == stance:
                self.stance_picker.set(name)
                break

    def auto_ultra(self, move):
        if move == "metsu_hadoken":
            self.builder.ultras[self.current_trial] = 0

        elif move == "messatsu_goshoryu":
            self.builder.ultras[self.current_trial] = 1


if __name__ == "__main__":

    import ctypes

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "USF4.TrialEditor"
        )

    root = tk.Tk()
    icon_path = Path(getattr(sys, "_MEIPASS", APP_DIR)) / "icon.ico"

    if icon_path.exists():
        root.iconbitmap(default=str(icon_path))
    try:
        if configure(root):
            app = TrialEditor(root)
            root.deiconify()
            root.mainloop()
        else:
            root.destroy()
    except Exception as error:
        messagebox.showerror("Setup failed", str(error), parent=root)
        root.destroy()
