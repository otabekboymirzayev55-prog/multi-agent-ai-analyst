"""Arithmetic specialist. Does not execute generated Python."""
import os
from langchain_openai import ChatOpenAI
from src.config import GEMINI_API_KEY, PROXY_BASE_URL
from src.safe_tools import calculate

_llm = ChatOpenAI(base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model=os.getenv('GEMINI_MODEL','gemini-flash-lite'), timeout=15, max_retries=0)

def code_agent(state):
    expression = _llm.invoke('Return one arithmetic expression using only numbers and + - * / // % ** parentheses. No imports, variables, code fences or explanations. Question: ' + state['question']).content.strip()
    result = str(calculate(expression))
    return {'code_result':result, 'steps':state.get('steps',[]) + ['code']}
