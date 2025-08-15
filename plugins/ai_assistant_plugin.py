import asyncio
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QFormLayout, QHBoxLayout, QLabel, QPlainTextEdit, QGroupBox,
    QMessageBox
)

from core.ai_agent import AiAgent
from core.utils import get_config, parse_commands
from core.commands_handler import handle_command
from core.imap_handler import MailMonitor


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


class AsyncPluginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.task = None

        layout = QVBoxLayout()
        cfg = get_config()

        field_labels = {
            "perplexity_api_token": "Perplexity API Token",
            "admin_email": "Admin Email",
            "assistant_email": "Assistant Email",
            "assistant_email_password": "Assistant Email Password",
            "imap_server": "IMAP Server",
            "smtp_server": "SMTP Server",
            "smtp_port": "SMTP Port",
        }

        conn_group = QGroupBox("🔑 Connection Settings")
        conn_form = QFormLayout()
        self.inputs = {}

        for key in field_labels:
            line = QLineEdit(str(cfg.get(key, "")))
            if "password" in key.lower():
                line.setEchoMode(QLineEdit.EchoMode.Password)
            self.inputs[key] = line
            conn_form.addRow(QLabel(field_labels[key]), line)

        conn_group.setLayout(conn_form)
        layout.addWidget(conn_group)

        prompt_group = QGroupBox("📝 Start Prompt")
        prompt_layout = QVBoxLayout()
        self.start_prompt_edit = QPlainTextEdit(cfg.get("start_prompt", ""))
        self.start_prompt_edit.setPlaceholderText("Enter the system prompt for the assistant...")
        prompt_layout.addWidget(self.start_prompt_edit)
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start")
        self.stop_btn = QPushButton("⏹ Stop")
        self.save_btn = QPushButton("💾 Save Settings")
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

        self.start_btn.clicked.connect(self.start_task)
        self.stop_btn.clicked.connect(self.stop_task)
        self.save_btn.clicked.connect(self.save_config)

        self.update_buttons()

    def update_buttons(self):
        running = self.task is not None and not self.task.done()
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)

    async def start_monitoring(self) -> None:
        cfg = get_config()
        ai_agent = AiAgent(
            api_key=cfg['perplexity_api_token'],
            start_prompt=cfg['start_prompt']
        )
        mails_monitor = MailMonitor(
            email_addr=cfg['assistant_email'],
            password=cfg['assistant_email_password'],
            imap_server=cfg['imap_server'],
            folder='INBOX',
            search_criteria='UNSEEN',
            check_interval=10,
        )

        while True:
            async for mail in mails_monitor.fetch_new_emails():
                response = await ai_agent.send_message(
                    f'{mail["from"]} sent a message with subject: {mail["subject"]} and body: {mail["body"]}'
                )
                if response == 'ignore':
                    print('ignore')

                commands = parse_commands(response)
                for command in commands:
                    await handle_command(command)

            print('yo')
            await asyncio.sleep(mails_monitor.check_interval)

    async def long_task(self):
        try:
            await self.start_monitoring()
        except asyncio.CancelledError:
            pass
        finally:
            self.task = None
            self.update_buttons()

    def start_task(self):
        if self.task is not None and not self.task.done():
            self.show_message("Warning", "Monitoring is already running.")
            return

        self.task = asyncio.create_task(self.long_task())
        self.update_buttons()
        self.show_message("Task started", "Monitoring started successfully.")

    def stop_task(self):
        if self.task is None or self.task.done():
            self.show_message("Warning", "Monitoring is not running.")
            return

        self.task.cancel()
        self.update_buttons()
        self.show_message("Task stopped", "Monitoring stopped successfully.")

    def save_config(self):
        new_cfg = {k: inp.text() for k, inp in self.inputs.items()}
        new_cfg["start_prompt"] = self.start_prompt_edit.toPlainText()

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(new_cfg, f, ensure_ascii=False, indent=4)

        self.show_message("Settings saved", "Configuration saved successfully.")

    def show_message(self, title: str, text: str):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()


def get_name():
    return "AI Assistant"

def get_widget():
    return AsyncPluginWidget()
