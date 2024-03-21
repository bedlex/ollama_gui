from abc import ABC

from app.database.database import engine, metadata
from app.database.models import history_table
from sqlalchemy import insert, select, delete, desc

from datetime import datetime


class History(ABC):
    """Abstract base class for managing the chat history."""

    @classmethod
    def add_agent(cls, model, chat, role) -> bool:
        """Add a new entry to the chat history.

               Args:
                   model (str): The name of the model used in the chat.
                   chat (str): The text of the chat message.
                   role (str): The role of the agent in the chat.

               Returns:
                   bool: True if successful, False otherwise.
               """
        with engine.begin() as conn:
            try:
                metadata.create_all(engine)
                history_object = insert(history_table).values(
                    model=model,
                    chat=chat,
                    role=role,
                    timestamp=datetime.utcnow()
                )
                conn.execute(history_object)
                return True
            except Exception as error:
                print(error)
                return False

    @staticmethod
    def get_last_agents():
        """
        Get the last 10 entries from the chat history.

        Returns:
                List[Tuple[int, str, str, str, datetime]] or None: A list of tuples containing the chat history data,
                or None if an error occurred.
        """
        with engine.begin() as conn:
            try:
                metadata.create_all(engine)
                history = select(history_table).order_by(desc(history_table.c.timestamp)).limit(10)
                result = conn.execute(history)
                return result.fetchall()
            except Exception as error:
                print(error)
                return False

    @classmethod
    def delete_history(cls, rest_amount: int = 10):
        """
        Delete all but the last n entries from the chat history.

        Args:
            rest_amount (int): The number of entries to keep in the history. Default is 10.

        Returns:
            bool: True if successful, False otherwise.
        """
        with engine.begin() as conn:
            try:
                metadata.create_all(engine)
                history = select(history_table).order_by(desc(history_table.c.timestamp))
                result = conn.execute(history).all()

                if len(result) > rest_amount:

                    for i in range(rest_amount, len(result)):
                        history_id = result[i][0]
                        conn.execute(delete(history_table).where(history_table.c.id == history_id))

                return True

            except Exception as error:
                print(error)
                return False
    @staticmethod
    def get_agent(agent_id):
        with engine.begin() as conn:
            try:
                agent_item = select(history_table).where(history_table.c.id == agent_id)
                result = conn.execute(agent_item).first()
                return result
            except Exception as error:
                print(error)
