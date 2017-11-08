# [Conan](http://conan.io) recipe for [CAF](http://actor-framework.org)

[ ![Download](https://api.bintray.com/packages/bincrafters/public-conan/caf%3Abincrafters/images/download.svg) ](https://bintray.com/bincrafters/public-conan/caf%3Abincrafters/_latestVersion)

|Platform|Build Status|
|:----|:----|
|Linux|[![Travis Build Status](https://travis-ci.org/bincrafters/conan-caf.svg?branch=0.15.5-upgrade)](https://travis-ci.org/sourcedelica/conan-caf)|
|Windows|[![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/8qdaau0pxfn3g58o/branch/0.15.5-upgrade?svg=true)](https://ci.appveyor.com/project/sourcedelica/conan-caf/branch/bintray_setup)|

## Setup

### Conan
```
pip install conan
```

## Usage

Add a requirement for `caf/0.15.5@actor-framework/stable`
to your `conanfile.txt` or `conanfile.py`.

### Build Options

There are a number of CAF-specific options which are activated
using `caf:option=value`:

|Option     |Values                             |Default  |Description             |
|:----------|:----------------------------------|:--------|:-----------------------|
|`shared`   |`True`, `False`                    | `False` | Build shared libraries |
|`static`   |`True`, `False`                    | `True`  | Build static libraries |
|`log_level`|`ERROR`, `WARNING`, `INFO`, `DEBUG`| None    | Build with logging     |

For example, to use shared libraries and debug logging for CAF, use:
```
conan install -o caf:shared=True -o caf:log_level=DEBUG
```

Conan keeps track of the option values used and each built combination of
options is a different package.

### GCC 5.1+

CAF compiles with the default C++ ABI.

Verify which version of the C++ ABI your compiler is using by default:

```
g++ --version -v 2>&1 | grep with-default-libstdcxx-abi
```

Edit `~/.conan/conan.conf` and change `compiler.libcxx` depending on the
value of `--with-default-libstdcxx-abi`:

| ABI value | Conan `compiler.libcxx` |
|:----------|:------------------------|
| `new`     | `libstdc++11`           |
| `old`     | `libstdc++`             |

You may need to run the `conan` command once to generate it.

## Development

### Testing a new version of the package

1. Edit the following files and and change the version to the new
   version number:
   1. `conanfile.py`
   2. `.travis.yml`
   3. `appveyor.yml`
2. Run `conan create`
 
The syntax for `conan create` is
```
conan create actor-framework/stable [-o caf:option=value]...
```

`conan create` will build CAF and install the package in your local
Conan cache under `~/.conan/data`.  It will also run a smoke test
against the package.


### Continuous Integration

Travis and Appveyor are set up to build packages for a number of
configurations.  See `.travis.yml`, `appveyor.yml` and `build.py`
for details.
