"""
Projectile Data from re-plants-vs-zombies
Contains all projectile types with damage values and special effects

数据来源:
- re-plants-vs-zombies Projectile.cpp gProjectileDefinition[] (line 14-28)
- https://github.com/Patoke/re-plants-vs-zombies

单位说明:
- damage: HP damage per hit
- splash_radius: grid cells (1 cell ≈ 80 pixels)
"""

from enum import IntEnum
from typing import NamedTuple, Optional


class ProjectileType(IntEnum):
    """
    All projectile types in PVZ
    Source: re-plants-vs-zombies ConstEnums.h ProjectileType enum
    """
    PEA = 0                 # 普通豌豆
    SNOW_PEA = 1            # 寒冰豌豆
    CABBAGE = 2             # 卷心菜
    MELON = 3               # 西瓜
    PUFF = 4                # 小喷菇孢子
    WINTERMELON = 5         # 冰西瓜
    FIRE_PEA = 6            # 火焰豌豆 (通过火炬树桩)
    STAR = 7                # 杨桃星星
    CACTUS_SPIKE = 8        # 仙人掌尖刺
    FUME = 9                # 大喷菇烟雾 (not actually a projectile, but tracked)
    BASKETBALL = 10         # 投篮僵尸的篮球
    COB = 11                # 玉米炮炮弹
    BUTTER = 12             # 玉米投手黄油
    KERNEL = 13             # 玉米投手玉米粒
    ZOMBIE_PEA = 14         # 豌豆僵尸的豌豆


class ProjectileProperties(NamedTuple):
    """
    Properties for a projectile type
    
    Attributes:
        damage: Base damage dealt to zombies (HP)
        splash: Whether projectile deals splash/AOE damage
        splash_damage: Damage dealt to zombies in splash radius (if different from main)
        splash_radius: Radius of splash effect in grid cells (1 cell ≈ 80px)
        slow_effect: Whether projectile slows zombies
        pierce: Whether projectile pierces through zombies (hits all in line)
        homing: Whether projectile tracks/follows zombies
        stun: Whether projectile stuns/immobilizes zombies
    """
    damage: int
    splash: bool = False
    splash_damage: Optional[int] = None
    splash_radius: float = 0.0
    slow_effect: bool = False
    pierce: bool = False
    homing: bool = False
    stun: bool = False


# ============================================================================
# Projectile Properties
# Source: re-plants-vs-zombies Projectile.cpp gProjectileDefinition[] (line 14-28)
# ============================================================================

PROJECTILE_PROPERTIES: dict[ProjectileType, ProjectileProperties] = {
    # Source: Projectile.cpp line 14: PROJECTILE_PEA damage=20
    ProjectileType.PEA: ProjectileProperties(
        damage=20,
    ),
    
    # Source: Projectile.cpp line 15: PROJECTILE_SNOWPEA damage=20
    ProjectileType.SNOW_PEA: ProjectileProperties(
        damage=20,
        slow_effect=True,  # Slows zombies
    ),
    
    # Source: Projectile.cpp line 16: PROJECTILE_CABBAGE damage=40
    ProjectileType.CABBAGE: ProjectileProperties(
        damage=40,
    ),
    
    # Source: Projectile.cpp line 17: PROJECTILE_MELON damage=80
    # Melon deals splash damage in a small radius
    ProjectileType.MELON: ProjectileProperties(
        damage=80,          # Direct hit damage
        splash=True,
        splash_damage=60,   # Splash to nearby zombies
        splash_radius=1.5,  # ~1.5 grid cells
    ),
    
    # Source: Projectile.cpp line 18: PROJECTILE_PUFF damage=20
    ProjectileType.PUFF: ProjectileProperties(
        damage=20,
    ),
    
    # Source: Projectile.cpp line 19: PROJECTILE_WINTERMELON damage=80
    ProjectileType.WINTERMELON: ProjectileProperties(
        damage=80,
        splash=True,
        splash_damage=60,
        splash_radius=1.5,
        slow_effect=True,   # Slows all zombies in splash
    ),
    
    # Source: Projectile.cpp line 20: PROJECTILE_FIREBALL damage=40
    # Fire pea is created when pea passes through Torchwood
    ProjectileType.FIRE_PEA: ProjectileProperties(
        damage=40,          # 2x normal pea damage
        splash=True,        # Small splash effect
        splash_damage=40,
        splash_radius=0.5,
    ),
    
    # Source: Projectile.cpp line 21: PROJECTILE_STAR damage=20
    ProjectileType.STAR: ProjectileProperties(
        damage=20,
    ),
    
    # Cactus spike (same as pea)
    ProjectileType.CACTUS_SPIKE: ProjectileProperties(
        damage=20,
    ),
    
    # Fume-shroom fume (pierces through zombies)
    # Source: Damage same as pea but pierces
    ProjectileType.FUME: ProjectileProperties(
        damage=20,
        pierce=True,        # Hits all zombies in range
    ),
    
    # Source: Projectile.cpp line 23: PROJECTILE_BASKETBALL damage=75
    # Thrown by Catapult Zombie
    ProjectileType.BASKETBALL: ProjectileProperties(
        damage=75,
    ),
    
    # Source: Projectile.cpp line 25: PROJECTILE_COBBIG damage=300
    # Cob Cannon projectile - massive AOE
    ProjectileType.COB: ProjectileProperties(
        damage=300,
        splash=True,
        splash_damage=300,  # Full damage in splash radius
        splash_radius=1.5,  # 3x3 grid area
    ),
    
    # Source: Projectile.cpp line 26: PROJECTILE_BUTTER damage=40
    # Kernel-pult butter - stuns zombie
    ProjectileType.BUTTER: ProjectileProperties(
        damage=40,
        stun=True,          # Immobilizes zombie
    ),
    
    # Source: Projectile.cpp line 24: PROJECTILE_KERNEL damage=20
    ProjectileType.KERNEL: ProjectileProperties(
        damage=20,
    ),
    
    # Source: Projectile.cpp line 27: PROJECTILE_ZOMBIE_PEA damage=20
    # Fired by Peashooter Zombie (in I, Zombie levels)
    ProjectileType.ZOMBIE_PEA: ProjectileProperties(
        damage=20,
    ),
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_projectile_damage(projectile_type: ProjectileType) -> int:
    """Get base damage for a projectile type"""
    props = PROJECTILE_PROPERTIES.get(projectile_type)
    if props:
        return props.damage
    return 0


def get_projectile_properties(
    projectile_type: ProjectileType
) -> Optional[ProjectileProperties]:
    """Get full properties for a projectile type"""
    return PROJECTILE_PROPERTIES.get(projectile_type)


def is_slowing_projectile(projectile_type: ProjectileType) -> bool:
    """Check if projectile type slows zombies"""
    props = PROJECTILE_PROPERTIES.get(projectile_type)
    return props.slow_effect if props else False


def is_splash_projectile(projectile_type: ProjectileType) -> bool:
    """Check if projectile type deals splash damage"""
    props = PROJECTILE_PROPERTIES.get(projectile_type)
    return props.splash if props else False


def is_piercing_projectile(projectile_type: ProjectileType) -> bool:
    """Check if projectile type pierces through zombies"""
    props = PROJECTILE_PROPERTIES.get(projectile_type)
    return props.pierce if props else False
