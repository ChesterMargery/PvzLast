"""
Plant Data from AsmVsZombies
Contains all 48 plant types with damage, attack intervals, range, HP, and collision boxes
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple


class PlantType(IntEnum):
    """All 48 plant types in PVZ"""
    PEASHOOTER = 0
    SUNFLOWER = 1
    CHERRY_BOMB = 2
    WALLNUT = 3
    POTATO_MINE = 4
    SNOW_PEA = 5
    CHOMPER = 6
    REPEATER = 7
    PUFFSHROOM = 8
    SUNSHROOM = 9
    FUMESHROOM = 10
    GRAVEBUSTER = 11
    HYPNOSHROOM = 12
    SCAREDYSHROOM = 13
    ICESHROOM = 14
    DOOMSHROOM = 15
    LILYPAD = 16
    SQUASH = 17
    THREEPEATER = 18
    TANGLEKELP = 19
    JALAPENO = 20
    SPIKEWEED = 21
    TORCHWOOD = 22
    TALLNUT = 23
    SEASHROOM = 24
    PLANTERN = 25
    CACTUS = 26
    BLOVER = 27
    SPLITPEA = 28
    STARFRUIT = 29
    PUMPKIN = 30
    MAGNETSHROOM = 31
    CABBAGEPULT = 32
    FLOWERPOT = 33
    KERNELPULT = 34
    COFFEEBEAN = 35
    GARLIC = 36
    UMBRELLALEAF = 37
    MARIGOLD = 38
    MELONPULT = 39
    GATLINGPEA = 40
    TWINSUNFLOWER = 41
    GLOOMSHROOM = 42
    CATTAIL = 43
    WINTERMELON = 44
    GOLDMAGNET = 45
    SPIKEROCK = 46
    COBCANNON = 47


@dataclass
class PlantData:
    """Complete data for a plant type"""
    type: PlantType
    name_en: str
    name_cn: str
    cost: int
    recharge: int  # cs (centiseconds)
    hp: int
    damage: int
    attack_interval: int  # cs, 0 if not applicable
    is_instant: bool  # Instant kill plant
    is_mushroom: bool  # Needs coffee bean in day
    is_aquatic: bool  # Needs lily pad in water


# Plant sun cost dictionary
PLANT_COST = {
    PlantType.PEASHOOTER: 100,
    PlantType.SUNFLOWER: 50,
    PlantType.CHERRY_BOMB: 150,
    PlantType.WALLNUT: 50,
    PlantType.POTATO_MINE: 25,
    PlantType.SNOW_PEA: 175,
    PlantType.CHOMPER: 150,
    PlantType.REPEATER: 200,
    PlantType.PUFFSHROOM: 0,
    PlantType.SUNSHROOM: 25,
    PlantType.FUMESHROOM: 75,
    PlantType.GRAVEBUSTER: 75,
    PlantType.HYPNOSHROOM: 75,
    PlantType.SCAREDYSHROOM: 25,
    PlantType.ICESHROOM: 75,
    PlantType.DOOMSHROOM: 125,
    PlantType.LILYPAD: 25,
    PlantType.SQUASH: 50,
    PlantType.THREEPEATER: 325,
    PlantType.TANGLEKELP: 25,
    PlantType.JALAPENO: 125,
    PlantType.SPIKEWEED: 100,
    PlantType.TORCHWOOD: 175,
    PlantType.TALLNUT: 125,
    PlantType.SEASHROOM: 0,
    PlantType.PLANTERN: 25,
    PlantType.CACTUS: 125,
    PlantType.BLOVER: 100,
    PlantType.SPLITPEA: 125,
    PlantType.STARFRUIT: 125,
    PlantType.PUMPKIN: 125,
    PlantType.MAGNETSHROOM: 100,
    PlantType.CABBAGEPULT: 100,
    PlantType.FLOWERPOT: 25,
    PlantType.KERNELPULT: 100,
    PlantType.COFFEEBEAN: 75,
    PlantType.GARLIC: 50,
    PlantType.UMBRELLALEAF: 100,
    PlantType.MARIGOLD: 50,
    PlantType.MELONPULT: 300,
    PlantType.GATLINGPEA: 250,
    PlantType.TWINSUNFLOWER: 150,
    PlantType.GLOOMSHROOM: 150,
    PlantType.CATTAIL: 225,
    PlantType.WINTERMELON: 200,
    PlantType.GOLDMAGNET: 50,
    PlantType.SPIKEROCK: 125,
    PlantType.COBCANNON: 500,
}

# Plant HP (health points)
PLANT_HP = {
    PlantType.PEASHOOTER: 300,
    PlantType.SUNFLOWER: 300,
    PlantType.CHERRY_BOMB: 300,
    PlantType.WALLNUT: 4000,
    PlantType.POTATO_MINE: 300,
    PlantType.SNOW_PEA: 300,
    PlantType.CHOMPER: 300,
    PlantType.REPEATER: 300,
    PlantType.PUFFSHROOM: 300,
    PlantType.SUNSHROOM: 300,
    PlantType.FUMESHROOM: 300,
    PlantType.GRAVEBUSTER: 300,
    PlantType.HYPNOSHROOM: 300,
    PlantType.SCAREDYSHROOM: 300,
    PlantType.ICESHROOM: 300,
    PlantType.DOOMSHROOM: 300,
    PlantType.LILYPAD: 300,
    PlantType.SQUASH: 300,
    PlantType.THREEPEATER: 300,
    PlantType.TANGLEKELP: 300,
    PlantType.JALAPENO: 300,
    PlantType.SPIKEWEED: 300,
    PlantType.TORCHWOOD: 300,
    PlantType.TALLNUT: 8000,
    PlantType.SEASHROOM: 300,
    PlantType.PLANTERN: 300,
    PlantType.CACTUS: 300,
    PlantType.BLOVER: 300,
    PlantType.SPLITPEA: 300,
    PlantType.STARFRUIT: 300,
    PlantType.PUMPKIN: 4000,
    PlantType.MAGNETSHROOM: 300,
    PlantType.CABBAGEPULT: 300,
    PlantType.FLOWERPOT: 300,
    PlantType.KERNELPULT: 300,
    PlantType.COFFEEBEAN: 300,
    PlantType.GARLIC: 400,
    PlantType.UMBRELLALEAF: 300,
    PlantType.MARIGOLD: 300,
    PlantType.MELONPULT: 300,
    PlantType.GATLINGPEA: 300,
    PlantType.TWINSUNFLOWER: 300,
    PlantType.GLOOMSHROOM: 300,
    PlantType.CATTAIL: 300,
    PlantType.WINTERMELON: 300,
    PlantType.GOLDMAGNET: 300,
    PlantType.SPIKEROCK: 450,  # 9 times durability
    PlantType.COBCANNON: 300,
}

# Plant recharge time (cs)
PLANT_RECHARGE = {
    PlantType.PEASHOOTER: 750,
    PlantType.SUNFLOWER: 750,
    PlantType.CHERRY_BOMB: 5000,
    PlantType.WALLNUT: 3000,
    PlantType.POTATO_MINE: 3000,
    PlantType.SNOW_PEA: 750,
    PlantType.CHOMPER: 750,
    PlantType.REPEATER: 750,
    PlantType.PUFFSHROOM: 750,
    PlantType.SUNSHROOM: 750,
    PlantType.FUMESHROOM: 750,
    PlantType.GRAVEBUSTER: 750,
    PlantType.HYPNOSHROOM: 3000,
    PlantType.SCAREDYSHROOM: 750,
    PlantType.ICESHROOM: 5000,
    PlantType.DOOMSHROOM: 5000,
    PlantType.LILYPAD: 750,
    PlantType.SQUASH: 3000,
    PlantType.THREEPEATER: 750,
    PlantType.TANGLEKELP: 3000,
    PlantType.JALAPENO: 5000,
    PlantType.SPIKEWEED: 750,
    PlantType.TORCHWOOD: 750,
    PlantType.TALLNUT: 3000,
    PlantType.SEASHROOM: 3000,
    PlantType.PLANTERN: 3000,
    PlantType.CACTUS: 750,
    PlantType.BLOVER: 750,
    PlantType.SPLITPEA: 750,
    PlantType.STARFRUIT: 750,
    PlantType.PUMPKIN: 3000,
    PlantType.MAGNETSHROOM: 750,
    PlantType.CABBAGEPULT: 750,
    PlantType.FLOWERPOT: 750,
    PlantType.KERNELPULT: 750,
    PlantType.COFFEEBEAN: 750,
    PlantType.GARLIC: 750,
    PlantType.UMBRELLALEAF: 750,
    PlantType.MARIGOLD: 750,
    PlantType.MELONPULT: 750,
    PlantType.GATLINGPEA: 5000,
    PlantType.TWINSUNFLOWER: 5000,
    PlantType.GLOOMSHROOM: 5000,
    PlantType.CATTAIL: 5000,
    PlantType.WINTERMELON: 5000,
    PlantType.GOLDMAGNET: 5000,
    PlantType.SPIKEROCK: 5000,
    PlantType.COBCANNON: 5000,
}

# ============================================================================
# Plant Collision Boxes (from judge.h)
# HIT_DEFENSE_RANGE: Range where zombies can hit the plant
# EXPLODE_DEFENSE_RANGE: Range where explosions can hit the plant
# ============================================================================

@dataclass
class CollisionBox:
    """Plant collision box relative to plant x coordinate"""
    left: int
    right: int


# Hit defense range (zombies can bite/hit)
# Format: (left_offset, right_offset) from plant x
HIT_DEFENSE_RANGE = {
    'DEFAULT': CollisionBox(30, 50),
    PlantType.TALLNUT: CollisionBox(30, 60),
    PlantType.PUMPKIN: CollisionBox(20, 80),
    PlantType.COBCANNON: CollisionBox(20, 120),
}

# Explode defense range (explosions affect plant)
# Format: (left_offset, right_offset) from plant x
EXPLODE_DEFENSE_RANGE = {
    'DEFAULT': CollisionBox(-50, 10),
    PlantType.TALLNUT: CollisionBox(-50, 30),
    PlantType.PUMPKIN: CollisionBox(-60, 40),
    PlantType.COBCANNON: CollisionBox(-60, 80),
}


def get_hit_defense_range(plant_type: PlantType) -> CollisionBox:
    """Get the hit defense range for a plant type"""
    return HIT_DEFENSE_RANGE.get(plant_type, HIT_DEFENSE_RANGE['DEFAULT'])


def get_explode_defense_range(plant_type: PlantType) -> CollisionBox:
    """Get the explode defense range for a plant type"""
    return EXPLODE_DEFENSE_RANGE.get(plant_type, EXPLODE_DEFENSE_RANGE['DEFAULT'])


# ============================================================================
# Plant Attack Data
# ============================================================================

# Plants that can attack
ATTACKING_PLANTS = {
    PlantType.PEASHOOTER,
    PlantType.SNOW_PEA,
    PlantType.REPEATER,
    PlantType.THREEPEATER,
    PlantType.SPLITPEA,
    PlantType.GATLINGPEA,
    PlantType.PUFFSHROOM,
    PlantType.SCAREDYSHROOM,
    PlantType.FUMESHROOM,
    PlantType.SEASHROOM,
    PlantType.CACTUS,
    PlantType.STARFRUIT,
    PlantType.CABBAGEPULT,
    PlantType.KERNELPULT,
    PlantType.MELONPULT,
    PlantType.WINTERMELON,
    PlantType.GLOOMSHROOM,
    PlantType.CATTAIL,
}

# Instant kill plants
INSTANT_KILL_PLANTS = {
    PlantType.CHERRY_BOMB,
    PlantType.JALAPENO,
    PlantType.DOOMSHROOM,
    PlantType.SQUASH,
    PlantType.POTATO_MINE,
    PlantType.CHOMPER,
    PlantType.TANGLEKELP,
    PlantType.HYPNOSHROOM,
}

# Mushroom plants (need coffee bean in day)
MUSHROOM_PLANTS = {
    PlantType.PUFFSHROOM,
    PlantType.SUNSHROOM,
    PlantType.FUMESHROOM,
    PlantType.HYPNOSHROOM,
    PlantType.SCAREDYSHROOM,
    PlantType.ICESHROOM,
    PlantType.DOOMSHROOM,
    PlantType.SEASHROOM,
    PlantType.MAGNETSHROOM,
    PlantType.GLOOMSHROOM,
}

# Aquatic plants
AQUATIC_PLANTS = {
    PlantType.LILYPAD,
    PlantType.TANGLEKELP,
    PlantType.SEASHROOM,
    PlantType.CATTAIL,
}

# Sun producing plants
SUN_PRODUCING_PLANTS = {
    PlantType.SUNFLOWER,
    PlantType.SUNSHROOM,
    PlantType.TWINSUNFLOWER,
}

# Defensive plants
DEFENSIVE_PLANTS = {
    PlantType.WALLNUT,
    PlantType.TALLNUT,
    PlantType.PUMPKIN,
    PlantType.GARLIC,
}

# Upgrade plants (require another plant to place on)
UPGRADE_PLANTS = {
    PlantType.GATLINGPEA: PlantType.REPEATER,
    PlantType.TWINSUNFLOWER: PlantType.SUNFLOWER,
    PlantType.GLOOMSHROOM: PlantType.FUMESHROOM,
    PlantType.CATTAIL: PlantType.LILYPAD,
    PlantType.WINTERMELON: PlantType.MELONPULT,
    PlantType.GOLDMAGNET: PlantType.MAGNETSHROOM,
    PlantType.SPIKEROCK: PlantType.SPIKEWEED,
    PlantType.COBCANNON: PlantType.KERNELPULT,  # Requires two kernel-pults
}
