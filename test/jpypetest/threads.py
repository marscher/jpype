from threading import Thread
from queue import Queue

import jpype
from . import common


class ThreadingTestCase(common.JPypeTestCase):

    def setUp(self):
        super(ThreadingTestCase, self).setUp()

    def _java_printer(self, name, q):
        #jpype.attachThreadToJVM()
        q.put(jpype.java.lang.String("foobar %s" % name))
        #jpype.detachThreadFromJVM()

    def testParallelThreads(self):
        q = Queue()
        t1 = Thread(target=self._java_printer, args=("thread 1", q))
        t2 = Thread(target=self._java_printer, args=("thread 2", q))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        results = q.get(), q.get()
        self.assertItemsEqual(results, ["foobar thread 1",
                                        "foobar thread 2"])
