from util import distance, generate_rate, movement_prob, spawn, calculate_charge, custom_print
import numpy as np
import random

distance_dict = distance()
movement_probability_dict = movement_prob()
locations = [
    "college",
    "sub1",
    "sub2",
    "beach",
    "airport",
    "downtown"
]


class StrategyBidder:

    def __init__(self, id, initial_position="college", weight=0.3):
        # general utilities
        self.location = initial_position
        self.is_busy = False
        self.start_ride_time = 0
        self.current_ride_duration = 0
        self.next_location = initial_position
        self.id = id

        # personalized values
        self.personal_rate = generate_rate()  # rate per time step
        self.look_into_future_weight = weight

        # book keeping
        self.collected_money = 0
        self.time_worked = 0
        self.driver_type = "Strategy"

    def bid(self, customers, current_time):
        """
        What bid do you have on every customer?
        :param customers: list of Customer objects
        :return: list of tuples (customer, bid), where bid <= max_price is what you're willing
        to take on this customer.
        """
        if len(customers) == 0:
            self.assign_ride(current_time, ("downtown", 0))
            return []

        # get expected cost and charge for every location, then get
        # the expected utility from being there
        spawn_dict = spawn(current_time)
        expected_utility = dict()
        for cur_location in locations:
            expected_distance = np.sum([
                distance_dict[cur_location][potential_location] *
                movement_probability_dict[cur_location][potential_location]
                for potential_location in locations
            ])
            expected_cost = expected_distance * self.personal_rate
            expected_population = spawn_dict[cur_location]
            expected_charge = calculate_charge(expected_distance, expected_population)
            cur_expected_utility = (expected_cost + expected_charge)/2 - expected_cost
            expected_utility[cur_location] = cur_expected_utility

        bids = []
        for customer in customers:
            current_max_price = customer.max_price
            current_distance = distance_dict[customer.source][customer.destination]
            current_cost = current_distance * self.personal_rate
            current_base_bid = (current_cost + current_max_price)/2
            current_bid = current_base_bid - self.look_into_future_weight * expected_utility[customer.destination]
            bids.append((
                customer,
                current_bid
            ))
        return bids

    def get_status(self, t):
        """
        Return current status and location
        :t: current time step
        :return:
        """
        if not self.is_busy:
            return self.is_busy, self.location
        if t - self.start_ride_time >= self.current_ride_duration:
            self.location = self.next_location
            self.is_busy = False
            self.start_ride_time = 0
            self.current_ride_duration = 0
        return self.is_busy, self.location

    def assign_ride(self, t, assigned_ride):
        """
        :param t: Current time
        :param assigned_ride: tuple of (location, payment)
        :return: nothing
        """
        assert not self.is_busy
        self.is_busy = True
        self.start_ride_time = t
        self.next_location = assigned_ride[0]
        self.current_ride_duration = distance_dict[self.location][self.next_location]

        self.collected_money += assigned_ride[1]
        self.time_worked += self.current_ride_duration

def tests():
    b1 = StrategyBidder("college")
    b2 = StrategyBidder("college")
    customers = [
        ("downtown", 20),
        ("sub1", 30),
        ("airport", 40),
    ]
    all_bids = [
        b1.bid(customers),
        b2.bid(customers)
    ]
    print(all_bids)
    b1.assign_ride(0, ("downtown", 10))
    b2.assign_ride(0, ("sub1", 20))

    print(b1.get_status(5))
    print(b1.get_status(15))
    print(b1.get_status(25))

    print(b2.get_status(5))
    print(b2.get_status(15))
    print(b2.get_status(25))
