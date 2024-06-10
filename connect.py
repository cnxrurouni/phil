from typing import Any

from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase
import psycopg2
from psycopg2._psycopg import connection
from models.models import create_models


def connect_to_db():
  config = {'user': 'postgres',
            'password': '', # Enter your password from installation
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
    print ("DATABASE CREATED")
  except DuplicateDatabase:
    print ("DATABASE ALREADY EXISTS")
    pass


def run_migrations():
  # Creates DB Finance
  create_database()

  # Create Tables Company and Volume in Finance DB
  create_models()


# to test out creation, just uncomment this and run
run_migrations()
