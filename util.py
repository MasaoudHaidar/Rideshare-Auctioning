import math
import random
from itertools import *
import numpy as np

# argmax from
# http://stackoverflow.com/questions/5098580/implementing-argmax-in-python

# TIME STEPS:
# M-F: [0,720)
# Sat-Sun: [720,1008)
# {"college": {}, "downtown": {}, "airport": {}, "sub1": {}, "sub2": {}, "beach": {}}
locations = ["college", "downtown", "airport", "sub1", "sub2", "beach"]
dist_dict = {"college": {"college": 0, "downtown": 1, "airport": 3, "beach": 5, "sub1": 3, "sub2": 5}, 
             "downtown": {"college": 1, "downtown": 0, "airport": 3, "beach": 5, "sub1": 2, "sub2": 4},
             "airport": {"college": 3, "downtown": 3, "airport": 0, "beach": 8, "sub1": 3, "sub2": 7},
             "sub1": {"college": 3, "downtown": 2, "airport": 3, "beach": 7, "sub1": 0, "sub2": 4}, 
             "sub2": {"college": 5, "downtown": 4, "airport": 7, "beach": 3, "sub1": 4, "sub2": 0},
             "beach": {"college": 5, "downtown": 5, "airport": 8, "beach": 0, "sub1": 7, "sub2": 3}}
        
# the mean for the normal distribution that # customers is drawn from, from 0 to 50
spawn_dict = {"weekday": [{"college": 8, "downtown": 8, "airport": 8, "sub1": 0, "sub2": 0, "beach": 0},  # 12-3a
                          {"college": 2, "downtown": 2, "airport": 5, "sub1": 0, "sub2": 0, "beach": 0},  # 3-8a
                          {"college": 8, "downtown": 2, "airport": 8, "sub1": 40, "sub2": 30, "beach": 0},  # 8-9a
                          {"college": 8, "downtown": 8, "airport": 8, "sub1": 3, "sub2": 3, "beach": 0},  # 9-12p
                          {"college": 15, "downtown": 40, "airport": 8, "sub1": 3, "sub2": 3, "beach": 0},  # 12-1p
                          {"college": 8, "downtown": 8, "airport": 10, "sub1": 3, "sub2": 3, "beach": 0},  # 1-5p
                          {"college": 8, "downtown": 60, "airport": 8, "sub1": 3, "sub2": 3, "beach": 0},  # 5-6p
                          {"college": 20, "downtown": 10, "airport": 8, "sub1": 10, "sub2": 5, "beach": 3},  # 6-9p
                          {"college": 8, "downtown": 15, "airport": 8, "sub1": 2, "sub2": 2, "beach": 0}], # 9-12a
              "weekend": [{"college": 10, "downtown": 35, "airport": 10, "sub1": 0, "sub2": 0, "beach": 5},  # 12-3a
                          {"college": 0, "downtown": 10, "airport": 10, "sub1": 0, "sub2": 0, "beach": 0},  # 3-8a
                          {"college": 0, "downtown": 10, "airport": 20, "sub1": 3, "sub2": 3, "beach": 0},  # 8-9a
                          {"college": 10, "downtown": 10, "airport": 20, "sub1": 8, "sub2": 8, "beach": 10},  # 9-12p
                          {"college": 20, "downtown": 10, "airport": 20, "sub1": 15, "sub2": 10, "beach": 10},  # 12-1p
                          {"college": 15, "downtown": 30, "airport": 20, "sub1": 8, "sub2": 8, "beach": 10},  # 1-5p
                          {"college": 15, "downtown": 10, "airport": 20, "sub1": 10, "sub2": 8, "beach": 20},  # 5-6p
                          {"college": 20, "downtown": 35, "airport": 20, "sub1": 20, "sub2": 13, "beach": 20},  # 6-9p
                          {"college": 30, "downtown": 35, "airport": 20, "sub1": 25, "sub2": 3, "beach": 10}]} # 9-12a

