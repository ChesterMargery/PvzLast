"""
PVZ Optimal Algorithm Bot
Main entry point

Based on AsmVsZombies (AVZ) reverse engineering research.
Provides an extensible framework for optimal PVZ gameplay automation.

Usage:
    python main.py [--debug] [--no-plant] [--no-collect]

Features:
    - Modular architecture based on AVZ data
    - Precise damage judgment and collision detection
    - Zombie movement prediction
    - Extensible decision engine interface
    - ASM injection for reliable plant operations
"""

import sys
import time
import argparse
from typing import Optional

# Import modules
from config import BotConfig, load_config
from utils.logger import Logger, LogLevel, get_logger, status_line

# Import data modules
from data.plants import PlantType, PLANT_COST
from data.zombies import ZombieType
from data.offsets import Offset

# Import memory modules
from memory.process import ProcessAttacher
from memory.reader import MemoryReader
from memory.writer import MemoryWriter
from memory.injector import AsmInjector

# Import game state modules
from game.state import GameState, SeedInfo
from game.zombie import ZombieInfo
from game.plant import PlantInfo
from game.grid import Grid

# Import engine modules
from engine.action import Action, ActionType
from engine.analyzer import ThreatAnalyzer, ResourceAnalyzer
from engine.strategy import StrategyPlanner
from engine.optimizer import ActionOptimizer


