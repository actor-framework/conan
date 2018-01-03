#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan.packager import ConanMultiPackager, tools
import importlib
import os
import platform


def get_module_location():
    repo = os.getenv("CONAN_MODULE_REPO", "https://raw.githubusercontent.com/bincrafters/conan-templates")
    branch = os.getenv("CONAN_MODULE_BRANCH", "package_tools_modules")
    return repo + "/" + branch

    
def get_module_name():
    return os.getenv("CONAN_MODULE_NAME", "build_template_default")

    
def get_module_filename():
    return get_module_name() + ".py"
    
    
def get_module_url():
    return get_module_location() + "/" + get_module_filename()

    
def get_os():
    return platform.system().replace("Darwin", "Macos")

    
if __name__ == "__main__":
    
    tools.download(get_module_url(), get_module_filename(), overwrite=True)
    
    module = importlib.import_module(get_module_name())
    
    builder = module.get_builder()
    
    builder.builds = filter(if get_os() == "Windows", builder.builds)

        # shared libs not currently supported on windows
        #https://github.com/actor-framework/actor-framework/blob/master/CMakeLists.txt#L15
    else:
        builder.add_common_builds(shared_option_name=name + ":shared")
    
    builder.run()
    
if __name__ == "__main__":
    name = get_name_from_recipe()
    username, channel, version = get_env_vars()
    reference = "{0}/{1}".format(name, version)
    upload = "https://api.bintray.com/conan/{0}/public-conan".format(username)

    builder = ConanMultiPackager(
        username=username, 
        channel=channel, 
        reference=reference, 
        upload=upload,
        remotes=upload, #while redundant, this moves bincrafters remote to position 0
        upload_only_when_stable=True, 
        stable_branch_pattern="stable/*")
        
    builder.run()
