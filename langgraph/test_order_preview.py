"""Deterministic guard tests; these do not count as live inference evidence."""
import unittest
from order_preview import build_graph, initial, demo

def scripted(*actions):
    iterator=iter(actions)
    return lambda state:next(iterator)
def action(kind, quantity=5, oid='SYN-42'):
    return {'action':kind,'order_id':oid,'quantity':quantity,'answer':'Done'}

class AgentGuards(unittest.TestCase):
    def setUp(self): self.orders={'SYN-42':{'product':'Desk lamp','quantity':2,'unit_price':35}}
    def run_actions(self,*actions):
        return build_graph(scripted(*actions,action('finish')),self.orders).invoke(initial('synthetic test'))
    def test_preview_totals_and_no_mutation(self):
        result=self.run_actions(action('lookup'),action('preview'))
        self.assertEqual(result['observations'][-1]['proposed_total'],175)
        self.assertFalse(result['observations'][-1]['applied'])
        self.assertEqual(self.orders['SYN-42']['quantity'],2)
    def test_lookup_required(self):
        self.assertIn('lookup required',self.run_actions(action('preview'))['observations'][0]['error'])
    def test_invalid_quantities(self):
        for quantity in (0,-1,True,2.5,'5'):
            with self.subTest(quantity=quantity):
                self.assertIn('positive integer',self.run_actions(action('lookup'),action('preview',quantity))['observations'][-1]['error'])
    def test_unknown_order(self):
        self.assertEqual(self.run_actions(action('lookup',oid='missing'))['observations'][0]['error'],'unknown order')
    def test_unknown_action(self):
        with self.assertRaises(ValueError): self.run_actions(action('delete'))
    def test_loop_bound(self):
        with self.assertRaises(RuntimeError):
            build_graph(lambda state:action('lookup'),self.orders).invoke(initial('test'))

    def test_streamed_fixture_path(self):
        result=demo()
        self.assertEqual(result['node_sequence'],['decide','tool','decide','tool','decide','finish'])
        self.assertTrue(result['order_unchanged'])
        self.assertIn('no LLM inference',result['model_backend'])
    def test_nonobject_decision_rejected(self):
        with self.assertRaises(ValueError):
            build_graph(lambda state:[],self.orders).invoke(initial('synthetic test'))

if __name__=='__main__': unittest.main()
