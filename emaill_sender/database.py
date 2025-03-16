import sqlite3

class Database:
    def __init__(self, db_name="email_sender.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Cria as tabelas necessárias no banco de dados."""
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS smtp_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)

    def save_smtp_config(self, server, port, email, password):
        """Salva as configurações SMTP no banco de dados."""
        with self.connection:
            self.connection.execute("DELETE FROM smtp_config")  # Remove configurações antigas
            self.connection.execute("""
                INSERT INTO smtp_config (server, port, email, password)
                VALUES (?, ?, ?, ?)
            """, (server, port, email, password))

    def load_smtp_config(self):
        """Carrega as configurações SMTP do banco de dados."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT server, port, email, password FROM smtp_config LIMIT 1")
        return cursor.fetchone()

    def save_contact(self, name, email):
        """Salva um contato no banco de dados."""
        with self.connection:
            self.connection.execute("""
                INSERT INTO contacts (name, email)
                VALUES (?, ?)
            """, (name, email))

    def load_contacts(self):
        """Carrega todos os contatos do banco de dados."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, email FROM contacts")
        return cursor.fetchall()

    def save_log(self, timestamp, message):
        """Salva um log no banco de dados."""
        with self.connection:
            self.connection.execute("""
                INSERT INTO logs (timestamp, message)
                VALUES (?, ?)
            """, (timestamp, message))

    def load_logs(self):
        """Carrega todos os logs do banco de dados."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT timestamp, message FROM logs")
        return cursor.fetchall()