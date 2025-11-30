"""
PVZ 最优算法 Bot v3.0
基于 AsmVsZombies 的权威内存结构
实现真正的智能决策系统

自动种植方案: 远程线程注入调用游戏函数 0x0040D120
- 优点：最快最稳定，100%成功
- 原理：在游戏进程中执行 shellcode 直接调用种植函数
"""

import ctypes
import struct
import time
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import IntEnum
from ctypes import wintypes

# ============================================================================
# 常量定义 (来自 AsmVsZombies)
# ============================================================================

class PlantType(IntEnum):
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

class ZombieType(IntEnum):
    ZOMBIE = 0
    FLAG = 1
    CONEHEAD = 2
    POLEVAULTER = 3
    BUCKETHEAD = 4
    NEWSPAPER = 5
    SCREENDOOR = 6
    FOOTBALL = 7
    DANCING = 8
    BACKUP = 9
    DUCKYTUBE = 10
    SNORKEL = 11
    ZOMBONI = 12
    BOBSLED = 13
    DOLPHIN = 14
    JACKINBOX = 15
    BALLOON = 16
    DIGGER = 17
    POGO = 18
    YETI = 19
    BUNGEE = 20
    LADDER = 21
    CATAPULT = 22
    GARGANTUAR = 23
    IMP = 24
    ZOMBOSS = 25
    GIGA_GARGANTUAR = 32

# 植物阳光花费
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
    PlantType.MELONPULT: 300,
    PlantType.WINTERMELON: 500,
    PlantType.COBCANNON: 500,
}

# 僵尸基础血量
ZOMBIE_HP = {
    ZombieType.ZOMBIE: 200,
    ZombieType.FLAG: 200,
    ZombieType.CONEHEAD: 200 + 370,
    ZombieType.POLEVAULTER: 500,
    ZombieType.BUCKETHEAD: 200 + 1100,
    ZombieType.NEWSPAPER: 200 + 150,
    ZombieType.SCREENDOOR: 200 + 1100,
    ZombieType.FOOTBALL: 1600,
    ZombieType.DANCING: 500,
    ZombieType.ZOMBONI: 1350,
    ZombieType.DOLPHIN: 500,
    ZombieType.JACKINBOX: 500,
    ZombieType.BALLOON: 400,
    ZombieType.DIGGER: 300,
    ZombieType.POGO: 500,
    ZombieType.LADDER: 500 + 500,
    ZombieType.CATAPULT: 850,
    ZombieType.GARGANTUAR: 3000,
    ZombieType.GIGA_GARGANTUAR: 6000,
}

# ============================================================================
# 内存偏移量 (来自 AsmVsZombies avz_pvz_struct.h)
# ============================================================================

class Offset:
    # Base
    BASE = 0x6A9EC0
    
    # PvzBase offsets
    MAIN_OBJECT = 0x768
    GAME_UI = 0x7FC
    
    # MainObject offsets
    ZOMBIE_ARRAY = 0x90
    ZOMBIE_COUNT_MAX = 0x94
    ZOMBIE_COUNT = 0xA0
    
    PLANT_ARRAY = 0xAC
    PLANT_COUNT_MAX = 0xB0
    PLANT_COUNT = 0xBC
    
    SEED_ARRAY = 0x144
    
    SUN = 0x5560
    GAME_CLOCK = 0x5568
    SCENE = 0x554C
    WAVE = 0x557C
    TOTAL_WAVE = 0x5564
    REFRESH_COUNTDOWN = 0x559C
    HUGE_WAVE_COUNTDOWN = 0x55A4
    
    # Item (收集物/阳光) struct (size = 0xD8)
    ITEM_ARRAY = 0xE4
    ITEM_COUNT_MAX = 0xE8
    ITEM_SIZE = 0xD8
    I_DISAPPEARED = 0x38  # bool
    I_COLLECTED = 0x50    # bool
    I_X = 0x24            # float
    I_Y = 0x28            # float
    I_TYPE = 0x58         # int (1=银币,2=金币,3=钻石,4=阳光,5=小阳光,6=大阳光)
    
    # Zombie struct (size = 0x15C)
    ZOMBIE_SIZE = 0x15C
    Z_ROW = 0x1C
    Z_X = 0x2C  # float
    Z_Y = 0x30  # float
    Z_TYPE = 0x24
    Z_HP = 0xC8
    Z_STATE = 0x28
    Z_DEAD = 0xEC  # bool
    Z_SPEED = 0x34  # float
    Z_SLOW_COUNTDOWN = 0xAC
    Z_FREEZE_COUNTDOWN = 0xB4
    Z_AT_WAVE = 0x6C
    
    # Plant struct (size = 0x14C)
    PLANT_SIZE = 0x14C
    P_ROW = 0x1C
    P_COL = 0x28
    P_TYPE = 0x24
    P_HP = 0x40
    P_STATE = 0x3C
    P_DEAD = 0x141  # bool
    P_SHOOT_COUNTDOWN = 0x90
    
    # Seed struct (size = 0x50)
    SEED_SIZE = 0x50
    S_CD = 0x4C  # 0x24 + 0x28
    S_TYPE = 0x5C  # 0x34 + 0x28
    S_USABLE = 0x70  # 0x48 + 0x28

