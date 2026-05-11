"""
JPype Crash Handler
===================

Provides access to crashhandler functionality from Python code.

This module allows registering custom crash callbacks and controlling
crash handler behavior.
"""

from typing import Callable, Optional, Dict, Any

# Callback function type: takes dict with crash info
CrashCallback = Callable[[Dict[str, Any]], None]

_crash_callback: Optional[CrashCallback] = None
_signal_handlers_disabled: bool = False


def set_crash_callback(callback: Optional[CrashCallback]) -> None:
    """
    Register a custom callback to be invoked when JPype detects a crash.
    
    The callback receives a dict with the following keys:
    - 'cpp_stack': C++ stack trace string
    - 'python_stack': Python stack trace string  
    - 'java_stack': Java stack trace string
    - 'error_message': String describing the error
    - 'error_code': Signal number or error code
    
    Parameters:
        callback: Callable that accepts crash info dict, or None to disable
        
    Example:
        >>> def log_crash(info):
        ...     with open('crash.log', 'w') as f:
        ...         f.write(info['cpp_stack'])
        ...         f.write(info['python_stack'])
        >>> set_crash_callback(log_crash)
    """
    global _crash_callback
    _crash_callback = callback


def get_crash_callback() -> Optional[CrashCallback]:
    """Get the currently registered crash callback."""
    return _crash_callback


def disable_signal_handlers() -> None:
    """
    Disable automatic signal handler installation.
    
    This should be called BEFORE jpype.startJVM() is called.
    
    Useful when JPype is embedded in another system that manages
    signal handlers, like a web server or other framework.
    
    Note: Call this before startJVM() for it to have an effect.
    """
    global _signal_handlers_disabled
    _signal_handlers_disabled = True


def enable_signal_handlers() -> None:
    """
    Enable automatic signal handler installation (default).
    
    This is the default behavior. Only call if you previously
    disabled signal handlers and want to re-enable them.
    
    Must be called before startJVM() to take effect.
    """
    global _signal_handlers_disabled
    _signal_handlers_disabled = False


def are_signal_handlers_enabled() -> bool:
    """Check if signal handlers will be installed."""
    return not _signal_handlers_disabled


__all__ = [
    'set_crash_callback',
    'get_crash_callback', 
    'disable_signal_handlers',
    'enable_signal_handlers',
    'are_signal_handlers_enabled',
]
