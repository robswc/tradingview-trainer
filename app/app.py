# -*- coding: utf-8 -*-

'''

This module is the core module, creating the tkInter GUI and "placing" the orders.

The order_engine module handles the orders and calculating the PNLs, returning those values here.

Lots to do! Need to clean all of this up, need to employ better code practice.
Will eventually add separate frames to allow for more customization.

by @robswc

'''

# TODO Remove debugging prints.
# TODO Clean up code.
# TODO Make new frames.
# TODO add function to store and retrieve config xpaths.

# Import necessary modules.
from sys import platform
from selenium import webdriver
from tkinter import StringVar, messagebox
import tkinter.font as tkFont
import tkinter as tk
import locale
import os.path
import config
import time

# Import custom modules
from order_engine import OrderEngine, get_position, get_account_value, percent_change
from trade_exporting import write, read_all, clear_csv


# Set formatting for currency.
if platform == "win32":
    # Windows formatting
    locale.setlocale(locale.LC_ALL, 'English_United States.1252')
else: 
    # Linux/OS X formatting
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


# Set variables
config.initial_amount = 100000
account_value = float(config.initial_amount)
is_playing = "▶"

# Check if csv file already exists, if not create it.
if not os.path.exists("trades.csv"):
    trades_file = open("trades.csv", "w")

# Set driver to chromedriver.exe
# Try to initialize the driver, if it fails user will be told to update chrome or chromedriver.

try:
    driver = webdriver.Chrome()
    driver.get("https://www.tradingview.com/#signin")
except Exception as e:
    print('+ Error Involving Chrome Driver + \n')
    print(str(e) + '\n')
    print('Visit: https://github.com/Robswc/tradingview-trainer/wiki/Errors')
    print('Report this error here: https://github.com/Robswc/tradingview-trainer/issues')
    input()
    quit()


