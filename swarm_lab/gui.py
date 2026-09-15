import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import ImageTk

from .config import ExperimentConfig
from .demo import generate_demo
from .experiment import ExperimentCollector, run_episode
from .policies import POLICIES
from .visualization import draw_world


class SwarmLabApp:
    BG, PANEL, FIELD, TEXT, MUTED, ACCENT = "#07111f", "#0d1b2d", "#12253b", "#e2e8f0", "#94a3b8", "#38bdf8"

    def __init__(self, root):
        self.root = root
        self.root.title("Swarm Lab - True Stage One")
        self.root.geometry("1240x790")
        self.root.configure(bg=self.BG)
        self.cancel_event = threading.Event()
        self.events = queue.Queue()
        self.image_ref = None
        self.busy = False
        self.latest_output = Path("results")
        self._build()
        self._show_initial()
        self.root.after(50, self._drain)

    def _build(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=28, pady=(22, 12))
        tk.Label(header, text="SWARM LAB", bg=self.BG, fg=self.TEXT, font=("Arial", 24, "bold")).pack(side="left")
        tk.Label(header, text="TRUE STAGE ONE", bg=self.BG, fg=self.ACCENT, font=("Arial", 11, "bold")).pack(
            side="left", padx=16
        )
        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        controls = tk.Frame(body, bg=self.PANEL, width=290)
        controls.pack(side="left", fill="y", padx=(0, 16))
        controls.pack_propagate(False)
        self.viewer = tk.Label(body, bg=self.PANEL)
        self.viewer.pack(side="left", fill="both", expand=True)
        tk.Label(controls, text="EXPERIMENT CONTROL", bg=self.PANEL, fg=self.MUTED, font=("Arial", 10, "bold")).pack(
            anchor="w", padx=20, pady=(24, 14)
        )
        self.policy = tk.StringVar(value="distributed-greedy")
        self.alpha = tk.DoubleVar(value=0.5)
        self.seed = tk.IntVar(value=7)
        self.agents = tk.IntVar(value=6)
        self._field(
            controls,
            "Policy",
            ttk.Combobox(controls, textvariable=self.policy, values=list(POLICIES), state="readonly"),
        )
        self._field(
            controls,
            "Reward alpha",
            tk.Scale(
                controls,
                variable=self.alpha,
                from_=0,
                to=1,
                resolution=0.25,
                orient="horizontal",
                bg=self.PANEL,
                fg=self.TEXT,
                highlightthickness=0,
                troughcolor=self.FIELD,
            ),
        )
        self._field(
            controls,
            "Seed",
            tk.Spinbox(
                controls,
                from_=0,
                to=99999,
                textvariable=self.seed,
                bg=self.FIELD,
                fg=self.TEXT,
                buttonbackground=self.FIELD,
            ),
        )
        self._field(
            controls,
            "Agents",
            tk.Spinbox(
                controls,
                from_=2,
                to=20,
                textvariable=self.agents,
                bg=self.FIELD,
                fg=self.TEXT,
                buttonbackground=self.FIELD,
            ),
        )
        self.progress = ttk.Progressbar(controls, mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=(18, 8))
        self.status = tk.StringVar(value="Ready - no experiment running")
        tk.Label(
            controls,
            textvariable=self.status,
            wraplength=245,
            justify="left",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Arial", 9),
        ).pack(anchor="w", padx=20, pady=(0, 16))
        self._button(controls, "RUN LIVE EPISODE", self.run_live, self.ACCENT, "#04111e")
        self._button(controls, "COLLECT + EXPORT", self.collect, "#34d399", "#04111e")
        self._button(controls, "STOP", self.stop, "#fb7185", "#ffffff")
        self._button(controls, "OPEN RESULTS", self.open_results, self.FIELD, self.TEXT)
        tk.Label(
            controls,
            text=(
                "Collect runs 4 policies x 5 alpha values x 5 seeds, appends raw CSV, "
                "then rebuilds summaries and charts."
            ),
            wraplength=245,
            justify="left",
            bg=self.PANEL,
            fg="#64748b",
            font=("Arial", 8),
        ).pack(anchor="w", padx=20, pady=18)

    def _field(self, parent, label, widget):
        tk.Label(parent, text=label.upper(), bg=self.PANEL, fg=self.MUTED, font=("Arial", 8, "bold")).pack(
            anchor="w", padx=20, pady=(8, 5)
        )
        widget.pack(fill="x", padx=20)

    def _button(self, parent, text, command, bg, fg):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            pady=9,
        ).pack(fill="x", padx=20, pady=4)

    def _config(self):
        return ExperimentConfig(n_agents=self.agents.get(), alpha=self.alpha.get(), seed=self.seed.get())

    def _show_initial(self):
        from .world import SwarmWorld

        self._render(SwarmWorld(n_agents=self.agents.get(), seed=self.seed.get()).snapshot(), "ready")

    def _render(self, snapshot, subtitle):
        self.image_ref = ImageTk.PhotoImage(draw_world(snapshot, 16, size=(880, 680), subtitle=subtitle))
        self.viewer.configure(image=self.image_ref)

    def _launch(self, target):
        if self.busy:
            self.status.set("An experiment is already running")
            return
        self.busy = True
        self.cancel_event.clear()
        self.progress["value"] = 0
        threading.Thread(target=target, daemon=True).start()

    def run_live(self):
        config, policy = self._config(), self.policy.get()

        def task():
            try:

                def frame(snapshot, _event):
                    self.events.put(("frame", snapshot, policy))
                    self.cancel_event.wait(0.045)

                result = run_episode(config, policy, frame, self.cancel_event)
                self.events.put(
                    (
                        "done",
                        f"Episode complete: {result.targets_collected}/{result.n_targets} targets "
                        f"in {result.steps} steps",
                    )
                )
            except InterruptedError:
                self.events.put(("done", "Episode stopped safely"))
            except Exception as exc:
                self.events.put(("error", str(exc)))

        self.status.set("Running live episode...")
        self._launch(task)

    def collect(self):
        base = self._config()

        def task():
            try:
                collector = ExperimentCollector(
                    self.latest_output,
                    lambda text, value: self.events.put(("progress", text, value)),
                    self.cancel_event,
                )
                outputs = collector.collect(range(5), (0, 0.25, 0.5, 0.75, 1), tuple(POLICIES), base)
                generate_demo("demos/stage-one-coordination.gif")
                self.events.put(("done", f"Exports rebuilt: {outputs['manifest']}"))
            except InterruptedError:
                self.events.put(("done", "Collection stopped before the batch commit"))
            except Exception as exc:
                self.events.put(("error", str(exc)))

        self.status.set("Collecting reproducible baseline evidence...")
        self._launch(task)

    def stop(self):
        self.cancel_event.set()
        self.status.set("Stopping at the next safe step...")

    def open_results(self):
        self.latest_output.mkdir(exist_ok=True)
        try:
            os.startfile(self.latest_output.resolve())
        except AttributeError:
            os.system(f'xdg-open "{self.latest_output.resolve()}" >/dev/null 2>&1 &')

    def _drain(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "frame":
                    self._render(event[1], event[2])
                elif event[0] == "progress":
                    self.status.set(event[1])
                    self.progress["value"] = event[2] * 100
                elif event[0] == "done":
                    self.busy = False
                    self.status.set(event[1])
                    self.progress["value"] = 100
                elif event[0] == "error":
                    self.busy = False
                    self.status.set("Experiment failed")
                    messagebox.showerror("Swarm Lab", event[1])
        except queue.Empty:
            pass
        self.root.after(50, self._drain)


def launch():
    root = tk.Tk()
    SwarmLabApp(root)
    root.mainloop()
