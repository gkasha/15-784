"""
Border Delivery local domain definition

"""
from pyhop import hop

# Action to move r from l1 to l2
def move_to(state, r, l1, l2):
    if (state.pos[r] == l1
        and l1 != l2):
        state.pos[r] = l2
        return state
    else:
        return False

# Action to pick up p with r
def pick_up(state, r, p, l):
    if (state.pos[r] == l
        and state.pos[p] == l
        and not p in state.holding[r]):
        state.holding[r].add(p)
        return state
    else:
        return False

def pick_up_2(state, r, p1, p2, l):
    if (state.pos[r] == l
        and state.pos[p1] == l
        and state.pos[p2] == l
        and (not p2 in state.holding[r])
        and (not p1 in state.holding[r])):
        state.holding[r].add(p1)
        state.holding[r].add(p2)
        return state
    else:
        print("PICK UP @ NOT SATISFIED")
        return False

# Action to drop p with r
def drop(state, r, p, l):
    if (state.pos[r] == l
        and p in state.holding[r]):
        state.holding[r].discard(p)
        state.pos[p] = l
        return state
    else:
        return False

def check(state, r, p):
    state.check[p] = True
    return state

hop.declare_operators(move_to, pick_up, drop)

def get_operators():
    d = {}
    operators = [move_to, pick_up, pick_up_2, drop, check]
    for op in operators:
        d[op.__name__] = op
    return d