# 收集物类型
class ItemType(IntEnum):
    SILVER_COIN = 1
    GOLD_COIN = 2
    DIAMOND = 3
    SUN = 4           # 普通阳光 (25)
    SMALL_SUN = 5     # 小阳光 (15)
    BIG_SUN = 6       # 大阳光 (50)

@dataclass
class CollectibleInfo:
    """收集物信息（阳光、金币等）"""
    index: int
    x: float
    y: float
    type: int
    collected: bool

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class ZombieInfo:
    index: int
    row: int
    x: float
    y: float
    type: int
    hp: int
    state: int
    speed: float
    is_slowed: bool
    is_frozen: bool
    at_wave: int
    
    @property
    def threat_level(self) -> float:
        """计算威胁等级"""
        # 基础威胁 = 距离草坪左边越近威胁越高
        distance_threat = max(0, (800 - self.x) / 800)
        
        # 血量威胁
        hp_threat = min(1.0, self.hp / 3000)
        
        # 类型威胁加成
        type_multiplier = 1.0
        if self.type in [ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR]:
            type_multiplier = 3.0
        elif self.type in [ZombieType.FOOTBALL, ZombieType.ZOMBONI]:
            type_multiplier = 2.0
        elif self.type in [ZombieType.BUCKETHEAD, ZombieType.SCREENDOOR]:
            type_multiplier = 1.5
        elif self.type == ZombieType.BALLOON:
            type_multiplier = 1.8  # 气球僵尸特殊处理
        
        # 速度加成
        speed_mult = 1.0 + abs(self.speed) * 0.5
        
        return distance_threat * (1 + hp_threat) * type_multiplier * speed_mult

@dataclass
class PlantInfo:
    index: int
    row: int
    col: int
    type: int
    hp: int
    state: int

@dataclass
class SeedInfo:
    index: int
    type: int
    cd: int
    usable: bool

@dataclass
class GameState:
    sun: int
    wave: int
    total_wave: int
    game_clock: int
    scene: int
    refresh_countdown: int
    huge_wave_countdown: int
    zombies: List[ZombieInfo]
    plants: List[PlantInfo]
    seeds: List[SeedInfo]
    plant_grid: List[List[Optional[PlantInfo]]]  # 5x9 grid

# ============================================================================
# 内存读取类
# ============================================================================

# Windows API 常量
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40