# Create main app tkinter frame.
class Application(tk.Frame):

    def __init__(self, master=None, bg=config.background_color):
        super().__init__(master)
        self.master = master
        self.master.configure(background="#1E1E1E")
        self.pack()
        self.create_widgets()
        self.limit_check()

    def create_fonts(self):
        self.font = tkFont.Font(family=config.font, weight=config.font_weight, size=config.font_size)
        self.font_large = tkFont.Font(family=config.font, weight=config.font_weight, size=round(config.font_size * 1.5))
        self.font_small = tkFont.Font(family=config.font, weight=config.font_weight, size=round(config.font_size * .66))

    def create_variables(self):
        # Set up StringVars that will be used.
        self.ticker_value = StringVar()
        self.account_value_text = StringVar()
        self.account_value_text.set(str(account_value))
        self.last_price_value = StringVar()
        self.current_position_value = StringVar()
        self.current_position_pnl = StringVar()
        self.account_value_pnl = StringVar()
        self.limit_price = StringVar()
        self.order_type = StringVar(None, 'market')

    # Create tkinter widgets.
    def create_widgets(self):
        self.create_fonts()
        self.create_variables()

        # Global is_playing as it is used as a boolean and StringVar
        global is_playing
        is_playing = StringVar()
        is_playing.set("▶")

        # Create Ticker Label for Ticker
        self.ticker_id = tk.Label(
            self,
            textvariable=self.ticker_value,
            fg=config.color_white,
            bg=config.background_color,
            font=self.font_large
        ).grid(row=0, column=0, columnspan=4, padx=33, sticky="nsew")

        # Create a label to show the last price
        self.last_price_label = tk.Label(
            self,
            textvariable=self.last_price_value,
            bg=config.background_color,
            fg=config.color_white,
            font=self.font_large
        ).grid(row=1, column=0, columnspan=4, sticky="nsew")

        # Create a button to start the reply
        self.play_button = tk.Button(
            self,
            textvariable=is_playing,
            bg=config.button_color_light,
            fg=config.color_grey,
            borderwidth=0
        )

        self.play_button["command"] = self.play_replay
        self.play_button.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Create a button for progressing to next bar
        self.next_button = tk.Button(self, text="▮▶", bg=config.button_color_light, fg=config.color_grey, borderwidth=0)
        self.next_button["command"] = self.next_bar
        self.next_button.grid(row=2, column=2, columnspan=2, sticky="nsew")

        # Create a button for long orders
        self.long_button = tk.Button(
            self,
            text="BUY",
            font=self.font,
            bg=config.button_color,
            fg=config.color_green,
            borderwidth=0
        )
        self.long_button["command"] = self.order_buy
        self.long_button.grid(row=3, column=0, columnspan=2, sticky="nsew")

        # Create a button for short orders
        self.short_button = tk.Button(
            self,
            text="SELL",
            font=self.font,
            bg=config.button_color,
            fg=config.color_red,
            borderwidth=0
        )
        self.short_button["command"] = self.order_sell
        self.short_button.grid(row=3, column=2, columnspan=2, sticky="nsew")

        # Create radio buttons to toggle between limit orders and market orders
        self.limit_radiobutton = tk.Radiobutton(
            self,
            bg=config.background_color,
            fg=config.color_dark_grey,
            selectcolor=config.background_color,
            text="LIMIT",
            variable=self.order_type,
            value="limit"
        )
        self.limit_radiobutton.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.market_radiobutton = tk.Radiobutton(
            self,
            bg=config.background_color,
            fg=config.color_dark_grey,
            selectcolor=config.background_color,
            text="MARKET",
            variable=self.order_type,
            value="market",
        ).grid(row=4, column=2, columnspan=2, sticky="nsew")

        # Create entry box for limit orders
        self.limit_price = tk.Entry(
            self,
            borderwidth=0,
            bg=config.button_color_light,
            fg=config.color_grey)
        self.limit_price.insert(0, " ")
        self.limit_price.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5)

        self.limit_copy_button = tk.Button(
            self,
            text="LAST",
            borderwidth=0,
            bg=config.button_color,
            fg=config.color_grey,
            font=self.font_small
        )
        self.limit_copy_button["command"] = self.copy_last
        self.limit_copy_button.grid(row=5, column=3, columnspan=1, sticky="nsew")

        self.current_position_label = tk.Label(
            self,
            text="Current Position",
            anchor="w",
            bg=config.background_color,
            fg=config.color_grey, font=self.font_small
        ).grid(row=6, column=0, columnspan=4, sticky="nsew")

        self.current_position_value_label = tk.Label(
            self,
            textvariable=self.current_position_value,
            anchor="w",
            bg=config.button_color_light,
            fg=config.color_dark_grey
        ).grid(row=7, column=0, columnspan=3, sticky="nsew")

        self.current_position_pnl_label = tk.Label(
            self,
            textvariable=self.current_position_pnl,
            anchor="e",
            bg=config.button_color_light,
            fg=config.color_dark_grey
        ).grid(row=7, column=3, columnspan=1, sticky="nsew")

        self.account_value_label = tk.Label(
            self,
            text="Account value",
            anchor="w",
            bg=config.background_color,
            fg=config.color_grey,
            font=self.font_small
        ).grid(row=8, column=0, columnspan=4, sticky="nsew")

        self.account_value_value_label = tk.Label(
            self,
            textvariable=self.account_value_text,
            bg=config.button_color_light,
            fg=config.color_white,
            anchor="w"
        ).grid(row=9, column=0, columnspan=3, sticky="nsew")

        self.account_value_pnl_label = tk.Label(
            self,
            textvariable=self.account_value_pnl,
            bg=config.button_color_light,
            fg=config.color_dark_grey,
            anchor="e"
        ).grid(row=9, column=3, columnspan=1, sticky="nsew")

        self.trade_history_label = tk.Label(
            self,
            text="Trades",
            anchor="w",
            bg=config.background_color,
            fg=config.color_grey,
            font=self.font_small
        ).grid(row=10, column=0, columnspan=3, sticky="nsew")

        self.trade_history_clear = tk.Button(
            self,
            text="Clear",
            bg=config.button_color,
            fg=config.color_grey,
            font=self.font_small,
            borderwidth=0
        )
        self.trade_history_clear.grid(row=10, column=3, columnspan=1, sticky="nsew")
        self.trade_history_clear['command'] = self.clear_list

        self.trade_history_list = tk.Listbox(
            self,
            fg=config.color_grey,
            bg=config.textarea_color,
            borderwidth=0)
        self.trade_history_list.grid(row=11, column=0, columnspan=4, sticky="nsew")

    # Write Timestamp to csv file
    write([time.strftime("%Y-%m-%d %H:%M")])

    # Start of Functions
    def message_box(self):
        messagebox.showinfo('Error', 'Sorry! Limit orders are not currently implemented.\n'
                                     'You can check progress here:\n'
                                     'https://github.com/Robswc/tradingview-trainer/issues/5')
        self.order_type.set('market')

    # Generic function to show error
    def show_error(self, cause, exception, message):
        messagebox.showerror(str(cause), str(str(exception) + '\n' + message))
        driver.get("https://github.com/Robswc/tradingview-trainer/wiki/Errors")

    def clear_list(self):
        clear_csv()
        self.update_labels()

    def get_ticker(self):
        #ticker = driver.find_element_by_xpath(
        #    '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/span[2]/div/div[1]/div'
        #).text
        try:
            ticker = driver.find_element_by_xpath(
                '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[1]/div[1]/div[1]'
            ).text
            ticker = str(ticker).split(' ')

            print(ticker[0])
            return str(ticker[0])
        except:
            return 'None'

    def get_price_data(self, request):
        try:
            if request == 'o':
                return float(driver.find_element_by_xpath(
                    '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/div[2]/div/div[1]/div[2]'
                ).text)

            if request == 'h':
                return float(driver.find_element_by_xpath(
                    '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[2]'
                ).text)

            if request == 'l':
                return float(driver.find_element_by_xpath(
                    '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/div[2]/div/div[3]/div[2]'
                ).text)

            if request == 'c':
                return float(driver.find_element_by_xpath(
                    '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/div[2]/div/div[4]/div[2]'
                ).text)
        except:
            return 0

    def get_limit_price(self):
        self.limit_price.get()

    def get_position_pnl(self):
        if get_position()['quantity'] < 0:
            pnl_percent = ((get_position()['entry'] - self.get_last_price()) / get_position()['entry']) * 100
        if get_position()['quantity'] > 0:
            pnl_percent = ((self.get_last_price() - get_position()['entry']) / self.get_last_price()) * 100

        try:
            return round(pnl_percent, 2)
        except:
            return 0

    # Doesn't seem to work :(
    def add_marker(self):
        pass
        # actions = ActionChains(driver)
        # element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]')
        # element.click()
        # actions.click(element).key_down(Keys.ALT, 'v').perform()

    def update_labels(self):

        # update all labels via tk StringVar()
        self.last_price_value.set(str(self.get_last_price()))
        self.current_position_pnl.set(str(self.get_position_pnl()) + '%')
        self.account_value_pnl.set(str(round(percent_change(get_account_value(), float(config.initial_amount)), 2)) + '%')
        self.current_position_value.set(str(get_position()['quantity']) + " @ " + str(get_position()['entry']))
        self.account_value_text.set(locale.currency(get_account_value(), grouping=True))
        self.ticker_value.set(self.get_ticker())

        # Update trade history box
        self.trade_history_list.delete(0, 'end')
        for trade in read_all():
            self.trade_history_list.insert(0, trade)

    # get last price via xpath
    def get_last_price(self):
        try:
            last_price = driver.find_element_by_xpath(
                '/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[2]/div/div[4]/div[2]'
            ).text
            return float(last_price)
        except:
            try:
                last_price = driver.find_element_by_xpath(config.custom_xpath_last_price).text
                return float(last_price)
            except Exception as error:
                pass

  #              self.show_error('last_value', str(error), 'Please report error here: ')


    # function to pass buy order to order engine.
    def order_buy(self):
        oe = OrderEngine
        if self.order_type.get() == 'market':
            oe.market(OrderEngine, round(get_account_value(), 2), self.get_last_price())
        if self.order_type.get() == 'limit':
            print('LIMIT BIMIT ORDER HEHEH')
            oe.limit(OrderEngine, round(get_account_value(), 2), float(self.limit_price.get()), self.get_last_price())
        self.update_labels()

    # function to pass sell order to order engine.
    def order_sell(self):
        oe = OrderEngine
        if self.order_type.get() == 'market':
            print(type(get_account_value()), type(self.get_last_price()))
            oe.market(OrderEngine, round(get_account_value(), 2) * -1, float(self.get_last_price()))
        if self.order_type.get() == 'limit':
            oe.limit(OrderEngine, get_account_value() * -1, float(self.limit_price.get()), self.get_last_price())
        self.update_labels()

    # Check with the order engine to see if there is a limit order.
    def limit_check(self):
        oe = OrderEngine
        oe.on_tick(OrderEngine,
                   self.get_price_data('o'),
                   self.get_price_data('h'),
                   self.get_price_data('l'),
                   self.get_price_data('c')
                   )
        global is_playing
        print(str(is_playing.get()))

        if str(is_playing.get()) == "▮▮":
            print(str(is_playing.get()))
            self.after(500, self.limit_check)

    # Function to auto-fill last price into limit price.
    def copy_last(self):
        self.limit_price.delete(0, "end")
        self.limit_price.insert(0, self.last_price_value.get())

    # Click next bar w/selenium, use functions to grab values.
    def next_bar(self):
        print(self.limit_price.get())
        global is_playing
        try:
            driver.find_element_by_xpath('/html/body/div[7]/div/div[2]/div[3]/div').click()
        except:
            try:
                driver.find_element_by_xpath(config.custom_xpath_replay).click()
            except:
                self.show_error('next_bar', 'xpath error', 'Please report error here: ')

        is_playing.set("▶")
        self.limit_check()
        self.update_labels()
        print('>>')

    # Function to click the play-replay with selenium, check for limit orders.
    def play_replay(self):
        global is_playing
        self.update_labels()
        try:
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div').click()
        except Exception:
            driver.find_element_by_xpath(config.custom_xpath_play_replay).click()
        print(str(is_playing.get()))
        if str(is_playing.get()) == "▶":
            is_playing.set("▮▮")
            print(str(is_playing))
            self.limit_check()
        else:
            is_playing.set("▶")
            print(str(is_playing))


# Create tkinter window/app
root = tk.Tk()
root.title('tv-Trainer ~@robswc')
root["bg"] = "#1E1E1E"
root.attributes('-topmost', True)
root.geometry("300x500+0+0")
app = Application(root)
app['bg'] = config.background_color
app.configure()
app.mainloop()
