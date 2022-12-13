"""
File for auctions, probably just going to do it all
in one file
"""
from __future__ import print_function
from pyhop import hop
import copy
import pprint
from enum import Enum
from functools import reduce
import time
import random
import ma_methods
import ma_operators

import agent_methods
import agent_operators



class Type(Enum):
    AND = 1
    OR = 2

class Node():

    def __init__(self,name,task,tree_type):
        self.name = name
        self.task_name = task[0]
        self.task = task
        self.type = tree_type
        self.children = []
        self.owner = None
        self.cost = -1
        self.bought = False

def print_tree(root,tabs):

    if root == None:
        return

    print(tabs+"{}\t{}\t{}\t{}\t{}".format(root.name,root.task,root.type,root.cost,root.bought))
    # print(tabs+"{}\t{}".format(root.task,root.cost))
    for child in root.children:
        print_tree(child,tabs+"\t")

def copy_tree(root):

    new_root = Node(root.name, root.task, root.type)
    new_root.cost = root.cost
    new_root.bought = root.bought

    for child in root.children:
        new_child = copy_tree(child)
        new_root.children.append(new_child)

    return new_root

def decompose(root, state, methods,operators):

    if root == None:
        return


    if root.task_name in methods:
        # We can decompose
        relevant = methods[root.task_name]

        # Generate an OR denoting the higher level parent of the methods

        # Create a method to list or node
        for method in relevant:
            # Need to make sure method is not already included as decomp of root
            method_exists = None
            for child in root.children:
                if child.name == method.__name__:
                    method_exists = child

            if method_exists:
                # We may want to decompose child
                for child in method_exists.children:
                    decompose(child, state, methods, operators)
            else:
                method_node = Node(method.__name__,(method.__name__,None), Type.AND)   
                root.children.append(method_node)
                subtasks = method(state, *root.task[1:])
                if subtasks:
                    for task in subtasks:
                        child = Node(task[0],task,Type.OR)
                        decompose(child,state,methods,operators)
                        method_node.children.append(child)

    return

# 1. Generate auction
# 1.a. Build grounded HTN



# # To agents, we pass the grounded HTN, the current state, and goal

# # Agents take the current state and goal, and decompose it using their own methods.
# # They then take the HTN, and look at the labesl

# # 2. Generate bids
# # 2.a. agents use their local domains to further decompose HTN



# Now need to generate plan from decomposition --> Go through tree, assign costs?
def generate_plan(root, state, methods, operators, op_costs, bidders):

    if root == None or root.bought == True:
        return
    # If we are at a leaf, compute cost of action, return
    states = {}
    if root.task_name in operators:
        operator = operators[root.task_name]
        new_state = operator(state, *root.task[1:])
        if len(bidders) > 0 or new_state:
            if root.children:
                # There are bids that exist for this operator
                temp = sorted(root.children, key=lambda x:x.cost)
                bought = False
                resell_child = None
                best_child = None
                for child in temp:
                    if child.cost >= 0 and (best_child == None or child.cost < best_child.cost):
                        if child.task == "allocate":
                            if child.name in bidders:
                                best_child = child
                                bidders.remove(child.name)
                                bought = True
                        else:
                            resell_child = child
                            best_child = resell_child
                if bought:
                    root.children = [best_child]
                    root.bought = True
                    root.cost = best_child.cost
                else:
                    root.cost = resell_child.cost
            elif root.name in op_costs:
                root.cost = op_costs[root.name]
            else:
                root.cost = 1
        else:
            root.cost = -1
        return root.cost
    elif root.task_name in methods:
        # We can decompose
        relevant = methods[root.task_name]

        # Create a method to list or node
        costs = []
        for method in relevant:
            new_state = copy.deepcopy(state)
            # Need to make sure method is not already included as decomp of root
            method_node = None
            for child in root.children:
                if child.name == method.__name__:
                    method_node = child

            if method_node:
                # We may want to decompose child and generate a plan
                for child in method_node.children:
                    generate_plan(child, new_state, methods, operators, op_costs, bidders)
                    
            else:
                method_node = Node(method.__name__,(method.__name__,None), Type.AND)   
                root.children.append(method_node)
                subtasks = method(new_state, *root.task[1:])
                if subtasks:
                    for task in subtasks:
                        child = Node(task[0],task,Type.OR)
                        generate_plan(child,new_state,methods,operators, op_costs, bidders)
                        method_node.children.append(child)
            
            tot_cost = 0
            for child in method_node.children:
                if child.cost >= 0:
                    tot_cost += child.cost
                else:
                    tot_cost = -1
                    break
            method_node.cost = tot_cost
            states[method_node.name] = new_state
    # We are in the WDP, look at children, 
    best_cost = -1
    best_child = None

    temp = sorted(root.children, key=lambda x:x.cost)
    bought = False
    resell_child = None
    min_cost = temp[-1].cost
    for child in temp:
        if child.cost >= 0 and child.cost < min_cost:
            min_cost = child.cost
        if child.task == "resell":
            child.cost = min_cost+ 1


    for child in temp:
        if child.cost >= 0 and (root.cost < 0 or child.cost < root.cost):
            if child.task == "allocate":
                if child.name in bidders:
                    root.cost = child.cost
                    best_child = child
                    bidders.remove(child.name)
                    bought = True
            else:
                root.cost = child.cost
                best_child = child

    if len(bidders) > 0:
        if bought:
            root.children = [best_child]
            root.bought = True
        else:
            if best_child:
                root.cost = best_child.cost
    else:
        root.children = [best_child]
    new_state = states[best_child.name]
    for key in state.pos:
        state.pos[key] = new_state.pos[key]
    for key in state.holding:
        state.holding[key] = new_state.holding[key]
    for key in state.check:
        state.check[key] = new_state.check[key]

