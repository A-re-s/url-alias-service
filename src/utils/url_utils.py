from sqlalchemy import and_

from models.short_urls import ShortURLModel
from schemas.short_urls import ShortURLFilters


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


def generate_short_code(db_id: int) -> str:
    """
    Generate a unique short code from a database ID.
    This ensures uniqueness as database IDs are unique.

    Args:
        id: The database ID to convert

    Returns:
        A unique short code
    """
    return id_to_short_url(db_id) + "~"


def build_short_url_filters(user_id: int, filters: ShortURLFilters):
    conditions = [ShortURLModel.user_id == user_id]

    if filters.short_code:
        conditions.append(ShortURLModel.short_code == filters.short_code)
    if filters.original_url:
        conditions.append(ShortURLModel.original_url == str(filters.original_url))
    if filters.is_active is not None:
        conditions.append(ShortURLModel.is_active == filters.is_active)
    if filters.tag:
        conditions.append(ShortURLModel.tag == filters.tag)

    return and_(*conditions)
