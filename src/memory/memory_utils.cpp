/**
 * @file memory_utils.cpp
 * @brief 内存操作工具类实现
 */

#include "memory_utils.h"
#include "game_data.h"

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#endif

namespace PvzLast {
namespace Memory {

MemoryManager& MemoryManager::GetInstance() {
    static MemoryManager instance;
    return instance;
}

MemoryManager::MemoryManager()
    : m_processHandle(nullptr)
    , m_baseAddress(0)
    , m_isAttached(false) {
}

MemoryManager::~MemoryManager() {
    Shutdown();
}

bool MemoryManager::Initialize() {
    // 初始化内存管理器
    return true;
}

void MemoryManager::Shutdown() {
    DetachFromGame();
}

bool MemoryManager::IsAttached() const {
    return m_isAttached;
}

bool MemoryManager::AttachToGame() {
#ifdef _WIN32
    // 查找游戏窗口
    HWND hwnd = FindWindowW(L"MainWindow", L"Plants vs. Zombies");
    if (hwnd == nullptr) {
        hwnd = FindWindowW(nullptr, L"植物大战僵尸");
    }
    
    if (hwnd == nullptr) {
        return false;
    }
    
    // 获取进程ID
    DWORD processId = 0;
    GetWindowThreadProcessId(hwnd, &processId);
    
    if (processId == 0) {
        return false;
    }
    
    // 打开进程
    m_processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
    
    if (m_processHandle == nullptr) {
        return false;
    }
    
    // 获取模块基地址
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, processId);
    
    if (snapshot != INVALID_HANDLE_VALUE) {
        MODULEENTRY32W moduleEntry;
        moduleEntry.dwSize = sizeof(moduleEntry);
        
        if (Module32FirstW(snapshot, &moduleEntry)) {
            m_baseAddress = reinterpret_cast<uintptr_t>(moduleEntry.modBaseAddr);
        }
        
        CloseHandle(snapshot);
    }
    
    m_isAttached = (m_baseAddress != 0);
    return m_isAttached;
#else
    // 非 Windows 平台暂不支持
    return false;
#endif
}

void MemoryManager::DetachFromGame() {
#ifdef _WIN32
    if (m_processHandle != nullptr) {
        CloseHandle(m_processHandle);
        m_processHandle = nullptr;
    }
#endif
    
    m_baseAddress = 0;
    m_isAttached = false;
}

template<typename T>
T MemoryManager::Read(uintptr_t address) const {
    T value{};
    
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesRead = 0;
        ReadProcessMemory(m_processHandle, reinterpret_cast<LPCVOID>(address), &value, sizeof(T), &bytesRead);
    }
#endif
    
    return value;
}

template<typename T>
bool MemoryManager::Write(uintptr_t address, T value) {
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesWritten = 0;
        return WriteProcessMemory(m_processHandle, reinterpret_cast<LPVOID>(address), &value, sizeof(T), &bytesWritten) != 0;
    }
#endif
    
    return false;
}

uintptr_t MemoryManager::ReadPointer(uintptr_t baseAddress, const std::vector<uintptr_t>& offsets) const {
    uintptr_t address = Read<uintptr_t>(baseAddress);
    
    for (size_t i = 0; i < offsets.size() - 1; ++i) {
        address = Read<uintptr_t>(address + offsets[i]);
        if (address == 0) {
            return 0;
        }
    }
    
    if (!offsets.empty()) {
        address += offsets.back();
    }
    
    return address;
}

std::string MemoryManager::ReadString(uintptr_t address, size_t maxLength) const {
    std::vector<char> buffer(maxLength + 1, '\0');
    
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesRead = 0;
        ReadProcessMemory(m_processHandle, reinterpret_cast<LPCVOID>(address), buffer.data(), maxLength, &bytesRead);
    }
#endif
    
    return std::string(buffer.data());
}

bool MemoryManager::WriteString(uintptr_t address, const std::string& str) {
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesWritten = 0;
        return WriteProcessMemory(m_processHandle, reinterpret_cast<LPVOID>(address), str.c_str(), str.size() + 1, &bytesWritten) != 0;
    }
#endif
    
    return false;
}

std::vector<uint8_t> MemoryManager::ReadBytes(uintptr_t address, size_t size) const {
    std::vector<uint8_t> buffer(size, 0);
    
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesRead = 0;
        ReadProcessMemory(m_processHandle, reinterpret_cast<LPCVOID>(address), buffer.data(), size, &bytesRead);
    }
#endif
    
    return buffer;
}

bool MemoryManager::WriteBytes(uintptr_t address, const std::vector<uint8_t>& bytes) {
#ifdef _WIN32
    if (m_processHandle != nullptr && m_isAttached) {
        SIZE_T bytesWritten = 0;
        return WriteProcessMemory(m_processHandle, reinterpret_cast<LPVOID>(address), bytes.data(), bytes.size(), &bytesWritten) != 0;
    }
#endif
    
    return false;
}

uintptr_t MemoryManager::GetBaseAddress() const {
    return m_baseAddress;
}

uintptr_t MemoryManager::GetPvzAddress() const {
    return Read<uintptr_t>(m_baseAddress + Address::BASE_ADDRESS);
}

// 模板实例化
template int MemoryManager::Read<int>(uintptr_t address) const;
template uint32_t MemoryManager::Read<uint32_t>(uintptr_t address) const;
template float MemoryManager::Read<float>(uintptr_t address) const;
template uintptr_t MemoryManager::Read<uintptr_t>(uintptr_t address) const;
template bool MemoryManager::Read<bool>(uintptr_t address) const;

template bool MemoryManager::Write<int>(uintptr_t address, int value);
template bool MemoryManager::Write<uint32_t>(uintptr_t address, uint32_t value);
template bool MemoryManager::Write<float>(uintptr_t address, float value);
template bool MemoryManager::Write<uintptr_t>(uintptr_t address, uintptr_t value);
template bool MemoryManager::Write<bool>(uintptr_t address, bool value);

} // namespace Memory
} // namespace PvzLast
