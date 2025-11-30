"""
Emergency Handler

Local rule-based emergency response that doesn't wait for LLM.
Handles critical situations requiring immediate action.
"""

from typing import List, Optional
from dataclasses import dataclass

from game.state import GameState
from game.zombie import ZombieInfo
from engine.action import Action, ActionType
from data.plants import PlantType, PLANT_COST
from data.zombies import ZombieType, GARGANTUAR_ZOMBIES


@dataclass
class EmergencyAction:
    """Emergency action with metadata"""
    action: Action
    urgency: int  # 0-100, higher = more urgent
    reason: str


class EmergencyHandler:
    """
    Local rule engine for emergency situations.
    
    Handles:
    - Zombies very close to home (x < 150)
    - Fast zombies approaching
    - No defense in threatened row
    """
    
    def __init__(self, emergency_x: int = 150, emergency_eta: int = 200):
        """
        Initialize handler.
        
        Args:
            emergency_x: X position threshold for emergency
            emergency_eta: ETA threshold in cs for emergency
        """
        self.emergency_x = emergency_x
        self.emergency_eta = emergency_eta
    
    def check(self, state: GameState) -> Optional[EmergencyAction]:
        """
        Check for emergency situations and return immediate action.
        
        Args:
            state: Current game state
            
        Returns:
            Emergency action if needed, None otherwise
        """
        emergencies = []
        
        # Check each row for emergencies
        for row in range(5):
            row_emergency = self._check_row_emergency(state, row)
            if row_emergency:
                emergencies.append(row_emergency)
        
        if not emergencies:
            return None
        
        # Return highest urgency emergency
        emergencies.sort(key=lambda e: e.urgency, reverse=True)
        return emergencies[0]
    
    def _check_row_emergency(self, state: GameState, row: int) -> Optional[EmergencyAction]:
        """Check for emergency in a specific row"""
        row_zombies = state.get_zombies_in_row(row)
        if not row_zombies:
            return None
        
        # Find most dangerous zombie
        closest = min(row_zombies, key=lambda z: z.x)
        
        # Check if emergency
        is_emergency = (
            closest.x < self.emergency_x or
            (closest.effective_speed > 0 and 
             closest.time_to_reach(0) < self.emergency_eta)
        )
        
        if not is_emergency:
            return None
        
        # Determine best response
        return self._get_emergency_response(state, row, closest, row_zombies)
    
    def _get_emergency_response(self, state: GameState, row: int,
                                 closest: ZombieInfo,
                                 row_zombies: List[ZombieInfo]) -> Optional[EmergencyAction]:
        """Determine best emergency response"""
        urgency = self._calculate_urgency(closest)
        
        # Try different emergency options in priority order
        
        # 1. Use cob cannon if available and multiple targets
        cob_action = self._try_cob(state, row, closest, row_zombies)
        if cob_action:
            return EmergencyAction(
                action=cob_action,
                urgency=urgency,
                reason=f"紧急: 玉米炮轰击r{row} ({len(row_zombies)}只僵尸)"
            )
        
        # 2. Use jalapeno for row clear (great for single row emergency)
        jalapeno_action = self._try_jalapeno(state, row)
        if jalapeno_action:
            return EmergencyAction(
                action=jalapeno_action,
                urgency=urgency,
                reason=f"紧急: 辣椒清行r{row}"
            )
        
        # 3. Use cherry bomb
        cherry_action = self._try_cherry(state, row, closest)
        if cherry_action:
            return EmergencyAction(
                action=cherry_action,
                urgency=urgency,
                reason=f"紧急: 樱桃炸r{row} x={int(closest.x)}"
            )
        
        # 4. Emergency wall plant
        wall_action = self._try_emergency_wall(state, row, closest)
        if wall_action:
            return EmergencyAction(
                action=wall_action,
                urgency=urgency - 20,  # Lower priority than instant kills
                reason=f"紧急: 补坚果r{row}"
            )
        
        return None
    
    def _calculate_urgency(self, zombie: ZombieInfo) -> int:
        """Calculate urgency based on zombie position and type"""
        # Base urgency from position
        if zombie.x < 50:
            urgency = 100
        elif zombie.x < 100:
            urgency = 90
        elif zombie.x < 150:
            urgency = 80
        else:
            urgency = 70
        
        # Bonus for dangerous zombies
        if zombie.type in GARGANTUAR_ZOMBIES:
            urgency = min(100, urgency + 10)
        elif zombie.type == ZombieType.FOOTBALL:
            urgency = min(100, urgency + 5)
        
        return urgency
    
    def _try_cob(self, state: GameState, row: int, closest: ZombieInfo,
                 row_zombies: List[ZombieInfo]) -> Optional[Action]:
        """Try to use cob cannon"""
        ready_cobs = state.get_ready_cobs()
        if not ready_cobs or not state.can_fire_cob():
            return None
        
        # Calculate optimal target position
        target_x = closest.x
        
        # Adjust for flying time (~373cs)
        if closest.effective_speed > 0:
            target_x -= closest.effective_speed * 373
        
        # Clamp to valid range
        target_x = max(0, min(800, target_x))
        
        return Action.use_cob(
            target_x=target_x,
            target_row=row,
            priority=100,
            reason=f"紧急炮击"
        )
    
    def _try_jalapeno(self, state: GameState, row: int) -> Optional[Action]:
        """Try to use jalapeno"""
        if not state.can_plant(PlantType.JALAPENO):
            return None
        
        # Find empty cell in row (prefer middle columns)
        for col in [4, 3, 5, 2, 6, 1, 7, 0, 8]:
            if state.is_cell_empty(row, col):
                return Action.use_jalapeno(
                    row=row,
                    priority=95,
                    reason="紧急辣椒"
                )
        
        return None
    
    def _try_cherry(self, state: GameState, row: int,
                    closest: ZombieInfo) -> Optional[Action]:
        """Try to use cherry bomb"""
        if not state.can_plant(PlantType.CHERRY_BOMB):
            return None
        
        # Find empty cell near zombie
        target_col = closest.col
        
        for col_offset in [0, -1, 1, -2, 2]:
            col = target_col + col_offset
            if 0 <= col <= 8 and state.is_cell_empty(row, col):
                return Action.use_cherry(
                    row=row,
                    col=col,
                    priority=90,
                    reason="紧急樱桃"
                )
        
        return None
    
    def _try_emergency_wall(self, state: GameState, row: int,
                            closest: ZombieInfo) -> Optional[Action]:
        """Try to plant emergency wall"""
        # Check if we have wall available
        can_wallnut = state.can_plant(PlantType.WALLNUT)
        can_tallnut = state.can_plant(PlantType.TALLNUT)
        
        if not can_wallnut and not can_tallnut:
            return None
        
        # Find good position for wall (between zombie and home)
        zombie_col = closest.col
        
        for col in range(zombie_col - 1, -1, -1):
            if state.is_cell_empty(row, col):
                plant_type = PlantType.TALLNUT if can_tallnut else PlantType.WALLNUT
                return Action.plant(
                    row=row,
                    col=col,
                    plant_type=plant_type,
                    priority=70,
                    reason="紧急补墙"
                )
        
        return None
    
    def get_all_emergencies(self, state: GameState) -> List[EmergencyAction]:
        """Get all emergency situations (for reporting)"""
        emergencies = []
        
        for row in range(5):
            row_emergency = self._check_row_emergency(state, row)
            if row_emergency:
                emergencies.append(row_emergency)
        
        return emergencies
