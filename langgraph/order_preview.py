"""Synthetic order lookup/preview with real LangGraph and scripted decisions."""
import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    request: str
    observations: list
    decision: dict
    steps: int
    answer: str

def build_graph(selector, orders):
    def decide(state):
        if state['steps'] >= 5:
            raise RuntimeError('Agent exceeded five model turns')
        decision=selector(state)
        if type(decision) is not dict: raise ValueError('Decision must be an object')
        if decision.get('action') not in ('lookup','preview','finish'):
            raise ValueError('Unknown action')
        return {'decision':decision,'steps':state['steps']+1}
    def tool(state):
        d=state['decision']; oid=d.get('order_id'); action=d['action']
        if oid not in orders: observation={'error':'unknown order','order_id':oid}
        elif action=='lookup': observation={'tool':'lookup','order_id':oid,**orders[oid]}
        elif not any(o.get('tool')=='lookup' and o.get('order_id')==oid for o in state['observations']):
            observation={'error':'lookup required before preview','order_id':oid}
        elif type(d.get('quantity')) is not int or d['quantity'] <= 0:
            observation={'error':'quantity must be a positive integer','order_id':oid}
        else:
            order=orders[oid]
            observation={'tool':'preview','order_id':oid,'current_quantity':order['quantity'],'proposed_quantity':d['quantity'],'unit_price':order['unit_price'],'current_total':order['quantity']*order['unit_price'],'proposed_total':d['quantity']*order['unit_price'],'applied':False}
        return {'observations':state['observations']+[observation]}
    def finish(state): return {'answer':state['decision'].get('answer','')}
    graph=StateGraph(State)
    graph.add_node('decide',decide); graph.add_node('tool',tool); graph.add_node('finish',finish)
    graph.add_edge(START,'decide')
    graph.add_conditional_edges('decide',lambda s:'finish' if s['decision']['action']=='finish' else 'tool')
    graph.add_edge('tool','decide'); graph.add_edge('finish',END)
    return graph.compile()

def initial(request): return {'request':request,'observations':[],'steps':0,'answer':''}

def fixture(state):
    observations=state['observations']
    action='lookup' if not observations else 'preview' if observations[-1].get('tool')=='lookup' else 'finish'
    return {'action':action,'order_id':'SYN-42','quantity':5,'answer':'Fixture preview totals: 70 -> 175; no mutation.'}

def demo():
    orders={'SYN-42':{'product':'Desk lamp','quantity':2,'unit_price':35}}
    graph=build_graph(fixture,orders)
    request=initial('Preview SYN-42 quantity 5')
    updates=list(graph.stream(request))
    result=graph.invoke(request)
    assert result['observations'][-1]['proposed_total']==175 and orders['SYN-42']['quantity']==2
    return {'engine':'actual installed LangGraph StateGraph','model_backend':'deterministic test fixture; no LLM inference','node_sequence':[key for update in updates for key in update],'observations':result['observations'],'order_unchanged':True}

if __name__ == "__main__": print(json.dumps(demo(),indent=2))
