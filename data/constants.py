"""
Game Constants from AsmVsZombies
Time constants, game mechanics values
All time values are in centiseconds (cs) = 1/100 second
"""

# ============================================================================
# Cob Cannon (玉米加农炮) Constants
# ============================================================================

COB_FLY_TIME = 373  # 玉米加农炮飞行时间 (cs)
COB_RECOVER_TIME = 3475  # 炮冷却时间 (cs)

# 屋顶炮飞行时间 (根据落点列数不同)
# 索引 0-6 对应 1-7 列
ROOF_COB_FLY_TIME = [359, 362, 364, 367, 369, 372, 373]

# 炮弹爆炸半径 (像素)
COB_EXPLODE_RADIUS = 115

# ============================================================================
# Instant Kill Plants (灰烬植物) Delay
# ============================================================================

CHERRY_DELAY = 100  # 樱桃爆炸延迟 (cs)
JALAPENO_DELAY = 100  # 火爆辣椒延迟 (cs)
DOOM_DELAY = 100  # 毁灭菇爆炸延迟 (cs)
SQUASH_DELAY = 100  # 窝瓜延迟 (cs)

POTATO_MINE_ARM_TIME = 1500  # 土豆雷武装时间 (cs)

# 樱桃爆炸范围 (以列为单位)
CHERRY_EXPLODE_RADIUS = 90  # 像素

# ============================================================================
# Ice Related (冰冻相关)
# ============================================================================

ICE_EFFECT_TIME = 298  # 冰菇生效时间 (cs)
ICE_DURATION = 400  # 冰冻持续时间 (cs)
SLOW_DURATION = 1000  # 减速持续时间 (cs)

# ============================================================================
# Gargantuar (巨人僵尸) Constants
# ============================================================================

GIGA_THROW_IMP_TIME = [105, 210]  # 红眼扔小鬼的时间点 (cs)
HAMMER_CIRCULATION_RATE = 0.644  # 锤击循环概率

# ============================================================================
# Speed Constants (速度常量)
# ============================================================================

# 僵尸平均速度 (像素/cs)
GIGA_AVG_SPEED = 484 / 3158 * 1.25  # ≈ 0.192 px/cs

# 曾菇每 cs 伤害
GLOOM_DAMAGE_PER_CS = 80 / 200  # = 0.4 hp/cs

# ============================================================================
# Grid Constants (场地常量)
# ============================================================================

GRID_WIDTH = 80  # 每格宽度 (像素)
GRID_HEIGHT = 85  # 每格高度 (像素) - 非屋顶场景
GRID_HEIGHT_ROOF = 85  # 屋顶场景基础高度 (same as non-roof, but roof has slope)

GRID_COLS = 9  # 列数
GRID_ROWS = 6  # 最大行数 (泳池有6行，草地有5行)

# 草地左边界 x 坐标
LAWN_LEFT_X = 40
LAWN_RIGHT_X = LAWN_LEFT_X + GRID_WIDTH * GRID_COLS

# 植物种植的 x 坐标计算: x = LAWN_LEFT_X + col * GRID_WIDTH
# 植物种植的 y 坐标计算: y = 80 + row * GRID_HEIGHT

# ============================================================================
# Scene Types (场景类型)
# ============================================================================

SCENE_DAY = 0  # 白天
SCENE_NIGHT = 1  # 夜晚
SCENE_POOL = 2  # 泳池
SCENE_FOG = 3  # 迷雾
SCENE_ROOF = 4  # 屋顶白天
SCENE_ROOF_NIGHT = 5  # 屋顶夜晚

# ============================================================================
# Game UI States (游戏界面状态)
# ============================================================================

UI_MAIN_MENU = 1
UI_ALMANAC = 2
UI_IN_GAME = 3
UI_PAUSE = 4

# ============================================================================
# Attack Constants (攻击常量)
# ============================================================================

# 豌豆射手攻击间隔 (cs)
PEASHOOTER_ATTACK_INTERVAL = 141

# 各植物伤害值
PEA_DAMAGE = 20
SNOW_PEA_DAMAGE = 20
FIRE_PEA_DAMAGE = 40  # 经过火炬的豌豆
MELON_DAMAGE = 80  # 西瓜投手
WINTER_MELON_DAMAGE = 80  # 冰西瓜

# 范围伤害
CHERRY_DAMAGE = 1800
JALAPENO_DAMAGE = 1800
DOOM_DAMAGE = 1800  # 对普通僵尸
DOOM_DAMAGE_GARG = 900  # 对巨人减半

# ============================================================================
# Zombie States (僵尸状态)
# ============================================================================

Z_STATE_WALKING = 1
Z_STATE_DYING = 2
Z_STATE_DYING_FROM_INSTANT = 3
Z_STATE_DYING_FROM_LAWNMOWER = 4
Z_STATE_BUNGEE_TARGET = 5
Z_STATE_BUNGEE_LANDING = 6
Z_STATE_BUNGEE_RISING = 7
Z_STATE_EATING = 8
Z_STATE_FALLING = 9  # 从蹦极掉下
Z_STATE_POLE_VAULTING = 10
Z_STATE_DANCING = 11
Z_STATE_SNORKEL = 12
Z_STATE_RISING_FROM_GRAVE = 13
Z_STATE_DIGGER_TUNNELING = 14
Z_STATE_DIGGER_RISING = 15
Z_STATE_DIGGER_WALKING = 16
Z_STATE_DOLPHIN_DIVING = 17
Z_STATE_DOLPHIN_JUMPING = 18
Z_STATE_POGO_JUMPING = 19
Z_STATE_LADDER_PLACING = 20
Z_STATE_LADDER_CLIMBING = 21
Z_STATE_YETI_ESCAPING = 22
Z_STATE_BOBSLED_SLIDING = 23
Z_STATE_GARG_THROWING = 24
Z_STATE_BALLOON_FLYING = 25
Z_STATE_DOLPHIN_RIDING = 26
Z_STATE_IMP_LANDING = 27
Z_STATE_ZOMBOSS = 28
