import pandas as pd
import os
import datetime as datetime

def get_report_dates():
    # Load the Excel file
    path = os.getcwd()
    file_path = os.path.join(path, "api_server/src","SaaS_HC_Data.xlsx")
    sheet_name = 'Report Dates -19 to 24'

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # If you want to access specific columns:
    quarters = df['Quarters']  # Access the 'CRM' column

    quarterly_data = {}

    for ticker, row in df.items():
        if(ticker == 'Quarters'):
            continue
        for index, date in row.items():
            now = datetime.datetime.now()
            # Skip invalid and empty dates
            if type(date) != datetime.datetime or date > now:
                continue
            quarter_key = quarters[index]
            if quarter_key not in quarterly_data:
                quarterly_data[quarter_key] = {}
            quarterly_data[quarter_key][ticker] = date
    return quarterly_data

get_report_dates()