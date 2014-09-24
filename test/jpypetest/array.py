#*****************************************************************************
#   Copyright 2004-2008 Steve Menard
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#   
#*****************************************************************************
import unittest2 as unittest
import difflib
import pprint
import jpype
from jpype import JPackage, JArray, JByte, java
from . import common

try:
    import numpy as np
    haveNumpy = True
except ImportError:
    haveNumpy = False

class ArrayTestCase(common.JPypeTestCase) :
    
    def assertSequenceEqual__(self, seq1, seq2,
                            msg=None, seq_type=None, max_diff=80*8):
        """
        taken from unittest2.TestCase.assertSequenceEqual and adopted to run
        with numpy arrays
        """
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException('First sequence is not a %s: %s'
                                            % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException('Second sequence is not a %s: %s'
                                            % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        if differing is None:
            if haveNumpy:
                if np.all(seq1 == seq2):
                    return
            else:
                if seq1 == seq2:
                    return

            seq1_repr = repr(seq1)
            seq2_repr = repr(seq2)
            if len(seq1_repr) > 30:
                seq1_repr = seq1_repr[:30] + '...'
            if len(seq2_repr) > 30:
                seq2_repr = seq2_repr[:30] + '...'
            elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
            differing = '%ss differ: %s != %s\n' % elements

            for i in xrange(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                 (i, seq_type_name))
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                 (i, seq_type_name))
                    break

                if item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                 (i, item1, item2))
                    break
            else:
                if (len1 == len2 and seq_type is None and
                    type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                             'elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                             'elements.\n' % (seq_type_name, len2 - len1))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))

        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)
    
    def setUp(self):
        common.JPypeTestCase.setUp(self)
        self.VALUES = [12234,1234,234,1324,424,234,234,142,5,251,242,35,235,62,
                       1235,46,245132,51, 2, 3, 4]
    
    @classmethod
    def setUpClass(self):
        self.assertItemsEqual = self.assertSequenceEqual__
        self.assertSequenceEqual = self.assertSequenceEqual__
    
    def testReadArray(self) :
        t = JPackage("jpype").array.TestArray()
        assert not isinstance(t, JPackage)
        
        self.assertSequenceEqual(self.VALUES, t.i)
        
        self.assertEqual(t.i[0], self.VALUES[0])
        self.assertSequenceEqual(self.VALUES[1:-2], t.i[1:-2])

    def testStangeBehavior(self) :
        ''' Test for stange crash reported in bug #1089302'''
        Test2 = jpype.JPackage('jpype.array').Test2
        test = Test2()
        test.test(test.getValue())

    def testWriteArray(self) :
        t = JPackage("jpype").array.TestArray()
        assert not isinstance(t, JPackage)

        t.i[0] = 32
        self.assertEqual(t.i[0], 32)
        
        t.i[1:3] = (33, 34)
        self.assertEqual(t.i[1], 33)
        self.assertEqual(t.i[2], 34)
        
        self.assertSequenceEqual(t.i[:5], (32, 33, 34 ,1324, 424) )
        
    def testObjectArraySimple(self) :
        a = JArray(java.lang.String, 1)(2)
        a[1] = "Foo"
        self.assertEqual("Foo", a[1])
        
    def testByteArraySimple(self) :
        a = JArray(JByte)(2)
        a[1] = 2
        self.assertEqual(a[1], 2)
        
    def testIterateArray(self):
        t = JPackage("jpype").array.TestArray()
        self.assertFalse(isinstance(t, JPackage))

        for i in t.i :
            self.assertNotEqual(i, 0)

    def testGetSubclass(self) :
        t = JPackage("jpype").array.TestArray()
        v = t.getSubClassArray()
        
        self.assertTrue(isinstance(v[0], unicode))
        
    def testGetArrayAsObject(self) :
        t = JPackage("jpype").array.TestArray()
        v = t.getArrayAsObject()     

    def testCharArrayAsString(self) :
        t = JPackage("jpype").array.TestArray()
        v = t.charArray
        self.assertEqual(str(v), 'avcd')
        self.assertEqual(unicode(v), u'avcd')
        
    def testByteArrayAsString(self) :
        t = JPackage("jpype").array.TestArray()
        v = t.byteArray
        self.assertEqual(str(v), 'avcd')
        
    def testByteArrayIntoVector(self):
        ba = jpype.JArray(jpype.JByte)(b'123')
        v = jpype.java.util.Vector(1)
        v.add(ba)
        self.assertEqual(len(v), 1)
        self.assertNotEqual(v[0], None)
        
    def testJArrayConversionBool(self):
        expected = [True, False, False, True]
        jarr = jpype.JArray(jpype.JBoolean)(expected)
        
        self.assertSequenceEqual(expected, jarr[:])

    def testJArrayConversionChar(self):
        t = JPackage("jpype").array.TestArray()
        v = t.charArray
        self.assertEqual(v[:], 'avcd')
        # FIXME: this returns unicode on windows
        self.assertEqual(str(v[:]), 'avcd')
        self.assertEqual(unicode(v[:]), u'avcd')
        
    def testJArrayConversionByte(self):
        expected = (0,1,2,3)
        ByteBuffer = jpype.java.nio.ByteBuffer
        bb = ByteBuffer.allocate(4)
        buf = bb.array()
        for i in xrange(len(expected)):
            buf[i] = expected[i]
        
        self.assertSequenceEqual(expected[:], buf[:])

    def testJArrayConversionShort(self):
        # filter out values, which can not be converted to jshort
        self.VALUES = [v for v in self.VALUES if v < (2**16/2 - 1) 
                                             and v > (2**16/2 * -1)]
        jarr = jpype.JArray(jpype.JShort)(self.VALUES)
        result = jarr[0 : len(jarr)]
        self.assertItemsEqual(self.VALUES, result)
        
        result = jarr[2:10]
        self.assertSequenceEqual(self.VALUES[2:10], result)
        
        # TODO: investigate why overflow is being casted on linux, but not on windows
        #with self.assertRaises(jpype._):
        #    jpype.JArray(jpype.JShort)([2**16/2])
        
    def testJArrayConversionInt(self):
        jarr = jpype.JArray(jpype.JInt)(self.VALUES)
        result = jarr[0 : len(jarr)]
        self.assertSequenceEqual(self.VALUES, result)
        
        result = jarr[2:10]
        self.assertSequenceEqual(self.VALUES[2:10], result)
    
    def testJArrayConversionLong(self):
        jarr = jpype.JArray(jpype.JLong)(self.VALUES)
        result = jarr[0 : len(jarr)]
        self.assertSequenceEqual(self.VALUES, result)
        
        result = jarr[2:10]
        self.assertSequenceEqual(self.VALUES[2:10], result)
        
    def testJArrayConversionFloat(self):
        self.VALUES = map(float, self.VALUES)
        jarr = jpype.JArray(jpype.JFloat)(self.VALUES)
        result = jarr[0 : len(jarr)]
        self.assertSequenceEqual(self.VALUES, result)
        
        result = jarr[2:10]
        self.assertSequenceEqual(self.VALUES[2:10], result)
        
    def testJArrayConversionDouble(self):
        self.VALUES = map(float, self.VALUES)
        jarr = jpype.JArray(jpype.JDouble)(self.VALUES)
        result = jarr[:]
        self.assertSequenceEqual(self.VALUES, result)
        
        result = jarr[2:10]
        self.assertSequenceEqual(self.VALUES[2:10], result)
        
        # empty slice
        result = jarr[-1:3]
        expected = self.VALUES[-1:3]
        self.assertSequenceEqual(expected, result)
        
        result = jarr[3:-2]
        expected = self.VALUES[3:-2]
        self.assertSequenceEqual(expected, result)

    def testConversionError(self):
        jarr = jpype.JArray(jpype.JInt, 1)(10)
        with self.assertRaises(RuntimeError):
            jarr[1:2] = [dict()]
        
        # -1 is returned by python, if conversion fails also, ensure this works
        jarr[1:2] = [-1]
        
    def testObjectArrayInitial(self):
        l1 = java.util.ArrayList()
        l1.add(0)
        l2 = java.util.ArrayList()
        l2.add(42)
        l3 = java.util.ArrayList()
        l3.add(13)
        jarr = jpype.JArray(java.util.ArrayList, 1)([l1, l2, l3])
        
        self.assertEqual(l1, jarr[0])
        self.assertEqual(l2, jarr[1])
        self.assertEqual(l3, jarr[2])
        
    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPBoolArray(self):
        n = 100
        a = np.random.randint(0, 1, size=n).astype(np.bool)
        jarr = jpype.JArray(jpype.JBoolean)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)

    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPByteArray(self):
        n = 100
        a = np.random.randint(-128, 127, size=n).astype(np.byte)
        jarr = jpype.JArray(jpype.JByte)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)

    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPShortArray(self):
        n = 100
        a = np.random.randint(-32768, 32767, size=n).astype(np.short)
        jarr = jpype.JArray(jpype.JShort)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)
        
    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetIntArray(self):
        n = 100
        a = np.random.randint(-2**31, 2**31 - 1, size=n).astype(np.int32)
        jarr = jpype.JArray(jpype.JInt)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)
        
    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPLongArray(self):
        n = 100
        # actuall the lower bound should be -2**63 -1, but raises Overflow error in numpy
        a = np.random.randint(-2**63, 2**63 - 1, size=n).astype(np.int64)
        jarr = jpype.JArray(jpype.JLong)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)
    
    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPFloatArray(self):
        n = 100
        a = np.random.random(n).astype(np.float32)
        jarr = jpype.JArray(jpype.JFloat)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)
        
    @unittest.skipUnless(haveNumpy, "numpy not available")
    def testSetFromNPDoubleArray(self):
        n = 100
        a = np.random.random(n).astype(np.float64)
        jarr = jpype.JArray(jpype.JDouble)(n)
        jarr[:] = a
        self.assertSequenceEqual(a, jarr)
