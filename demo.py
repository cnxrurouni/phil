import configparser
from models.models import Company, CurrentQuarter, Volume
from src.database import create_database_engine
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker
import ast

config = configparser.ConfigParser()
config.read('universe_configuration.ini')

# get Company list from Universe 1
universe_one = ast.literal_eval(config.get("UNIVERSES", "ONE"))
universe_two = ast.literal_eval(config.get("UNIVERSES", "TWO"))

# check data flags
volume = ast.literal_eval(config["DATA"]["Volume"])
current_quarter = ast.literal_eval(config["DATA"]["CurrentQuarter"])
print(current_quarter)

engine = create_database_engine()

Session = sessionmaker(bind=engine)

with (Session() as session):
    query = select(Company).where(Company.ticker.in_(universe_one))
    result = session.execute(query)
    for r in result.mappings().fetchall():
        ticker = r['Company'].ticker
        print(f'Company: {ticker}')

        if volume:
            total = session.query(func.sum(Volume.count)).filter(Volume.company_ticker == ticker).scalar()
            print(f'Total Volume: {total}')
            print()

        if current_quarter:
            query = select(CurrentQuarter).where(CurrentQuarter.company_ticker.in_(universe_one), CurrentQuarter.quarter.in_(current_quarter))
            result = session.execute(query)
            for cq in result.mappings().fetchall():
                print(f'Quarter: {cq["CurrentQuarter"].quarter}')
                print(f'gp: {cq["CurrentQuarter"].gp}')
                print(f'sb: {cq["CurrentQuarter"].sb}')
                print(f'gm: {cq["CurrentQuarter"].gm}')
                print(f'current_def_revenue: {cq["CurrentQuarter"].current_def_revenue}')
                print(f'billings: {cq["CurrentQuarter"].billings}')
                print()

        print()