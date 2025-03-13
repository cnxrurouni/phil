from typing import Any
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, select, func, update, delete, between
import numpy
from sqlalchemy.orm import sessionmaker
import os
from models import create_models, Company, CurrentQuarter, Volume, Universe, UniverseTickerMapping, QuarterlyReportDates, ShortInterest, StockPrice, IndexPrice
from BaseModels import CreateUniverseRequestBody, DeleteUniverseRequestBody, EditUniverseRequestBody
from parse_excel import parse_excel_sheet
from parse_saas_hc import get_report_dates, get_ciq_ipo_dates, get_short_interest
from fastapi import HTTPException
import yfinance as yf
import pandas as pd
import datetime
from sqlalchemy.dialects.postgresql import insert
import matplotlib.pyplot as plt
from io import BytesIO
import base64


DEBUG = False


def get_tickers():
  engine = create_database_engine()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    query = select(Company)
    result = session.execute(query)
    tickers = result.scalars().all()
    return tickers

def get_universes():
  engine = create_database_engine()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    query = select(Universe)
    result = session.execute(query)
    universes = result.scalars().all()
    
    # Map each universe to its list of tickers
    universe_data = []
    
    for universe in universes:
      # Extract tickers
      tickers = [utm.ticker for utm in universe.mappings]
      universe_data.append({
        'id': universe.id,
        'name': universe.name,
        'date_range': universe.date_range,  # Make sure date_range is in a serializable format
        'tickers': tickers,
        'measurement_period': universe.measurement_period,
    })
      
    return universe_data
      

def post_create_universe(body: CreateUniverseRequestBody):
  engine = create_database_engine()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    # Create Universe
    universe = Universe(name=body.name, date_range=body.date_range, measurement_period=body.measurement_period)
    session.add(universe)
    
    # Create a list of UniverseTickerMapping instances
    mappings = [UniverseTickerMapping(universe=universe, ticker=ticker) for ticker in body.tickers]

    # Add all mappings to the session at once
    session.add_all(mappings)

    session.commit()

    return universe
  

def update_universe(universe_id: int, body: EditUniverseRequestBody):
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Update Universe details
        stmt = (
            update(Universe)
            .where(Universe.id == universe_id)
            .values(
                name=body.name,
                date_range=body.date_range,
                measurement_period=body.measurement_period
            )
            .returning(Universe)
        )
        result = session.execute(stmt)
        
        updated_universe = result.scalar()

        # Delete all existing UniverseTickerMapping entries for this universe
        session.execute(
            delete(UniverseTickerMapping)
            .where(UniverseTickerMapping.universe_id == universe_id)
        )

        # Add new UniverseTickerMapping entries
        mappings = [UniverseTickerMapping(universe_id=universe_id, ticker=ticker) for ticker in body.tickers]
        session.add_all(mappings)

        # Commit transaction
        session.commit()

        universe_data = {
          'id': updated_universe.id,
          'name': updated_universe.name,
          'date_range': updated_universe.date_range,  # Make sure date_range is in a serializable format
          'tickers': body.tickers,
          'measurement_period': body.measurement_period
        }

        return universe_data
    

def delete_universes(body: DeleteUniverseRequestBody):
  engine = create_database_engine()
  Session = sessionmaker(bind=engine)

  with Session() as session:
    for universe_id in body.universe_ids:
      # Delete all existing UniverseTickerMapping entries for this universe
      session.execute(
        delete(Universe)
        .where(Universe.id == universe_id)
    )
    
    session.commit()
    return True


def get_volume_data(tickers, engine=None):
  if engine is None:
    engine = create_database_engine()

  Session = sessionmaker(bind=engine)
  volume = {}
  with Session() as session:
    query = select(Company).where(Company.ticker.in_(tickers))
    result = session.execute(query)
    for r in result.mappings().fetchall():
      ticker = r['Company'].ticker

      if DEBUG:
        print(f'Company: {ticker}')

      total = session.query(func.sum(Volume.count)).filter(Volume.company_ticker == ticker).scalar()
      volume[ticker] = total

  return volume


