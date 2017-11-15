from conan.packager import ConanMultiPackager, PlatformInfo
import os, re, platform
import linux_platform


def get_value_from_recipe(search_string):
    with open("conanfile.py", "r") as conanfile:
        contents = conanfile.read()
        result = re.search(search_string, contents)
    return result


def get_name_from_recipe():
    return get_value_from_recipe(r'''name\s*=\s*["'](\S*)["']''').groups()[0]


def get_version_from_recipe():
    return get_value_from_recipe(r'''version\s*=\s*["'](\S*)["']''').groups()[0]


def get_default_vars():
    username = os.getenv("CONAN_USERNAME", "bincrafters")
    channel = os.getenv("CONAN_CHANNEL", "testing")
    version = get_version_from_recipe()
    return username, channel, version


def is_ci_running():
    return os.getenv("APPVEYOR_REPO_NAME","") or os.getenv("TRAVIS_REPO_SLUG","")


def get_ci_vars():
    reponame_a = os.getenv("APPVEYOR_REPO_NAME","")
    repobranch_a = os.getenv("APPVEYOR_REPO_BRANCH","")

    reponame_t = os.getenv("TRAVIS_REPO_SLUG","")
    repobranch_t = os.getenv("TRAVIS_BRANCH","")

    username, _ = reponame_a.split("/") if reponame_a else reponame_t.split("/")
    channel, version = repobranch_a.split("/") if repobranch_a else repobranch_t.split("/")
    return username, channel, version


def get_env_vars():
    return get_ci_vars() if is_ci_running() else get_default_vars()


def get_os():
    return platform.system().replace("Darwin", "Macos")


if __name__ == "__main__":
    name = get_name_from_recipe()
    username, channel, version = get_env_vars()
    reference = "{0}/{1}".format(name, version)
    upload = "https://api.bintray.com/conan/{0}/public-conan".format(username)

    # For testing Docker on Mac
    force_linux = os.getenv('CONAN_LINUX_PLATFORM')
    platform_info = linux_platform if force_linux else PlatformInfo()
    system = platform_info.system()

    builder = ConanMultiPackager(
        username=username, 
        channel=channel, 
        reference=reference, 
        upload=upload,
        remotes=upload, #while redundant, this moves bincrafters remote to position 0
        upload_only_when_stable=True, 
        stable_branch_pattern="stable/*",
        platform_info=platform_info)

    builder.add_common_builds()
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
        if force_linux:
            settings['os'] = 'Linux'

        if system != 'Windows' or settings['compiler.runtime'] in {'MD', 'MDd'}:
            filtered_builds.append([settings, options, env_vars, build_requires])

        # Add one shared library build per x86_64 compiler (except Windows)
        if platform_info.system() != 'Windows' and settings['arch'] == 'x86_64' and compiler not in compilers:
            filtered_builds.append([settings, {'caf:shared': True}, env_vars, build_requires])
            compilers.add(compiler)

    builder.builds = filtered_builds

    builder.run()
