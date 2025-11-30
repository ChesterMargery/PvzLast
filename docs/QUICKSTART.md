# 快速入门指南

## 环境准备

### 系统要求

- Windows 7 或更高版本
- Visual Studio 2019 或更高版本（或支持 CMake 的其他 IDE）
- CMake 3.10 或更高版本
- 植物大战僵尸游戏本体

### 获取代码

```bash
git clone https://github.com/ChesterMargery/PvzLast.git
cd PvzLast
```

## 编译项目

### 使用 CMake

```bash
# 创建构建目录
mkdir build
cd build

# 生成项目文件
cmake ..

# 编译
cmake --build . --config Release
```

### 使用 Visual Studio

1. 打开 Visual Studio
2. 选择"打开本地文件夹"
3. 选择 PvzLast 项目目录
4. Visual Studio 会自动检测 CMakeLists.txt
5. 选择构建配置（Debug/Release）
6. 按 F7 或选择"生成" -> "全部生成"

## 第一个脚本

### 创建脚本文件

在 `examples` 目录下创建新文件 `my_script.cpp`：

```cpp
#include "pvzlast.h"
#include "script_base.h"
#include <iostream>

using namespace PvzLast;
using namespace PvzLast::Script;

class MyFirstScript : public ScriptBase {
public:
    MyFirstScript() {
        SetName("MyFirstScript");
    }

protected:
    void OnSetup() override {
        std::cout << "脚本已启动！" << std::endl;
        
        // 在第一波时种植向日葵
        ActionData plant;
        plant.type = ActionType::PlantCard;
        plant.param1 = 1;  // 向日葵卡片
        plant.param2 = 1;  // 第一行
        plant.param3 = 1;  // 第一列
        AddAction(TimeStamp(1, 0), plant);
    }
    
    void OnUpdate() override {
        // 打印当前阳光（每帧）
        static int lastSun = -1;
        int currentSun = GetSunCount();
        if (currentSun != lastSun) {
            std::cout << "阳光: " << currentSun << std::endl;
            lastSun = currentSun;
        }
    }
};

int main() {
    MyFirstScript script;
    
    if (!script.Initialize()) {
        std::cout << "初始化失败，请确保游戏正在运行" << std::endl;
        return 1;
    }
    
    std::cout << "脚本运行中，按 Ctrl+C 停止..." << std::endl;
    script.Run();
    
    return 0;
}
```

### 编译和运行

1. 在 CMakeLists.txt 中添加新的可执行文件：

```cmake
add_executable(my_script examples/my_script.cpp)
target_link_libraries(my_script pvzlast)
```

2. 重新编译项目
3. 启动植物大战僵尸游戏
4. 运行编译生成的可执行文件

## 常用操作

### 读取游戏数据

```cpp
// 获取当前阳光
int sun = GetSunCount();

// 获取当前波数
int wave = GetCurrentWave();

// 获取游戏时钟
int clock = GetGameClock();
```

### 修改游戏数据

```cpp
// 设置阳光为 9990
SetSunCount(9990);
```

### 定时操作

```cpp
// 在第 5 波第 100 刻种植玉米炮
ActionData action;
action.type = ActionType::PlantCard;
action.param1 = 10;  // 玉米炮卡片索引
action.param2 = 3;   // 第三行
action.param3 = 1;   // 第一列
AddAction(TimeStamp(5, 100), action);
```

## 下一步

- 阅读 [API 文档](API.md) 了解更多功能
- 查看 `examples` 目录中的示例代码
- 加入社区讨论，分享你的脚本
