"""
Zombie Data from AsmVsZombies
Contains all 33 zombie types with HP, movement speed, and special abilities
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional


class ZombieType(IntEnum):
    """All zombie types in PVZ"""
    ZOMBIE = 0  # 普通僵尸
    FLAG = 1  # 旗帜僵尸
    CONEHEAD = 2  # 路障僵尸
    POLEVAULTER = 3  # 撑杆僵尸
    BUCKETHEAD = 4  # 铁桶僵尸
    NEWSPAPER = 5  # 读报僵尸
    SCREENDOOR = 6  # 铁栅门僵尸
    FOOTBALL = 7  # 橄榄球僵尸
    DANCING = 8  # 舞王僵尸
    BACKUP = 9  # 伴舞僵尸
    DUCKYTUBE = 10  # 鸭子救生圈僵尸
    SNORKEL = 11  # 潜水僵尸
    ZOMBONI = 12  # 冰车僵尸
    BOBSLED = 13  # 雪橇僵尸
    DOLPHIN = 14  # 海豚骑士僵尸
    JACKINBOX = 15  # 小丑僵尸
    BALLOON = 16  # 气球僵尸
    DIGGER = 17  # 矿工僵尸
    POGO = 18  # 跳跳僵尸
    YETI = 19  # 雪人僵尸
    BUNGEE = 20  # 蹦极僵尸
    LADDER = 21  # 扶梯僵尸
    CATAPULT = 22  # 投篮僵尸
    GARGANTUAR = 23  # 巨人僵尸
    IMP = 24  # 小鬼僵尸
    ZOMBOSS = 25  # 僵尸博士
    # 26-31 unused
    GIGA_GARGANTUAR = 32  # 红眼巨人


@dataclass
class ZombieData:
    """Complete data for a zombie type"""
    type: ZombieType
    name_en: str
    name_cn: str
    body_hp: int  # 本体血量
    accessory_hp: int  # 防具血量 (路障/铁桶/门/梯子等)
    speed: float  # 基础速度 (像素/cs)
    has_flying: bool  # 是否可飞行
    has_special: bool  # 是否有特殊能力


# Zombie HP (body + accessory)
# Format: (body_hp, accessory_hp)
ZOMBIE_HP_DATA = {
    ZombieType.ZOMBIE: (200, 0),
    ZombieType.FLAG: (200, 0),
    ZombieType.CONEHEAD: (200, 370),
    ZombieType.POLEVAULTER: (500, 0),
    ZombieType.BUCKETHEAD: (200, 1100),
    ZombieType.NEWSPAPER: (200, 150),
    ZombieType.SCREENDOOR: (200, 1100),
    ZombieType.FOOTBALL: (1600, 0),  # Has internal armor
    ZombieType.DANCING: (500, 0),
    ZombieType.BACKUP: (200, 0),
    ZombieType.DUCKYTUBE: (200, 0),  # HP depends on base zombie
    ZombieType.SNORKEL: (200, 0),
    ZombieType.ZOMBONI: (1350, 0),  # Ice machine HP
    ZombieType.BOBSLED: (200, 0),
    ZombieType.DOLPHIN: (500, 0),
    ZombieType.JACKINBOX: (500, 0),
    ZombieType.BALLOON: (200, 200),  # Balloon + zombie
    ZombieType.DIGGER: (300, 100),  # Mining helmet
    ZombieType.POGO: (500, 0),  # Pogo stick
    ZombieType.YETI: (1350, 0),
    ZombieType.BUNGEE: (450, 0),
    ZombieType.LADDER: (500, 500),  # Body + ladder
    ZombieType.CATAPULT: (850, 0),  # Basketball machine
    ZombieType.GARGANTUAR: (3000, 0),
    ZombieType.IMP: (300, 0),
    ZombieType.ZOMBOSS: (40000, 0),  # Dr. Zomboss
    ZombieType.GIGA_GARGANTUAR: (6000, 0),
}


def get_zombie_total_hp(zombie_type: ZombieType) -> int:
    """Get total HP (body + accessory) for a zombie type"""
    body, accessory = ZOMBIE_HP_DATA.get(zombie_type, (200, 0))
    return body + accessory


def get_zombie_body_hp(zombie_type: ZombieType) -> int:
    """Get body HP for a zombie type"""
    body, _ = ZOMBIE_HP_DATA.get(zombie_type, (200, 0))
    return body


def get_zombie_accessory_hp(zombie_type: ZombieType) -> int:
    """Get accessory HP for a zombie type"""
    _, accessory = ZOMBIE_HP_DATA.get(zombie_type, (200, 0))
    return accessory


# Zombie base speed (pixels per centisecond)
# Normal walking speed before any modifiers
ZOMBIE_BASE_SPEED = {
    ZombieType.ZOMBIE: 0.23,
    ZombieType.FLAG: 0.36,  # Faster than normal
    ZombieType.CONEHEAD: 0.23,
    ZombieType.POLEVAULTER: 0.48,  # Before jump: very fast
    ZombieType.BUCKETHEAD: 0.23,
    ZombieType.NEWSPAPER: 0.23,  # Becomes 0.68 when angry
    ZombieType.SCREENDOOR: 0.23,
    ZombieType.FOOTBALL: 0.68,  # Very fast
    ZombieType.DANCING: 0.13,  # Slow
    ZombieType.BACKUP: 0.33,
    ZombieType.DUCKYTUBE: 0.23,  # Water speed
    ZombieType.SNORKEL: 0.23,
    ZombieType.ZOMBONI: 0.44,  # Ice machine
    ZombieType.BOBSLED: 0.68,  # On ice track
    ZombieType.DOLPHIN: 0.93,  # Very fast in water
    ZombieType.JACKINBOX: 0.82,
    ZombieType.BALLOON: 0.3,  # Flying
    ZombieType.DIGGER: 0.12,  # Underground
    ZombieType.POGO: 0.5,  # Bouncing
    ZombieType.YETI: 0.23,
    ZombieType.BUNGEE: 0.0,  # Descends from sky
    ZombieType.LADDER: 0.46,
    ZombieType.CATAPULT: 0.22,
    ZombieType.GARGANTUAR: 0.15,  # Slow
    ZombieType.IMP: 0.6,  # Fast
    ZombieType.ZOMBOSS: 0.0,  # Stationary
    ZombieType.GIGA_GARGANTUAR: 0.15,
}

# Average speed for Giga Gargantuar with attack time factored in
GIGA_AVG_SPEED = 484 / 3158 * 1.25  # ≈ 0.192 px/cs

# Speed when slowed (50% of normal)
SLOW_SPEED_MULTIPLIER = 0.5

# Speed when frozen (0)
FROZEN_SPEED = 0.0


# ============================================================================
# Special Zombie Abilities
# ============================================================================

# Zombies that can jump over plants
JUMPING_ZOMBIES = {
    ZombieType.POLEVAULTER,
    ZombieType.POGO,
    ZombieType.DOLPHIN,
}

# Zombies that fly (need Blover/Cactus)
FLYING_ZOMBIES = {
    ZombieType.BALLOON,
    ZombieType.BUNGEE,
}

# Zombies with shields (need Magnet-shroom or Fume-shroom)
SHIELD_ZOMBIES = {
    ZombieType.SCREENDOOR,
    ZombieType.LADDER,
}

# Metal zombies (can be affected by Magnet-shroom)
METAL_ZOMBIES = {
    ZombieType.BUCKETHEAD,
    ZombieType.SCREENDOOR,
    ZombieType.FOOTBALL,
    ZombieType.LADDER,
    ZombieType.POGO,
    ZombieType.JACKINBOX,
    ZombieType.DIGGER,
}

# Zombies immune to instant kill (Gargantuar takes half damage)
GARGANTUAR_ZOMBIES = {
    ZombieType.GARGANTUAR,
    ZombieType.GIGA_GARGANTUAR,
}

# Zombies that crush plants (don't eat, just destroy)
CRUSHING_ZOMBIES = {
    ZombieType.ZOMBONI,
    ZombieType.GARGANTUAR,
    ZombieType.GIGA_GARGANTUAR,
    ZombieType.CATAPULT,
}

# Underground zombies (need special plants)
UNDERGROUND_ZOMBIES = {
    ZombieType.DIGGER,
}

# Water zombies
WATER_ZOMBIES = {
    ZombieType.DUCKYTUBE,
    ZombieType.SNORKEL,
    ZombieType.DOLPHIN,
}

# ============================================================================
# Gargantuar Specific Constants
# ============================================================================

# HP thresholds for throwing imp
GARG_THROW_IMP_HP_THRESHOLD_1 = 0.5  # First throw at 50% HP
GARG_THROW_IMP_HP_THRESHOLD_2 = 0.25  # Second throw at 25% HP (Giga only)

# Hammer attack range (from zombie x position)
GARG_HAMMER_RANGE_LEFT = -30
GARG_HAMMER_RANGE_RIGHT = 59

# Time for hammer attack animation (cs)
GARG_HAMMER_TIME = 105  # Also 210 for second imp throw


# ============================================================================
# Zombie Animation Timing
# ============================================================================

# Eating speed (damage per cs to plants)
ZOMBIE_BITE_DAMAGE = 100 / 70  # About 1.43 damage per cs
ZOMBIE_BITE_INTERVAL = 70  # cs between bites (100 damage per bite at 70cs interval)

# Gargantuar smash damage (instant kill plants)
GARG_SMASH_DAMAGE = 300  # Kills any plant in one hit


# ============================================================================
# Helper Functions
# ============================================================================

def is_dangerous_zombie(zombie_type: ZombieType) -> bool:
    """Check if zombie type is considered dangerous (priority target)"""
    return zombie_type in {
        ZombieType.GARGANTUAR,
        ZombieType.GIGA_GARGANTUAR,
        ZombieType.FOOTBALL,
        ZombieType.ZOMBONI,
        ZombieType.JACKINBOX,
        ZombieType.DOLPHIN,
        ZombieType.POGO,
        ZombieType.DIGGER,
    }


def is_fast_zombie(zombie_type: ZombieType) -> bool:
    """Check if zombie type is fast moving"""
    return ZOMBIE_BASE_SPEED.get(zombie_type, 0.23) >= 0.4


def can_be_frozen(zombie_type: ZombieType) -> bool:
    """Check if zombie type can be frozen"""
    # All zombies except Zomboss can be frozen
    return zombie_type != ZombieType.ZOMBOSS


def can_be_slowed(zombie_type: ZombieType) -> bool:
    """Check if zombie type can be slowed"""
    # All zombies except Zomboss can be slowed
    return zombie_type != ZombieType.ZOMBOSS


def is_gargantuar(zombie_type: ZombieType) -> bool:
    """Check if zombie type is a Gargantuar variant"""
    return zombie_type in GARGANTUAR_ZOMBIES


def get_threat_multiplier(zombie_type: ZombieType) -> float:
    """Get threat level multiplier for a zombie type"""
    if zombie_type in {ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR}:
        return 3.0
    elif zombie_type in {ZombieType.FOOTBALL, ZombieType.ZOMBONI}:
        return 2.0
    elif zombie_type in {ZombieType.BUCKETHEAD, ZombieType.SCREENDOOR}:
        return 1.5
    elif zombie_type == ZombieType.BALLOON:
        return 1.8
    elif zombie_type in {ZombieType.JACKINBOX, ZombieType.DIGGER, ZombieType.POGO}:
        return 1.7
    else:
        return 1.0
