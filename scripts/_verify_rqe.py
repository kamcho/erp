import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("137.184.137.222", username="root", password="141778215aA!A", timeout=30)
stdin, stdout, stderr = c.exec_command(
    "python3 - <<'PY'\n"
    "from pathlib import Path\n"
    "t = Path('/var/www/excel-schools/core/views.py').read_text()\n"
    "i = t.find(\"'needs_confirm'\")\n"
    "print(t[i:i+400])\n"
    "html = Path('/var/www/excel-schools/core/templates/core/class_detail.html').read_text()\n"
    "print('modal', 'roster-quick-edit-modal' in html)\n"
    "print('js', 'confirm_link' in html)\n"
    "PY"
)
print(stdout.read().decode())
print(stderr.read().decode())
c.close()
