"""
Memory Offsets from AsmVsZombies (avz_pvz_struct.h)
All memory addresses and structure offsets for PVZ memory reading/writing
"""


class Offset:
    """Memory offsets for PVZ game structures"""
    
    # ========================================================================
    # Base Addresses
    # ========================================================================
    
    BASE = 0x6A9EC0  # PvzBase pointer
    
    # PvzBase offsets
    MAIN_OBJECT = 0x768  # Board/MainObject pointer
    GAME_UI = 0x7FC  # Current UI state (3 = in game)
    
    # ========================================================================
    # MainObject (Board) Offsets
    # ========================================================================
    
    # Zombie array
    ZOMBIE_ARRAY = 0x90
    ZOMBIE_COUNT_MAX = 0x94
    ZOMBIE_COUNT = 0xA0
    
    # Plant array
    PLANT_ARRAY = 0xAC
    PLANT_COUNT_MAX = 0xB0
    PLANT_COUNT = 0xBC
    
    # Seed/Card array
    SEED_ARRAY = 0x144
    
    # Projectile array
    PROJECTILE_ARRAY = 0xC8
    PROJECTILE_COUNT_MAX = 0xCC
    
    # Item (collectible/sun) array
    ITEM_ARRAY = 0xE4
    ITEM_COUNT_MAX = 0xE8
    
    # Lawnmower array
    LAWNMOWER_ARRAY = 0x100
    LAWNMOWER_COUNT_MAX = 0x104
    
    # Game state
    SUN = 0x5560
    GAME_CLOCK = 0x5568
    SCENE = 0x554C
    WAVE = 0x557C
    TOTAL_WAVE = 0x5564
    REFRESH_COUNTDOWN = 0x559C
    HUGE_WAVE_COUNTDOWN = 0x55A4
    
    # Additional game state
    COIN_COUNT = 0x5570
    PAUSED = 0x164
    
    # ========================================================================
    # Zombie Structure (size = 0x15C)
    # ========================================================================
    
    ZOMBIE_SIZE = 0x15C
    
    # Position and movement
    Z_ROW = 0x1C  # int, current row
    Z_X = 0x2C  # float, x position
    Z_Y = 0x30  # float, y position
    Z_SPEED = 0x34  # float, current speed
    Z_HEIGHT = 0x38  # float, height offset (for jumping/flying)
    
    # Type and state
    Z_TYPE = 0x24  # int, zombie type
    Z_STATE = 0x28  # int, current state (walking, eating, etc.)
    
    # Health
    Z_HP = 0xC8  # int, current body HP
    Z_HP_MAX = 0xCC  # int, max body HP
    Z_ACCESSORY_HP_1 = 0xD0  # int, first accessory HP (cone/bucket/etc.)
    Z_ACCESSORY_HP_2 = 0xDC  # int, second accessory HP (shield door)
    
    # Status effects
    Z_SLOW_COUNTDOWN = 0xAC  # int, slow effect remaining time
    Z_FREEZE_COUNTDOWN = 0xB4  # int, freeze effect remaining time
    Z_BUTTER_COUNTDOWN = 0xB0  # int, butter effect remaining time
    
    # Animation
    Z_ANIMATION = 0x118  # AnimationMain pointer
    Z_ANIMATION_PROGRESS = 0x58  # float, 0.0-1.0
    
    # Status flags
    Z_DEAD = 0xEC  # bool, is dead/removed
    Z_VISIBLE = 0x18  # bool, is visible
    Z_AT_WAVE = 0x6C  # int, which wave spawned this zombie
    
    # Attack
    Z_EATING_COUNTDOWN = 0x88  # int, time until next bite
    
    # Special zombie data
    Z_TARGET_ROW = 0x68  # int, for pole vaulter, digger, etc.
    Z_HAS_BALLOON = 0xB8  # bool, balloon zombie still has balloon
    Z_HAS_SHIELD = 0xC4  # bool, has screen door or ladder
    Z_LADDER_PLACED = 0xBC  # bool, ladder zombie placed ladder
    Z_HYPNOTIZED = 0xB9  # bool, hypno-shroom effect
    
    # Jack-in-box
    Z_BOX_EXPLODED = 0xBA  # bool, jack-in-box exploded
    
    # ========================================================================
    # Plant Structure (size = 0x14C)
    # ========================================================================
    
    PLANT_SIZE = 0x14C
    
    # Position
    P_ROW = 0x1C  # int, row
    P_COL = 0x28  # int, column
    P_X = 0x8  # int, x position (pixel)
    P_Y = 0xC  # int, y position (pixel)
    
    # Type and state
    P_TYPE = 0x24  # int, plant type
    P_STATE = 0x3C  # int, current state
    
    # Health
    P_HP = 0x40  # int, current HP
    P_HP_MAX = 0x44  # int, max HP
    
    # Attack
    P_SHOOT_COUNTDOWN = 0x90  # int, countdown to next shot
    P_EFFECTIVE = 0x48  # int, is awake/effective
    
    # Status
    P_DEAD = 0x141  # bool, is dead/removed
    P_SQUASHED = 0x142  # bool, is being squashed
    P_SLEEPING = 0x143  # bool, is sleeping (mushrooms in day)
    
    # Pumpkin
    P_PUMPKIN_HP = 0x4C  # int, pumpkin shield HP if present
    
    # Cob Cannon
    P_COB_COUNTDOWN = 0x54  # int, cob cannon reload time
    P_COB_READY = 0x58  # bool, cob cannon ready to fire
    
    # Animation
    P_ANIMATION = 0x94  # AnimationMain pointer
    
    # ========================================================================
    # Seed/Card Structure (size = 0x50)
    # ========================================================================
    
    SEED_SIZE = 0x50
    
    # Card info (offset from seed_array + index * SEED_SIZE + 0x28)
    S_RECHARGE_COUNTDOWN = 0x24  # int, current recharge remaining
    S_RECHARGE_TIME = 0x28  # int, total recharge time
    S_TYPE = 0x34  # int, plant type
    S_IMITATOR_TYPE = 0x38  # int, imitator plant type (-1 if not imitator)
    S_USABLE = 0x48  # bool, is card usable
    S_X = 0x0  # int, x position on screen
    S_Y = 0x4  # int, y position on screen
    S_VISIBLE = 0x18  # bool, is card visible
    
    # Legacy offsets (combined with 0x28 base)
    S_CD = 0x4C  # 0x24 + 0x28 - recharge countdown from base
    S_TYPE_LEGACY = 0x5C  # 0x34 + 0x28 - type from base
    S_USABLE_LEGACY = 0x70  # 0x48 + 0x28 - usable from base
    
    # ========================================================================
    # Item/Collectible Structure (size = 0xD8)
    # ========================================================================
    
    ITEM_SIZE = 0xD8
    
    # Position
    I_X = 0x24  # float, x position
    I_Y = 0x28  # float, y position
    
    # State
    I_TYPE = 0x58  # int, item type (1=silver, 2=gold, 3=diamond, 4=sun, etc.)
    I_DISAPPEARED = 0x38  # bool, has disappeared
    I_COLLECTED = 0x50  # bool, has been collected
    I_DEAD = 0x20  # bool, is dead/removed
    
    # Value
    I_VALUE = 0x50  # int, sun value
    
    # ========================================================================
    # Projectile Structure
    # ========================================================================
    
    PROJECTILE_SIZE = 0x94
    
    PR_X = 0x30  # float, x position
    PR_Y = 0x34  # float, y position
    PR_ROW = 0x1C  # int, row
    PR_TYPE = 0x5C  # int, projectile type
    PR_DEAD = 0x50  # bool, is dead
    
    # ========================================================================
    # Lawnmower Structure
    # ========================================================================
    
    LAWNMOWER_SIZE = 0x48
    
    LM_ROW = 0x14  # int, row
    LM_X = 0x30  # float, x position
    LM_DEAD = 0x48  # bool, is dead/used
    LM_STATE = 0x34  # int, state
    
    # ========================================================================
    # Function Addresses (for ASM injection)
    # ========================================================================
    
    FUNC_PLANT = 0x0040D120  # Plant function
    FUNC_REMOVE_PLANT = 0x004679B0  # Remove/shovel plant
    FUNC_REFRESH_SEEDS = 0x00489D50  # Refresh all seed cooldowns
    FUNC_CLICK_SEED = 0x00488E00  # Click on a seed card
    FUNC_SET_SUN = 0x00430A00  # Set sun amount
    FUNC_COB_FIRE = 0x00466D50  # Fire cob cannon
    
    # ========================================================================
    # Animation Structure
    # ========================================================================
    
    ANIM_CIRCULATION_RATE = 0x0  # float, animation circulation rate
    ANIM_PROGRESS = 0x8  # float, current progress (0-1)
    ANIM_FRAME = 0x24  # int, current frame


