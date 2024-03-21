from app.database.database import metadata
from sqlalchemy import Table, Column, Integer, String, BOOLEAN, TEXT, TIMESTAMP

history_table = Table('history_table', metadata,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('model', String(50)),
                      Column('chat', BOOLEAN),
                      Column('role', TEXT),
                      Column('timestamp', TIMESTAMP)
                      )