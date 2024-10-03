from sqlalchemy import Column, CheckConstraint, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import DATERANGE
from enum import Enum
import datetime

class MeasurementPeriodEnum(Enum):
    FOUR = 4
    EIGHT = 8
    THIRTEEN = 13
    FIFTY_TWO = 52


class Base(DeclarativeBase):
  pass


class Company(Base):
  __tablename__ = 'company'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
  # setting name unique to false due to these 2 rows: 
  # IQ50985792	Mimecast Services Limited
  # MIME	Mimecast Services Limited
  name: Mapped[str] = mapped_column(String(50), unique=False, nullable=True)
  ipo_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
  m_n_a_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)


class Volume(Base):
  __tablename__ = 'volume'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
  company_ticker: Mapped[str] = mapped_column(ForeignKey("company.ticker"))
  date: Mapped[Date] = mapped_column(Date)
  count: Mapped[int] = mapped_column(Float, default=0.0)

  __table_args__ = (
      UniqueConstraint('company_ticker', 'date'),
  )


class CurrentQuarter(Base):
  __tablename__ = 'current_quarter'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  quarter: Mapped[str] = mapped_column(String(10), nullable=False)
  company_ticker: Mapped[str] = mapped_column(ForeignKey("company.ticker"))
  revenue: Mapped[Float] = mapped_column(Float)
  gp: Mapped[Float] = mapped_column(Float)
  sb: Mapped[Float] = mapped_column(Float)
  gm: Mapped[Float] = mapped_column(Float)
  current_def_revenue: Mapped[Float] = mapped_column(Float)
  billings: Mapped[Float] = mapped_column(Float)

  __table_args__ = (
      UniqueConstraint('quarter', 'company_ticker'),
  )


class Universe(Base):
  __tablename__ = 'universe' 

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
  date_range: Mapped[DATERANGE] = mapped_column(DATERANGE, nullable=False)
  measurement_period: Mapped[int] = mapped_column(Integer)

  # Relationship to UniverseTickerMapping with cascade delete
  mappings = relationship(
      "UniverseTickerMapping",
      back_populates="universe",
      cascade="all, delete-orphan"  # Enable cascade delete for related mappings
  )

  __table_args__ = (
    CheckConstraint('lower(date_range) < upper(date_range)', name='valid_date_range'),
  )

  __table_args__ = (
    CheckConstraint(
        f"measurement_period IN ({', '.join(str(v.value) for v in MeasurementPeriodEnum)})",
        name="check_measurement_period"
    ),
  )


class UniverseTickerMapping(Base):
  __tablename__ = 'universe_ticker_mapping'
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  universe_id: Mapped[int] = mapped_column(ForeignKey("universe.id", ondelete="CASCADE"), index=True)
  ticker: Mapped[str] = mapped_column(ForeignKey("company.ticker"))

  # Relationship back to Universe
  universe = relationship("Universe", back_populates="mappings")


class QuarterlyReportDates(Base):
  __tablename__ = 'quarterly_report_dates'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  quarter: Mapped[str] = mapped_column(String(10), nullable=False)
  date: Mapped[Date] = mapped_column(Date)
  quarter_end: Mapped[Date] = mapped_column(Date)
  company_ticker: Mapped[str] = mapped_column(ForeignKey("company.ticker"), index=True)

  __table_args__ = (
      UniqueConstraint('company_ticker', 'quarter'),
  )


class ShortInterest(Base):
  __tablename__ = 'short_interest'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_ticker: Mapped[str] = mapped_column(ForeignKey("company.ticker"))
  date: Mapped[Date] = mapped_column(Date)
  short_interest: Mapped[Float] = mapped_column(Float)

  __table_args__ = (
      UniqueConstraint('company_ticker', 'date'),
  )

def create_models(engine):
  Base.metadata.create_all(engine)

  Session = sessionmaker(bind=engine)

  with Session() as session:
    session.commit()




