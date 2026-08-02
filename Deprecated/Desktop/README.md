# CMMS Installation Guide

## Prerequisites
- Windows, Linux, or macOS
- Python 3.8 or higher
- Internet connection for downloading dependencies

## Installation Steps

1. Download the installer package
2. Run the installer:
   - Windows: Double-click `CMMS_installer.exe`
   - Linux/macOS: Open terminal and run `./CMMS_installer`
3. Follow the prompts to:
   - Install MySQL if not present
   - Set up the database
   - Configure initial settings

## Manual Installation

If the installer doesn't work, you can install manually:

1. Install MySQL Server from https://dev.mysql.com/downloads/
2. Run `python install.py` to set up the database and dependencies
3. Run `python main.py` to start the application

## Troubleshooting

If you encounter any issues:
1. Check if MySQL service is running
2. Verify database credentials in config file
3. Check logs in the application directory 