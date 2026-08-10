"""One-shot: set each Guardian password to their phone number on production."""
import paramiko

HOST = "137.184.137.222"
PASSWORD = "141778215aA!A"

REMOTE_SCRIPT = r"""
from users.models import MyUser
qs = MyUser.objects.filter(role='Guardian').exclude(phone_number__isnull=True).exclude(phone_number='')
total = qs.count()
print(f'Found {total} guardians with phone numbers', flush=True)
updated = 0
for g in qs.iterator():
    phone = (g.phone_number or '').strip()
    if not phone:
        continue
    g.set_password(phone)
    g.save(update_fields=['password'])
    updated += 1
    if updated % 25 == 0:
        print(f'  ... {updated}/{total}', flush=True)
print(f'DONE Updated {updated} of {total} guardians.', flush=True)
"""


def main():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username="root", password=PASSWORD, timeout=30)

    # Kill any stuck prior shell if still running from previous attempt
    c.exec_command(
        "pkill -f 'manage.py shell' 2>/dev/null; true",
        timeout=30,
    )

    # Upload and run as a file so progress prints stream
    sftp = c.open_sftp()
    remote_path = "/tmp/set_guardian_passwords.py"
    with sftp.file(remote_path, "w") as f:
        f.write(REMOTE_SCRIPT)
    sftp.close()

    cmd = (
        "cd /var/www/excel-schools && source venv/bin/activate "
        f"&& python manage.py shell < {remote_path}"
    )
    print("Running:", cmd)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=1800)
    # Stream stdout
    for line in iter(stdout.readline, ""):
        if not line:
            break
        print(line, end="")
    err = stderr.read().decode(errors="replace")
    if err.strip():
        print("STDERR:", err[-4000:])
    print("exit:", stdout.channel.recv_exit_status())
    c.exec_command(f"rm -f {remote_path}", timeout=15)
    c.close()


if __name__ == "__main__":
    main()
