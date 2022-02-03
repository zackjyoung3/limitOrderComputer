from Order import Order
from StockPrice import StockPrice
import sqlite3
import os.path
from os import path
from datetime import date


# method that will convert a list of StockPrice objects into the form for them to be added to the sqlite db
def stocks_to_values(stock_list):
    records = []
    for stock in stock_list:
        if stock.cost_basis_exists:
            records.append((str(date.today()), stock.symbol, stock.prices['cost_basis']))
        else:
            records.append((str(date.today()), stock.symbol, None))
    return records


# method that will create an  sqlite3 db
def create_db():
    con = sqlite3.connect('stock.db')
    cur = con.cursor()

    # create the table for the stocks
    # note that I only have columns for cost_basis as the other prices will be determined
    # at run time using yfinance
    cur.execute('''CREATE TABLE stocks
                   (date text, ticker text, cost_basis real)''')

    stocks_to_add = {}
    first = True
    # prompt the user to enter any stocks that they desire to have in the db
    while True:
        while True:
            if first:
                add_stock = input("Would you like to add any stocks to the database? (yes/no):")
                first = False
            else:
                add_stock = input("Would you like to add another stocks to the database? (yes/no):")
            if add_stock == "yes" or add_stock == "no":
                break
            print("Answer must be \'yes\' or \'no\'")
        if add_stock == "no":
            break
        temp_stock = get_stock()
        stocks_to_add[temp_stock.symbol] = temp_stock

    records = stocks_to_values(list(stocks_to_add.values()))

    cur.executemany('INSERT INTO stocks VALUES(?,?,?);', records)

    # commit the changes to db
    con.commit()

    # close the connection
    con.close()

    # return the dictionary that will permit O(1) lookup based on stock ticker
    return stocks_to_add


# method that will load the stocks that are stored in the db into a dictionary
def load_db():
    con = sqlite3.connect('stock.db')
    cur = con.cursor()

    # dictionary that will hold all of the stocks from the db
    stocks_dict = {}
    for row in cur.execute('SELECT * FROM stocks ORDER BY ticker ASC'):
        temp_stock = load_stock(row[1], row[1])
        stocks_dict[temp_stock.symbol] = temp_stock

    # close the connection
    con.close()

    # return the dictionary that will permit O(1) lookup based on stock ticker
    print(stocks_dict)
    return stocks_dict


# method that will get the stock that the user wishes to trade
def get_stock_db():
    symbol = input("Enter the name of the stock you wish to add to the db: ")
    return StockPrice(symbol)


# method that will get the stock that the user wishes to trade
def get_stock():
    symbol = input("Enter the name of the stock whose prices you wish to be displayed: ")
    return StockPrice(symbol)


# method that will load a stock
def load_stock(ticker, cost_basis):
    return StockPrice(ticker, cost_basis)


# prompt the user to specify the prices that they wish to trade off of from the options that exist for that stock
def get_prices(stock):
    while True:
        times = ["latest_price", "previous_close", "pre_market"]
        print("Please enter the case or cases that you wish to view in display from the following...")
        if stock.cost_basis_exists:
            times.append("cost_basis")
        for time in times:
            print(time)
        time_frames = input("Enter a single option or comma separated list:")
        time_frame_list = time_frames.split(',')

        # correctly format the inputted strings removing blanks
        i = 0
        while i < len(time_frame_list):
            time_frame_list[i] = time_frame_list[i].lstrip(' ')
            time_frame_list[i] = time_frame_list[i].rstrip(' ')
            i += 1

        not_found = False
        for time_frame in time_frame_list:
            if not (time_frame in times):
                print("\n\nInvalid Input! The time frame must be entered exactly as displayed "
                      "and multiple inputs must be separated by commas")
                not_found = True
                break

        # if one of the user entered time frames was invalid prompt for time frames until valid
        if not_found:
            continue
        # otherwise break because all user inputted values are valid
        break

    print()
    print(str(stock.name) + "(" + str(stock.symbol) + ")")
    for time_frame in time_frame_list:
        print(time_frame, ":", "$" + str(stock.prices[time_frame]))

    return time_frame_list


# helper method that will obtain all of the percentages that the user wishes for a specified time frame
def get_percentages(time_frame, cost):
    while True:
        print("\nPlease enter the percentages from", time_frame, ": $" + str(cost))
        percentages = input("Enter a single option or comma separated list(15 = 15% and -15 = -15%):")
        percentage_list = percentages.split(',')

        # correctly format the inputted percentages removing blanks
        i = 0
        while i < len(percentage_list):
            percentage_list[i] = percentage_list[i].lstrip(' ')
            percentage_list[i] = percentage_list[i].rstrip(' ')
            i += 1

        # attempt to convert all of the user input to the corresponding percentage as a float
        # if this fails notify the user of invalid input and prompt again
        i = 0
        converted = True
        while i < len(percentage_list):
            try:
                percentage_list[i] = float(percentage_list[i]) / 100
            except ValueError:
                print("ERROR!!! Your inputs must be of the form specified\n")
                converted = False
                break
            i += 1
        if not converted:
            continue
        break
    # sort the percentages before returning
    percentage_list.sort()
    return percentage_list


# helper method to get the cost for an order
def get_cost(stock, percentage, time_frame):
    while True:
        order_cost = input(
            "Enter the desired amount in dollars to spend on order for " + str(stock.prices[time_frame]) +
            " % " + str(percentage * 100) + " : $")
        try:
            order_cost = float(order_cost)
            break
        except ValueError:
            print("ERROR!!! Your inputs must be of the form specified\n")
    return order_cost


# method that will allow the user to generate limit orders of specified percentages
def get_orders(stock, time_frames):
    # dictionary that will hold the different orders for each stock
    all_orders = {}

    # create a list that will hold the associated orders for time frames
    for time_frame in time_frames:
        all_orders[time_frame] = []
        percentages = get_percentages(time_frame, stock.prices[time_frame])
        for percentage in percentages:
            new_order = Order(stock.symbol, stock.prices[time_frame], percentage)
            order_cost = get_cost(stock, percentage, time_frame)
            new_order.compute_num_shares(order_cost)
            all_orders[time_frame].append(new_order)

    print()
    # print all of the orders
    for time_frame in time_frames:
        print("Orders based on the basis of " + str(time_frame))
        for order in all_orders[time_frame]:
            order.print_order()
        print()


# main
if __name__ == '__main__':
    # # create the database if it doesn't exist else connect to existing db
    # if path.exists("stocks.db"):
    #     print("Loading db...")
    #     load_db()
    # else:
    #     print("Creating db for your stocks...")
    #     create_db()
    # obtain the stock that the user wishes
    stock = get_stock()
    # get the time frames for the particular stock that the user wishes to trade off of
    time_frames = get_prices(stock)
    # obtain the users orders and print them to the console
    get_orders(stock, time_frames)
