from sqlalchemy import create_engine, Column, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///users.db", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    sup = Column(String)
    groups = Column(JSON)
    notifications = Column(Boolean, default=True)
    last_status = Column(String, default="Normal")

Base.metadata.create_all(engine)