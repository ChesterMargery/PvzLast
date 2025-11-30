"""
Collision Detection Module
Implements precise collision/hit detection from AVZ judge.h

All coordinate values are in pixels.
The game grid has columns 0-8 (left to right) and rows 0-5 (top to bottom).
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass

from data.constants import (
    COB_EXPLODE_RADIUS,
    CHERRY_EXPLODE_RADIUS,
    GRID_WIDTH,
    LAWN_LEFT_X,
)
from data.zombies import (
    GARG_HAMMER_RANGE_LEFT,
    GARG_HAMMER_RANGE_RIGHT,
)


def col_to_x(col: int) -> float:
    """Convert column to x coordinate (center of cell)"""
    return LAWN_LEFT_X + col * GRID_WIDTH + GRID_WIDTH / 2


def x_to_col(x: float) -> int:
    """Convert x coordinate to column"""
    return max(0, min(8, int((x - LAWN_LEFT_X) / GRID_WIDTH)))


# ============================================================================
# Cherry Bomb Collision
# ============================================================================

def is_cherry_hit(zombie_x: float, zombie_row: int, 
                  cherry_col: int, cherry_row: int) -> bool:
    """
    Check if a zombie would be hit by a cherry bomb
    
    Cherry bomb has a circular explosion radius of about 90 pixels.
    It affects all zombies within 1 row above and below.
    
    Args:
        zombie_x: Zombie x position
        zombie_row: Zombie row
        cherry_col: Column where cherry is planted
        cherry_row: Row where cherry is planted
        
    Returns:
        True if zombie would be hit
    """
    # Check row range (cherry affects ±1 row)
    if abs(zombie_row - cherry_row) > 1:
        return False
    
    # Cherry x position (center of cell)
    cherry_x = col_to_x(cherry_col)
    
    # Check distance
    distance = abs(zombie_x - cherry_x)
    return distance <= CHERRY_EXPLODE_RADIUS + 20  # Extra margin for zombie width


def get_cherry_hit_range(cherry_col: int) -> Tuple[float, float]:
    """
    Get the x-range where cherry bomb will hit
    
    Based on AVZ judge.h: 6列樱桃 left=264+10, right=612
    
    Args:
        cherry_col: Column where cherry is planted
        
    Returns:
        (left_x, right_x) hit range
    """
    cherry_x = col_to_x(cherry_col)
    return (cherry_x - CHERRY_EXPLODE_RADIUS - 20, 
            cherry_x + CHERRY_EXPLODE_RADIUS + 20)


# ============================================================================
# Cob Cannon Collision
# ============================================================================

def is_cob_hit(zombie_x: float, zombie_y: float, zombie_row: int,
               cob_target_x: float, cob_target_y: float) -> bool:
    """
    Check if a zombie would be hit by a cob cannon blast
    
    Cob cannon has a circular explosion with radius of 115 pixels.
    It affects zombies within about ±1 row of the target row.
    
    Args:
        zombie_x: Zombie x position
        zombie_y: Zombie y position
        zombie_row: Zombie row
        cob_target_x: Target x coordinate
        cob_target_y: Target y coordinate
        
    Returns:
        True if zombie would be hit
    """
    # Calculate distance from explosion center
    dx = zombie_x - cob_target_x
    dy = zombie_y - cob_target_y
    distance = math.sqrt(dx * dx + dy * dy)
    
    return distance <= COB_EXPLODE_RADIUS


def is_cob_hit_simple(zombie_x: float, zombie_row: int,
                      cob_col: float, cob_row: int) -> bool:
    """
    Simplified cob hit check using column/row
    
    Args:
        zombie_x: Zombie x position
        zombie_row: Zombie row
        cob_col: Target column (can be float for precision)
        cob_row: Target row
        
    Returns:
        True if zombie would be hit
    """
    # Check row range (cob affects approximately ±1.5 rows)
    if abs(zombie_row - cob_row) > 1:
        return False
    
    # Target x position
    target_x = LAWN_LEFT_X + cob_col * GRID_WIDTH
    
    distance = abs(zombie_x - target_x)
    return distance <= COB_EXPLODE_RADIUS


def get_cob_hit_range(cob_col: float) -> Tuple[float, float]:
    """
    Get the x-range where cob cannon will hit
    
    Args:
        cob_col: Target column
        
    Returns:
        (left_x, right_x) hit range
    """
    target_x = LAWN_LEFT_X + cob_col * GRID_WIDTH
    return (target_x - COB_EXPLODE_RADIUS, target_x + COB_EXPLODE_RADIUS)


# ============================================================================
# Jalapeno Collision
# ============================================================================

def is_jalapeno_hit(zombie_row: int, jalapeno_row: int) -> bool:
    """
    Check if a zombie would be hit by jalapeno
    
    Jalapeno kills all zombies in its row.
    
    Args:
        zombie_row: Zombie row
        jalapeno_row: Row where jalapeno is planted
        
    Returns:
        True if zombie would be hit
    """
    return zombie_row == jalapeno_row


# ============================================================================
# Doom-shroom Collision
# ============================================================================

def is_doom_hit(zombie_x: float, zombie_row: int,
                doom_col: int, doom_row: int) -> bool:
    """
    Check if a zombie would be hit by doom-shroom
    
    Doom-shroom has a larger explosion radius than cherry bomb,
    approximately 3x3 cells centered on the doom-shroom.
    
    Args:
        zombie_x: Zombie x position
        zombie_row: Zombie row
        doom_col: Column where doom-shroom is planted
        doom_row: Row where doom-shroom is planted
        
    Returns:
        True if zombie would be hit
    """
    # Check row range (doom affects approximately ±1.5 rows)
    if abs(zombie_row - doom_row) > 1:
        return False
    
    # Doom x position
    doom_x = col_to_x(doom_col)
    
    # Doom has larger radius than cherry
    doom_radius = 150
    distance = abs(zombie_x - doom_x)
    return distance <= doom_radius


# ============================================================================
# Gargantuar Hammer Attack
# ============================================================================

def is_giga_hammer(zombie_x: float, zombie_row: int,
                   plant_x: float, plant_row: int) -> bool:
    """
    Check if a Gargantuar can hammer a plant
    
    Gargantuar attack range: x-30 to x+59 from zombie position.
    
    Args:
        zombie_x: Gargantuar x position
        zombie_row: Gargantuar row
        plant_x: Plant x position
        plant_row: Plant row
        
    Returns:
        True if plant is in hammer range
    """
    # Must be same row
    if zombie_row != plant_row:
        return False
    
    # Check x range
    left_bound = zombie_x + GARG_HAMMER_RANGE_LEFT
    right_bound = zombie_x + GARG_HAMMER_RANGE_RIGHT
    
    return left_bound <= plant_x <= right_bound


def get_hammer_danger_zone(zombie_x: float) -> Tuple[float, float]:
    """
    Get the x-range where a Gargantuar can hammer
    
    Args:
        zombie_x: Gargantuar x position
        
    Returns:
        (left_x, right_x) danger zone
    """
    return (zombie_x + GARG_HAMMER_RANGE_LEFT, 
            zombie_x + GARG_HAMMER_RANGE_RIGHT)


# ============================================================================
# Jack-in-the-Box Explosion
# ============================================================================

def is_box_explode(zombie_x: float, zombie_y: float,
                   plant_x: float, plant_y: float) -> bool:
    """
    Check if a plant would be destroyed by Jack-in-the-box explosion
    
    Jack-in-the-box has a circular explosion with radius of about 90 pixels.
    
    Args:
        zombie_x: Jack-in-box x position
        zombie_y: Jack-in-box y position
        plant_x: Plant x position
        plant_y: Plant y position
        
    Returns:
        True if plant would be destroyed
    """
    box_radius = 90
    dx = plant_x - zombie_x
    dy = plant_y - zombie_y
    distance = math.sqrt(dx * dx + dy * dy)
    return distance <= box_radius


# ============================================================================
# Zomboni Crush Detection
# ============================================================================

def is_will_be_crushed(zombie_x: float, zombie_row: int,
                       plant_x: float, plant_row: int,
                       zombie_speed: float = 0.44) -> bool:
    """
    Check if a plant will be crushed by Zomboni
    
    Zomboni crushes plants in its path in the same row.
    
    Args:
        zombie_x: Zomboni x position
        zombie_row: Zomboni row
        plant_x: Plant x position
        plant_row: Plant row
        zombie_speed: Zomboni speed
        
    Returns:
        True if plant will be crushed
    """
    # Must be same row
    if zombie_row != plant_row:
        return False
    
    # Zomboni must be to the right of plant and moving left
    if zombie_x <= plant_x:
        return False
    
    return True  # Will eventually crush the plant


# ============================================================================
# Pea Projectile Hit Detection
# ============================================================================

def is_pea_hit(pea_x: float, pea_row: int,
               zombie_x: float, zombie_row: int,
               zombie_width: float = 20) -> bool:
    """
    Check if a pea projectile would hit a zombie
    
    Args:
        pea_x: Pea x position
        pea_row: Pea row
        zombie_x: Zombie x position
        zombie_row: Zombie row
        zombie_width: Zombie hitbox width
        
    Returns:
        True if pea would hit zombie
    """
    # Must be same row
    if pea_row != zombie_row:
        return False
    
    # Check if pea x overlaps with zombie hitbox
    return abs(pea_x - zombie_x) <= zombie_width


# ============================================================================
# Splash Damage (Melon/Winter Melon)
# ============================================================================

def get_melon_splash_targets(impact_x: float, impact_row: int,
                             splash_radius: float = 80) -> Tuple[float, float, int, int]:
    """
    Get the splash damage range for melon projectiles
    
    Args:
        impact_x: X coordinate of impact
        impact_row: Row of impact
        splash_radius: Splash damage radius
        
    Returns:
        (left_x, right_x, min_row, max_row)
    """
    return (
        impact_x - splash_radius,
        impact_x + splash_radius,
        max(0, impact_row - 1),
        min(5, impact_row + 1)
    )
