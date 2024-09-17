import pandas as pd
from Company import Company, MostRecentQuarter, InvestmentFirm, MRQ, KEY_METRICS, INPUT_VARIABLES, DERIVED_VARIABLES, Z_SCORE

DEBUG = 0
    

def parse_excel_sheet(excel_file_path):
    sheet = pd.ExcelFile(excel_file_path)

    # take only sheets that are stocks
    companies = [ticker for ticker in sheet.sheet_names if ticker.isupper() and ' ' not in ticker]

    all_companies = {}

    for company in companies:
        try: 
            company_obj = Company()
            # create empty dictionary for this ticker
            
            company_obj.ticker = company
            
            # sheet df
            df = pd.read_excel(sheet, company)
            
            # MRQ cell
            mrq = df.iloc[MRQ.MRQ,1]
            company_obj.mrq_data = get_mrq_data(df)
            
            # Key Metrics
            company_obj.key_metrics = get_key_metrics_data(df)
            
            # InvestmentFirm data
            company_obj.investment_firm = get_investment_firm_data(df)
            
            # input variables data
            company_obj.input_variables = get_input_variables_data(df)
            
            # derived variables data
            company_obj.derived_variables = get_derived_variables_data(df)
            
            # get volume data
            company_obj.volume = get_volume_data(df)
            
            # z score
            company_obj.z_score = get_z_score_data(df)
            
            col = df.columns.get_loc('Z Score')+3
            company_obj.retained_earnings = df.iloc[1, col]
            company_obj.ebit = df.iloc[2, col]
            company_obj.total_liabilities = df.iloc[3, col]
            
            # Save company data
            all_companies[company] = company_obj
        except Exception as e:
            print (f'Error parsing sheet {company}')
            print(e)

    return all_companies


def get_mrq_data(df):
    # MRQ cell
    mrq = df.iloc[2,1]
    mrq_data = {}
    
    # Parse MRQ Data
    for col in range(1, 14):
        date = df.iloc[MRQ.Date, col]
        quarter = df.iloc[MRQ.Quarter,col]

        # some sheets have less MRQ data, stop when we hit an empy column
        if type(quarter) != str:
            break

        revenue = df.iloc[MRQ.Revenue, col]
        gp = df.iloc[MRQ.GP, col]
        sb = df.iloc[MRQ.SB, col]
        gm = df.iloc[MRQ.GM, col]
        current_def_rev = df.iloc[MRQ.CurrentDefRevenue, col]
        billings = df.iloc[MRQ.Billings, col]
        
        mrq_data[quarter] = (MostRecentQuarter(date=date, quarter=quarter, revenue=revenue, \
                gp=gp, sb=sb, gm = gm, current_def_revenue=current_def_rev, billings=billings))
        
        if DEBUG:
            mrq_data[quarter].print()
    
    # save MRQ data in dictionary
    return mrq_data
    
    
def get_investment_firm_data(df):
    # Parse Investment Firm Section
    investment_firms = []
    for x in range(len(df['Holder'])):
        name = df['Holder'][x]
        cseh = df['Common Stock Equivalent Held'][x]
        percent_of_cso = df['% Of CSO'][x]
        if 'Market Value (CAD in mm)' in df:
            market_value = df['Market Value (CAD in mm)']
        else:
            market_value = df['Market Value (USD in mm)'][x]
        change_in_shares = df['Change in Shares']
        percent_change = df['% Change']
        position_date = df['Position Date'][x]
        source = df['Source'][x]
        pf_turnover_category = df['Portfolio Turnover Category'][x]
        pf_turnover_percentage = df['Portfolio Turnover (%)'][x]
        investment_orientation = df['Investment Orientation'][x]
        calculated_investment_style = df['Calculated Investment Style'][x]
        market_cap_emphasis = df['Market Cap Emphasis'][x]
        owner_type = df['Owner Type'][x]
        funds = df['Funds'][x]
        
        investment_firm = InvestmentFirm(name=name, cseh=cseh, percent_of_cso=percent_of_cso, \
            market_value=market_value, position_date=position_date, source=source, \
            change_in_shares=change_in_shares, percent_change=percent_change, \
            pf_to_category=pf_turnover_category, pf_to_percentage=pf_turnover_percentage, \
            investment_orientation=investment_orientation, cis=calculated_investment_style, \
            mc_emphasis=market_cap_emphasis, owner_type=owner_type, funds=funds)
    
        if DEBUG:
            investment_firm.print()
            
        investment_firms.append(investment_firm)
    
    return investment_firms
    
    
