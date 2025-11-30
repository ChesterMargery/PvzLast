"""
Game Reader Module
Factory class for reading game objects from memory
"""

from typing import List

from data.offsets import Offset
from memory.reader import MemoryReader
from game.zombie import ZombieInfo
from game.plant import PlantInfo
from game.projectile import ProjectileInfo, ProjectileType
from game.lawnmower import LawnmowerInfo
from game.place_item import PlaceItemInfo
from game.state import GameState, SeedInfo
from game.grid import Grid


class GameReader:
    """
    Factory class for reading game entities from memory
    
    Converts raw memory addresses into structured Python objects.
    """
    
    def __init__(self, reader: MemoryReader):
        """
        Initialize GameReader
        
        Args:
            reader: MemoryReader instance for reading memory
        """
        self.reader = reader
    
    # ========================================================================
    # Single Entity Readers
    # ========================================================================
    
    def read_zombie(self, addr: int, index: int) -> ZombieInfo:
        """
        Read a single zombie from memory
        
        Args:
            addr: Base address of zombie structure
            index: Index in zombie array
            
        Returns:
            ZombieInfo instance
        """
        return ZombieInfo(
            index=index,
            row=self.reader.read_int(addr + Offset.Z_ROW),
            x=self.reader.read_float(addr + Offset.Z_X),
            y=self.reader.read_float(addr + Offset.Z_Y),
            type=self.reader.read_int(addr + Offset.Z_TYPE),
            hp=self.reader.read_int(addr + Offset.Z_HP),
            hp_max=self.reader.read_int(addr + Offset.Z_HP_MAX),
            accessory_hp=self.reader.read_int(addr + Offset.Z_ACCESSORY_HP_1),
            state=self.reader.read_int(addr + Offset.Z_STATE),
            speed=self.reader.read_float(addr + Offset.Z_SPEED),
            slow_countdown=self.reader.read_int(addr + Offset.Z_SLOW_COUNTDOWN),
            freeze_countdown=self.reader.read_int(addr + Offset.Z_FREEZE_COUNTDOWN),
            butter_countdown=self.reader.read_int(addr + Offset.Z_BUTTER_COUNTDOWN),
            at_wave=self.reader.read_int(addr + Offset.Z_AT_WAVE),
            height=self.reader.read_float(addr + Offset.Z_HEIGHT),
            exist_time=self.reader.read_int(addr + Offset.Z_EXIST_TIME),
            state_countdown=self.reader.read_int(addr + Offset.Z_STATE_COUNTDOWN),
            is_eating=self.reader.read_bool(addr + Offset.Z_IS_EAT),
            hurt_width=self.reader.read_int(addr + Offset.Z_HURT_WIDTH),
            hurt_height=self.reader.read_int(addr + Offset.Z_HURT_HEIGHT),
            bullet_x=self.reader.read_int(addr + Offset.Z_BULLET_X),
            bullet_y=self.reader.read_int(addr + Offset.Z_BULLET_Y),
            attack_x=self.reader.read_int(addr + Offset.Z_ATTACK_X),
            attack_y=self.reader.read_int(addr + Offset.Z_ATTACK_Y),
        )
    
    def read_plant(self, addr: int, index: int) -> PlantInfo:
        """
        Read a single plant from memory
        
        Args:
            addr: Base address of plant structure
            index: Index in plant array
            
        Returns:
            PlantInfo instance
        """
        return PlantInfo(
            index=index,
            row=self.reader.read_int(addr + Offset.P_ROW),
            col=self.reader.read_int(addr + Offset.P_COL),
            type=self.reader.read_int(addr + Offset.P_TYPE),
            hp=self.reader.read_int(addr + Offset.P_HP),
            hp_max=self.reader.read_int(addr + Offset.P_HP_MAX),
            state=self.reader.read_int(addr + Offset.P_STATE),
            shoot_countdown=self.reader.read_int(addr + Offset.P_SHOOT_COUNTDOWN),
            effective=self.reader.read_int(addr + Offset.P_EFFECTIVE) != 0,
            pumpkin_hp=self.reader.read_int(addr + Offset.P_PUMPKIN_HP),
            cob_countdown=self.reader.read_int(addr + Offset.P_COB_COUNTDOWN),
            cob_ready=self.reader.read_bool(addr + Offset.P_COB_READY),
            visible=self.reader.read_bool(addr + Offset.P_VISIBLE),
            explode_countdown=self.reader.read_int(addr + Offset.P_EXPLODE_COUNTDOWN),
            blover_countdown=self.reader.read_int(addr + Offset.P_BLOVER_COUNTDOWN),
            mushroom_countdown=self.reader.read_int(addr + Offset.P_MUSHROOM_COUNTDOWN),
            bungee_state=self.reader.read_int(addr + Offset.P_BUNGEE_STATE),
            hurt_width=self.reader.read_int(addr + Offset.P_HURT_WIDTH),
            hurt_height=self.reader.read_int(addr + Offset.P_HURT_HEIGHT),
        )
    
    def read_projectile(self, addr: int, index: int) -> ProjectileInfo:
        """
        Read a single projectile from memory
        
        Args:
            addr: Base address of projectile structure
            index: Index in projectile array
            
        Returns:
            ProjectileInfo instance
        """
        return ProjectileInfo(
            index=index,
            x=self.reader.read_float(addr + Offset.PR_X),
            y=self.reader.read_float(addr + Offset.PR_Y),
            row=self.reader.read_int(addr + Offset.PR_ROW),
            type=self.reader.read_int(addr + Offset.PR_TYPE),
            exist_time=self.reader.read_int(addr + Offset.PR_EXIST_TIME),
            is_dead=self.reader.read_bool(addr + Offset.PR_DEAD),
            cob_target_x=self.reader.read_float(addr + Offset.PR_COB_TARGET_X),
            cob_target_row=self.reader.read_int(addr + Offset.PR_COB_TARGET_ROW),
        )
    
    def read_lawnmower(self, addr: int, index: int) -> LawnmowerInfo:
        """
        Read a single lawnmower from memory
        
        Args:
            addr: Base address of lawnmower structure
            index: Index in lawnmower array
            
        Returns:
            LawnmowerInfo instance
        """
        return LawnmowerInfo(
            index=index,
            row=self.reader.read_int(addr + Offset.LM_ROW),
            x=self.reader.read_float(addr + Offset.LM_X),
            state=self.reader.read_int(addr + Offset.LM_STATE),
            is_dead=self.reader.read_bool(addr + Offset.LM_DEAD),
        )
    
    def read_place_item(self, addr: int, index: int) -> PlaceItemInfo:
        """
        Read a single place item from memory
        
        Args:
            addr: Base address of place item structure
            index: Index in place item array
            
        Returns:
            PlaceItemInfo instance
        """
        return PlaceItemInfo(
            index=index,
            row=self.reader.read_int(addr + Offset.PI_ROW),
            col=self.reader.read_int(addr + Offset.PI_COL),
            type=self.reader.read_int(addr + Offset.PI_TYPE),
            value=self.reader.read_int(addr + Offset.PI_VALUE),
            is_dead=self.reader.read_bool(addr + Offset.PI_DEAD),
        )
    
    def read_seed(self, addr: int, index: int) -> SeedInfo:
        """
        Read a single seed card from memory
        
        Args:
            addr: Base address of seed structure
            index: Index in seed array
            
        Returns:
            SeedInfo instance
        """
        return SeedInfo(
            index=index,
            type=self.reader.read_int(addr + Offset.S_TYPE),
            recharge_countdown=self.reader.read_int(addr + Offset.S_RECHARGE_COUNTDOWN),
            recharge_time=self.reader.read_int(addr + Offset.S_RECHARGE_TIME),
            usable=self.reader.read_bool(addr + Offset.S_USABLE),
            imitator_type=self.reader.read_int(addr + Offset.S_IMITATOR_TYPE),
        )
    
    # ========================================================================
    # Array Readers
    # ========================================================================
    
    def read_all_zombies(self) -> List[ZombieInfo]:
        """
        Read all zombies from memory
        
        Returns:
            List of ZombieInfo instances (alive zombies only)
        """
        zombies = []
        zombie_array = self.reader.get_zombie_array()
        if zombie_array == 0:
            return zombies
        
        zombie_count_max = self.reader.get_zombie_count_max()
        
        for i in range(zombie_count_max):
            addr = zombie_array + i * Offset.ZOMBIE_SIZE
            is_dead = self.reader.read_bool(addr + Offset.Z_DEAD)
            if not is_dead:
                zombies.append(self.read_zombie(addr, i))
        
        return zombies
    
    def read_all_plants(self) -> List[PlantInfo]:
        """
        Read all plants from memory
        
        Returns:
            List of PlantInfo instances (alive plants only)
        """
        plants = []
        plant_array = self.reader.get_plant_array()
        if plant_array == 0:
            return plants
        
        plant_count_max = self.reader.get_plant_count_max()
        
        for i in range(plant_count_max):
            addr = plant_array + i * Offset.PLANT_SIZE
            is_dead = self.reader.read_bool(addr + Offset.P_DEAD)
            if not is_dead:
                plants.append(self.read_plant(addr, i))
        
        return plants
    
    def read_all_projectiles(self) -> List[ProjectileInfo]:
        """
        Read all projectiles from memory
        
        Returns:
            List of ProjectileInfo instances (alive projectiles only)
        """
        projectiles = []
        board = self.reader.get_board()
        if board == 0:
            return projectiles
        
        projectile_array = self.reader.read_int(board + Offset.PROJECTILE_ARRAY)
        if projectile_array == 0:
            return projectiles
        
        projectile_count_max = self.reader.read_int(board + Offset.PROJECTILE_COUNT_MAX)
        
        for i in range(projectile_count_max):
            addr = projectile_array + i * Offset.PROJECTILE_SIZE
            is_dead = self.reader.read_bool(addr + Offset.PR_DEAD)
            if not is_dead:
                projectiles.append(self.read_projectile(addr, i))
        
        return projectiles
    
    def read_all_lawnmowers(self) -> List[LawnmowerInfo]:
        """
        Read all lawnmowers from memory
        
        Returns:
            List of LawnmowerInfo instances (alive lawnmowers only)
        """
        lawnmowers = []
        board = self.reader.get_board()
        if board == 0:
            return lawnmowers
        
        lawnmower_array = self.reader.read_int(board + Offset.LAWNMOWER_ARRAY)
        if lawnmower_array == 0:
            return lawnmowers
        
        lawnmower_count_max = self.reader.read_int(board + Offset.LAWNMOWER_COUNT_MAX)
        
        for i in range(lawnmower_count_max):
            addr = lawnmower_array + i * Offset.LAWNMOWER_SIZE
            is_dead = self.reader.read_bool(addr + Offset.LM_DEAD)
            if not is_dead:
                lawnmowers.append(self.read_lawnmower(addr, i))
        
        return lawnmowers
    
    def read_all_place_items(self) -> List[PlaceItemInfo]:
        """
        Read all place items from memory
        
        Returns:
            List of PlaceItemInfo instances (alive items only)
        """
        items = []
        board = self.reader.get_board()
        if board == 0:
            return items
        
        place_item_array = self.reader.read_int(board + Offset.PLACE_ITEM_ARRAY)
        if place_item_array == 0:
            return items
        
        place_item_count_max = self.reader.read_int(board + Offset.PLACE_ITEM_COUNT_MAX)
        
        for i in range(place_item_count_max):
            addr = place_item_array + i * Offset.PLACE_ITEM_SIZE
            is_dead = self.reader.read_bool(addr + Offset.PI_DEAD)
            if not is_dead:
                items.append(self.read_place_item(addr, i))
        
        return items
    
    def read_all_seeds(self, seed_count: int = 10) -> List[SeedInfo]:
        """
        Read all seed cards from memory
        
        Args:
            seed_count: Number of seed cards to read (default 10)
            
        Returns:
            List of SeedInfo instances
        """
        seeds = []
        seed_array = self.reader.get_seed_array()
        if seed_array == 0:
            return seeds
        
        for i in range(seed_count):
            addr = seed_array + i * Offset.SEED_SIZE
            seeds.append(self.read_seed(addr, i))
        
        return seeds
    
    # ========================================================================
    # Full State Reader
    # ========================================================================
    
    def read_game_state(self) -> GameState:
        """
        Read complete game state from memory
        
        Returns:
            GameState instance with all game data
        """
        board = self.reader.get_board()
        if board == 0:
            return GameState()
        
        # Read all entities
        zombies = self.read_all_zombies()
        plants = self.read_all_plants()
        projectiles = self.read_all_projectiles()
        lawnmowers = self.read_all_lawnmowers()
        place_items = self.read_all_place_items()
        seeds = self.read_all_seeds()
        
        # Build plant grid
        plant_grid = Grid()
        for plant in plants:
            plant_grid.set(plant.row, plant.col, plant)
        
        return GameState(
            sun=self.reader.read_int(board + Offset.SUN),
            wave=self.reader.read_int(board + Offset.WAVE),
            total_waves=self.reader.read_int(board + Offset.TOTAL_WAVE),
            refresh_countdown=self.reader.read_int(board + Offset.REFRESH_COUNTDOWN),
            huge_wave_countdown=self.reader.read_int(board + Offset.HUGE_WAVE_COUNTDOWN),
            game_clock=self.reader.read_int(board + Offset.GAME_CLOCK),
            global_clock=self.reader.read_int(board + Offset.GLOBAL_CLOCK),
            initial_countdown=self.reader.read_int(board + Offset.INITIAL_COUNTDOWN),
            click_pao_countdown=self.reader.read_int(board + Offset.CLICK_PAO_COUNTDOWN),
            zombie_refresh_hp=self.reader.read_int(board + Offset.ZOMBIE_REFRESH_HP),
            scene=self.reader.read_int(board + Offset.SCENE),
            zombies=zombies,
            plants=plants,
            seeds=seeds,
            projectiles=projectiles,
            lawnmowers=lawnmowers,
            place_items=place_items,
            plant_grid=plant_grid,
        )
