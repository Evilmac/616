# CMakeLists.txt

cmake_minimum_required(VERSION 3.10)

# Set the project name
project(ia_offline_asistente)

# Include directories
include_directories(include)

# Add source files
set(SOURCES
    src/main.cpp
    # Add more source files here
)

# Create executable
add_executable(ia_offline_asistente ${SOURCES})
