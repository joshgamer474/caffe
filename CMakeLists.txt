cmake_minimum_required(VERSION 2.8.7)
if(POLICY CMP0046)
  cmake_policy(SET CMP0046 NEW)
endif()
if(POLICY CMP0054)
  cmake_policy(SET CMP0054 NEW)
endif()

# ---[ Caffe project
project(Caffe C CXX)

# ---[ Caffe version
set(CAFFE_TARGET_VERSION "1.0.0-rc3" CACHE STRING "Caffe logical version")
set(CAFFE_TARGET_SOVERSION "1.0.0-rc3" CACHE STRING "Caffe soname version")
add_definitions(-DCAFFE_VERSION=${CAFFE_TARGET_VERSION})

if(USE_CONANFILE)
  include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
  conan_basic_setup()

  set(CMAKE_PREFIX_PATH
    ${CMAKE_PREFIX_PATH}
    ${CONAN_PROTOBUF_ROOT}/cmake
    ${CONAN_OPENCV_ROOT})

  message("************************************")
  message("CMAKE_BUILD_TYPE: ${CMAKE_BUILD_TYPE}")
  message("************************************")

  # Force use HDF5
  add_compile_definitions(USE_HDF5)

  add_compile_definitions(NO_STRICT)
  add_compile_definitions(WIN32_LEAN_AND_MEAN)
  add_compile_definitions(NOMINMAX)
  add_compile_definitions(GLOG_NO_ABBREVIATED_SEVERITIES)

  set(GFLAGS_LIBRARY ${CONAN_LIBS_GFLAGS})
  set(GLOG_LIBRARY ${CONAN_LIBS_GLOG})
  set(glog_DIR ${CONAN_LIB_DIRS_GLOG})
  find_package(Glog REQUIRED)
  find_package(GFlags REQUIRED)

  # This is needed to force the correct OpenCV to be found
  set(OpenCV_DIR ${CONAN_OPENCV_ROOT}/cmake/x64/vc16/staticlib)
  set(OpenCV_LIB_PATH ${CONAN_LIB_DIRS_OPENCV})
  find_package(OpenCV REQUIRED)

  #set(Atlas_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_ATLAS})
  #set(Atlas_LIBRARIES ${CONAN_LIBS_ATLAS})
  #set(Atlas_CLAPACK_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_ATLAS})
  #set(Atlas_CBLAS_LIBRARY ${CONAN_LIBS_ATLAS})
  #set(Atlas_BLAS_LIBRARY ${CONAN_LIBS_ATLAS})
  #set(Atlas_LAPACK_LIBRARY ${CONAN_LIBS_ATLAS})
  #find_package(Atlas REQUIRED)

  include(cmake/Utils.cmake)

  set(PROTOBUF_LIBRARIES ${CONAN_LIBS_PROTOBUF})
  set(Protobuf_LIBRARIES ${CONAN_LIBS_PROTOBUF})
  set(Protobuf_INCLUDE_DIRS ${CONAN_LIB_DIRS_PROTOBUF})
  find_package(Protobuf REQUIRED PROTOBUF_LIBRARIES Protobuf_LIBRARIES Protobuf_PROTOC_EXECUTABLE Protobuf_INCLUDE_DIRS)
  include(cmake/ProtoBuf.cmake)

  find_package(Eigen3 REQUIRED)

  link_libraries(${CONAN_LIBS})

else()
  # ---[ Prebuild dependencies on windows
  include(cmake/WindowsDownloadPrebuiltDependencies.cmake)
endif()

# ---[ Using cmake scripts and modules
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/Modules)

include(ExternalProject)

include(cmake/Utils.cmake)
include(cmake/Targets.cmake)
include(cmake/Misc.cmake)
include(cmake/Summary.cmake)
include(cmake/ConfigGen.cmake)

