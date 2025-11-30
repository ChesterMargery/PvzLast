# PvzLast 项目 Copilot 指令

## 强制参考源

**所有涉及 PVZ 游戏数据的代码必须参考 AVZ (AsmVsZombies) 源码：**
- 仓库: https://github.com/vector-wlc/AsmVsZombies
- 这是 PVZ 逆向工程社区最权威的数据来源

## 关键参考文件

在编写或修改以下内容时，必须查阅对应的 AVZ 源文件：

| 本项目文件 | 必须参考的 AVZ 文件 |
|-----------|-------------------|
| `data/offsets.py` | `inc/avz_pvz_struct.h` - 所有内存偏移量 |
| `data/zombies.py` | `inc/avz_types.h` - 僵尸类型枚举 |
| `data/plants.py` | `inc/avz_types.h` - 植物类型枚举 |
| `data/constants.py` | `inc/avz_time_operation.h` - 时间常量 |
| `judge/collision.py` | `tutorial/scripts/liang_yi/judge.h` - 碰撞判定 |
| `judge/prediction.py` | `tutorial/scripts/liang_yi/judge.h` - 移动预测 |

## 数据标准

### 僵尸血量
- 普通僵尸本体血量: **270**（不是 200！包含濒死状态）
- 参考 AVZ 社区标准

### 内存偏移量
- 必须与 `avz_pvz_struct.h` 中的定义完全一致
- 不要猜测偏移量，必须从源码复制

### 时间单位
- 使用厘秒 (cs) 作为时间单位: 1cs = 10ms
- 炮弹飞行时间: 373cs
- 灰烬生效延迟: 100cs

## 禁止事项

1. ❌ 不要从网上 Wiki 或论坛帖子获取数值
2. ❌ 不要凭直觉猜测内存偏移量
3. ❌ 不要假设连续的内存布局
4. ❌ 不要使用 200 作为普通僵尸血量

## 验证要求

修改数据文件时，必须在 commit message 或 PR 描述中注明：
- 参考的 AVZ 源文件路径
- 对应的代码行号（如果适用）
