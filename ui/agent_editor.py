from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
)
import os

class AgentEditor(QDialog):
    def __init__(self, agent_manager, parent=None, edit_mode=False, agent_name=None):
        super().__init__(parent)
        self.agent_manager = agent_manager
        self.edit_mode = edit_mode
        self.agent_name = agent_name
        self.setWindowTitle("Edit Agent" if edit_mode else "Create New Agent")
        self.setMinimumWidth(400)
        self.folder_path = ""

        self._build_ui()
        if edit_mode and agent_name:
            self._load_agent(agent_name)

    def _build_ui(self):
        layout = QVBoxLayout()

        # Agent name
        layout.addWidget(QLabel("Agent Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Base prompt
        layout.addWidget(QLabel("Base Prompt:"))
        self.prompt_input = QTextEdit()
        layout.addWidget(self.prompt_input)

        # Folder picker (only in create mode)
        if not self.edit_mode:
            folder_layout = QHBoxLayout()
            self.folder_label = QLabel("No folder selected")
            folder_btn = QPushButton("Select Folder")
            folder_btn.clicked.connect(self._select_folder)
            folder_layout.addWidget(self.folder_label)
            folder_layout.addWidget(folder_btn)
            layout.addLayout(folder_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Save Changes" if self.edit_mode else "Create Agent")
        self.submit_btn.clicked.connect(self._edit_agent if self.edit_mode else self._create_agent)
        btn_layout.addWidget(self.submit_btn)

        if self.edit_mode:
            delete_btn = QPushButton("Delete Agent")
            delete_btn.clicked.connect(self._delete_agent)
            btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Knowledge Folder")
        if path:
            self.folder_path = path
            self.folder_label.setText(os.path.basename(path))

    def _create_agent(self):
        name = self.name_input.text().strip()
        prompt = self.prompt_input.toPlainText().strip()

        if not name or not prompt or not self.folder_path:
            QMessageBox.warning(self, "Incomplete Info", "Please fill all fields and select a folder.")
            return

        if name in self.agent_manager.list_agents():
            QMessageBox.warning(self, "Duplicate Agent", f"Agent '{name}' already exists.")
            return

        try:
            self.agent_manager.create_agent(
                name=name,
                base_prompt=prompt,
                llm_choice="deepseek",
                ingest_path=self.folder_path
            )
            QMessageBox.information(self, "Agent Created", f"Agent '{name}' successfully created.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create agent: {str(e)}")

    def _load_agent(self, agent_name):
        agent_config = self.agent_manager.get_agent_config(agent_name)
        self.name_input.setText(agent_name)
        self.name_input.setDisabled(True)
        self.prompt_input.setText(agent_config.get("base_prompt", ""))

    def _edit_agent(self):
        new_prompt = self.prompt_input.toPlainText().strip()
        if not new_prompt:
            QMessageBox.warning(self, "Missing Prompt", "Base prompt cannot be empty.")
            return

        try:
            self.agent_manager.update_agent_prompt(self.agent_name, new_prompt)
            QMessageBox.information(self, "Updated", f"Prompt for '{self.agent_name}' updated.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update agent: {str(e)}")

    def _delete_agent(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete agent '{self.agent_name}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.agent_manager.delete_agent(self.agent_name)
                QMessageBox.information(self, "Deleted", f"Agent '{self.agent_name}' deleted.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete agent: {str(e)}")