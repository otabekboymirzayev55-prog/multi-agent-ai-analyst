import sqlite3
import pytest
from src.safe_tools import calculate, read_sql

def test_arithmetic():
    assert calculate('print((12 + 8) / 4)') == 5

@pytest.mark.parametrize('expression', ['__import__("os").system("whoami")', '2 ** 1000000000', '[1] * 10000', 'float("nan")'])
def test_arbitrary_code_rejected(expression):
    with pytest.raises((ValueError, SyntaxError)):
        calculate(expression)

def test_sql_read_only(tmp_path):
    path = tmp_path / 'company.db'
    with sqlite3.connect(path) as c:
        c.execute('CREATE TABLE revenue (amount INTEGER)')
        c.execute('INSERT INTO revenue VALUES (42)')
    assert read_sql(path, 'SELECT SUM(amount) FROM revenue') == [(42,)]
    with pytest.raises(ValueError):
        read_sql(path, 'DELETE FROM revenue')
    with pytest.raises(sqlite3.ProgrammingError):
        read_sql(path, 'SELECT * FROM revenue; DELETE FROM revenue')
