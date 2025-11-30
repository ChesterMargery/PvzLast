"""
Action Optimizer
Evaluates and optimizes actions for best decision making

This module provides the core optimization algorithm interface.
Future implementations can include MCTS, reinforcement learning, etc.
"""

from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from game.state import GameState
from engine.action import Action, ActionType
from engine.analyzer import ThreatAnalyzer, ResourceAnalyzer
from engine.strategy import StrategyPlanner
from data.plants import PlantType, PLANT_COST


@dataclass
class ActionEvaluation:
    """Evaluation result for an action"""
    action: Action
    score: float
    components: Dict[str, float]  # Score breakdown
    is_valid: bool
    validation_error: Optional[str] = None


class BaseOptimizer(ABC):
    """
    Abstract base class for action optimizers
    
    Subclasses can implement different optimization strategies:
    - Rule-based (current implementation)
    - Monte Carlo Tree Search
    - Reinforcement Learning
    - Genetic algorithms
    """
    
    @abstractmethod
    def get_best_action(self, state: GameState) -> Optional[Action]:
        """Get the best action for the current state"""
        pass
    
    @abstractmethod
    def evaluate_action(self, state: GameState, action: Action) -> ActionEvaluation:
        """Evaluate a single action"""
        pass


class ActionOptimizer(BaseOptimizer):
    """
    Rule-based action optimizer
    
    Evaluates actions based on multiple weighted factors:
    - Threat reduction
    - Resource efficiency
    - Strategic value
    - Urgency
    """
    
    def __init__(self):
        # Weights for different evaluation components
        self.weights = {
            'threat_reduction': 2.0,
            'resource_efficiency': 1.0,
            'strategic_value': 1.5,
            'urgency': 3.0,
        }
        
        # Configuration
        self.min_action_interval_cs = 15  # Minimum time between actions
        self.last_action_time = 0
    
    def get_best_action(self, state: GameState) -> Optional[Action]:
        """
        Get the best action for the current state
        
        Uses the strategy planner to generate candidates,
        then evaluates and selects the best one.
        """
        # Generate candidate actions
        planner = StrategyPlanner(state)
        strategy_plan = planner.plan()
        
        if not strategy_plan.actions:
            return Action.wait("No actions available")
        
        # Evaluate all candidates
        evaluations = []
        for action in strategy_plan.actions:
            evaluation = self.evaluate_action(state, action)
            if evaluation.is_valid:
                evaluations.append(evaluation)
        
        if not evaluations:
            return Action.wait("No valid actions")
        
        # Select best action
        best = max(evaluations, key=lambda e: e.score)
        return best.action
    
    def evaluate_action(self, state: GameState, action: Action) -> ActionEvaluation:
        """
        Evaluate a single action
        
        Returns an evaluation with score breakdown.
        """
        # Validate action first
        is_valid, error = self._validate_action(state, action)
        if not is_valid:
            return ActionEvaluation(
                action=action,
                score=-1000,
                components={},
                is_valid=False,
                validation_error=error,
            )
        
        components = {}
        
        # Component 1: Threat reduction
        components['threat_reduction'] = self._evaluate_threat_reduction(state, action)
        
        # Component 2: Resource efficiency
        components['resource_efficiency'] = self._evaluate_resource_efficiency(state, action)
        
        # Component 3: Strategic value
        components['strategic_value'] = self._evaluate_strategic_value(state, action)
        
        # Component 4: Urgency
        components['urgency'] = self._evaluate_urgency(state, action)
        
        # Calculate weighted score
        total_score = sum(
            self.weights.get(key, 1.0) * value 
            for key, value in components.items()
        )
        
        # Add base priority
        total_score += action.priority / 10
        
        return ActionEvaluation(
            action=action,
            score=total_score,
            components=components,
            is_valid=True,
        )
    
    def _validate_action(self, state: GameState, action: Action) -> tuple:
        """
        Validate if an action can be performed
        
        Returns:
            (is_valid, error_message)
        """
        if action.action_type == ActionType.WAIT:
            return True, None
        
        if action.is_plant_action:
            # Check sun cost
            cost = action.sun_cost
            if state.sun < cost:
                return False, f"Not enough sun ({state.sun} < {cost})"
            
            # Check if seed is available
            seed = state.get_seed_by_type(action.plant_type)
            if not seed:
                return False, f"Seed not in deck"
            if not seed.usable:
                return False, f"Seed on cooldown"
            
            # Check if position is valid
            if not (0 <= action.row < 6 and 0 <= action.col < 9):
                return False, f"Invalid position ({action.row}, {action.col})"
            
            # Check if position is empty (for most plants)
            # Note: Some plants can be placed on others (pumpkin, upgrade plants)
            if not state.is_cell_empty(action.row, action.col):
                if action.plant_type not in [PlantType.PUMPKIN, PlantType.WALLNUT]:
                    return False, f"Position occupied"
        
        return True, None
    
    def _evaluate_threat_reduction(self, state: GameState, action: Action) -> float:
        """Evaluate how much this action reduces threats"""
        score = 0.0
        
        if action.action_type in {ActionType.USE_CHERRY, ActionType.USE_JALAPENO,
                                   ActionType.USE_COB, ActionType.USE_DOOM}:
            # High score for instant kill near zombies
            analyzer = ThreatAnalyzer(state)
            row_threat = analyzer._analyze_row(action.row)
            score = row_threat.total_threat * 2
            
            # Bonus if zombies are close
            if row_threat.closest_zombie_x < 300:
                score += 5.0
        
        elif action.action_type == ActionType.PLANT:
            # Defensive plants reduce threat
            from data.plants import DEFENSIVE_PLANTS, ATTACKING_PLANTS
            if action.plant_type in DEFENSIVE_PLANTS:
                score = 3.0
            elif action.plant_type in ATTACKING_PLANTS:
                score = 2.0
        
        return score
    
    def _evaluate_resource_efficiency(self, state: GameState, action: Action) -> float:
        """Evaluate resource efficiency of the action"""
        if not action.is_plant_action:
            return 0.0
        
        cost = action.sun_cost
        if cost == 0:
            return 5.0  # Free plants are efficient
        
        # Efficiency based on remaining sun after action
        remaining = state.sun - cost
        
        # Prefer keeping some sun in reserve
        if remaining >= 150:
            return 3.0
        elif remaining >= 75:
            return 2.0
        elif remaining >= 0:
            return 1.0
        else:
            return -5.0  # Cannot afford
    
    def _evaluate_strategic_value(self, state: GameState, action: Action) -> float:
        """Evaluate long-term strategic value"""
        score = 0.0
        
        if action.action_type == ActionType.PLANT:
            from data.plants import SUN_PRODUCING_PLANTS, ATTACKING_PLANTS
            
            # Sun producers have high strategic value early
            if action.plant_type in SUN_PRODUCING_PLANTS:
                sun_count = len(state.get_plants_by_type(PlantType.SUNFLOWER))
                if sun_count < 8:
                    score = 5.0 - sun_count * 0.5
            
            # Attackers have strategic value
            elif action.plant_type in ATTACKING_PLANTS:
                score = 2.0
        
        return score
    
    def _evaluate_urgency(self, state: GameState, action: Action) -> float:
        """Evaluate urgency of the action"""
        score = 0.0
        
        if action.is_instant_kill:
            # Check if there are critical threats
            analyzer = ThreatAnalyzer(state)
            analysis = analyzer.analyze()
            
            if analysis.critical_zombies:
                score = 10.0  # Maximum urgency
            elif analysis.overall_threat > 10:
                score = 5.0
        
        return score
    
    # ========================================================================
    # Advanced Optimization Methods (for future implementation)
    # ========================================================================
    
    def get_action_sequence(self, state: GameState, 
                           horizon: int = 5) -> List[Action]:
        """
        Plan a sequence of actions looking ahead
        
        This is a placeholder for more advanced planning algorithms
        like MCTS or dynamic programming.
        
        Args:
            state: Current game state
            horizon: Number of actions to plan ahead
            
        Returns:
            List of planned actions
        """
        # Current implementation: greedy single-action selection
        # TODO: Implement lookahead planning
        actions = []
        
        action = self.get_best_action(state)
        if action and not action.is_wait:
            actions.append(action)
        
        return actions


