from conans import ConanFile, CMake, tools
import os
import platform

class ZeroMQConan(ConanFile):
    name = 'zeromq'

    source_version = '4.3.3'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://zeromq.org/'
    license = 'http://zeromq.org/area:licensing'
    description = 'A library for distributed messaging'
    source_dir = 'zeromq-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    exports_sources = '*.patch'

    libs = {
        'zmq': 5,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/zeromq/libzmq/releases/download/v%s/zeromq-%s.tar.gz' % (self.source_version, self.source_version),
                  sha256='9d9285db37ae942ed0780c016da87060497877af45094ff9e1a1ca736e3875a2')

        # https://b33p.net/kosada/node/7603
        tools.patch(patch_file='skip-abort-%s.patch' % platform.system(),
                    base_path=self.source_dir)

        tools.patch(patch_file='thread-name.patch', base_path=self.source_dir)

        self.run('cp %s/COPYING.LESSER %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils

        cmake = CMake(self)

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER']   = '%s/bin/clang'   % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_CXX_COMPILER'] = '%s/bin/clang++' % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz'
        cmake.definitions['CMAKE_CXX_FLAGS'] = cmake.definitions['CMAKE_C_FLAGS']
        cmake.definitions['CMAKE_CXX_STANDARD'] = '11'
        cmake.definitions['CMAKE_CXX_STANDARD_REQUIRED'] = 'ON'
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['BUILD_SHARED'] = 'ON'
        cmake.definitions['BUILD_STATIC'] = 'OFF'
        cmake.definitions['BUILD_TESTS'] = 'OFF'
        cmake.definitions['WITH_DOCS'] = 'OFF'
        cmake.definitions['WITH_LIBBSD'] = 'OFF'
        cmake.definitions['WITH_LIBSODIUM'] = 'OFF'
        cmake.definitions['ZMQ_BUILD_TESTS'] = 'OFF'
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

        with tools.chdir('%s/lib' % self.install_dir):
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/zmq')
        self.copy('libzmq.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['zmq']
