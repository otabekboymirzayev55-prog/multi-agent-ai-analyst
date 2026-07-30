"""
Run: python -m tests.test_data_agent
Checks Feature 5 — a "how many..." question should return the correct
number from data/company.db. (There are 5 churned customers in the sample data.)
"""
from src.state import new_state
from src.agents.data_sql import data_agent

if __name__ == "__main__":
    state = new_state("How many customers have churned?")
    result = data_agent(state)

    print(result["sql_result"])
    print("\nsteps:", result["steps"])
    print("\nCheck by eye: the sample data has 5 churned customers.")
