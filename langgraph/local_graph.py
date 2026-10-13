"""Original deterministic demo: real LangGraph; no model or network calls."""
import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    x: int
    y: int
    operation: str
    result: int

def validate(state):
    if state['operation'] not in ('sum', 'product'):
        raise ValueError('Unsupported operation')
    for name in ('x', 'y'):
        if type(state[name]) is not int:
            raise TypeError('Inputs must be integers')
    return {}

def calculate(state):
    x, y = state['x'], state['y']
    return {'result': x + y if state['operation'] == 'sum' else x * y}

def build_graph():
    graph = StateGraph(State)
    graph.add_node('validate', validate)
    graph.add_node('calculate', calculate)
    graph.add_edge(START, 'validate')
    graph.add_edge('validate', 'calculate')
    graph.add_edge('calculate', END)
    return graph.compile()

if __name__ == '__main__':
    graph = build_graph()
    for operation in ('sum', 'product'):
        state = {'x': 2, 'y': 3, 'operation': operation}
        print(json.dumps(graph.invoke(state), sort_keys=True))
        print('updates:', list(graph.stream(state)))
