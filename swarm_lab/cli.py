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


if __name__ == "__main__":
    main()
