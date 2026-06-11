import pytest
from calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_divide_normal():
    calc = Calculator()
    assert calc.divide(10, 2) == 5

def test_divide_by_zero():
    calc = Calculator()
    # This test expects a ValueError when dividing by zero.
    # The current calculator.py will throw a ZeroDivisionError instead, causing this test to FAIL.
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)
