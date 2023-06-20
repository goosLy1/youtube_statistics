from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@172.27.0.101:5432/yt_statistics_db"
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/yt_statistics_db"


engine = create_engine(
    # if sqlite - add  connect_args={"check_same_thread": False}
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
