/**
 * @file game_data.h
 * @brief 游戏数据结构定义
 * 
 * 定义了游戏内部数据结构，包括植物、僵尸、场地等信息。
 */

#ifndef GAME_DATA_H
#define GAME_DATA_H

#include <cstdint>
#include "pvzlast.h"

namespace PvzLast {

/**
 * @brief 游戏内存地址常量
 */
namespace Address {
    constexpr uintptr_t BASE_ADDRESS = 0x6A9EC0;        ///< 基地址
    constexpr uintptr_t BOARD_OFFSET = 0x768;           ///< 场地偏移
    constexpr uintptr_t SUN_OFFSET = 0x5560;            ///< 阳光偏移
    constexpr uintptr_t WAVE_OFFSET = 0x557C;           ///< 波数偏移
    constexpr uintptr_t CLOCK_OFFSET = 0x5568;          ///< 时钟偏移
    constexpr uintptr_t PLANT_ARRAY_OFFSET = 0xAC;      ///< 植物数组偏移
    constexpr uintptr_t ZOMBIE_ARRAY_OFFSET = 0x90;     ///< 僵尸数组偏移
    constexpr uintptr_t SCENE_OFFSET = 0x554C;          ///< 场景偏移
}

/**
 * @brief 植物数据结构
 */
struct PlantData {
    int32_t x;              ///< X坐标（像素）
    int32_t y;              ///< Y坐标（像素）
    int32_t row;            ///< 行号
    int32_t col;            ///< 列号
    int32_t type;           ///< 植物类型
    int32_t hp;             ///< 当前生命值
    int32_t maxHp;          ///< 最大生命值
    int32_t state;          ///< 状态
    int32_t shootTimer;     ///< 射击计时器
    int32_t produceTimer;   ///< 生产计时器
    bool isVisible;         ///< 是否可见
    bool isAttacking;       ///< 是否在攻击
    bool isSquashed;        ///< 是否被压扁
    
    /**
     * @brief 检查植物是否存活
     * @return 存活返回 true
     */
    bool IsAlive() const {
        return hp > 0 && isVisible;
    }
    
    /**
     * @brief 获取植物类型枚举
     * @return 植物类型，如果类型无效则返回 PlantType::Peashooter
     */
    PlantType GetPlantType() const {
        if (type >= 0 && type < static_cast<int>(PlantType::Count)) {
            return static_cast<PlantType>(type);
        }
        return PlantType::Peashooter;
    }
};

/**
 * @brief 僵尸数据结构
 */
struct ZombieData {
    float x;                ///< X坐标（像素）
    float y;                ///< Y坐标（像素）
    int32_t row;            ///< 行号
    int32_t type;           ///< 僵尸类型
    int32_t hp;             ///< 当前生命值
    int32_t maxHp;          ///< 最大生命值
    int32_t accessoryHp;    ///< 配件生命值（如铁桶）
    int32_t accessoryMaxHp; ///< 配件最大生命值
    int32_t state;          ///< 状态
    float speed;            ///< 移动速度
    bool isVisible;         ///< 是否可见
    bool isHypnotized;      ///< 是否被魅惑
    bool isSlowed;          ///< 是否被减速
    bool isFrozen;          ///< 是否被冰冻
    bool isButter;          ///< 是否被黄油定身
    
    /**
     * @brief 检查僵尸是否存活
     * @return 存活返回 true
     */
    bool IsAlive() const {
        return hp > 0 && isVisible;
    }
    
    /**
     * @brief 获取僵尸类型枚举
     * @return 僵尸类型，如果类型无效则返回 ZombieType::Normal
     */
    ZombieType GetZombieType() const {
        if (type >= 0 && type < static_cast<int>(ZombieType::Count)) {
            return static_cast<ZombieType>(type);
        }
        return ZombieType::Normal;
    }
    
    /**
     * @brief 获取总生命值
     * @return 总生命值
     */
    int32_t GetTotalHp() const {
        return hp + accessoryHp;
    }
};

/**
 * @brief 投掷物数据结构
 */
struct ProjectileData {
    float x;                ///< X坐标
    float y;                ///< Y坐标
    int32_t row;            ///< 行号
    int32_t type;           ///< 投掷物类型
    int32_t damage;         ///< 伤害值
    bool isVisible;         ///< 是否可见
    
    /**
     * @brief 检查投掷物是否有效
     * @return 有效返回 true
     */
    bool IsValid() const {
        return isVisible;
    }
};

/**
 * @brief 阳光数据结构
 */
struct SunData {
    float x;                ///< X坐标
    float y;                ///< Y坐标
    int32_t value;          ///< 阳光值
    int32_t type;           ///< 阳光类型
    bool isVisible;         ///< 是否可见
    
    /**
     * @brief 检查阳光是否有效
     * @return 有效返回 true
     */
    bool IsValid() const {
        return isVisible && value > 0;
    }
};

/**
 * @brief 格子数据结构
 */
struct GridData {
    int32_t row;            ///< 行号
    int32_t col;            ///< 列号
    int32_t content;        ///< 格子内容（冰道、弹坑等）
    int32_t cooldown;       ///< 冷却时间
    
    /**
     * @brief 检查格子是否可种植
     * @return 可种植返回 true
     */
    bool CanPlant() const {
        return content == 0;
    }
};

/**
 * @brief 卡片数据结构
 */
struct CardData {
    int32_t type;           ///< 植物类型
    int32_t cost;           ///< 阳光消耗
    int32_t cooldown;       ///< 当前冷却时间
    int32_t maxCooldown;    ///< 最大冷却时间
    bool isImitater;        ///< 是否为模仿者卡片
    
    /**
     * @brief 检查卡片是否可用
     * @param sunCount 当前阳光数量
     * @return 可用返回 true
     */
    bool IsUsable(int sunCount) const {
        return cooldown == 0 && cost <= sunCount;
    }
};

} // namespace PvzLast

#endif // GAME_DATA_H
