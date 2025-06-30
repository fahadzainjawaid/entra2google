import random

def generate_random_string(length=12, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    """
    Generate a random string of specified length using the provided allowed characters.

    Args:
        length (int): Length of the random string to generate. Default is 12.
        allowed_chars (str): String of characters to choose from. Default is alphanumeric (A-Z, a-z, 0-9).

    Returns:
        str: Randomly generated string.
    """
    if not allowed_chars:
        raise ValueError("allowed_chars must not be empty")
    if length < 1:
        raise ValueError("length must be at least 1")

    return ''.join(random.choice(allowed_chars) for _ in range(length))
