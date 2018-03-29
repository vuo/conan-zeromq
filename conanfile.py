from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import platform

class ZeroMQConan(ConanFile):
    name = 'zeromq'

    source_version = '2.2.0'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-1@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://zeromq.org/'
    license = 'http://zeromq.org/area:licensing'
    description = 'A library for distributed messaging'
    source_dir = 'zeromq-%s' % source_version
    build_dir = '_build'
    exports_sources = '*.patch'

    def source(self):
        tools.get('http://download.zeromq.org/zeromq-%s.tar.gz' % self.source_version,
                  sha256='43904aeb9ea6844f72ca02e4e53bf1d481a1a0264e64979da761464e88604637')

        # https://b33p.net/kosada/node/7603
        tools.patch(patch_file='skip-abort.patch', base_path=self.source_dir)

        self.run('mv %s/COPYING.LESSER %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = []

            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-Wno-error')

            if platform.system() == 'Darwin':
                autotools.cxx_flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-headerpad_max_install_names')
                autotools.link_flags.append('-Wl,-install_name,@rpath/libzmq.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--disable-static',
                                          '--enable-shared',
                                          '--enable-silent-rules',
                                          '--without-documentation',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include/zmq')
        self.copy('libzmq.dylib', src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['zmq']
