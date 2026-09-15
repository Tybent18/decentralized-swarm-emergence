# True Stage One verification record

Test date: 2026-09-15

## Legacy baseline

The original documented installation failed before simulation startup because `requirements.txt` contained the invalid requirement line `later:`. The top-level program also duplicated world state instead of using the PettingZoo environment, and no automated correctness suite existed.

| Check | Legacy result |
| --- | --- |
| `pip install -r requirements.txt` | Failed |
| Automated tests | None |
| Fixed observation space | No |
| Literal per-agent local credit | No |
| One-command chart export | No |

## Stage One verification

| Check | Result |
| --- | --- |
| Clean editable installation | Passed |
| Ruff static analysis | Passed |
| Pytest suite | 8/8 passed |
| PettingZoo parallel API test | Passed |
| Deterministic repeat | Passed |
| Frozen evidence batch | 200 rows exported |
| Summary and manifest | Exported |
| Publication chart set | Three PNGs exported |
| Replacement demos | Two GIFs exported |

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest -q
python main.py collect --seeds 10 --output results/reproduction
```
