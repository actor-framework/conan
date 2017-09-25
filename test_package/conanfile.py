try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from conans import ConanFile, CMake
import conans.util.files as files
import os


class CAFReuseConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake'

    def build(self):
        self.copy_tests()

        cmake = CMake(self)
        cmake.parallel = True
        cmake.configure()
        cmake.build()

    def _run_command(self, cmd, output=True, cwd=None):
        self.output.info(cmd)
        self.run(cmd, output=output, cwd=cwd)

    def copy_tests(self):
        tests_dir = '%s/tests' % self.conanfile_directory
        repo_url = 'https://github.com/actor-framework/actor-framework.git'
        self._run_command('rm -rf %s' % tests_dir)
        self._run_command('git init %s' % tests_dir)
        self._run_command('git remote add origin %s' % repo_url, output=True, cwd=tests_dir)
        self._run_command('git config core.sparseCheckout true', output=True, cwd=tests_dir)
        sparse_checkout = '%s/.git/info/sparse-checkout' % tests_dir
        files.save(sparse_checkout, 'libcaf_test\n')
        files.save(sparse_checkout, 'libcaf_io/test\n', True)
        version = self.requires['caf'].range_reference.version
        self._run_command('git pull origin %s --depth 1' % version, output=True, cwd=tests_dir)

    def test(self):
        self._run_command(os.path.join('.', 'caf-test'), output=True, cwd='bin')

    def imports(self):
        self.copy('*.dll', dst='bin', src='bin')
        self.copy('*.dylib*', dst='bin', src='lib')
