/**
 * @file example_script.cpp
 * @brief 示例脚本
 * 
 * 演示如何使用 PvzLast 框架编写简单的游戏脚本。
 */

#include "pvzlast.h"
#include "script_base.h"
#include <iostream>

using namespace PvzLast;
using namespace PvzLast::Script;

/**
 * @brief 示例脚本类
 * 
 * 展示基本的脚本结构和操作
 */
class ExampleScript : public ScriptBase {
public:
    ExampleScript() {
        SetName("ExampleScript");
    }

protected:
    void OnSetup() override {
        std::cout << "脚本初始化: " << GetName() << std::endl;
        
        // 示例：在第一波开始时种植向日葵
        ActionData plantSunflower;
        plantSunflower.type = ActionType::PlantCard;
        plantSunflower.param1 = 1;  // 卡片索引
        plantSunflower.param2 = 1;  // 行号
        plantSunflower.param3 = 1;  // 列号
        AddAction(TimeStamp(1, 0), plantSunflower);
        
        // 示例：添加自定义操作
        ActionData customAction;
        customAction.type = ActionType::Custom;
        customAction.customAction = []() {
            std::cout << "执行自定义操作!" << std::endl;
        };
        AddAction(TimeStamp(1, 100), customAction);
    }
    
    void OnUpdate() override {
        // 每帧更新逻辑
        // 可以在这里添加实时检测和响应逻辑
    }
};

/**
 * @brief 演示基本 API 使用
 */
void DemoBasicAPI() {
    std::cout << "=== PvzLast 基本 API 演示 ===" << std::endl;
    std::cout << "项目名称: " << PROJECT_NAME << std::endl;
    std::cout << "版本: " << VERSION << std::endl;
    
    // 初始化框架
    if (!Initialize()) {
        std::cout << "初始化失败，请确保游戏正在运行" << std::endl;
        return;
    }
    
    std::cout << "框架初始化成功!" << std::endl;
    
    // 检查游戏状态
    if (IsGameRunning()) {
        std::cout << "游戏正在运行" << std::endl;
        
        // 获取游戏信息
        std::cout << "当前阳光: " << GetSunCount() << std::endl;
        std::cout << "当前波数: " << GetCurrentWave() << std::endl;
        std::cout << "游戏时钟: " << GetGameClock() << std::endl;
        
        // 获取场景类型
        SceneType scene = GetCurrentScene();
        const char* sceneNames[] = {
            "白天", "夜晚", "泳池", "浓雾", "屋顶", "月夜"
        };
        std::cout << "当前场景: " << sceneNames[static_cast<int>(scene)] << std::endl;
    }
    
    // 关闭框架
    Shutdown();
    std::cout << "框架已关闭" << std::endl;
}

/**
 * @brief 演示脚本使用
 */
void DemoScript() {
    std::cout << "=== PvzLast 脚本演示 ===" << std::endl;
    
    ExampleScript script;
    
    if (!script.Initialize()) {
        std::cout << "脚本初始化失败" << std::endl;
        return;
    }
    
    std::cout << "脚本已初始化: " << script.GetName() << std::endl;
    std::cout << "按 Ctrl+C 停止脚本..." << std::endl;
    
    // 运行脚本
    script.Run();
    
    std::cout << "脚本已停止" << std::endl;
}

/**
 * @brief 主函数
 */
int main() {
    std::cout << "==================================" << std::endl;
    std::cout << "  PvzLast - 植物大战僵尸优化框架  " << std::endl;
    std::cout << "==================================" << std::endl;
    std::cout << std::endl;
    
    // 演示基本 API
    DemoBasicAPI();
    
    std::cout << std::endl;
    
    // 演示脚本（取消注释以运行）
    // DemoScript();
    
    return 0;
}
