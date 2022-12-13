"""
Border Delivery local methods
"""


def bring_package_m(state, r, p, l1, l2):
    res = []

    # Get robot to correct location
    if state.pos[r] != l1:
        res.append(('move_to', r, state.pos[r], l1))
    
    res += [('pick_up', r, p, l1), ('move_to', r ,l1 ,l2), ('drop', r, p, l2)]
    if l2 == "check":
        res.append(('check',r,p))
    return res


def bring_all_packages_m(state, r, p1, p2, l1, l2):
    res = []
    if state.pos[r] != l1:
        res.append(('move_to', r, state.pos[r], l1))
    
    res += [('pick_up_2', r, p1, p2, l1), ('move_to', r, l1, l2),
          ('drop', r, p1, l2), ('drop', r, p2, l2)]

    return res


def store_packages_one_m(state, r, p1, p2, l1, l2):
    res = []
    
    # Execute package delivery sequence
    res.append(('bring_package', r, p1, l1, l2))
    res.append(('bring_package', r, p2, l1, l2))

    return res

def store_packages_all_m(state, r, p1, p2, l1, l2):
    
    return [("bring_all_packages", r, p1, p2, l1 ,l2)]


def border_delivery_m(state, goal):
    return [('store_packages', "r", "p1", "p2", "l0", "l1"),
            ('store_packages', "r", "p1", "p2", "l1", "l2"),
            ('store_packages', "r", "p1", "p2", "l2", "l3"),
            ('store_packages', "r", "p1", "p2", "l3", "l4"),
            ('store_packages', "r", "p1", "p2", "l4", "l5")]

def get_methods():
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    d = {}
    d['bring_package'] = [bring_package_m]
    d['bring_all_packages'] = [bring_all_packages_m]
    d['store_packages'] = [store_packages_all_m, store_packages_one_m]
    d['border_delivery'] = [border_delivery_m]
    return d