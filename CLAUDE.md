# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Drop Puzzle × Roguelike is a Python-based game that combines Puyo Puyo puzzle mechanics with Slay the Spire-style roguelike elements. Players chain colored puyos to deal damage to enemies while progressing through a dungeon map, collecting rewards, artifacts, and potions.

## Development Commands

### Running the Game
```bash
python main.py
```

### Testing Components
```bash
# Core system tests
python test_game_flow.py
python test_battle_integration.py
python test_dungeon_map.py

# Puzzle mechanic tests  
python test_chain.py
python test_proper_chain.py
python test_fall_speed.py

# Balance and scaling tests
python test_battle_balance.py
python test_dungeon_scaling.py
python test_reward_system.py

# Special feature tests
python test_special_puyo.py
python test_map_rules.py
```

### Environment Setup
```bash
pip install -r requirements.txt
```

## Architecture Overview

### Core Game Engine (`src/core/`)
The game uses a state-driven architecture with `GameEngine` as the central hub:

- **State Management**: Each game screen (menu, battle, map, etc.) is handled by dedicated state handlers
- **Player Data**: Unified `PlayerData` class manages HP, gold, inventory, stats, and skills
- **Game Flow**: States transition through: Menu → Dungeon Map → Battle/Event/Shop/Rest → Rewards → Repeat

### State Handlers Pattern
Each major game screen has its own handler in the respective module:
- `BattleHandler` (battle/)
- `DungeonMapHandler` (dungeon/) 
- `EventHandler` (event/)
- `RestHandler` (rest/)
- `TreasureHandler` (treasure/)
- `ShopHandler` (shop/)

### Puzzle System (`src/puzzle/`)
- **PuyoGrid**: 6x12 grid system with gravity and chain detection
- **Falling System**: Handles puyo pair dropping and player controls
- **Chain Detection**: 4+ connected same-color puyos trigger chains

### Dungeon Map System (`src/dungeon/`)
The roguelike progression uses a node-based map:
- **DungeonMap**: Generates procedural floor layouts with different node types
- **MapRenderer**: Handles visual representation with status bar overlay
- **MapHandler**: Manages navigation and node selection

### Battle System (`src/battle/`)
Integrates puzzle mechanics with combat:
- **BattleHandler**: Main battle state management
- **Enemy System**: AI opponents with intent display
- **Damage Calculation**: Converts puyo chains to damage values

### Items & Rewards (`src/items/`, `src/rewards/`)
- **Artifacts**: Permanent passive effects
- **Potions**: Consumable battle effects  
- **Reward System**: Post-battle rewards (gold, HP upgrades, items)

## Important Implementation Details

### Display System
- **Resolution**: 1920x1080 (adjustable in constants.py)
- **No Emoji**: All UI icons use ASCII characters for display compatibility
- **Font Handling**: Automatic fallback system for Japanese text support

### Energy System Removal
Energy mechanics have been completely removed from the codebase. Any energy-related code should be avoided or replaced with alternative mechanics (damage bonuses, HP effects, etc.).

### Player Data Integration
The `PlayerData` class centralizes all player state:
- HP and max HP management
- Gold and inventory tracking  
- Battle statistics
- Skill progression
- Artifact effects application

### Map Status Display
The dungeon map shows player status at the top:
- Current HP/Max HP
- Gold amount
- Special puyo count
- Potion count  
- Artifact count

### Event System
Random events show detailed before/after status changes to clearly communicate what happened to the player.

## File Organization

### Core Systems
- `src/core/constants.py` - All game constants and enums
- `src/core/game_engine.py` - Main game loop and state management
- `src/core/player_data.py` - Unified player data management

### Game Flow States
- `src/dungeon/map_handler.py` - Dungeon navigation
- `src/battle/battle_handler.py` - Combat encounters
- `src/event/event_handler.py` - Random events with choices
- `src/rest/rest_handler.py` - Healing and upgrade locations
- `src/treasure/treasure_handler.py` - Loot discovery
- `src/shop/shop_handler.py` - Item purchasing

### Supporting Systems
- `src/puzzle/puyo_grid.py` - Core puzzle mechanics
- `src/rewards/reward_system.py` - Post-encounter rewards
- `src/items/` - Artifact and potion definitions
- `src/inventory/` - Item management systems

## Common Development Patterns

### Adding New State Handlers
1. Create handler class inheriting from `StateHandler`
2. Implement required methods: `handle_event()`, `update()`, `render()`
3. Register with engine: `engine.register_state_handler(GameState.NEW_STATE, handler)`
4. Handle state transitions with `engine.change_state()`

### Map Progression
When creating new node types or handlers, ensure proper map progression by calling `dungeon_map.select_node(node_id)` after completing the encounter.

### Status Change Display
For any mechanic that modifies player stats, capture before/after values and display the changes clearly to the user.

### Error Handling
The codebase uses extensive try/catch blocks with fallback behaviors, especially for state transitions and file operations.

## Testing Strategy

The project includes comprehensive test files covering different aspects:
- Core mechanics (chain detection, falling, grid operations)
- Battle integration and balance
- Dungeon map generation and progression  
- Reward and scaling systems
- UI and input responsiveness

Run tests individually to verify specific components before making changes to related systems.