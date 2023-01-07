import robin_stocks.robinhood as r
import time
import schedule
from pathlib import Path

#login and building portfolio
username = input("username: ")
password = input("password: ")
login = r.login(username, password)

first_trade = False
position = [stock for stock in r.crypto.get_crypto_positions() if stock['currency']['code'] == 'BTC']
average_price = 0
cost_basis = 0
quantity = 0
orders = []
BUY_AMOUNT = 50
FILE = Path(r'orderhistory.txt')

#Calculates the sma
def calculate_sma():
    historicals = r.crypto.get_crypto_historicals(symbol = 'btc', interval = '5minute', span = 'week')
    close_prices = []
    
    for dictionary in historicals:
        close_prices.append(float(dictionary['close_price']))

    close_prices = close_prices[len(close_prices)-20-1:]
    return sum(close_prices)/len(close_prices)-1
    
#function to determine when to buy or sell
def make_order(sma):
    global first_trade
    global cost_basis
    global BUY_AMOUNT
    global position
    global quantity
    global average_price
    if float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price'))<sma:
        if first_trade and float(r.profiles.load_account_profile()['crypto_buying_power'])-BUY_AMOUNT > 0:
            print(f'buying: current sma is {sma}')
            return r.orders.order_crypto(symbol = 'btc', side = 'buy', quantityOrPrice = BUY_AMOUNT, amountIn = 'price')
        elif float(r.profiles.load_account_profile()['crypto_buying_power'])-BUY_AMOUNT > 0:
            print(f'buying: current sma is {sma}')
            first_trade = True
            return r.orders.order_crypto(symbol = 'btc', side = 'buy', quantityOrPrice = BUY_AMOUNT, amountIn = 'price')#fix buy amount in master branch
    if sma<float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price')) and average_price*1.003<=float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price'))  or average_price*1.01<=float(r.crypto.get_crypto_quote(symbol = 'BTC', info = 'ask_price')):
        if cost_basis != 0:
            print(f'selling: current sma is {sma}')
            first_trade = False
            return r.orders.order_crypto(symbol = 'btc', side = 'sell', quantityOrPrice = quantity, amountIn = 'quantity')

def update():
    global cost_basis
    global position
    global quantity
    global average_price
    global orders
    position = [stock for stock in r.crypto.get_crypto_positions() if stock['currency']['code'] == 'BTC']

    if len(position) != 0:
        if float(position[0]['cost_bases'][0]['direct_quantity']) != 0:
            cost_basis = float(position[0]['cost_bases'][0]['direct_cost_basis'])
            quantity = float(position[0]['cost_bases'][0]['direct_quantity'])
        else:
            cost_basis = 0
            quantity = 0
            orders = []
    if float(position[0]['cost_bases'][0]['direct_quantity']) != 0:
        print(orders)
        average_price = sum([float(num['price']) for num in orders])/len(orders)
    else:
        average_price = 0
    
def job():
    global orders
    global FILE
    print('working')
    receipt = make_order(calculate_sma())
    if receipt!= None:
        orders.append(receipt)
        with open(FILE, 'a') as file:
            file.write(str(receipt))
    update()

update()
job()
schedule.every(2).minutes.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)




