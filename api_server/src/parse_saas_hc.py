import pandas as pd
import os
import datetime as datetime


def get_ciq_ipo_dates():
    # Load the Excel file
    path = os.getcwd()
    file_path = os.path.join(path, "api_server/src","SaaS_HC_Data.xlsx")
    sheet_name = 'CIQ IPO Dates'

    ciq_ipo_dates = {}
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    tickers = df['Ticker']
    ipo_dates = df['IPO Date']
    m_n_a_dates = df['M&A Date']
    
    for idx, ticker in tickers.items():
        ciq_ipo_dates[ticker] = {}
        ciq_ipo_dates[ticker]['ipo_date'] = ipo_dates[idx]
        ciq_ipo_dates[ticker]['m_n_a_date'] = "" if pd.isna(m_n_a_dates[idx]) else m_n_a_dates[idx]

    return ciq_ipo_dates
            

def get_report_dates():
    # Load the Excel file
    path = os.getcwd()
    file_path = os.path.join(path, "api_server/src","SaaS_HC_Data.xlsx")
    sheet_name = 'Report Dates -19 to 24'

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # If you want to access specific columns:
    quarters = df['Quarter']
    quarter_end = df['Quarter End']

    quarterly_data = {}

    for ticker, row in df.items():
        if ticker == 'Quarter' or ticker == 'Quarter End':
            continue
        for index, date in row.items():
            now = datetime.datetime.now()
            # Skip empty dates
            if (pd.isna(date)):
                continue

            # skip invalid dates
            if date > now:
                continue

            # Quarter string from column 0
            quarter_key = quarters[index]

            if quarter_key not in quarterly_data:
                quarterly_data[quarter_key] = {}

            # set quarter end for this quarter
            quarterly_data[quarter_key]['quarter_end'] = quarter_end[index]
            quarterly_data[quarter_key][ticker] = date
    return quarterly_data


def get_short_interest():
    # Load the Excel file
    path = os.getcwd()
    file_path = os.path.join(path, "api_server/src","SaaS_HC_Data.xlsx")
    sheet_name = 'Short Interest'

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # If you want to access specific columns:
    dates = df['Date']

    short_interest_data = {}

    for ticker, row in df.items():
        if ticker == 'Date':
            continue

        short_interest_data[ticker] = []
        for index, short_interest in row.items():
            # Skip empty
            if pd.isna(short_interest):
                continue

            short_interest_data[ticker].append(
                {
                    'date': dates[index],
                    'short_interest': short_interest
                }
            )
    return short_interest_data