#import psycopg2
from sqlalchemy import create_engine


def connect_postgres():
    user = 'postgres'
    password = 'password'
    host = '127.0.0.1'
    port = '5432'
    database = 'postgres'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    return engine