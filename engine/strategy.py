"""
Strategy Planner
Plans high-level strategies based on game analysis
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import IntEnum, auto

from game.state import GameState
from engine.action import Action, ActionType
from engine.analyzer import ThreatAnalyzer, ResourceAnalyzer, DefenseAnalyzer
from data.plants import (
    PlantType,
    PLANT_COST,
    ATTACKING_PLANTS,
    DEFENSIVE_PLANTS,
    SUN_PRODUCING_PLANTS,
)


class StrategyPhase(IntEnum):
    """Current game phase affecting strategy"""
    EARLY_GAME = auto()  # Building economy
    MID_GAME = auto()  # Balanced defense/economy
    LATE_GAME = auto()  # Full defense mode
    EMERGENCY = auto()  # Crisis management


@dataclass
class StrategyPlan:
    """High-level strategy plan"""
    phase: StrategyPhase
    primary_goal: str
    actions: List[Action]
    notes: List[str]


class StrategyPlanner:
    """
    Plans high-level strategies based on game state
    
    Determines what the bot should focus on (economy, defense, offense)
    and generates action plans accordingly.
    """
    
    def __init__(self, state: GameState):
        self.state = state
        self.threat_analyzer = ThreatAnalyzer(state)
        self.resource_analyzer = ResourceAnalyzer(state)
        self.defense_analyzer = DefenseAnalyzer(state)
        
        # Configuration
        self.target_sun_plants = 8
        self.defense_column = 4  # Column for defensive plants
        self.row_count = 6 if state.scene in [2, 3] else 5
    
    def plan(self) -> StrategyPlan:
        """Create a strategy plan for the current game state"""
        phase = self._determine_phase()
        
        if phase == StrategyPhase.EMERGENCY:
            return self._plan_emergency()
        elif phase == StrategyPhase.EARLY_GAME:
            return self._plan_early_game()
        elif phase == StrategyPhase.MID_GAME:
            return self._plan_mid_game()
        else:
            return self._plan_late_game()
    
    def _determine_phase(self) -> StrategyPhase:
        """Determine current game phase"""
        threat_analysis = self.threat_analyzer.analyze()
        resource_analysis = self.resource_analyzer.analyze()
        
        # Emergency if any zombie is critically close
        if threat_analysis.critical_zombies:
            return StrategyPhase.EMERGENCY
        
        # Early game: wave < 5 or low sun production
        if self.state.wave < 5 and resource_analysis.sun_rate < 200:
            return StrategyPhase.EARLY_GAME
        
        # Late game: wave > 80% or gargantuars present
        if (self.state.wave > self.state.total_waves * 0.8 or 
            threat_analysis.gargantuar_count > 0):
            return StrategyPhase.LATE_GAME
        
        return StrategyPhase.MID_GAME
    
    def _plan_emergency(self) -> StrategyPlan:
        """Plan for emergency situations"""
        actions = []
        notes = []
        threat_analysis = self.threat_analyzer.analyze()
        
        # Priority 1: Use instant kill on critical zombies
        for zombie in threat_analysis.critical_zombies:
            # Try cherry bomb
            cherry_action = self._try_instant_kill(zombie, PlantType.CHERRY_BOMB)
            if cherry_action:
                actions.append(cherry_action)
                notes.append(f"Emergency cherry at row {zombie.row}")
                break
            
            # Try jalapeno
            jalapeno_action = self._try_instant_kill(zombie, PlantType.JALAPENO)
            if jalapeno_action:
                actions.append(jalapeno_action)
                notes.append(f"Emergency jalapeno at row {zombie.row}")
                break
        
        return StrategyPlan(
            phase=StrategyPhase.EMERGENCY,
            primary_goal="Survive immediate threat",
            actions=actions,
            notes=notes,
        )
    
    def _plan_early_game(self) -> StrategyPlan:
        """Plan for early game (economy focus)"""
        actions = []
        notes = []
        
        # Count sun producers
        sun_count = len(self.state.get_plants_by_type(PlantType.SUNFLOWER))
        twin_count = len(self.state.get_plants_by_type(PlantType.TWINSUNFLOWER))
        total_sun_production = sun_count + twin_count * 2
        
        # Priority 1: Plant more sunflowers
        if total_sun_production < self.target_sun_plants:
            sunflower_action = self._plan_sun_production()
            if sunflower_action:
                actions.append(sunflower_action)
                notes.append(f"Building economy ({total_sun_production}/{self.target_sun_plants})")
        
        # Priority 2: Basic defense if needed
        threat_analysis = self.threat_analyzer.analyze()
        if threat_analysis.overall_threat > 3:
            defense_action = self._plan_basic_defense()
            if defense_action:
                actions.append(defense_action)
                notes.append("Adding basic defense")
        
        return StrategyPlan(
            phase=StrategyPhase.EARLY_GAME,
            primary_goal="Build sun economy",
            actions=actions,
            notes=notes,
        )
    
    def _plan_mid_game(self) -> StrategyPlan:
        """Plan for mid game (balanced approach)"""
        actions = []
        notes = []
        
        threat_analysis = self.threat_analyzer.analyze()
        
        # Priority 1: Reinforce defense where needed
        for row_threat in threat_analysis.row_threats:
            if row_threat.total_threat > 5:
                defense_action = self._plan_row_defense(row_threat.row)
                if defense_action:
                    actions.append(defense_action)
                    notes.append(f"Reinforcing row {row_threat.row}")
                    break
        
        # Priority 2: Add attackers
        rows_without_attack = self.defense_analyzer.get_rows_without_attackers()
        if rows_without_attack:
            attack_action = self._plan_attacker(rows_without_attack[0])
            if attack_action:
                actions.append(attack_action)
                notes.append(f"Adding attacker to row {rows_without_attack[0]}")
        
        return StrategyPlan(
            phase=StrategyPhase.MID_GAME,
            primary_goal="Balance defense and offense",
            actions=actions,
            notes=notes,
        )
    
    def _plan_late_game(self) -> StrategyPlan:
        """Plan for late game (full defense)"""
        actions = []
        notes = []
        
        threat_analysis = self.threat_analyzer.analyze()
        
        # Priority 1: Handle gargantuars
        if threat_analysis.gargantuar_count > 0:
            garg_action = self._plan_gargantuar_response()
            if garg_action:
                actions.append(garg_action)
                notes.append("Responding to Gargantuar threat")
        
        # Priority 2: Strengthen weak defenses
        weak_rows = self.defense_analyzer.get_weak_defense_rows()
        if weak_rows:
            replace_action = self._plan_defense_replacement(weak_rows[0])
            if replace_action:
                actions.append(replace_action)
                notes.append(f"Replacing weak wall in row {weak_rows[0]}")
        
        return StrategyPlan(
            phase=StrategyPhase.LATE_GAME,
            primary_goal="Maintain defense until victory",
            actions=actions,
            notes=notes,
        )
    
    # ========================================================================
    # Helper Methods for Planning Actions
    # ========================================================================
    
    def _plan_sun_production(self) -> Optional[Action]:
        """Plan to place a sun-producing plant"""
        seed = self.state.get_seed_by_type(PlantType.SUNFLOWER)
        if not seed or not seed.usable:
            return None
        if self.state.sun < PLANT_COST[PlantType.SUNFLOWER]:
            return None
        
        # Find empty spot in back columns
        for col in [1, 0, 2]:
            for row in range(self.row_count):
                if self.state.is_cell_empty(row, col):
                    return Action.plant(
                        row=row, col=col,
                        plant_type=PlantType.SUNFLOWER,
                        priority=50.0,
                        reason="Economy development"
                    )
        return None
    
    def _plan_basic_defense(self) -> Optional[Action]:
        """Plan basic defensive placement"""
        # Try to place a peashooter
        seed = self.state.get_seed_by_type(PlantType.PEASHOOTER)
        if not seed or not seed.usable:
            return None
        if self.state.sun < PLANT_COST[PlantType.PEASHOOTER]:
            return None
        
        # Find row with zombies but no attacker
        for row in range(self.row_count):
            if self.state.get_row_threat(row) > 0:
                for col in [3, 2, 4]:
                    if self.state.is_cell_empty(row, col):
                        return Action.plant(
                            row=row, col=col,
                            plant_type=PlantType.PEASHOOTER,
                            priority=35.0,
                            reason=f"Basic defense for row {row}"
                        )
        return None
    
    def _plan_row_defense(self, row: int) -> Optional[Action]:
        """Plan defense for a specific row"""
        # Try wall-nut
        seed = self.state.get_seed_by_type(PlantType.WALLNUT)
        if seed and seed.usable and self.state.sun >= PLANT_COST[PlantType.WALLNUT]:
            for col in [self.defense_column, self.defense_column + 1, self.defense_column - 1]:
                if 0 <= col < 9 and self.state.is_cell_empty(row, col):
                    return Action.plant(
                        row=row, col=col,
                        plant_type=PlantType.WALLNUT,
                        priority=40.0,
                        reason=f"Row {row} defense"
                    )
        
        # Fallback to peashooter
        seed = self.state.get_seed_by_type(PlantType.PEASHOOTER)
        if seed and seed.usable and self.state.sun >= PLANT_COST[PlantType.PEASHOOTER]:
            for col in [3, 2, 4]:
                if self.state.is_cell_empty(row, col):
                    return Action.plant(
                        row=row, col=col,
                        plant_type=PlantType.PEASHOOTER,
                        priority=35.0,
                        reason=f"Row {row} attacker"
                    )
        return None
    
    def _plan_attacker(self, row: int) -> Optional[Action]:
        """Plan attacker placement for a row"""
        seed = self.state.get_seed_by_type(PlantType.PEASHOOTER)
        if not seed or not seed.usable:
            return None
        if self.state.sun < PLANT_COST[PlantType.PEASHOOTER]:
            return None
        
        for col in [3, 2, 4, 5]:
            if self.state.is_cell_empty(row, col):
                return Action.plant(
                    row=row, col=col,
                    plant_type=PlantType.PEASHOOTER,
                    priority=30.0,
                    reason=f"Attacker for row {row}"
                )
        return None
    
    def _plan_gargantuar_response(self) -> Optional[Action]:
        """Plan response to Gargantuar"""
        # Try cherry bomb
        cherry_seed = self.state.get_seed_by_type(PlantType.CHERRY_BOMB)
        if cherry_seed and cherry_seed.usable and self.state.sun >= PLANT_COST[PlantType.CHERRY_BOMB]:
            # Find gargantuar position
            for zombie in self.state.alive_zombies:
                if zombie.type in [23, 32]:  # Gargantuar types
                    col = zombie.col
                    if self.state.is_cell_empty(zombie.row, col):
                        return Action.use_cherry(
                            row=zombie.row, col=col,
                            priority=85.0,
                            reason="Gargantuar response"
                        )
        return None
    
    def _plan_defense_replacement(self, row: int) -> Optional[Action]:
        """Plan to replace weak defensive plant"""
        seed = self.state.get_seed_by_type(PlantType.WALLNUT)
        if not seed or not seed.usable:
            return None
        if self.state.sun < PLANT_COST[PlantType.WALLNUT]:
            return None
        
        # Find the weak wall
        for plant in self.state.get_plants_in_row(row):
            if plant.type in DEFENSIVE_PLANTS and plant.hp_ratio < 0.3:
                # Plant on top (game allows replacing walls)
                return Action.plant(
                    row=plant.row, col=plant.col,
                    plant_type=PlantType.WALLNUT,
                    priority=45.0,
                    reason="Replace weak wall"
                )
        return None
    
    def _try_instant_kill(self, zombie, plant_type: int) -> Optional[Action]:
        """Try to use an instant kill plant on a zombie"""
        seed = self.state.get_seed_by_type(plant_type)
        if not seed or not seed.usable:
            return None
        cost = PLANT_COST.get(plant_type, 150)
        if self.state.sun < cost:
            return None
        
        if plant_type == PlantType.CHERRY_BOMB:
            col = zombie.col
            if self.state.is_cell_empty(zombie.row, col):
                return Action.use_cherry(
                    row=zombie.row, col=col,
                    priority=100.0,
                    reason=f"Emergency kill at ({zombie.row}, {col})"
                )
        elif plant_type == PlantType.JALAPENO:
            if self.state.is_cell_empty(zombie.row, 0):
                return Action.use_jalapeno(
                    row=zombie.row,
                    priority=95.0,
                    reason=f"Emergency clear row {zombie.row}"
                )
        
        return None
