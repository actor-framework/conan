#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import platform


if __name__ == "__main__":

    builder = build_template_default.get_builder()

    filtered_builds = []

    for settings, options, env_vars, build_requires, reference in builder.items:
        # The CAF build does not support shared on Windows or shared on x86
        if options['caf:shared']:
            if settings['arch'] != 'x86' and platform.system() != 'Windows':
                filtered_builds.append([settings, options, env_vars, build_requires])
        else:
            filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds

    builder.run()
