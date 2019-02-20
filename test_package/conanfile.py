from conans import ConanFile
import platform

class ZeroMQTestConan(ConanFile):
    generators = 'qbs'

    requires = 'llvm/3.3-5@vuo/stable'

    def build(self):
        # @todo convert to cmake or whatever
        # self.run('qbs -f "%s"' % self.source_folder)
        self.run('true')

    def imports(self):
        self.copy('*', src='bin', dst='bin')
        self.copy('*', dst='lib', src='lib')

    def test(self):
        # self.run('qbs run -f "%s"' % self.source_folder)

        # Ensure we only link to system libraries and our own libraries.
        if platform.system() == 'Darwin':
            self.run('! (otool -L lib/libzmq.dylib | grep -v "^lib/" | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
            self.run('! (otool -L lib/libzmq.dylib | fgrep "libstdc++")')
            self.run('! (otool -L lib/libzmq.dylib | fgrep "@rpath/libc++.dylib")') # Ensure this library references the system's libc++.
            self.run('! (otool -l lib/libzmq.dylib | grep -A2 LC_RPATH | cut -d"(" -f1 | grep "\s*path" | egrep -v "^\s*path @(executable|loader)_path")')
        elif platform.system() == 'Linux':
            self.run('! (ldd lib/libzmq.so | grep "/" | egrep -v "(\s(/lib64/|(/usr)?/lib/x86_64-linux-gnu/)|test_package/build)")')
            self.run('! (ldd lib/libzmq.so | fgrep "libstdc++")')
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
