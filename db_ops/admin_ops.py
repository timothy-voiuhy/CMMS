class AdminOps:
    def __init__(self, db_manager):
        """
        Initialize AdminOps with a reference to the parent database manager
        
        Args:
            db_manager: The parent DatabaseManager instance
        """
        self.db_manager = db_manager
        self.console_logger = db_manager.console_logger
        
    def connect(self):
        """Use the parent's connection method"""
        return self.db_manager.connect()
        
    def close(self, connection):
        """Use the parent's close method"""
        return self.db_manager.close(connection)
    
    def verify_admin_password(self, password):
        """
        Verify if the provided password is valid for admin access.
        Initially checks against a default password, then against stored admin user credentials.
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First check if the admin_users table exists
            cursor.execute("SHOW TABLES LIKE 'admin_users'")
            if not cursor.fetchone():
                # If no admin_users table, check if this is the default admin password
                return password == "admin"  # Default password for first-time access
            
            # Query the admin_users table
            cursor.execute("""
                SELECT user_id, password_hash, username 
                FROM admin_users 
                WHERE active = 1
                LIMIT 1
            """)
            
            admin = cursor.fetchone()
            if not admin:
                # If no active admin users found, allow access with default password
                return password == "admin"
            
            # Get user_id and stored password hash
            user_id = admin[0]
            stored_hash = admin[1]
            username = admin[2]
            
            # If stored hash is in the old format (direct string comparison)
            if isinstance(stored_hash, str) and len(stored_hash) < 64:
                result = (password == stored_hash)
            else:
                # Modern password verification with salt
                try:
                    # Split salt and hash
                    salt = stored_hash[:32]
                    hash_part = stored_hash[32:]
                    
                    # Verify password
                    import hashlib
                    
                    hash_obj = hashlib.pbkdf2_hmac(
                        'sha256',
                        password.encode('utf-8'),
                        salt,
                        100000
                    )
                    
                    result = (hash_part == hash_obj)
                except Exception:
                    # Fallback to direct comparison if something goes wrong
                    result = (password == "admin")
            
            # If login successful, update last login time
            if result:
                cursor.execute("""
                    UPDATE admin_users 
                    SET last_login = NOW(), login_attempts = 0
                    WHERE user_id = %s
                """, (user_id,))
                
                # Log successful login
                self.add_audit_log_entry(
                    username=username,
                    action="Admin Login",
                    details=f"Admin user {username} logged in",
                    status="Success"
                )
            else:
                # Increment login attempts
                cursor.execute("""
                    UPDATE admin_users 
                    SET login_attempts = login_attempts + 1
                    WHERE user_id = %s
                """, (user_id,))
                
                # Check if account should be locked (5+ failed attempts)
                cursor.execute("""
                    UPDATE admin_users 
                    SET locked = 1
                    WHERE user_id = %s AND login_attempts >= 5
                """, (user_id,))
                
                # Log failed login attempt
                self.add_audit_log_entry(
                    username=username,
                    action="Admin Login",
                    details=f"Failed login attempt for admin user {username}",
                    status="Failure"
                )
            
            connection.commit()
            return result
            
        except Exception as e:
            self.console_logger.error(f"Error verifying admin password: {e}")
            # For security, return False on any error
            return False
        finally:
            self.close(connection)
    
    def create_admin_tables(self):
        """Create the tables needed for the administration module"""
        connection = self.connect()
        cursor = connection.cursor()
        
        try:
            # Admin users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    password_hash VARBINARY(128) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'Administrator',
                    created_date DATETIME NOT NULL,
                    last_login DATETIME,
                    login_attempts INT DEFAULT 0,
                    locked BOOLEAN DEFAULT 0,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Permission categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permission_categories (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description VARCHAR(200)
                )
            """)
            
            # Permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description VARCHAR(200),
                    FOREIGN KEY (category_id) REFERENCES permission_categories(category_id)
                )
            """)
            
            # User permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    user_id INT NOT NULL,
                    permission_id INT NOT NULL,
                    granted BOOLEAN DEFAULT 0,
                    PRIMARY KEY (user_id, permission_id),
                    FOREIGN KEY (user_id) REFERENCES admin_users(user_id),
                    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
                )
            """)
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    ip_address VARCHAR(45),
                    action VARCHAR(50) NOT NULL,
                    details TEXT,
                    status VARCHAR(20)
                )
            """)
            
            # System settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    setting_id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(50) NOT NULL UNIQUE,
                    setting_value TEXT,
                    setting_type VARCHAR(20),
                    description VARCHAR(200),
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by VARCHAR(50)
                )
            """)
            
            # Backup history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_history (
                    backup_id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    file_size BIGINT,
                    backup_type VARCHAR(50),
                    status VARCHAR(20),
                    details TEXT
                )
            """)
            
            # Backup schedule table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_schedule (
                    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                    enabled BOOLEAN DEFAULT 0,
                    frequency VARCHAR(20) DEFAULT 'Weekly',
                    time TIME DEFAULT '01:00:00',
                    day_of_week VARCHAR(10) DEFAULT 'Monday',
                    day_of_month INT DEFAULT 1,
                    backup_location VARCHAR(255),
                    compression VARCHAR(20) DEFAULT 'Medium',
                    include_attachments BOOLEAN DEFAULT 1,
                    keep_backups INT DEFAULT 10,
                    notify_on_success BOOLEAN DEFAULT 1,
                    notify_on_failure BOOLEAN DEFAULT 1,
                    notification_email VARCHAR(100),
                    last_run DATETIME,
                    next_run DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add default admin user if none exists
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Create admin with password "admin"
                import hashlib
                import os
                
                # Generate a random salt
                salt = os.urandom(32)
                
                # Hash password with salt
                hash_obj = hashlib.pbkdf2_hmac(
                    'sha256',
                    'admin'.encode('utf-8'),
                    salt,
                    100000
                )
                
                # Combine salt and hash for storage
                password_hash = salt + hash_obj
                
                cursor.execute("""
                    INSERT INTO admin_users (
                        username, full_name, email, password_hash, role, created_date
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    'admin',
                    'System Administrator',
                    'admin@example.com',
                    password_hash,
                    'Super Admin'
                ))
            
            # Add default permission categories if none exist
            cursor.execute("SELECT COUNT(*) FROM permission_categories")
            count = cursor.fetchone()[0]
            
            if count == 0:
                categories = [
                    ('System', 'System-wide permissions'),
                    ('Users', 'User management permissions'),
                    ('Equipment', 'Equipment management permissions'),
                    ('Work Orders', 'Work order management permissions'),
                    ('Reports', 'Reporting permissions'),
                    ('Database', 'Database management permissions')
                ]
                
                for category in categories:
                    cursor.execute("""
                        INSERT INTO permission_categories (name, description) 
                        VALUES (%s, %s)
                    """, category)
            
            # Add default permissions if none exist
            cursor.execute("SELECT COUNT(*) FROM permissions")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Get category IDs
                cursor.execute("SELECT category_id, name FROM permission_categories")
                categories = {}
                for row in cursor.fetchall():
                    categories[row[1]] = row[0]
                
                permissions = [
                    # System permissions
                    (categories['System'], 'View System Settings', 'Can view system settings'),
                    (categories['System'], 'Edit System Settings', 'Can edit system settings'),
                    (categories['System'], 'View Audit Log', 'Can view the audit log'),
                    (categories['System'], 'Clear Audit Log', 'Can clear the audit log'),
                    
                    # User permissions
                    (categories['Users'], 'View Users', 'Can view user list'),
                    (categories['Users'], 'Add User', 'Can add new users'),
                    (categories['Users'], 'Edit User', 'Can edit user details'),
                    (categories['Users'], 'Delete User', 'Can delete users'),
                    (categories['Users'], 'Reset Password', 'Can reset user passwords'),
                    
                    # Equipment permissions
                    (categories['Equipment'], 'View Equipment', 'Can view equipment'),
                    (categories['Equipment'], 'Add Equipment', 'Can add new equipment'),
                    (categories['Equipment'], 'Edit Equipment', 'Can edit equipment details'),
                    (categories['Equipment'], 'Delete Equipment', 'Can delete equipment'),
                    
                    # Work order permissions
                    (categories['Work Orders'], 'View Work Orders', 'Can view work orders'),
                    (categories['Work Orders'], 'Create Work Order', 'Can create new work orders'),
                    (categories['Work Orders'], 'Edit Work Order', 'Can edit work orders'),
                    (categories['Work Orders'], 'Delete Work Order', 'Can delete work orders'),
                    (categories['Work Orders'], 'Assign Work Order', 'Can assign work orders'),
                    
                    # Report permissions
                    (categories['Reports'], 'View Reports', 'Can view reports'),
                    (categories['Reports'], 'Create Report', 'Can create new reports'),
                    (categories['Reports'], 'Export Report', 'Can export reports'),
                    
                    # Database permissions
                    (categories['Database'], 'View Database Info', 'Can view database information'),
                    (categories['Database'], 'Backup Database', 'Can backup the database'),
                    (categories['Database'], 'Restore Database', 'Can restore the database'),
                    (categories['Database'], 'Optimize Database', 'Can optimize the database'),
                    (categories['Database'], 'Reset Database', 'Can reset the database')
                ]
                
                for permission in permissions:
                    cursor.execute("""
                        INSERT INTO permissions (category_id, name, description) 
                        VALUES (%s, %s, %s)
                    """, permission)
            
            connection.commit()
            self.console_logger.info("Admin tables created successfully")
            return True
            
        except Exception as e:
            self.console_logger.error(f"Error creating admin tables: {e}")
            connection.rollback()
            return False
        finally:
            self.close(connection)
    
    def add_audit_log_entry(self, username, action, details=None, status="Success", ip_address=None):
        """
        Add an entry to the audit log.
        
        Args:
            username: The username of the user performing the action
            action: The action performed
            details: Additional details about the action
            status: Success or Failure
            ip_address: The IP address of the user
            
        Returns:
            Boolean indicating success
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First check if the audit_log table exists, create it if not
            cursor.execute("SHOW TABLES LIKE 'audit_log'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        log_id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        ip_address VARCHAR(45),
                        action VARCHAR(50) NOT NULL,
                        details TEXT,
                        status VARCHAR(20)
                    )
                """)
            
            # Insert audit log entry
            cursor.execute("""
                INSERT INTO audit_log (
                    timestamp, username, ip_address, action, details, status
                ) VALUES (NOW(), %s, %s, %s, %s, %s)
            """, (
                username,
                ip_address,
                action,
                details,
                status
            ))
            
            connection.commit()
            return True
        except Exception as e:
            self.console_logger.error(f"Error adding audit log entry: {e}")
            return False
        finally:
            self.close(connection)
    
    def get_admin_users(self):
        """Get list of admin users"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # First check if admin_users table exists
            cursor.execute("SHOW TABLES LIKE 'admin_users'")
            if not cursor.fetchone():
                self.create_admin_tables()
            
            cursor.execute("""
                SELECT user_id, username, full_name, email, role, 
                       DATE_FORMAT(created_date, '%Y-%m-%d %H:%i') as created_date, 
                       DATE_FORMAT(last_login, '%Y-%m-%d %H:%i') as last_login,
                       locked, active
                FROM admin_users
                ORDER BY username
            """)
            
            users = cursor.fetchall()
            
            return users
        except Exception as e:
            self.console_logger.error(f"Error getting admin users: {e}")
            return []
        finally:
            self.close(connection)
    
    def get_admin_permissions(self, user_id):
        """Get permissions for a specific admin user"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # First check if tables exist
            cursor.execute("SHOW TABLES LIKE 'permission_categories'")
            if not cursor.fetchone():
                self.create_admin_tables()
            
            # Get permission categories
            cursor.execute("SELECT category_id, name FROM permission_categories")
            categories = cursor.fetchall()
            
            # Get permissions by category
            permissions = {}
            for category in categories:
                cursor.execute("""
                    SELECT p.permission_id as id, p.name, 
                           IFNULL(up.granted, 0) as granted
                    FROM permissions p
                    LEFT JOIN user_permissions up ON p.permission_id = up.permission_id
                                                AND up.user_id = %s
                    WHERE p.category_id = %s
                    ORDER BY p.name
                """, (user_id, category['category_id']))
                
                permissions[category['name']] = cursor.fetchall()
            
            return permissions
        except Exception as e:
            self.console_logger.error(f"Error getting admin permissions: {e}")
            return {}
        finally:
            self.close(connection)
    
    def add_admin_user(self, user_data):
        """Add a new admin user"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First check if tables exist
            cursor.execute("SHOW TABLES LIKE 'admin_users'")
            if not cursor.fetchone():
                self.create_admin_tables()
            
            # Hash password for admin_users table
            import hashlib
            import os
            
            # Generate a random salt
            salt = os.urandom(32)
            
            # Hash password with salt
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                user_data['password'].encode('utf-8'),
                salt,
                100000
            )
            
            # Combine salt and hash for storage
            password_hash = salt + hash_obj
            
            # Insert user into admin_users table
            cursor.execute("""
                INSERT INTO admin_users (
                    username, full_name, email, password_hash, role, created_date
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                user_data['username'],
                user_data['full_name'],
                user_data['email'],
                password_hash,
                user_data['role']
            ))
            
            user_id = cursor.lastrowid
            
            # Add permissions if provided
            if 'permissions' in user_data:
                for perm in user_data['permissions']:
                    cursor.execute("""
                        INSERT INTO user_permissions (
                            user_id, permission_id, granted
                        ) VALUES (%s, %s, %s)
                    """, (
                        user_id,
                        perm['id'],
                        perm['granted']
                    ))
            
            # Also add the user to the main users table for Django authentication
            from django.contrib.auth.hashers import make_password
            
            # Create a Django-compatible password hash
            django_password_hash = make_password(user_data['password'])
            
            # Determine if this admin should be a Django superuser
            is_superuser = user_data['role'] == 'Super Admin'
            
            # Insert into users table
            cursor.execute("""
                INSERT INTO users (
                    employee_id, password, role, access_level,
                    is_superuser, is_staff, is_active, 
                    date_joined, first_name, last_name, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
            """, (
                user_data['username'],  # Use username as employee_id
                django_password_hash,
                'cmms_admin',  # Special role for CMMS administrators
                user_data['role'],  # Store the admin role as access_level
                is_superuser,
                True,  # All admins are staff
                True,  # All admins are active
                user_data.get('full_name', '').split(' ')[0] if ' ' in user_data.get('full_name', '') else user_data.get('full_name', ''),  # First name
                user_data.get('full_name', '').split(' ', 1)[1] if ' ' in user_data.get('full_name', '') else '',  # Last name
                user_data['email']
            ))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Add Admin User",
                details=f"Added admin user: {user_data['username']}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error adding admin user: {e}")
            return False
        finally:
            self.close(connection)
    
    def update_admin_user(self, user_data):
        """Update an existing admin user"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get the username for this user_id
            cursor.execute("SELECT username FROM admin_users WHERE user_id = %s", (user_data['user_id'],))
            result = cursor.fetchone()
            if not result:
                return False
            
            username = result[0]
            
            # Update user details in admin_users table
            cursor.execute("""
                UPDATE admin_users SET
                    full_name = %s,
                    email = %s,
                    role = %s
                WHERE user_id = %s
            """, (
                user_data['full_name'],
                user_data['email'],
                user_data['role'],
                user_data['user_id']
            ))
            
            # Update permissions if provided
            if 'permissions' in user_data:
                # First delete existing permissions
                cursor.execute("""
                    DELETE FROM user_permissions
                    WHERE user_id = %s
                """, (user_data['user_id'],))
                
                # Then add new permissions
                for perm in user_data['permissions']:
                    cursor.execute("""
                        INSERT INTO user_permissions (
                            user_id, permission_id, granted
                        ) VALUES (%s, %s, %s)
                    """, (
                        user_data['user_id'],
                        perm['id'],
                        perm['granted']
                    ))
            
            # Also update the user in the main users table
            is_superuser = user_data['role'] == 'Super Admin'
            
            # Split full name into first and last name
            first_name = user_data.get('full_name', '').split(' ')[0] if ' ' in user_data.get('full_name', '') else user_data.get('full_name', '')
            last_name = user_data.get('full_name', '').split(' ', 1)[1] if ' ' in user_data.get('full_name', '') else ''
            
            cursor.execute("""
                UPDATE users SET
                    access_level = %s,
                    is_superuser = %s,
                    first_name = %s,
                    last_name = %s,
                    email = %s
                WHERE employee_id = %s
            """, (
                user_data['role'],
                is_superuser,
                first_name,
                last_name,
                user_data['email'],
                username
            ))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Update Admin User",
                details=f"Updated admin user: {username}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error updating admin user: {e}")
            return False
        finally:
            self.close(connection)
    
    def delete_admin_user(self, user_id):
        """Delete an admin user"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get the username for this user_id
            cursor.execute("SELECT username FROM admin_users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            username = result[0]
            
            # Delete permissions first (foreign key constraint)
            cursor.execute("""
                DELETE FROM user_permissions
                WHERE user_id = %s
            """, (user_id,))
            
            # Delete from admin_users table
            cursor.execute("""
                DELETE FROM admin_users
                WHERE user_id = %s
            """, (user_id,))
            
            # Also delete from users table
            cursor.execute("""
                DELETE FROM users
                WHERE employee_id = %s AND role = 'cmms_admin'
            """, (username,))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Delete Admin User",
                details=f"Deleted admin user: {username}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error deleting admin user: {e}")
            return False
        finally:
            self.close(connection)
    
    def reset_admin_password(self, user_id, new_password):
        """Reset an admin user's password"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get the username for this user_id
            cursor.execute("SELECT username FROM admin_users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            username = result[0]
            
            # Hash password for admin_users table
            import hashlib
            import os
            
            # Generate a random salt
            salt = os.urandom(32)
            
            # Hash password with salt
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                new_password.encode('utf-8'),
                salt,
                100000
            )
            
            # Combine salt and hash for storage
            password_hash = salt + hash_obj
            
            # Update password in admin_users table
            cursor.execute("""
                UPDATE admin_users SET
                    password_hash = %s,
                    login_attempts = 0,
                    locked = 0
                WHERE user_id = %s
            """, (
                password_hash,
                user_id
            ))
            
            # Also update password in users table
            from django.contrib.auth.hashers import make_password
            django_password_hash = make_password(new_password)
            
            cursor.execute("""
                UPDATE users SET
                    password = %s
                WHERE employee_id = %s AND role = 'cmms_admin'
            """, (
                django_password_hash,
                username
            ))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Reset Admin Password",
                details=f"Reset password for admin user: {username}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error resetting admin password: {e}")
            return False
        finally:
            self.close(connection)
    
    def get_database_info(self):
        """Get database information"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get database type and version
            cursor.execute("SELECT VERSION() as version")
            version_result = cursor.fetchone()
            
            # Get total size of database
            cursor.execute("""
                SELECT 
                    table_schema,
                    SUM(data_length + index_length) as size
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                GROUP BY table_schema
            """)
            size_result = cursor.fetchone()
            
            # Get number of tables
            cursor.execute("""
                SELECT COUNT(*) as tables
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
            """)
            tables_result = cursor.fetchone()
            
            db_size = size_result['size'] if size_result else 0
            
            # Format size to human-readable format
            if db_size < 1024:
                size_str = f"{db_size} bytes"
            elif db_size < 1024 * 1024:
                size_str = f"{db_size / 1024:.2f} KB"
            elif db_size < 1024 * 1024 * 1024:
                size_str = f"{db_size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{db_size / (1024 * 1024 * 1024):.2f} GB"
            
            info = {
                'type': 'MySQL',
                'version': version_result['version'] if version_result else 'Unknown',
                'size': size_str,
                'tables': tables_result['tables'] if tables_result else 0
            }
            
            return info
        except Exception as e:
            self.console_logger.error(f"Error getting database info: {e}")
            return {
                'type': 'Unknown',
                'version': 'Unknown',
                'size': 'Unknown',
                'tables': 0
            }
        finally:
            self.close(connection)
    
    def get_database_tables(self):
        """Get list of tables in the database"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            self.console_logger.error(f"Error getting database tables: {e}")
            return []
        finally:
            self.close(connection)
    
    def get_table_info(self, table_name):
        """Get information about a specific table"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get row count - fix the reserved keyword issue
            cursor.execute(f"SELECT COUNT(*) as row_count FROM `{table_name}`")
            rows_result = cursor.fetchone()
            
            # Get table size
            cursor.execute(f"""
                SELECT 
                    data_length + index_length as size
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = %s
            """, (table_name,))
            size_result = cursor.fetchone()
            
            # Get column information
            cursor.execute(f"""
                SELECT 
                    column_name as name,
                    column_type as type,
                    column_key as `key`,
                    is_nullable as nullable,
                    column_default as `default`
                FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cursor.fetchall()
            
            # Get foreign key information
            cursor.execute(f"""
                SELECT
                    column_name,
                    referenced_table_name as ref_table,
                    referenced_column_name as ref_column
                FROM information_schema.key_column_usage
                WHERE table_schema = DATABASE() 
                  AND table_name = %s
                  AND referenced_table_name IS NOT NULL
            """, (table_name,))
            foreign_keys = cursor.fetchall()
            
            # Mark foreign key columns
            for col in columns:
                for fk in foreign_keys:
                    if col['name'] == fk['column_name']:
                        col['key'] = 'FOR'
                        col['ref_table'] = fk['ref_table']
                        col['ref_column'] = fk['ref_column']
            
            # Format size
            table_size = size_result['size'] if size_result else 0
            if table_size < 1024:
                size_str = f"{table_size} bytes"
            elif table_size < 1024 * 1024:
                size_str = f"{table_size / 1024:.2f} KB"
            elif table_size < 1024 * 1024 * 1024:
                size_str = f"{table_size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{table_size / (1024 * 1024 * 1024):.2f} GB"
            
            return {
                'rows': rows_result['row_count'] if rows_result else 0,
                'size': size_str,
                'columns': columns
            }
        except Exception as e:
            self.console_logger.error(f"Error getting table info: {e}")
            return {
                'rows': 0,
                'size': '0 bytes',
                'columns': []
            }
        finally:
            self.close(connection)
    
    def get_table_data(self, table_name, limit=100, search=None, column=None):
        """Get data from a specific table with optional filtering"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Build query with search filter if provided
            query = f"SELECT * FROM `{table_name}`"
            params = []
            
            if search and column:
                query += f" WHERE `{column}` LIKE %s"
                params.append(f"%{search}%")
            elif search:
                # Get all columns for search
                cursor.execute(f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = %s
                """, (table_name,))
                columns = [row['column_name'] for row in cursor.fetchall()]
                
                if columns:
                    search_conditions = []
                    for col in columns:
                        search_conditions.append(f"`{col}` LIKE %s")
                        params.append(f"%{search}%")
                    
                    query += " WHERE " + " OR ".join(search_conditions)
            
            # Add limit
            if limit > 0:
                query += " LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            self.console_logger.error(f"Error getting table data: {e}")
            return []
        finally:
            self.close(connection)
    
    def truncate_table(self, table_name):
        """Truncate (clear) a table"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Truncate the table
            cursor.execute(f"TRUNCATE TABLE `{table_name}`")
            
            # Re-enable foreign key checks
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Truncate Table",
                details=f"Truncated table: {table_name}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error truncating table: {e}")
            connection.rollback()
            return False
        finally:
            self.close(connection)
    
    def optimize_database(self):
        """Optimize database tables"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get list of tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            # Optimize each table
            for table in tables:
                cursor.execute(f"OPTIMIZE TABLE `{table}`")
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Optimize Database",
                details=f"Optimized {len(tables)} tables"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error optimizing database: {e}")
            return False
        finally:
            self.close(connection)
    
    def get_audit_logs(self, limit=100, start_date=None, end_date=None, username=None, action=None):
        """Get audit logs with optional filtering"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if audit_log table exists
            cursor.execute("SHOW TABLES LIKE 'audit_log'")
            if not cursor.fetchone():
                return []
            
            # Base query - fix the table name (audit_log instead of audit_logs)
            query = """
                SELECT 
                    log_id,
                    DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as timestamp,
                    username,
                    action,
                    details,
                    status,
                    ip_address
                FROM audit_log
                WHERE 1=1
            """
            
            # Build parameters list
            params = []
            
            # Add filters if provided
            if username:
                query += " AND username = %s"
                params.append(username)
                
            if action:
                query += " AND action = %s"
                params.append(action)
                
            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)
                
            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)
                
            # Add ordering and limit
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            self.console_logger.error(f"Error getting audit logs: {e}")
            return []
        finally:
            self.close(connection)
    
    def get_system_settings(self):
        """Get all system settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if system_settings table exists
            cursor.execute("SHOW TABLES LIKE 'system_settings'")
            if not cursor.fetchone():
                # Create system_settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        setting_id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(50) NOT NULL UNIQUE,
                        setting_value TEXT,
                        setting_type VARCHAR(20),
                        description VARCHAR(200),
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_by VARCHAR(50)
                    )
                """)
                connection.commit()
                
                # Add default settings
                default_settings = [
                    ('company_name', 'CMMS System', 'string', 'Company name displayed in reports and emails'),
                    ('company_logo', '', 'file', 'Path to company logo image'),
                    ('email_notifications', 'true', 'boolean', 'Enable email notifications'),
                    ('email_server', 'smtp.example.com', 'string', 'SMTP server address'),
                    ('email_port', '587', 'integer', 'SMTP server port'),
                    ('email_username', '', 'string', 'SMTP username'),
                    ('email_password', '', 'password', 'SMTP password'),
                    ('email_from', 'cmms@example.com', 'string', 'From email address'),
                    ('email_use_ssl', 'true', 'boolean', 'Use SSL for email connection'),
                    ('auto_backup', 'true', 'boolean', 'Enable automatic database backups'),
                    ('backup_frequency', 'daily', 'string', 'Frequency of automatic backups'),
                    ('backup_time', '01:00', 'string', 'Time for automatic backups'),
                    ('backup_path', 'backups/', 'string', 'Path for backup files'),
                    ('max_backup_age', '30', 'integer', 'Maximum age (days) for backup files'),
                    ('date_format', 'YYYY-MM-DD', 'string', 'Default date format'),
                    ('time_format', 'HH:mm:ss', 'string', 'Default time format'),
                    ('timezone', 'UTC', 'string', 'System timezone'),
                    ('api_enabled', 'false', 'boolean', 'Enable API access'),
                    ('api_key', '', 'string', 'API key for external access'),
                    ('log_level', 'INFO', 'string', 'System log level'),
                    ('theme', 'light', 'string', 'UI theme (light/dark)'),
                    ('session_timeout', '30', 'integer', 'Session timeout in minutes')
                ]
                
                for setting in default_settings:
                    cursor.execute("""
                        INSERT INTO system_settings 
                        (setting_key, setting_value, setting_type, description) 
                        VALUES (%s, %s, %s, %s)
                    """, setting)
                
                connection.commit()
            
            # Get settings
            cursor.execute("SELECT * FROM system_settings ORDER BY setting_key")
            settings = cursor.fetchall()
            
            # Convert to dictionary
            settings_dict = {}
            for setting in settings:
                value = setting['setting_value']
                if setting['setting_type'] == 'boolean':
                    value = value.lower() == 'true'
                elif setting['setting_type'] == 'integer':
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                
                settings_dict[setting['setting_key']] = {
                    'value': value,
                    'type': setting['setting_type'],
                    'description': setting['description']
                }
            
            return settings_dict
        except Exception as e:
            self.console_logger.error(f"Error getting system settings: {e}")
            return {}
        finally:
            self.close(connection)
    
    def update_system_setting(self, key, value, updated_by='System'):
        """Update a system setting"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if system_settings table exists
            cursor.execute("SHOW TABLES LIKE 'system_settings'")
            if not cursor.fetchone():
                return False
            
            # Check if setting exists
            cursor.execute("SELECT setting_type FROM system_settings WHERE setting_key = %s", (key,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            # Convert value based on type
            setting_type = result[0]
            if setting_type == 'boolean':
                value = str(value).lower()
            elif setting_type == 'integer':
                try:
                    value = str(int(value))
                except (ValueError, TypeError):
                    value = '0'
            else:
                value = str(value)
            
            # Update setting
            cursor.execute("""
                UPDATE system_settings 
                SET setting_value = %s, updated_at = NOW(), updated_by = %s
                WHERE setting_key = %s
            """, (value, updated_by, key))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username=updated_by,
                action="Update Setting",
                details=f"Updated setting: {key}"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error updating system setting: {e}")
            return False
        finally:
            self.close(connection)
    
    def backup_database(self, backup_path=None, include_attachments=True):
        """
        Backup the database to a file
        
        Args:
            backup_path: Path where backup should be saved (default: backups/)
            include_attachments: Whether to include attachment files in backup
            
        Returns:
            Dictionary with status and path of backup file
        """
        try:
            import os
            import datetime
            import zipfile
            import subprocess
            
            # Get backup path from settings if not provided
            if not backup_path:
                settings = self.get_system_settings()
                backup_path = settings.get('backup_path', {}).get('value', 'backups/')
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            sql_filename = f"{timestamp}_database_backup.sql"
            zip_filename = f"{timestamp}_full_backup.zip"
            
            sql_path = os.path.join(backup_path, sql_filename)
            zip_path = os.path.join(backup_path, zip_filename)
            
            # Get database connection info
            connection = self.connect()
            config = connection.config
            host = config.get('host', 'localhost')
            user = config.get('user', 'root')
            password = config.get('password', '')
            database = config.get('database', '')
            
            # Build mysqldump command
            cmd = [
                'mysqldump',
                f'--host={host}',
                f'--user={user}'
            ]
            
            if password:
                cmd.append(f'--password={password}')
                
            cmd.extend([
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                database
            ])
            
            # Execute mysqldump and save output to file
            with open(sql_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            # Create ZIP file with SQL dump
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(sql_path, os.path.basename(sql_path))
                
                # Include attachments if requested
                if include_attachments:
                    # Add attachment files
                    attachments_dir = 'attachments/'
                    if os.path.exists(attachments_dir):
                        for root, dirs, files in os.walk(attachments_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                zipf.write(file_path, file_path)
            
            # Clean up temporary SQL file
            os.remove(sql_path)
            
            # Get file size
            file_size = os.path.getsize(zip_path)
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
            
            # Log backup in database
            connection = self.connect()
            cursor = connection.cursor()
            
            # Create backup_history table if it doesn't exist
            cursor.execute("SHOW TABLES LIKE 'backup_history'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_history (
                        backup_id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        file_size BIGINT,
                        backup_type VARCHAR(50),
                        status VARCHAR(20),
                        details TEXT
                    )
                """)
            
            # Log backup
            cursor.execute("""
                INSERT INTO backup_history (
                    timestamp, filename, file_size, backup_type, status, details
                ) VALUES (NOW(), %s, %s, %s, %s, %s)
            """, (
                zip_filename,
                file_size,
                'Full' if include_attachments else 'Database Only',
                'Success',
                f"Backup size: {size_str}"
            ))
            
            connection.commit()
            
            # Log to audit log
            self.add_audit_log_entry(
                username="System",
                action="Database Backup",
                details=f"Created backup: {zip_filename} ({size_str})"
            )
            
            return {
                'status': 'success',
                'file': zip_path,
                'size': size_str
            }
            
        except Exception as e:
            self.console_logger.error(f"Error backing up database: {e}")
            
            # Log failed backup
            try:
                connection = self.connect()
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO backup_history (
                        timestamp, filename, backup_type, status, details
                    ) VALUES (NOW(), %s, %s, %s, %s)
                """, (
                    f"{timestamp}_failed_backup.zip",
                    'Full' if include_attachments else 'Database Only',
                    'Failure',
                    f"Error: {str(e)}"
                ))
                
                connection.commit()
                
                # Log to audit log
                self.add_audit_log_entry(
                    username="System",
                    action="Database Backup",
                    status="Failure",
                    details=f"Backup failed: {str(e)}"
                )
            except:
                pass
                
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_backup_history(self, limit=10):
        """Get database backup history"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if backup_history table exists
            cursor.execute("SHOW TABLES LIKE 'backup_history'")
            if not cursor.fetchone():
                return []
            
            cursor.execute("""
                SELECT 
                    backup_id,
                    DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as timestamp,
                    filename,
                    file_size,
                    backup_type,
                    status,
                    details
                FROM backup_history
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Exception as e:
            self.console_logger.error(f"Error getting backup history: {e}")
            return []
        finally:
            self.close(connection)
    
    def restore_database_from_backup(self, backup_file, restore_attachments=True):
        """
        Restore database from a backup file
        
        Args:
            backup_file: Path to backup ZIP file
            restore_attachments: Whether to restore attachment files
            
        Returns:
            Dictionary with status and message
        """
        try:
            import os
            import zipfile
            import tempfile
            import subprocess
            
            # Extract SQL file from ZIP
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract zip contents
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Find SQL file
                    sql_files = [f for f in zipf.namelist() if f.endswith('.sql')]
                    if not sql_files:
                        return {
                            'status': 'error', 
                            'message': 'No SQL file found in backup'
                        }
                    
                    sql_file = sql_files[0]
                    zipf.extract(sql_file, temp_dir)
                    
                    # Extract attachments if requested
                    if restore_attachments:
                        attachment_files = [f for f in zipf.namelist() if f.startswith('attachments/')]
                        for file in attachment_files:
                            zipf.extract(file, '/')  # Extract to root directory
                
                # Get database connection info
                connection = self.connect()
                config = connection.config
                host = config.get('host', 'localhost')
                user = config.get('user', 'root')
                password = config.get('password', '')
                database = config.get('database', '')
                
                # Build mysql command for restore
                cmd = [
                    'mysql',
                    f'--host={host}',
                    f'--user={user}'
                ]
                
                if password:
                    cmd.append(f'--password={password}')
                    
                cmd.append(database)
                
                # Execute mysql command
                sql_path = os.path.join(temp_dir, sql_file)
                with open(sql_path, 'r') as f:
                    process = subprocess.run(
                        cmd, 
                        stdin=f, 
                        capture_output=True, 
                        text=True, 
                        check=True
                    )
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Database Restore",
                details=f"Restored database from backup: {os.path.basename(backup_file)}"
            )
            
            return {
                'status': 'success',
                'message': 'Database restored successfully'
            }
            
        except Exception as e:
            self.console_logger.error(f"Error restoring database: {e}")
            
            # Log the failure
            self.add_audit_log_entry(
                username="System",
                action="Database Restore",
                status="Failure",
                details=f"Failed to restore database: {str(e)}"
            )
            
            return {
                'status': 'error',
                'message': f'Error restoring database: {str(e)}'
            }
    
    def get_backup_schedule(self):
        """Get backup schedule settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if backup_schedule table exists
            cursor.execute("SHOW TABLES LIKE 'backup_schedule'")
            if not cursor.fetchone():
                # Create backup_schedule table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_schedule (
                        schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                        enabled BOOLEAN DEFAULT 0,
                        frequency VARCHAR(20) DEFAULT 'Weekly',
                        time TIME DEFAULT '01:00:00',
                        day_of_week VARCHAR(10) DEFAULT 'Monday',
                        day_of_month INT DEFAULT 1,
                        backup_location VARCHAR(255),
                        compression VARCHAR(20) DEFAULT 'Medium',
                        include_attachments BOOLEAN DEFAULT 1,
                        keep_backups INT DEFAULT 10,
                        notify_on_success BOOLEAN DEFAULT 1,
                        notify_on_failure BOOLEAN DEFAULT 1,
                        notification_email VARCHAR(100),
                        last_run DATETIME,
                        next_run DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert default schedule
                cursor.execute("""
                    INSERT INTO backup_schedule (
                        enabled, backup_location
                    ) VALUES (0, 'backups/')
                """)
                
                connection.commit()
            
            # Get schedule
            cursor.execute("SELECT * FROM backup_schedule LIMIT 1")
            schedule = cursor.fetchone()
            
            return schedule
        except Exception as e:
            self.console_logger.error(f"Error getting backup schedule: {e}")
            return None
        finally:
            self.close(connection)    
    def update_backup_schedule(self, schedule_data):
        """Update backup schedule settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if backup_schedule table exists
            cursor.execute("SHOW TABLES LIKE 'backup_schedule'")
            if not cursor.fetchone():
                # Create backup_schedule table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_schedule (
                        schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                        enabled BOOLEAN DEFAULT 0,
                        frequency VARCHAR(20) DEFAULT 'Weekly',
                        time TIME DEFAULT '01:00:00',
                        day_of_week VARCHAR(10) DEFAULT 'Monday',
                        day_of_month INT DEFAULT 1,
                        backup_location VARCHAR(255),
                        compression VARCHAR(20) DEFAULT 'Medium',
                        include_attachments BOOLEAN DEFAULT 1,
                        keep_backups INT DEFAULT 10,
                        notify_on_success BOOLEAN DEFAULT 1,
                        notify_on_failure BOOLEAN DEFAULT 1,
                        notification_email VARCHAR(100),
                        last_run DATETIME,
                        next_run DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                connection.commit()
            
            # Check if schedule exists
            cursor.execute("SELECT COUNT(*) FROM backup_schedule")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert new schedule
                cursor.execute("""
                    INSERT INTO backup_schedule (
                        enabled, frequency, time, day_of_week, day_of_month, 
                        backup_location, compression, include_attachments, 
                        keep_backups, notify_on_success, notify_on_failure, 
                        notification_email, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    schedule_data.get('enabled', 0),
                    schedule_data.get('frequency', 'Weekly'),
                    schedule_data.get('time', '01:00:00'),
                    schedule_data.get('day_of_week', 'Monday'),
                    schedule_data.get('day_of_month', 1),
                    schedule_data.get('backup_location', 'backups/'),
                    schedule_data.get('compression', 'Medium'),
                    schedule_data.get('include_attachments', 1),
                    schedule_data.get('keep_backups', 10),
                    schedule_data.get('notify_on_success', 1),
                    schedule_data.get('notify_on_failure', 1),
                    schedule_data.get('notification_email', '')
                ))
            else:
                # Update existing schedule
                cursor.execute("""
                    UPDATE backup_schedule SET
                        enabled = %s,
                        frequency = %s,
                        time = %s,
                        day_of_week = %s,
                        day_of_month = %s,
                        backup_location = %s,
                        compression = %s,
                        include_attachments = %s,
                        keep_backups = %s,
                        notify_on_success = %s,
                        notify_on_failure = %s,
                        notification_email = %s,
                        updated_at = NOW()
                """, (
                    schedule_data.get('enabled', 0),
                    schedule_data.get('frequency', 'Weekly'),
                    schedule_data.get('time', '01:00:00'),
                    schedule_data.get('day_of_week', 'Monday'),
                    schedule_data.get('day_of_month', 1),
                    schedule_data.get('backup_location', 'backups/'),
                    schedule_data.get('compression', 'Medium'),
                    schedule_data.get('include_attachments', 1),
                    schedule_data.get('keep_backups', 10),
                    schedule_data.get('notify_on_success', 1),
                    schedule_data.get('notify_on_failure', 1),
                    schedule_data.get('notification_email', '')
                ))
            
            connection.commit()
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Update Backup Schedule",
                details=f"Updated backup schedule settings"
            )
            
            return True
        except Exception as e:
            self.console_logger.error(f"Error updating backup schedule: {e}")
            return False
        finally:
            self.close(connection)
    
    def generate_api_key(self):
        """Generate a new API key for system access"""
        try:
            import uuid
            import base64
            
            # Generate a random API key
            api_key = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
            api_key = api_key.replace('=', '').replace('+', '-').replace('/', '_')
            
            # Save in system settings
            self.update_system_setting('api_key', api_key)
            self.update_system_setting('api_enabled', 'true')
            
            # Log the action
            self.add_audit_log_entry(
                username="System",
                action="Generate API Key",
                details="Generated new API key"
            )
            
            return api_key
        except Exception as e:
            self.console_logger.error(f"Error generating API key: {e}")
            return None
        
    def get_last_backup_time(self):
        """Get the timestamp of the most recent database backup"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if backup_history table exists
            cursor.execute("SHOW TABLES LIKE 'backup_history'")
            if not cursor.fetchone():
                return None
            
            # Get the most recent successful backup
            cursor.execute("""
                SELECT timestamp 
                FROM backup_history 
                WHERE status = 'Success' 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            self.console_logger.error(f"Error getting last backup time: {e}")
            return None
        finally:
            self.close(connection)

    def get_audit_log_users(self):
        """Get list of distinct usernames from audit log"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if audit_log table exists
            cursor.execute("SHOW TABLES LIKE 'audit_log'")
            if not cursor.fetchone():
                return []
            
            # Get distinct usernames
            cursor.execute("""
                SELECT DISTINCT username 
                FROM audit_log 
                ORDER BY username
            """)

            users = [row[0] for row in cursor.fetchall()]
            return users
        except Exception as e:
            self.console_logger.error(f"Error getting audit log users: {e}")
            return []
        finally:
            self.close(connection)
