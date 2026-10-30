from src.llm import create_chat_model
"""Arithmetic specialist. Does not execute generated Python."""
import os
from src.safe_tools import calculate

_llm = create_chat_model()

def code_agent(state):
    expression = _llm.invoke('Return one arithmetic expression using only numbers and + - * / // % ** parentheses. No imports, variables, code fences or explanations. Question: ' + state['question']).content.strip()
    result = str(calculate(expression))
    return {'code_result':result, 'steps':state.get('steps',[]) + ['code']}