def get_key_metrics_data(df):
    # col 15-16
    key_metrics = {}
    
    # Growth
    growth = {}
    growth['revenue_mrq'] = df.iloc[KEY_METRICS.REVENUE_MRQ, 16] * 100
    growth['revenue_ltm'] = df.iloc[KEY_METRICS.REVENUE_LTM, 16] * 100
    growth['gm_mrq'] = df.iloc[KEY_METRICS.GM_MRQ, 16] * 100
    growth['gm_ltm'] = df.iloc[KEY_METRICS.GM_LTM, 16] * 100
    growth['billings_mrq'] = df.iloc[KEY_METRICS.BILLINGS_MRQ, 16] * 100
    growth['billings_ltm'] = df.iloc[KEY_METRICS.BILLINGS_LTM, 16] * 100
    key_metrics['growth'] = growth
    
    valuation = {}
    valuation['gm_div_ev'] = df.iloc[KEY_METRICS.GM_DIV_EV, 16]
    valuation['revenue_div_ev'] = df.iloc[KEY_METRICS.REVENUE_DIV_EV, 16]
    valuation['billings_div_ev'] = df.iloc[KEY_METRICS.BILLINGS_DIV_EV, 16]
    key_metrics['valuation'] = valuation
    
    
    efficiency = {}
    efficiency['gm_percentage'] = df.iloc[KEY_METRICS.GM_PERCENTAGE, 16] * 100
    efficiency['g_and_a_percentage'] = df.iloc[KEY_METRICS.G_AND_A_PERCENTAGE, 16] * 100
    efficiency['sales_efficiency_mrq'] = df.iloc[KEY_METRICS.SALES_EFFICIENCY_MRQ, 16]
    efficiency['sales_efficient_ltm'] = df.iloc[KEY_METRICS.SALES_EFFICIENCY_LTM, 16]
    efficiency['sales_comm_growth'] = df.iloc[KEY_METRICS.SALES_COMM_GROWTH, 16] * 100
    key_metrics['efficiency'] = efficiency
    
    technical_indicators = {}
    technical_indicators['short_interest'] = df.iloc[KEY_METRICS.SHORT_INTEREST, 16] * 100
    technical_indicators['passive_percentage'] = df.iloc[KEY_METRICS.PASSIVE_PERCENTAGE, 16] * 100
    technical_indicators['top_20_concentration'] = df.iloc[KEY_METRICS.TOP_20_CONCENTRATION, 16] * 100
    key_metrics['technical_indicators'] = technical_indicators

    other_qualitative = {}
    other_qualitative['share_dilution'] = df.iloc[KEY_METRICS.SHARE_DILUTION, 16] * 100
    other_qualitative['m_score'] = df.iloc[KEY_METRICS.M_SCORE, 16]
    other_qualitative['avg_volume_scaled'] = df.iloc[KEY_METRICS.AVG_VOLUME_SCALED, 16]
    other_qualitative['active_weighted_vol'] = df.iloc[KEY_METRICS.ACTIVE_WEIGHTED_VOL, 16]
    key_metrics['other_qualitative'] = other_qualitative
    
    cash_comm_metrics = {}
    cash_comm_metrics['billings_inc_div_cash_comm_ltm'] = df.iloc[KEY_METRICS.BILLINGS_INC_DIV_CASH_COMM_LTM, 16]
    cash_comm_metrics['billings_div_cash_comm'] = df.iloc[KEY_METRICS.BILLINGS_DIV_CASH_COMM, 16]
    cash_comm_metrics['billings_div_total_s_and_m'] = df.iloc[KEY_METRICS.BILLINGS_DIV_TOTAL_S_AND_M, 16]
    key_metrics['cash_comm_metrics'] = cash_comm_metrics
    
    if DEBUG:
        print(key_metrics)
        
    return key_metrics
    
    
