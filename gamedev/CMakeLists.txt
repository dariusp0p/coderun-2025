cmake_minimum_required(VERSION 3.30)
project(gamedev)

set(CMAKE_CXX_STANDARD 14)

find_package(SDL3 REQUIRED)
include_directories(${SDL3_INCLUDE_DIRS})

add_executable(
        gamedev
        game/main.cpp
        game/circle.h
        game/circle.cpp
)

target_include_directories(gamedev PRIVATE include)
target_link_libraries(gamedev ${SDL3_LIBRARIES})
