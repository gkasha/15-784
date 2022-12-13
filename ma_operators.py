"""
Border Delivery global domain definition

"""
from pyhop import hop


"""
Action to bring package at loc1 to loc2
"""

def bring_package(state, r, p, l1, l2):
    if (state.pos[p] == l1
        and l1 != l2):
        state.pos[p] = l2
        return state
    else:
        return False
    
"""
Action to bring both packages from loc1 to loc2
"""
def bring_all_packages(state, r, p1, p2, l1, l2):
    if (state.pos[p1] == l1
        and state.pos[p2] == l1
        and l1 != l2):
        state.pos[p1] = l2
        state.pos[p2] = l2
        return state
    else:
        return False

"""
Operators
"""
hop.declare_operators(bring_package, bring_all_packages)

def get_operators():
    d = {}
    d["bring_package"] = bring_package
    d["bring_all_packages"] = bring_all_packages
    return d