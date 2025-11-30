# PvzLast API 文档

## 概述

PvzLast 是一个用于植物大战僵尸游戏的 C++ 框架，提供了内存操作、游戏数据读取和脚本编写等功能。

## 核心 API

### 初始化和关闭

```cpp
#include "pvzlast.h"

// 初始化框架
bool result = PvzLast::Initialize();

// 关闭框架
PvzLast::Shutdown();
```

### 游戏状态查询

```cpp
// 检查游戏是否运行
bool running = PvzLast::IsGameRunning();

// 获取游戏状态
PvzLast::GameState state = PvzLast::GetGameState();

// 获取当前场景
PvzLast::SceneType scene = PvzLast::GetCurrentScene();

// 获取阳光数量
int sun = PvzLast::GetSunCount();

// 设置阳光数量
PvzLast::SetSunCount(9990);

// 获取当前波数
int wave = PvzLast::GetCurrentWave();

// 获取游戏时钟
int clock = PvzLast::GetGameClock();
```

## 内存操作 API

### MemoryManager 类

```cpp
#include "memory_utils.h"

// 获取单例实例
auto& mem = PvzLast::Memory::MemoryManager::GetInstance();

// 读取内存
int value = mem.Read<int>(address);

// 写入内存
mem.Write<int>(address, 100);

// 读取多级指针
uintptr_t finalAddr = mem.ReadPointer(baseAddr, {0x10, 0x20, 0x30});

// 读取字符串
std::string str = mem.ReadString(address, 256);

// 读取字节数组
std::vector<uint8_t> bytes = mem.ReadBytes(address, 16);
```

## 脚本 API

### ScriptBase 类

创建自定义脚本需要继承 `ScriptBase` 类：

```cpp
#include "script_base.h"

class MyScript : public PvzLast::Script::ScriptBase {
public:
    MyScript() {
        SetName("MyScript");
    }

protected:
    void OnSetup() override {
        // 初始化时调用
        // 在这里注册定时操作
    }
    
    void OnUpdate() override {
        // 每帧调用
        // 在这里添加实时逻辑
    }
};
```

### 定时操作

```cpp
// 添加种植操作
PvzLast::Script::ActionData action;
action.type = PvzLast::Script::ActionType::PlantCard;
action.param1 = cardIndex;
action.param2 = row;
action.param3 = col;
AddAction(TimeStamp(wave, tick), action);

// 添加自定义操作
PvzLast::Script::ActionData custom;
custom.type = PvzLast::Script::ActionType::Custom;
custom.customAction = []() {
    // 自定义逻辑
};
AddAction(TimeStamp(wave, tick), custom);
```

### 时间控制

```cpp
// 等待到指定时间
WaitUntil(wave, tick);

// 延迟指定时钟刻
Delay(100);
```

## 数据结构

### PlantData

植物数据结构，包含位置、类型、生命值等信息。

### ZombieData

僵尸数据结构，包含位置、类型、生命值、状态等信息。

### CardData

卡片数据结构，包含类型、消耗、冷却时间等信息。

## 枚举类型

### GameState

- `NotRunning`: 游戏未运行
- `MainMenu`: 主菜单
- `Playing`: 游戏中
- `Paused`: 暂停
- `GameOver`: 游戏结束

### SceneType

- `Day`: 白天
- `Night`: 夜晚
- `Pool`: 泳池
- `Fog`: 浓雾
- `Roof`: 屋顶
- `MoonNight`: 月夜

### PlantType

包含所有植物类型的枚举。

### ZombieType

包含所有僵尸类型的枚举。
