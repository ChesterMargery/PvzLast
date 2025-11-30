#!/usr/bin/env python3
"""
LLM Main Entry Point

Entry script for running the LLM-based PVZ player.

Usage:
    python llm_main.py --api-key sk-xxx
    python llm_main.py --api-key sk-xxx --debug
"""

import sys
import time
import asyncio
import argparse
from typing import Optional

# Import memory interface modules
from config import BotConfig
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

# Import LLM modules
from llm.config import LLMConfig, set_config
from llm.player import LLMPlayer


class PVZMemoryInterface:
    """
    Unified memory interface for PVZ (same as main.py)
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
        
        for i in range(10):
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
            
            self.writer.write_byte(addr + Offset.I_COLLECTED, 1)
            count += 1
        
        return count
    
    @property
    def pid(self) -> Optional[int]:
        """Get process ID"""
        return self.attacher.pid


class LLMBot:
    """
    LLM-based bot using async architecture.
    """
    
    def __init__(self, api_key: str, config: Optional[BotConfig] = None):
        self.api_key = api_key
        self.config = config or BotConfig()
        self.memory = PVZMemoryInterface()
        self.logger = get_logger()
        
        # Initialize LLM config
        llm_config = LLMConfig()
        llm_config.api_key = api_key
        set_config(llm_config)
        
        # Create LLM player
        self.player = LLMPlayer(
            config=llm_config,
            state_reader=self._read_state,
            action_executor=self._execute_action
        )
        
        # Set up callbacks
        self.player.on_action = self._on_action
        self.player.on_llm_response = self._on_llm_response
        self.player.on_emergency = self._on_emergency
        
        self.running = False
    
    def _read_state(self) -> Optional[GameState]:
        """Read game state callback"""
        if not self.memory.is_in_game():
            return None
        return self.memory.get_game_state()
    
    def _execute_action(self, action: Action) -> bool:
        """Execute action callback"""
        if action.action_type == ActionType.WAIT:
            return True
        
        if action.is_plant_action:
            return self.memory.plant(action.row, action.col, action.plant_type)
        elif action.action_type == ActionType.SHOVEL:
            return self.memory.shovel(action.row, action.col)
        elif action.action_type == ActionType.USE_COB:
            # Cob cannon requires special handling via injector
            # For now, we'd need to implement cob firing in the injector
            self.logger.warning(f"Cob cannon firing not yet implemented")
            return False
        
        return False
    
    def _on_action(self, action: Action, success: bool) -> None:
        """Action callback"""
        if success:
            try:
                plant_name = PlantType(action.plant_type).name if action.plant_type >= 0 else "N/A"
            except ValueError:
                plant_name = f"Type{action.plant_type}"
            print(f"\n[Action] {action.type_name} {plant_name} at ({action.row}, {action.col})")
            print(f"         Reason: {action.reason}")
    
    def _on_llm_response(self, response) -> None:
        """LLM response callback"""
        if response.plan:
            print(f"\n[LLM] Plan: {response.plan}")
        if response.actions:
            print(f"[LLM] Actions queued: {len(response.actions)}")
    
    def _on_emergency(self, action: Action) -> None:
        """Emergency callback"""
        print(f"\n[EMERGENCY] {action.reason}")
    
    def start(self):
        """Start the bot"""
        self._print_banner()
        
        if not self.memory.attach():
            self.logger.error("Failed to attach to PVZ process. Make sure the game is running!")
            return
        
        self.logger.info(f"Attached to PVZ (PID: {self.memory.pid})")
        self.logger.info("LLM Player Mode - Using DeepSeek V3.2-Exp")
        self.logger.info("Press Ctrl+C to stop")
        print("-" * 60)
        
        self.running = True
        
        # Run async event loop
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            print("\n")
            self.logger.info("Bot stopped by user")
            self.running = False
    
    async def _run_async(self) -> None:
        """Run async main loop"""
        # Start player
        player_task = asyncio.create_task(self.player.start())
        
        # Status display loop
        try:
            while self.running:
                if not self.memory.is_attached():
                    self.logger.error("Lost connection to PVZ")
                    break
                
                # Auto-collect items
                if self.config.auto_collect_sun:
                    self.memory.collect_all_items()
                
                # Display status
                state = self.player.state.game_state
                if state:
                    status = self._get_status_line(state)
                    status_line(status)
                else:
                    status_line("[Waiting] Not in game...")
                
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            pass
        finally:
            await self.player.stop()
    
    def _get_status_line(self, state: GameState) -> str:
        """Generate status line"""
        player_status = self.player.get_status()
        return (f"[Wave {state.wave}/{state.total_waves}] "
               f"Sun: {state.sun:4d} | "
               f"Plants: {state.plant_count:2d} | "
               f"Zombies: {state.zombie_count:2d} | "
               f"LLM calls: {player_status['llm_calls']} | "
               f"Actions: {player_status['actions_executed']}")
    
    def _print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("  PVZ LLM Player")
        print("  Powered by DeepSeek V3.2-Exp (deepseek-chat)")
        print("  Async Architecture: Fast Loop + LLM Loop")
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PVZ LLM Player")
    parser.add_argument("--api-key", required=True, help="DeepSeek API key")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-collect", action="store_true", help="Disable auto-collecting")
    args = parser.parse_args()
    
    # Create config
    config = BotConfig()
    if args.debug:
        config.debug = True
        config.log_level = 0
    if args.no_collect:
        config.auto_collect_sun = False
    
    # Start bot
    bot = LLMBot(api_key=args.api_key, config=config)
    bot.start()


if __name__ == "__main__":
    main()
