# method that will round a number to two decimal places correctly
# I observed that pythons round function always would round down ie 0.125 to 0.12
def round_correct(num, ndigits=0):
    if ndigits == 0:
        return int(num + 0.5)
    else:
        digit_value = 10 ** ndigits
        return int(num * digit_value + 0.5) / digit_value


# the instantiation of an Order class will be the encapsulation of a single limit order
class Order:
    def __init__(self, ticker, current_price, percentage):
        self.ticker = ticker
        self.current_price = current_price
        # note that I compute the price of the order before storing the percentage because the percentage
        # may not be exact due to rounding
        self.price = round_correct((current_price * (1 + percentage)), 2)
        # note that I round the percentage to 4 decimal places because the percentage that corresponds
        # to the decimal value I am storing in percentage is then rounded to 2 decimal places
        self.percentage = round_correct((self.price / self.current_price)-1, 4)
        self.num_shares = 0
        self.total_cost = 0

    # compute the number of shares that are to be purchased at the current price
    # in order to have the dollar_amount purchased that the user desires
    def compute_num_shares(self, dollar_amount):
        self.num_shares = round_correct(float(dollar_amount / self.price), 3)
        self.total_cost = self.num_shares * self.price
        return self.num_shares

    def print_order(self):
        print("Limit order:", self.ticker, self.num_shares,
              "shares x $" + str(self.price), "= $" + str(self.total_cost), "%" + str(self.percentage * 100))