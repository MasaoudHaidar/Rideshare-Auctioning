from util import distance

distance_dict = distance()

class DummyBidder:

    def __init__(self, id, initial_position = "college"):
        self.location = initial_position
        self.is_busy = False
        self.start_ride_time = 0
        self.current_ride_duration = 0
        self.next_location = initial_position
        self.id = id

        self.collected_money = 0

    def bid(self, customers):
        """
        What bid do you have on every customer?
        :param customers: list of Customer objects
        :return: list of tuples (customer, bid), where bid = -1
        if you don't want this ride, and bid <= max_price is what you're willing
        to take on this customer. Must have the same length as the passed in customers
        """
        bids = []
        for customer in customers:
            bids.append((customer, customer.max_price//2))
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
        self.is_busy = True
        self.start_ride_time = t
        self.next_location = assigned_ride[0]
        self.current_ride_duration = distance_dict[self.location][self.next_location]

        self.collected_money += assigned_ride[1]

def tests():
    b1 = DummyBidder("college")
    b2 = DummyBidder("college")
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