# Item types for collectibles
class ItemType:
    """Item/collectible types"""
    SILVER_COIN = 1
    GOLD_COIN = 2
    DIAMOND = 3
    SUN = 4  # Normal sun (25)
    SMALL_SUN = 5  # Small sun (15)
    BIG_SUN = 6  # Big sun (50)
    FINAL_SUN = 17  # End of level sun


# Scene/Level types
class SceneType:
    """Scene/level types"""
    DAY = 0
    NIGHT = 1
    POOL = 2
    FOG = 3
    ROOF = 4
    ROOF_NIGHT = 5
    
    @staticmethod
    def has_pool(scene: int) -> bool:
        """Check if scene has water/pool"""
        return scene in [SceneType.POOL, SceneType.FOG]
    
    @staticmethod
    def is_night(scene: int) -> bool:
        """Check if scene is night (mushrooms wake)"""
        return scene in [SceneType.NIGHT, SceneType.FOG, SceneType.ROOF_NIGHT]
    
    @staticmethod
    def is_roof(scene: int) -> bool:
        """Check if scene is roof (need flower pots)"""
        return scene in [SceneType.ROOF, SceneType.ROOF_NIGHT]
    
    @staticmethod
    def get_row_count(scene: int) -> int:
        """Get number of playable rows for scene"""
        if scene in [SceneType.POOL, SceneType.FOG]:
            return 6
        else:
            return 5
