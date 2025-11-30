/**
 * @file script_base.h
 * @brief 脚本基类定义
 * 
 * 提供脚本编写的基础框架和接口定义。
 */

#ifndef SCRIPT_BASE_H
#define SCRIPT_BASE_H

#include <string>
#include <functional>
#include <vector>
#include <map>

namespace PvzLast {
namespace Script {

/**
 * @brief 时间戳类型，用于脚本调度
 */
struct TimeStamp {
    int wave;               ///< 波数
    int tick;               ///< 时钟刻
    
    TimeStamp(int w = 1, int t = 0) : wave(w), tick(t) {}
    
    bool operator<(const TimeStamp& other) const {
        if (wave != other.wave) return wave < other.wave;
        return tick < other.tick;
    }
    
    bool operator==(const TimeStamp& other) const {
        return wave == other.wave && tick == other.tick;
    }
};

/**
 * @brief 操作类型枚举
 */
enum class ActionType {
    PlantCard,              ///< 种植卡片
    RemovePlant,            ///< 铲除植物
    ClickSun,               ///< 点击阳光
    UseCard,                ///< 使用卡片
    Custom                  ///< 自定义操作
};

/**
 * @brief 操作数据结构
 */
struct ActionData {
    ActionType type;        ///< 操作类型
    int param1;             ///< 参数1
    int param2;             ///< 参数2
    int param3;             ///< 参数3
    std::function<void()> customAction;  ///< 自定义操作函数
    
    ActionData() : type(ActionType::Custom), param1(0), param2(0), param3(0) {}
};

/**
 * @brief 脚本基类
 * 
 * 提供脚本编写的基础框架
 */
class ScriptBase {
public:
    ScriptBase();
    virtual ~ScriptBase();
    
    /**
     * @brief 初始化脚本
     * @return 初始化成功返回 true
     */
    virtual bool Initialize();
    
    /**
     * @brief 运行脚本主循环
     */
    virtual void Run();
    
    /**
     * @brief 停止脚本
     */
    virtual void Stop();
    
    /**
     * @brief 检查脚本是否正在运行
     * @return 运行中返回 true
     */
    bool IsRunning() const;
    
    /**
     * @brief 获取脚本名称
     * @return 脚本名称
     */
    const std::string& GetName() const;
    
    /**
     * @brief 设置脚本名称
     * @param name 脚本名称
     */
    void SetName(const std::string& name);

protected:
    /**
     * @brief 脚本设置（子类实现）
     * 
     * 在脚本初始化时调用一次，用于注册定时操作和进行初始设置。
     * 子类必须实现此方法。
     */
    virtual void OnSetup() = 0;
    
    /**
     * @brief 每帧更新（子类实现）
     * 
     * 在脚本运行期间每帧调用，用于实现实时检测和响应逻辑。
     * 子类必须实现此方法。
     */
    virtual void OnUpdate() = 0;
    
    /**
     * @brief 添加定时操作
     * @param time 时间戳
     * @param action 操作数据
     */
    void AddAction(const TimeStamp& time, const ActionData& action);
    
    /**
     * @brief 种植卡片
     * @param cardIndex 卡片索引
     * @param row 行号
     * @param col 列号
     */
    void PlantCard(int cardIndex, int row, int col);
    
    /**
     * @brief 铲除植物
     * @param row 行号
     * @param col 列号
     */
    void RemovePlant(int row, int col);
    
    /**
     * @brief 等待到指定时间
     * @param wave 波数
     * @param tick 时钟刻
     */
    void WaitUntil(int wave, int tick);
    
    /**
     * @brief 延迟指定时钟刻
     * @param ticks 时钟刻数
     */
    void Delay(int ticks);

private:
    std::string m_name;                                     ///< 脚本名称
    bool m_isRunning;                                       ///< 是否运行中
    std::multimap<TimeStamp, ActionData> m_scheduledActions; ///< 计划的操作
};

} // namespace Script
} // namespace PvzLast

#endif // SCRIPT_BASE_H
