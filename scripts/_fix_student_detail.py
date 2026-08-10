import paramiko
from pathlib import Path

HOST = "137.184.137.222"
PASSWORD = "141778215aA!A"
REMOTE = "/var/www/excel-schools"
LOCAL = Path(r"c:\Users\USER\Downloads\ERPv1\SMS-main")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=PASSWORD, timeout=30)

# Check if cbe_pathways exists on prod
stdin, stdout, stderr = c.exec_command(
    f"ls -la {REMOTE}/core/cbe_pathways.py 2>&1; "
    f"grep -n \"infer_cbe_pathway\\|LoginRequiredMixin\\|AnonymousUser\\|role !=\" {REMOTE}/core/views.py | head -20"
)
print(stdout.read().decode())
print(stderr.read().decode())

sftp = c.open_sftp()
for rel in ["core/views.py", "core/cbe_pathways.py"]:
    local = LOCAL / rel
    if local.exists():
        print("UPLOAD", rel)
        sftp.put(str(local), f"{REMOTE}/{rel}")
    else:
        print("MISSING LOCAL", rel)
sftp.close()

stdin, stdout, stderr = c.exec_command(
    "systemctl restart gunicorn && sleep 1 && systemctl is-active gunicorn"
)
print(stdout.read().decode())
print(stderr.read().decode())
c.close()
print("DONE")
