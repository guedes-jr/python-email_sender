## create a new repository on the command line

```bash
echo "# python-email_sender" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/guedes-jr/python-email_sender.git
git push -u origin main
```

---

## push an existing repository from the command line

```bash
git remote add origin https://github.com/guedes-jr/python-email_sender.git
git branch -M main
git push -u origin main
```