"""
LLM Player - Main Controller

Async architecture with fast loop (20ms) and LLM loop (1-2s).
Coordinates all LLM modules for playing PVZ.
"""

import asyncio
import time
from typing import Optional, List, Callable, Any
from dataclasses import dataclass, field

from game.state import GameState
from engine.action import Action, ActionType
from data.plants import PlantType, SUN_PRODUCING_PLANTS, ATTACKING_PLANTS, DEFENSIVE_PLANTS

from llm.config import LLMConfig, get_config
from llm.encoder import StateEncoder
from llm.decoder import ResponseDecoder, LLMResponse
from llm.prompt import get_system_prompt, get_emergency_prompt
from llm.context import ContextManager
from llm.client import DeepSeekClient
from llm.emergency import EmergencyHandler
from llm.validator import ActionValidator


@dataclass
class PlayerState:
    """Shared state between fast and LLM loops"""
    
    # Current game state (updated by fast loop)
    game_state: Optional[GameState] = None
    
    # Pending actions from LLM (consumed by fast loop)
    pending_actions: List[Action] = field(default_factory=list)
    
    # Emergency action (highest priority)
    emergency_action: Optional[Action] = None
    
    # Timestamps
    last_llm_call: float = 0.0
    last_action_time: float = 0.0
    last_state_update: float = 0.0
    
    # Status
    running: bool = False
    llm_busy: bool = False
    
    # Statistics
    actions_executed: int = 0
    llm_calls: int = 0
    emergencies_handled: int = 0