def get_current_quarter_data(tickers, quarters, engine=None):
  if engine is None:
    engine = create_database_engine()

  Session = sessionmaker(bind=engine)

  data = {}
  with Session() as session:
    query = select(CurrentQuarter).where(CurrentQuarter.company_ticker.in_(tickers),
                                         CurrentQuarter.quarter.in_(quarters))
    result = session.execute(query)
    for cq in result.mappings().fetchall():
      data[cq["CurrentQuarter"].company_ticker] = {}
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter] = {}
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter]["gp"] = cq["CurrentQuarter"].gp
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter]["sb"] = cq["CurrentQuarter"].sb
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter]["gm"] = cq["CurrentQuarter"].gm
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter]["current_def_revenue"] = cq["CurrentQuarter"].current_def_revenue
      data[cq["CurrentQuarter"].company_ticker][cq["CurrentQuarter"].quarter]["billings"] = cq[
        "CurrentQuarter"].billings

      if DEBUG:
        print(f'Quarter: {cq["CurrentQuarter"].quarter}')
        print(f'gp: {cq["CurrentQuarter"].gp}')
        print(f'sb: {cq["CurrentQuarter"].sb}')
        print(f'gm: {cq["CurrentQuarter"].gm}')
        print(f'current_def_revenue: {cq["CurrentQuarter"].current_def_revenue}')
        print(f'billings: {cq["CurrentQuarter"].billings}')

    return data
  

def get_short_interest_for_tickers(
    tickers,  # Expecting a list of tickers
    start_date,
    end_date,
):
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    all_short_interest_data = {}  # Dictionary to store short interest data by ticker
    with Session() as session:
        # Build the query for short interest data for the specified tickers and date range
        short_interest_query = (
            select(ShortInterest.company_ticker, ShortInterest.short_interest, ShortInterest.date)
            .filter(
                ShortInterest.company_ticker.in_(tickers),  # Use in_ for multiple tickers
                ShortInterest.date.between(start_date, end_date)  # Date range filter
            ).order_by(ShortInterest.date.asc()) 
        )

        short_interest_result = session.execute(short_interest_query)
        short_interest_data = short_interest_result.fetchall()  # Use fetchall() instead of scalars()

        # Organizing data by ticker
        for row in short_interest_data:
            company_ticker = row[0]  # First column (ticker)
            short_interest = row[1]   # Second column (short interest)
            date = row[2]             # Third column (date)

            if company_ticker not in all_short_interest_data:
                all_short_interest_data[company_ticker] = []
            # Append a dictionary for each record
            all_short_interest_data[company_ticker].append({
                "short_interest": short_interest,
                "date": date
            })

    return all_short_interest_data



def create_database_engine():
  host = 'db'
  user = os.getenv('PGUSER', '')
  password = os.getenv('PGPASSWORD', '')
  db = os.getenv('PGDATABASE', '')

  database_url = f'postgresql://{user}:{password}@{host}/{db}'

  # Create an engine to connect to a postgres DB
  engine = create_engine(database_url)

  return engine


def populate_database_from_excel(engine):
  path = os.getcwd()
  companies = parse_excel_sheet(os.path.join(path, "api_server/src","sheet2.xls"))

  Session = sessionmaker(bind=engine)

  with Session() as session:
    # get volume Data
    for ticker, obj in companies.items():
      query = select(Company).where(Company.ticker == ticker)
      result = session.execute(query).mappings().first()

      # if company doesn't exist in DB, create it
      if not result:
        comp = Company(ticker=ticker)
        session.add(comp)
        session.commit()
        query = select(Company).where(Company.ticker == ticker)
        result = session.execute(query).mappings().first()

      comp = result["Company"]

      for quarter, quarter_obj in obj.mrq_data.items():
        if not quarter:
          continue

        query = select(CurrentQuarter).where(CurrentQuarter.quarter == quarter, CurrentQuarter.company_ticker == ticker)
        result = session.execute(query).mappings().first()
        if not result:
          current_quarter = CurrentQuarter(quarter=quarter, company_ticker=ticker, revenue=quarter_obj.revenue,
                                           gp=quarter_obj.gp, sb=quarter_obj.sb, gm=quarter_obj.gm,
                                           current_def_revenue=quarter_obj.current_def_revenue,
                                           billings=quarter_obj.billings)
          session.add(current_quarter)
          session.commit()

      for date, val in obj.volume:
        if type(val) is not numpy.float64:
          # PCOR has invalid volume data
          continue

        query = select(Volume).where(Volume.company_ticker == ticker, Volume.date == date)
        result = session.execute(query).mappings().first()

        if not result:
          volume = Volume(company_id=comp.id, company_ticker=comp.ticker, date=date, count=float(val)) 
          session.add(volume)
          session.commit()


