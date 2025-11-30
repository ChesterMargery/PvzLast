# PVZ Optimal Algorithm Framework

A modular, extensible framework for Plants vs. Zombies game automation based on [AsmVsZombies (AVZ)](https://github.com/vector-wlc/AsmVsZombies) reverse engineering research.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for data, memory operations, game state, judgment, and decision making
- **AVZ-Based Data**: All game constants, plant/zombie data, and memory offsets sourced from authoritative AVZ research
- **Precise Judgment**: Accurate collision detection, damage calculation, and movement prediction
- **Extensible Engine**: Decision engine interface supporting rule-based, MCTS, and reinforcement learning optimizers
- **ASM Injection**: Direct game function calls for 100% reliable planting operations

## Project Structure

```
PvzLast/
├── README.md               # This file
├── main.py                 # Entry point
├── config.py               # Configuration settings
├── optimal_bot.py          # Original monolithic bot (reference)
│
├── data/                   # Game data from AVZ
│   ├── __init__.py
│   ├── constants.py        # Time constants, game mechanics
│   ├── plants.py           # Plant types, stats, collision boxes
│   ├── zombies.py          # Zombie types, HP, speeds
│   └── offsets.py          # Memory structure offsets
│
├── memory/                 # Memory operations
│   ├── __init__.py
│   ├── process.py          # Process attachment
│   ├── reader.py           # Memory reading
│   ├── writer.py           # Memory writing
│   └── injector.py         # ASM code injection
│
├── game/                   # Game state representation
│   ├── __init__.py
│   ├── state.py            # Complete game state
│   ├── zombie.py           # Zombie entity class
│   ├── plant.py            # Plant entity class
│   └── grid.py             # Grid representation
│
├── judge/                  # Damage judgment (from AVZ judge.h)
│   ├── __init__.py
│   ├── collision.py        # Hit detection algorithms
│   ├── damage.py           # Damage calculation
│   └── prediction.py       # Movement prediction
│
├── engine/                 # Decision engine
│   ├── __init__.py
│   ├── action.py           # Action definitions
│   ├── analyzer.py         # Threat/resource analysis
│   ├── strategy.py         # Strategy planning
│   └── optimizer.py        # Action optimization
│
└── utils/                  # Utilities
    ├── __init__.py
    └── logger.py           # Logging system
```

## Requirements

- Windows OS (for process memory access)
- Python 3.7+
- Plants vs. Zombies game (running)

## Usage

### Basic Usage

```bash
# Run with default settings
python main.py

# Run with debug output
python main.py --debug

# Run without auto-planting (observation mode)
python main.py --no-plant

# Run without auto-collecting sun
python main.py --no-collect
```

### Programmatic Usage

```python
from main import OptimalBot
from config import BotConfig

# Create custom config
config = BotConfig()
config.auto_plant = True
config.auto_collect_sun = True
config.target_sun_plants = 10

# Create and start bot
bot = OptimalBot(config)
bot.start()
```

## Key Constants (from AVZ)

### Time Constants (centiseconds)

| Constant | Value | Description |
|----------|-------|-------------|
| `COB_FLY_TIME` | 373 | Cob cannon flight time |
| `COB_RECOVER_TIME` | 3475 | Cob cannon reload time |
| `CHERRY_DELAY` | 100 | Cherry bomb explosion delay |
| `ICE_DURATION` | 400 | Ice-shroom freeze duration |
| `SLOW_DURATION` | 1000 | Snow pea slow duration |

### Zombie Data

| Zombie | Body HP | Accessory HP | Base Speed |
|--------|---------|--------------|------------|
| Normal | 200 | 0 | 0.23 px/cs |
| Conehead | 200 | 370 | 0.23 px/cs |
| Buckethead | 200 | 1100 | 0.23 px/cs |
| Football | 1600 | 0 | 0.68 px/cs |
| Gargantuar | 3000 | 0 | 0.15 px/cs |
| Giga Gargantuar | 6000 | 0 | 0.15 px/cs |

### Collision Boxes

| Plant | Hit Range | Explode Range |
|-------|-----------|---------------|
| Default | (30, 50) | (-50, 10) |
| Tall-nut | (30, 60) | (-50, 30) |
| Pumpkin | (20, 80) | (-60, 40) |
| Cob Cannon | (20, 120) | (-60, 80) |

## Architecture

### Decision Engine

The decision engine follows a hierarchical design:

1. **Analyzer** - Evaluates game state (threats, resources, defense)
2. **Strategy Planner** - Determines high-level goals (economy, defense, emergency)
3. **Action Generator** - Creates candidate actions
4. **Optimizer** - Scores and selects best action

### Extensibility

The `BaseOptimizer` abstract class allows implementing custom optimization algorithms:

```python
from engine.optimizer import BaseOptimizer

class MyCustomOptimizer(BaseOptimizer):
    def get_best_action(self, state):
        # Your optimization logic
        pass
    
    def evaluate_action(self, state, action):
        # Your evaluation logic
        pass
```

Planned optimizers:
- `MCTSOptimizer` - Monte Carlo Tree Search
- `RLOptimizer` - Reinforcement Learning (neural network policy)

## References

- [AsmVsZombies](https://github.com/vector-wlc/AsmVsZombies) - Primary data source
- `inc/avz_pvz_struct.h` - Memory structure definitions
- `tutorial/scripts/liang_yi/judge.h` - Damage judgment logic
- `src/avz_cob_manager.cpp` - Cob cannon management

## License

MIT License

## Acknowledgments

Special thanks to the AsmVsZombies community for their extensive reverse engineering work.