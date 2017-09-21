from conan.packager import ConanMultiPackager
import linux_platform


if __name__ == "__main__":
    builder = ConanMultiPackager(platform_info=linux_platform)
    builder.add_common_builds()
    filtered_builds = []

    for settings, options, env_vars, build_requires in builder.builds:
        if settings['compiler'] == 'gcc' or settings['compiler'] == 'clang':
            settings['compiler.libcxx'] = 'libstdc++11'

        filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
