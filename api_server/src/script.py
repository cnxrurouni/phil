from yahooquery import Ticker

# Define the ticker for the stock
ticker = Ticker('AAPL')

# Fetch historical balance sheet data (quarterly)
balance_sheet = ticker.balance_sheet(frequency='q')

# Check the balance sheet for a specific quarter
print(balance_sheet)