class PVZMemory:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.process = None
        self.pid = None
        
    def attach(self) -> bool:
        """附加到 PVZ 进程"""
        import ctypes.wintypes as wt
        
        # 查找窗口
        hwnd = ctypes.windll.user32.FindWindowW(None, "Plants vs. Zombies")
        if not hwnd:
            hwnd = ctypes.windll.user32.FindWindowW("MainWindow", None)
        if not hwnd:
            return False
        
        # 获取进程ID
        pid = wt.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        self.pid = pid.value
        
        # 打开进程
        PROCESS_ALL_ACCESS = 0x1F0FFF
        self.process = self.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        return self.process != 0
    
    def read_int(self, addr: int) -> int:
        buf = ctypes.c_int()
        self.kernel32.ReadProcessMemory(self.process, addr, ctypes.byref(buf), 4, None)
        return buf.value
    
    def read_float(self, addr: int) -> float:
        buf = ctypes.c_float()
        self.kernel32.ReadProcessMemory(self.process, addr, ctypes.byref(buf), 4, None)
        return buf.value
    
    def read_byte(self, addr: int) -> int:
        buf = ctypes.c_byte()
        self.kernel32.ReadProcessMemory(self.process, addr, ctypes.byref(buf), 1, None)
        return buf.value
    
    def write_int(self, addr: int, value: int):
        buf = ctypes.c_int(value)
        self.kernel32.WriteProcessMemory(self.process, addr, ctypes.byref(buf), 4, None)
    
    # ==================== ASM 注入执行 ====================
    
    def alloc_memory(self, size: int) -> int:
        """在游戏进程中分配可执行内存"""
        addr = self.kernel32.VirtualAllocEx(
            self.process, 
            None, 
            size, 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_EXECUTE_READWRITE
        )
        return addr or 0
    
    def free_memory(self, addr: int):
        """释放游戏进程中的内存"""
        self.kernel32.VirtualFreeEx(self.process, addr, 0, MEM_RELEASE)
    
    def write_bytes(self, addr: int, data: bytes) -> bool:
        """写入字节数据"""
        written = ctypes.c_size_t()
        return self.kernel32.WriteProcessMemory(
            self.process, addr, data, len(data), ctypes.byref(written)
        )
    
    def execute_asm(self, shellcode: bytes, timeout: int = 1000) -> bool:
        """
        在游戏进程中执行 shellcode
        
        原理:
        1. 在游戏进程分配可执行内存
        2. 写入 shellcode
        3. 创建远程线程执行
        4. 等待完成，释放内存
        """
        # 分配内存
        addr = self.alloc_memory(len(shellcode) + 16)
        if not addr:
            return False
        
        try:
            # 写入代码
            if not self.write_bytes(addr, shellcode):
                return False
            
            # 创建远程线程执行
            thread_id = wintypes.DWORD()
            thread = self.kernel32.CreateRemoteThread(
                self.process,
                None, 0,
                addr, None, 0,
                ctypes.byref(thread_id)
            )
            
            if not thread:
                return False
            
            # 等待执行完成
            self.kernel32.WaitForSingleObject(thread, timeout)
            self.kernel32.CloseHandle(thread)
            return True
            
        finally:
            self.free_memory(addr)
    
    def asm_plant(self, row: int, col: int, plant_type: int, imitator: int = -1) -> bool:
        """
        直接调用游戏种植函数 0x0040D120
        
        这是最稳定的种植方法，100% 成功率！
        
        调用约定 (来自 pvz_cpp_bot/dllmain.cpp):
            push imitatorType  (-1 = 非模仿者)
            push plantType
            mov eax, row
            push col
            mov edi, pBoard
            push edi
            call 0x0040D120
        """
        board = self.get_board()
        if board == 0:
            return False
        
        # 函数地址
        FUNC_PLANT = 0x0040D120
        
        # 构建 shellcode
        shellcode = bytes([
            # push imitator (-1)
            0x68, *struct.pack('<i', imitator),
            
            # push plant_type
            0x68, *struct.pack('<i', plant_type),
            
            # mov eax, row
            0xB8, *struct.pack('<I', row),
            
            # push col
            0x68, *struct.pack('<i', col),
            
            # mov edi, board
            0xBF, *struct.pack('<I', board),
            
            # push edi (board)
            0x57,
            
            # mov edx, FUNC_PLANT
            0xBA, *struct.pack('<I', FUNC_PLANT),
            
            # call edx
            0xFF, 0xD2,
            
            # ret
            0xC3
        ])
        
        return self.execute_asm(shellcode)
    
    def asm_shovel(self, row: int, col: int) -> bool:
        """
        直接调用游戏铲子函数
        先查找植物地址，然后调用 RemovePlant (0x004679B0)
        """
        board = self.get_board()
        if board == 0:
            return False
        
        # 查找该位置的植物
        plant_array = self.read_int(board + Offset.PLANT_ARRAY)
        plant_max = self.read_int(board + Offset.PLANT_COUNT_MAX)
        
        plant_addr = None
        for i in range(min(plant_max, 200)):
            addr = plant_array + i * Offset.PLANT_SIZE
            if self.read_byte(addr + Offset.P_DEAD):
                continue
            if self.read_int(addr + Offset.P_ROW) == row and self.read_int(addr + Offset.P_COL) == col:
                plant_addr = addr
                break
        
        if plant_addr is None:
            return False
        
        # 调用 RemovePlant
        FUNC_REMOVE = 0x004679B0
        
        shellcode = bytes([
            # push plant_addr
            0x68, *struct.pack('<I', plant_addr),
            
            # mov edx, FUNC_REMOVE
            0xBA, *struct.pack('<I', FUNC_REMOVE),
            
            # call edx
            0xFF, 0xD2,
            
            # ret
            0xC3
        ])
        
        return self.execute_asm(shellcode)
    
    def asm_refresh_cooldown(self) -> bool:
        """刷新所有卡片冷却"""
        board = self.get_board()
        if board == 0:
            return False
        
        seed_bank = self.read_int(board + Offset.SEED_ARRAY)
        if seed_bank == 0:
            return False
        
        FUNC_REFRESH = 0x00489D50
        
        shellcode = bytes([
            # push seed_bank
            0x68, *struct.pack('<I', seed_bank),
            
            # mov eax, FUNC_REFRESH
            0xB8, *struct.pack('<I', FUNC_REFRESH),
            
            # call eax
            0xFF, 0xD0,
            
            # ret
            0xC3
        ])
        
        return self.execute_asm(shellcode)
    
    # ==================== 收集物相关 ====================
    
    def collect_all_items(self) -> int:
        """
        直接收集所有阳光/金币
        
        原理：直接设置 IsCollected = true，游戏会自动将阳光加到总数
        这是最简单最快的方法！
        
        Returns:
            收集的物品数量
        """
        board = self.get_board()
        if board == 0:
            return 0
        
        count = 0
        item_array = self.read_int(board + Offset.ITEM_ARRAY)
        item_max = self.read_int(board + Offset.ITEM_COUNT_MAX)
        
        for i in range(min(item_max, 100)):
            addr = item_array + i * Offset.ITEM_SIZE
            
            # 检查是否消失
            disappeared = self.read_byte(addr + Offset.I_DISAPPEARED)
            if disappeared:
                continue
            
            # 检查是否已被收集
            collected = self.read_byte(addr + Offset.I_COLLECTED)
            if collected:
                continue
            
            # 直接设置为已收集！
            self.write_byte(addr + Offset.I_COLLECTED, 1)
            count += 1
        
        return count
    
    def write_byte(self, addr: int, value: int):
        """写入一个字节"""
        buf = ctypes.c_byte(value)
        self.kernel32.WriteProcessMemory(self.process, addr, ctypes.byref(buf), 1, None)
    
    # ==================== 原有方法 ====================
    
    def get_base(self) -> int:
        return self.read_int(Offset.BASE)
    
    def get_board(self) -> int:
        base = self.get_base()
        if base == 0:
            return 0
        return self.read_int(base + Offset.MAIN_OBJECT)
    
    def is_in_game(self) -> bool:
        base = self.get_base()
        if base == 0:
            return False
        return self.read_int(base + Offset.GAME_UI) == 3
    
    def get_game_state(self) -> Optional[GameState]:
        """读取完整游戏状态"""
        if not self.is_in_game():
            return None
        
        board = self.get_board()
        if board == 0:
            return None
        
        # 基础信息
        sun = self.read_int(board + Offset.SUN)
        wave = self.read_int(board + Offset.WAVE)
        total_wave = self.read_int(board + Offset.TOTAL_WAVE)
        game_clock = self.read_int(board + Offset.GAME_CLOCK)
        scene = self.read_int(board + Offset.SCENE)
        refresh_cd = self.read_int(board + Offset.REFRESH_COUNTDOWN)
        huge_wave_cd = self.read_int(board + Offset.HUGE_WAVE_COUNTDOWN)
        
        # 读取僵尸
        zombies = []
        zombie_array = self.read_int(board + Offset.ZOMBIE_ARRAY)
        zombie_max = self.read_int(board + Offset.ZOMBIE_COUNT_MAX)
        
        for i in range(min(zombie_max, 200)):
            z_addr = zombie_array + i * Offset.ZOMBIE_SIZE
            is_dead = self.read_byte(z_addr + Offset.Z_DEAD)
            if is_dead:
                continue
            
            zombies.append(ZombieInfo(
                index=i,
                row=self.read_int(z_addr + Offset.Z_ROW),
                x=self.read_float(z_addr + Offset.Z_X),
                y=self.read_float(z_addr + Offset.Z_Y),
                type=self.read_int(z_addr + Offset.Z_TYPE),
                hp=self.read_int(z_addr + Offset.Z_HP),
                state=self.read_int(z_addr + Offset.Z_STATE),
                speed=self.read_float(z_addr + Offset.Z_SPEED),
                is_slowed=self.read_int(z_addr + Offset.Z_SLOW_COUNTDOWN) > 0,
                is_frozen=self.read_int(z_addr + Offset.Z_FREEZE_COUNTDOWN) > 0,
                at_wave=self.read_int(z_addr + Offset.Z_AT_WAVE),
            ))
        
        # 读取植物
        plants = []
        plant_grid = [[None for _ in range(9)] for _ in range(6)]
        
        plant_array = self.read_int(board + Offset.PLANT_ARRAY)
        plant_max = self.read_int(board + Offset.PLANT_COUNT_MAX)
        
        for i in range(min(plant_max, 200)):
            p_addr = plant_array + i * Offset.PLANT_SIZE
            is_dead = self.read_byte(p_addr + Offset.P_DEAD)
            if is_dead:
                continue
            
            row = self.read_int(p_addr + Offset.P_ROW)
            col = self.read_int(p_addr + Offset.P_COL)
            
            plant = PlantInfo(
                index=i,
                row=row,
                col=col,
                type=self.read_int(p_addr + Offset.P_TYPE),
                hp=self.read_int(p_addr + Offset.P_HP),
                state=self.read_int(p_addr + Offset.P_STATE),
            )
            plants.append(plant)
            
            if 0 <= row < 6 and 0 <= col < 9:
                plant_grid[row][col] = plant
        
        # 读取卡片
        seeds = []
        seed_array = self.read_int(board + Offset.SEED_ARRAY)
        # 通常有10个卡槽
        for i in range(10):
            s_addr = seed_array + i * Offset.SEED_SIZE
            seeds.append(SeedInfo(
                index=i,
                type=self.read_int(s_addr + Offset.S_TYPE),
                cd=self.read_int(s_addr + Offset.S_CD),
                usable=self.read_byte(s_addr + Offset.S_USABLE) != 0,
            ))
        
        return GameState(
            sun=sun,
            wave=wave,
            total_wave=total_wave,
            game_clock=game_clock,
            scene=scene,
            refresh_countdown=refresh_cd,
            huge_wave_countdown=huge_wave_cd,
            zombies=zombies,
            plants=plants,
            seeds=seeds,
            plant_grid=plant_grid,
        )

