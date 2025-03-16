from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget,
    QToolBar, QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLineEdit, QLabel, QMessageBox, QDateTimeEdit
)
from PyQt6.QtGui import QFont, QTextCursor, QAction
from PyQt6.QtCore import Qt, QDateTime, QTimer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import Database
import smtplib
import csv
import json
import re

def is_valid_email(email):
    """Valida o formato do email."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


class EmailSenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Email Sender")
        self.scheduled_emails = []
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

        # Inicializa o timer para verificar emails agendados
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_scheduled_emails)
        self.timer.start(60000)  # Verifica a cada 60 segundos

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Aba do Editor de Texto
        self.email_tab = QWidget()
        self.init_email_tab()
        self.tabs.addTab(self.email_tab, "Editor de Email")
        
        # Aba de Gerenciamento de Contatos
        self.contacts_tab = QWidget()
        self.init_contacts_tab()
        self.tabs.addTab(self.contacts_tab, "Contatos")

        self.load_contacts()
        
        # Aba de Configuração SMTP
        self.smtp_tab = QWidget()
        self.init_smtp_tab()
        self.tabs.addTab(self.smtp_tab, "Configuração SMTP")

        # Carrega as configurações SMTP após inicializar os widgets
        self.load_smtp_config()

        # Aba de Logs
        self.logs_tab = QWidget()
        self.init_logs_tab()
        self.tabs.addTab(self.logs_tab, "Logs")

        self.load_logs()
    
    def set_bold(self):
        """Define o texto selecionado como negrito."""
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontWeight(QFont.Weight.Bold if fmt.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        cursor.setCharFormat(fmt)

    def set_italic(self):
        """Define o texto selecionado como itálico."""
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.setCharFormat(fmt)

    def set_underline(self):
        """Define o texto selecionado como sublinhado."""
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        cursor.setCharFormat(fmt)

    def load_contacts(self):
        contacts = self.db.load_contacts()
        for name, email in contacts:
            row_position = self.contacts_table.rowCount()
            self.contacts_table.insertRow(row_position)
            self.contacts_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.contacts_table.setItem(row_position, 1, QTableWidgetItem(email))

    def init_email_tab(self):
        layout = QVBoxLayout()
        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        bold_action = QAction("B", self)
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)
        
        italic_action = QAction("I", self)
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)
        
        underline_action = QAction("U", self)
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)
        
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Escreva sua mensagem aqui...")
        layout.addWidget(self.text_editor)
        
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        layout.addWidget(QLabel("Agendar envio para:"))
        layout.addWidget(self.datetime_edit)
        
        self.schedule_button = QPushButton("Agendar Envio")
        self.schedule_button.clicked.connect(self.schedule_email)
        layout.addWidget(self.schedule_button)
        
        self.send_button = QPushButton("Enviar Email Agora")
        self.send_button.clicked.connect(self.send_email)
        layout.addWidget(self.send_button)
        
        self.email_tab.setLayout(layout)
    
    def schedule_email(self):
        send_time = self.datetime_edit.dateTime()
        email_content = self.text_editor.toHtml()
        self.scheduled_emails.append((send_time, email_content))
        self.log_message(f"Email agendado para {send_time.toString('yyyy-MM-dd HH:mm:ss')}")
    
    def check_scheduled_emails(self):
        current_time = QDateTime.currentDateTime()
        for scheduled in self.scheduled_emails[:]:
            send_time, email_content = scheduled
            if send_time <= current_time:
                self.send_email(email_content)
                self.scheduled_emails.remove(scheduled)
    
    def load_smtp_config(self):
        config = self.db.load_smtp_config()
        if config:
            server, port, email, password = config
            self.smtp_server.setText("smtp.gmail.com")
            self.smtp_port.setText("587")  # Use 465 para SSL
            self.smtp_email.setText("joaog.tsmx@gmail.com")
            self.smtp_password.setText("pbwr hoil aasu ekbb")
            """
            self.smtp_server.setText(server)
            self.smtp_port.setText(str(port))
            self.smtp_email.setText(email)
            self.smtp_password.setText(password)"
            """

    def save_smtp_config(self):
        server = self.smtp_server.text()
        port = self.smtp_port.text()
        email = self.smtp_email.text()
        password = self.smtp_password.text()

        if not (server and port and email and password):
            QMessageBox.warning(self, "Erro", "Por favor, preencha todas as configurações SMTP.")
            return

        self.db.save_smtp_config(server, int(port), email, password)
        QMessageBox.information(self, "Sucesso", "Configurações SMTP salvas com sucesso!")

    def send_email(self, email_content=None):
        if email_content is None:
            # Obtém o texto puro do editor
            email_content = self.text_editor.toPlainText().strip()
    
        # Garante que email_content seja uma string válida
        if not email_content or email_content.lower() == "false":
            QMessageBox.warning(self, "Erro", "O conteúdo do email está vazio. Por favor, escreva algo antes de enviar.")
            return
    
        server = self.smtp_server.text()
        port = self.smtp_port.text()
        sender_email = self.smtp_email.text()
        password = self.smtp_password.text()
    
        if not (server and port and sender_email and password):
            QMessageBox.warning(self, "Erro", "Por favor, preencha todas as configurações SMTP.")
            return
    
        contacts = [self.contacts_table.item(row, 1).text() for row in range(self.contacts_table.rowCount())]
    
        try:
            with smtplib.SMTP(server, int(port)) as smtp:
                smtp.starttls()
                smtp.login(sender_email, password)
    
                for recipient in contacts:
                    # Cria um novo objeto MIMEMultipart para cada destinatário
                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = recipient
                    message["Subject"] = "Email Automático"
                    message.attach(MIMEText(email_content, "html"))
    
                    smtp.sendmail(sender_email, recipient, message.as_string())
    
                QMessageBox.information(self, "Sucesso", "Emails enviados com sucesso!")
                self.log_message("Emails enviados com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao enviar email: {str(e)}")
            self.log_message(f"Erro ao enviar email: {str(e)}")

    def init_contacts_tab(self):
        layout = QVBoxLayout()
        
        # Campo de entrada para nome e e-mail
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.add_contact_button = QPushButton("Adicionar")
        self.add_contact_button.clicked.connect(self.add_contact)
        
        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Email:"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.add_contact_button)
        layout.addLayout(form_layout)
        
        # Tabela de contatos
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(2)
        self.contacts_table.setHorizontalHeaderLabels(["Nome", "Email"])
        layout.addWidget(self.contacts_table)
        
        self.contacts_tab.setLayout(layout)

    def add_contact(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
    
        if not name or not email:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos Nome e Email.")
            return
    
        if not is_valid_email(email):
            QMessageBox.warning(self, "Erro", "Por favor, insira um email válido.")
            return
    
        self.db.save_contact(name, email)
    
        row_position = self.contacts_table.rowCount()
        self.contacts_table.insertRow(row_position)
        self.contacts_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.contacts_table.setItem(row_position, 1, QTableWidgetItem(email))
    
        self.name_input.clear()
        self.email_input.clear()
        self.log_message(f"Contato adicionado: {name} <{email}>")
    
    def init_smtp_tab(self):
        layout = QVBoxLayout()
        
        self.smtp_server = QLineEdit()
        self.smtp_server.setPlaceholderText("SMTP Server")
        self.smtp_port = QLineEdit()
        self.smtp_port.setPlaceholderText("SMTP Port")
        self.smtp_email = QLineEdit()
        self.smtp_email.setPlaceholderText("Email")
        self.smtp_password = QLineEdit()
        self.smtp_password.setPlaceholderText("Senha")
        self.smtp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.save_smtp_button = QPushButton("Salvar Configurações")
        self.save_smtp_button.clicked.connect(self.save_smtp_config)
        
        layout.addWidget(QLabel("Servidor SMTP:"))
        layout.addWidget(self.smtp_server)
        layout.addWidget(QLabel("Porta:"))
        layout.addWidget(self.smtp_port)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.smtp_email)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.smtp_password)
        layout.addWidget(self.save_smtp_button)
        
        self.smtp_tab.setLayout(layout)
    
    def init_logs_tab(self):
        layout = QVBoxLayout()
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)
        self.logs_tab.setLayout(layout)
    
    def log_message(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.logs_text.append(f"[{timestamp}] {message}")
        self.db.save_log(timestamp, message)
    
    def load_logs(self):
        """Carrega os logs do banco de dados e exibe na aba de logs."""
        logs = self.db.load_logs()
        for timestamp, message in logs:
            self.logs_text.append(f"[{timestamp}] {message}")


if __name__ == "__main__":
    app = QApplication([])
    window = EmailSenderApp()
    window.show()
    app.exec()