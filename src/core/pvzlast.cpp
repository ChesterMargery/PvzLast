/**
 * @file pvzlast.cpp
 * @brief PvzLast 核心功能实现
 */

#include "pvzlast.h"
#include "memory_utils.h"
#include "game_data.h"

namespace PvzLast {

static bool g_initialized = false;

bool Initialize() {
    if (g_initialized) {
        return true;
    }
    
    if (!Memory::MemoryManager::GetInstance().Initialize()) {
        return false;
    }
    
    if (!Memory::MemoryManager::GetInstance().AttachToGame()) {
        Memory::MemoryManager::GetInstance().Shutdown();
        return false;
    }
    
    g_initialized = true;
    return true;
}

void Shutdown() {
    if (!g_initialized) {
        return;
    }
    
    Memory::MemoryManager::GetInstance().DetachFromGame();
    Memory::MemoryManager::GetInstance().Shutdown();
    g_initialized = false;
}

bool IsGameRunning() {
    return Memory::MemoryManager::GetInstance().IsAttached();
}

GameState GetGameState() {
    if (!IsGameRunning()) {
        return GameState::NotRunning;
    }
    
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return GameState::MainMenu;
    }
    
    // TODO: 根据游戏状态偏移读取实际状态
    return GameState::Playing;
}

SceneType GetCurrentScene() {
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return SceneType::Day;
    }
    
    uintptr_t boardAddr = mem.Read<uintptr_t>(pvzBase + Address::BOARD_OFFSET);
    if (boardAddr == 0) {
        return SceneType::Day;
    }
    
    int sceneId = mem.Read<int>(boardAddr + Address::SCENE_OFFSET);
    return static_cast<SceneType>(sceneId);
}

int GetSunCount() {
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return 0;
    }
    
    uintptr_t boardAddr = mem.Read<uintptr_t>(pvzBase + Address::BOARD_OFFSET);
    if (boardAddr == 0) {
        return 0;
    }
    
    return mem.Read<int>(boardAddr + Address::SUN_OFFSET);
}

void SetSunCount(int count) {
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return;
    }
    
    uintptr_t boardAddr = mem.Read<uintptr_t>(pvzBase + Address::BOARD_OFFSET);
    if (boardAddr == 0) {
        return;
    }
    
    mem.Write<int>(boardAddr + Address::SUN_OFFSET, count);
}

int GetCurrentWave() {
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return 0;
    }
    
    uintptr_t boardAddr = mem.Read<uintptr_t>(pvzBase + Address::BOARD_OFFSET);
    if (boardAddr == 0) {
        return 0;
    }
    
    return mem.Read<int>(boardAddr + Address::WAVE_OFFSET);
}

int GetGameClock() {
    auto& mem = Memory::MemoryManager::GetInstance();
    uintptr_t pvzBase = mem.GetPvzAddress();
    
    if (pvzBase == 0) {
        return 0;
    }
    
    uintptr_t boardAddr = mem.Read<uintptr_t>(pvzBase + Address::BOARD_OFFSET);
    if (boardAddr == 0) {
        return 0;
    }
    
    return mem.Read<int>(boardAddr + Address::CLOCK_OFFSET);
}

} // namespace PvzLast