def populate_report_dates(engine):
  quarterly_data = get_report_dates()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    for quarter, tickers in quarterly_data.items():
          for ticker, date in tickers.items():
              if ticker == 'quarter_end':
                continue

              row = session.query(Company).filter_by(ticker=ticker).first()  # Check if row exists
              if not row:
                row = Company(ticker=ticker)
                session.add(row)
                session.commit()
              
              qrd = session.query(QuarterlyReportDates).filter_by(company_ticker=row.ticker, quarter=quarter)
              if not qrd:
                qrd = QuarterlyReportDates(company_ticker=row.ticker, date=date, quarter=quarter, quarter_end=quarterly_data[quarter]['quarter_end'])
                session.add(qrd)      
                session.commit()
    
    print('Quarterly Report Dates written to Database')


def populate_ciq_ipo_dates(engine):
  ciq_ipo_dates = get_ciq_ipo_dates()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    for ticker, val in ciq_ipo_dates.items():
      row = session.query(Company).filter_by(ticker=ticker).first()  # Check if row exists
      if not row:
        row = Company(ticker=ticker, ipo_date=val['ipo_date'], m_n_a_date=val['m_n_a_date'] if val['m_n_a_date'] else None)
      else:
        if not row.ipo_date and val['ipo_date']:
          row.ipo_date= val['ipo_date']
        if not row.m_n_a_date and val['m_n_a_date']:
          row.m_n_a_date = val['m_n_a_date']
      session.add(row)
      session.commit()
    print('CIQ IPO dates written to Database')


def populate_short_interest(engine):
  short_interest_data = get_short_interest()
  Session = sessionmaker(bind=engine)
  with Session() as session:
    for ticker, data in short_interest_data.items():
      row = session.query(Company).filter_by(ticker=ticker).first()  # Check if row exists
      if not row:
        row = Company(ticker=ticker)
        session.add(row)
        session.commit()
      
      for item in data:
        si = ShortInterest(company_ticker=ticker, date=item['date'], short_interest=item['short_interest'])
        session.add(si)
        session.commit()
    print('Short interest written to Database')


def connect_to_db():
  config = {'user': os.getenv('PGUSER', ''),
            'password': os.getenv('PGPASSWORD', ''),
            'host': 'db',
            'port': '5432',
            'dbname': os.getenv('PGDATABASE', '')}
  try:
    cnx: psycopg2.connection | psycopg2.connection | Any = psycopg2.connect(**config)
  except psycopg2.Error as err:
    print(f"CONNECTION ERROR: {err}")
    print(config)
    exit(1)
  else:
    return cnx


def create_database():
  conn = connect_to_db()
  conn.autocommit = True
  cursor = conn.cursor()
  try:
    cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier('Finance')))
    print("DATABASE CREATED")
  except psycopg2.errors.DuplicateDatabase:
    print("DATABASE ALREADY EXISTS")
    pass


def run_migrations():
  # Creates DB Finance
  create_database()

  engine = create_database_engine()

  # Create Tables Company and Volume in Finance DB
  create_models(engine)

  # read data in from Excel
  populate_database_from_excel(engine)

  populate_ciq_ipo_dates(engine)

  populate_report_dates(engine)

  populate_short_interest(engine)


