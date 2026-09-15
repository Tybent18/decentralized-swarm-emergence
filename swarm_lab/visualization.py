import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

PALETTE = ["#38bdf8", "#a78bfa", "#34d399", "#fb923c", "#f472b6", "#facc15", "#22d3ee", "#c084fc"]


def _font(size, bold=False):
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation2/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_world(snapshot, grid_size, size=(900, 620), title="LIVE SWARM", subtitle="decentralized baseline"):
    width, height = size
    image = Image.new("RGB", size, "#07111f")
    draw = ImageDraw.Draw(image)
    panel = (28, 74, width - 28, height - 28)
    draw.rounded_rectangle(panel, 24, fill="#0d1b2d", outline="#1e3a56", width=2)
    draw.text((52, 26), title, font=_font(25, True), fill="#e2e8f0")
    draw.text((width - 52, 31), subtitle.upper(), anchor="ra", font=_font(12, True), fill="#38bdf8")
    board_size = min(height - 128, width - 330)
    left, top = 56, 98
    cell = board_size / grid_size
    draw.rounded_rectangle((left - 10, top - 10, left + board_size + 10, top + board_size + 10), 18, fill="#071525")
    for i in range(grid_size + 1):
        x, y = left + i * cell, top + i * cell
        draw.line((x, top, x, top + board_size), fill="#17324b", width=1)
        draw.line((left, y, left + board_size, y), fill="#17324b", width=1)
    for tx, ty in snapshot["targets"]:
        cx, cy = left + (tx + 0.5) * cell, top + (ty + 0.5) * cell
        radius = max(5, cell * 0.24)
        draw.ellipse((cx - radius * 1.7, cy - radius * 1.7, cx + radius * 1.7, cy + radius * 1.7), fill="#123f36")
        draw.polygon([(cx, cy - radius), (cx + radius, cy), (cx, cy + radius), (cx - radius, cy)], fill="#34d399")
    for index, (ax, ay) in enumerate(snapshot["agents"]):
        cx, cy = left + (ax + 0.5) * cell, top + (ay + 0.5) * cell
        radius = max(7, cell * 0.34)
        color = PALETTE[index % len(PALETTE)]
        draw.ellipse((cx - radius * 1.35, cy - radius * 1.35, cx + radius * 1.35, cy + radius * 1.35), fill="#142a41")
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color, outline="#dbeafe", width=2)
        draw.ellipse((cx - radius * 0.25, cy - radius * 0.25, cx + radius * 0.25, cy + radius * 0.25), fill="#07111f")
    hud_x = left + board_size + 34
    draw.text((hud_x, top), "TELEMETRY", font=_font(15, True), fill="#94a3b8")
    telemetry = [("STEP", snapshot["step"]), ("AGENTS", len(snapshot["agents"])), ("TARGETS", len(snapshot["targets"]))]
    for row, (label, value) in enumerate(telemetry):
        y = top + 38 + row * 74
        draw.rounded_rectangle((hud_x, y, width - 54, y + 58), 12, fill="#12253b")
        draw.text((hud_x + 16, y + 10), label, font=_font(11, True), fill="#64748b")
        draw.text((width - 72, y + 28), str(value), anchor="rm", font=_font(23, True), fill="#e2e8f0")
    draw.text((hud_x, top + 285), "STATUS", font=_font(11, True), fill="#64748b")
    status = "COMPLETE" if not snapshot["targets"] else "SEARCHING"
    draw.text((hud_x, top + 315), status, font=_font(19, True), fill="#34d399" if status == "COMPLETE" else "#38bdf8")
    draw.text((hud_x, height - 72), "TRUE STAGE ONE", font=_font(11, True), fill="#64748b")
    return image


def draw_dashboard(snapshot, grid_size, policy, progress=0.0):
    image = Image.new("RGB", (1240, 790), "#07111f")
    draw = ImageDraw.Draw(image)
    draw.text((30, 23), "SWARM LAB", font=_font(26, True), fill="#e2e8f0")
    draw.text((215, 34), "TRUE STAGE ONE", font=_font(11, True), fill="#38bdf8")
    draw.rounded_rectangle((28, 78, 310, 760), 20, fill="#0d1b2d")
    draw.text((52, 106), "EXPERIMENT CONTROL", font=_font(11, True), fill="#94a3b8")
    fields = (("POLICY", policy), ("REWARD ALPHA", "0.50"), ("SEED", "7"), ("AGENTS", str(len(snapshot["agents"]))))
    for index, (label, value) in enumerate(fields):
        y = 154 + index * 76
        draw.text((52, y), label, font=_font(9, True), fill="#64748b")
        draw.rounded_rectangle((48, y + 18, 290, y + 60), 9, fill="#12253b")
        draw.text((64, y + 39), value, anchor="lm", font=_font(13, True), fill="#e2e8f0")
    y = 474
    draw.rounded_rectangle((48, y, 290, y + 10), 5, fill="#1e344c")
    draw.rounded_rectangle((48, y, 48 + 242 * progress, y + 10), 5, fill="#38bdf8")
    for label, color, top in (
        ("RUN LIVE EPISODE", "#38bdf8", 510),
        ("COLLECT + EXPORT", "#34d399", 562),
        ("STOP", "#fb7185", 614),
        ("OPEN RESULTS", "#12253b", 666),
    ):
        draw.rounded_rectangle((48, top, 290, top + 42), 9, fill=color)
        draw.text((169, top + 21), label, anchor="mm", font=_font(11, True), fill="#04111e" if top < 614 else "#e2e8f0")
    world = draw_world(snapshot, grid_size, (890, 682), title="LIVE SWARM", subtitle=policy)
    image.paste(world, (328, 78))
    return image


