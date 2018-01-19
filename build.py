#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared

if __name__ == "__main__":

    builder = build_template_default.get_builder()

    filtered_builds = []
    compilers = set()
    filtered_builds = []

    for settings, options, env_vars, build_requires in builder.builds:
        compiler = settings['compiler']
        if compiler == 'gcc':
            version = settings['compiler.version']
            libstdcxx = 'libstdc++11' if version >= '5.1' else 'libstdc++'
            settings['compiler.libcxx'] = libstdcxx
        elif compiler == 'clang':
            settings['compiler.libcxx'] = 'libc++'

        if build_shared.get_os() != 'Windows' or settings['compiler.runtime'] in {'MD', 'MDd'}:
            filtered_builds.append([settings, options, env_vars, build_requires])

        # Add one shared library build per x86_64 compiler (except Windows)
        if build_shared.get_os() != 'Windows' and settings['arch'] == 'x86_64' and compiler not in compilers:
            filtered_builds.append([settings, {'caf:shared': True}, env_vars, build_requires])
            compilers.add(compiler)

    builder.builds = filtered_builds

    builder.run()
