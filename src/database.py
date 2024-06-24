from typing import Any

from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase
import psycopg2
from psycopg2._psycopg import connection
from models.models import create_models
from sqlalchemy import create_engine
import numpy
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from src.parse_excel import parse_excel_sheet
import os
from models.models import Company, CurrentQuarter, Volume

password = ''

def create_database_engine():
  username = 'postgres'
  host = '127.0.0.1'
  db = 'Finance'

  database_url = f'postgresql://{username}:{password}@{host}/{db}'

  # Create an engine to connect to a postgres DB
  engine = create_engine(database_url)

  return engine


def populate_database_from_excel(engine):
  path = os.getcwd()
  companies = parse_excel_sheet(os.path.join(path, "src", "sheet2.xls"))

  Session = sessionmaker(bind=engine)

  with Session() as session:
    # get volume Data
    for ticker, obj in companies.items():
      query = select(Company).where(Company.ticker == ticker)
      result = session.execute(query).mappings().first()

      # if company doesn't exist in DB, create it
      if not result:
        comp = Company(name=ticker, ticker=ticker)
        session.add(comp)
        session.commit()
        query = select(Company).where(Company.ticker == ticker)
        result = session.execute(query).mappings().first()

      comp = result["Company"]

      for quarter, quarter_obj in obj.mrq_data.items():
        if not quarter:
          continue

        print(f'ticker: {ticker} quarter: {quarter}')
        query = select(CurrentQuarter).where(CurrentQuarter.quarter == quarter, CurrentQuarter.company_ticker == ticker)
        result = session.execute(query).mappings().first()
        if not result:
          current_quarter = CurrentQuarter(quarter=quarter, company_ticker=ticker, revenue=quarter_obj.revenue,
                                           gp=quarter_obj.gp, sb=quarter_obj.sb, gm=quarter_obj.gm,
                                           current_def_revenue=quarter_obj.current_def_revenue,
                                           billings=quarter_obj.billings)
          session.add(current_quarter)
          quarter_obj.print()
          session.commit()


      for date, val in obj.volume:
        if type(val) is not numpy.float64:
          # PCOR has invalid volume data
          continue

        query = select(Volume).where(Volume.company_ticker == ticker, Volume.date == date)
        result = session.execute(query).mappings().first()

        if not result:
          volume = Volume(company_id=comp.id, company_ticker=comp.ticker, date=date, count=val)
          session.add(volume)
          session.commit()


def connect_to_db():
  config = {'user': 'postgres',
            'password': password,
            'host': '127.0.0.1',
            'port': '5432',
            'dbname': 'postgres'}
  try:
    cnx: connection | connection | Any = psycopg2.connect(**config)
  except psycopg2.Error as err:
    print(err)
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
  except DuplicateDatabase:
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

