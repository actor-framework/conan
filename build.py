from conan.packager import ConanMultiPackager, PlatformInfo
import linux_platform
import os


if __name__ == "__main__":
    # For testing Docker on Mac
    force_linux = os.getenv('CONAN_LINUX_PLATFORM')
    platform_info = linux_platform if force_linux else PlatformInfo()
    system = platform_info.system()

    builder = ConanMultiPackager(platform_info=platform_info)
    builder.add_common_builds()
    filtered_builds = []
    compilers = set()

    for settings, options, env_vars, build_requires in builder.builds:
        compiler = settings['compiler']
        if compiler == 'gcc':
            settings['compiler.libcxx'] = 'libstdc++11'
        elif compiler == 'clang':
            settings['compiler.libcxx'] = 'libc++'
        if force_linux:
            settings['os'] = 'Linux'

        # Support static runtime once PR 590 is in a tagged build
        if system != 'Windows' or settings['compiler.runtime'] in {'MD', 'MDd'}:
            filtered_builds.append([settings, options, env_vars, build_requires])

        # Add one shared library build per compiler (except Windows)
        if platform_info.system() != 'Windows' and compiler not in compilers:
            filtered_builds.append([settings, {'caf:shared': True, 'caf:static': False}, env_vars, build_requires])
            compilers.add(compiler)

    builder.builds = filtered_builds
    builder.run()
