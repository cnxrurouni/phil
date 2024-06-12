from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import datetime
import src.database as db


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
  date = mapped_column(Date, default=datetime.datetime.now().date())
  count: Mapped[int] = mapped_column(Float, default=0.0)

  __table_args__ = (
      UniqueConstraint('company_ticker', 'date'),
  )


def create_models():
  engine = db.create_database_engine()

  Base.metadata.create_all(engine)

  Session = sessionmaker(bind=engine)

  with Session() as session:
    session.commit()



