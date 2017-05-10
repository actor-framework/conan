try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from conans import ConanFile
from conans.errors import ConanException


class CAFConan(ConanFile):
    version = '0.15.3'

    name = "caf"
    url = "https://github.com/sourcedelica/conan-recipes/tree/master/caf"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "log_level": ["NONE", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]}
    default_options = "shared=False", "log_level=NONE"
    source_dir = "actor-framework"

    def config_options(self):
        if self.settings.compiler == 'gcc' and float(self.settings.compiler.version.value) >= 5.1:
            if self.settings.compiler.libcxx != 'libstdc++11':
                raise ConanException("You must use the setting compiler.libcxx=libstdc++11")

    def source(self):
        self.run_command("git clone https://github.com/actor-framework/actor-framework.git")
        self.run_command("git checkout -b %s.x %s" % (self.version, self.version), self.source_dir)

    def build(self):
        static_suffix = "" if self.options.shared else "-only"
        logging = "--with-log-level=%s" % self.options.log_level if self.options.log_level != "NONE" else ""
        configure = \
            "./configure --no-python --no-examples --no-opencl --no-tools --no-unit-tests --build-static%s %s" % \
            (static_suffix, logging)
        self.run_command("%s" % configure, self.source_dir)
        self.run_command("make", self.source_dir)

    def run_command(self, cmd, cwd=None):
        self.output.info(cmd)
        self.run(cmd, True, cwd)

    def package(self):
        self.copy("*.hpp",   dst="include/caf", src="%s/libcaf_core/caf" % self.source_dir)
        self.copy("*.hpp",   dst="include/caf", src="%s/libcaf_io/caf" % self.source_dir)
        self.copy("*.dylib", dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.so",    dst="lib",         src="%s/build/lib" % self.source_dir)
        self.copy("*.a",     dst="lib",         src="%s/build/lib" % self.source_dir)

    def package_info(self):
        self.cpp_info.libs = ["caf_io_static", "caf_core_static"]
