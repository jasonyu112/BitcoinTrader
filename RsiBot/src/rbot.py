import robin_stocks.robinhood as r
import numpy as np
import tulipy as tl
import time
import schedule
from pathlib import Path


#implement 10:1 buy sell timer ratio
#login and building portfolio
username = input("username: ")
password = input("password: ")
login = r.login(username, password)

first_trade = False
position = [stock for stock in r.crypto.get_crypto_positions() if stock['currency']['code'] == 'BTC']
counter = 150
average_price = 0
cost_basis = 0
quantity = 0
orders = []
BUY_AMOUNT = 100
last_price = 0
FILE = Path(r'C:\Users\Kay and Jay\Documents\GitHub\RobinHood-RSI-Trading-Bot\venv1\src\orderhistory.txt')

#Calculates the rsi
def calculate_rsi():
    historicals = r.crypto.get_crypto_historicals(symbol = 'btc', interval = '5minute', span = 'day')
    close_prices = []
    
    for dictionary in historicals:
        close_prices.append(float(dictionary['close_price']))

    close_prices = np.array(close_prices)
    rsi_data = tl.rsi(close_prices, 5)
    return rsi_data[len(rsi_data)-1]

#function to determine when to buy or sell
def make_order(rsi):
    global first_trade
    global cost_basis
    global BUY_AMOUNT
    global position
    global quantity
    global average_price
    global counter
    global last_price
    print(rsi)
    if rsi <=35:
        if counter>=150:
            if first_trade and float(r.profiles.load_account_profile()['crypto_buying_power'])-BUY_AMOUNT > 0 and float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price')) < last_price:
                
                print(f'buying: current rsi is {rsi}')
                
                counter = 0
                return r.orders.order_crypto(symbol = 'btc', side = 'buy', quantityOrPrice = BUY_AMOUNT, amountIn = 'price')
            
            elif float(r.profiles.load_account_profile()['crypto_buying_power'])-BUY_AMOUNT > 0:
                
                print(f'buying: current rsi is {rsi}')
                
                first_trade = True
                counter = 0
                return r.orders.order_crypto(symbol = 'btc', side = 'buy', quantityOrPrice = BUY_AMOUNT, amountIn = 'price')
            
    if rsi >=65 and average_price*1.003<=float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price')) or rsi>=80:
        if cost_basis != 0:
            print(f'selling: current rsi is {rsi}')
            first_trade = False
            return r.orders.order_crypto(symbol = 'btc', side = 'sell', quantityOrPrice = quantity, amountIn = 'quantity')

def update():
    global cost_basis
    global position
    global quantity
    global average_price
    global orders
    global counter
    global last_price
    position = [stock for stock in r.crypto.get_crypto_positions() if stock['currency']['code'] == 'BTC']
    counter +=1
    if len(position) != 0:
        if float(position[0]['cost_bases'][0]['direct_quantity']) !=0:
            cost_basis = float(position[0]['cost_bases'][0]['direct_cost_basis'])
            quantity = float(position[0]['cost_bases'][0]['direct_quantity'])
        else:
            cost_basis = 0
            quantity = 0
            orders = []
            last_price = 0
            
        if float(position[0]['cost_bases'][0]['direct_quantity']) !=0 and len(orders) != 0:

            try:
                average_price = sum([float(num['price']) for num in orders])/len(orders)
            except KeyError:
                average_price = 0
        else:
            average_price = 0
        print(average_price)
def job():
    global orders
    global FILE
    global last_price
    print('working')
    receipt = make_order(calculate_rsi())
    if receipt!= None:
        orders.append(receipt)
        last_price = float(receipt['price'])
        with open(FILE, 'a') as file:
            file.write(str(receipt))
    update()



update()

job()
schedule.every(1).seconds.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)


#idea: make counter dependent on the rsi. higher counter for higher rsi and low counter for lower rsi
#def calculate_counter(rsi): ->int
#buy only if it is less than the previous buy price
#also buy only when rsi is <=30 three times in a row to confirm
