## 1️⃣ Configuração do ambiente
**Instalar as dependências: PyQt6, smtplib, sqlite3, PyInstaller**

```bash
pip install PyQt6
pip install pyinstaller
```

## 2️⃣ Estrutura do projeto
**Vamos organizar os arquivos para manter um código limpo:**

```
/email_sender
  ├── main.py                # Arquivo principal
  ├── ui.py                  # Interface gráfica (PyQt6)
  ├── email_sender.py        # Lógica de envio de e-mails
  ├── database.py            # Banco de dados SQLite (contatos, logs)
  ├── utils.py               # Funções auxiliares (backup, import/export)
  ├── assets/                # Imagens e ícones
  ├── templates/             # Modelos de e-mail prontos
```

## 3️⃣ Criar a interface gráfica (UI) com PyQt6

**Criar uma tela com:**
✅ Editor de texto avançado
✅ Gerenciamento de contatos
✅ Botões para envio e backup
4️⃣ Implementar a funcionalidade de envio de e-mails

**Configurar SMTP para envio**
**Criar suporte a múltiplas contas**
**Suporte a envio agendado**

## 5️⃣ Adicionar logs e backup

**Gerar arquivos CSV, TXT ou JSON com os contatos**
**Registrar logs de envios**

## 6️⃣ Gerar um executável (.exe)

**Usar PyInstaller para criar um `.exe` no final**