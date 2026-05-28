from sqlmodel import create_engine, Session, SQLModel
from pathlib import Path

DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[1] / 'travel.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