# NOTE: for simplicity, we made this time independent, even though that is not realistic
movement_dict = {"college": {"college": .1, "downtown": .3, "airport": .1, "beach": .2, "sub1": .2, "sub2": .1}, 
             "downtown": {"college": .3, "downtown": .2, "airport": 0, "beach": .05, "sub1": .25, "sub2": .2},
             "airport": {"college": .35, "downtown": 0, "airport": 0, "beach": 0, "sub1": .35, "sub2": .3},
             "sub1": {"college": .2, "downtown": .4, "airport": .2, "beach": .1, "sub1": 0, "sub2": .1}, 
             "sub2": {"college": 0, "downtown": .5, "airport": .2, "beach": .2, "sub1": .1, "sub2": 0},
             "beach": {"college": .25, "downtown": .2, "airport": 0, "beach": 0, "sub1": .25, "sub2": .3}}


# takes a time step between 0 and 1008 (6*24*7) and returns (weekday/weekend, index in list)
def find_time(step):
    is_weekday = True if 0 <= step < 720 else False
    step_of_day = step % 144 # 144 is the number of 10 minute steps in a day
    if 0 <= step_of_day < 18: # 12-3a
        index = 0
    elif step_of_day < 48: # 3-8a
        index = 1
    elif step_of_day < 54: # 8-9a
        index = 2
    elif step_of_day < 72: # 9-12p
        index = 3
    elif step_of_day < 78: # 12-1p
        index = 4
    elif step_of_day < 102: # 1-5p
        index = 5
    elif step_of_day < 108: # 5-6p
        index = 6
    elif step_of_day < 126: # 6-9p
        index = 7
    else:                   # 9-12a
        index = 8

    if is_weekday:
        return ("weekday", index)
    else: 
        return ("weekend", index)

# returns distances between map locations
def distance():
    return dist_dict

# given a timestep, returns the spawn rate of map locations
def spawn(step):
    key, index = find_time(step)
    return movement_dict[key][index] 

# given a timestep, returns the movement probability between map locations
def movement_prob(dest):
    return movement_dict[dest]

def generate_customers(step):
    customers = []
    key, i = find_time(step) #weekend/weekday, index

    for location in locations:
        num_customers = max(0,round(random.normalvariate(spawn_dict[key][i][location], 1.0)))
        dest_prob = list(movement_dict[location].values())
        dests = list(movement_dict[location].keys())

        samples = np.random.multinomial(num_customers, dest_prob).tolist()
        
        for index in range(len(samples)):
            new_customers = [(location, dests[index])] * samples[index]
            customers = customers + new_customers
    
    return customers


def custom_print(tt, is_debug_print=False):
    # if it is a debug mode, print everything, else, only
    # print non-debug outputs
    if debug_mode:
        print(tt)
    elif not is_debug_print:
        print(tt)


class Customer:
    def __init__(self, id, source, destination, max_price, spawn_time):
        self.id = id
        self.source = source
        self.destination = destination
        self.max_price = max_price
        self.spawn_time = spawn_time
        self.is_picked = False

if __name__ == '__main__':
    generate_customers(136) # weekday, index 8

# given an iterable of pairs return the key corresponding to the greatest value
def argmax(pairs):
    return max(pairs, key=lambda a_b: a_b[1])[0]

# given an iterable of values return the index of the greatest value
def argmax_index(values):
    return argmax(zip(count(), values))

# given an iterable of keys and a function f, return the key with largest f(*key)
def argmax_f(keys, func):
    return max(map(lambda key: (func(*key), key), keys))[1]


def shuffled(l):
    x = l[:]
    random.shuffle(x)
    return x


def mean(lst):
    """Throws a div by zero exception if list is empty"""
    return sum(lst) / float(len(lst))

def stddev(lst):
    if len(lst) == 0:
        return 0
    m = mean(lst)
    return math.sqrt(sum((x-m)*(x-m) for x in lst) / len(lst))