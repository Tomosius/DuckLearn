# tests/test_app.py
from ducklearn.app import add



def test_add():
    """Test that add() correctly sums two integers."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0