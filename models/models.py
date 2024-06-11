from sqlalchemy import create_engine, Date, Float, ForeignKey, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, sessionmaker
from parse_excel import parse_excel_sheet
import datetime


class Base(DeclarativeBase):
  pass


class Company(Base):
  __tablename__ = 'company'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
  ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)


class Volume(Base):
  __tablename__ = 'volume'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
  company_ticker: Mapped[str] = mapped_column(ForeignKey("company.name"))
  date = mapped_column(Date, unique=True, default=datetime.datetime.now().date())
  count: Mapped[int] = mapped_column(Float, default=0.0)


def create_models():
  username = 'postgres'
  password = ''
  host = '127.0.0.1'
  db = 'Finance'

  database_url = f'postgresql://{username}:{password}@{host}/{db}'

  # Create an engine to connect to a postgres DB
  engine = create_engine(database_url)

  # Step 4: Create the database tables
  Base.metadata.create_all(engine)

  # Step 5: Insert data into the database
  Session = sessionmaker(bind=engine)

  companies = parse_excel_sheet("sheet2.xls")

  with Session() as session:
    # get volume Data
    for ticker, obj in companies.items():
      query = select(Company).where(Company.ticker == ticker)
      result = session.execute(query)

      # if company doesn't exist in DB, create it
      if result is None:
        comp = Company(name=ticker, ticker=ticker)
        session.add(comp)
        session.commit()
        query = select(Company).where(Company.ticker == ticker)
        result = session.execute(query)

      comp = result.mappings().first()["Company"]

      for date, val in obj.volume:
        query = select(Volume).where(Volume.company_ticker == comp.ticker, Volume.date ==date)
        result = session.execute(query)
        if result is None:
          volume = Volume(company_id=comp.id, company_ticker=comp.ticker, date=date, count=val)
          session.add(volume)

      session.commit()

