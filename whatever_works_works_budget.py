#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index

import math

def get_position_effect(t, j):
    """
    Return the pos_j at time t
    """
    # get the cost and round it
    base_c_1 = 30 * math.cos(math.pi * t / 24) + 50
    c_1 = int(base_c_1 + 0.5)
    if j == 0:
        return c_1
    base_c_j = (0.75 ** j) * c_1
    c_j = int(base_c_j + 0.5)
    return c_j

class whatever_works_works_budget:
    """tournament agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

        self.total_clicks_left = None
        self.total_clicks_used = None

    def initial_bid(self, reserve):
        return self.value / 2

    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks

        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        # get the info on the slots
        info = self.slot_info(t, history, reserve)

        # calculate the utilities
        utilities = []
        for (slot, min_price, _) in info:
            pos_effect = get_position_effect(t - 1, slot)
            u = pos_effect * (self.value - min_price)
            utilities.append(u)
        return utilities

    def bid(self, t, history, reserve):

        # TODO: Fill this in.

        # pre calculate how many clicks every slot have left after every round:
        if t == 1:
            total_rounds = 48
            total_clicks_left = [[0] * len(history.round(0).occupants) for _ in range(total_rounds)]
            i = total_rounds - 1
            while i >= 0:
                for slot in range(len(total_clicks_left[i])):
                    if i == total_rounds - 1:
                        total_clicks_left[i][slot] = get_position_effect(i, slot)
                    else:
                        total_clicks_left[i][slot] = total_clicks_left[i + 1][slot] + get_position_effect(i, slot)
                i -= 1
            self.total_clicks_left = total_clicks_left

        # find candidate slots
        slot_info = self.slot_info(t, history, reserve)
        slot_expected_utils = self.expected_utils(t, history, reserve)

        slot_expected_total_utility = []
        for i in range(len(slot_info)):
            slot_id, mn, _ = slot_info[i]
            expected_u = slot_expected_utils[i]

            # assume you can bid this until the day ends, What's the utility?
            expected_u_per_click = (expected_u / get_position_effect(t - 1, slot_id))
            if t < len(self.total_clicks_left):
                utility_till_end = expected_u_per_click * self.total_clicks_left[t][slot_id]
            else:
                # in this case, the code is being run on a number of rounds higher than 48, there is
                # no way to estimate how much time is left
                utility_till_end = math.inf

            # assume you can bid this until the budget ends, What's the utility?
            budget_left = self.budget - history.agents_spent[self.id]
            total_affordable_clicks = budget_left / mn
            utility_till_bankrupt = total_affordable_clicks * expected_u_per_click

            # what's the expected total utility?
            current_expected_total_utility = min(utility_till_bankrupt, utility_till_end)
            slot_expected_total_utility.append(current_expected_total_utility)

        target_slot = argmax_index(slot_expected_total_utility)
        _, mn, mx = slot_info[target_slot]
        md = round((mn + mx) / 2)
        bid = min(md, self.value)
        
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


