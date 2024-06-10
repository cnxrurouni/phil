from sqlalchemy import create_engine, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column
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
  date = mapped_column(Date, default=datetime.datetime.now().date())
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

  '''
  TODO: Populate data from excel sheet
  # Step 5: Insert data into the database
  Session = sessionmaker(bind=engine)
  session = Session()
  
  # Example: Inserting a new user into the database
  new_user = User(username='Sandy', email='sandy@gmail.com', password='cool-password')
  session.add(new_user)
  session.commit()

  # Step 6: Query data from the database
  # Example: Querying all users from the database
  all_users = session.query(User).all()

  # Example: Querying a specific user by their username
  user = session.query(User).filter_by(username='Sandy').first()

  # Step 7: Close the session
  session.close()
  '''

