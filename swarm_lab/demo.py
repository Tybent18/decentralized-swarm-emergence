from pathlib import Path

from .config import ExperimentConfig
from .experiment import run_episode
from .visualization import draw_dashboard


def generate_demo(path="demos/stage-one-emergence.gif", policy="distributed-greedy", seed=7):
    frames = []
    config = ExperimentConfig(seed=seed, max_steps=90)

    def capture(snapshot, _event):
        if snapshot["step"] % 2 == 0 or not snapshot["targets"]:
            progress = min(snapshot["step"] / config.max_steps, 1.0)
            frames.append(draw_dashboard(snapshot, config.grid_size, policy, progress))

    result = run_episode(config, policy, frame_callback=capture)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=95, loop=0, optimize=True)
    return target, result


def main():
    for policy, name in (("random", "stage-one-random.gif"), ("distributed-greedy", "stage-one-coordination.gif")):
        path, result = generate_demo(Path("demos") / name, policy)
        print(f"{path}: success={result.success}, steps={result.steps}")


if __name__ == "__main__":
    main()
