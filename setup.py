#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import platform
from glob import glob

from setuptools import setup
from setuptools import Extension
from setuptools.command.build_ext import build_ext

"""
this parameter is used to opt out numpy support in _jpype library
"""
if "--disable-numpy" in sys.argv:
    disabled_numpy = True
    sys.argv.remove("--disable-numpy")
else:
    disabled_numpy = False


def read_utf8(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(filename, encoding='utf-8').read()

def find_sources():
    cpp_files = []
    for dirpath, dirnames, filenames in os.walk('native'):
        for filename in filenames:
            if filename.endswith('.cpp') or filename.endswith('.c'):
                cpp_files.append(os.path.join(dirpath, filename))
    return cpp_files


platform_specific = {
    'include_dirs': [
        os.path.join('native', 'common', 'include'),
        os.path.join('native', 'python', 'include'),
    ],
    'sources': find_sources(),
}

fallback_jni = os.path.join('src', 'native', 'jni_include')
# TODO: remove  this
os.environ['JAVA_HOME'] = ''
# try to include JNI first from eventually given JAVA_HOME, then from distributed
java_home = os.getenv('JAVA_HOME')
found_jni = False
if os.path.exists(java_home):
    platform_specific['include_dirs'] += [os.path.join(java_home, 'include')]
    
    # check if jni.h can be found
    for d in platform_specific['include_dirs']:
        if os.path.exists(os.path.join(d, 'jni.h')):
            found_jni = True
            break

    if not found_jni:
        import warnings
        warnings.warn('Falling back to provided JNI headers, since your provided'
                      ' JAVA_HOME %s does not provide jni.h' % java_home)
        platform_specific['include_dirs'] += [fallback_jni]
    
else:
    platform_specific['include_dirs'] += [fallback_jni]

if sys.platform == 'win32':
    platform_specific['libraries'] = ['Advapi32']
    platform_specific['define_macros'] = [('WIN32', 1)]
    if found_jni:
        platform_specific['include_dirs'] += [os.path.join(java_home, 'include', 'win32')]

elif sys.platform == 'darwin':
    platform_specific['libraries'] = ['dl']
    # this raises warning:
    # distutils/extension.py:133: UserWarning: Unknown Extension options: 'library_dir'
    #platform_specific['library_dir'] = [os.path.join(java_home, 'Libraries')]
    platform_specific['define_macros'] = [('MACOSX', 1)]
    if found_jni:
        platform_specific['include_dirs'] += [os.path.join(java_home, 'include', 'darwin')]
else: # linux etc.
    platform_specific['libraries'] = ['dl']
    if found_jni:
        platform_specific['include_dirs'] += [os.path.join(java_home, 'include', 'linux')]
 


# if not opted out, try to use NumPy and define macro 'HAVE_NUMPY', so arrays
# returned from Java can be wrapped efficiently in a ndarray.
if not disabled_numpy:
    try:
        import numpy
        if platform_specific.has_key('define_macros'):
            platform_specific['define_macros'].append(('HAVE_NUMPY', 1))
        else:
            platform_specific['define_macros'] = [('HAVE_NUMPY', 1)]
    
        platform_specific['include_dirs'].append(numpy.get_include())
    except ImportError:
        pass

jpypeLib = Extension(name='_jpype', **platform_specific)

class my_build_ext(build_ext):
    # extra compile args
    copt = {'msvc': ['/EHsc'],
            'gcc' : [],
            'mingw32' : [],
           }
    # extra link args
    lopt = {
            'mingw32' : [],
           }
    
    def initialize_options(self, *args):
        """omit -Wstrict-prototypes from CFLAGS since its only valid for C code."""
        from distutils.sysconfig import get_config_vars
        (opt,) = get_config_vars('OPT')
        if opt:
            os.environ['OPT'] = ' '.join(flag for flag in opt.split() 
                                         if flag != '-Wstrict-prototypes')
        build_ext.initialize_options(self)
        
    def build_extensions(self):
        c = self.compiler.compiler_type
        if self.copt.has_key(c):
           for e in self.extensions:
               e.extra_compile_args = self.copt[ c ]
        if self.lopt.has_key(c):
            for e in self.extensions:
                e.extra_link_args = self.lopt[ c ]
        build_ext.build_extensions(self)

setup(
    name='JPype1',
    version='0.5.5.4',
    description='A Python to Java bridge.',
    long_description=(read_utf8('README.rst') + '\n\n' +
                      read_utf8('doc/CHANGELOG.rst') + '\n\n' +
                      read_utf8('AUTHORS.rst')),
    license='License :: OSI Approved :: Apache Software License',
    author='Steve Menard',
    author_email='devilwolf@users.sourceforge.net',
    maintainer='Luis Nell',
    maintainer_email='cooperate@originell.org',
    url='https://github.com/originell/jpype/',
    platforms=[
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: POSIX :: Linux',
    ],
    classifiers=[
        'Programming Language :: Java',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    packages=[
        'jpype', 'jpype.awt', 'jpype.awt.event', 'jpypex', 'jpypex.swing'],
    package_dir={
        'jpype': 'jpype',
        'jpypex': 'jpypex',
    },
    extras_require = {'numpy' : ['numpy>=1.6']},
    cmdclass={'build_ext': my_build_ext},
    zip_safe=False,
    ext_modules=[jpypeLib],
)
