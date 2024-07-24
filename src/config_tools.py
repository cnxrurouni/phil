import configparser
import ast

config = configparser.ConfigParser()
config.read('universe_configuration.ini')

# global universe variable
global target_universe


def set_universe(universe):
  global target_universe
  target_universe = universe


def get_all_config():
  pass


def get_tickers_from_universe():
  return ast.literal_eval(config[target_universe]['Tickers'])


def get_current_quarters():
  return ast.literal_eval(config.get(target_universe, 'CurrentQuarter'))
