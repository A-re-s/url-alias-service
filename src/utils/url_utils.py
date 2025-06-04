def id_to_short_url(num: int) -> str:
    """
    Convert a number to base62 string using digits 0-9, letters a-z and A-Z.
    This provides a unique, short representation of the number.

    Args:
        num: The number to convert (must be positive)

    Returns:
        A base62 string representation of the number

    Example:
        >>> id_to_short_url(123)
        '1Z'
        >>> id_to_short_url(1000)
        'g8'
    """

    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(chars)

    if num == 0:
        return chars[0]

    result = []
    while num:
        num, remainder = divmod(num, base)
        result.append(chars[remainder])

    return "".join(reversed(result))


def generate_short_code(id: int) -> str:
    """
    Generate a unique short code from a database ID.
    This ensures uniqueness as database IDs are unique.

    Args:
        id: The database ID to convert

    Returns:
        A unique short code
    """
    return id_to_short_url(id) + "~"