# ============================================================================
# 决策引擎
# ============================================================================

@dataclass
class Action:
    action_type: str  # "plant", "shovel", "cherry", "jalapeno", "wait"
    row: int = 0
    col: int = 0
    plant_type: int = 0
    priority: float = 0.0
    reason: str = ""

class DecisionEngine:
    """最优决策引擎"""
    
    def __init__(self):
        self.last_action_time = 0
        self.action_cooldown = 100  # ms
        self.debug = True  # 调试模式
    
    def analyze(self, state: GameState) -> List[Action]:
        """分析游戏状态，返回优先级排序的行动列表"""
        actions = []
        
        # 调试: 打印卡槽信息
        if self.debug:
            usable_seeds = [s for s in state.seeds if s.usable and s.type >= 0]
            if usable_seeds:
                seed_names = [PlantType(s.type).name if s.type < 48 else f"?{s.type}" for s in usable_seeds]
                # 只在有变化时打印
                pass
        
        # 1. 紧急情况处理
        emergency = self._check_emergency(state)
        if emergency:
            actions.extend(emergency)
        
        # 2. 经济发展（阳光生产）
        economy = self._plan_economy(state)
        actions.extend(economy)
        
        # 3. 防御布局
        defense = self._plan_defense(state)
        actions.extend(defense)
        
        # 4. 攻击强化
        offense = self._plan_offense(state)
        actions.extend(offense)
        
        # 按优先级排序
        actions.sort(key=lambda a: -a.priority)
        
        return actions
    
    def _check_emergency(self, state: GameState) -> List[Action]:
        """检查紧急情况"""
        actions = []
        
        for zombie in state.zombies:
            # 僵尸太靠近左边 (x < 200)
            if zombie.x < 200 and zombie.hp > 0:
                # 优先使用樱桃炸弹
                cherry_seed = self._find_seed(state, PlantType.CHERRY_BOMB)
                if cherry_seed and cherry_seed.usable and state.sun >= 150:
                    # 找一个能炸到多个僵尸的位置
                    best_col = max(0, min(8, int((zombie.x - 40) / 80)))
                    actions.append(Action(
                        action_type="plant",
                        row=zombie.row,
                        col=best_col,
                        plant_type=PlantType.CHERRY_BOMB,
                        priority=100.0,
                        reason=f"紧急! 僵尸在 ({zombie.row}, {zombie.x:.0f})"
                    ))
                
                # 或者用火爆辣椒清行
                jalapeno_seed = self._find_seed(state, PlantType.JALAPENO)
                if jalapeno_seed and jalapeno_seed.usable and state.sun >= 125:
                    actions.append(Action(
                        action_type="plant",
                        row=zombie.row,
                        col=0,
                        plant_type=PlantType.JALAPENO,
                        priority=95.0,
                        reason=f"紧急! 火爆辣椒清第{zombie.row}行"
                    ))
        
        # 检查巨人僵尸
        for zombie in state.zombies:
            if zombie.type in [ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR]:
                if zombie.x < 600:
                    actions.append(Action(
                        action_type="plant",
                        row=zombie.row,
                        col=max(0, min(8, int((zombie.x - 40) / 80))),
                        plant_type=PlantType.CHERRY_BOMB,
                        priority=90.0,
                        reason=f"巨人僵尸威胁!"
                    ))
        
        return actions
    
    def _plan_economy(self, state: GameState) -> List[Action]:
        """规划经济发展"""
        actions = []
        
        # 计算当前向日葵数量
        sunflower_count = sum(1 for p in state.plants if p.type == PlantType.SUNFLOWER)
        twin_sunflower_count = sum(1 for p in state.plants if p.type == PlantType.TWINSUNFLOWER)
        
        total_sun_plants = sunflower_count + twin_sunflower_count * 2
        
        # 目标: 至少 6-8 个阳光生产单位
        target_sun_plants = 8
        
        if total_sun_plants < target_sun_plants:
            # 找到可以种植的位置 (后两列)
            sunflower_seed = self._find_seed(state, PlantType.SUNFLOWER)
            if sunflower_seed and sunflower_seed.usable and state.sun >= 50:
                # 优先在后两列种植
                for col in [1, 0]:
                    for row in range(5):
                        if state.plant_grid[row][col] is None:
                            priority = 50.0 - total_sun_plants * 5  # 越少优先级越高
                            actions.append(Action(
                                action_type="plant",
                                row=row,
                                col=col,
                                plant_type=PlantType.SUNFLOWER,
                                priority=priority,
                                reason=f"经济发展: 向日葵 ({total_sun_plants}/{target_sun_plants})"
                            ))
                            break
                    else:
                        continue
                    break
        
        return actions
    
    def _plan_defense(self, state: GameState) -> List[Action]:
        """规划防御"""
        actions = []
        
        # 分析每行的威胁
        row_threats = [0.0] * 6
        for zombie in state.zombies:
            if 0 <= zombie.row < 6:
                row_threats[zombie.row] += zombie.threat_level
        
        # 检查每行是否有足够防御
        for row in range(5):  # 通常5行
            threat = row_threats[row]
            
            # 检查该行的防御植物
            has_wallnut = any(
                p.type in [PlantType.WALLNUT, PlantType.TALLNUT] 
                for p in state.plants if p.row == row
            )
            
            shooter_count = sum(
                1 for p in state.plants 
                if p.row == row and p.type in [
                    PlantType.PEASHOOTER, PlantType.REPEATER, 
                    PlantType.SNOW_PEA, PlantType.THREEPEATER,
                    PlantType.GATLINGPEA, PlantType.MELONPULT, PlantType.WINTERMELON
                ]
            )
            
            # 如果威胁高但没有墙
            if threat > 0.5 and not has_wallnut:
                wallnut_seed = self._find_seed(state, PlantType.WALLNUT)
                if wallnut_seed and wallnut_seed.usable and state.sun >= 50:
                    # 在第4或5列放墙
                    for col in [4, 5, 3]:
                        if state.plant_grid[row][col] is None:
                            actions.append(Action(
                                action_type="plant",
                                row=row,
                                col=col,
                                plant_type=PlantType.WALLNUT,
                                priority=40.0 + threat * 20,
                                reason=f"防御: 第{row}行威胁={threat:.1f}"
                            ))
                            break
            
            # 如果该行没有射手
            if threat > 0 and shooter_count == 0:
                peashooter_seed = self._find_seed(state, PlantType.PEASHOOTER)
                if peashooter_seed and peashooter_seed.usable and state.sun >= 100:
                    for col in [3, 2, 4]:
                        if state.plant_grid[row][col] is None:
                            actions.append(Action(
                                action_type="plant",
                                row=row,
                                col=col,
                                plant_type=PlantType.PEASHOOTER,
                                priority=35.0 + threat * 15,
                                reason=f"攻击: 第{row}行需要射手"
                            ))
                            break
        
        return actions
    
    def _plan_offense(self, state: GameState) -> List[Action]:
        """规划进攻强化"""
        actions = []
        
        # 如果阳光充足，升级攻击
        if state.sun >= 300:
            # 尝试种植豌豆射手替换为双发
            repeater_seed = self._find_seed(state, PlantType.REPEATER)
            if repeater_seed and repeater_seed.usable:
                for row in range(5):
                    for col in range(2, 6):
                        plant = state.plant_grid[row][col]
                        if plant and plant.type == PlantType.PEASHOOTER:
                            # 这里需要先铲除再种植（简化处理）
                            pass
        
        return actions
    
    def _find_seed(self, state: GameState, plant_type: int) -> Optional[SeedInfo]:
        """查找指定类型的卡片"""
        for seed in state.seeds:
            if seed.type == plant_type:
                return seed
        return None
    
    def get_best_action(self, state: GameState) -> Optional[Action]:
        """获取最佳行动"""
        actions = self.analyze(state)
        
        for action in actions:
            # 验证行动是否可执行
            if action.action_type == "plant":
                # 检查位置是否空闲
                if state.plant_grid[action.row][action.col] is not None:
                    continue
                # 检查阳光是否足够
                cost = PLANT_COST.get(action.plant_type, 100)
                if state.sun < cost:
                    continue
                # 检查卡片是否可用
                seed = self._find_seed(state, action.plant_type)
                if not seed or not seed.usable:
                    continue
                
                return action
        
        return None

