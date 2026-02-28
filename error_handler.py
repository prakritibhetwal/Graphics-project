"""
error_handler.py – Centralized error handling and logging utilities.

Provides consistent error handling patterns across the graphics engine,
including logging, graceful degradation, and resource cleanup on critical errors.
"""
import sys
import traceback
from typing import Optional, Callable


class GraphicsError(Exception):
    """Base exception for graphics engine errors."""
    pass


class OpenGLError(GraphicsError):
    """Raised when OpenGL operations fail."""
    pass


class WindowError(GraphicsError):
    """Raised when window/GLFW operations fail."""
    pass


class ResourceError(GraphicsError):
    """Raised when resource loading fails."""
    pass


def log_error(message: str, error_type: str = "ERROR", print_traceback: bool = False) -> None:
    """
    Log an error message to console and/or file.
    
    Args:
        message: The error message to log
        error_type: Type of error (ERROR, WARNING, CRITICAL)
        print_traceback: If True, print the full traceback
    """
    prefix = f"[{error_type}]"
    output = f"{prefix} {message}"
    print(output, file=sys.stderr)
    
    if print_traceback:
        traceback.print_exc(file=sys.stderr)


def handle_opengl_error(operation: str = "OpenGL operation") -> None:
    """
    Check for and handle OpenGL errors.
    
    Args:
        operation: Description of the operation that may have failed
    """
    from OpenGL.GL import glGetError, GL_NO_ERROR
    
    error_code = glGetError()
    if error_code != GL_NO_ERROR:
        error_names = {
            0x0500: "GL_INVALID_ENUM",
            0x0501: "GL_INVALID_VALUE",
            0x0502: "GL_INVALID_OPERATION",
            0x0505: "GL_OUT_OF_MEMORY",
        }
        error_name = error_names.get(error_code, f"GL_ERROR_{error_code}")
        log_error(f"{operation} failed: {error_name} (0x{error_code:X})", error_type="OPENGL_ERROR")
        return False
    return True


def safe_call(func: Callable, *args, operation_name: str = "", catch_exceptions: bool = True, **kwargs) -> Optional:
    """
    Safely call a function with error handling and traceback reporting.
    
    Args:
        func: The function to call
        *args: Positional arguments for the function
        operation_name: Human-readable name for logging
        catch_exceptions: If False, exceptions will not be caught
        **kwargs: Keyword arguments for the function
        
    Returns:
        The return value of func, or None if an error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_msg = operation_name or func.__name__
        log_error(f"Error in {error_msg}: {str(e)}", error_type="EXCEPTION", print_traceback=True)
        if not catch_exceptions:
            raise
        return None


def ensure_file_exists(filepath: str, error_if_missing: bool = False) -> bool:
    """
    Verify that a file exists at the given path.
    
    Args:
        filepath: Path to check
        error_if_missing: If True, raise ResourceError if file is missing
        
    Returns:
        True if file exists, False otherwise
    """
    import os
    exists = os.path.isfile(filepath)
    if not exists:
        msg = f"File not found: {filepath}"
        if error_if_missing:
            log_error(msg, error_type="RESOURCE_ERROR")
            raise ResourceError(msg)
        else:
            log_error(msg, error_type="WARNING")
    return exists


def safe_gl_call(func: Callable, *args, operation_name: str = "", **kwargs) -> Optional:
    """
    Call an OpenGL function and check for errors.
    
    Args:
        func: The OpenGL function to call
        *args: Positional arguments
        operation_name: Description of the operation
        **kwargs: Keyword arguments
        
    Returns:
        The return value of func, or None if an error occurred
    """
    result = safe_call(func, *args, operation_name=operation_name, **kwargs)
    handle_opengl_error(operation_name or func.__name__)
    return result


class ErrorContext:
    """Context manager for error handling in complex operations."""
    
    def __init__(self, operation_name: str, cleanup_func: Optional[Callable] = None):
        """
        Initialize error context.
        
        Args:
            operation_name: Name of the operation for logging
            cleanup_func: Optional cleanup function to call on error
        """
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func
        self.error_occurred = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            log_error(
                f"Error in {self.operation_name}: {exc_val}",
                error_type="OPERATION_ERROR",
                print_traceback=True
            )
            if self.cleanup_func:
                try:
                    self.cleanup_func()
                except Exception as cleanup_error:
                    log_error(f"Cleanup failed: {cleanup_error}", error_type="CLEANUP_ERROR")
            return False
        return True
