from enum import IntEnum


# row indexes for MRQ data
class MRQ(IntEnum):
  Date = 1
  MRQ = 2
  Quarter = 5
  Revenue = 6
  GP = 7
  SB = 8
  GM = 9
  CurrentDefRevenue = 10
  Billings = 11


# row indexes for Key Metrics Data
class KEY_METRICS(IntEnum):
  KEY_METRICS = 0
  GROWTH = 1
  REVENUE_MRQ = 2
  REVENUE_LTM = 3
  GM_MRQ = 4
  GM_LTM = 5
  BILLINGS_MRQ = 6
  BILLINGS_LTM = 7
  VALUATION = 8
  GM_DIV_EV = 9
  REVENUE_DIV_EV = 10
  BILLINGS_DIV_EV = 11
  EFFICIENCY = 12
  GM_PERCENTAGE = 13
  G_AND_A_PERCENTAGE = 14
  SALES_EFFICIENCY_MRQ = 15
  SALES_EFFICIENCY_LTM = 16
  SALES_COMM_GROWTH = 17
  TECHNICAL_INDICATORS = 18
  SHORT_INTEREST = 19
  PASSIVE_PERCENTAGE = 20
  TOP_20_CONCENTRATION = 21
  OTHER_QUALITATIVE = 22
  SHARE_DILUTION = 23
  M_SCORE = 24
  AVG_VOLUME_SCALED = 25
  ACTIVE_WEIGHTED_VOL = 26
  CASH_COMM_METRICS = 27
  BILLINGS_INC_DIV_CASH_COMM_LTM = 28
  BILLINGS_DIV_CASH_COMM = 29
  BILLINGS_DIV_TOTAL_S_AND_M = 30


class INPUT_VARIABLES(IntEnum):
  NET_SALES = 0
  CGS = 1
  NET_RECEIVABLES = 2
  CURRENT_ASSETS_CA = 3
  PPE_NET = 4
  DEPRECIATION = 5
  TOTAL_ASSETS = 6
  SGA_EXPENSE = 7
  NET_INCOME_BEFORE_XITEMS = 8
  CFO = 9
  CURRENT_LIABILITIES = 10
  LONG_TERM_DEBT = 11


class DERIVED_VARIABLES(IntEnum):
  OTHER_LT_ASSETS = 15
  DSRI = 17
  GMI = 18
  AQI = 19
  SGI = 20
  DEPI = 21
  SGAI = 22
  TOTAL_ACCRUALS_DIV_TA = 23
  LVGI = 24


class Z_SCORE(IntEnum):
  A = 0
  B = 1
  C = 2
  D = 3
  E = 4
  TOTAL = 5


class Company:
  def __INIT__(self):
    self.name = ""
    self.ticker = ""

    # left side data
    self.mrq_data = {}

    self.billings_ltm_calcs = []
    self.gaap_s_and_m = []
    self.s_and_m_sbc = []
    self.s_and_m = []
    self.gaap_g_and_a = []
    self.g_and_a_sbc = []
    self.g_and_a = []
    self.sales_etf = []
    self.st_dev = 0.0
    self.avg = 0.0
    self.cfo = []
    self.ni = []
    self.share_count = []
    self.last_price = 0.0
    self.shares_out = 0.0
    self.equity_value = 0.0
    self.cash = 0
    self.debt = 0
    self.ev = 0

    self.float_shares = 0
    self.float_percentage = 0
    self.shares_short = 0
    self.short_interest = 0
    self.passive = 0
    self.passive_percentage = 0

    self.key_metrics = {}

    # middle of sheet
    self.investment_firms = []

    # right side
    self.input_variables = {}
    self.derived_variables = {}
    self.volume = []
    self.z_score = {}
    self.retained_earnings = 0
    self.ebit = 0
    self.total_liabilities = 0


class InvestmentFirm:
  # constructor
  def __init__(self, \
               name, cseh, percent_of_cso, market_value, change_in_shares, \
               percent_change, position_date, source, pf_to_category, pf_to_percentage, \
               investment_orientation, cis, mc_emphasis, owner_type, funds):
    self.name = name
    self.common_stock_equivalent_held = cseh
    self.percent_of_cso = percent_of_cso
    # usd in mm
    self.market_value = market_value
    self.change_in_shares = change_in_shares
    self.percent_change = percent_change
    self.position_date = position_date
    self.source = source
    self.portfolio_turnover_category = pf_to_category
    self.portfolio_turnover_percentage = pf_to_percentage
    self.investment_orientation = investment_orientation
    self.calculated_investment_style = cis
    self.market_cap_emphasis = mc_emphasis
    self.owner_type = owner_type
    self.funds = funds

  def print(self):
    print(f'name: {self.name}')
    print(f'Common Stock Equivalent Held: {self.common_stock_equivalent_held}')
    print(f'% of CSO: {self.percent_of_cso}')
    print(f'Market Value: {self.market_value}')
    print(f'position_date: {self.position_date}')
    print(f'source: {self.source}')
    print(f'pf_turnover category: {self.portfolio_turnover_category}')
    print(f'pf_turnover_percentage = {self.portfolio_turnover_percentage}')
    print(f'investment_orientation: {self.investment_orientation}')
    print(f'calculated_investment_style = {self.calculated_investment_style}')
    print(f'market_cap_emphasis: {self.market_cap_emphasis}')
    print(f'owner_type: {self.owner_type}')
    print(f'fund: {self.funds}')


class MostRecentQuarter:
  def __init__(self, \
               date, quarter, revenue, gp, sb, gm, current_def_revenue, billings):
    self.date = date
    self.quarter = quarter
    self.revenue = revenue
    self.gp = gp
    self.sb = sb
    self.gm = gm
    self.current_def_revenue = current_def_revenue
    self.billings = billings

  def print(self):
    print(f'quarter: {self.quarter}')
    print(f'revenue: {self.revenue}')
    print(f'GP: {self.gp}')
    print(f'SB: {self.sb}')
    print(f'GM: {self.gm}')
    print(f'Current Def. Revenue: {self.current_def_revenue}')
    print(f'Billings: {self.billings}')
