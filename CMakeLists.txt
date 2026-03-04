cmake_minimum_required(VERSION 3.8)
project(semubot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED) 

# Install Directiories
install(
  DIRECTORY launch meshes urdf config
  DESTINATION share/${PROJECT_NAME}
)

# Disable tests
set(BUILD_TESTING OFF)

ament_package()
