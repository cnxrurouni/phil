from typing import Any
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, select, func, update, delete
import numpy
from sqlalchemy.orm import sessionmaker
import os
from models import create_models, Company, CurrentQuarter, Volume, Universe, UniverseTickerMapping, QuarterlyReportDates, ShortInterest
from BaseModels import CreateUniverseRequestBody, DeleteUniverseRequestBody, EditUniverseRequestBody
from parse_excel import parse_excel_sheet
from parse_saas_hc import get_report_dates, get_ciq_ipo_dates, get_short_interest
from fastapi import HTTPException



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
