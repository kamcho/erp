import os
import subprocess
import gzip
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Backup the database (SQLite/PostgreSQL), gzip it, and retain only the last 30 backups."

    def add_arguments(self, parser):
        parser.add_argument(
            '--retention-limit',
            type=int,
            default=30,
            help='Number of backup files to keep (default: 30)'
        )

    def handle(self, *args, **options):
        retention_limit = options['retention_limit']
        
        # 1. Establish backups directory
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Created backup directory at: {backup_dir}"))

        # 2. Get database configuration
        db_config = settings.DATABASES.get('default')
        if not db_config:
            raise CommandError("No 'default' database configuration found in settings.")

        engine = db_config.get('ENGINE')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        self.stdout.write(f"Starting backup for database engine: {engine}...")

        try:
            if 'sqlite3' in engine:
                db_path = db_config.get('NAME')
                if not db_path:
                    raise CommandError("SQLite 'NAME' database path not set in settings.")
                
                db_path_str = str(db_path)
                if not os.path.exists(db_path_str):
                    raise CommandError(f"SQLite database file not found at: {db_path_str}")

                backup_filename = f"db_backup_{timestamp}.sqlite3.gz"
                backup_file_path = os.path.join(backup_dir, backup_filename)

                self.stdout.write(f"Copying and compressing SQLite database: {db_path_str}...")
                with open(db_path_str, 'rb') as f_in:
                    with gzip.open(backup_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                self.stdout.write(self.style.SUCCESS(f"Backup created successfully: {backup_file_path}"))

            elif 'postgresql' in engine:
                db_name = db_config.get('NAME')
                db_user = db_config.get('USER')
                db_password = db_config.get('PASSWORD')
                db_host = db_config.get('HOST')
                db_port = db_config.get('PORT')

                backup_filename = f"db_backup_{timestamp}.sql.gz"
                backup_file_path = os.path.join(backup_dir, backup_filename)

                # Set up command for pg_dump
                cmd = ['pg_dump']
                if db_host:
                    cmd.extend(['-h', db_host])
                if db_port:
                    cmd.extend(['-p', str(db_port)])
                if db_user:
                    cmd.extend(['-U', db_user])
                
                cmd.extend(['-d', db_name])

                # Set password via PGPASSWORD environment variable to prevent prompt
                env = os.environ.copy()
                if db_password:
                    env['PGPASSWORD'] = db_password

                self.stdout.write(f"Running pg_dump for PostgreSQL database '{db_name}'...")
                
                # We execute pg_dump and stream output directly into gzip file to handle large DBs efficiently
                with gzip.open(backup_file_path, 'wb') as f_out:
                    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    shutil.copyfileobj(process.stdout, f_out)
                    process.wait()

                    if process.returncode != 0:
                        # Clean up failed backup file if any
                        if os.path.exists(backup_file_path):
                            os.remove(backup_file_path)
                        stderr_output = process.stderr.read().decode('utf-8')
                        raise CommandError(f"pg_dump failed: {stderr_output}")

                self.stdout.write(self.style.SUCCESS(f"Backup created successfully: {backup_file_path}"))

            else:
                raise CommandError(f"Database engine '{engine}' is not currently supported for automated backup.")

            # 3. Clean up / Retention mechanism
            self.stdout.write(f"Checking backup retention (limit: {retention_limit})...")
            backups = [
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if os.path.isfile(os.path.join(backup_dir, f)) and f.startswith("db_backup_")
            ]
            # Sort backups by modification time (oldest first)
            backups.sort(key=os.path.getmtime)

            if len(backups) > retention_limit:
                num_to_delete = len(backups) - retention_limit
                self.stdout.write(f"Found {len(backups)} backups. Pruning the oldest {num_to_delete} backup(s)...")
                for i in range(num_to_delete):
                    old_backup_path = backups[i]
                    try:
                        os.remove(old_backup_path)
                        self.stdout.write(self.style.WARNING(f"Deleted old backup: {os.path.basename(old_backup_path)}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Failed to delete {os.path.basename(old_backup_path)}: {str(e)}"))
            else:
                self.stdout.write(self.style.SUCCESS("Backup count within retention limit. No pruning required."))

        except Exception as e:
            if not isinstance(e, CommandError):
                raise CommandError(f"Backup process failed: {str(e)}")
            raise e