# ---[ Options
caffe_option(CPU_ONLY  "Build Caffe without CUDA support" OFF) # TODO: rename to USE_CUDA
caffe_option(USE_CUDNN "Build Caffe with cuDNN library support" ON IF NOT CPU_ONLY)
caffe_option(BUILD_SHARED_LIBS "Build shared libraries" ON)
caffe_option(BUILD_python "Build Python wrapper" ON)
set(python_version "2" CACHE STRING "Specify which Python version to use")
caffe_option(BUILD_matlab "Build Matlab wrapper" OFF IF UNIX OR APPLE)
caffe_option(BUILD_docs   "Build documentation" ON IF UNIX OR APPLE)
caffe_option(BUILD_python_layer "Build the Caffe Python layer" ON)
caffe_option(USE_OPENCV "Build with OpenCV support" ON)
caffe_option(USE_LEVELDB "Build with levelDB" ON)
caffe_option(USE_LMDB "Build with lmdb" ON)
caffe_option(ALLOW_LMDB_NOLOCK "Allow MDB_NOLOCK when reading LMDB files (only if necessary)" OFF)
caffe_option(BUILD_WITH_STATIC_CRT "Use CRT Static Runtime Library on Visual Studio" OFF)

# ---[ Dependencies
include(cmake/Dependencies.cmake)

# ---[ Flags
if(UNIX OR APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -Wall")
endif()

caffe_set_caffe_link()

if(USE_libstdcpp)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libstdc++")
  message("-- Warning: forcing libstdc++ (controlled by USE_libstdcpp option in cmake)")
endif()

if(NOT MSVC) # rely on gtest header to determine what to do
add_definitions(-DGTEST_USE_OWN_TR1_TUPLE)
endif(NOT MSVC)

#if(MSVC AND BUILD_WITH_STATIC_CRT)
#  foreach(flag_var
#      CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
#      CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO
#      CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
#      CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
#    if(${flag_var} MATCHES "/MD")
#      string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
#    endif(${flag_var} MATCHES "/MD")
#    if(${flag_var} MATCHES "/MDd")
#      string(REGEX REPLACE "/MDd" "/MTd" ${flag_var} "${${flag_var}}")
#    endif(${flag_var} MATCHES "/MDd")
#  endforeach(flag_var)
#endif()

# ---[ Warnings
caffe_warnings_disable(CMAKE_CXX_FLAGS -Wno-sign-compare -Wno-uninitialized)
caffe_warnings_disable(CMAKE_CXX_FLAGS /wd4819)

# ---[ Config generation
configure_file(cmake/Templates/caffe_config.h.in "${PROJECT_BINARY_DIR}/caffe_config.h")

# ---[ Includes
set(Caffe_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/include)
include_directories(BEFORE ${Caffe_INCLUDE_DIR} ${PROJECT_BINARY_DIR})
include_directories(BEFORE src) # This is needed for gtest.

# ---[ Subdirectories
#add_subdirectory(src/gtest)
add_subdirectory(src/caffe)
#add_subdirectory(tools)
#add_subdirectory(examples)
#add_subdirectory(python)
#add_subdirectory(matlab)
#add_subdirectory(docs)

# ---[ Linter target
if(MSVC)
  find_package(PythonInterp 2)
  set(PYTHON2_EXECUTABLE ${PYTHON_EXECUTABLE} CACHE FILEPATH "Path to the python 2.x executable")
endif()
add_custom_target(lint COMMAND ${CMAKE_COMMAND} -DMSVC=${MSVC} -DPYTHON2_EXECUTABLE=${PYTHON2_EXECUTABLE} -P ${PROJECT_SOURCE_DIR}/cmake/lint.cmake)

# ---[ pytest target
if(BUILD_python)
  add_custom_target(pytest COMMAND python${python_version} -m unittest discover -s caffe/test WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/python )
  add_dependencies(pytest pycaffe)
endif()

# ---[ Configuration summary
caffe_print_configuration_summary()

# ---[ Export configs generation
caffe_generate_export_configs()
