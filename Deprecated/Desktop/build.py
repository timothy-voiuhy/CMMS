import PyInstaller.__main__
import os

def create_installer():
    PyInstaller.__main__.run([
        'main.py',
        '--name=CMMS',
        '--onefile',
        '--windowed',
        '--add-data=resources/*:resources',
        '--icon=resources/icon.ico',
        '--hidden-import=mysql.connector',
    ])

if __name__ == "__main__":
    create_installer()