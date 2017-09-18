try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import sys
from conans import ConanFile
from conans.errors import ConanException

# TODO - change Travis and Appveyor config to conan-center


class CAFConan(ConanFile):
    version = '0.15.3'

    name = "caf"
    description = "An open source implementation of the Actor Model in C++"
    url = "http://actor-framework.org"
    license = "BSD-3-Clause"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "static": [True, False],
               "log_level": ["NONE", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]}
    default_options = "shared=False", "static=True", "log_level=NONE"
    source_dir = "actor-framework"

    def configure(self):
        if self.settings.compiler == "gcc":
            if self.settings.compiler.version < "4.8":
                raise ConanException("g++ >= 4.8 is required")
            elif self.settings.compiler.libcxx != 'libstdc++11':
                raise ConanException("You must use the setting compiler.libcxx=libstdc++11")
        if self.settings.compiler == "clang" and self.settings.compiler.version < "3.4":
            raise ConanException("g++ >= 3.4 is required")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version < "14":
            raise ConanException("Visual Studio >= 14 is required")
        if not (self.options.shared or self.options.static):
            raise ConanException("You must use at least one of shared=True or static=True")

    def source(self):
        self.run_command("git clone https://github.com/actor-framework/actor-framework.git")
        self.run_command("git checkout -b %s.x %s" % (self.version, self.version), self.source_dir)

    def build(self):
        lib_type = ""
        build_dir = "%s/build" % self.source_dir
        os.mkdir(build_dir)
        if self.options.static:
            lib_type = "-DCAF_BUILD_STATIC=ON" if self.options.shared else "-DCAF_BUILD_STATIC_ONLY=ON"
        logging = "-DCAF_LOG_LEVEL=%s" % self.options.log_level if self.options.log_level != "NONE" else ""
        skip_rpath = '-DCMAKE_SKIP_RPATH=ON' if sys.platform == 'darwin' else ''
        standard_options = \
            "-DCAF_NO_EXAMPLES=ON -DCAF_NO_OPENCL=ON -DCAF_NO_TOOLS=ON -DCAF_NO_UNIT_TESTS=ON -DCAF_NO_PYTHON=ON"
        configure = 'cmake .. %s %s %s %s' % (standard_options, skip_rpath, lib_type, logging)
        self.run_command(configure, build_dir)
        self.run_command('make', build_dir)

    def run_command(self, cmd, cwd=None):
        self.output.info(cmd)
        self.run(cmd, True, cwd)

    def package(self):
        self.copy("*.hpp",    dst="include/caf", src="%s/libcaf_core/caf" % self.source_dir)
        self.copy("*.hpp",    dst="include/caf", src="%s/libcaf_io/caf" % self.source_dir)
        self.copy("*.dylib",  dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.so",     dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.a",      dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("license*", dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        if self.options.shared:
            self.cpp_info.libs.extend(["caf_core", "caf_io"])
        if self.options.static:
            self.cpp_info.libs.extend(["caf_core_static", "caf_io_static"])
