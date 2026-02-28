"""
utils.py – Small shared utility functions.
"""


def ease_in_out_cubic(t):
    """Smooth easing function for natural acceleration/deceleration."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2
