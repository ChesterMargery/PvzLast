/**
 * @file memory_utils.h
 * @brief 内存操作工具类
 * 
 * 提供安全的内存读写操作接口，用于与游戏进程进行交互。
 */

#ifndef MEMORY_UTILS_H
#define MEMORY_UTILS_H

#include <cstdint>
#include <string>
#include <vector>

namespace PvzLast {
namespace Memory {

/**
 * @brief 内存操作类
 * 
 * 封装了与游戏进程的内存交互操作
 */
class MemoryManager {
public:
    /**
     * @brief 获取单例实例
     * @return MemoryManager 实例引用
     */
    static MemoryManager& GetInstance();

    /**
     * @brief 初始化内存管理器
     * @return 初始化成功返回 true
     */
    bool Initialize();

    /**
     * @brief 关闭内存管理器
     */
    void Shutdown();

    /**
     * @brief 检查是否已附加到游戏进程
     * @return 已附加返回 true
     */
    bool IsAttached() const;

    /**
     * @brief 附加到游戏进程
     * @return 附加成功返回 true
     */
    bool AttachToGame();

    /**
     * @brief 从游戏进程分离
     */
    void DetachFromGame();

    /**
     * @brief 读取内存数据
     * @tparam T 数据类型
     * @param address 内存地址
     * @return 读取的数据
     */
    template<typename T>
    T Read(uintptr_t address) const;

    /**
     * @brief 写入内存数据
     * @tparam T 数据类型
     * @param address 内存地址
     * @param value 要写入的值
     * @return 写入成功返回 true
     */
    template<typename T>
    bool Write(uintptr_t address, T value);

    /**
     * @brief 读取多级指针
     * @param baseAddress 基地址
     * @param offsets 偏移量列表
     * @return 最终地址
     */
    uintptr_t ReadPointer(uintptr_t baseAddress, const std::vector<uintptr_t>& offsets) const;

    /**
     * @brief 读取字符串
     * @param address 内存地址
     * @param maxLength 最大长度
     * @return 读取的字符串
     */
    std::string ReadString(uintptr_t address, size_t maxLength) const;

    /**
     * @brief 写入字符串
     * @param address 内存地址
     * @param str 要写入的字符串
     * @return 写入成功返回 true
     */
    bool WriteString(uintptr_t address, const std::string& str);

    /**
     * @brief 读取字节数组
     * @param address 内存地址
     * @param size 字节数
     * @return 字节数组
     */
    std::vector<uint8_t> ReadBytes(uintptr_t address, size_t size) const;

    /**
     * @brief 写入字节数组
     * @param address 内存地址
     * @param bytes 字节数组
     * @return 写入成功返回 true
     */
    bool WriteBytes(uintptr_t address, const std::vector<uint8_t>& bytes);

    /**
     * @brief 获取游戏基地址
     * @return 基地址
     */
    uintptr_t GetBaseAddress() const;

    /**
     * @brief 获取 PvZ 主对象地址
     * @return 主对象地址
     */
    uintptr_t GetPvzAddress() const;

private:
    MemoryManager();
    ~MemoryManager();
    MemoryManager(const MemoryManager&) = delete;
    MemoryManager& operator=(const MemoryManager&) = delete;

    void* m_processHandle;      ///< 进程句柄
    uintptr_t m_baseAddress;    ///< 基地址
    bool m_isAttached;          ///< 是否已附加
};

} // namespace Memory
} // namespace PvzLast

#endif // MEMORY_UTILS_H
