#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


from bincrafters import build_template_default
import platform


if __name__ == "__main__":
    builder = build_template_default.get_builder()

    filtered_builds = []

    for settings, options, env_vars, build_requires in builder.builds:
        # The CAF build does not support shared on Windows or shared on x86
        if options['caf:shared']:
            if settings['arch'] != 'x86' and platform.system() != 'Windows':
                filtered_builds.append([settings, options, env_vars, build_requires])
        else:
            filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds

    builder.run()
