#!/usr/bin/env python3
"""
Light weight AppImage installer script with proper desktop integration.
Author: HabaneroSpices [admin@habanerospices.com]
Version: 1.0 (Python rewrite)
"""

import argparse
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.logging import RichHandler

# Set up logging
logging.basicConfig(
    level="NOTSET", format='%(message)s', datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)

# Global variables
DESKTOP_FILE_DIR = Path.home() / ".local/share/applications"
ICON_DIR = Path.home() / ".local/share/icons"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Light weight AppImage installer script with proper desktop integration.")
    parser.add_argument("appimage_path", type=Path, help="Path to the AppImage file")
    parser.add_argument("install_directory", nargs='?', type=Path, default=Path.home() / ".local/bin", help="Installation directory (default: ~/.local/bin)")
    parser.add_argument("-v", "--verbose", action='store_true', help="show verbose log output.")
    return parser.parse_args()

def extract_appimage(appimage_path, extract_dir):
    logger.debug("Extracting AppImage...")
    appimage_path.chmod(0o755)
    result = subprocess.run([appimage_path, "--appimage-extract"], cwd=extract_dir, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to extract AppImage: {result.stderr}")
        sys.exit(1)

def find_desktop_and_icon_files(extract_dir):
    desktop_file = next(extract_dir.glob("squashfs-root/*.desktop"), None)
    icon_file = next(extract_dir.glob("squashfs-root/*.png"), None) or next(extract_dir.glob("squashfs-root/*.svg"), None)

    if not desktop_file:
        logger.error("No desktop file found in AppImage.")
        sys.exit(1)

    return desktop_file, icon_file

def install_appimage(temp_appimage, install_dir):
    logger.info(f"Installing AppImage to {install_dir}...")
    install_dir.mkdir(parents=True, exist_ok=True)
    installed_appimage = install_dir / temp_appimage.name
    shutil.move(temp_appimage, installed_appimage)
    return installed_appimage

def install_desktop_file(desktop_file):
    logger.debug("Moving desktop file...")
    DESKTOP_FILE_DIR.mkdir(parents=True, exist_ok=True)
    dest_desktop_file = DESKTOP_FILE_DIR / desktop_file.name
    shutil.copy(desktop_file, dest_desktop_file)
    dest_desktop_file.chmod(0o755)  # This fixes icon issues
    return dest_desktop_file

def install_icon_file(icon_file):
    if icon_file:
        logger.debug("Moving icon file...")
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        dest_icon_file = ICON_DIR / icon_file.name
        if icon_file.is_symlink():
            icon_file = icon_file.resolve()
        shutil.copy(icon_file, dest_icon_file)
        return dest_icon_file
    else:
        logger.warning("No suitable icon file found in AppImage.")
        return None

def update_desktop_file(desktop_file, installed_appimage, icon_file):
    logger.debug("Updating desktop file...")
    with desktop_file.open('r') as f:
        content = f.read()

    content = re.sub(r'Exec=.*(?=\s%)', f'Exec={installed_appimage}', content)
    if icon_file:
        content = re.sub(r'Icon=.*', f'Icon={icon_file}', content)

    # Add uninstall action
    if 'Actions=' in content:
        content = re.sub(r'Actions=.*', lambda m: f'{m.group(0)}Uninstall-Proper;', content)
    else:
        content += '\nActions=Uninstall-Proper;\n'

    content += f"""
[Desktop Action Uninstall-Proper]
Name=Uninstall (Proper)
Exec=/usr/bin/rm -f '{installed_appimage}' '{icon_file if icon_file else ""}' '{desktop_file}'
"""

    with desktop_file.open('w') as f:
        f.write(content)

def main():
    args = parse_arguments()
    appimage_path = args.appimage_path.resolve()
    install_dir = args.install_directory.resolve()

    if not args.verbose:
        logger.setLevel("INFO")

    if not appimage_path.is_file():
        logger.error("AppImage file not found.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Copy AppImage to temporary directory
        logger.debug("Copying AppImage to temporary directory...")
        temp_appimage = temp_dir / appimage_path.name
        shutil.copy(appimage_path, temp_appimage)

        # Extract AppImage
        extract_appimage(temp_appimage, temp_dir)

        # Find desktop file and icon
        desktop_file, icon_file = find_desktop_and_icon_files(temp_dir)

        # Install AppImage
        installed_appimage = install_appimage(temp_appimage, install_dir)

        # Install desktop file and icon
        dest_desktop_file = install_desktop_file(desktop_file)
        dest_icon_file = install_icon_file(icon_file)

        # Update desktop file
        update_desktop_file(dest_desktop_file, installed_appimage, dest_icon_file)

    logger.info("Installation complete!")

if __name__ == "__main__":
    main()