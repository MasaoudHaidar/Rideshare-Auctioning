import random
from DummyBidder import DummyBidder
from StrategyBidder import StrategyBidder
from TruthfulBidder import TruthfulBidder
from util import Customer, custom_print, distance, generate_customers, calculate_charge
import numpy as np

distance_dict = distance()

strategy_drivers = True
end_of_week_time = 1008
number_of_drivers = 500
max_wait_time = 3
locations = [
    "college",
    "sub1",
    "sub2",
    "beach",
    "airport",
    "downtown"
]

def get_random_driver():
    x = random.randint(1, 3)
    if x == 1:
        return DummyBidder
    elif x == 2:
        return TruthfulBidder
    return StrategyBidder

def get_diverse_drivers():
    return {
        x: get_random_driver()(x, locations[x % len(locations)])
        for x in range(number_of_drivers)
    }

def get_strategy_drivers():
    possible_weights = [x/10 for x in range(10)]
    return {
        x: StrategyBidder(x,
                          locations[x % len(locations)],
                          possible_weights[x % len(possible_weights)])
        for x in range(number_of_drivers)
    }

def run():
    customers = []  # list of Customer objects
    drivers = None
    if strategy_drivers:
        drivers = get_strategy_drivers()
    else:
        drivers = get_diverse_drivers()
    revenue = 0
    customers_unsatisfied = 0
    customers_satisfied = 0
    customer_id_counter = 0

    for current_time in range(end_of_week_time):
        if current_time % 100 == 0:
            custom_print(("Step: ", current_time))

        custom_print(("current time:", current_time), True)

        # delete old customers and get the population to help with price determining
        current_population = {
            loc: 0 for loc in locations
        }
        current_customers = []
        for customer in customers:
            spawn_time = customer.spawn_time
            source = customer.source
            if current_time - spawn_time < max_wait_time:
                current_customers.append(customer)
                current_population[source] += 1
            else:
                customers_unsatisfied += 1
        customers = current_customers

        # generate new costumers
        new_customers = generate_customers(current_time)

        # add the new customers and determine their payments
        for source, destination in new_customers:
            customers.append(
                Customer(customer_id_counter,
                         source,
                         destination,
                         calculate_charge(distance_dict[source][destination], current_population[source]),
                         current_time)
            )
            customer_id_counter += 1
        custom_print(current_population, True)

        # collect customer data to be sent to bidders
        current_customers_per_location = {
            loc: [] for loc in locations
        }
        for customer in customers:
            current_customers_per_location[customer.source].append(customer)

        # Send data to customers and store their bids
        all_bids = {
            loc: [] for loc in locations
        }  # tuple of (driver id, driver's bids)

        all_bids_per_customer = {
            customer.id: [] for customer in customers
        }  # tuple of (bid_amount, driver_id)
        for driver in drivers.values():
            custom_print("Drivers:", True)
            is_busy, location = driver.get_status(current_time)
            custom_print((driver.id, driver.is_busy, driver.location), True)
            if is_busy:
                continue
            driver_bids = driver.bid(current_customers_per_location[location], current_time)
            all_bids[location].append((
                driver.id,
                driver_bids
            ))
            for (customer, bid_amount) in driver_bids:
                all_bids_per_customer[customer.id].append((
                    bid_amount,  # maybe add a random number in the middle?
                    driver.id
                ))
        custom_print(all_bids_per_customer, True)
        # determine the winners for every customer
        random.shuffle(customers)
        for customer in customers:
            customer_bids = all_bids_per_customer[customer.id]
            customer_bids.sort()
            for bid_amount, driver_id in customer_bids:
                if drivers[driver_id].is_busy:
                    continue
                drivers[driver_id].assign_ride(current_time, (customer.destination, bid_amount))
                custom_print((driver_id, customer.destination), True)
                revenue += customer.max_price - bid_amount
                customer.is_picked = True
                customers_satisfied += 1
                break

        # delete old customers
        current_customers = []
        for customer in customers:
            if not customer.is_picked:
                current_customers.append(customer)
        customers = current_customers

        custom_print(len(customers), True)

    custom_print("Mean driver results:")
    for driver_type in ["Dummy", "Truthful", "Strategy"]:
        current_money_made = [driver.collected_money for driver in drivers.values() if
                              driver.driver_type == driver_type]
        current_time_worked = [driver.time_worked for driver in drivers.values() if
                              driver.driver_type == driver_type]
        if len(current_money_made) == 0:
            continue
        custom_print((driver_type, "Mean Money Made", np.mean(current_money_made)))
        custom_print((driver_type, "Mean Time worked", np.mean(current_time_worked)))
        custom_print((driver_type, "Mean Rate", np.mean(current_money_made) / np.mean(current_time_worked)))
    if strategy_drivers:
        for x in range(10):
            weight = x/10
            current_money_made = [driver.collected_money for driver in drivers.values() if
                                  driver.look_into_future_weight == weight]
            current_time_worked = [driver.time_worked for driver in drivers.values() if
                                   driver.look_into_future_weight == weight]
            if len(current_money_made) == 0:
                continue
            custom_print((weight, "Mean Money Made", np.mean(current_money_made)))
            custom_print((weight, "Mean Time worked", np.mean(current_time_worked)))
            custom_print((weight, "Mean Rate", np.mean(current_money_made) / np.mean(current_time_worked)))
    custom_print(("revenue:", revenue))
    custom_print(("customers satisfies:", customers_satisfied))
    custom_print(("customers unsatisfies:", customers_unsatisfied))
run()
