cmake_minimum_required(VERSION 3.10)
project(PvzLast VERSION 1.0.0 LANGUAGES CXX)

# C++17 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 包含目录
include_directories(${CMAKE_SOURCE_DIR}/include)

# 源文件
set(CORE_SOURCES
    src/core/pvzlast.cpp
    src/memory/memory_utils.cpp
    src/scripts/script_base.cpp
)

# 核心库
add_library(pvzlast STATIC ${CORE_SOURCES})
target_include_directories(pvzlast PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Windows 特定设置
if(WIN32)
    target_compile_definitions(pvzlast PRIVATE _WIN32_WINNT=0x0601)
endif()

# 示例程序
add_executable(example examples/example_script.cpp)
target_link_libraries(example pvzlast)

# 安装配置
install(TARGETS pvzlast DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)

# 输出配置信息
message(STATUS "PvzLast version: ${PROJECT_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
