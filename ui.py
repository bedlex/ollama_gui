from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget,
                             QPlainTextEdit, QPushButton, QTextBrowser,
                             QAction, QComboBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
import sys

from app.model_agent.agent import Ollama, Agent

from app.style.style import Style

from app.database.CRUD import History

agent = Agent()


class UI(QMainWindow):
    """Main window"""

    def __init__(self):
        """Initialize main window"""
        super(UI, self).__init__()

        self.chatTread = None

        # load ui
        uic.loadUi("app/ui/main.ui", self)

        # load Agent Form menu
        self.agentMenu = AgentForm()
        self.agentMenu.hide()
        # load setting Form menu
        self.interface = Interface()
        self.interface.hide()

        # load manage_agents settings menu
        self.manageAgents = self.findChild(QAction, "actionManage_agents")
        # load interface settings menu
        self.interface_setting = self.findChild(QAction, "actionInterface_settings")

        # load message button
        self.sendMessageButton = self.findChild(QPushButton, "pushButton")
        # load message textBox
        self.userMessage = self.findChild(QPlainTextEdit, "userMessage")
        # load AI response TextBox
        self.modelResponse = self.findChild(QTextBrowser, "modelResponse")

        # set size of the fonts

        # Execute agent form
        self.manageAgents.triggered.connect(self.show_Agent_form)
        # Execute interface form
        self.interface_setting.triggered.connect(self.show_interface_form)
        # Execute send message
        self.sendMessageButton.clicked.connect(self.start_chat)
        # Show the app
        self.show()

    def start_chat(self):
        previous_message = self.modelResponse.toPlainText()
        if previous_message != "":
            agent.add_context_message(previous_message)
            self.modelResponse.setPlainText("")
        message = self.userMessage.toPlainText()

        # start Thread
        self.chatTread = Chat(message)
        self.chatTread.start()
        self.chatTread.data_signal.connect(self.printMessage)
        self.chatTread.finish_signal.connect(self.finishMessage)

        self.sendMessageButton.setEnabled(False)
        self.sendMessageButton.setStyleSheet('background-color: #6F7D85')

    def printMessage(self, data):

        # Get data from thread
        response = f"{self.modelResponse.toPlainText()}{data}"
        self.modelResponse.setPlainText(response)

    def finishMessage(self):
        # execute code when message is done
        self.sendMessageButton.setEnabled(True)
        self.sendMessageButton.setStyleSheet('background-color: #308CC6')

    def message(self):
        """ Send message to the model """
        message = self.userMessage.toPlainText()
        response = str()

        for chunk in agent.chat(message=message):
            response = f"{response}{chunk}"
            self.modelResponse.setPlainText(response)

        agent.add_context_message(message=response)

    def show_Agent_form(self):
        """ Show Agent form """
        self.agentMenu.show()

    def show_interface_form(self):
        self.interface.show()


class AgentForm(QWidget):
    """Agent form"""

    def __init__(self):
        """Initialize Agent form"""
        super().__init__()
        # load ui
        uic.loadUi("app/ui/agents.ui", self)
        # get history
        self.history = [f"{el[0]}- {el[1]} {el[2]} {el[3]}" for el in History.get_last_agents()]

        # get start agent button
        self.startAgentButton = self.findChild(QPushButton, "startAgentButton")
        # get load agent button
        self.loadAgentButton = self.findChild(QPushButton, "loadAgentButton")

        # get modelsComboBox
        self.modelsComboBox = self.findChild(QComboBox, "modelsComboBox")
        # get checkbox
        self.checkBox = self.findChild(QCheckBox, "chatCheckBox")
        # get agent role
        self.agent_role = self.findChild(QPlainTextEdit, "agentRolePlanText")
        # get previous agents box
        self.prevAgents = self.findChild(QComboBox, "prevAgentsBox")

        # set variables
        if agent.agent_set:
            self.modelsComboBox.setCurrentText(agent.model)
            self.checkBox.setChecked(agent.active_chat)
            self.agent_role.setPlainText(agent.model)

        # start agent button action
        self.startAgentButton.clicked.connect(lambda: self.set_agent())
        # load agent button action
        self.loadAgentButton.clicked.connect(self.load_agent)
        # Add list to modelsComboBox
        self.modelsComboBox.addItems(Ollama.list())

        # Add list to prevAgents
        self.prevAgents.addItems(self.history)

    def load_agent(self):
        model_str = self.prevAgents.currentText()

        try:
            model_id = int(model_str.split("- ")[0])
            model = History.get_agent(agent_id=model_id)
            self.modelsComboBox.setCurrentText(model[1])
            self.checkBox.setChecked(model[2])
            self.agent_role.setPlainText(model[3])

        except Exception as error:
            print(error)

    def set_agent(self):
        """"Set agent variables"""

        model = self.modelsComboBox.currentText()
        active_chat = self.checkBox.isChecked()
        role = self.agent_role.toPlainText()

        History.add_agent(model=model, chat=active_chat, role=role)
        History.delete_history()

        agent.set_agent(model=model, role=role, active_chat=active_chat)

        self.history = [f"{el[0]}- {el[1]} {el[2]} {el[3]}" for el in History.get_last_agents()]
        # Add list to prevAgents
        self.prevAgents.clear()
        self.prevAgents.addItems(self.history)

        self.hide()


class Interface(QWidget):
    """Interface Form"""

    def __init__(self):
        """Initialize Interface form"""
        super().__init__()
        # load ui
        uic.loadUi("app/ui/ui_setting.ui", self)

        # load themes
        self.themesBox = self.findChild(QComboBox, "themesBox")
        # load button
        self.applyButton = self.findChild(QPushButton, "applyButton")
        # load QSpinBox
        self.font_size = self.findChild(QSpinBox, "font_size")

        # get Themes list
        self.themesBox.addItems(Style.available_themes())
        # button click event
        self.applyButton.clicked.connect(self.change_theme)
        # Set font_size to QSpinBox
        self.font_size.setValue(Style.get_font())

    def change_theme(self):
        new_style = self.themesBox.currentText()
        font_size = self.font_size.value()

        Style.change_theme(new_style)
        Style.set_font(font_size)
        set_style(app)
        self.hide()


class Chat(QThread):
    # Define a signal to send data from the chat thread to the main thread
    data_signal = pyqtSignal(str)
    finish_signal = pyqtSignal()

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        # Do some work in the Chat thread
        for chunk in agent.chat(message=self.message):
            # Emit the signal to send the data back to the main thread
            self.data_signal.emit(chunk)

        self.finish_signal.emit()


def set_style(app):
    """
    Set the style of the application.
    
    Parameters:
        - app: The application to apply the style to.
        - theme: The style to apply. "light" or "dark".
    
    """
    style = Style.current()
    if style:
        app.setStyleSheet(style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_style(app)
    UIWindow = UI()
    app.exec_()
