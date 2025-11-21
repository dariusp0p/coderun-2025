cmake_minimum_required(VERSION 3.30)
project(gamedev)

set(CMAKE_CXX_STANDARD 14)

find_package(SDL3 REQUIRED)
include_directories(${SDL3_INCLUDE_DIRS})

add_executable(
        gamedev
        test_project/main.cpp
)

target_include_directories(gamedev PRIVATE include)
target_link_libraries(gamedev ${SDL3_LIBRARIES})
