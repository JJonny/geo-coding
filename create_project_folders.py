from pathlib import Path
import os
import stat

from app import Config


default_paths = [
    Config.UPLOAD_FOLDER,
    Config.DB_DATA_FOLDER,
]


def create_directories_with_permissions(paths: list[str] = None):
    if paths is None:
        paths = default_paths

    for path in paths:
        directory = Path(path)

        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")

        if os.name == 'nt':  # win
            os.chmod(directory, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        else:
            os.chmod(directory, 0o777)
        print(f"Set full permissions for: {directory}")


if __name__ == '__main__':
    create_directories_with_permissions()
