"""
Configuration File
Contains all configurable settings for the PVZ bot
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BotConfig:
    """Bot configuration settings"""
    
    # ========================================================================
    # General Settings
    # ========================================================================
    
    # Whether to automatically plant
    auto_plant: bool = True
    
    # Whether to automatically collect sun
    auto_collect_sun: bool = True
    
    # Interval between actions (seconds)
    action_interval: float = 0.15
    
    # Main loop refresh rate (seconds)
    refresh_rate: float = 0.05
    
    # ========================================================================
    # Debug Settings
    # ========================================================================
    
    # Enable debug output
    debug: bool = False
    
    # Log level (0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR)
    log_level: int = 1
    
    # Log to file path (None = console only)
    log_file: Optional[str] = None
    
    # ========================================================================
    # Economy Settings
    # ========================================================================
    
    # Target number of sun-producing plant units
    target_sun_plants: int = 8
    
    # Columns to prioritize for sunflowers
    sunflower_columns: List[int] = field(default_factory=lambda: [0, 1])
    
    # ========================================================================
    # Defense Settings
    # ========================================================================
    
    # Column for defensive plants (walls)
    defense_column: int = 4
    
    # X coordinate considered dangerous
    danger_x: int = 200
    
    # X coordinate considered critical
    critical_x: int = 100
    
    # ========================================================================
    # Optimizer Settings
    # ========================================================================
    
    # Weights for action evaluation
    threat_weight: float = 2.0
    efficiency_weight: float = 1.0
    strategic_weight: float = 1.5
    urgency_weight: float = 3.0
    
    # ========================================================================
    # Strategy Settings
    # ========================================================================
    
    # Rows to manage (depends on scene type)
    row_count: int = 5
    
    # Emergency threat threshold
    emergency_threshold: float = 8.0
    
    # High threat threshold
    high_threat_threshold: float = 5.0


# Default configuration
DEFAULT_CONFIG = BotConfig()


def load_config(config_path: Optional[str] = None) -> BotConfig:
    """
    Load configuration from file
    
    Args:
        config_path: Path to config file (JSON or YAML)
        
    Returns:
        BotConfig instance
    """
    if config_path is None:
        return BotConfig()
    
    # TODO: Implement config file loading
    # For now, return default config
    return BotConfig()


def save_config(config: BotConfig, config_path: str):
    """
    Save configuration to file
    
    Args:
        config: Configuration to save
        config_path: Path to save config file
    """
    # TODO: Implement config file saving
    pass
