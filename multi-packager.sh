#!/usr/bin/env bash
# TODO - this is a work in progress, mostly meant for manual testing
# Set CONAN_PASSWORD to the Bintray API key
# For example:
#    CONAN_PASSWORD=xxxx ./multi-packager.sh

export CONAN_ARCHS=x86_64
export CONAN_LOGIN_USERNAME=sourcedelica
export CONAN_CHANNEL=testing
export CONAN_REFERENCE=caf/0.15.3
export CONAN_UPLOAD=https://api.bintray.com/conan/sourcedelica/conan-caf
export CONAN_USERNAME=sourcedelica
export CONAN_APPLE_CLANG_VERSIONS=9.0

python build.py