def get_input_variables_data(df):
    # column 37-38
    input_variables = {}
    ltm = {}
    ltm['net_sales'] = df.iloc[INPUT_VARIABLES.NET_SALES, 37]
    ltm['cgs'] = df.iloc[INPUT_VARIABLES.CGS, 37]
    ltm['net_receivables'] = df.iloc[INPUT_VARIABLES.NET_RECEIVABLES, 37]
    ltm['current_assets_ca'] = df.iloc[INPUT_VARIABLES.CURRENT_ASSETS_CA, 37]
    ltm['ppe_net'] = df.iloc[INPUT_VARIABLES.PPE_NET, 37]
    ltm['depreciation'] = df.iloc[INPUT_VARIABLES.DEPRECIATION, 37]
    ltm['total_assets'] = df.iloc[INPUT_VARIABLES.TOTAL_ASSETS, 37]
    ltm['sga_expense'] = df.iloc[INPUT_VARIABLES.SGA_EXPENSE, 37]
    ltm['net_income_before_xitems'] = df.iloc[INPUT_VARIABLES.NET_INCOME_BEFORE_XITEMS, 37]
    ltm['cfo'] = df.iloc[INPUT_VARIABLES.CFO, 37]
    ltm['current_liabilities'] = df.iloc[INPUT_VARIABLES.CURRENT_LIABILITIES, 37]
    ltm['long_term_debt'] = df.iloc[INPUT_VARIABLES.LONG_TERM_DEBT, 37]
    input_variables['ltm'] = ltm
    
    prior_ltm = {}
    prior_ltm['net_sales'] = df.iloc[INPUT_VARIABLES.NET_SALES, 38]
    prior_ltm['cgs'] = df.iloc[INPUT_VARIABLES.CGS, 38]
    prior_ltm['net_receivables'] = df.iloc[INPUT_VARIABLES.NET_RECEIVABLES, 38]
    prior_ltm['current_assets_ca'] = df.iloc[INPUT_VARIABLES.CURRENT_ASSETS_CA, 38]
    prior_ltm['ppe_net'] = df.iloc[INPUT_VARIABLES.PPE_NET, 38]
    prior_ltm['depreciation'] = df.iloc[INPUT_VARIABLES.DEPRECIATION, 38]
    prior_ltm['total_assets'] = df.iloc[INPUT_VARIABLES.TOTAL_ASSETS, 38]
    prior_ltm['sga_expense'] = df.iloc[INPUT_VARIABLES.SGA_EXPENSE, 38]
    prior_ltm['net_income_before_xitems'] = df.iloc[INPUT_VARIABLES.NET_INCOME_BEFORE_XITEMS, 38]
    prior_ltm['cfo'] = df.iloc[INPUT_VARIABLES.CFO, 38]
    prior_ltm['current_liabilities'] = df.iloc[INPUT_VARIABLES.CURRENT_LIABILITIES, 38]
    prior_ltm['long_term_debt'] = df.iloc[INPUT_VARIABLES.LONG_TERM_DEBT, 38]
    input_variables['prior_ltm'] = prior_ltm  
    
    if DEBUG:
        print(input_variables)
        
    return input_variables
    
  
def get_derived_variables_data(df):
    # column 37-38
    derived_variables = {}
    derived_variables['other_lt_assets'] = df.iloc[DERIVED_VARIABLES.OTHER_LT_ASSETS, 37]
    say = {}
    say['dsri'] = df.iloc[DERIVED_VARIABLES.DSRI, 37]
    say['gmi'] = df.iloc[DERIVED_VARIABLES.GMI, 37]
    say['aqi'] = df.iloc[DERIVED_VARIABLES.AQI, 37]
    say['sgi'] = df.iloc[DERIVED_VARIABLES.SGI, 37]
    say['depi'] = df.iloc[DERIVED_VARIABLES.DEPI, 37]
    say['sgai'] = df.iloc[DERIVED_VARIABLES.SGAI, 37]
    say['total_accruals_div_ta'] = df.iloc[DERIVED_VARIABLES.TOTAL_ACCRUALS_DIV_TA, 37]
    say['lvgi'] = df.iloc[DERIVED_VARIABLES.LVGI, 37]
    derived_variables['say'] = say
    
    beneish_avg = {}
    beneish_avg['dsri'] = df.iloc[DERIVED_VARIABLES.DSRI, 38]
    beneish_avg['gmi'] = df.iloc[DERIVED_VARIABLES.GMI, 38]
    beneish_avg['aqi'] = df.iloc[DERIVED_VARIABLES.AQI, 38]
    beneish_avg['sgi'] = df.iloc[DERIVED_VARIABLES.SGI, 38]
    beneish_avg['depi'] = df.iloc[DERIVED_VARIABLES.DEPI, 38]
    beneish_avg['sgai'] = df.iloc[DERIVED_VARIABLES.SGAI, 38]
    beneish_avg['total_accruals_div_ta'] = df.iloc[DERIVED_VARIABLES.TOTAL_ACCRUALS_DIV_TA, 38]
    beneish_avg['lvgi'] = df.iloc[DERIVED_VARIABLES.LVGI, 38]
    derived_variables['beneish_avg'] = beneish_avg
    
    if DEBUG:
        print (derived_variables)
    
    return derived_variables
    

def get_volume_data(df):
    volume_data = []
    col = df.columns.get_loc('VOLUME')
    for x in range(len(df['VOLUME'])):
        # stop once row is empty
        if (pd.isnull(df.iloc[x, col+1])):
            break
        volume_data.append( [ df.iloc[x, col], df.iloc[x, col+1] ] )

    return volume_data
    

def get_z_score_data(df):
    #col 49
    col = df.columns.get_loc('Z Score')+1
    z_score = {}
    z_score['a'] = df.iloc[Z_SCORE.A, col]
    z_score['b'] = df.iloc[Z_SCORE.B, col]
    z_score['c'] = df.iloc[Z_SCORE.C, col]
    z_score['d'] = df.iloc[Z_SCORE.D, col]
    z_score['e'] = df.iloc[Z_SCORE.E, col]
    z_score['total'] = df.iloc[Z_SCORE.TOTAL, col]
    return z_score