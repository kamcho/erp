import paramiko
from pathlib import Path

HOST = "137.184.137.222"
PASSWORD = "141778215aA!A"
REMOTE = "/var/www/excel-schools"
LOCAL = Path(r"c:\Users\USER\Downloads\ERPv1\SMS-main")
files = [
    "core/views.py",
    "core/urls.py",
    "core/templates/core/class_detail.html",
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=PASSWORD, timeout=30)
sftp = c.open_sftp()
for rel in files:
    local = LOCAL / rel
    assert local.exists(), rel
    print("UPLOAD", rel, local.stat().st_size)
    sftp.put(str(local), f"{REMOTE}/{rel}")
sftp.close()

stdin, stdout, stderr = c.exec_command(
    "systemctl restart gunicorn && sleep 2 && systemctl is-active gunicorn"
)
print("gunicorn:", stdout.read().decode().strip(), stderr.read().decode().strip())

stdin, stdout, stderr = c.exec_command(
    "grep -n 'roster-quick-edit' /var/www/excel-schools/core/urls.py; "
    "grep -c 'roster-quick-edit-modal' /var/www/excel-schools/core/templates/core/class_detail.html; "
    "grep -c 'def roster_quick_edit' /var/www/excel-schools/core/views.py"
)
print(stdout.read().decode())
print(stderr.read().decode())
c.close()
print("DONE")
