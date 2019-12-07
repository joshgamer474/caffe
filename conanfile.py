from conans import ConanFile, CMake, tools
import os

class caffe(ConanFile):
    name = "caffe"
    version = "1.0.0"
    license = ""
    url = ""
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports = "CMakeLists.txt"
    exports_sources = "src/*", "include/*", "cmake/*", "data/*", "docker/*", "docs/*", "examples/*", "models/*", "python/*", "matlab/*", "tools/*"
    requires = (
        "atlas/0.7.0@worldforge/testing",
        "boost/1.71.0@conan/stable",
        "bzip2/1.0.8@conan/stable",
        "cmake_findboost_modular/1.69.0@bincrafters/stable",
        "eigen/3.3.7@conan/stable",
        "gflags/2.2.2@bincrafters/stable",
        "glog/0.4.0@bincrafters/stable",
        "gtest/1.8.1@bincrafters/stable",
        "hdf5/1.10.5-dm2@ess-dmsc/stable",
        "lapack/3.7.1@conan/stable",
        #"lmdb/0.9.18@sunsided/stable",
        "openblas/0.3.5@conan/stable",
        "opencv/4.1.1@conan/stable",
        "protobuf/3.6.1@bincrafters/stable",
        "protoc_installer/3.6.1@bincrafters/stable",
        "zlib/1.2.11@conan/stable",
    )

    def configure(self):
        self.source()
        self.options["protobuf"].shared = True
        self.options["protobuf"].lite = True

        #self.options["gflags"].shared = False
        self.options["gflags"].nothreads = False

        self.options["gflags"].nothreads = False
        self.options["gflags"].shared = True
        self.options["glog"].shared = True
        self.options["glog"].with_gflags = True
        self.options["glog"].with_threads = False

        self.options["lapack"].visual_studio = True
        self.options["lapack"].shared = True

        self.options["opencv"].cuda = True
        self.options["opencv"].contrib = True
        self.options["opencv"].gflags = True
        self.options["opencv"].glog = True
        self.options["opencv"].harfbuzz = False
        self.options["opencv"].protobuf = True
        self.options["opencv"].lapack = False

        self.options["hdf5"].cxx = True

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_CONANFILE"] = True
        
        cmake.definitions["USE_LMDB"] = False
        cmake.definitions["USE_LEVELDB"] = False
        cmake.definitions["BUILD_python"] = False
        cmake.definitions["CUDA_ARCH_BIN"] = "6.1"
        cmake.definitions["CUDA_ARCH_PTX"] = ""

        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("caffe*", dst="include", src="include")
        self.copy("*.hpp", dst="caffe", src="caffe")
        self.copy("caffe*.lib", dst="lib", src="lib")
        