import paramiko
from pathlib import Path

HOST = "137.184.137.222"
PASSWORD = "141778215aA!A"
REMOTE = "/var/www/excel-schools"
LOCAL = Path(r"c:\Users\USER\Downloads\ERPv1\SMS-main")
rel = "core/templates/core/classes_list.html"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=PASSWORD, timeout=30)
sftp = c.open_sftp()
sftp.put(str(LOCAL / rel), f"{REMOTE}/{rel}")
sftp.close()
stdin, stdout, stderr = c.exec_command(
    "systemctl restart gunicorn && sleep 1 && systemctl is-active gunicorn"
)
print(stdout.read().decode(), stderr.read().decode())
c.close()
print("DONE")
