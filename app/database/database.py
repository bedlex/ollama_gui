from sqlalchemy import create_engine, MetaData

metadata = MetaData()

engine = create_engine("sqlite:///database.db", echo=False)
