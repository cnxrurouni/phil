import configparser
from models.models import Company, Volume
from src.database import create_database_engine
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker
import ast

config = configparser.ConfigParser()
config.read('universe_configuration.ini')

# get Company list from Universe 1
universe_one = ast.literal_eval(config.get("UNIVERSES", "ONE"))
universe_two = ast.literal_eval(config.get("UNIVERSES", "TWO"))

# if volume flag is set, ready volume data
volume = ast.literal_eval(config["DATA"]["Volume"])

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
            print(f'Volume sum: {total}\n')
