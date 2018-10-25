from selenium import webdriver
import time
from tkinter import *
import csv

driver = webdriver.Chrome()
driver.get("https://www.tradingview.com/#signin")

username = driver.find_element_by_name('username')
username.send_keys(' ')

password = driver.find_element_by_name('password')
password.send_keys(' ')


driver.find_element_by_css_selector('.tv-button__loader').click()

time.sleep(1.5)

driver.get("https://www.tradingview.com/chart")

OrderType = "---"
Order = "---"
Close = 0
Open = 0

def writeCsv(input):
    input = input.split()
    csvfile = open("trades.csv", "a", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(input)


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

tk_OrderType = StringVar()
tk_Open = StringVar()
tk_Open.set(str(Open))
tk_OrderType.set(str(OrderType))

def buttonClick(option):
    if option is "Buy":
        buy()
    else:
        sell()

    tk_Open.set(str(getPrice()))
    tk_OrderType.set(str(OrderType))

root.geometry("500x500")

topFrame = Frame(root)
topFrame.pack(side=TOP)
midFrame = Frame(root)
midFrame.pack(fill=X)
bottomFrame = Frame(root, width=256)
bottomFrame.pack(side=BOTTOM, fill=X)

labelOrderType = Label(topFrame, textvariable=tk_OrderType, font='Arial 18 bold')
labelOrder = Label(topFrame, textvariable=tk_Open, font='Arial 36 bold')
labelOrder.pack(side=BOTTOM)
labelOrderType.pack()

tradesList = Listbox(midFrame, fg="black", font='Arial 16 bold')
tradesList.pack(fill=X)

reader = csv.reader(open("trades.csv", "r", newline=""))
for row in reader:
    print(str(row))
    tradesList.insert(END, str(row))



buttonBuy = Button(bottomFrame, text="BUY", bg="#53b987", fg="white", command = lambda: buttonClick("Buy"), font='Arial 16 bold')
buttonSell = Button(bottomFrame, text="SELL", bg="#eb4d5c", fg="white",command = lambda: buttonClick("Sell"), font='Arial 16 bold')
buttonBuy.pack(side=TOP, fill=X)
buttonSell.pack(fill=X)

root.wm_attributes("-topmost", 1)
root.lift()
root.mainloop()
driver.close()