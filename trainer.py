from selenium import webdriver
from tkinter import *
from pynput.keyboard import Key, Listener
from pyautogui import press, typewrite, hotkey
import threading
import os.path
import time
import csv


if os.path.exists("trades.csv"):
    pass
else:
    csvfile = open("trades.csv", "w")

driver = webdriver.Chrome()
driver.get("https://www.tradingview.com/#signin")

username = driver.find_element_by_name('username')
username.send_keys('')

password = driver.find_element_by_name('password')
password.send_keys('')


driver.find_element_by_css_selector('.tv-button__loader').click()

time.sleep(2)

driver.get("https://www.tradingview.com/chart")

OrderType = "No Position"
Order = "---"
Close = 0
Open = 0

def writeCsv(input):
    input = input.split()
    csvfile = open("trades.csv", "a", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(input)

def titleCsv():
    tradesList.delete('0', 'end')
    csvfile = open("trades.csv", "a")
    writer = csv.writer(csvfile)
    pair = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[1]/div[2]/table/tbody/tr[1]/td[2]/div/div[3]/div[1]/span[2]/div/div[1]").text
    timeFrame = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[1]/div[2]/table/tbody/tr[1]/td[2]/div/div[3]/div[1]/span[2]/div/div[2]").text
    exchange = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[1]/div[2]/table/tbody/tr[1]/td[2]/div/div[3]/div[1]/span[2]/div/div[3]").text
    writer.writerow([str(pair) + str(timeFrame) + str(exchange)])

def getPrice():
    price = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div[1]/div[2]/table/tbody/tr[1]/td[2]/div/div[3]/div[1]/div/span[4]/span[2]").text
    return price

def getProfit():
    global Open
    global Close
    global profit
    global OrderType
    profit = abs(float(Open) - float(Close)) / (float(Open)) * 100
    if OrderType is "Long":
        if Open < Close:
            print("Gain")
            profit = profit * 1
        else:
            print("Loss")
            profit = profit * -1

    if OrderType is "Short":
        if Open > Close:
            print("Gain")
            profit = profit * 1
        else:
            print("Loss")
            profit = profit * -1

    profit = round(profit, 2)
    return profit

def buy():
    global OrderType
    global Open
    global Close
    if OrderType is "Short":
        Close = getPrice()
        print("Close " + str(OrderType) + " @ " + str(getPrice()))
        print("Profit: " + str(getProfit()) + "%")
        writeCsv('\n' + str(OrderType) + " " + str(Open) + " " + str(getPrice()) + " " + str(getProfit()))

        OrderType = "Close"
    else:
        Open = getPrice()
        OrderType = "Long"
        print("Open " + str(OrderType) + " @ " + str(getPrice()))

def sell():
    global OrderType
    global Open
    global Close
    if OrderType is "Long":
        Close = getPrice()
        print("Close " + str(OrderType) + " @ " + str(getPrice()))
        print("Profit: " + str(getProfit()) + "%")
        writeCsv('\n' + str(OrderType) + " " + str(Open) + " " + str(getPrice()) + " " + str(getProfit()))
        OrderType = "Close"
    else:
        Open = getPrice()
        OrderType = "Short"
        print("Open " + str(OrderType) + " @ " + str(getPrice()))


root = Tk()
root.configure(background='#313335')

tk_OrderType = StringVar()
tk_Open = StringVar()
tk_Open.set(str(Open))
tk_OrderType.set(str(OrderType))
root.wm_attributes("-topmost", 1)
root.lift()

optionsBar = Frame(root)
optionsBar.pack(side=TOP, fill=X)
topFrame = Frame(root, background='#313335')
topFrame.pack(side=TOP)
midFrame = Frame(root)
midFrame.pack(fill=X)
bottomFrame = Frame(root, width=256)
bottomFrame.pack(side=BOTTOM, fill=X)

tradesList = Listbox(midFrame, font='Arial 16 bold', bg="#3C3F41", borderwidth=0, fg="#F1F3F4")
tradesList.config(relief=FLAT)
tradesList.pack(fill=X)


def updateTrades():
    tradesList.delete('1', 'end')
    reader = csv.reader(open("trades.csv", "r", newline=""))
    for row in reader:
        print(str(row))
        tradesList.insert(END, str(row))

def buttonClick(option):
    if option is "Buy":
        buy()
    else:
        sell()

    tk_Open.set(str(getPrice()))
    tk_OrderType.set(str(OrderType))
    updateTrades()

root.geometry("500x500")

labelOrderType = Label(topFrame, textvariable=tk_OrderType, font='Arial 18 bold', bg='#313335', fg="#F1F3F4")
labelOrder = Label(topFrame, textvariable=tk_Open, font='Arial 36 bold', bg='#313335', fg="#F1F3F4")
labelOrder.pack(side=BOTTOM)
labelOrderType.pack()

def on_press(key):
    key_press = key
    if str(key_press) == "Key.f7":
        buttonClick("Buy")
        hotkey('alt', 'v')
    if str(key_press) == "Key.f8":
        buttonClick("Sell")
        hotkey('alt', 'v')

def startListen():
    with Listener(on_press=on_press) as listener:
        listener.join()

listenThread = threading.Thread(target=lambda: startListen())
listenThread.start()


buttonPair = Button(optionsBar, text="------", bg="grey", fg="white", command = lambda: buttonClick("Buy"), font='Arial 9 bold')
buttonPair.pack(side=RIGHT)

buttonBuy = Button(bottomFrame, text="BUY", bg="#53b987", fg="white", command = lambda: buttonClick("Buy"), font='Arial 16 bold')
buttonSell = Button(bottomFrame, text="SELL", bg="#eb4d5c", fg="white", command = lambda: buttonClick("Sell"), font='Arial 16 bold')
buttonBuy.config(relief=FLAT)
buttonSell.config(relief=FLAT)
buttonBuy.pack(side=TOP, fill=X)
buttonSell.pack(fill=X)

time.sleep(2)

titleCsv()
root.mainloop()
driver.close()
listenThread.daemon = True
exit()
