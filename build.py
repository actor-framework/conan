from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds()
    # filtered_builds = []
    # for settings, options, env_vars, build_requires in builder.builds:
    #     if settings['compiler'] == 'gcc':
    #         settings['compiler.libcxx'] = 'libstdc++11'
    #         # TODO - re-enable other builds
    #         if settings['compiler.version'] == 5.4:
    #             filtered_builds.append([settings, options, env_vars, build_requires])
    # builder.builds = filtered_builds
    builder.run()
