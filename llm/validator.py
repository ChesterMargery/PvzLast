"""
Action Validator

Validates LLM-proposed actions against current game state.
Handles delay compensation for stale action data.
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass

from game.state import GameState
from engine.action import Action, ActionType
from data.plants import PlantType, PLANT_COST


@dataclass
class ValidationResult:
    """Result of action validation"""
    valid: bool
    action: Action
    error: Optional[str] = None
    adjusted: bool = False  # True if action was adjusted


class ActionValidator:
    """
    Validates actions from LLM against current game state.
    
    Handles:
    - Sun cost validation
    - Seed availability/cooldown check
    - Cell occupancy check
    - Delay compensation (action may be stale)
    """
    
    def validate(self, action: Action, state: GameState) -> ValidationResult:
        """
        Validate an action against current state.
        
        Args:
            action: Action to validate
            state: Current game state
            
        Returns:
            ValidationResult with validity and error message
        """
        if action.action_type == ActionType.WAIT:
            return ValidationResult(valid=True, action=action)
        
        if action.action_type == ActionType.SHOVEL:
            return self._validate_shovel(action, state)
        
        if action.action_type == ActionType.USE_COB:
            return self._validate_cob(action, state)
        
        if action.is_plant_action:
            return self._validate_plant(action, state)
        
        return ValidationResult(valid=True, action=action)
    
    def _validate_plant(self, action: Action, state: GameState) -> ValidationResult:
        """Validate plant action"""
        plant_type = action.plant_type
        row = action.row
        col = action.col
        
        # Check sun cost
        cost = PLANT_COST.get(plant_type, 100)
        if state.sun < cost:
            return ValidationResult(
                valid=False,
                action=action,
                error=f"阳光不足: 需要{cost}, 当前{state.sun}"
            )
        
        # Check seed availability
        seed = state.get_seed_by_type(plant_type)
        if not seed:
            return ValidationResult(
                valid=False,
                action=action,
                error=f"没有该植物卡片: type={plant_type}"
            )
        
        if not seed.usable:
            return ValidationResult(
                valid=False,
                action=action,
                error=f"卡片冷却中: {int(seed.cooldown_percent)}%"
            )
        
        # Check row bounds
        if not (0 <= row <= 4):
            return ValidationResult(
                valid=False,
                action=action,
                error=f"行号无效: {row}"
            )
        
        # Check col bounds
        if not (0 <= col <= 8):
            return ValidationResult(
                valid=False,
                action=action,
                error=f"列号无效: {col}"
            )
        
        # Check cell occupancy (unless pumpkin which can stack)
        existing = state.get_plant_at(row, col)
        if existing and plant_type != PlantType.PUMPKIN:
            # Try to find nearby empty cell
            adjusted = self._find_nearby_cell(state, row, col)
            if adjusted:
                new_action = Action(
                    action_type=action.action_type,
                    row=adjusted[0],
                    col=adjusted[1],
                    plant_type=plant_type,
                    priority=action.priority,
                    reason=action.reason + f" (调整位置{row},{col}->{adjusted[0]},{adjusted[1]})"
                )
                return ValidationResult(
                    valid=True,
                    action=new_action,
                    adjusted=True
                )
            
            return ValidationResult(
                valid=False,
                action=action,
                error=f"格子已被占用: ({row}, {col})"
            )
        
        # Check conditions from metadata
        conditions = action.metadata.get("conditions", {})
        if conditions:
            result = self._check_conditions(conditions, state, action)
            if not result.valid:
                return result
        
        return ValidationResult(valid=True, action=action)
    
    def _validate_shovel(self, action: Action, state: GameState) -> ValidationResult:
        """Validate shovel action"""
        row = action.row
        col = action.col
        
        # Check bounds
        if not (0 <= row <= 4 and 0 <= col <= 8):
            return ValidationResult(
                valid=False,
                action=action,
                error=f"位置无效: ({row}, {col})"
            )
        
        # Check if plant exists
        plant = state.get_plant_at(row, col)
        if not plant:
            return ValidationResult(
                valid=False,
                action=action,
                error=f"没有植物可铲: ({row}, {col})"
            )
        
        return ValidationResult(valid=True, action=action)
    
    def _validate_cob(self, action: Action, state: GameState) -> ValidationResult:
        """Validate cob cannon action"""
        # Check if we have ready cobs
        ready_cobs = state.get_ready_cobs()
        if not ready_cobs:
            return ValidationResult(
                valid=False,
                action=action,
                error="没有可用的玉米炮"
            )
        
        # Check click cooldown
        if not state.can_fire_cob():
            return ValidationResult(
                valid=False,
                action=action,
                error="玉米炮点击冷却中"
            )
        
        # Check target row
        if not (0 <= action.row <= 4):
            return ValidationResult(
                valid=False,
                action=action,
                error=f"目标行无效: {action.row}"
            )
        
        return ValidationResult(valid=True, action=action)
    
    def _check_conditions(self, conditions: dict, state: GameState,
                          action: Action) -> ValidationResult:
        """Check action conditions"""
        # Check minimum sun
        min_sun = conditions.get("min_sun")
        if min_sun and state.sun < min_sun:
            return ValidationResult(
                valid=False,
                action=action,
                error=f"未达到最小阳光条件: {state.sun} < {min_sun}"
            )
        
        # Check seed ready
        seed_type = conditions.get("seed_ready")
        if seed_type is not None:
            seed = state.get_seed_by_type(seed_type)
            if not seed or not seed.usable:
                return ValidationResult(
                    valid=False,
                    action=action,
                    error=f"指定卡片未就绪: type={seed_type}"
                )
        
        # Check cell empty
        cell_empty = conditions.get("cell_empty")
        if cell_empty:
            r, c = cell_empty
            if not state.is_cell_empty(r, c):
                return ValidationResult(
                    valid=False,
                    action=action,
                    error=f"指定格子非空: ({r}, {c})"
                )
        
        return ValidationResult(valid=True, action=action)
    
    def _find_nearby_cell(self, state: GameState, row: int, col: int) -> Optional[Tuple[int, int]]:
        """Find nearby empty cell (for position adjustment)"""
        # Check same row first
        for offset in [1, -1, 2, -2]:
            new_col = col + offset
            if 0 <= new_col <= 8 and state.is_cell_empty(row, new_col):
                return (row, new_col)
        
        return None
    
    def validate_batch(self, actions: List[Action], state: GameState) -> List[ValidationResult]:
        """Validate multiple actions"""
        results = []
        
        # Track simulated state changes
        spent_sun = 0
        used_seeds = set()
        occupied_cells = set()
        
        for action in actions:
            if action.action_type == ActionType.WAIT:
                results.append(ValidationResult(valid=True, action=action))
                continue
            
            # Adjust state simulation
            if action.is_plant_action:
                cost = PLANT_COST.get(action.plant_type, 100)
                
                # Check if we'd have enough sun
                if state.sun - spent_sun < cost:
                    results.append(ValidationResult(
                        valid=False,
                        action=action,
                        error=f"阳光不足(累计): 需要{cost}, 剩余{state.sun - spent_sun}"
                    ))
                    continue
                
                # Check if seed already used in batch
                if action.plant_type in used_seeds:
                    seed = state.get_seed_by_type(action.plant_type)
                    if seed and not seed.usable:
                        results.append(ValidationResult(
                            valid=False,
                            action=action,
                            error=f"同批次重复使用未就绪卡片"
                        ))
                        continue
                
                # Check cell occupancy including batch
                cell = (action.row, action.col)
                existing = state.get_plant_at(action.row, action.col)
                if existing or cell in occupied_cells:
                    results.append(ValidationResult(
                        valid=False,
                        action=action,
                        error=f"格子已被占用(批次内): {cell}"
                    ))
                    continue
                
                # Validate normally
                result = self.validate(action, state)
                results.append(result)
                
                if result.valid:
                    spent_sun += cost
                    used_seeds.add(action.plant_type)
                    occupied_cells.add(cell)
            else:
                results.append(self.validate(action, state))
        
        return results
