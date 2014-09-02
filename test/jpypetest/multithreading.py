#*****************************************************************************
#   Copyright 2004-2008 Steve Menard
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#	   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#   
#*****************************************************************************
import jpype
import common
import time
import threading

class myThread (threading.Thread):
    """
    try to system.println("hello world") and check for exceptions during the call
    
    join() returns False, if any exception during this has been raised.
    """
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.success = False
        
    def _msg(self, msg):
        print "[" + self.name + "] " + msg

    def run(self):
        self._msg("starting")
        assert jpype.isJVMStarted()
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
        else:
            self._msg('already attached')
            print self.name, 
            
        self._msg("trying to access jvm")
        try:
            jpype.java.lang.System.out.println(self.name + ": hello world")
            #time.sleep(1)q
            self.success = True
        except:
            self._msg("exception")
            import traceback
            self._msg(traceback.format_exc())
            self.success = False
        finally:
            jpype.detachThreadFromJVM()
        
        self._msg("Exiting " + self.name)
        
    def join(self):
        threading.Thread.join(self)
        return self.success

class ThreadingTestCase(common.JPypeTestCase) :
    def setUp(self) :
        # jvm gets started
        common.JPypeTestCase.setUp(self)
    
    def testSequentialThreads(self):
        t1 = myThread(1, "worker-1")
        t2 = myThread(2, "worker-2")

        t1.start()
        self.assertTrue( t1.join(), t1.name + " failed")

        t2.start()
        self.assertTrue( t2.join(), t2.name + " failed")

        
    def testParallelThreads(self):
        t1 = myThread(1, "worker-1")
        t2 = myThread(2, "worker-2")

        t1.start()
        t2.start()

        self.assertTrue( t1.join(), t1.name + " failed")
        self.assertTrue( t2.join(), t2.name + " failed")
    
    @classmethod
    def tearDownClass(cls):
        print "tear down"
        jpype.attachThreadToJVM()