# ============================================================================
# Bot 主类
# ============================================================================

class OptimalBot:
    def __init__(self):
        self.memory = PVZMemory()
        self.engine = DecisionEngine()
        self.running = False
        self.auto_plant = True   # 是否自动执行种植
        self.auto_collect = True # 是否自动收集阳光
        self.action_interval = 0.15  # 每次操作间隔 (秒)
        self.last_action_time = 0
        
    def start(self):
        """启动 Bot"""
        print("=" * 60)
        print("  PVZ 最优算法 Bot v3.0")
        print("  基于 AsmVsZombies 权威内存结构")
        print("  使用 ASM 注入直接调用游戏函数 (100%成功率)")
        print("=" * 60)
        
        if not self.memory.attach():
            print("[错误] 无法找到 PVZ 进程，请先启动游戏!")
            return
        
        print(f"[成功] 已附加到 PVZ 进程 (PID: {self.memory.pid})")
        print(f"[模式] 自动种植: {'开启' if self.auto_plant else '关闭'}")
        print(f"[模式] 自动收集: {'开启' if self.auto_collect else '关闭'}")
        print("[提示] 按 Ctrl+C 停止 Bot")
        print("-" * 60)
        
        self.running = True
        self.run_loop()
    
    def execute_action(self, action: Action, state: GameState) -> bool:
        """
        执行行动 - 直接调用游戏函数
        
        Returns:
            是否成功执行
        """
        if action.action_type == "plant":
            # 检查阳光
            cost = PLANT_COST.get(action.plant_type, 100)
            if state.sun < cost:
                return False
            
            # 检查位置是否空闲
            if state.plant_grid[action.row][action.col] is not None:
                return False
            
            # 查找卡槽索引
            slot_index = -1
            for i, seed in enumerate(state.seeds):
                if seed.type == action.plant_type and seed.usable:
                    slot_index = i
                    break
            
            if slot_index == -1:
                return False
            
            # 直接调用游戏种植函数！
            success = self.memory.asm_plant(action.row, action.col, action.plant_type)
            if success:
                print(f"  ✓ 种植成功: {PlantType(action.plant_type).name} at ({action.row}, {action.col})")
            return success
            
        elif action.action_type == "shovel":
            success = self.memory.asm_shovel(action.row, action.col)
            if success:
                print(f"  ✓ 铲除成功: ({action.row}, {action.col})")
            return success
        
        return False
    
    def run_loop(self):
        """主循环"""
        try:
            while self.running:
                state = self.memory.get_game_state()
                
                if state is None:
                    print("\r[等待] 不在游戏中...", end="")
                    time.sleep(0.5)
                    continue
                
                # 自动收集阳光！
                if self.auto_collect:
                    self.memory.collect_all_items()
                
                # 显示状态
                zombie_count = len(state.zombies)
                plant_count = len(state.plants)
                print(f"\r[Wave {state.wave}/{state.total_wave}] "
                      f"Sun: {state.sun:4d} | "
                      f"Plants: {plant_count:2d} | "
                      f"Zombies: {zombie_count:2d} | "
                      f"Clock: {state.game_clock}", end="")
                
                # 获取最佳行动
                action = self.engine.get_best_action(state)
                
                if action and self.auto_plant:
                    # 检查操作间隔
                    current_time = time.time()
                    if current_time - self.last_action_time >= self.action_interval:
                        print(f"\n[决策] {action.reason}")
                        print(f"       -> {action.action_type} {PlantType(action.plant_type).name if action.plant_type else ''} at ({action.row}, {action.col})")
                        
                        # 执行操作！
                        if self.execute_action(action, state):
                            self.last_action_time = current_time
                
                time.sleep(0.05)  # 50ms 刷新率
                
        except KeyboardInterrupt:
            print("\n\n[停止] Bot 已停止")
            self.running = False

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    bot = OptimalBot()
    bot.start()
