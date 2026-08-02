import sys
import subprocess
import os
import platform
import getpass
import mysql.connector

def check_mysql_installed():
    """Check if MySQL is installed"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['where', 'mysql'], capture_output=True)
        else:
            result = subprocess.run(['which', 'mysql'], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def install_mysql():
    """Install MySQL based on the operating system"""
    system = platform.system()
    
    if system == "Windows":
        print("Please download and install MySQL from: https://dev.mysql.com/downloads/installer/")
        print("After installation, press Enter to continue...")
        input()
    
    elif system == "Linux":
        distro = platform.linux_distribution()[0].lower()
        if "ubuntu" in distro or "debian" in distro:
            subprocess.run(['sudo', 'apt-get', 'update'])
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mysql-server'])
        elif "fedora" in distro or "redhat" in distro:
            subprocess.run(['sudo', 'dnf', 'install', '-y', 'mysql-server'])
        else:
            print(f"Unsupported Linux distribution: {distro}")
            sys.exit(1)
    
    elif system == "Darwin":  # macOS
        if subprocess.run(['which', 'brew']).returncode == 0:
            subprocess.run(['brew', 'install', 'mysql'])
        else:
            print("Please install Homebrew first: https://brew.sh/")
            sys.exit(1)
    
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

def setup_mysql_database():
    """Set up the CMMS database and user"""
    root_password = getpass.getpass("Enter MySQL root password: ")
    
    try:
        # Connect as root
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=root_password
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS cmms_db")
        
        # Create user and grant privileges
        cursor.execute("CREATE USER IF NOT EXISTS 'CMMS'@'localhost' IDENTIFIED BY 'cmms'")
        cursor.execute("GRANT ALL PRIVILEGES ON cmms_db.* TO 'CMMS'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error setting up database: {err}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def install_python_dependencies():
    """Install required Python packages"""
    requirements = [
        'PySide6',
        'mysql-connector-python',
        # Add other dependencies
    ]
    
    subprocess.run([sys.executable, '-m', 'pip', 'install'] + requirements)

def main():
    print("CMMS Installation Script")
    print("=======================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check and install MySQL if needed
    print("Checking MySQL installation...")
    if not check_mysql_installed():
        print("MySQL not found. Installing...")
        install_mysql()
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    install_python_dependencies()
    
    # Setup MySQL database
    print("Setting up MySQL database...")
    setup_mysql_database()
    
    print("\nInstallation completed successfully!")
    print("You can now run the CMMS application.")

if __name__ == "__main__":
    main()