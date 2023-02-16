# IdleKnights

Valiant knights for the game [Quest](https://github.com/nvaytet/quest), aiming to quickly and efficiently kill opposing king and storm the castle.

## Installation

Install the wheel with:

```
pip install IdleKnights[full] --extra-index-url https://pypi.simonskaal.com
```

Or build from source with:

```
pip install '.[full]'
```

If you are running in competition mode, drop the `[full]` part.

## Usage

Two example usages are provided in the `tests` folder. You can play flag mode with:

```
python tests/test_run_flag.py
```

Or King mode with:

```
python tests/test_run_king.py
```

