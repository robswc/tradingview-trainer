from pyautogui import hotkey
from pynput.keyboard import Listener
from selenium import webdriver
from colorama import Fore, Style, init
import urllib.request
import zipfile
import webbrowser
import requests
import locale
import threading
import os.path
import config
import time
import csv

init(convert=True)
locale.setlocale(locale.LC_ALL, 'English_United States.1252')

account_value = config.initial_amount
order_type = "No Position"
Order = "---"
Close = 0
Open = 0

if os.path.exists("trades.csv"):
    pass
else:
    trades_file = open("trades.csv", "w")

# Set driver to chromedriver.exe
try:
    driver = webdriver.Chrome()
except Exception as e:
    # UPDATE CHROME DRIVER
    print(Fore.RED + '+ Error Involving Chrome Driver + \n')
    print(str(e) + '\n')
    print('Visit: https://github.com/Robswc/tradingview-trainer/wiki/Errors')
    print('Report this error here: https://github.com/Robswc/tradingview-trainer/issues')
    input()
    quit()


print('''
 _______     __  _____          _                 
|_   _\ \   / / |_   _| __ __ _(_)_ __   ___ _ __ 
  | |  \ \ / /____| || '__/ _` | | '_ \ / _ \ '__|
  | |   \ V /_____| || | | (_| | | | | |  __/ |   
  |_|    \_/      |_||_|  \__,_|_|_| |_|\___|_|   
                                                  
''')
print(Fore.CYAN + 'Created by Rob')
print(Fore.YELLOW + 'https://github.com/Robswc/tradingview-trainer')
print(Style.DIM + 'GLHF')
print('\n')

def get_chart():
    try:
        driver.get("https://www.tradingview.com/chart")
    except:
        print(driver.capabilities['version'])


if config.un == 'REPLACE W/YOUR USERNAME':
    print(Fore.RED + 'No Username Set, opening chart')
    print(Fore.YELLOW + 'For timeframes lower than 1 Day, you must have a tradingview account.')
    print(Style.DIM + 'Once you have an account, set your username/password in the config.py file.')
    print(Style.DIM + 'If you prefer to enter credentials manually, you can set un = "MANUAL"')
    print('\n')
    get_chart()

elif config.un == 'MANUAL':
    print(Fore.RED + 'No Username Set, credentials to be entered manually')
    print(Style.DIM + 'Enter your username and password into tradingview.com')
    print('\n')
    driver.get("https://www.tradingview.com/#signin")
    input("Press Enter *after* you have logged into tradingview...")
    get_chart()

else:
    # If Username/Password is set, go to sign in screen first and log in
    print(Fore.GREEN + 'Username Found, Signing In')
    print('\n')
    driver.get("https://www.tradingview.com/#signin")
    driver.find_element_by_name('username').send_keys(str(config.un))
    driver.find_element_by_name('password').send_keys(str(config.pw))
    driver.find_element_by_css_selector('.tv-button__loader').click()
    time.sleep(config.sleep)
    get_chart()


def write_csv(input):
    input = input.split()
    trades_file = open("trades.csv", "a", newline="")
    writer = csv.writer(trades_file)
    writer.writerow(input)

def value_change_format(a, b):
    if a <= b:
        return str(Fore.GREEN + '▲')
    else:
        return str(Fore.RED + '▼')

def update_account_value(profit):
    global account_value
    previous_value = account_value
    new_value = account_value + ((account_value * profit) * 0.01)
    account_value = account_value + ((account_value * profit) * 0.01)
    print(Style.RESET_ALL + 'Account Value: ' + str(locale.currency(account_value, grouping=True)) + value_change_format(previous_value, new_value))

def get_price():
	try:
		return driver.find_element_by_xpath(
			"/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tbody/tr[1]/td[2]/div/div[3]/div[1]/div/span[4]/span[2]").text
	except:
		return driver.find_element_by_xpath(
			"/html/body/div[1]/div[1]/div[3]/div[1]/div/table/tr[1]/td[2]/div/div[3]/div[1]/div/span[4]/span[2]").text

def get_profit():
    global Open
    global Close
    global profit
    global order_type
    global account_value
    profit = abs((float(Open) - float(Close)) / (float(Open)) * 100)
    if order_type is "Long":
        if Open < Close:
            print(Style.RESET_ALL + Fore.LIGHTGREEN_EX)
            profit = (profit * 1) - config.fee * 2
        else:
            print(Style.RESET_ALL + Fore.LIGHTRED_EX)
            profit = (profit * -1) - config.fee * 2

    if order_type is "Short":
        if Open > Close:
            print(Style.RESET_ALL + Fore.LIGHTGREEN_EX)
            profit = (profit * 1) - config.fee * 2
        else:
            print(Style.RESET_ALL + Fore.LIGHTRED_EX)
            profit = (profit * -1) - config.fee * 2

    profit = round(profit, 2)
    return profit


def buy():
    global account_value
    global order_type
    global Open
    global Close
    if order_type is "Short":
        Close = get_price()
        time.sleep(0.1)
        print(Fore.LIGHTMAGENTA_EX + "Close " + str(order_type) + Style.RESET_ALL + Style.DIM + " @ " + Fore.LIGHTYELLOW_EX + str(get_price()) + Style.RESET_ALL)
        print("PL%: " + str(get_profit()) + "%")
        print("Profit: " + str(locale.currency(account_value + ((account_value * profit) * 0.01) - account_value, grouping=True)))
        write_csv('\n' + str(order_type) + " " + str(Open) + " " + str(get_price()) + " " + str(get_profit()))
        order_type = "Close"
        update_account_value(profit)
    else:
        Open = get_price()
        order_type = "Long"
        print(Style.BRIGHT + Fore.GREEN + "Open " + str(order_type) + Style.RESET_ALL + Style.DIM + " @ " + str(get_price()))

    print('\n')


def sell():
    global account_value
    global order_type
    global Open
    global Close
    if order_type is "Long":
        Close = get_price()
        print(Fore.LIGHTMAGENTA_EX + "Close " + str(order_type) + Style.RESET_ALL + Style.DIM + " @ " + Fore.LIGHTYELLOW_EX + str(get_price()) + Style.RESET_ALL)
        print("PL%: " + str(get_profit()) + "%")
        print("Profit: " + str(locale.currency(account_value + ((account_value * profit) * 0.01) - account_value, grouping=True)))
        write_csv('\n' + str(order_type) + " " + str(Open) + " " + str(get_price()) + " " + str(get_profit()))
        account_value = account_value + ((account_value * profit) * 0.01)
        order_type = "Close"
        update_account_value(profit)
    else:
        Open = get_price()
        order_type = "Short"
        print("Open " + str(order_type) + Style.RESET_ALL + Style.DIM + " @ " + str(get_price()))
    print('\n')


def button_click(option):
    if option is "Buy":
        buy()
    else:
        sell()


def on_press(key):
    key_press = key
    if str(key_press) == "Key.f7":
        button_click("Buy")
        hotkey('alt', 'v')
    if str(key_press) == "Key.f8":
        button_click("Sell")
        hotkey('alt', 'v')


def start_listen():
    with Listener(on_press=on_press) as listener:
        listener.join()


listen_thread = threading.Thread(target=lambda: start_listen())
listen_thread.start()


