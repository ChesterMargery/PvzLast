/**
 * @file pvzlast.h
 * @brief PvzLast 主头文件
 * 
 * 本文件包含 PvzLast 项目的主要接口定义和核心功能声明。
 * 基于 AVZ 框架设计理念实现的 PvZ 游戏优化框架。
 */

#ifndef PVZLAST_H
#define PVZLAST_H

#include <cstdint>
#include <string>
#include <vector>
#include <functional>
#include <memory>

namespace PvzLast {

/**
 * @brief PvzLast 版本信息
 */
constexpr const char* VERSION = "1.0.0";
constexpr const char* PROJECT_NAME = "PvzLast";

/**
 * @brief 游戏状态枚举
 */
enum class GameState {
    NotRunning,    ///< 游戏未运行
    MainMenu,      ///< 主菜单
    Playing,       ///< 游戏中
    Paused,        ///< 暂停
    GameOver       ///< 游戏结束
};

/**
 * @brief 植物类型枚举
 */
enum class PlantType {
    Peashooter = 0,        ///< 豌豆射手
    Sunflower = 1,         ///< 向日葵
    CherryBomb = 2,        ///< 樱桃炸弹
    WallNut = 3,           ///< 坚果墙
    PotatoMine = 4,        ///< 土豆雷
    SnowPea = 5,           ///< 寒冰射手
    Chomper = 6,           ///< 大嘴花
    Repeater = 7,          ///< 双发射手
    PuffShroom = 8,        ///< 小喷菇
    SunShroom = 9,         ///< 阳光菇
    FumeShroom = 10,       ///< 大喷菇
    GraveBuster = 11,      ///< 墓碑吞噬者
    HypnoShroom = 12,      ///< 魅惑菇
    ScaredyShroom = 13,    ///< 胆小菇
    IceShroom = 14,        ///< 寒冰菇
    DoomShroom = 15,       ///< 毁灭菇
    // ... 更多植物类型
    Count
};

/**
 * @brief 僵尸类型枚举
 */
enum class ZombieType {
    Normal = 0,            ///< 普通僵尸
    Flag = 1,              ///< 旗帜僵尸
    Conehead = 2,          ///< 路障僵尸
    PoleVaulting = 3,      ///< 撑杆跳僵尸
    Buckethead = 4,        ///< 铁桶僵尸
    Newspaper = 5,         ///< 读报僵尸
    ScreenDoor = 6,        ///< 铁栅门僵尸
    Football = 7,          ///< 橄榄球僵尸
    Dancing = 8,           ///< 舞王僵尸
    BackupDancer = 9,      ///< 伴舞僵尸
    DuckyTube = 10,        ///< 鸭子救生圈僵尸
    Snorkel = 11,          ///< 潜水僵尸
    Zomboni = 12,          ///< 雪橇僵尸
    BobsledTeam = 13,      ///< 雪橇队僵尸
    Dolphin = 14,          ///< 海豚骑士僵尸
    JackInTheBox = 15,     ///< 玩偶匣僵尸
    Balloon = 16,          ///< 气球僵尸
    Digger = 17,           ///< 矿工僵尸
    Pogo = 18,             ///< 跳跳僵尸
    Yeti = 19,             ///< 雪人僵尸
    Bungee = 20,           ///< 蹦极僵尸
    Ladder = 21,           ///< 扶梯僵尸
    Catapult = 22,         ///< 投石车僵尸
    Gargantuar = 23,       ///< 巨人僵尸
    Imp = 24,              ///< 小鬼僵尸
    DrZomBoss = 25,        ///< 僵尸博士
    // ... 更多僵尸类型
    Count
};

/**
 * @brief 游戏场景类型枚举
 */
enum class SceneType {
    Day = 0,               ///< 白天
    Night = 1,             ///< 夜晚
    Pool = 2,              ///< 泳池
    Fog = 3,               ///< 浓雾
    Roof = 4,              ///< 屋顶
    MoonNight = 5          ///< 月夜
};

/**
 * @brief 初始化 PvzLast 框架
 * @return 初始化成功返回 true，否则返回 false
 */
bool Initialize();

/**
 * @brief 关闭 PvzLast 框架
 */
void Shutdown();

/**
 * @brief 检查游戏是否正在运行
 * @return 游戏运行中返回 true，否则返回 false
 */
bool IsGameRunning();

/**
 * @brief 获取当前游戏状态
 * @return 当前游戏状态
 */
GameState GetGameState();

/**
 * @brief 获取当前场景类型
 * @return 当前场景类型
 */
SceneType GetCurrentScene();

/**
 * @brief 获取当前阳光数量
 * @return 阳光数量
 */
int GetSunCount();

/**
 * @brief 设置阳光数量
 * @param count 阳光数量
 */
void SetSunCount(int count);

/**
 * @brief 获取当前波数
 * @return 当前波数
 */
int GetCurrentWave();

/**
 * @brief 获取游戏时钟
 * @return 游戏时钟计数
 */
int GetGameClock();

} // namespace PvzLast

#endif // PVZLAST_H
