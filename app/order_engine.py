# -*- coding: utf-8 -*-

'''

This module handles the orders, orderbook and calculating PNLs.

by @robswc

'''

# TODO Clean up code.
# TODO Make things more efficient.

import statistics
from trade_exporting import write

# Test variables.
limit_price = 500
account_value = 10000
last_price = 1000

'''
I figured separating the main app and the order engine
into separate files would be a decent move here.
'''

# Mock orderbook, since there is no exchange/matching engine, this takes its place.
orderbook = {
    'bid': {
        'qty': 0,
        'price': 0,
    },
    'ask': {
        'qty': 0,
        'price': 0,
    }
}

# A dict for user position
position = {
    'quantity': 0,
    'entry': 0,
}

# Various Functions to grab values, most aren't needed and were used for testing, will clean up when possible.

# Gets position to avoid globals
def get_position():
    return position


# Gets account value to avoid globals
def get_account_value():
    return account_value


# Gets last price to avoid globals
def get_last_price():
    return last_price


# Gets last price to avoid globals
def get_last_high():
    return last_price


# Gets last price to avoid globals
def get_last_low():
    return last_price


def get_limit_price():
    return limit_price


def get_order_book():
    return orderbook


# Calculates basic percentage change from a to b
def percent_change(a, b):
    return ((a - b) / a) * 100


# Add realized pnl to account value.
def add_realized_pnl(realized_pnl):
    global account_value
    account_value = account_value + round(realized_pnl, 2)


# A class that represents a single trade.
class Trade:

    def __init__(self):
        self.position = position

    # Method to execute trades.
    def execute(self, quantity, price):
        global position

        # Check if position is increasing or decreasing.
        # If position is decreasing, take the difference and use it to get PNLs for the trade.
        if abs(position['quantity'] + quantity) < abs(position['quantity']):
            self.calculate_pnl(quantity, position['entry'], price)
            self.calculate_pnl_percent(quantity, position['entry'], price)
            add_realized_pnl(self.calculate_pnl(quantity, position['entry'], price))
            write([quantity, '@', price, round(self.calculate_pnl_percent(quantity, position['entry'], price), 2), '%'])
            print()

        # If increasing position average them for entry price
        if abs(position['quantity'] + quantity) > abs(position['quantity']):
            write([quantity, '@', price])
            print('increasing')
            if position['entry'] != 0:
                print('average')
                position['entry'] = statistics.mean([position['entry'], price])
            else:
                position['entry'] = price

        # Set Position
        position['quantity'] = position['quantity'] + quantity
        print('Position: ' + str(position['quantity']))
        if position['quantity'] == 0:
            position['entry'] = 0

    # Calculate the profit and loss.
    def calculate_pnl(self, quantity, entry_price, exit_price):
        print('calc quantity: ', quantity)
        print(quantity, ' * ', ' ( ', entry_price, '-', exit_price, ')', ' * ', 0.001)
        pnl = abs(quantity) * self.calculate_pnl_percent(quantity, entry_price, exit_price) * 0.01
        print('pnl: ', pnl)
        return pnl

    # Calculate the profit and loss percentage.
    def calculate_pnl_percent(self, quantity, entry_price, exit_price):
        print('PERCENT CHANGE: ', entry_price, exit_price)
        if quantity > 0:
            pnl_percent = percent_change(entry_price, exit_price)
        if quantity < 0:
            pnl_percent = percent_change(exit_price, entry_price)

        print('pnl%: ', pnl_percent)
        return pnl_percent


# Order Engine class, handles executing the trades.
class OrderEngine:

    # On tick, runs every virtual "tick", checks and updates values for limit orders.
    def on_tick(self, o, h, l, c):
        print('Order Engine *Tick*')
        print('-------------------')
        print(orderbook)
        print('-------------------')
        trade = Trade()

        print('GET LAST ORDER ENGINE HIGH: ', h)
        print('GET LAST ORDER ENGINE LOW: ', l)
        if orderbook['ask']['price'] < h:
            trade.execute(orderbook['ask']['qty'], orderbook['ask']['price'])
            orderbook['ask']['qty'] = 0
            orderbook['ask']['price'] = 0

        if orderbook['bid']['price'] > l:
            trade.execute(orderbook['bid']['qty'], orderbook['bid']['price'])
            orderbook['bid']['qty'] = 0
            orderbook['bid']['price'] = 0

    # Market Orders, executes immediately.
    def market(self, quantity, price):
        trade = Trade()
        trade.execute(quantity, price)

    # Limit Orders, check direction via quantity, get values from virtual orderbook.
    def limit(self, quantity, limit_price, last_price):
        print('Adding limit order to orderbook: ', str(quantity), str(limit_price))
        if quantity < 0 and limit_price > last_price:
            print('short limit')
            orderbook['ask']['qty'] = quantity
            orderbook['ask']['price'] = limit_price
        elif quantity < 0 and limit_price < last_price:
            self.market(quantity, last_price)
        if quantity > 0 and limit_price < last_price:
            print('long limit')
            print(limit_price)
            orderbook['bid']['qty'] = quantity
            orderbook['bid']['price'] = limit_price
        elif quantity > 0 and limit_price > last_price:
            self.market(quantity, last_price)


'''
End of Order Engine
'''


