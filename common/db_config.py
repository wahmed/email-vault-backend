# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
# # load_dotenv('../.env') 
# # load_dotenv('../.env.secrets') 

# load_dotenv('../.env_secrets')

# Base = declarative_base()

# class DatabaseConfig:
#     def __init__(self):
#         self.DB_NAME = os.getenv("DB_NAME")
#         self.DB_USER = os.getenv("DB_USER")
#         self.DB_PASSWORD = os.getenv("DB_PASSWORD")
#         self.DB_HOST = os.getenv("DB_HOST")
#         self.DB_PORT = os.getenv("DB_PORT")


#         print(f"DB_NAME: {self.DB_NAME}")
#         print(f"DB_USER: {self.DB_USER}")
#         print(f"DB_PASSWORD: {self.DB_PASSWORD}")
#         print(f"DB_HOST: {self.DB_HOST}")
#         print(f"DB_PORT: {self.DB_PORT}")


#         self.DATABASE_URL = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
#         print(f"DATABASE_URL: {self.DATABASE_URL}")

#         self.engine = create_engine(self.DATABASE_URL)
#         self.Session = sessionmaker(bind=self.engine)

#     def open(self):
#         """Open a new session."""
#         return self.Session()

#     def close(self, session):
#         """Close the provided session."""
#         session.close()


# db_config = DatabaseConfig()
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# load_dotenv('../.env_secrets')
load_dotenv('/app/.env_secrets') 

Base = declarative_base()

class DatabaseConfig:
    def __init__(self):
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")

        print(f"DB_NAME: {self.DB_NAME}")
        print(f"DB_USER: {self.DB_USER}")
        print(f"DB_PASSWORD: {self.DB_PASSWORD}")
        print(f"DB_HOST: {self.DB_HOST}")
        print(f"DB_PORT: {self.DB_PORT}")

        self.DATABASE_URL = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(f"DATABASE_URL: {self.DATABASE_URL}")

        self.engine = create_engine(self.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)

    def open(self):
        """Open a new session."""
        return self.Session()

    def close(self, session):
        """Close the provided session."""
        session.close()

db_config = DatabaseConfig()
