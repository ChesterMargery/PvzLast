/**
 * @file script_base.cpp
 * @brief 脚本基类实现
 */

#include "script_base.h"
#include "pvzlast.h"
#include <thread>
#include <chrono>

namespace PvzLast {
namespace Script {

ScriptBase::ScriptBase()
    : m_name("Unnamed Script")
    , m_isRunning(false) {
}

ScriptBase::~ScriptBase() {
    Stop();
}

bool ScriptBase::Initialize() {
    if (!PvzLast::Initialize()) {
        return false;
    }
    
    OnSetup();
    return true;
}

void ScriptBase::Run() {
    if (m_isRunning) {
        return;
    }
    
    m_isRunning = true;
    
    while (m_isRunning && PvzLast::IsGameRunning()) {
        // 获取当前游戏时间
        int currentWave = PvzLast::GetCurrentWave();
        int currentTick = PvzLast::GetGameClock();
        TimeStamp currentTime(currentWave, currentTick);
        
        // 执行到期的操作
        auto it = m_scheduledActions.begin();
        while (it != m_scheduledActions.end() && it->first < currentTime) {
            const ActionData& action = it->second;
            
            switch (action.type) {
                case ActionType::PlantCard:
                    PlantCard(action.param1, action.param2, action.param3);
                    break;
                case ActionType::RemovePlant:
                    RemovePlant(action.param1, action.param2);
                    break;
                case ActionType::Custom:
                    if (action.customAction) {
                        action.customAction();
                    }
                    break;
                default:
                    break;
            }
            
            it = m_scheduledActions.erase(it);
        }
        
        // 调用更新函数
        OnUpdate();
        
        // 休眠一小段时间，避免占用过多 CPU
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    m_isRunning = false;
}

void ScriptBase::Stop() {
    m_isRunning = false;
}

bool ScriptBase::IsRunning() const {
    return m_isRunning;
}

const std::string& ScriptBase::GetName() const {
    return m_name;
}

void ScriptBase::SetName(const std::string& name) {
    m_name = name;
}

void ScriptBase::AddAction(const TimeStamp& time, const ActionData& action) {
    m_scheduledActions.insert(std::make_pair(time, action));
}

void ScriptBase::PlantCard(int cardIndex, int row, int col) {
    // TODO: 实现卡片种植逻辑
    // 1. 检查阳光是否足够
    // 2. 检查卡片冷却
    // 3. 模拟点击卡片
    // 4. 模拟点击目标格子
}

void ScriptBase::RemovePlant(int row, int col) {
    // TODO: 实现铲子逻辑
    // 1. 模拟点击铲子
    // 2. 模拟点击目标植物
}

void ScriptBase::WaitUntil(int wave, int tick) {
    TimeStamp target(wave, tick);
    
    while (m_isRunning && PvzLast::IsGameRunning()) {
        int currentWave = PvzLast::GetCurrentWave();
        int currentTick = PvzLast::GetGameClock();
        TimeStamp current(currentWave, currentTick);
        
        if (!(current < target)) {
            break;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

void ScriptBase::Delay(int ticks) {
    int currentWave = GetCurrentWave();
    int currentTick = GetGameClock();
    WaitUntil(currentWave, currentTick + ticks);
}

} // namespace Script
} // namespace PvzLast
