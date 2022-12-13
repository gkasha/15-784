"""
Border Delivery methods
"""

def random_check_m(state, r, p):
    return [('bring_package', r, p, 'storage', 'check'), ('bring_package', r, p, 'check', 'storage')]

def store_packages_one_m(state, r, p1, p2, l1, l2):
    return [('bring_package', r, p1, l1, l2), ('bring_package', r, p2, l1, l2)]

def store_packages_all_m(state, r, p1, p2, l1, l2):
    return [('bring_all_packages', r, p1, p2, l1, l2)]

def border_delivery_m(state, goal):
    return [("store_packages", "r", "p1", "p2", "ext", "storage"), ("random_check", "r", "p1")]

def get_methods():
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    d = {}
    d['random_check'] = [random_check_m]
    d['store_packages'] = [store_packages_all_m, store_packages_one_m]
    d['border_delivery'] = [border_delivery_m]
    return d