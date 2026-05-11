Crash Handler Documentation
=============================

Overview
--------

JPype now includes a comprehensive crash handler that provides detailed diagnostic
information when fatal errors occur. This is especially useful for debugging issues
that involve interactions between C++, Python, and Java code.

The crash handler captures and displays:

1. **C++ Stack Trace** - Complete function calls with symbol resolution
2. **Python Stack Trace** - Python code location and available source code
3. **Java Stack Trace** - Java exception information and stack trace
4. **Error Message** - Description of what caused the crash

Features
--------

### Automatic Signal Handling

The crash handler is initialized automatically when JPype starts. It installs
signal handlers for:

- SIGSEGV (Segmentation Fault)
- SIGABRT (Abort)
- SIGBUS (Bus Error)
- SIGFPE (Floating Point Exception)  
- SIGILL (Illegal Instruction)

When any of these signals occur, the handler:

1. Captures all available stack traces
2. Formats and prints a detailed crash report to stderr
3. Exits gracefully with status 128+signal

### Stack Trace Capture

#### C++ Stack Trace

The C++ stack trace includes:
- Function names with C++ name demangling
- File names and shared libraries
- Memory addresses
- Offsets from the function start

Example output::

    === C++ Stack Trace ===
    Frames: 12
    
    [0] /usr/lib/libc.so.6 : abort + 0x1address
    [1] ./build/lib/_jpype.cpython-39-x86_64-linux-gnu.so : JPCrashHandler::emergencyHandler(int) + 0x150
    [2] /lib64/libc.so.6 : __restore_rt + 0x0
    ...

#### Python Stack Trace

The Python stack trace includes:
- File paths and line numbers
- Function names
- Source code lines (retrieved from linecache)
- Exception type and message

Example output::

    === Python Stack Trace ===
    File "test.py", line 42, in main
        result = jpype.javax.swing.JFrame()
    File "/usr/lib/jpype/_jclass.py", line 156, in __init__
        self._init(...)
    ...
    Exception: Attempt to create frame with invalid JVM state

#### Java Stack Trace

The Java stack trace includes:
- Full exception type and message
- Stack trace elements with class, method, and line numbers

Example output::

    === Java Stack Trace ===
    java.lang.NullPointerException: Virtual machine is not initialized
        at org.jpype.JPypeContext.checkInitialized(JPypeContext.java:123)
        at org.jpype.JPypeContext.getTypeManager(JPypeContext.java:456)
    ...

Customization
-------------

### Disable Signal Handlers

If JPype is embedded in another system that already manages signals, you can
disable the automatic signal handlers:

.. code-block:: python

    import jpype
    jpype.jpypeJavaFrame._disable_signal_handlers()
    jpype.startJVM()

Note: This must be called before startJVM() takes effect.

### Custom Crash Callbacks

You can register a custom Python function to be called when a crash is detected.
This allows for custom logging, telemetry, or cleanup:

.. code-block:: python

    import jpype
    from jpype import _crashhandler
    
    def my_crash_handler(crash_info):
        # crash_info is a dict containing:
        # - 'cpp_stack': C++ stack trace
        # - 'python_stack': Python stack trace  
        # - 'java_stack': Java stack trace
        # - 'error_message': Error description
        # - 'error_code': Signal number
        
        # Custom handling here - log to file, send alert, etc.
        with open('/var/log/jpype_crash.log', 'w') as f:
            f.write(crash_info['cpp_stack'])
            f.write(crash_info['python_stack'])
            f.write(crash_info['java_stack'])
    
    _crashhandler.set_crash_callback(my_crash_handler)
    jpype.startJVM()

Debugging with GDB
------------------

If a crash is caused by a signal that the signal handlers don't intercept,
you can still use GDB to get a backtrace:

.. code-block:: bash

    gdb -ex run -ex bt -ex quit python
    (gdb) run your_script.py
    
    # Or attach to running process
    gdb -p <pid>
    (gdb) bt

Integration with Logging
------------------------

For production deployments, integrate crash logs with your logging system:

.. code-block:: python

    import jpype
    import jpype._crashhandler as crashhandler
    import logging
    
    logger = logging.getLogger('jpype')
    
    def log_crash(crash_info):
        logger.critical("JPype Crash Detected")
        logger.critical(crash_info['cpp_stack'])
        logger.critical(crash_info['python_stack'])
        logger.critical(crash_info['java_stack'])
        
        # Send alert if needed
        # send_to_monitoring_system(crash_info)
    
    crashhandler.set_crash_callback(log_crash)

Limitations
-----------

1. **Java Stack Traces in Signal Handlers**: Java stack traces cannot be
   safely captured from within signal handlers, as the JNI environment may
   be in an inconsistent state. The crash handler will indicate when this
   limit is reached.

2. **Python GIL**: If a crash occurs while the Python GIL is not held, the
   Python stack trace may be incomplete or unavailable.

3. **Memory Corruption**: If the crash is caused by severe memory
   corruption, the crash handler itself may crash. This is rare but can occur.

4. **Non-signal Crashes**: Some fatal errors (like out-of-memory) may not
   trigger the signal handlers and will use Python's default error handling.

Best Practices
--------------

1. **Enable in Development**: Always enable crash handler during development
   to catch issues early.

2. **Log to Files**: Configure logging to capture crashes to persistent storage
   for post-mortem analysis.

3. **Monitor Crashes**: Track crashes in production and file issues based on
   crash patterns.

4. **Test Recovery**: Test that your application can handle and log crashes
   cleanly, allowing for graceful shutdown.

5. **Archive Symbols**: Keep debug symbols for your C++ extensions to enable
   resolution of function names in crash reports.

Troubleshooting
---------------

### Crash Handler Not Catching Signal

If you see a segfault message directly instead of the crash handler output,
the signal may not be registered. Check:

1. Is the crash handler initialization being called?
2. Are signal handlers being disabled somewhere in your code?
3. Is the crash from a different thread than the one that initialized JPype?

### Incomplete Stack Traces

C++ stack traces require debug symbols. If you see addresses instead of
function names:

1. Rebuild with debug symbols: ``python setup.py build_ext --debug``
2. Install development headers for libunwind if available
3. Check that DWARF debug info is present: ``nm -D your_module.so``

### Python Backtrace Showing "????"

This occurs when source files are not available. The crash handler tries to
load source from linecache, but if the file has been deleted or modified,
it cannot display the source line. This is not a sign of an error.

See Also
--------

- :doc:`develguide` - Development guide with debugging information
- :doc:`install` - Installation instructions
- `GDB Documentation <https://www.gnu.org/software/gdb/>`_
- `Python Debugging Tools <https://docs.python.org/3/library/debug.html>`_
