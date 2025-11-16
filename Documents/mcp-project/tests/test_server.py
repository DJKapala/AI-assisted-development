import pytest

from server import add_numbers


def test_add_numbers_basic():
    """Basic sanity test for add_numbers."""
    assert add_numbers(1, 1) == 2


def test_add_numbers_negative():
    assert add_numbers(-2, 3) == 1
