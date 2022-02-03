import yfinance as yf


# storing all the stock price info in a stock_price object
class StockPrice:
    def __init__(self, symbol, cost_basis_db=-1):
        self.stock_info = yf.Ticker(symbol).info
        self.symbol = symbol
        self.name = self.stock_info['shortName']
        self.prices = {'latest_price': self.stock_info['regularMarketPrice'],
                       'previous_close': self.stock_info['previousClose'],
                       'pre_market': self.stock_info['preMarketPrice']}

        if cost_basis_db != -1:
            if cost_basis_db is not None:
                self.cost_basis_exists = True
                self.prices['cost_basis'] = cost_basis_db
            else:
                self.cost_basis_exists = False

        else:
            while True:
                cost_basis = input("Enter cost basis per share for this stock. If none exists enter \'none\' : $")
                if cost_basis == 'none':
                    self.cost_basis_exists = False
                    break
                try:
                    cost_basis = float(cost_basis)
                    self.prices['cost_basis'] = cost_basis
                    self.cost_basis_exists = True
                    break
                except ValueError:
                    print("Invalid Input! Must be \'none\' or the cost basis")
