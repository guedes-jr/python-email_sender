from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QToolBar, QAction, QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, QMessageBox
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt
import csv
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Sender")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
    
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
        
        # Aba de Configuração SMTP
        self.smtp_tab = QWidget()
        self.init_smtp_tab()
        self.tabs.addTab(self.smtp_tab, "Configuração SMTP")
    
    def init_email_tab(self):
        layout = QVBoxLayout()
        
        # Criar barra de ferramentas
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Botões de formatação
        bold_action = QAction("B", self)
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)
        
        italic_action = QAction("I", self)
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)
        
        underline_action = QAction("U", self)
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)
        
        # Editor de texto
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Escreva sua mensagem aqui...")
        layout.addWidget(self.text_editor)
        
        # Botão de envio
        self.send_button = QPushButton("Enviar Email")
        self.send_button.clicked.connect(self.send_email)
        layout.addWidget(self.send_button)
        
        self.email_tab.setLayout(layout)
    
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
        
        layout.addWidget(QLabel("Servidor SMTP:"))
        layout.addWidget(self.smtp_server)
        layout.addWidget(QLabel("Porta:"))
        layout.addWidget(self.smtp_port)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.smtp_email)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.smtp_password)
        
        self.smtp_tab.setLayout(layout)
    
    def send_email(self):
        server = self.smtp_server.text()
        port = self.smtp_port.text()
        sender_email = self.smtp_email.text()
        password = self.smtp_password.text()
        
        if not (server and port and sender_email and password):
            QMessageBox.warning(self, "Erro", "Por favor, preencha todas as configurações SMTP.")
            return
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["Subject"] = "Email Automático"
        message.attach(MIMEText(self.text_editor.toHtml(), "html"))
        
        contacts = [self.contacts_table.item(row, 1).text() for row in range(self.contacts_table.rowCount())]
        
        try:
            with smtplib.SMTP(server, int(port)) as smtp:
                smtp.starttls()
                smtp.login(sender_email, password)
                
                for recipient in contacts:
                    message["To"] = recipient
                    smtp.sendmail(sender_email, recipient, message.as_string())
                
            QMessageBox.information(self, "Sucesso", "Emails enviados com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao enviar email: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = EmailSenderApp()
    window.show()
    app.exec()
