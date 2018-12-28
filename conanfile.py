# -*- coding: utf-8 -*-

import os
from conans import ConanFile, VisualStudioBuildEnvironment, tools

class TbbConan(ConanFile):
    name = 'tbb'
    version = '19.2'
    description = 'Intel® Threading Building Blocks (Intel® TBB) is a popular software C++ template library that simplifies the development of software applications running in parallel (key to any multicore computer).'
    url = 'https://github.com/birsoyo/conan-tbb'
    homepage = 'https://github.com/01org/tbb'
    author = 'Orhun Birsoy <orhunbirsoy@gmail.com>'

    license = 'Apache 2.0'

    # Packages the license for the conanfile.py
    exports = ['LICENSE.md']

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'fPIC': [True, False]}
    default_options = 'fPIC=True'

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = 'source_subfolder'
    build_subfolder = 'build_subfolder'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version = self.version.replace('.', '_U')
        tools.download(f'https://github.com/01org/tbb/archive/20{version}.zip', 'tbb.zip')
        tools.unzip(f'tbb.zip')
        os.unlink(f'tbb.zip')
        os.rename(f'{self.name}-20{version}', self.source_subfolder)

        tools.replace_in_file(f'{self.source_subfolder}/MakeFile', 'all: tbb tbbmalloc tbbproxy test examples', """all: tbb tbbmalloc tbbproxy test examples

tbb_debug: mkdir
	$(MAKE) -C "$(work_dir)_debug"  -r -f $(tbb_root)/build/Makefile.tbb cfg=debug

tbb_release: mkdir
	$(MAKE) -C "$(work_dir)_release"  -r -f $(tbb_root)/build/Makefile.tbb cfg=release

tbbmalloc_debug: mkdir
	$(MAKE) -C "$(work_dir)_debug"  -r -f $(tbb_root)/build/Makefile.tbbmalloc cfg=debug malloc

tbbmalloc_release: mkdir
	$(MAKE) -C "$(work_dir)_release"  -r -f $(tbb_root)/build/Makefile.tbbmalloc cfg=release malloc

""")
        #tools.replace_in_file(f'{self.source_subfolder}/src/tbb/tbb_assert_impl.h', 'using namespace std;', '//using namespace std;')

    def build(self):
        if self.settings.arch == 'x86_64':
            arch = 'intel64'
        elif self.settings.arch == 'x86':
            arch = 'ia32'
        elif str(self.settings.arch).startswith('armv7'):
            arch = 'arm'
        elif str(self.settings.arch).startswith('armv8'):
            arch = 'arm64'

        self.output.warn(arch)

        bt = str(self.settings.build_type)
        if bt != 'Debug':
            bt = 'Release'

        with tools.chdir(self.source_subfolder):
            if 'Windows' in str(self.settings.os):
                runtime = str(self.settings.compiler.toolset).replace('v', 'vc')
                runtime = runtime[:4] + '.' + runtime[4:]
                # -j1 because kept getting 'write error: stdout'.
                make = f'make -j1 arch={arch} stdver=c++17 tbb_build_prefix=my runtime={runtime}'
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    if self.settings.os == 'Windows':
                        self.run(f'{vcvars} && {make} tbb_{bt.lower()}"')
                        self.run(f'{vcvars} && {make} tbbmalloc_{bt.lower()}"')
                    elif self.settings.os == 'WindowsStore':
                        self.run(f'{vcvars} && {make} target_app=uwp target_mode=store tbb_{bt.lower()}"')
                        self.run(f'{vcvars} && {make} target_app=uwp target_mode=store tbbmalloc_{bt.lower()}"')
            elif self.settings.os == 'Linux':
                self.run(f'make arch={arch} stdver=gnu++17 tbb_build_prefix=my')
            elif self.settings.os == 'Macos':
                self.run(f'make arch={arch} stdver=gnu++1z tbb_build_prefix=my')
            elif self.settings.os == 'Android':
                with tools.environment_append({'PATH': [f'{os.path.join(self.deps_cpp_info["ndk_installer"].rootpath, "ndk")}']}), tools.chdir('jni'):
                    self.run(f'ndk-build api_version={self.settings.os.api_level} target=android arch={arch} tbb_os=windows stdver=gnu++17 tbb_build_prefix=my')

    def package(self):
        self.copy(pattern='LICENSE', dst='licenses', src=self.source_subfolder)
        bt = str(self.settings.build_type)
        if bt != 'Debug':
            bt = 'Release'

        self.copy('*', src=f'{self.source_subfolder}/include', dst='include', keep_path=True)
        config_build_path = f'{self.source_subfolder}/build/my_{bt.lower()}'
        if self.settings.os == 'Windows' or self.settings.os == 'WindowsStore':
            self.copy('tbb*.lib', src=config_build_path, dst='lib', keep_path=False)
            self.copy('tbb*.pdb', src=config_build_path, dst='bin', keep_path=False)
            self.copy('tbb*.dll', src=config_build_path, dst='bin', keep_path=False)
        else:
            self.copy('libtbb*.dylib', src=config_build_path, dst='lib', keep_path=False)

    def package_info(self):
        suffix = ''
        if self.settings.build_type == 'Debug':
            suffix = '_debug'
        self.cpp_info.libs = [f'tbb{suffix}']