def gen_bids_help(root, d):
    if root == None:
        return

    if root.type == Type.OR:
        d[root.task] = root.cost
    
    for child in root.children:
        gen_bids_help(child,d)

def generate_bids(root):
    d = {}

    if root == None:
        return
    gen_bids_help(root, d)

    return d
 
# Now send tree back, want to plan using the new bids
def generate_allocate_tree(root, bids):
    
    if root == None:
        return

    if root.type == Type.OR:
        min_bid = 1000
        max_bid = -1000
        for bidder in bids:
            if root.task in bids[bidder]:
                child = Node(bidder,"allocate",Type.AND)
                child.cost = bids[bidder][root.task]
                if child.cost < min_bid:
                    min_bid = child.cost
                if child.cost > max_bid:
                    max_bid = child.cost
                root.children.append(child)
        min_bid += 1
        max_bid += 1
        child = Node("resell", "resell", Type.AND)
        child.cost = max_bid
        # if (random.randint(0,1) == 1): child.cost = max_bid
        root.children.append(child)

    for child in root.children:
        generate_allocate_tree(child,bids)

# Need to filter tree to get rid of nodes where we already allocated stuff
def filter_tree(root):
    

    if root == None:
        return False
    if root.bought:
        return True
    
    allocated_child = None
    allocated = True
    for child in root.children:
        status = filter_tree(child)
        if root.type == Type.AND:
            root.bought = True
            if not status:
                # child not bought, but if we look through it might be, so recurse
                root.bought = False
                return False
        else:
            if status:
                root.bought = True
                return True
    # if root.type == Type.AND:
    #     root.bought = True
    #     return True

    return root.bought


def solve_auction(root, state, methods, operators, op_costs, bidders):

    if root == None or root.bought == True:
        return
    # If we are at a leaf, compute cost of action, return

    # if root.children
    best_child = None
    for child in root.children:
        if root.type == Type.OR:
            # Want to choose best
            if child.bought and child.task != "resell" and child.task != "allocate":
                best_child = child
                break
            solve_auction(child, state, methods, operators, op_costs, bidders)
            

            if child.cost >= 0 and (best_child == None or child.cost < best_child.cost):
                if child.task == "allocate":
                    if child.name in bidders:
                        best_child = child
                        # root.bought = True
                        # new_bidders.remove(child.name)
                        print("TASK {} BOUGHT BY {}".format(root.task,child.name))
                else:
                    best_child = child
                    # root.bought = False
            
    
        if root.type == Type.AND:
            solve_auction(child, state, methods, operators, op_costs, bidders)

            # if root.cost 
            # root.cost += child.cost

    if root.type == Type.OR and best_child != None:
        
        if best_child.task == "allocate":
            if best_child.name in bidders:
                bidders.remove(best_child.name)
            root.bought = True
        if best_child.task != "resell":
            root.children = [best_child]
            root.bought = True
        else:
            root.bought = False
        root.cost = best_child.cost
    if root.type == Type.AND:
        if not root.task == "resell":
            root.bought = True
        # root.cost = 0
        if root.children != []: root.cost= 0
        for child in root.children:
            root.cost += child.cost
            if not child.bought:
                root.bought = False
                root.cost = -1
                break
        



