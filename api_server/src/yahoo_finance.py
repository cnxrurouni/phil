import yfinance as yf

def get_ipo_date(ticker_symbol):
    # Fetch stock data from Yahoo Finance
    stock = yf.Ticker(ticker_symbol)
    
    # Try to get the IPO date from the stock's info
    stock_info = stock.info
    
    ipo_date = stock_info.get("ipoDate")
    
    # If IPO date is available, return it
    if ipo_date:
        return f"The IPO date for {ticker_symbol} is {ipo_date}."
    else:
        return f"IPO date for {ticker_symbol} is not available."

# Example usage
ticker_symbol = input("Enter the stock ticker symbol: ").upper()
ipo_date_info = get_ipo_date(ticker_symbol)
print(ipo_date_info)


get_ipo_date("RDDT")
