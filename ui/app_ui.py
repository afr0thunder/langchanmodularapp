from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QPushButton, QLineEdit
import sys
from ui.agent_editor import AgentEditor

class ChatInterface(QWidget):
    def __init__(self, agent_manager):
        super().__init__()
        self.setWindowTitle("LangChain Modular AI Chat App")
        self.resize(800, 600)

        self.agent_manager = agent_manager
        self.agent_names = self.agent_manager.list_agents()
        self.chat_handlers = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._build_widgets()
        self._set_active_agent(self.agent_names[0])

    def _build_widgets(self):
        self.agent_dropdown = QComboBox()
        self.agent_dropdown.addItems(self.agent_names)
        self.agent_dropdown.currentIndexChanged.connect(self._on_agent_change)
        self.layout.addWidget(self.agent_dropdown)

        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.clicked.connect(self._clear_chat)
        self.layout.addWidget(self.clear_btn)

        self.chat_display = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.chat_display, stretch=1)

        self.user_input = QLineEdit()
        self.user_input.returnPressed.connect(self._send_message)
        self.layout.addWidget(self.user_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_message)
        self.layout.addWidget(self.send_btn)

        self.new_agent_btn = QPushButton("New Agent")
        self.new_agent_btn.clicked.connect(self._open_new_agent_dialog)
        self.layout.addWidget(self.new_agent_btn)

        self.edit_btn = QPushButton("Edit Agent")
        self.edit_btn.clicked.connect(self._open_edit_agent_dialog)
        self.layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete Agent")
        self.delete_btn.clicked.connect(self._delete_agent)
        self.layout.addWidget(self.delete_btn)

    def _set_active_agent(self, agent_name):
        if not agent_name or agent_name not in self.agent_names:
            return
        self.agent_dropdown.setCurrentText(agent_name)
        agent = self.agent_manager.get_agent(agent_name)
        if agent_name not in self.chat_handlers:
            from chat.chat_handler import ChatHandler
            self.chat_handlers[agent_name] = ChatHandler(agent)
        self.handler = self.chat_handlers[agent_name]
        self._refresh_display()

    def _on_agent_change(self):
        selected = self.agent_dropdown.currentText()
        if selected:
            self._set_active_agent(selected)

    def _refresh_display(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
            body { font-family: sans-serif; padding: 10px; }
            .msg { margin-bottom: 20px; }
            .user { font-weight: bold; color: #007acc; }
            .agent { font-weight: bold; color: #009900; }
        </style>
        </head>
        <body>
        """
        for msg in self.handler.get_history():
            role = msg['role'].lower()
            content = msg['content'].replace("\n", "<br>")
            timestamp = msg['timestamp']
            html += f'<div class="msg"><span class="{role}">[{timestamp}] {role.capitalize()}:</span><br>{content}</div>'

        html += "</body></html>"
        self.chat_display.setHtml(html)

    def _send_message(self):
        user_input = self.user_input.text().strip()
        if user_input:
            self.handler.send_message(user_input)
            self.user_input.clear()
            self._refresh_display()

    def _clear_chat(self):
        self.handler.clear_history()
        self._refresh_display()

    def _open_new_agent_dialog(self):
        dialog = AgentEditor(self.agent_manager, self)
        if dialog.exec_():
            self.agent_names = self.agent_manager.list_agents()
            self.agent_dropdown.clear()
            self.agent_dropdown.addItems(self.agent_names)

            if self.agent_names:
                self._set_active_agent(self.agent_names[-1])

    def _open_edit_agent_dialog(self):
        name = self.agent_dropdown.currentText()
        dialog = AgentEditor(self.agent_manager, self, edit_mode=True, agent_name=name)
        if dialog.exec_():
            self.agent_names = self.agent_manager.list_agents()
            self.agent_dropdown.clear()
            self.agent_dropdown.addItems(self.agent_names)

    def _delete_agent(self):
        name = self.agent_dropdown.currentText()
        if not name:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Confirm Delete",
                                                 f"Are you sure you want to delete '{name}'?",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            self.agent_manager.delete_agent(name)
            self.agent_names = self.agent_manager.list_agents()
            self.agent_dropdown.clear()
            self.agent_dropdown.addItems(self.agent_names)
            if self.agent_names:
                self._set_active_agent(self.agent_names[0])
            else:
                self.chat_display.setHtml("")


def launch_interface(agent_manager):
    app = QApplication(sys.argv)
    window = ChatInterface(agent_manager)
    window.show()
    sys.exit(app.exec_())