"""
File for auctions, probably just going to do it all
in one file
"""
from __future__ import print_function
from pyhop import hop
import copy
import pprint


import ma_methods
import ma_operators

import agent_methods
import agent_operators

# Model setup
ma_m = ma_methods.get_methods()
ma_o = ma_operators.get_operators()

state1 = hop.State("state1")
state1.pos = {"p1":"ext","p2":"ext"}
state1.check = {"p1":False,"p2":False}

goal1 = hop.Goal("goal1")
goal1.pos = {"p1":"storage","p2":"storage"}
goal1.check = {"p1":True}

def ma_border_delivery_m(state, goal):
    return [("store_packages", "r", "p1", "p2", "ext", "storage"), ("random_check", "r", "p1")]
ma_m["border_delivery"] = [ma_border_delivery_m]


# print(ops)
# print(methods)

# x = methods["store_packages"][0]

# print(x(state1,"p1","p2","ext","storage"))
# hop.plan(state1,[("border_delivery",goal1)],ops,methods,verbose=2)

# 1. Generate auction
# 1.a. Build grounded HTN
# 1.b. Send out HTN

H = {}
label_counter = 0

def construct_h(state, tasks, operators, methods):
    global label_counter
    res = []
                
    for task in tasks:
        d = {}

        if task[0] in operators:
            d[task] = []
        else:
            key = task
            d[key] = []
            relevant = methods[task[0]]
            for method in relevant:
                temp = {}
                subtasks = method(state, *task[1:])
                if subtasks:
                    temp[method.__name__] = build_h(state, subtasks, operators, methods)
                d[key].append(temp)
        res.append(d)
           
    return res
def build_h(state, tasks,operators,methods):
    global label_counter

    H = construct_h(state, tasks, operators, methods)
    # frontier = H
    # while frontier:
    #     new_frontier = []
    #     for node in frontier:
    #         new_d = {}
    #         for key in node:
    #             temp = node[key]
    #             new_key = (label_counter,key)
    #             label_counter += 1
    #             new_d[new_key] = temp
    #             new_frontier += new_d[new_key]
            

    #     frontier = new_frontier

    return H
    

def print_h(H, depth):

    for node in H:
        tabs = ""
        for i in range(depth):
            tabs += "\t"
        for key in node:
            print(tabs + "{}".format(key))
            print_h(node[key],depth+1)


H = build_h(state1, [("border_delivery",goal1)], ma_o, ma_m)
print(H)
print_h(H,0)

# To agents, we pass the grounded HTN, the current state, and goal

# Agents take the current state and goal, and decompose it using their own methods.
# They then take the HTN, and look at the labesl

# 2. Generate bids
# 2.a. agents use their local domains to further decompose HTN
r = "r"
p1 = "p1"
p2 = "p2"
def sa_border_delivery_m(state, goal):
    return [('store_packages', r, p1, p2, "ext", "storage"), ('random_check', r, p1)]
sa_m = agent_methods.get_methods()
sa_o = agent_operators.get_operators()
sa_m["border_delivery"] = [sa_border_delivery_m]
state1.pos[r] = "home"
state1.holding = {r: set()}
label_counter = 0
hop.plan(state1, [('border_delivery',goal1)], sa_o, sa_m, verbose=2)
loc_H = build_h(state1, [('border_delivery',goal1)], sa_o, sa_m)
print(loc_H)
print_h(loc_H,0)

