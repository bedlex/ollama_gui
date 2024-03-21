"""Module to use for chatting with Ollama."""
from abc import ABC
import ollama

from typing import List


class Ollama(ABC):
    @staticmethod
    def list() -> List[str]:
        """Return available list in ollama server"""
        return [el.get("name") for el in ollama.list().get("models")]


class Agent:
    """Class to represent a chat agent."""

    def __init__(self):
        self.model = str()
        self.messages = list()
        self.active_chat = bool()
        self.agent_set = False

    def set_agent(self, model: str, role: str, active_chat: bool = False):
        """
        Class method to initialize class object

        Parameters:
            model(str): Specified model name
            role(str): Specified chat role
            active_chat(bool): Specified chat mode
        """

        self.model = model
        self.messages = [
            {
                'role': 'system',
                'content': role
            }
        ]
        self.active_chat = active_chat
        self.agent_set = True

    def chat(self, message: str):
        """
        Class method to receive response from chatbot

        Parameters:
            message(str): Message to bot
        Returns:
            str: Message from bot
        """
        self.messages.append(
            {
                'role': 'user',
                'content': message
            }
        )
        try:
            if self.agent_set:

                stream = ollama.chat(model=self.model, messages=self.messages, stream=True)

                if not self.active_chat:
                    self.messages.pop()

                for chunk in stream:
                    yield chunk['message']['content']

            else:
                return "Need to set agent first"
        except Exception as e:
            print(e)

    def add_context_message(self, message: str) -> bool:
        if self.active_chat:
            self.messages.append({
                'role': 'assistant',
                'content': message
            })
            return True
        return False

def main():
    """
    Example of usage chatbot agent
    :return:
    """
    agent = Agent()
    agent.set_agent('mistral:latest', 'Professional python programmer', active_chat=True)

    while True:
        print()
        message = input("user: ")

        response_message = str()
        for el in agent.chat(message):
            response_message = f"{response_message}{el}"
            print(el, end='')

        agent.add_context_message(message=response_message)


if __name__ == "__main__":
    main()
