"""
Wave Spawner for PVZ Simulator
Manages zombie wave spawning based on predefined configurations

Reference:
- Board.cpp: Board::SpawnZombie(), wave timing logic
- avz_tick.h: Frame synchronization
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import IntEnum

from data.zombies import ZombieType


@dataclass
class WaveConfig:
    """Configuration for a single wave of zombies"""
    wave_number: int
    zombies: List[Tuple[ZombieType, int]]  # List of (zombie_type, row)
    spawn_delay: int = 0  # Delay in cs before spawning this wave
    spawn_interval: int = 50  # Interval between zombie spawns in cs
    
    @property
    def zombie_count(self) -> int:
        """Get total number of zombies in this wave"""
        return len(self.zombies)
    
    @classmethod
    def create_simple(cls, wave_number: int, zombie_types: List[ZombieType], 
                      row_count: int = 5) -> WaveConfig:
        """
        Create a simple wave with zombies distributed across rows
        
        Args:
            wave_number: Wave number
            zombie_types: List of zombie types to spawn
            row_count: Number of rows to distribute across
            
        Returns:
            WaveConfig with zombies assigned to rows
        """
        zombies = []
        for i, z_type in enumerate(zombie_types):
            row = i % row_count
            zombies.append((z_type, row))
        
        return cls(
            wave_number=wave_number,
            zombies=zombies,
            spawn_delay=0,
            spawn_interval=50,
        )


class SpawnState(IntEnum):
    """Wave spawner state"""
    WAITING = 0  # Waiting for wave to start
    SPAWNING = 1  # Currently spawning zombies
    FINISHED = 2  # All waves completed


class WaveSpawner:
    """
    Wave spawner manager
    
    Handles timing and spawning of zombie waves based on configurations.
    """
    
    def __init__(self, waves: List[WaveConfig] = None, initial_delay: int = 500):
        """
        Initialize wave spawner
        
        Args:
            waves: List of wave configurations
            initial_delay: Delay before first wave (cs)
        """
        self.waves: List[WaveConfig] = waves or []
        self.current_wave_index: int = 0
        self.state: SpawnState = SpawnState.WAITING
        
        # Timing state
        self.initial_delay: int = initial_delay
        self.delay_countdown: int = initial_delay
        self.spawn_countdown: int = 0
        
        # Current wave spawning state
        self._current_zombie_index: int = 0
        self._wave_spawn_countdown: int = 0
    
    def update(self, frame: int) -> List[Tuple[ZombieType, int]]:
        """
        Update spawner and return zombies to spawn this frame
        
        Args:
            frame: Current frame number
            
        Returns:
            List of (zombie_type, row) tuples to spawn
        """
        spawns: List[Tuple[ZombieType, int]] = []
        
        if self.state == SpawnState.FINISHED:
            return spawns
        
        if self.state == SpawnState.WAITING:
            # Check if initial delay passed
            self.delay_countdown -= 1
            if self.delay_countdown <= 0:
                self.state = SpawnState.SPAWNING
                self._start_current_wave()
            return spawns
        
        if self.state == SpawnState.SPAWNING:
            spawns = self._update_spawning()
        
        return spawns
    
    def _start_current_wave(self) -> None:
        """Start spawning the current wave"""
        if self.current_wave_index >= len(self.waves):
            self.state = SpawnState.FINISHED
            return
        
        wave = self.waves[self.current_wave_index]
        self._current_zombie_index = 0
        self._wave_spawn_countdown = wave.spawn_delay
    
    def _update_spawning(self) -> List[Tuple[ZombieType, int]]:
        """Update spawning and return zombies to spawn"""
        spawns: List[Tuple[ZombieType, int]] = []
        
        if self.current_wave_index >= len(self.waves):
            self.state = SpawnState.FINISHED
            return spawns
        
        wave = self.waves[self.current_wave_index]
        
        # Check wave spawn delay
        if self._wave_spawn_countdown > 0:
            self._wave_spawn_countdown -= 1
            return spawns
        
        # Check spawn interval countdown
        if self.spawn_countdown > 0:
            self.spawn_countdown -= 1
            return spawns
        
        # Spawn next zombie in wave
        if self._current_zombie_index < len(wave.zombies):
            zombie_type, row = wave.zombies[self._current_zombie_index]
            spawns.append((zombie_type, row))
            self._current_zombie_index += 1
            self.spawn_countdown = wave.spawn_interval
        
        # Check if wave is complete
        if self._current_zombie_index >= len(wave.zombies):
            self.current_wave_index += 1
            if self.current_wave_index >= len(self.waves):
                self.state = SpawnState.FINISHED
            else:
                self._start_current_wave()
        
        return spawns
    
    def is_finished(self) -> bool:
        """Check if all waves have been spawned"""
        return self.state == SpawnState.FINISHED
    
    def get_remaining_waves(self) -> int:
        """Get number of remaining waves"""
        return max(0, len(self.waves) - self.current_wave_index)
    
    def get_remaining_zombies_in_wave(self) -> int:
        """Get remaining zombies in current wave"""
        if self.current_wave_index >= len(self.waves):
            return 0
        wave = self.waves[self.current_wave_index]
        return max(0, len(wave.zombies) - self._current_zombie_index)
    
    def get_total_remaining_zombies(self) -> int:
        """Get total remaining zombies across all waves"""
        total = self.get_remaining_zombies_in_wave()
        for i in range(self.current_wave_index + 1, len(self.waves)):
            total += len(self.waves[i].zombies)
        return total
    
    @property
    def current_wave(self) -> int:
        """Get current wave number (1-based)"""
        return min(self.current_wave_index + 1, len(self.waves))
    
    @property
    def total_waves(self) -> int:
        """Get total number of waves"""
        return len(self.waves)
    
    def skip_to_wave(self, wave_number: int) -> None:
        """
        Skip to a specific wave
        
        Args:
            wave_number: Wave number to skip to (1-based)
        """
        target_index = wave_number - 1
        if target_index < 0:
            target_index = 0
        if target_index >= len(self.waves):
            self.state = SpawnState.FINISHED
            return
        
        self.current_wave_index = target_index
        self.state = SpawnState.SPAWNING
        self.delay_countdown = 0
        self._start_current_wave()
    
    def reset(self) -> None:
        """Reset spawner to initial state"""
        self.current_wave_index = 0
        self.state = SpawnState.WAITING
        self.delay_countdown = self.initial_delay
        self.spawn_countdown = 0
        self._current_zombie_index = 0
        self._wave_spawn_countdown = 0


# ============================================================================
# Predefined Wave Configurations
# ============================================================================

def create_standard_waves(total_waves: int = 10, row_count: int = 5) -> List[WaveConfig]:
    """
    Create standard wave configurations
    
    Args:
        total_waves: Total number of waves
        row_count: Number of rows in the level
        
    Returns:
        List of WaveConfig for each wave
    """
    waves = []
    
    for wave_num in range(1, total_waves + 1):
        zombies = []
        
        # Calculate zombie count based on wave number
        base_count = 2 + wave_num // 2
        
        # Every 10th wave is a "huge wave"
        if wave_num % 10 == 0:
            base_count = base_count * 2
        
        # Determine zombie types based on wave number
        for i in range(base_count):
            row = i % row_count
            
            if wave_num <= 2:
                # Early waves: only normal zombies
                zombie_type = ZombieType.ZOMBIE
            elif wave_num <= 5:
                # Mid-early: mix of normal and conehead
                zombie_type = ZombieType.ZOMBIE if i % 3 != 0 else ZombieType.CONEHEAD
            elif wave_num <= 8:
                # Mid: add bucketheads
                if i % 4 == 0:
                    zombie_type = ZombieType.BUCKETHEAD
                elif i % 3 == 0:
                    zombie_type = ZombieType.CONEHEAD
                else:
                    zombie_type = ZombieType.ZOMBIE
            else:
                # Late: more variety
                if i % 5 == 0:
                    zombie_type = ZombieType.FOOTBALL
                elif i % 4 == 0:
                    zombie_type = ZombieType.BUCKETHEAD
                elif i % 3 == 0:
                    zombie_type = ZombieType.CONEHEAD
                else:
                    zombie_type = ZombieType.ZOMBIE
            
            zombies.append((zombie_type, row))
        
        # Calculate spawn delay (longer between waves as game progresses)
        spawn_delay = 100 + wave_num * 20
        
        waves.append(WaveConfig(
            wave_number=wave_num,
            zombies=zombies,
            spawn_delay=spawn_delay,
            spawn_interval=30 + wave_num * 5,
        ))
    
    return waves


def create_gargantuar_waves(row_count: int = 5) -> List[WaveConfig]:
    """
    Create waves with Gargantuars for testing
    
    Args:
        row_count: Number of rows
        
    Returns:
        List of WaveConfig with Gargantuars
    """
    waves = []
    
    # Wave 1: Normal zombies
    waves.append(WaveConfig(
        wave_number=1,
        zombies=[(ZombieType.ZOMBIE, i) for i in range(row_count)],
        spawn_delay=100,
        spawn_interval=50,
    ))
    
    # Wave 2: Mixed
    zombies = []
    for i in range(row_count):
        zombies.append((ZombieType.CONEHEAD, i))
        zombies.append((ZombieType.ZOMBIE, i))
    waves.append(WaveConfig(
        wave_number=2,
        zombies=zombies,
        spawn_delay=200,
        spawn_interval=40,
    ))
    
    # Wave 3: Gargantuar wave
    zombies = []
    for i in range(row_count):
        zombies.append((ZombieType.GARGANTUAR, i))
        zombies.append((ZombieType.BUCKETHEAD, i))
    waves.append(WaveConfig(
        wave_number=3,
        zombies=zombies,
        spawn_delay=300,
        spawn_interval=100,
    ))
    
    return waves
