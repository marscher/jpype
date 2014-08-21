/* jni_md.h
   Copyright (C) 2001, 2005 Free Software Foundation, Inc.

This file has been taken from GNU Classpath and modified by Martin Scherer, 2014

GNU Classpath is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.
 
GNU Classpath is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with GNU Classpath; see the file COPYING.  If not, write to the
Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 USA.

As a special exception, if you link this library with other files to
produce an executable, this library does not by itself cause the
resulting executable to be covered by the GNU General Public License.
This exception does not however invalidate any other reasons why the
executable file might be covered by the GNU General Public License. */

#ifndef __JPYPE_JNI_MD_H__
#define __JPYPE_JNI_MD_H__

#ifdef MSW
    #include <windows.h>
#endif

#ifndef __has_attribute
  #define __has_attribute(x) 0
#endif

#if defined( _WIN32 )
    #define JNIEXPORT __declspec(dllexport)
    #define JNIIMPORT __declspec(dllimport)
    #define JNICALL __stdcall

    typedef long jint;
    typedef __int64 jlong;
#elif (defined(__GNUC__) && ((__GNUC__ > 4) || (__GNUC__ == 4) && (__GNUC_MINOR__ > 2))) || __has_attribute(visibility)
    #define JNIEXPORT     __attribute__((visibility("default")))
    #define JNIIMPORT     __attribute__((visibility("default")))
    #define JNICALL
#else
    /* Define some defaults */
    #define JNICALL
    #define JNIEXPORT
    #define JNIIMPORT
#endif


typedef unsigned char jboolean;
typedef signed char jbyte;
typedef unsigned short jchar;
typedef short jshort;
typedef int jint;

#ifdef _LP64 /* 64-bit Solaris */
    typedef long jlong;
#else
    typedef long long jlong;
#endif

typedef float jfloat;
typedef double jdouble;
typedef jint jsize;

#endif /* __JPYPE_JNI_MD_H__ */
