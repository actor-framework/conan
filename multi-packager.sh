#!/usr/bin/env bash

# This is a work in progress, meant for manual testing of the multi-packager

# Set CONAN_PASSWORD to the Bintray API key
# For example:
#    CONAN_PASSWORD=xxxx ./multi-packager.sh

export CONAN_ARCHS=x86_64
export CONAN_LOGIN_USERNAME=actor-framework
export CONAN_CHANNEL=stable
export CONAN_REFERENCE=caf/0.15.3
export CONAN_UPLOAD=https://api.bintray.com/conan/actor-framework/actor-framework
export CONAN_USERNAME=actor-framework
export CONAN_APPLE_CLANG_VERSIONS=9.0

python build.py
