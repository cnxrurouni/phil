import configparser
from models.models import create_database_engine, Company, Volume
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker
import ast

config = configparser.ConfigParser()
config.read('universe_configuration.ini')

# get Company list from Universe 1
companies_list = ast.literal_eval(config.get("UNIVERSES", "ONE"))

# if volume flag is set, ready volume data
volume = ast.literal_eval(config["DATA"]["Volume"])

engine = create_database_engine()

Session = sessionmaker(bind=engine)

with (Session() as session):
    query = select(Company).where(Company.ticker.in_(companies_list))
    result = session.execute(query)
    for r in result.mappings().fetchall():
        ticker = r['Company'].ticker
        print(f'Company: {ticker}')

        if volume:
            total = session.query(func.sum(Volume.count)).filter(Volume.company_ticker == ticker).scalar()
            print(f'Volume sum: {total}\n')
