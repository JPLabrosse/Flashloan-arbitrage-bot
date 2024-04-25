import json
from avalanche import Avax, Flashloan
from web3 import Web3
import requests
from itertools import combinations
from requests.exceptions import RequestException

# Load configuration data
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize the Avalanche network and Flashloan
avalanche = Avax()
flashloan = Flashloan(avalanche)

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider(config['web3Provider']))

# Initialize contract instances
uniswap_router = web3.eth.contract(address=config['uniswapV2Router'], abi=uniswap_router_abi)
aave_lending_pool = web3.eth.contract(address=config['lendingPool'], abi=aave_lending_pool_abi)

# Fetch exchange rates
def fetch_exchange_rates():
    exchange_rates = {}
    for coin in config['coinAddresses']:
        try:
            coin_symbol = coin.symbol()
            coin_price = get_coin_price(coin_symbol)
            exchange_rates[coin_symbol] = coin_price
        except Exception as e:
            print(f"Error fetching exchange rate for {coin_symbol}: {e}")
            exchange_rates[coin_symbol] = 0
    return exchange_rates

# Fetch protocol loan fee rate
def fetch_protocol_loan_fee_rate():
    try:
        loan_fee_rate = aave_lending_pool.functions.getConfiguration().call()[0]
        return loan_fee_rate
    except Exception as e:
        print(f"Error fetching protocol loan fee rate: {e}")
        return 0

# Fetch coin prices on each exchange
def fetch_coin_prices():
    coin_prices = {}
    for coin in config['coinAddresses']:
        try:
            coin_symbol = coin.symbol()
            uniswap_price = fetch_uniswap_price(coin_symbol)
            coin_prices[coin_symbol] = uniswap_price
        except Exception as e:
            print(f"Error fetching coin price for {coin_symbol} on Uniswap: {e}")
            coin_prices[coin_symbol] = 0
    return coin_prices

# Check if it's profitable to execute the flash loan
def check_profitability():
    exchange_rates = fetch_exchange_rates()
    protocol_loan_fee_rate = fetch_protocol_loan_fee_rate()
    coin_prices = fetch_coin_prices()

    for coin in config['coinAddresses']:
        coin_symbol = coin.symbol()
        coin_price = coin_prices[coin_symbol]
        exchange_rate = exchange_rates[coin_symbol]
        protocol_fee = calculate_protocol_fee(coin_price, protocol_loan_fee_rate)
        expected_profit = (coin_price * (1 - protocol_fee - exchange_rate))
        transaction_value = calculate_transaction_value(coin_price, number_of_coins)
        
        # Calculate maximum acceptable loss
        slippage_fee = transaction_value * 0.03  # 3% slippage fee
        ex1_fee = transaction_value * 0.01  # 1% fee on ex1
        ex2_fee = transaction_value * 0.01  # 1% fee on ex2
        lending_pool_fee = calculate_aave_flash_loan_fee(transaction_value)
        max_loss = slippage_fee + ex1_fee + ex2_fee + lending_pool_fee
        max_loss = max_loss / 20  # Maximum loss is 1/20th of the possible successful outcome
        
        if expected_profit > max_loss:
            print(f"Profitability check passed for {coin_symbol}")
            execute_flash_loan(coin)
        else:
            print(f"Profitability check failed for {coin_symbol}")
def execute_flashloan_trade(ex1, ex2, coin, amount):
    try:
        flash_loan_amount = amount + calculate_aave_flash_loan_fee(amount)
        rates_ex1 = config['exchanges'][ex1]['rates'][coin]['price']
        rates_ex2 = config['exchanges'][ex2]['rates'][coin]['price']

        buy_cost = amount * rates_ex1
        sell_revenue = amount * rates_ex2
        repayment_amount = flash_loan_amount + calculate_aave_flash_loan_fee(flash_loan_amount)

        if sell_revenue >= buy_cost + repayment_amount:
            print(f"Executing profitable trade between {ex1} and {ex2} for {coin}")
        else:
            pass

    except Exception as e:
        print(f"Trade execution failed: {str(e)}")

def calculate_aave_flash_loan_fee(loan_amount):
    return loan_amount * 0.0009  # Aave flash loan fee is currently set at 0.09%

def arbitrage_bot():
    # Update exchange rates
    with ThreadPoolExecutor() as executor:
        exchange_rates = {exchange_name: executor.submit(fetch_exchange_rates, exchange_name, config['volatileCoins'])
                          for exchange_name in config['exchanges']}
    for exchange_name, rates_future in exchange_rates.items():
        config['exchanges'][exchange_name]['rates'] = rates_future.result() if rates_future.result() else None

    # Check for arbitrage opportunities
    with ProcessPoolExecutor() as executor:
        for coin in config['volatileCoins']:
            for ex1, ex2 in combinations(config['exchanges'].keys(), 2):
                executor.submit(check_arbitrage, ex1, ex2, coin)

def check_arbitrage(ex1, ex2, coin):
    if is_profitable(ex1, ex2, coin):
        print(f"Profitable arbitrage opportunity found for {coin} between {ex1} and {ex2}")
        execute_flashloan_trade(ex1, ex2, coin, 100)

# Run the arbitrage bot
arbitrage_bot()
