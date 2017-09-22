from conan.packager import ConanMultiPackager, PlatformInfo
import linux_platform
import os


if __name__ == "__main__":
    # For testing Docker on Mac
    platform_info = linux_platform if os.getenv('CONAN_LINUX_PLATFORM') else PlatformInfo()

    builder = ConanMultiPackager(platform_info=platform_info)
    builder.add_common_builds()
    filtered_builds = []

    for settings, options, env_vars, build_requires in builder.builds:
        if settings['compiler'] == 'gcc':
            settings['compiler.libcxx'] = 'libstdc++11'
        elif settings['compiler'] == 'clang':
            settings['compiler.libcxx'] = 'libc++'

        filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
