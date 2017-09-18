# [Conan](http://conan.io) recipe for [CAF](http://actor-framework.org)

## Setup

### Conan
```
pip install conan
```

### GCC 5.1+

CAF compiles with the default C++ ABI.

Verify which version of the C++ ABI your compiler is using by default:

```
g++ --version -v 2>&1 | grep -- --with-default-libstdcxx-abi
```

Edit `~/.conan/conan.conf` and change `compiler.libcxx` depending on the
value of `--with-default-libstdcxx-abi`:

| ABI value | Conan `compiler.libcxx` |
|:----------|:------------------------|
| `new`     | `libstdc++11`           |
| `old`     | `libstdc++`             |

You may need to run the `conan` command once to generate it.

## Usage

Add a requirement for `caf/version@sourcedelica/testing`
to your `conanfile.txt` or `conanfile.py`.

Check `conanfile.py` in this repo for the _version_.  It is
the first attribute in the class definition:
```
class CAFConan(ConanFile):
    version = '2.5.0'
```

## Build Options

Supported options are:

|Option     |Values                             |Default  |Description             |
|:----------|:----------------------------------|:--------|:-----------------------|
|`shared`   |`True`, `False`                    | `False` | Build shared libraries |
|`static`   |`True`, `False`                    | `True`  | Build static libraries |
|`log_level`|`ERROR`, `WARNING`, `INFO`, `DEBUG`| None    | Build with logging     |

For example, to build with shared libraries and debug logging, use:
```
conan test_package -o caf:shared=True -o caf:log_level=DEBUG
```

Conan keeps track of the option values used and each built combination of
options is a different package.

## Development

### Building a new version of the package

1. Edit `conanfile.py` and `test_package/conanfile.py` and change the
   `version` attribute to the new version number.
2. Run `conan test_package`  
 
The syntax for `conan test_package` is  
```
conan test_package [-o caf:option=value]...
```

`conan test_package` will build CAF and install the package in your local 
Conan repository under `~/.conan/data`.  It will also run a smoke test 
against the package.


### Uploading built packages to `conan.io`
```
conan upload --all caf/version@user/channel
```
where _version_, _user_, and _channel_ are the same values from 
[Building a new version](#building-a-new-version-of-the-package) above.

This command will upload all of the packages built with that _version_ 
to the `conan.io` repository.

After the package is uploaded successfully you should commit and push 
the updated `conanfile.py` files to Github.
