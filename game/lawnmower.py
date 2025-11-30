"""
Lawnmower Info Class
Represents a lawnmower entity in the game
"""

from dataclasses import dataclass


@dataclass
class LawnmowerInfo:
    """
    Information about a lawnmower on the field
    
    Contains position, state, and availability information.
    """
    
    index: int  # Index in lawnmower array
    row: int  # Row (0-5)
    x: float  # X position (pixels)
    state: int  # Current state (0=idle, other=moving/used)
    is_dead: bool  # Whether lawnmower is dead/used
    
    @property
    def is_available(self) -> bool:
        """Check if lawnmower is available (not used and idle)"""
        return not self.is_dead and self.state == 0
    
    @property
    def is_moving(self) -> bool:
        """Check if lawnmower is currently moving"""
        return not self.is_dead and self.state != 0
    
    def __repr__(self) -> str:
        status = "available" if self.is_available else ("moving" if self.is_moving else "used")
        return f"LawnmowerInfo(row={self.row}, x={self.x:.1f}, status={status})"