class LLMPlayer:
    """
    Main LLM-based player controller.
    
    Uses async architecture:
    - Fast loop (20ms): Emergency handling, action execution
    - LLM loop (1-2s): Strategic decision making
    """
    
    def __init__(self, config: Optional[LLMConfig] = None,
                 state_reader: Optional[Callable[[], Optional[GameState]]] = None,
                 action_executor: Optional[Callable[[Action], bool]] = None):
        """
        Initialize LLM player.
        
        Args:
            config: LLM configuration
            state_reader: Function to read game state
            action_executor: Function to execute actions
        """
        self.config = config or get_config()
        self.state_reader = state_reader
        self.action_executor = action_executor
        
        # Initialize components
        self.encoder = StateEncoder()
        self.decoder = ResponseDecoder()
        self.context = ContextManager(
            max_rounds=self.config.max_history_rounds,
            max_actions=self.config.max_action_history
        )
        self.emergency_handler = EmergencyHandler(
            emergency_x=self.config.emergency_x_threshold,
            emergency_eta=self.config.emergency_eta_threshold
        )
        self.validator = ActionValidator()
        
        # Client initialized lazily
        self._client: Optional[DeepSeekClient] = None
        
        # Shared state
        self.state = PlayerState()
        
        # Callbacks
        self.on_action: Optional[Callable[[Action, bool], None]] = None
        self.on_llm_response: Optional[Callable[[LLMResponse], None]] = None
        self.on_emergency: Optional[Callable[[Action], None]] = None
    
    @property
    def client(self) -> DeepSeekClient:
        """Get or create DeepSeek client"""
        if self._client is None:
            self._client = DeepSeekClient(self.config)
        return self._client
    
    async def start(self) -> None:
        """Start the player loops"""
        self.state.running = True
        
        # Run both loops concurrently
        await asyncio.gather(
            self._fast_loop(),
            self._llm_loop()
        )
    
    async def stop(self) -> None:
        """Stop the player"""
        self.state.running = False
    
    async def _fast_loop(self) -> None:
        """
        Fast loop (20ms interval).
        
        Handles:
        - State reading
        - Emergency detection and handling
        - Action execution
        """
        while self.state.running:
            try:
                # Read current state
                if self.state_reader:
                    game_state = self.state_reader()
                    if game_state:
                        self.state.game_state = game_state
                        self.state.last_state_update = time.time()
                
                if self.state.game_state:
                    # Check for emergencies
                    await self._handle_emergencies()
                    
                    # Execute pending actions
                    await self._execute_pending_actions()
                
                await asyncio.sleep(self.config.fast_loop_interval)
                
            except Exception as e:
                print(f"[LLM Player] Fast loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _llm_loop(self) -> None:
        """
        LLM loop (1-2s interval).
        
        Handles:
        - State encoding
        - LLM API calls
        - Response decoding
        - Action planning
        """
        while self.state.running:
            try:
                # Wait for minimum interval
                elapsed = time.time() - self.state.last_llm_call
                if elapsed < self.config.llm_interval:
                    await asyncio.sleep(self.config.llm_interval - elapsed)
                
                if not self.state.game_state:
                    await asyncio.sleep(0.5)
                    continue
                
                # Call LLM for decisions
                await self._call_llm()
                
            except Exception as e:
                print(f"[LLM Player] LLM loop error: {e}")
                await asyncio.sleep(1.0)
    
    async def _handle_emergencies(self) -> None:
        """Check and handle emergency situations"""
        if not self.state.game_state:
            return
        
        emergency = self.emergency_handler.check(self.state.game_state)
        
        if emergency:
            self.state.emergency_action = emergency.action
            self.state.emergencies_handled += 1
            
            if self.on_emergency:
                self.on_emergency(emergency.action)
            
            # Execute immediately
            await self._execute_action(emergency.action)
    
    async def _execute_pending_actions(self) -> None:
        """Execute pending actions from LLM"""
        if not self.state.pending_actions or not self.state.game_state:
            return
        
        # Rate limit execution
        if time.time() - self.state.last_action_time < 0.1:
            return
        
        # Get highest priority valid action
        for action in self.state.pending_actions:
            if action.is_wait:
                continue
            
            # Re-validate against current state
            result = self.validator.validate(action, self.state.game_state)
            
            if result.valid:
                success = await self._execute_action(result.action)
                if success:
                    self.state.pending_actions.remove(action)
                    return
            else:
                # Remove invalid action
                self.state.pending_actions.remove(action)
                
                # Record failure
                self.encoder.add_action_to_history(
                    clock=self.state.game_state.game_clock,
                    action_type="plant" if action.is_plant_action else action.type_name.lower(),
                    plant_type=action.plant_type if action.is_plant_action else None,
                    row=action.row,
                    col=action.col,
                    success=False,
                    error=result.error
                )
                return
    
    async def _execute_action(self, action: Action) -> bool:
        """Execute a single action"""
        if not self.action_executor or not self.state.game_state:
            return False
        
        success = self.action_executor(action)
        self.state.last_action_time = time.time()
        
        if success:
            self.state.actions_executed += 1
            
            # Record in history
            self.encoder.add_action_to_history(
                clock=self.state.game_state.game_clock,
                action_type="plant" if action.is_plant_action else action.type_name.lower(),
                plant_type=action.plant_type if action.is_plant_action else None,
                row=action.row,
                col=action.col,
                success=True
            )
        
        if self.on_action:
            self.on_action(action, success)
        
        return success
    
    async def _call_llm(self) -> None:
        """Make LLM API call for strategic decisions"""
        if self.state.llm_busy or not self.state.game_state:
            return
        
        self.state.llm_busy = True
        
        try:
            game_state = self.state.game_state
            
            # Encode current state
            state_yaml = self.encoder.encode(game_state)
            
            # Get emergencies for prompt adjustment
            emergencies = self.encoder._detect_emergencies(game_state)
            
            # Select appropriate prompt
            if emergencies:
                system_prompt = get_emergency_prompt(emergencies)
            else:
                system_prompt = get_system_prompt()
            
            # Update context with game summary
            self._update_context_summary(game_state)
            
            # Build messages
            messages = self.context.get_messages_for_llm(state_yaml, system_prompt)
            
            # Call LLM
            response_text = await self.client.chat_with_retry(messages)
            
            # Decode response
            llm_response = self.decoder.decode(response_text)
            
            # Add to context
            self.context.add_round(
                user_message=state_yaml,
                assistant_response=response_text,
                game_clock=game_state.game_clock,
                wave=game_state.wave
            )
            
            # Process actions
            if llm_response.actions:
                # Validate all actions
                valid_actions = []
                for action in llm_response.actions:
                    result = self.validator.validate(action, game_state)
                    if result.valid:
                        valid_actions.append(result.action)
                
                self.state.pending_actions = valid_actions
            
            self.state.llm_calls += 1
            self.state.last_llm_call = time.time()
            
            if self.on_llm_response:
                self.on_llm_response(llm_response)
                
        finally:
            self.state.llm_busy = False
    
    def _update_context_summary(self, game_state: GameState) -> None:
        """Update context with game summary"""
        # Count plants by type
        sunflower_count = sum(
            1 for p in game_state.alive_plants 
            if p.type in SUN_PRODUCING_PLANTS
        )
        attacker_count = sum(
            1 for p in game_state.alive_plants 
            if p.type in ATTACKING_PLANTS
        )
        defender_count = sum(
            1 for p in game_state.alive_plants 
            if p.type in DEFENSIVE_PLANTS
        )
        
        # Count lawnmowers
        lawnmowers = sum(1 for r in range(5) if game_state.has_lawnmower(r))
        
        self.context.update_summary(
            wave=game_state.wave,
            total_waves=game_state.total_waves,
            sunflower_count=sunflower_count,
            attacker_count=attacker_count,
            defender_count=defender_count,
            lawnmowers_remaining=lawnmowers
        )
    
    def get_status(self) -> dict:
        """Get current player status"""
        return {
            "running": self.state.running,
            "llm_busy": self.state.llm_busy,
            "pending_actions": len(self.state.pending_actions),
            "actions_executed": self.state.actions_executed,
            "llm_calls": self.state.llm_calls,
            "emergencies_handled": self.state.emergencies_handled,
            "last_state_update": self.state.last_state_update,
        }
    
    def reset(self) -> None:
        """Reset player state"""
        self.state = PlayerState()
        self.context.clear()
        self.encoder.action_history.clear()


async def create_player(api_key: str,
                        state_reader: Optional[Callable[[], Optional[GameState]]] = None,
                        action_executor: Optional[Callable[[Action], bool]] = None) -> LLMPlayer:
    """
    Create and configure an LLM player.
    
    Args:
        api_key: DeepSeek API key
        state_reader: Function to read game state
        action_executor: Function to execute actions
        
    Returns:
        Configured LLMPlayer instance
    """
    config = get_config()
    config.api_key = api_key
    
    return LLMPlayer(
        config=config,
        state_reader=state_reader,
        action_executor=action_executor
    )
