################################################################################
# Toolchain Location - Modify this path to point to the directory of the
# toolchain on your system
set(TOOLCHAIN_ROOT $ENV{HOME}/toolchain/microblazeel-buildroot-linux-gnu_sdk-buildroot)

################################################################################
# System Architecture 
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR microblaze)

################################################################################
# Cross Compiler Options
set(CMAKE_C_COMPILER ${TOOLCHAIN_ROOT}/bin/microblazeel-linux-gcc)
set(CMAKE_SYSROOT ${TOOLCHAIN_ROOT}/microblazeel-buildroot-linux-gnu/sysroot)

################################################################################
# Set CMake to search for libraries and includes in the toolchain path, but
# search for binaries in the host path.
set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_ROOT})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

################################################################################
# These variable settings are specific to cFE/OSAL and determines which 
# abstraction layers are built when using this toolchain
SET(CFE_SYSTEM_PSPNAME      "pc-linux")
SET(OSAL_SYSTEM_OSTYPE      "posix")
