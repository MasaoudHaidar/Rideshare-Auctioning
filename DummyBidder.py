

class Bidder:

    def __init__(self, initial_position = "college"):
        self.location = initial_position
        self.is_busy = False
        self.start_ride_time = 0
        self.current_ride_duration = 0
        self.next_location = initial_position

        self.collected_money = 0

    def bid(self, customers):
        """
        What bid do you have on every customer?
        :param customers: list of tuples (destination, max_price)
        :return: list of tuples (distance, max_price, bid), where bid = -1
        if you don't want this ride, and bid <= max_price is what you're willing
        to take on this customer
        """
        bids = []
        for customer in customers:
            bids.append((customer[0], customer[1], customer[1]//2))
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
        self.current_ride_duration = assigned_ride[1]  # change that based on utils
        self.next_location = assigned_ride[0]

        self.collected_money += assigned_ride[1]

def tests():
    b1 = Bidder("college")
    b2 = Bidder("college")
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

tests()