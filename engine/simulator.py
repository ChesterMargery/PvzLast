"""
Frame-precise Game State Simulator for PVZ
Implements game logic matching re-plants-vs-zombies Board::Update()

Reference:
- Board.cpp: Board::Update() for main loop order
- Plant.cpp: Plant::Update(), Plant::Fire() for plant behavior
- Zombie.cpp: Zombie::Update(), Zombie::TakeDamage() for zombie behavior
- Projectile.cpp: Projectile::Update(), Projectile::CheckForCollision()

Update Order (per frame):
1. Update projectiles (position and collision)
2. Update zombies (position and behavior)
3. Update plants (state and attacks)
4. Clean up dead entities
5. Check game over conditions

Time unit: 1 frame = 1 centisecond (cs) = 10 milliseconds
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import IntEnum
import copy

from data.plants import (
    PlantType,
    PLANT_HP,
    PLANT_COST,
    ATTACKING_PLANTS,
)
from data.zombies import (
    ZombieType,
    ZOMBIE_HP_DATA,
    ZOMBIE_BASE_SPEED,
    SLOW_SPEED_MULTIPLIER,
    ZOMBIE_BITE_DAMAGE,
    ZOMBIE_BITE_INTERVAL,
    is_gargantuar,
    GARGANTUAR_ZOMBIES,
)
from data.projectiles import (
    ProjectileType,
    PROJECTILE_DAMAGE,
    PROJECTILE_SPEED,
    SLOWING_PROJECTILES,
    SPLASH_PROJECTILES,
    PROJECTILE_SPLASH_RADIUS,
    is_slowing_projectile,
    is_splash_projectile,
)
from data.constants import (
    GRID_WIDTH,
    GRID_HEIGHT,
    LAWN_LEFT_X,
    LAWN_RIGHT_X,
    GRID_COLS,
    GRID_ROWS,
    PEASHOOTER_ATTACK_INTERVAL,
    PEA_DAMAGE,
    SLOW_DURATION,
    COB_EXPLODE_RADIUS,
)


# ============================================================================
# Simulator Entity Classes
# ============================================================================

@dataclass
class Plant:
    """Plant entity for simulation"""
    type: PlantType
    row: int
    col: int
    health: int
    attack_countdown: int = 0
    is_alive: bool = True
    
    # Unique identifier
    id: int = 0
    
    @property
    def x(self) -> float:
        """Get x position in pixels"""
        return LAWN_LEFT_X + self.col * GRID_WIDTH
    
    @classmethod
    def create(cls, plant_type: PlantType, row: int, col: int, plant_id: int = 0) -> Plant:
        """Factory method to create a plant with default HP"""
        hp = PLANT_HP.get(plant_type, 300)
        attack_countdown = PEASHOOTER_ATTACK_INTERVAL if plant_type in ATTACKING_PLANTS else 0
        return cls(
            type=plant_type,
            row=row,
            col=col,
            health=hp,
            attack_countdown=attack_countdown,
            is_alive=True,
            id=plant_id,
        )


@dataclass
class Zombie:
    """Zombie entity for simulation"""
    type: ZombieType
    row: int
    x: float
    body_health: int
    armor_health: int = 0  # Accessory HP (cone/bucket/door)
    shield_health: int = 0  # Shield HP (screen door)
    is_alive: bool = True
    is_slowed: bool = False
    slow_countdown: int = 0
    is_frozen: bool = False
    freeze_countdown: int = 0
    is_eating: bool = False
    eat_countdown: int = 0
    target_plant_id: int = -1  # ID of plant being eaten
    
    # Unique identifier
    id: int = 0
    
    @property
    def total_health(self) -> int:
        """Get total HP including all components"""
        return self.body_health + self.armor_health + self.shield_health
    
    @property
    def effective_speed(self) -> float:
        """Get current movement speed considering effects"""
        if self.is_frozen or self.is_eating:
            return 0.0
        base_speed = ZOMBIE_BASE_SPEED.get(self.type, 0.23)
        if self.is_slowed:
            return base_speed * SLOW_SPEED_MULTIPLIER
        return base_speed
    
    @classmethod
    def create(cls, zombie_type: ZombieType, row: int, x: float = 800.0, zombie_id: int = 0) -> Zombie:
        """Factory method to create a zombie with default HP"""
        body_hp, armor_hp = ZOMBIE_HP_DATA.get(zombie_type, (270, 0))
        return cls(
            type=zombie_type,
            row=row,
            x=x,
            body_health=body_hp,
            armor_health=armor_hp,
            shield_health=0,
            is_alive=True,
            is_slowed=False,
            slow_countdown=0,
            is_frozen=False,
            freeze_countdown=0,
            is_eating=False,
            eat_countdown=0,
            target_plant_id=-1,
            id=zombie_id,
        )


@dataclass
class Projectile:
    """Projectile entity for simulation"""
    type: ProjectileType
    row: int
    x: float
    y: float = 0.0
    damage: int = 20
    is_alive: bool = True
    source_plant_id: int = -1
    
    # Unique identifier
    id: int = 0
    
    @property
    def speed(self) -> float:
        """Get projectile speed"""
        return PROJECTILE_SPEED.get(self.type, 3.7)
    
    @classmethod
    def create(cls, proj_type: ProjectileType, row: int, x: float, y: float = 0.0,
               proj_id: int = 0, source_plant_id: int = -1) -> Projectile:
        """Factory method to create a projectile"""
        damage = PROJECTILE_DAMAGE.get(proj_type, 20)
        return cls(
            type=proj_type,
            row=row,
            x=x,
            y=y,
            damage=damage,
            is_alive=True,
            source_plant_id=source_plant_id,
            id=proj_id,
        )


@dataclass
class GameState:
    """Complete game state snapshot for MCTS"""
    frame: int = 0
    sun: int = 50
    plants: List[Plant] = field(default_factory=list)
    zombies: List[Zombie] = field(default_factory=list)
    projectiles: List[Projectile] = field(default_factory=list)
    wave: int = 0
    is_game_over: bool = False
    is_win: bool = False
    
    @property
    def alive_plants(self) -> List[Plant]:
        """Get all alive plants"""
        return [p for p in self.plants if p.is_alive]
    
    @property
    def alive_zombies(self) -> List[Zombie]:
        """Get all alive zombies"""
        return [z for z in self.zombies if z.is_alive]
    
    @property
    def alive_projectiles(self) -> List[Projectile]:
        """Get all alive projectiles"""
        return [p for p in self.projectiles if p.is_alive]


# ============================================================================
# Game Simulator
# ============================================================================

class GameSimulator:
    """
    Frame-precise game state simulator
    
    Update order matches re-plants-vs-zombies Board::Update():
    1. Update projectiles (position and collision)
    2. Update zombies (position and behavior)
    3. Update plants (state and attacks)
    4. Clean up dead entities
    5. Check game over conditions
    """
    
    def __init__(self, sun: int = 50, scene: int = 0):
        """
        Initialize simulator
        
        Args:
            sun: Initial sun count
            scene: Scene type (0=day, 2=pool, etc.)
        """
        self.frame: int = 0
        self.sun: int = sun
        self.scene: int = scene
        self.wave: int = 0
        self.is_game_over: bool = False
        self.is_win: bool = False
        
        # Entity lists
        self.plants: List[Plant] = []
        self.zombies: List[Zombie] = []
        self.projectiles: List[Projectile] = []
        
        # Grid for quick plant lookup (row, col) -> plant_id
        self._plant_grid: Dict[Tuple[int, int], int] = {}
        
        # ID counters for entities
        self._next_plant_id: int = 0
        self._next_zombie_id: int = 0
        self._next_projectile_id: int = 0
        
        # Number of rows (5 for day/night, 6 for pool/fog)
        self._row_count = 6 if scene in [2, 3] else 5
    
    # ========================================================================
    # Main Simulation Loop
    # ========================================================================
    
    def tick(self) -> None:
        """
        Advance simulation by one frame (1cs = 10ms)
        
        Order matches Board::Update():
        1. Projectiles
        2. Zombies
        3. Plants
        4. Cleanup
        5. Game over check
        """
        if self.is_game_over:
            return
        
        self.frame += 1
        
        # 1. Update projectiles (position and collision)
        self._update_projectiles()
        
        # 2. Update zombies (position and behavior)
        self._update_zombies()
        
        # 3. Update plants (state and attacks)
        self._update_plants()
        
        # 4. Clean up dead entities
        self._cleanup_dead_entities()
        
        # 5. Check game over conditions
        self._check_game_over()
    
    def tick_n(self, n: int) -> None:
        """Advance simulation by n frames"""
        for _ in range(n):
            if self.is_game_over:
                break
            self.tick()
    
    # ========================================================================
    # Projectile Update
    # ========================================================================
    
    def _update_projectiles(self) -> None:
        """Update all projectiles (position and collision)"""
        for proj in self.projectiles:
            if not proj.is_alive:
                continue
            
            # Move projectile
            proj.x += proj.speed
            
            # Check if out of bounds
            if proj.x > LAWN_RIGHT_X + 50:
                proj.is_alive = False
                continue
            
            # Check collision with zombies
            self._check_projectile_collision(proj)
    
    def _check_projectile_collision(self, proj: Projectile) -> None:
        """Check and handle projectile collision with zombies"""
        if not proj.is_alive:
            return
        
        # Get zombies in the same row (or adjacent rows for splash)
        if is_splash_projectile(proj.type):
            target_rows = [proj.row - 1, proj.row, proj.row + 1]
        else:
            target_rows = [proj.row]
        
        hit_any = False
        for zombie in self.zombies:
            if not zombie.is_alive:
                continue
            if zombie.row not in target_rows:
                continue
            
            # Simple collision check: projectile x overlaps with zombie
            # Zombie hitbox is approximately 20 pixels wide centered at x
            zombie_left = zombie.x - 20
            zombie_right = zombie.x + 20
            
            if is_splash_projectile(proj.type):
                # Splash projectiles use radius and hit all zombies in range
                splash_radius = PROJECTILE_SPLASH_RADIUS.get(proj.type, 80)
                if abs(proj.x - zombie.x) <= splash_radius:
                    self._apply_projectile_damage(proj, zombie)
                    hit_any = True
            else:
                # Direct hit check
                if zombie_left <= proj.x <= zombie_right:
                    self._apply_projectile_damage(proj, zombie)
                    proj.is_alive = False
                    return
        
        # Mark splash projectile as dead after hitting at least one zombie
        if is_splash_projectile(proj.type) and hit_any:
            proj.is_alive = False
    
    def _apply_projectile_damage(self, proj: Projectile, zombie: Zombie) -> None:
        """Apply projectile damage to zombie"""
        # Apply slow effect if applicable
        if is_slowing_projectile(proj.type):
            zombie.is_slowed = True
            zombie.slow_countdown = SLOW_DURATION
        
        # Apply damage
        self._apply_damage_to_zombie(zombie, proj.damage)
    
    # ========================================================================
    # Zombie Update
    # ========================================================================
    
    def _update_zombies(self) -> None:
        """Update all zombies (position and behavior)"""
        for zombie in self.zombies:
            if not zombie.is_alive:
                continue
            
            # Update status effects
            self._update_zombie_status(zombie)
            
            # Check if eating a plant
            if zombie.is_eating:
                self._update_zombie_eating(zombie)
            else:
                # Move zombie
                zombie.x -= zombie.effective_speed
                
                # Check for plant collision
                self._check_zombie_plant_collision(zombie)
    
    def _update_zombie_status(self, zombie: Zombie) -> None:
        """Update zombie status effects (slow, freeze)"""
        if zombie.slow_countdown > 0:
            zombie.slow_countdown -= 1
            if zombie.slow_countdown <= 0:
                zombie.is_slowed = False
        
        if zombie.freeze_countdown > 0:
            zombie.freeze_countdown -= 1
            if zombie.freeze_countdown <= 0:
                zombie.is_frozen = False
    
    def _update_zombie_eating(self, zombie: Zombie) -> None:
        """Update zombie eating behavior"""
        zombie.eat_countdown -= 1
        
        if zombie.eat_countdown <= 0:
            # Deal damage to plant
            target_plant = self._get_plant_by_id(zombie.target_plant_id)
            if target_plant and target_plant.is_alive:
                target_plant.health -= int(ZOMBIE_BITE_DAMAGE)
                if target_plant.health <= 0:
                    target_plant.is_alive = False
                    self._remove_plant_from_grid(target_plant)
                    zombie.is_eating = False
                    zombie.target_plant_id = -1
                else:
                    # Reset eat countdown for next bite
                    zombie.eat_countdown = ZOMBIE_BITE_INTERVAL
            else:
                # Plant is gone, stop eating
                zombie.is_eating = False
                zombie.target_plant_id = -1
    
    def _check_zombie_plant_collision(self, zombie: Zombie) -> None:
        """Check if zombie collides with any plant"""
        for plant in self.plants:
            if not plant.is_alive:
                continue
            if plant.row != zombie.row:
                continue
            
            # Check if zombie reached plant
            plant_x = plant.x
            plant_right = plant_x + 40  # Plant hitbox extends right
            
            if zombie.x <= plant_right:
                # Start eating
                zombie.is_eating = True
                zombie.target_plant_id = plant.id
                zombie.eat_countdown = ZOMBIE_BITE_INTERVAL
                break
    
    # ========================================================================
    # Plant Update
    # ========================================================================
    
    def _update_plants(self) -> None:
        """Update all plants (state and attacks)"""
        for plant in self.plants:
            if not plant.is_alive:
                continue
            
            # Only attacking plants have countdown
            if plant.type not in ATTACKING_PLANTS:
                continue
            
            # Decrement attack countdown
            if plant.attack_countdown > 0:
                plant.attack_countdown -= 1
            
            # Check if should fire
            if plant.attack_countdown <= 0:
                if self._should_plant_fire(plant):
                    self._plant_fire(plant)
                    plant.attack_countdown = PEASHOOTER_ATTACK_INTERVAL
    
    def _should_plant_fire(self, plant: Plant) -> bool:
        """Check if plant should fire (zombies in row(s) ahead)"""
        # Determine which rows this plant can target
        if plant.type == PlantType.THREEPEATER:
            target_rows = [plant.row - 1, plant.row, plant.row + 1]
        else:
            target_rows = [plant.row]
        
        for zombie in self.zombies:
            if not zombie.is_alive:
                continue
            if zombie.row not in target_rows:
                continue
            # Check if zombie is ahead of plant
            if zombie.x > plant.x:
                return True
        return False
    
    def _plant_fire(self, plant: Plant) -> None:
        """Fire projectile(s) from plant based on plant type"""
        proj_type = self._get_projectile_type_for_plant(plant.type)
        if proj_type is None:
            return
        
        # Determine number of projectiles and rows based on plant type
        if plant.type == PlantType.REPEATER:
            # Repeater fires 2 peas in the same row
            self._create_projectile(proj_type, plant.row, plant.x + 40, plant.id)
            self._create_projectile(proj_type, plant.row, plant.x + 45, plant.id)  # Slight offset
        elif plant.type == PlantType.THREEPEATER:
            # Threepeater fires 3 peas in adjacent rows
            for row_offset in [-1, 0, 1]:
                target_row = plant.row + row_offset
                if 0 <= target_row < self._row_count:
                    self._create_projectile(proj_type, target_row, plant.x + 40, plant.id)
        elif plant.type == PlantType.SPLITPEA:
            # Splitpea fires forward and backward
            self._create_projectile(proj_type, plant.row, plant.x + 40, plant.id)
            # Create backward projectile (negative speed)
            back_proj = Projectile.create(
                proj_type=proj_type,
                row=plant.row,
                x=plant.x - 10,
                y=0,
                proj_id=self._next_projectile_id,
                source_plant_id=plant.id,
            )
            self._next_projectile_id += 1
            self.projectiles.append(back_proj)
            # Note: backward projectile moves left - handled in update
        elif plant.type == PlantType.GATLINGPEA:
            # Gatling pea fires 4 peas
            for i in range(4):
                self._create_projectile(proj_type, plant.row, plant.x + 40 + i * 3, plant.id)
        else:
            # Single projectile for other plants
            self._create_projectile(proj_type, plant.row, plant.x + 40, plant.id)
    
    def _create_projectile(self, proj_type: ProjectileType, row: int, x: float, 
                          source_plant_id: int) -> None:
        """Create a single projectile"""
        proj = Projectile.create(
            proj_type=proj_type,
            row=row,
            x=x,
            y=0,
            proj_id=self._next_projectile_id,
            source_plant_id=source_plant_id,
        )
        self._next_projectile_id += 1
        self.projectiles.append(proj)
    
    def _get_projectile_type_for_plant(self, plant_type: PlantType) -> Optional[ProjectileType]:
        """Get projectile type for attacking plant"""
        plant_to_proj = {
            PlantType.PEASHOOTER: ProjectileType.PEA,
            PlantType.SNOW_PEA: ProjectileType.SNOW_PEA,
            PlantType.REPEATER: ProjectileType.PEA,
            PlantType.THREEPEATER: ProjectileType.PEA,
            PlantType.SPLITPEA: ProjectileType.PEA,
            PlantType.GATLINGPEA: ProjectileType.PEA,
            PlantType.PUFFSHROOM: ProjectileType.PUFF,
            PlantType.FUMESHROOM: ProjectileType.FUME,
            PlantType.SEASHROOM: ProjectileType.PUFF,
            PlantType.SCAREDYSHROOM: ProjectileType.PUFF,
            PlantType.CACTUS: ProjectileType.CACTUS,
            PlantType.CABBAGEPULT: ProjectileType.CABBAGE,
            PlantType.KERNELPULT: ProjectileType.KERNEL,
            PlantType.MELONPULT: ProjectileType.MELON,
            PlantType.WINTERMELON: ProjectileType.WINTERMELON,
        }
        return plant_to_proj.get(plant_type)
    
    # ========================================================================
    # Damage Calculation
    # ========================================================================
    
    def _apply_damage_to_zombie(self, zombie: Zombie, damage: int) -> None:
        """
        Apply damage to zombie following correct order:
        Shield → Armor → Body
        
        Reference: Zombie::TakeDamage() in Zombie.cpp
        """
        remaining_damage = damage
        
        # 1. Shield absorbs first
        if zombie.shield_health > 0:
            absorbed = min(zombie.shield_health, remaining_damage)
            zombie.shield_health -= absorbed
            remaining_damage -= absorbed
        
        # 2. Armor absorbs next
        if remaining_damage > 0 and zombie.armor_health > 0:
            absorbed = min(zombie.armor_health, remaining_damage)
            zombie.armor_health -= absorbed
            remaining_damage -= absorbed
        
        # 3. Body takes remaining damage
        if remaining_damage > 0:
            zombie.body_health -= remaining_damage
            if zombie.body_health <= 0:
                zombie.is_alive = False
    
    # ========================================================================
    # Entity Cleanup
    # ========================================================================
    
    def _cleanup_dead_entities(self) -> None:
        """Remove dead entities from lists"""
        # Clean up projectiles (remove dead)
        self.projectiles = [p for p in self.projectiles if p.is_alive]
        
        # Clean up plants (keep references but mark dead)
        for plant in self.plants:
            if not plant.is_alive:
                self._remove_plant_from_grid(plant)
        
        # Clean up zombies (keep references but mark dead)
        # Dead zombies are kept for death animation but not processed
    
    def _remove_plant_from_grid(self, plant: Plant) -> None:
        """Remove plant from grid lookup"""
        key = (plant.row, plant.col)
        if key in self._plant_grid and self._plant_grid[key] == plant.id:
            del self._plant_grid[key]
    
    # ========================================================================
    # Game Over Check
    # ========================================================================
    
    def _check_game_over(self) -> None:
        """Check if game is over (zombies reached left edge)"""
        for zombie in self.zombies:
            if not zombie.is_alive:
                continue
            # Zombie reached left edge (game over)
            if zombie.x < 0:
                self.is_game_over = True
                self.is_win = False
                return
        
        # Check win condition (all zombies dead and no more waves)
        # This is simplified - full implementation would check wave spawner
        alive_zombies = [z for z in self.zombies if z.is_alive]
        if not alive_zombies and self.wave > 0:
            # No zombies left - could be win (depends on wave spawner)
            pass
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_plant_by_id(self, plant_id: int) -> Optional[Plant]:
        """Get plant by ID"""
        for plant in self.plants:
            if plant.id == plant_id:
                return plant
        return None
    
    def _get_zombie_by_id(self, zombie_id: int) -> Optional[Zombie]:
        """Get zombie by ID"""
        for zombie in self.zombies:
            if zombie.id == zombie_id:
                return zombie
        return None
    
    # ========================================================================
    # MCTS Support Methods
    # ========================================================================
    
    def snapshot(self) -> GameState:
        """
        Create a complete state snapshot for MCTS
        
        Returns:
            GameState with deep copies of all entities
        """
        return GameState(
            frame=self.frame,
            sun=self.sun,
            plants=[copy.deepcopy(p) for p in self.plants],
            zombies=[copy.deepcopy(z) for z in self.zombies],
            projectiles=[copy.deepcopy(p) for p in self.projectiles],
            wave=self.wave,
            is_game_over=self.is_game_over,
            is_win=self.is_win,
        )
    
    def restore(self, state: GameState) -> None:
        """
        Restore simulator state from snapshot
        
        Args:
            state: GameState snapshot to restore
        """
        self.frame = state.frame
        self.sun = state.sun
        self.plants = [copy.deepcopy(p) for p in state.plants]
        self.zombies = [copy.deepcopy(z) for z in state.zombies]
        self.projectiles = [copy.deepcopy(p) for p in state.projectiles]
        self.wave = state.wave
        self.is_game_over = state.is_game_over
        self.is_win = state.is_win
        
        # Rebuild plant grid
        self._plant_grid = {}
        for plant in self.plants:
            if plant.is_alive:
                self._plant_grid[(plant.row, plant.col)] = plant.id
        
        # Update ID counters
        if self.plants:
            self._next_plant_id = max(p.id for p in self.plants) + 1
        if self.zombies:
            self._next_zombie_id = max(z.id for z in self.zombies) + 1
        if self.projectiles:
            self._next_projectile_id = max(p.id for p in self.projectiles) + 1
    
    def clone(self) -> GameSimulator:
        """
        Create a deep copy of the simulator
        
        Returns:
            New GameSimulator instance with identical state
        """
        new_sim = GameSimulator(sun=self.sun, scene=self.scene)
        new_sim.restore(self.snapshot())
        new_sim._row_count = self._row_count
        new_sim._next_plant_id = self._next_plant_id
        new_sim._next_zombie_id = self._next_zombie_id
        new_sim._next_projectile_id = self._next_projectile_id
        return new_sim
    
    # ========================================================================
    # Operation Interface
    # ========================================================================
    
    def place_plant(self, plant_type: PlantType, row: int, col: int) -> bool:
        """
        Place a plant on the grid
        
        Args:
            plant_type: Type of plant to place
            row: Row (0-based)
            col: Column (0-based)
            
        Returns:
            True if plant was placed successfully
        """
        # Validate position
        if row < 0 or row >= self._row_count:
            return False
        if col < 0 or col >= GRID_COLS:
            return False
        
        # Check if cell is occupied
        if (row, col) in self._plant_grid:
            return False
        
        # Check sun cost
        cost = PLANT_COST.get(plant_type, 100)
        if self.sun < cost:
            return False
        
        # Create and add plant
        plant = Plant.create(plant_type, row, col, self._next_plant_id)
        self._next_plant_id += 1
        self.plants.append(plant)
        self._plant_grid[(row, col)] = plant.id
        self.sun -= cost
        
        return True
    
    def remove_plant(self, row: int, col: int) -> bool:
        """
        Remove (shovel) a plant from the grid
        
        Args:
            row: Row (0-based)
            col: Column (0-based)
            
        Returns:
            True if plant was removed
        """
        key = (row, col)
        if key not in self._plant_grid:
            return False
        
        plant_id = self._plant_grid[key]
        plant = self._get_plant_by_id(plant_id)
        if plant:
            plant.is_alive = False
            del self._plant_grid[key]
            return True
        
        return False
    
    def spawn_zombie(self, zombie_type: ZombieType, row: int, x: float = 800.0) -> None:
        """
        Spawn a zombie on the field
        
        Args:
            zombie_type: Type of zombie to spawn
            row: Row to spawn on
            x: Starting x position (default: right edge)
        """
        zombie = Zombie.create(zombie_type, row, x, self._next_zombie_id)
        self._next_zombie_id += 1
        self.zombies.append(zombie)
    
    def get_plant_at(self, row: int, col: int) -> Optional[Plant]:
        """
        Get plant at grid position
        
        Args:
            row: Row
            col: Column
            
        Returns:
            Plant at position or None
        """
        key = (row, col)
        if key not in self._plant_grid:
            return None
        return self._get_plant_by_id(self._plant_grid[key])
    
    def get_zombies_in_row(self, row: int) -> List[Zombie]:
        """Get all alive zombies in a row"""
        return [z for z in self.zombies if z.is_alive and z.row == row]
    
    def get_closest_zombie_in_row(self, row: int) -> Optional[Zombie]:
        """Get closest alive zombie to left edge in a row"""
        row_zombies = self.get_zombies_in_row(row)
        if not row_zombies:
            return None
        return min(row_zombies, key=lambda z: z.x)
    
    @property
    def alive_zombie_count(self) -> int:
        """Get count of alive zombies"""
        return sum(1 for z in self.zombies if z.is_alive)
    
    @property
    def alive_plant_count(self) -> int:
        """Get count of alive plants"""
        return sum(1 for p in self.plants if p.is_alive)
