#!/usr/bin/env python
"""
Example: Using JPype Crash Handler for Diagnostics

This example demonstrates how to use the JPype crash handler to capture
and log comprehensive diagnostic information when fatal errors occur.
"""

import jpype
import jpype._crashhandler as crashhandler
import logging
import sys
from datetime import datetime


# Configure logging to capture crashes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jpype_crash.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('jpype_crash_example')


def crash_logger(crash_info):
    """
    Custom crash handler that logs crash information.
    
    This callback is invoked when JPype detects a fatal signal.
    Args:
        crash_info: Dict with 'cpp_stack', 'python_stack', 'java_stack', 
                   'error_message', 'error_code'
    """
    logger.critical("=" * 80)
    logger.critical("JPYPE CRASH DETECTED")
    logger.critical("=" * 80)
    logger.critical("Timestamp: %s", datetime.now().isoformat())
    logger.critical("Error Message: %s", crash_info.get('error_message', 'Unknown'))
    logger.critical("Error Code: %s", crash_info.get('error_code', -1))
    logger.critical("")
    
    logger.critical("C++ Stack Trace:")
    logger.critical(crash_info.get('cpp_stack', 'Not available'))
    
    logger.critical("Python Stack Trace:")
    logger.critical(crash_info.get('python_stack', 'Not available'))
    
    logger.critical("Java Stack Trace:")
    logger.critical(crash_info.get('java_stack', 'Not available'))
    
    logger.critical("=" * 80)


def example_basic_setup():
    """Example 1: Basic crash handler setup"""
    logger.info("Example 1: Basic crash handler setup")
    
    # Register crash handler callback
    crashhandler.set_crash_callback(crash_logger)
    
    # Start JVM with crash handler enabled
    jpype.startJVM(classpath=['.'])
    
    # Your application code here
    # If a crash occurs, crash_logger will be called
    
    jpype.shutdownJVM()


def example_disable_signals():
    """Example 2: Disable signal handlers (for embedded use)"""
    logger.info("Example 2: Disable signal handlers")
    
    # Disable automatic signal handler installation
    # Call BEFORE startJVM()
    crashhandler.disable_signal_handlers()
    
    # Start JVM without signal handlers
    jpype.startJVM(classpath=['.'])
    
    # Application code here
    
    jpype.shutdownJVM()


def example_graceful_error_handling():
    """Example 3: Graceful error handling with crash reporting"""
    logger.info("Example 3: Graceful error handling")
    
    def graceful_crash_handler(crash_info):
        """
        More sophisticated error handler that could integrate
        with external monitoring systems
        """
        error_msg = crash_info['error_message']
        error_code = crash_info['error_code']
        
        # Log to monitoring system
        logger.critical(f"Signal {error_code}: {error_msg}")
        
        # Extract key information for analytics
        cpp_trace = crash_info['cpp_stack']
        
        # Find the faulting function from C++ trace
        for line in cpp_trace.split('\n'):
            if '[' in line and ']' in line:
                logger.critical(f"Faulting frame: {line}")
                break
        
        # Send alert (in production)
        # send_alert_to_monitoring(error_msg, error_code)
    
    crashhandler.set_crash_callback(graceful_crash_handler)
    jpype.startJVM(classpath=['.'])
    
    # Application code
    
    jpype.shutdownJVM()


def example_check_signal_status():
    """Example 4: Check if signal handlers are enabled"""
    logger.info("Example 4: Check signal handler status")
    
    if crashhandler.are_signal_handlers_enabled():
        logger.info("Signal handlers are ENABLED (default)")
    else:
        logger.info("Signal handlers are DISABLED")
    
    # Can also get the current callback (if any)
    current_callback = crashhandler.get_crash_callback()
    if current_callback:
        logger.info("Current crash callback: %s", current_callback.__name__)
    else:
        logger.info("No crash callback registered")


if __name__ == '__main__':
    logger.info("JPype Crash Handler Examples")
    logger.info("=" * 80)
    
    # Run examples (uncomment to test)
    
    try:
        logger.info("\nRunning: Basic Setup Example")
        example_basic_setup()
    except Exception as e:
        logger.exception("Example failed: %s", e)
    
    try:
        example_check_signal_status()
    except Exception as e:
        logger.exception("Example failed: %s", e)
    
    logger.info("\n" + "=" * 80)
    logger.info("Examples complete. Check jpype_crash.log for crash reports.")
