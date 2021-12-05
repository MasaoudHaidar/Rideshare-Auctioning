#!/usr/bin/env python

import random

from gsp import GSP

class VCG:
    """
    Implements the Vickrey-Clarke-Groves mechanism for ad auctions.
    """
    @staticmethod
    def compute(slot_clicks, reserve, bids):
        """
        Given info about the setting (clicks for each slot, and reserve price),
        and bids (list of (id, bid) tuples), compute the following:
          allocation:  list of the occupant in each slot
              len(allocation) = min(len(bids), len(slot_clicks))
          per_click_payments: list of payments for each slot
              len(per_click_payments) = len(allocation)

        If any bids are below the reserve price, they are ignored.

        Returns a pair of lists (allocation, per_click_payments):
         - allocation is a list of the ids of the bidders in each slot
            (in order)
         - per_click_payments is the corresponding payments.
        """

        # The allocation is the same as GSP, so we filled that in for you...

        valid = lambda a_bid: a_bid[1] >= reserve
        valid_bids = list(filter(valid, bids))

        # shuffle first to make sure we don't have any bias for lower or
        # higher ids
        random.shuffle(valid_bids)
        valid_bids.sort(key=lambda b: b[1], reverse=True)

        num_slots = len(slot_clicks)
        allocated_bids = valid_bids[:num_slots]
        if len(allocated_bids) == 0:
            return [], []

        (allocation, just_bids) = list(zip(*allocated_bids))

        # TODO: You just have to implement this function
        def total_payment(k):
            """
            Total payment for a bidder in slot k.
            """
            n = len(allocation)

            # last bidder:
            last_bidder = reserve * slot_clicks[n-1]
            if len(valid_bids) >= n + 1:
                last_bidder = max(reserve, valid_bids[n][1]) * slot_clicks[n-1]
            if k == n - 1:
                return last_bidder

            previous_bidder = last_bidder
            previous_bidder_slot = n - 1
            while previous_bidder_slot >= 0:
                next_bidder_slot = previous_bidder_slot - 1
                next_bidder = (slot_clicks[previous_bidder_slot - 1] -
                               slot_clicks[previous_bidder_slot]) * \
                              valid_bids[previous_bidder_slot][1] + \
                              previous_bidder
                if next_bidder_slot == k:
                    return next_bidder
                previous_bidder = next_bidder
                previous_bidder_slot = next_bidder_slot
            # should never get here
            raise

        def norm(totals):
            """Normalize total payments by the clicks in each slot"""
            return [x_y[0]/x_y[1] for x_y in zip(totals, slot_clicks)]
        per_click_payments = norm([total_payment(k) for k in range(len(allocation))])
        return list(allocation), per_click_payments

    @staticmethod
    def bid_range_for_slot(slot, slot_clicks, reserve, bids):
        """
        Compute the range of bids that would result in the bidder ending up
        in slot, given that the other bidders submit bidders.
        Returns a tuple (min_bid, max_bid).
        If slot == 0, returns None for max_bid, since it's not well defined.
        """
        # Conveniently enough, bid ranges are the same for GSP and VCG:
        return GSP.bid_range_for_slot(slot, slot_clicks, reserve, bids)
