# Set CONAN_PASSWORD to the Bintray API key

export CONAN_ARCHS=x86_64
export CONAN_LOGIN_USERNAME=sourcedelica
export CONAN_CHANNEL=testing
export CONAN_REFERENCE=caf/0.15.3
export CONAN_UPLOAD=https://api.bintray.com/conan/sourcedelica/conan-caf
export CONAN_USERNAME=sourcedelica
export CONAN_CLANG_VERSIONS=3.9

export CONAN_LINUX_PLATFORM=T
export CONAN_DOCKER_IMAGE=lasote/conanclang39

python3 build.py