# Model setup
ma_m = ma_methods.get_methods()
ma_o = ma_operators.get_operators()

state1 = hop.State("state1")
state1.pos = {"p1":"ext","p2":"ext"}
state1.check = {"p1":False,"p2":False}

goal1 = hop.Goal("goal1")
goal1.pos = {"p1":"storage","p2":"storage"}
goal1.check = {"p1":True}

# Generalized state for use
sa_m = agent_methods.get_methods()
sa_o = agent_operators.get_operators()
state1.pos["r"] = "home"
state1.holding = {"r": set()}

# Timer
start_time = time.perf_counter()


# Initialize auction
print("\n------------------\n\tINITIALIZING AUCTION\n------------------\n")
root = Node("border_delivery_OR",("border_delivery",goal1),Type.OR)
decompose(root,state1,ma_m,ma_o)
print_tree(root,"")

# Generate bids for each agent
r1_op_costs = {
    "move_to" : 1,
    "pick_up" : 1,
    "pick_up_2" : 100,
    "drop" : 1,
    "check": 100
}
r2_op_costs = {
    "move_to" : 2,
    "pick_up" : 2,
    "pick_up_2" : 100,
    "drop" : 2,
    "check": 100
}
r3_op_costs = {
    "move_to" : 10,
    "pick_up" : 1,
    "pick_up_2" : 100,
    "drop" : 1,
    "check": 10
}

op_cost_pool = [r1_op_costs, r2_op_costs, r3_op_costs]
num_agents = 2
agents = set()
agent_op_costs = {}
for i in range(num_agents):
    agent = "r" + str(i)
    agents.add(agent)
    # agent_op_costs[agent] = {}
    # for key in op_cost_pool[0]:
    #     agent_op_costs[agent][key] = random.randint(1,1)
    agent_op_costs[agent] = op_cost_pool[i%len(op_cost_pool)]


print("\n------------------\n\tGENERATING BIDS\n------------------\n")

# agent_op_costs = {"r1": r1_op_costs, "r2": r2_op_costs, "r3": r3_op_costs}
bids = {}
for agent in agents:
    tree = copy_tree(root)
    
    generate_plan(tree, copy.deepcopy(state1), sa_m, sa_o, agent_op_costs[agent], set())
    bids[agent] = generate_bids(tree)
    print("Local plan for {}:".format(agent))
    print_tree(tree,"")
    # print("Bids for agent {}:".format(agent))
    # pprint.pprint(bids[agent])


print("\n--------\n")
bidders = set(agents)
bidders.add("placeholder")

op_costs = {}
for operator in ma_o:
    op_costs[operator] = 100000

print("\n------------------\n\tSOLVIN AUCTION\n------------------\n")
avg_rounds = 0
avg_cost = 0
num_rounds = 10
for i in range(num_rounds):
    new_root = copy_tree(root)
    generate_allocate_tree(new_root, bids)
    rounds = -1
    for i in range(20):
        bidders = set(agents)
        bidders.add("placeholder")
        # print_tree(root,"")
        auction_state = copy.deepcopy(state1)
        solve_auction(new_root, auction_state, ma_m, ma_o, op_costs, bidders)
        print("\n---------\n\tFIRST ROUND\n---------\n")
        print_tree(new_root,"")
        if new_root.bought == True:
            rounds = i+1
            avg_rounds += rounds
            avg_cost += new_root.cost
            break
        # temp = copy_tree(new_root)
        # filter_tree(temp)

        # if temp.bought == True:
        #     
    filter_tree(new_root)
    print_tree(new_root,"")
    print("ROUNDS: {}".format(i))
    elapsed_time = time.perf_counter() - start_time
    print(elapsed_time)
print("AVERAGE RUONDS: {}".format(avg_rounds/10))
print("AVERAGE COST: {}".format(avg_cost/10))