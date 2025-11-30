"""
LLM Configuration

DeepSeek API settings for the LLM game player.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for LLM API"""
    
    # API Settings
    api_key: str = "sk-xxx"  # User needs to fill in
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"  # V3.2-Exp
    
    # Request settings
    temperature: float = 0.3  # Lower for more deterministic decisions
    max_tokens: int = 1024
    timeout: float = 10.0  # API timeout in seconds
    
    # Game loop settings
    llm_interval: float = 1.5  # Seconds between LLM calls
    fast_loop_interval: float = 0.02  # 20ms fast loop for emergency handling
    
    # Context settings
    max_history_rounds: int = 6  # Sliding window size
    max_action_history: int = 10  # Recent actions to track
    
    # Emergency thresholds
    emergency_x_threshold: int = 150  # Zombie x position for emergency
    emergency_eta_threshold: int = 200  # Time to reach home (cs)


# Global config instance
_config: Optional[LLMConfig] = None


def get_config() -> LLMConfig:
    """Get global LLM configuration"""
    global _config
    if _config is None:
        _config = LLMConfig()
    return _config


def set_config(config: LLMConfig) -> None:
    """Set global LLM configuration"""
    global _config
    _config = config
