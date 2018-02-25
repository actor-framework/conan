#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class CAFConan(ConanFile):
    name = "caf"
    version = "0.15.5"
    description = "An open source implementation of the Actor Model in C++"
    url = "https://github.com/actor-framework/actor-framework"
    license = "BSD-3-Clause, BSL-1.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake"]
    source_subfolder = "source_subfolder"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "log_level": ["NONE", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]
   }
    default_options = "shared=False", "log_level=NONE"

    def source(self):
        project_url = "https://github.com/actor-framework/actor-framework"
        archive_path = "/archive/"
        archive_ext = ".tar.gz"
        download_url = project_url + archive_path + self.version + archive_ext
        tools.get(download_url)
        os.rename("actor-framework-" + self.version, self.source_subfolder)
        
    def configure(self):
        if self.settings.compiler == "gcc":
            if self.settings.compiler.version < 4.8:
                raise ConanException("g++ >= 4.8 is required, yours is %s" % self.settings.compiler.version)
        if self.settings.compiler == "clang" and str(self.settings.compiler.version) < "3.4":
            raise ConanException("clang >= 3.4 is required, yours is %s" % self.settings.compiler.version)
        if self.settings.compiler == "Visual Studio" and str(self.settings.compiler.version) < "14":
            raise ConanException("Visual Studio >= 14 is required, yours is %s" % self.settings.compiler.version)

    def build(self):
        cmake = CMake(self)
        cmake.parallel = True
        cmake.definitions["CMAKE_CXX_STANDARD"] = "11"
        if self.settings.compiler=="Visual Studio" or self.settings.arch == "x86":
            cmake.definitions["CAF_NO_OPENSSL"] = "ON"
        for define in ["CAF_NO_EXAMPLES", "CAF_NO_TOOLS", "CAF_NO_UNIT_TESTS", "CAF_NO_PYTHON"]:
            cmake.definitions[define] = "ON"
        if tools.os_info.is_macos and self.settings.arch == "x86":
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = "i386"
        if self.options.shared:
            cmake.definitions["CAF_BUILD_STATIC"] = "OFF"
            cmake.definitions["CAF_BUILD_STATIC_ONLY"] = "OFF"
        else:
            cmake.definitions["CAF_BUILD_STATIC"] = "ON"
            cmake.definitions["CAF_BUILD_STATIC_ONLY"] = "ON"
        if self.options.log_level and self.options.log_level != "NONE":
            cmake.definitions["CAF_LOG_LEVEL"] = self.options.log_level

        cmake.configure(build_dir="build")
        cmake.build()

    def package(self):
        dst_include_dir = os.path.join("include", "caf")
        self.copy("LICENSE*", src=self.source_subfolder)
        self.copy("*.hpp",    dst=dst_include_dir,  src=os.path.join(self.source_subfolder, "libcaf_core", "caf"))
        self.copy("*.hpp",    dst=dst_include_dir,  src=os.path.join(self.source_subfolder, "libcaf_io", "caf"))
        self.copy("*.dylib",  dst="lib", keep_path=False)
        self.copy("*.so",     dst="lib", keep_path=False)
        self.copy("*.so.*",  dst="lib", keep_path=False)
        self.copy("*.a",      dst="lib", keep_path=False)
        self.copy("*.lib",    dst="lib", keep_path=False)
        self.copy("*.dll",    dst="bin", keep_path=False)

    def package_info(self):
        tools.collect_libs(self)
        
        if self.options.shared:
            self.cpp_info.libs.extend(["caf_io", "caf_core"])
        if not self.options.shared:
            self.cpp_info.libs.extend(["caf_io_static", "caf_core_static"])

        if self.settings.compiler=="Visual Studio":
            if not self.options.shared:
                self.cpp_info.libs.append('ws2_32')
                self.cpp_info.libs.append('iphlpapi')
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')

