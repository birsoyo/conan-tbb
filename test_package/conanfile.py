# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools, RunEnvironment

class TbbTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy('*.dll', src='bin', dst='bin', root_package='tbb', excludes="*proxy*")
        self.copy('*.dylib', src='bin', dst='bin', root_package='tbb', excludes="*proxy*")

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.environment_append(RunEnvironment(self).vars), tools.chdir('bin'):
                self.run(f'.{os.sep}test_package')
