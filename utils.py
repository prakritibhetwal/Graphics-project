"""
utils.py – Shared utility and easing functions.

Provides mathematical helpers for animations and interpolations used
throughout the graphics engine.
"""


def ease_in_out_cubic(t: float) -> float:
    """
    Smooth cubic easing function for natural acceleration and deceleration.
    
    Implements ease-in-out cubic interpolation. At t=0 returns 0, at t=1 returns 1.
    The function has smooth acceleration at the start and smooth deceleration
    at the end, creating natural-feeling animations.
    
    Useful for camera transitions, zoom operations, and fade effects.
    
    Args:
        t: Normalized time parameter, typically 0.0 to 1.0
        
    Returns:
        Eased value (0.0 to 1.0). Can be multiplied by a range to create
        animated values (e.g., t * 100 for 0-100 animation).
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2