class PVZMemoryInterface:
    """
    Unified memory interface for PVZ
    
    Combines process attachment, reading, writing, and ASM injection.
    """
    
    def __init__(self):
        self.attacher = ProcessAttacher()
        self.reader: Optional[MemoryReader] = None
        self.writer: Optional[MemoryWriter] = None
        self.injector: Optional[AsmInjector] = None
        self.logger = get_logger()
    
    def attach(self) -> bool:
        """Attach to PVZ process"""
        if not self.attacher.attach():
            return False
        
        # Initialize components
        kernel32 = self.attacher.kernel32
        handle = self.attacher.handle
        
        self.reader = MemoryReader(kernel32, handle)
        self.writer = MemoryWriter(kernel32, handle)
        self.injector = AsmInjector(kernel32, handle, self.reader)
        
        return True
    
    def is_attached(self) -> bool:
        """Check if attached to process"""
        return self.attacher.is_attached()
    
    def is_in_game(self) -> bool:
        """Check if in game"""
        if not self.reader:
            return False
        return self.reader.is_in_game()
    
    def get_game_state(self) -> Optional[GameState]:
        """Read complete game state"""
        if not self.reader or not self.reader.is_in_game():
            return None
        
        board = self.reader.get_board()
        if board == 0:
            return None
        
        # Read basic info
        sun = self.reader.get_sun()
        wave = self.reader.get_wave()
        total_waves = self.reader.get_total_waves()
        game_clock = self.reader.get_game_clock()
        scene = self.reader.get_scene()
        refresh_cd = self.reader.read_int(board + Offset.REFRESH_COUNTDOWN)
        huge_wave_cd = self.reader.read_int(board + Offset.HUGE_WAVE_COUNTDOWN)
        
        # Read zombies
        zombies = self._read_zombies(board)
        
        # Read plants and build grid
        plants, plant_grid = self._read_plants(board)
        
        # Read seeds
        seeds = self._read_seeds(board)
        
        return GameState(
            sun=sun,
            wave=wave,
            total_waves=total_waves,
            game_clock=game_clock,
            scene=scene,
            refresh_countdown=refresh_cd,
            huge_wave_countdown=huge_wave_cd,
            zombies=zombies,
            plants=plants,
            seeds=seeds,
            plant_grid=plant_grid,
        )
    
    def _read_zombies(self, board: int) -> list:
        """Read all zombies from memory"""
        zombies = []
        zombie_array = self.reader.read_int(board + Offset.ZOMBIE_ARRAY)
        zombie_max = self.reader.read_int(board + Offset.ZOMBIE_COUNT_MAX)
        
        for i in range(min(zombie_max, 200)):
            addr = zombie_array + i * Offset.ZOMBIE_SIZE
            
            if self.reader.read_byte(addr + Offset.Z_DEAD):
                continue
            
            zombies.append(ZombieInfo(
                index=i,
                row=self.reader.read_int(addr + Offset.Z_ROW),
                x=self.reader.read_float(addr + Offset.Z_X),
                y=self.reader.read_float(addr + Offset.Z_Y),
                type=self.reader.read_int(addr + Offset.Z_TYPE),
                hp=self.reader.read_int(addr + Offset.Z_HP),
                hp_max=self.reader.read_int(addr + Offset.Z_HP_MAX),
                accessory_hp=self.reader.read_int(addr + Offset.Z_ACCESSORY_HP_1),
                state=self.reader.read_int(addr + Offset.Z_STATE),
                speed=self.reader.read_float(addr + Offset.Z_SPEED),
                slow_countdown=self.reader.read_int(addr + Offset.Z_SLOW_COUNTDOWN),
                freeze_countdown=self.reader.read_int(addr + Offset.Z_FREEZE_COUNTDOWN),
                butter_countdown=self.reader.read_int(addr + Offset.Z_BUTTER_COUNTDOWN),
                at_wave=self.reader.read_int(addr + Offset.Z_AT_WAVE),
            ))
        
        return zombies
    
    def _read_plants(self, board: int) -> tuple:
        """Read all plants and build grid"""
        plants = []
        grid = Grid()
        
        plant_array = self.reader.read_int(board + Offset.PLANT_ARRAY)
        plant_max = self.reader.read_int(board + Offset.PLANT_COUNT_MAX)
        
        for i in range(min(plant_max, 200)):
            addr = plant_array + i * Offset.PLANT_SIZE
            
            if self.reader.read_byte(addr + Offset.P_DEAD):
                continue
            
            row = self.reader.read_int(addr + Offset.P_ROW)
            col = self.reader.read_int(addr + Offset.P_COL)
            plant_type = self.reader.read_int(addr + Offset.P_TYPE)
            
            plant = PlantInfo(
                index=i,
                row=row,
                col=col,
                type=plant_type,
                hp=self.reader.read_int(addr + Offset.P_HP),
                hp_max=self.reader.read_int(addr + Offset.P_HP_MAX),
                state=self.reader.read_int(addr + Offset.P_STATE),
                shoot_countdown=self.reader.read_int(addr + Offset.P_SHOOT_COUNTDOWN),
                effective=self.reader.read_int(addr + Offset.P_EFFECTIVE) != 0,
                pumpkin_hp=self.reader.read_int(addr + Offset.P_PUMPKIN_HP),
                cob_countdown=self.reader.read_int(addr + Offset.P_COB_COUNTDOWN) if plant_type == PlantType.COBCANNON else 0,
                cob_ready=self.reader.read_bool(addr + Offset.P_COB_READY) if plant_type == PlantType.COBCANNON else False,
            )
            
            plants.append(plant)
            grid.set(row, col, plant)
        
        return plants, grid
    
    def _read_seeds(self, board: int) -> list:
        """Read seed cards"""
        seeds = []
        seed_array = self.reader.read_int(board + Offset.SEED_ARRAY)
        
        for i in range(10):  # 10 card slots
            addr = seed_array + i * Offset.SEED_SIZE
            seeds.append(SeedInfo(
                index=i,
                type=self.reader.read_int(addr + Offset.S_TYPE),
                recharge_countdown=self.reader.read_int(addr + Offset.S_RECHARGE_COUNTDOWN),
                recharge_time=self.reader.read_int(addr + Offset.S_RECHARGE_TIME),
                usable=self.reader.read_byte(addr + Offset.S_USABLE) != 0,
                imitator_type=self.reader.read_int(addr + Offset.S_IMITATOR_TYPE),
            ))
        
        return seeds
    
    def plant(self, row: int, col: int, plant_type: int) -> bool:
        """Plant at position"""
        if not self.injector:
            return False
        return self.injector.plant(row, col, plant_type)
    
    def shovel(self, row: int, col: int) -> bool:
        """Remove plant at position"""
        if not self.injector:
            return False
        return self.injector.shovel(row, col)
    
    def collect_all_items(self) -> int:
        """Collect all items (sun, coins)"""
        if not self.reader or not self.writer:
            return 0
        
        board = self.reader.get_board()
        if board == 0:
            return 0
        
        count = 0
        item_array = self.reader.read_int(board + Offset.ITEM_ARRAY)
        item_max = self.reader.read_int(board + Offset.ITEM_COUNT_MAX)
        
        for i in range(min(item_max, 100)):
            addr = item_array + i * Offset.ITEM_SIZE
            
            if self.reader.read_byte(addr + Offset.I_DISAPPEARED):
                continue
            if self.reader.read_byte(addr + Offset.I_COLLECTED):
                continue
            
            # Set as collected
            self.writer.write_byte(addr + Offset.I_COLLECTED, 1)
            count += 1
        
        return count
    
    @property
    def pid(self) -> Optional[int]:
        """Get process ID"""
        return self.attacher.pid


