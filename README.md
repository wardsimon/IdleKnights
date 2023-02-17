# IdleKnights

Valiant knights for the game [Quest](https://github.com/nvaytet/quest), aiming to quickly and efficiently kill opposing king and storm the castle.

## Installation

Install the wheel with:

```
pip install --extra-index-url=https://pypi.simonskaal.com/ IdleKnights[full]
```

Or build from source with:

```
pip install '.[full]'
```

If you are running in competition mode, drop the `[full]`. A competition version of quest should already be installed.

## Usage

Two example usages are provided in the `tests` folder. You can play flag mode with:

```
python examples/test_run_flag.py
```

Or King mode with:

```
python examples/test_run_king.py
```

