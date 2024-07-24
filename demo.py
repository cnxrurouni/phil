import configparser
from src.config_tools import set_universe, get_tickers_from_universe, get_current_quarters
from src.database import get_current_quarter_data, get_volume_data

def main():
  # mimic backtest operations

  # 1. Set Universe we are targeting
  set_universe('UNIVERSE_ONE')

  # 2. get tickers from config
  tickers = get_tickers_from_universe()
  print(tickers)

  # 3a. get current quarter list from config
  current_quarters = get_current_quarters()
  print(current_quarters)

  # 3b. get current quarter data for given ticker(s)
  quarter_data = get_current_quarter_data(tickers, current_quarters)
  print(quarter_data)
  # access as dict ex: quarter_data["ADBE"]["CQ42019"]["gp"]

  # 4a. Get volume data
  volume_data = get_volume_data(tickers)
  print(volume_data)




if __name__ == "__main__":
  main()

