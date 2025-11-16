#!/usr/bin/env python3
"""
Automated Database Backup Script for GitHub Actions
This script backs up the database and uploads it to GitHub Releases as an artifact
"""

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    """Main backup function"""
    # Get DATABASE_URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is not set")
        sys.exit(1)

    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backstock_backup_{timestamp}.sql"

    print(f"🔄 Starting database backup...")
    print(f"📁 Backup file: {backup_file}")

    try:
        # Run pg_dump to create backup
        with open(backup_file, "w") as f:
            result = subprocess.run(
                ["pg_dump", database_url],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

        # Get file size
        file_size = backup_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print(f"✅ Backup completed successfully!")
        print(f"   Size: {file_size_mb:.2f} MB")

        # Compress the backup
        print(f"🗜️  Compressing backup...")
        subprocess.run(["gzip", str(backup_file)], check=True)
        compressed_file = backup_file.with_suffix(".sql.gz")
        compressed_size = compressed_file.stat().st_size
        compressed_size_mb = compressed_size / (1024 * 1024)

        print(f"✅ Compressed to {compressed_file.name}")
        print(f"   Size: {compressed_size_mb:.2f} MB")

        # Output for GitHub Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            # Set output for use in subsequent steps
            github_output = os.environ.get("GITHUB_OUTPUT")
            if github_output:
                with open(github_output, "a") as f:
                    f.write(f"backup_file={compressed_file}\n")
                    f.write(f"backup_date={timestamp}\n")

        print("")
        print("✅ Backup process complete!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
