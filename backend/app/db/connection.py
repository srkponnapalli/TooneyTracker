from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



load_dotenv()
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

#create engine
engine = create_engine(db_url)

#use engine to create session 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)