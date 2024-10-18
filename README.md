# AppImage Installer

A lightweight Python script for installing AppImages with proper desktop integration on Linux.

## Features

- Installs AppImages to a specified directory (defaults to `~/.local/bin`)
- Creates desktop entries for easy application launching
- Adds an uninstall option to the desktop entry
- Handles icon installation

## Requirements

- Python 3.6 or higher
- python package: rich
- Linux DE eg. Cinnamon

## Installation

1. Clone this repository or download the `appimage_installer.py` script.
2. Make the script executable:

```bash
chmod +x appimage_installer.py
```

## Usage

```bash
./appimage_installer.py <path_to_appimage> [install_directory]
```

- `<path_to_appimage>`: The path to the AppImage file you want to install.
- `[install_directory]`: (Optional) The directory where you want to install the AppImage. If not specified, it defaults to `~/.local/bin`.

Example:

```bash
./appimage_installer.py ~/Downloads/MyApp.AppImage
```

## What it does

1. Copies the AppImage to the specified install directory
2. Extracts the AppImage to find the `.desktop` file and icon
3. Installs the desktop file to `~/.local/share/applications`
4. Installs the icon to `~/.local/share/icons`
5. Updates the desktop file with the correct paths
6. Adds an uninstall action to the desktop file

## Uninstalling

To uninstall an application installed with this script, right-click on the application's entry in your DE's application menu and click "Uninstall (Proper)".