def update_stock_data(symbols, index=None, days=60):
    """
    Update database with latest stock data from yfinance.
    
    Parameters:
    -----------
    symbols : str or list
        Stock symbol(s) to update (e.g., 'AAPL' or ['AAPL', 'MSFT'])
    index : str, optional
        Index symbol to update (e.g., '^IXIC' for NASDAQ)
    days : int
        Number of days of historical data to fetch
    """
    # Convert single symbol to list for consistent handling
    if isinstance(symbols, str):
        symbols = [symbols]
    
    # Remove any index-like symbols from symbols list
    stock_symbols = [s for s in symbols if not s.startswith('^')]
    
    # Gather all index symbols
    index_symbols = [s for s in symbols if s.startswith('^')]
    if index and index not in index_symbols:
        index_symbols.append(index)

    # Setup database connection
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Process regular stocks
        for symbol in stock_symbols:
            print(f"Fetching data for stock: {symbol}...")
            
            # Get stock data from yfinance
            try:
                stock = yf.Ticker(symbol)
                df = stock.history(period=f'{days}d')           
                # Reset index to make Date a column
                df = df.reset_index()
                
                # Insert or update data in database
                for _, row in df.iterrows():
                    # Format date to handle timezone info from yfinance
                    date_str = row['Date'].strftime('%Y-%m-%d')
                    
                    # Create insert statement with on_conflict_do_update
                    stmt = insert(StockPrice).values(
                        stock_symbol=symbol,
                        date=date_str,
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume']),
                        adjusted_close=float(row.get('Adj Close', row['Close']))
                    ).on_conflict_do_update(
                        index_elements=['stock_symbol', 'date'],
                        set_={
                            'open_price': float(row['Open']),
                            'high_price': float(row['High']),
                            'low_price': float(row['Low']),
                            'close_price': float(row['Close']),
                            'volume': int(row['Volume']),
                            'adjusted_close': float(row.get('Adj Close', row['Close'])),
                            'created_at': func.current_timestamp()
                        }
                    )
                    
                    session.execute(stmt)
                    
                session.commit()
                print(f"Successfully processed {len(df)} records for stock {symbol}")
                
            except Exception as e:
                print(f"Error processing stock {symbol}: {e}")
                session.rollback()
                continue
        
        # Process index symbols separately
        for idx_symbol in index_symbols:
            print(f"Fetching data for index: {idx_symbol}...")
            
            try:
                index_ticker = yf.Ticker(idx_symbol)
                df = index_ticker.history(period=f'{days}d')
                # Reset index to make Date a column
                df = df.reset_index()
                
                # Insert or update data in database
                for _, row in df.iterrows():
                    # Format date to handle timezone info from yfinance
                    date_str = row['Date'].strftime('%Y-%m-%d')
                    
                    # Create insert statement with on_conflict_do_update for IndexPrice
                    stmt = insert(IndexPrice).values(
                        index_symbol=idx_symbol,
                        date=date_str,
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        adjusted_close=float(row.get('Adj Close', row['Close']))
                    ).on_conflict_do_update(
                        index_elements=['index_symbol', 'date'],
                        set_={
                            'open_price': float(row['Open']),
                            'high_price': float(row['High']),
                            'low_price': float(row['Low']),
                            'close_price': float(row['Close']),
                            'adjusted_close': float(row.get('Adj Close', row['Close'])),
                            'created_at': func.current_timestamp()
                        }
                    )
                    
                    session.execute(stmt)
                    
                session.commit()
                print(f"Successfully processed {len(df)} records for index {idx_symbol}")
                
            except Exception as e:
                print(f"Error processing index {idx_symbol}: {e}")
                session.rollback()
                continue
                
        return {"status": "success", "message": f"Updated {len(stock_symbols)} stocks and {len(index_symbols)} indices"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update stock data: {str(e)}")
    finally:
        session.close()
        engine.dispose()

def calculate_stock_volatility(stock_symbol, start_date=None, end_date=None):
    """
    Calculate the volatility of a stock from the database.
    
    Parameters:
    -----------
    stock_symbol : str
        The stock symbol to analyze (e.g., 'AAPL')
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format. If None, uses 1 year before end_date
    end_date : str, optional
        End date in 'YYYY-MM-DD' format. If None, uses current date
        
    Returns:
    --------
    dict
        Dictionary containing volatility metrics and base64 encoded plot
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        # Default to 1 year lookback
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        start_dt = end_dt - datetime.timedelta(days=365)
        start_date = start_dt.strftime('%Y-%m-%d')
    
    # Setup database connection
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if it's an index symbol
        if stock_symbol.startswith('^'):
            # Query using IndexPrice for indices
            stmt = select(IndexPrice.date, IndexPrice.close_price).where(
                IndexPrice.index_symbol == stock_symbol,
                IndexPrice.date >= start_date,
                IndexPrice.date <= end_date
            ).order_by(IndexPrice.date)
        else:
            # Query using StockPrice for stocks
            stmt = select(StockPrice.date, StockPrice.close_price).where(
                StockPrice.stock_symbol == stock_symbol,
                StockPrice.date >= start_date,
                StockPrice.date <= end_date
            ).order_by(StockPrice.date)
        
        # Execute query and convert to DataFrame
        result = session.execute(stmt)
        df = pd.DataFrame(result.fetchall(), columns=['date', 'close_price'])
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {stock_symbol} in the specified date range")
        
        # Calculate metrics
        df['daily_return'] = df['close_price'].pct_change() * 100
        df = df.dropna()
        
        daily_volatility = df['daily_return'].std()
        mean_return = df['daily_return'].mean()
        min_return = df['daily_return'].min()
        max_return = df['daily_return'].max()
        trading_days = len(df)
        
        # Generate plot
        plt.figure(figsize=(10, 6))
        plt.hist(df['daily_return'], bins=30, alpha=0.75)
        plt.title(f"{stock_symbol} Daily Returns Distribution")
        plt.xlabel("Daily Return (%)")
        plt.ylabel("Frequency")
        plt.axvline(mean_return, color='r', linestyle='dashed', linewidth=1)
        plt.grid(True, alpha=0.3)
        
        # Convert plot to base64 image
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close()
        
        results = {
            'stock_symbol': stock_symbol,
            'start_date': start_date if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d'),
            'end_date': end_date if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d'),
            'trading_days': trading_days,
            'daily_volatility': daily_volatility,
            'mean_daily_return': mean_return,
            'min_daily_return': min_return,
            'max_daily_return': max_return,
            'plot': img_base64
        }
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating volatility: {str(e)}")
    finally:
        session.close()
        engine.dispose()

def calculate_stock_correlation(stock_symbol, index=None, start_date=None, end_date=None):
    """
    Calculate the correlation between a stock and an index.
    
    Parameters:
    -----------
    stock_symbol : str
        The stock symbol to analyze (e.g., 'AAPL')
    index : str
        The index to measure correlation against (e.g., '^IXIC')
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format. If None, uses 1 year before end_date
    end_date : str, optional
        End date in 'YYYY-MM-DD' format. If None, uses current date
        
    Returns:
    --------
    dict
        Dictionary containing correlation metrics and base64 encoded plot
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        # Default to 1 year lookback
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        start_dt = end_dt - datetime.timedelta(days=365)
        start_date = start_dt.strftime('%Y-%m-%d')
    
    if not index:
        raise HTTPException(status_code=400, detail="Index symbol is required for correlation calculation")
    
    # Setup database connection
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get stock data
        stock_stmt = select(StockPrice.date, StockPrice.close_price).where(
            StockPrice.stock_symbol == stock_symbol,
            StockPrice.date.between(start_date, end_date)
        ).order_by(StockPrice.date)
        
        result = session.execute(stock_stmt)
        stock_data = pd.DataFrame(result.fetchall(), columns=['date', 'price'])
        
        if stock_data.empty:
            raise HTTPException(status_code=404, 
                               detail=f"No data found for stock {stock_symbol} in the specified date range")
        
        # Get index data from IndexPrice table
        index_stmt = select(IndexPrice.date, IndexPrice.close_price).where(
            IndexPrice.index_symbol == index,
            IndexPrice.date.between(start_date, end_date)
        ).order_by(IndexPrice.date)
        
        result = session.execute(index_stmt)
        index_data = pd.DataFrame(result.fetchall(), columns=['date', 'price'])
        
        if index_data.empty:
            raise HTTPException(status_code=404, 
                               detail=f"No data found for index {index} in the specified date range")
        
        # Merge dataframes on date
        merged_data = pd.merge(stock_data, index_data, on='date', suffixes=('_stock', '_index'))
        
        # Calculate returns
        merged_data['stock_return'] = merged_data['price_stock'].pct_change()
        merged_data['index_return'] = merged_data['price_index'].pct_change()
        merged_data = merged_data.dropna()
        
        if merged_data.empty:
            raise HTTPException(status_code=404, detail="Insufficient data for correlation calculation")
        
        # Calculate correlation and beta
        correlation = merged_data['stock_return'].corr(merged_data['index_return'])
        covariance = merged_data['stock_return'].cov(merged_data['index_return'])
        index_variance = merged_data['index_return'].var()
        beta = covariance / index_variance if index_variance != 0 else None
        
        # Generate scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(merged_data['index_return'], merged_data['stock_return'], alpha=0.5)
        plt.xlabel(f"{index} Returns")
        plt.ylabel(f"{stock_symbol} Returns")
        plt.title(f"{stock_symbol} vs {index} Daily Returns\nBeta: {beta:.2f}, Correlation: {correlation:.2f}")
        plt.grid(True, alpha=0.3)
        
        # Convert plot to base64 image
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close()
        
        results = {
            'stock_symbol': stock_symbol,
            'index': index,
            'start_date': start_date if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d'),
            'end_date': end_date if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d'),
            'correlation': correlation,
            'beta': beta,
            'trading_days': len(merged_data),
            'plot': img_base64
        }
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating correlation: {str(e)}")
    finally:
        session.close()
        engine.dispose()

def get_price_data(symbol: str, start_date: datetime, end_date: datetime):
    """Get price data for a symbol between start and end dates"""
    try:
        # Try to get stock price data first
        data = StockPrice.query.filter(
            StockPrice.symbol == symbol,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).order_by(StockPrice.date).all()
        
        # If no stock data found, try index price data
        if not data:
            data = IndexPrice.query.filter(
                IndexPrice.symbol == symbol,
                IndexPrice.date >= start_date,
                IndexPrice.date <= end_date
            ).order_by(IndexPrice.date).all()
        
        return data
    except Exception as e:
        print(f"Error getting price data: {str(e)}")
        return None

def calculate_volatility(symbol: str, start_date: datetime, end_date: datetime):
    """Calculate volatility for a symbol between start and end dates"""
    price_data = get_price_data(symbol, start_date, end_date)
    if not price_data:
        return None
    
    # Extract closing prices
    prices = [float(price.close) for price in price_data]
    if len(prices) < 2:
        return None
    
    # Calculate daily returns
    returns = np.array([(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))])
    
    # Calculate annualized volatility (assuming 252 trading days)
    volatility = np.std(returns) * np.sqrt(252)
    return float(volatility)

def calculate_correlation(symbol1: str, symbol2: str, start_date: datetime, end_date: datetime):
    """Calculate correlation between two symbols"""
    data1 = get_price_data(symbol1, start_date, end_date)
    data2 = get_price_data(symbol2, start_date, end_date)
    
    if not data1 or not data2:
        return None
    
    # Create DataFrames with date and close price
    df1 = pd.DataFrame([(d.date, float(d.close)) for d in data1], columns=['date', 'close'])
    df2 = pd.DataFrame([(d.date, float(d.close)) for d in data2], columns=['date', 'close'])
    
    # Merge on date to ensure we only use dates present in both series
    df = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
    
    if len(df) < 2:
        return None
    
    # Calculate correlation
    correlation = df['close_1'].corr(df['close_2'])
    return float(correlation)