def generate_plan(state, tasks, operators, methods):
    MaxVal = 1000
    if tasks == []:
        return [0,[]]
    
    tot_cost = 0
    plan = {}
    # These are things that we need to execute
    for task in tasks:
        if task[0] in operators:
            # base case
            new_state = operators[task[0]](state, *task[1:])
            if new_state:
                state = new_state
                plan[task] = [1,[]]
                tot_cost += 1
            else:
                plan[task] = [MaxVal, []]
                tot_cost += MaxVal
        else:
            relevant = methods[task[0]]
            best_cost,best_plan,best_state = MaxVal,None,None
            for method in relevant:
                temp_state = copy.deepcopy(state)
                subtasks = method(temp_state, *task[1:])
                if subtasks:
                    res = generate_plan(temp_state, subtasks, operators, methods)
                    if res[0] < best_cost:
                        best_cost = res[0]
                        best_plan = res[1]
                        best_state = res[2]
            plan[task] = [best_cost,best_plan]
            state = best_state
            tot_cost += best_cost

    return [tot_cost, plan, state]


        # If these are operators, then need to do them all
        # If these are methods, then need to 

print("-----------")
plan = generate_plan(copy.deepcopy(state1),[('border_delivery',goal1)],sa_o,sa_m)
print(plan)

# Now, want to generate bids based on this plan --> go through tree, make a bid for a particular item

def gen_bids_helper(res,plan):
    d = plan[1]
    for key in d:
        res[key] = d[key][0]
        gen_bids_helper(res,d[key])
def generate_bids(plan):

    res = {}
    gen_bids_helper(res,plan)
    return res
print("------")
# print(generate_bids(plan))
bids = {"r1": generate_bids(plan)}

bids["r2"] = {('bring_package', 'r', 'p1', 'storage', 'check') : 1}

# Now, try to decompose HTN again, but now use bids
def decompose_with_bids(state, tasks, operators, methods, bids, winners, allocated):
    print("WDAdwdawadawdawdaw")
    if tasks == []:
        return [0,[]]
    
    tot_cost = 0
    plan = {}
    # These are things that we need to execute
    for task in tasks:
        # if task in allocated:
        #     plan[task] = allocated[task][1:3]
        #     state = allocated[task][3]
        #     tot_cost += allocated[task][1]
        #     continue
        if task[0] in operators:
            # base case
            new_state = operators[task[0]](state, *task[1:])
            if new_state:
                state = new_state
                # Choose bid
                
                bid = 1000
                bid_winner = "NONE"
                for agent in bids:
                    if not agent in winners:
                        print("BID FROM {}".format(agent))
                        if task in bids[agent]:
                            if bids[agent][task] < bid:
                                bid = bids[agent][task]
                                bid_winner = agent

                print("------\nBest bid for {} is from {} = {}".format(task,bid_winner,bid))
                plan[task] = [bid, bid_winner]
                if bid_winner != "NONE":
                    allocated[task] = [bid_winner,bid,[],state]
                    winners.add(bid_winner)
                tot_cost += bid
            else:
                plan[task] = [1000, []]
                tot_cost += 1000
                print("NO VALUE")
        else:
            relevant = methods[task[0]]
            best_cost,best_plan,best_state = 1000,None,None
            for method in relevant:
                temp_state = copy.deepcopy(state)
                subtasks = method(temp_state, *task[1:])
                if subtasks:
                    res = decompose_with_bids(temp_state, subtasks, operators, methods,bids, winners, allocated)
                    if best_plan == None or res[0] < best_cost:
                        best_cost = res[0]
                        best_plan = res[1]
                        best_state = res[2]

            bid = 1000
            bid_winner = best_plan
            for agent in bids:
                if not agent in winners:
                    if task in bids[agent]:
                        if bids[agent][task] < bid:
                            bid = bids[agent][task]
                            bid_winner = agent

            if bid_winner != best_plan and bid <= best_cost:
                best_cost = bid
                best_plan = bid_winner
                winners.add(bid_winner)
            plan[task] = [best_cost,best_plan]
            state = best_state
            tot_cost += best_cost

    print("TOT COST FOR {} IS {}".format(tasks, tot_cost))
    return [tot_cost, plan, state]

print("=======BIDS=======")
print(bids)
print("\nDecomposing with bids\n")
allocated = {}
winners = set()
dec_bids = decompose_with_bids(copy.deepcopy(state1),[('border_delivery', goal1)], ma_o, ma_m,bids, winners, allocated)
print("--------------")
pprint.pprint(dec_bids)