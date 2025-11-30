"""
Judge Module
Provides damage judgment, collision detection, and prediction algorithms
Based on AVZ tutorial/scripts/liang_yi/judge.h
"""

from judge.collision import (
    is_cherry_hit,
    is_cob_hit,
    is_jalapeno_hit,
    is_doom_hit,
    is_giga_hammer,
    is_box_explode,
    is_will_be_crushed,
)
from judge.damage import (
    calculate_cob_damage,
    calculate_cherry_damage,
    calculate_gloom_dps,
    can_kill_zombie,
)
from judge.prediction import (
    predict_position,
    time_to_reach,
    is_giga_io_dead,
    get_safe_time,
)
