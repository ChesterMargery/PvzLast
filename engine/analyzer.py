"""
Threat and Resource Analyzer
Analyzes game state for decision making
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from game.state import GameState
from game.zombie import ZombieInfo
from game.plant import PlantInfo
from data.zombies import (
    ZombieType, 
    is_dangerous_zombie, 
    is_gargantuar,
    GARGANTUAR_ZOMBIES,
)
from data.plants import (
    PlantType,
    PLANT_COST,
    ATTACKING_PLANTS,
    DEFENSIVE_PLANTS,
    INSTANT_KILL_PLANTS,
)


@dataclass
class RowThreat:
    """Analysis of threat level in a single row"""
    row: int
    total_threat: float
    zombie_count: int
    closest_zombie_x: float
    has_gargantuar: bool
    has_fast_zombie: bool
    time_to_danger: float  # Time until closest zombie reaches danger zone


@dataclass
class ThreatAnalysis:
    """Complete threat analysis for the game"""
    overall_threat: float
    row_threats: List[RowThreat]
    most_threatened_row: int
    critical_zombies: List[ZombieInfo]
    gargantuar_count: int
    total_zombie_hp: int


class ThreatAnalyzer:
    """
    Analyzes threats on the playing field
    
    Identifies dangerous zombies, calculates threat levels,
    and determines priority targets.
    """
    
    DANGER_X = 200  # X coordinate considered dangerous
    CRITICAL_X = 100  # X coordinate considered critical
    
    def __init__(self, state: GameState):
        self.state = state
        self.row_count = 6 if state.scene in [2, 3] else 5  # Pool/Fog have 6 rows
    
    def analyze(self) -> ThreatAnalysis:
        """Perform complete threat analysis"""
        row_threats = []
        total_threat = 0.0
        total_hp = 0
        garg_count = 0
        critical_zombies = []
        
        for row in range(self.row_count):
            row_threat = self._analyze_row(row)
            row_threats.append(row_threat)
            total_threat += row_threat.total_threat
            
            # Collect critical zombies
            for z in self.state.get_zombies_in_row(row):
                total_hp += z.total_hp
                if is_gargantuar(z.type):
                    garg_count += 1
                if z.x < self.DANGER_X:
                    critical_zombies.append(z)
        
        # Find most threatened row
        most_threatened = max(range(self.row_count), 
                             key=lambda r: row_threats[r].total_threat)
        
        return ThreatAnalysis(
            overall_threat=total_threat,
            row_threats=row_threats,
            most_threatened_row=most_threatened,
            critical_zombies=critical_zombies,
            gargantuar_count=garg_count,
            total_zombie_hp=total_hp,
        )
    
    def _analyze_row(self, row: int) -> RowThreat:
        """Analyze threat level for a single row"""
        zombies = self.state.get_zombies_in_row(row)
        
        if not zombies:
            return RowThreat(
                row=row,
                total_threat=0.0,
                zombie_count=0,
                closest_zombie_x=float('inf'),
                has_gargantuar=False,
                has_fast_zombie=False,
                time_to_danger=float('inf'),
            )
        
        total_threat = sum(z.threat_level for z in zombies)
        closest = min(zombies, key=lambda z: z.x)
        has_garg = any(is_gargantuar(z.type) for z in zombies)
        has_fast = any(z.effective_speed >= 0.4 for z in zombies)
        
        # Calculate time to danger
        if closest.effective_speed > 0:
            time_to_danger = max(0, (closest.x - self.DANGER_X) / closest.effective_speed)
        else:
            time_to_danger = float('inf')
        
        return RowThreat(
            row=row,
            total_threat=total_threat,
            zombie_count=len(zombies),
            closest_zombie_x=closest.x,
            has_gargantuar=has_garg,
            has_fast_zombie=has_fast,
            time_to_danger=time_to_danger,
        )
    
    def get_priority_targets(self, max_targets: int = 5) -> List[ZombieInfo]:
        """Get high-priority zombie targets"""
        zombies = sorted(self.state.alive_zombies, 
                        key=lambda z: -z.threat_level)
        return zombies[:max_targets]
    
    def get_row_danger(self, row: int) -> float:
        """Get danger level for a specific row (0-10 scale)"""
        row_threat = self._analyze_row(row)
        
        # Base danger from threat level
        danger = min(10, row_threat.total_threat)
        
        # Increase danger if zombies are close
        if row_threat.closest_zombie_x < self.CRITICAL_X:
            danger = 10.0
        elif row_threat.closest_zombie_x < self.DANGER_X:
            danger = max(danger, 8.0)
        elif row_threat.closest_zombie_x < 400:
            danger = max(danger, 5.0)
        
        return danger


@dataclass
class ResourceAnalysis:
    """Analysis of available resources"""
    sun: int
    sun_rate: float  # Estimated sun per minute
    usable_seeds: List[int]  # Plant types that can be used
    instant_kill_available: bool
    cob_cannons_ready: int


class ResourceAnalyzer:
    """
    Analyzes available resources
    
    Tracks sun, card availability, and resource generation rate.
    """
    
    def __init__(self, state: GameState):
        self.state = state
    
    def analyze(self) -> ResourceAnalysis:
        """Perform complete resource analysis"""
        # Count sun production plants
        sun_producers = self.state.get_plants_by_type(PlantType.SUNFLOWER)
        twin_producers = self.state.get_plants_by_type(PlantType.TWINSUNFLOWER)
        sun_shrooms = self.state.get_plants_by_type(PlantType.SUNSHROOM)
        
        # Estimate sun rate (sun per minute)
        # Sunflower: 25 sun every 24 seconds = ~62.5/min
        # Twin Sunflower: 50 sun every 24 seconds = ~125/min
        sun_rate = (len(sun_producers) * 62.5 + 
                   len(twin_producers) * 125 +
                   len(sun_shrooms) * 45)  # Sun-shroom varies
        
        # Get usable seeds
        usable_seeds = [s.type for s in self.state.seeds if s.usable]
        
        # Check for instant kill availability
        instant_types = {PlantType.CHERRY_BOMB, PlantType.JALAPENO, 
                        PlantType.DOOMSHROOM}
        instant_available = any(
            s.type in instant_types and s.usable and self.state.sun >= PLANT_COST.get(s.type, 100)
            for s in self.state.seeds
        )
        
        # Count ready cob cannons
        cobs_ready = sum(1 for p in self.state.alive_plants 
                        if p.type == PlantType.COBCANNON and p.cob_ready)
        
        return ResourceAnalysis(
            sun=self.state.sun,
            sun_rate=sun_rate,
            usable_seeds=usable_seeds,
            instant_kill_available=instant_available,
            cob_cannons_ready=cobs_ready,
        )
    
    def can_afford(self, plant_type: int) -> bool:
        """Check if we can afford to plant a specific type"""
        cost = PLANT_COST.get(plant_type, 100)
        return self.state.sun >= cost
    
    def get_affordable_plants(self) -> List[int]:
        """Get list of plant types we can currently afford"""
        affordable = []
        for seed in self.state.seeds:
            if seed.usable:
                cost = PLANT_COST.get(seed.type, 100)
                if self.state.sun >= cost:
                    affordable.append(seed.type)
        return affordable
    
    def get_sun_deficit(self, plant_type: int) -> int:
        """Get how much more sun we need for a plant"""
        cost = PLANT_COST.get(plant_type, 100)
        return max(0, cost - self.state.sun)


class DefenseAnalyzer:
    """
    Analyzes defensive coverage
    
    Identifies gaps in defense and plant health.
    """
    
    def __init__(self, state: GameState):
        self.state = state
        self.row_count = 6 if state.scene in [2, 3] else 5
    
    def get_undefended_rows(self) -> List[int]:
        """Get rows without defensive plants"""
        undefended = []
        for row in range(self.row_count):
            has_wall = any(
                p.type in DEFENSIVE_PLANTS 
                for p in self.state.get_plants_in_row(row)
            )
            if not has_wall:
                undefended.append(row)
        return undefended
    
    def get_weak_defense_rows(self, hp_threshold: float = 0.3) -> List[int]:
        """Get rows where defensive plants have low HP"""
        weak_rows = []
        for row in range(self.row_count):
            for plant in self.state.get_plants_in_row(row):
                if plant.type in DEFENSIVE_PLANTS:
                    if plant.hp_ratio < hp_threshold:
                        weak_rows.append(row)
                        break
        return weak_rows
    
    def get_rows_without_attackers(self) -> List[int]:
        """Get rows without any attacking plants"""
        no_attackers = []
        for row in range(self.row_count):
            has_attacker = any(
                p.type in ATTACKING_PLANTS
                for p in self.state.get_plants_in_row(row)
            )
            if not has_attacker:
                no_attackers.append(row)
        return no_attackers
    
    def get_defense_score(self, row: int) -> float:
        """
        Calculate defense score for a row (0-10)
        
        Higher score = better defense
        """
        plants = self.state.get_plants_in_row(row)
        if not plants:
            return 0.0
        
        score = 0.0
        
        # Add score for defensive plants
        for p in plants:
            if p.type in DEFENSIVE_PLANTS:
                score += 3.0 * p.hp_ratio
            if p.type in ATTACKING_PLANTS:
                score += 2.0
        
        # Bonus for complete defense
        if self.state.get_row_defense_count(row) > 0:
            score += 2.0
        
        return min(10.0, score)
