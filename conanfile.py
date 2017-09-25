try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import subprocess
from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class CAFConan(ConanFile):
    # Note: when this version number changes it also needs to be changed in:
    #  test_package/conanfile.py, .travis.yml, appveyor.yml
    version = '0.15.3'

    git_version = '0.15.3.1'
    git_user = 'sourcedelica'

    # git_version = version
    # git_user = 'actor-framework'

    source_dir = 'actor-framework-%s' % git_version

    name = "caf"
    description = "An open source implementation of the Actor Model in C++"
    url = "http://actor-framework.org"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "static": [True, False],
               "log_level": ["NONE", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]}
    default_options = "shared=False", "static=True", "log_level=NONE"
    generators = 'cmake'

    def configure(self):
        if self.settings.compiler == "gcc":
            if self.settings.compiler.version < 4.8:
                raise ConanException("g++ >= 4.8 is required, yours is %s" % self.settings.compiler.version)
            else:
                # This is temporary until CAF adds support for configuring stdlib
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
        git_url = 'https://github.com/%s/actor-framework/archive/%s.zip' % (self.git_user, self.git_version)
        zip_filename = '%s.zip' % self.git_version
        tools.download(git_url, zip_filename)
        tools.unzip(zip_filename)

    def build(self):
        build_dir = '%s/build' % self.source_dir
        os.mkdir(build_dir)

        conan_magic_lines = '''project(caf C CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        cmake_file = '%s/CMakeLists.txt' % self.source_dir
        tools.replace_in_file(cmake_file, 'project(caf C CXX)', conan_magic_lines)

        cmake = CMake(self)
        cmake.parallel = True
        cmake.definitions['CMAKE_CXX_STANDARD'] = '11'
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
        self.copy('*.lib',    dst='lib',         src='lib')
        self.copy('license*', dst='licenses',    ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        if self.options.shared:
            self.cpp_info.libs.extend(['caf_io', 'caf_core'])
        if self.options.static:
            self.cpp_info.libs.extend(['caf_io_static', 'caf_core_static'])