class OptimalBot:
    """
    Main bot class
    
    Coordinates memory interface, game state reading, decision making,
    and action execution.
    """
    
    def __init__(self, config: Optional[BotConfig] = None):
        self.config = config or BotConfig()
        self.memory = PVZMemoryInterface()
        self.optimizer = ActionOptimizer()
        self.logger = get_logger()
        
        self.running = False
        self.last_action_time = 0.0
    
    def start(self):
        """Start the bot"""
        self._print_banner()
        
        if not self.memory.attach():
            self.logger.error("Failed to attach to PVZ process. Make sure the game is running!")
            return
        
        self.logger.info(f"Attached to PVZ (PID: {self.memory.pid})")
        self.logger.info(f"Auto-plant: {'ON' if self.config.auto_plant else 'OFF'}")
        self.logger.info(f"Auto-collect: {'ON' if self.config.auto_collect_sun else 'OFF'}")
        self.logger.info("Press Ctrl+C to stop")
        print("-" * 60)
        
        self.running = True
        self._run_loop()
    
    def _print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("  PVZ Optimal Algorithm Bot")
        print("  Based on AsmVsZombies Framework")
        print("  Modular Architecture with Extensible Decision Engine")
        print("=" * 60)
    
    def _run_loop(self):
        """Main loop"""
        try:
            while self.running:
                # Get game state
                state = self.memory.get_game_state()
                
                if state is None:
                    status_line("[Waiting] Not in game...")
                    time.sleep(0.5)
                    continue
                
                # Auto-collect items
                if self.config.auto_collect_sun:
                    self.memory.collect_all_items()
                
                # Display status
                self._display_status(state)
                
                # Get and execute action
                if self.config.auto_plant:
                    self._process_action(state)
                
                time.sleep(self.config.refresh_rate)
                
        except KeyboardInterrupt:
            print("\n")
            self.logger.info("Bot stopped by user")
            self.running = False
    
    def _display_status(self, state: GameState):
        """Display current game status"""
        status = (f"[Wave {state.wave}/{state.total_waves}] "
                 f"Sun: {state.sun:4d} | "
                 f"Plants: {state.plant_count:2d} | "
                 f"Zombies: {state.zombie_count:2d} | "
                 f"Clock: {state.game_clock}")
        status_line(status)
    
    def _process_action(self, state: GameState):
        """Process and execute actions"""
        current_time = time.time()
        if current_time - self.last_action_time < self.config.action_interval:
            return
        
        # Get best action from optimizer
        action = self.optimizer.get_best_action(state)
        
        if action and not action.is_wait:
            if self._execute_action(action, state):
                self.last_action_time = current_time
    
    def _execute_action(self, action: Action, state: GameState) -> bool:
        """Execute an action"""
        if action.action_type == ActionType.WAIT:
            return False
        
        if action.is_plant_action:
            # Validate
            cost = action.sun_cost
            if state.sun < cost:
                return False
            
            seed = state.get_seed_by_type(action.plant_type)
            if not seed or not seed.usable:
                return False
            
            # Execute
            success = self.memory.plant(action.row, action.col, action.plant_type)
            if success:
                try:
                    plant_name = PlantType(action.plant_type).name
                except ValueError:
                    plant_name = f"Type{action.plant_type}"
                print(f"\n[Action] Planted {plant_name} at ({action.row}, {action.col})")
                print(f"         Reason: {action.reason}")
            return success
        
        elif action.action_type == ActionType.SHOVEL:
            return self.memory.shovel(action.row, action.col)
        
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PVZ Optimal Algorithm Bot")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-plant", action="store_true", help="Disable auto-planting")
    parser.add_argument("--no-collect", action="store_true", help="Disable auto-collecting")
    args = parser.parse_args()
    
    # Create config
    config = BotConfig()
    if args.debug:
        config.debug = True
        config.log_level = 0
    if args.no_plant:
        config.auto_plant = False
    if args.no_collect:
        config.auto_collect_sun = False
    
    # Start bot
    bot = OptimalBot(config)
    bot.start()


if __name__ == "__main__":
    main()
