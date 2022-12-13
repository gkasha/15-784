from __future__ import print_function
from pyhop import hop

import global_operators
import global_methods


"""
Problem definition
"""

def print_htn(H, depth):

    if not H:
        return

    tabs = ""
    for i in range(depth):
        tabs += "\t"
    
    for arr in H:
        for d in arr:
            print(tabs + "{}".format(d))
            print_htn(arr[d],depth+1)

def border_delivery_m(state, goal):
    keys = (list)(state.pos.keys())
    p1,p2 = keys[0],keys[1]

    # Describe store package ordering < random check
    return [('store_packages', p1, p2, "ext", "storage"), ('random_check', p1)]

hop.declare_methods('border_delivery', border_delivery_m)


print('')
hop.print_operators(hop.get_operators())
print('')
hop.print_methods(hop.get_methods())

state1 = hop.State('state1')
state1.pos={'p1':'X','p2':'X'}
state1.check={'p1':'F', 'p2':'F'}

print("- Define state1:")
hop.print_state(state1)
print('')

goal1 = hop.Goal('goal1')
goal1.pos={'p1':'storage','p2':'storage'}
goal1.check={'p1':'T','p2':'F'}

print("- Define goal1:")
hop.print_goal(goal1)
print('')


# plan = hop.plan(state1,
#             [('border_delivery',goal1)], 
#             hop.get_operators(), 
#             hop.get_methods(), 
#             verbose=3)

res = hop.build_htn(state1,[('border_delivery',goal1)],hop.get_operators(),hop.get_methods(),verbose=3)
print(res)
print_htn(res,0)

print("-------")
print("Switching to local decomp")
hop.clear()

import local_methods
import local_operators

def border_delivery_r_m(state, r, goal):
    keys = (list)(state.pos.keys())
    p1,p2 = keys[0],keys[1]

    # Describe store package ordering < random check
    return [('store_packages', r, p1, p2, "ext", "storage"), ('random_check', r, p1)]

hop.declare_methods('border_delivery', border_delivery_r_m)


l0 = "startpos"
r1 = "robot1"
state2 = hop.State('state2')
state2.pos={'p1':'ext', 'p2' : 'ext', r1 : l0}
state2.check={'p1' : 'F', 'p2' : 'F'}
state2.holding = {r1 : set()}


goal2 = hop.Goal('goal2')
goal2.pos = {'p1' : 'storage', 'p2' : 'storage'}
goal2.check = {'p1' : 'T', 'p2' : 'F'}

t = ('bring_package', 'p1', 'ext', 'storage')
res = hop.plan(state2,
        [('border_delivery', r1, goal2)],
        hop.get_operators(),
        hop.get_methods(),
        verbose=3
)
# res = hop.decompose(state2, t, hop.get_operators(), hop.get_methods(), 3)
# print(res)
# print_htn(res,0)