def export_charts(rows, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    numeric = (
        "alpha",
        "completion_rate",
        "coordination_efficiency",
        "collision_rate",
        "spatial_order",
        "steps",
        "team_return",
    )
    rows = [{**row, **{key: float(row[key]) for key in numeric}} for row in rows]
    policies = sorted({r["policy"] for r in rows})
    paths = []
    style = {
        "figure.facecolor": "#07111f",
        "axes.facecolor": "#0d1b2d",
        "axes.edgecolor": "#334155",
        "axes.labelcolor": "#cbd5e1",
        "xtick.color": "#94a3b8",
        "ytick.color": "#94a3b8",
        "text.color": "#e2e8f0",
        "grid.color": "#263d55",
    }
    with plt.rc_context(style):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
        for index, policy in enumerate(policies):
            grouped = {}
            for row in (r for r in rows if r["policy"] == policy):
                grouped.setdefault(row["alpha"], []).append(row)
            xs = sorted(grouped)
            completion = [sum(x["completion_rate"] for x in grouped[a]) / len(grouped[a]) for a in xs]
            reward = [sum(x["team_return"] for x in grouped[a]) / len(grouped[a]) for a in xs]
            color = PALETTE[index % len(PALETTE)]
            axes[0].plot(xs, completion, marker="o", label=policy, color=color)
            axes[1].plot(xs, reward, marker="o", label=policy, color=color)
        axes[0].set(
            title="Baseline completion by reward topology", xlabel="alpha", ylabel="completion rate", ylim=(-0.03, 1.03)
        )
        axes[1].set(title="Recorded team return", xlabel="alpha", ylabel="mean return")
        for axis in axes:
            axis.grid(alpha=0.45)
            axis.legend(frameon=False, fontsize=8)
        path = output_dir / "reward_topology_baselines.png"
        fig.savefig(path, dpi=170)
        plt.close(fig)
        paths.append(path)
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), constrained_layout=True)
        for axis, (metric, label) in zip(
            axes, (("steps", "Steps"), ("collision_rate", "Collision rate"), ("spatial_order", "Spatial order"))
        ):
            data = [[r[metric] for r in rows if r["policy"] == p] for p in policies]
            boxes = axis.boxplot(data, tick_labels=policies, patch_artist=True)
            for index, box in enumerate(boxes["boxes"]):
                box.set_facecolor(PALETTE[index % len(PALETTE)])
                box.set_alpha(0.7)
            axis.set_title(label)
            axis.tick_params(axis="x", rotation=25)
            axis.grid(axis="y", alpha=0.4)
        path = output_dir / "behavioral_metrics.png"
        fig.savefig(path, dpi=170)
        plt.close(fig)
        paths.append(path)
    return paths


def load_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def export_reference_visuals(snapshots, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    agent_count = len(snapshots[0]["agents"])
    trajectories = [[snapshot["agents"][i] for snapshot in snapshots] for i in range(agent_count)]
    grid_size = max(max(max(x, y) for x, y in snapshot["agents"]) for snapshot in snapshots) + 1
    heat = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    for trajectory in trajectories:
        for x, y in trajectory:
            heat[y][x] += 1
    style = {
        "figure.facecolor": "#07111f",
        "axes.facecolor": "#0d1b2d",
        "axes.edgecolor": "#334155",
        "axes.labelcolor": "#cbd5e1",
        "xtick.color": "#94a3b8",
        "ytick.color": "#94a3b8",
        "text.color": "#e2e8f0",
    }
    with plt.rc_context(style):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 5), constrained_layout=True)
        for index, trajectory in enumerate(trajectories):
            xs, ys = zip(*trajectory)
            axes[0].plot(xs, ys, color=PALETTE[index % len(PALETTE)], alpha=0.8, linewidth=1.6)
            axes[0].scatter(xs[-1], ys[-1], color=PALETTE[index % len(PALETTE)], s=32)
        axes[0].invert_yaxis()
        axes[0].set(title="Reference trajectory overlay", xlabel="x", ylabel="y")
        image = axes[1].imshow(heat, cmap="viridis", interpolation="nearest")
        axes[1].set(title="Agent visitation heatmap", xlabel="x", ylabel="y")
        fig.colorbar(image, ax=axes[1], label="visits", shrink=0.82)
        path = output_dir / "trajectory_and_heatmap.png"
        fig.savefig(path, dpi=170)
        plt.close(fig)
    return path