class MCTSOptimizer(BaseOptimizer):
    """
    Monte Carlo Tree Search optimizer (placeholder for future implementation)
    
    This would implement proper MCTS for finding optimal action sequences.
    """
    
    def __init__(self, simulations: int = 1000, exploration: float = 1.41):
        self.simulations = simulations
        self.exploration = exploration
    
    def get_best_action(self, state: GameState) -> Optional[Action]:
        """MCTS-based action selection (not implemented)"""
        # Placeholder - falls back to rule-based
        fallback = ActionOptimizer()
        return fallback.get_best_action(state)
    
    def evaluate_action(self, state: GameState, action: Action) -> ActionEvaluation:
        """MCTS evaluation (not implemented)"""
        fallback = ActionOptimizer()
        return fallback.evaluate_action(state, action)


class RLOptimizer(BaseOptimizer):
    """
    Reinforcement Learning optimizer (placeholder for future implementation)
    
    This would use a trained neural network policy for action selection.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
    
    def get_best_action(self, state: GameState) -> Optional[Action]:
        """RL-based action selection (not implemented)"""
        # Placeholder - falls back to rule-based
        fallback = ActionOptimizer()
        return fallback.get_best_action(state)
    
    def evaluate_action(self, state: GameState, action: Action) -> ActionEvaluation:
        """RL evaluation (not implemented)"""
        fallback = ActionOptimizer()
        return fallback.evaluate_action(state, action)
