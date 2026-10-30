"""Small bounded tools: no execution of model-generated Python or write SQL."""
import ast
import math
import operator
import sqlite3
from pathlib import Path

def calculate(expression):
    if len(expression) > 500:
        raise ValueError('Expression too long')
    node = ast.parse(expression.strip(), mode='eval').body
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print' and len(node.args) == 1 and not node.keywords:
        node = node.args[0]
    if len(list(ast.walk(node))) > 100:
        raise ValueError('Expression too complex')
    ops = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul, ast.Div:operator.truediv, ast.FloorDiv:operator.floordiv, ast.Mod:operator.mod, ast.Pow:operator.pow}
    def evaluate(n):
        if isinstance(n, ast.Constant) and type(n.value) in {int,float}:
            value = n.value
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            value = evaluate(n.operand) * (-1 if isinstance(n.op, ast.USub) else 1)
        elif isinstance(n, ast.BinOp) and type(n.op) in ops:
            left, right = evaluate(n.left), evaluate(n.right)
            if isinstance(n.op, ast.Pow) and abs(right) > 20:
                raise ValueError('Exponent too large')
            value = ops[type(n.op)](left, right)
        else:
            raise ValueError('Only arithmetic expressions are supported')
        if not isinstance(value, (float,int)) or not math.isfinite(value) or abs(value) > 1e12:
            raise ValueError('Result outside supported range')
        return value
    return evaluate(node)

def read_sql(path, query):
    if not query.lstrip().lower().startswith('select'):
        raise ValueError('Only SELECT queries are allowed')
    uri = Path(path).resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True, timeout=3) as conn:
        conn.execute('PRAGMA query_only=ON')
        ticks = 0
        def limit():
            nonlocal ticks
            ticks += 1
            return ticks > 1000
        conn.set_progress_handler(limit, 1000)
        return conn.execute(query).fetchmany(100)
