import argparse
from pathlib import Path

from .config import ExperimentConfig
from .demo import generate_demo
from .experiment import ExperimentCollector, run_episode
from .policies import POLICIES


def parser():
    cli = argparse.ArgumentParser(description="True Stage One swarm laboratory")
    sub = cli.add_subparsers(dest="command")
    sub.add_parser("gui", help="open the interactive laboratory")
    run = sub.add_parser("run", help="run one measured episode")
    run.add_argument("--policy", choices=POLICIES, default="distributed-greedy")
    run.add_argument("--alpha", type=float, default=0.5)
    run.add_argument("--seed", type=int, default=7)
    run.add_argument("--reward-scheme", choices=("weak", "sparse"), default="weak")
    collect = sub.add_parser("collect", help="append a reproducible sweep and rebuild exports")
    collect.add_argument("--seeds", type=int, default=5, help="number of seeds starting at zero")
    collect.add_argument("--start-seed", type=int, default=0)
    collect.add_argument("--output", type=Path, default=Path("results"))
    demo = sub.add_parser("demo", help="generate the replacement GIF")
    demo.add_argument("--output", type=Path, default=Path("demos/stage-one-coordination.gif"))
    learn = sub.add_parser("learn", help="run the no-communication learned-policy experiment")
    learn.add_argument("--output", type=Path, default=Path("results/learned_stage_one"))
    learn.add_argument("--updates", type=int, default=30)
    learn.add_argument("--episodes-per-update", type=int, default=4)
    learn.add_argument("--train-seeds", type=int, default=3)
    learn.add_argument("--evaluation-seeds", type=int, default=5)
    learn.add_argument("--pilot", action="store_true", help="quick pipeline validation; not confirmatory evidence")
    learn.add_argument(
        "--neighbor-controls", action="store_true", help="also train hidden and shuffled-neighbor controls"
    )
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command in (None, "gui"):
        from .gui import launch

        launch()
    elif args.command == "run":
        config = ExperimentConfig(alpha=args.alpha, seed=args.seed, reward_scheme=args.reward_scheme)
        print(run_episode(config, args.policy))
    elif args.command == "collect":
        collector = ExperimentCollector(args.output, lambda text, value: print(f"[{value:6.1%}] {text}"))
        seeds = range(args.start_seed, args.start_seed + args.seeds)
        outputs = collector.collect(seeds, (0, 0.25, 0.5, 0.75, 1), tuple(POLICIES))
        for name, path in outputs.items():
            print(f"{name}: {path}")
    elif args.command == "demo":
        path, result = generate_demo(args.output)
        print(f"{path}: {result}")
    elif args.command == "learn":
        from .learned_experiment import LearnedExperiment
        from .learning import PPOBudget

        if args.pilot:
            alphas, train_seeds, evaluation_seeds = (0.0, 0.5, 1.0), range(1), range(100, 102)
            updates, episodes_per_update = min(args.updates, 3), min(args.episodes_per_update, 2)
        else:
            alphas = (0.0, 0.25, 0.5, 0.75, 1.0)
            train_seeds = range(args.train_seeds)
            evaluation_seeds = range(100, 100 + args.evaluation_seeds)
            updates, episodes_per_update = args.updates, args.episodes_per_update
        neighbor_modes = ("visible", "hidden", "shuffled") if args.neighbor_controls else ("visible",)
        experiment = LearnedExperiment(args.output, lambda text, value: print(f"[{value:6.1%}] {text}"))
        outputs = experiment.run(
            alphas=alphas,
            train_seeds=train_seeds,
            evaluation_seeds=evaluation_seeds,
            neighbor_modes=neighbor_modes,
            budget=PPOBudget(updates=updates, episodes_per_update=episodes_per_update),
        )
        for name, path in outputs.items():
            print(f"{name}: {path}")


if __name__ == "__main__":
    main()
