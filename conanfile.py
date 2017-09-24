try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import subprocess
from conans import ConanFile, CMake, tools
from conans.errors import ConanException


# TODO - CAF uses the default ABI. build.py is hardcoded to libstdc++11 for gcc, also _gcc_libcxx() workaround below.
# TODO - Add to CAF configure/CMakeLists.txt: libcxx, arch, additional CXX flags (for /MP8 in VS)
# TODO - update docs
# TODO - change Travis and Appveyor config to conan-center
# TODO - static runtime option (after PR 590 is in a tagged build)


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
    generators = 'cmake'

    source_dir = 'actor-framework-%s' % version

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
        # FIXME - revert back to CAF release, this is for testing Clang 4.0/Apple Clang 9.0
        url_format = 'https://github.com/sourcedelica/actor-framework/archive/%s.zip'
        version = '0.15.3.1'
        self.source_dir = 'actor-framework-%s' % version   # REMOVE

        # url_format = 'https://github.com/sourcedelica/actor-framework/archive/%s.zip'
        # version = self.version

        tools.download(url_format % version, '%s.zip' % version)
        tools.unzip('%s.zip' % version)

    def build(self):
        build_dir = '%s/build' % self.source_dir
        os.mkdir(build_dir)

        conan_magic_lines = '''project(caf C CXX)
        set(CONAN_CXX_FLAGS '-std=c++11')
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        cmake_file = '%s/CMakeLists.txt' % self.source_dir
        tools.replace_in_file(cmake_file, 'project(caf C CXX)', conan_magic_lines)

        cmake = CMake(self)
        cmake.parallel = True

        # skip_rpath = '-DCMAKE_SKIP_RPATH=ON' if sys.platform == 'darwin' else ''
        # build_type = '-DCMAKE_BUILD_TYPE=%s' % self.settings.build_type
        # compiler = '-DCMAKE_CXX_COMPILER=clang++' if self.settings.compiler == 'clang' else ''

        for define in ['CAF_NO_EXAMPLES', 'CAF_NO_TOOLS', 'CAF_NO_UNIT_TESTS', 'CAF_NO_PYTHON']:
            cmake.definitions[define] = 'ON'
        if self.options.static:
            static_def = 'CAF_BUILD_STATIC' if self.options.shared else 'CAF_BUILD_STATIC_ONLY'
            cmake.definitions[static_def] = 'ON'
        if self.options.log_level and self.options.log_level != 'NONE':
            cmake.definitions['CAF_LOG_LEVEL'] = self.options.log_level

        cmake.configure(source_dir=self.source_dir)

        cmake.build()

    def _run_command(self, cmd, output=True, cwd=None):
        self.output.info(cmd)
        self.run(cmd, output=output, cwd=cwd)

    def package(self):
        self.copy('*.hpp',    dst='include/caf', src='%s/libcaf_core/caf' % self.source_dir)
        self.copy('*.hpp',    dst='include/caf', src='%s/libcaf_io/caf' % self.source_dir)
        self.copy('*.dylib',  dst='lib',         src='lib')
        self.copy('*.so',     dst='lib',         src='lib')
        self.copy('*.so.*',   dst='lib',         src='lib')
        self.copy('*.a',      dst='lib',         src='lib')
        self.copy('*.lib',    dst='lib',         src='%s' % self.settings.build_type, keep_path=False)
        self.copy('license*', dst='licenses',    ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        if self.options.shared:
            self.cpp_info.libs.extend(['caf_io', 'caf_core'])
        if self.options.static:
            self.cpp_info.libs.extend(['caf_io_static', 'caf_core_static'])
