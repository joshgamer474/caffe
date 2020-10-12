from conans import ConanFile, CMake, tools
import os

class caffe(ConanFile):
    name = "caffe"
    version = "1.0.0"
    license = ""
    url = "https://github.com/BVLC/caffe"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "cpu_only": [True, False],
               "cuda_arch_name": ["Fermi", "Kepler", "Maxwell", "All", "Auto"]}
    default_options = {"shared": True,
                       "cpu_only": False,
                       "cuda_arch_name": "Auto"}
    generators = "cmake"
    exports = "CMakeLists.txt"
    exports_sources = "src/*", "include/*", "cmake/*", "data/*", "docker/*", "docs/*", "examples/*", "models/*", "python/*", "matlab/*", "tools/*"
    requires = (
        "boost/1.68.0@conan/stable",
        "cmake_findboost_modular/1.69.0@bincrafters/stable",
        "eigen/3.3.7@conan/stable",
        "gflags/2.2.2@bincrafters/stable",
        "glog/0.4.0@bincrafters/stable",
        "gtest/1.8.1@bincrafters/stable",
        "hdf5/1.10.5-dm2@ess-dmsc/stable",
        "lapack/3.7.1@conan/stable",
        "openblas/0.3.5@conan/stable",
        "opencv/3.4.5@conan/stable",
        "protobuf/3.5.1@bincrafters/stable",
        "protoc_installer/3.5.1@bincrafters/stable",
    )

    def imports(self):
        dest = os.getenv("CONAN_IMPORT_PATH", "bin")
        self.copy("*.dll", dst=dest, root_package="opencv", keep_path=False)
        self.copy("*.dll", src="bin", dst=dest)
        self.copy("*.pdb", src="bin", dst=dest)
        self.keep_imports = True

    def configure(self):
        self.source()

        #self.options["boost"].shared = self.options.shared
        self.options["boost"].shared = True
        #self.options["boost"].header_only = True
        self.options["boost"].skip_lib_rename = True

        self.options["protobuf"].shared = self.options.shared
        self.options["protobuf"].lite = False # We need the full protobuf build support

        #self.options["gflags"].shared = False
        self.options["gflags"].nothreads = False

        self.options["gflags"].nothreads = False
        self.options["gflags"].shared = True
        self.options["glog"].shared = True
        self.options["glog"].with_gflags = True
        self.options["glog"].with_threads = False
        self.options["gtest"].shared = True

        self.options["lapack"].visual_studio = True
        self.options["lapack"].shared = True    # Only shared build is supported for VS

        #self.options["opencv"].cuda = True
        #self.options["opencv"].contrib = True
        #self.options["opencv"].gflags = True
        #self.options["opencv"].glog = True
        #self.options["opencv"].harfbuzz = False
        #self.options["opencv"].protobuf = True
        #self.options["opencv"].lapack = True
        self.options["opencv"].shared = self.options.shared

        self.options["hdf5"].cxx = True
        self.options["hdf5"].parallel = False
        self.options["hdf5"].shared = self.options.shared

        self.options["zlib"].shared = self.options.shared

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_CONANFILE"] = True

        cmake.definitions["BLAS"] = "open"
        
        cmake.definitions["CPU_ONLY"] = self.options.cpu_only
        cmake.definitions["USE_LMDB"] = False
        cmake.definitions["USE_LEVELDB"] = False
        cmake.definitions["BUILD_python"] = False
        cmake.definitions["CUDA_ARCH_NAME"] = self.options.cuda_arch_name
        #cmake.definitions["CUDA_ARCH_BIN"] = "6.1" # https://en.wikipedia.org/wiki/CUDA
        cmake.definitions["CUDA_ARCH_PTX"] = ""

        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("caffe*", dst="bin", src="bin")
        self.copy("caffe*", dst="include", src="include")
        self.copy("*.hpp", dst="include/caffe", src="caffe")
        self.copy("*.lib", dst="lib", src="lib")

    def package_info(self):
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["caffe-d", "proto-d"]
        else:
           self.cpp_info.libs = ["caffe", "proto"]