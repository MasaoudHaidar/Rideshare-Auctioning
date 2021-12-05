import random
from DummyBidder import DummyBidder

"""
 - Every step:
      - delete old customers and mark them (after some time steps)
      - generate new customers
      - for every node, collect all customers, call the bidder function from every bidder in the node and collect the bids
      - determine the winner of every customer,
        update the revenue, location, and money for every driver.
        (Location and money should be updated by calling the bidder)
"""

end_of_week_time = 10
max_wait_time = 6
locations = [
    "college",
    "sub1",
    "sub2",
    "beach",
    "airport",
    "downtown"
]

debug_mode = True


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


def get_drivers():
    return {
        0: DummyBidder(0, "college"),
        1: DummyBidder(1, "sub1")
    }


def run():
    customers = []  # list of Customer objects
    drivers = get_drivers()
    revenue = 0
    customer_id_counter = 0

    for current_time in range(end_of_week_time):

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
        customers = current_customers

        # generate new costumers
        # edit based on utils
        new_customers = [
            ("sub1", "sub2"),
            ("sub2", "college"),
            ("college", "sub1"),
        ]

        # add the new customers and determine their payments
        for source, destination in new_customers:
            customers.append(
                Customer(customer_id_counter,
                         source,
                         destination,
                         2 + current_population[source],  # should be distance*constant, edit based on utils
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
            driver_bids = driver.bid(current_customers_per_location[location])
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
                break

        # delete old customers
        current_customers = []
        for customer in customers:
            if not customer.is_picked:
                current_customers.append(customer)
        customers = current_customers

        custom_print((revenue), True)


run()
