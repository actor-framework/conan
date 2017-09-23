try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import subprocess
import sys
from conans import ConanFile, CMake
from conans.errors import ConanException


# TODO - CAF uses the default ABI. build.py is hardcoded to libstdc++11 for gcc, also _gcc_libcxx() workaround below.
# TODO - Add standard library and architecture to CAF configure/CMakeLists.txt
# TODO - update docs
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
            if self.settings.compiler.version < 4.8:
                raise ConanException("g++ >= 4.8 is required, yours is %s" % self.settings.compiler.version)
            else:
                # TODO - this is temporary until CAF adds support for configuring stdlib
                self.settings.compiler.libcxx = self._gcc_libcxx()
        if self.settings.compiler == "clang" and str(self.settings.compiler.version) < "3.4":
            raise ConanException("clang >= 3.4 is required, yours is %s" % self.settings.compiler.version)
        if self.settings.compiler == "Visual Studio" and str(self.settings.compiler.version) < "14":
            raise ConanException("Visual Studio >= 14 is required, yours is %s" % self.settings.compiler.version)
        if not (self.options.shared or self.options.static):
            raise ConanException("You must use at least one of shared=True or static=True")

    def _gcc_libcxx(self):
        if self.settings.compiler.version < 5:
            libcxx = 'libstdc++'
        else:
            process = subprocess.Popen(['g++', '--version', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            libcxx = 'libstdc++11' if 'with-default-libstdcxx-abi=new' in err else 'libstdc++'
        return libcxx

    def source(self):
        # FIXME - revert back to CAF repo, this is for testing Clang 4.0/Apple Clang 9.0
        self._run_command("git clone https://github.com/sourcedelica/actor-framework.git")
        self._run_command("git checkout 0.15.3.1", self.source_dir)

        # self._run_command("git clone https://github.com/actor-framework/actor-framework.git")
        # self._run_command("git checkout %s" % self.version, self.source_dir)

    def build(self):
        lib_type = ""
        build_dir = "%s/build" % self.source_dir
        os.mkdir(build_dir)
        if self.options.static:
            lib_type = "-DCAF_BUILD_STATIC=ON" if self.options.shared else "-DCAF_BUILD_STATIC_ONLY=ON"
        logging = "-DCAF_LOG_LEVEL=%s" % self.options.log_level if self.options.log_level != "NONE" else ""
        skip_rpath = '-DCMAKE_SKIP_RPATH=ON' if sys.platform == 'darwin' else ''
        build_type = '-DCMAKE_BUILD_TYPE=%s' % self.settings.build_type
        compiler = '-DCMAKE_CXX_COMPILER=clang++' if self.settings.compiler == 'clang' else ''
        standard_options = \
            "-DCAF_NO_EXAMPLES=ON -DCAF_NO_OPENCL=ON -DCAF_NO_TOOLS=ON -DCAF_NO_UNIT_TESTS=ON -DCAF_NO_PYTHON=ON"

        cmake = CMake(self.settings)
        configure = 'cmake .. %s %s %s %s %s %s %s' % \
                    (cmake.command_line, standard_options, skip_rpath, lib_type, logging, build_type, compiler)
        self._run_command(configure, build_dir)
        self._run_command('cmake --build . %s' % cmake.build_config, build_dir)

    def _run_command(self, cmd, cwd=None):
        self.output.info(cmd)
        self.run(cmd, True, cwd)

    def package(self):
        self.copy("*.hpp",    dst="include/caf", src="%s/libcaf_core/caf" % self.source_dir)
        self.copy("*.hpp",    dst="include/caf", src="%s/libcaf_io/caf" % self.source_dir)
        self.copy("*.dylib",  dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.so",     dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.so.*",   dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.a",      dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.lib",    dst="lib",         src="%s/build/lib/%s" % (self.source_dir, self.settings.build_type),
                  keep_path=False)
        self.copy("license*", dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        if self.options.shared:
            self.cpp_info.libs.extend(["caf_io", "caf_core"])
        if self.options.static:
            self.cpp_info.libs.extend(["caf_io_static", "caf_core_static"])
