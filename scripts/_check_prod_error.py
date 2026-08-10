import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("137.184.137.222", username="root", password="141778215aA!A", timeout=30)

cmds = [
    "journalctl -u gunicorn -n 80 --no-pager",
    "tail -80 /var/www/excel-schools/logs/*.log 2>/dev/null; ls /var/www/excel-schools/*.log 2>/dev/null; ls /var/log/gunicorn* 2>/dev/null; ls /var/www/excel-schools/logs/ 2>/dev/null",
]
for cmd in cmds:
    print("====", cmd)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=60)
    print(stdout.read().decode(errors="replace")[-8000:])
    err = stderr.read().decode(errors="replace")
    if err.strip():
        print(err[-2000:])
c.close()
