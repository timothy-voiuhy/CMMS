from mysql.connector import Error
import json
import traceback

class DbInit:
    def __init__(self, db_manager):
        self.db_manager = db_manager 
        self.console_logger = self.db_manager.console_logger

    def connect(self):
        return self.db_manager.connect()

    def close(self, connection):
        return self.db_manager.close(connection)

    def create_admin_tables(self):
        return self.db_manager.create_admin_tables()

    def initialize_database(self):
        try:
            connection = self.connect()
            if connection is None:
                return False
            
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS cmms_db")

            # create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    access_level VARCHAR(50),
                    last_login DATETIME NULL,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    is_staff BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
                    first_name VARCHAR(150) DEFAULT '',
                    last_name VARCHAR(150) DEFAULT '',
                    email VARCHAR(254) DEFAULT ''
                )
            """)

            # create the admin tables
            self.create_admin_tables()

            # Create equipment_templates table to store different equipment types
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_templates (
                    template_id INT AUTO_INCREMENT PRIMARY KEY,
                    template_name VARCHAR(100) NOT NULL,
                    fields_schema JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create equipment_registry table for all equipment instances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_registry (
                    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
                    template_id INT,
                    part_number VARCHAR(50) NOT NULL,
                    equipment_name VARCHAR(100) NOT NULL,
                    location VARCHAR(100),
                    installation_date DATE,
                    manufacturer VARCHAR(100),
                    model VARCHAR(100),
                    serial_number VARCHAR(100),
                    status VARCHAR(20),
                    custom_fields JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES equipment_templates(template_id)
                )
            """)

            # Check if default template exists, if not create it
            cursor.execute("SELECT template_id FROM equipment_templates WHERE template_name = 'Default Template'")
            if not cursor.fetchone():
                default_schema = json.dumps([
                    {"name": "part_number", "type": "string", "required": True},
                    {"name": "equipment_name", "type": "string", "required": True},
                    {"name": "manufacturer", "type": "string", "required": False},
                    {"name": "model", "type": "string", "required": False},
                    {"name": "serial_number", "type": "string", "required": False},
                    {"name": "location", "type": "string", "required": False},
                    {"name": "installation_date", "type": "date", "required": False},
                    {"name": "status", "type": "string", "required": False}
                ])
                cursor.execute("""
                    INSERT INTO equipment_templates (template_name, fields_schema)
                    VALUES ('Default Template', %s)
                """, (default_schema,))

            # Create technical info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_technical_info (
                    equipment_id INT PRIMARY KEY,
                    power_requirements TEXT,
                    operating_temperature TEXT,
                    weight TEXT,
                    dimensions TEXT,
                    operating_pressure TEXT,
                    capacity TEXT,
                    precision_accuracy TEXT,
                    detailed_specifications TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE
                )
            """)

            # Create history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_history (
                    history_id INT AUTO_INCREMENT PRIMARY KEY,
                    equipment_id INT,
                    date DATE NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    performed_by VARCHAR(100),
                    notes TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE
                )
            """)

            # Create maintenance schedule table (updated to fix the reserved word issue)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_schedule (
                    task_id INT AUTO_INCREMENT PRIMARY KEY,
                    equipment_id INT,
                    task_name VARCHAR(200) NOT NULL,
                    frequency INT,
                    frequency_unit VARCHAR(20),
                    last_done DATE,
                    next_due DATE,
                    maintenance_procedure TEXT,
                    required_parts TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE
                )
            """)

            # Create special tools table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS special_tools (
                    tool_id INT AUTO_INCREMENT PRIMARY KEY,
                    equipment_id INT,
                    tool_name VARCHAR(200) NOT NULL,
                    specification TEXT,
                    purpose TEXT,
                    location VARCHAR(200),
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE
                )
            """)

            # Create safety information table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS safety_information (
                    equipment_id INT PRIMARY KEY,
                    ppe_requirements TEXT,
                    operating_precautions TEXT,
                    emergency_procedures TEXT,
                    hazardous_materials TEXT,
                    lockout_procedures TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE
                )
            """)

            # Create craftsmen table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen (
                    craftsman_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    specialization VARCHAR(100),
                    experience_level VARCHAR(50),
                    hire_date DATE,
                    status VARCHAR(20) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create craftsmen skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen_skills (
                    skill_id INT AUTO_INCREMENT PRIMARY KEY,
                    craftsman_id INT,
                    skill_name VARCHAR(100) NOT NULL,
                    skill_level VARCHAR(50),
                    certification_date DATE,
                    expiry_date DATE,
                    certification_authority VARCHAR(100),
                    certification_number VARCHAR(50),
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE CASCADE
                )
            """)

            # Create craftsmen work history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen_work_history (
                    history_id INT AUTO_INCREMENT PRIMARY KEY,
                    craftsman_id INT,
                    equipment_id INT,
                    task_date DATE NOT NULL,
                    task_type VARCHAR(50),
                    task_description TEXT,
                    performance_rating INT,
                    completion_time FLOAT,
                    notes TEXT,
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE SET NULL
                )
            """)

            # Create craftsmen training records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen_training (
                    training_id INT AUTO_INCREMENT PRIMARY KEY,
                    craftsman_id INT,
                    training_name VARCHAR(100) NOT NULL,
                    training_date DATE,
                    completion_date DATE,
                    training_provider VARCHAR(100),
                    certification_received VARCHAR(100),
                    expiry_date DATE,
                    training_status VARCHAR(50),
                    notes TEXT,
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE CASCADE
                )
            """)

            # Create craftsmen availability schedule
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen_schedule (
                    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                    craftsman_id INT,
                    date DATE NOT NULL,
                    shift_start TIME,
                    shift_end TIME,
                    status VARCHAR(50),
                    notes TEXT,
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE CASCADE
                )
            """)

            # Create teams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS craftsmen_teams (
                    team_id INT AUTO_INCREMENT PRIMARY KEY,
                    team_name VARCHAR(100) NOT NULL,
                    team_leader_id INT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_leader_id) REFERENCES craftsmen(craftsman_id)
                )
            """)
            
            # Create team members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    team_id INT,
                    craftsman_id INT,
                    role VARCHAR(50),
                    joined_date DATE,
                    PRIMARY KEY (team_id, craftsman_id),
                    FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id),
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id)
                )
            """)

            # Create work orders table with team support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_orders (
                    work_order_id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    equipment_id INT,
                    assignment_type VARCHAR(20) DEFAULT 'Individual',
                    craftsman_id INT NULL,
                    team_id INT NULL,
                    priority VARCHAR(20) DEFAULT 'Medium',
                    status VARCHAR(20) DEFAULT 'Open',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date DATE,
                    completed_date DATE,
                    estimated_hours FLOAT,
                    actual_hours FLOAT,
                    tools_required JSON,
                    spares_required JSON,
                    notes TEXT,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE SET NULL,
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE SET NULL,
                    FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id) ON DELETE SET NULL
                )
            """)
            
            # Add assignment type check trigger instead of check constraint
            
            # Drop triggers if they exist to avoid errors on recreation
            cursor.execute("""
                DROP TRIGGER IF EXISTS work_orders_assignment_check;
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS work_orders_assignment_update_check;
            """)
            
            cursor.execute("""
                CREATE TRIGGER work_orders_assignment_check 
                BEFORE INSERT ON work_orders
                FOR EACH ROW
                BEGIN
                    IF NEW.assignment_type IS NULL THEN
                        SET NEW.assignment_type = 'Individual';
                    END IF;
                    
                    IF (NEW.assignment_type = 'Individual' AND (NEW.craftsman_id IS NULL OR NEW.team_id IS NOT NULL)) THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Individual assignments must have craftsman_id set and team_id null';
                    ELSEIF (NEW.assignment_type = 'Team' AND (NEW.team_id IS NULL OR NEW.craftsman_id IS NOT NULL)) THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Team assignments must have team_id set and craftsman_id null';
                    END IF;
                END;
            """)
            
            cursor.execute("""
                CREATE TRIGGER work_orders_assignment_update_check
                BEFORE UPDATE ON work_orders
                FOR EACH ROW
                BEGIN
                    IF NEW.assignment_type IS NULL THEN
                        SET NEW.assignment_type = 'Individual';
                    END IF;
                    
                    IF (NEW.assignment_type = 'Individual' AND (NEW.craftsman_id IS NULL OR NEW.team_id IS NOT NULL)) THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Individual assignments must have craftsman_id set and team_id null';
                    ELSEIF (NEW.assignment_type = 'Team' AND (NEW.team_id IS NULL OR NEW.craftsman_id IS NOT NULL)) THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Team assignments must have team_id set and craftsman_id null';
                    END IF;
                END;
            """)

            # Add new columns to work_orders table if they don't exist
            try:
                cursor.execute("""
                    ALTER TABLE work_orders
                    ADD COLUMN IF NOT EXISTS assignment_type VARCHAR(20) DEFAULT 'Individual',
                    ADD COLUMN IF NOT EXISTS team_id INT NULL,
                    ADD COLUMN IF NOT EXISTS tools_required JSON,
                    ADD COLUMN IF NOT EXISTS spares_required JSON,
                    ADD FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id) ON DELETE SET NULL
                """)
                connection.commit()
            except Error as e:
                # Handle the case where IF NOT EXISTS is not supported
                try:
                    # Check if columns exist
                    cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'assignment_type'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE work_orders ADD COLUMN assignment_type VARCHAR(20) DEFAULT 'Individual'")
                    
                    cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'team_id'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE work_orders ADD COLUMN team_id INT NULL")
                        cursor.execute("ALTER TABLE work_orders ADD FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id) ON DELETE SET NULL")
                    
                    cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'tools_required'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE work_orders ADD COLUMN tools_required JSON")
                    
                    cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'spares_required'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE work_orders ADD COLUMN spares_required JSON")
                    
                    connection.commit()
                except Error as e2:
                    print(f"Error adding columns: {e2}")

            # Migrate existing work orders
            self.migrate_work_orders()

            # Create work order reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_order_reports (
                    report_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_name VARCHAR(200) NOT NULL,
                    report_type VARCHAR(50) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parameters TEXT
                )
            """)

            # Create inventory categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_categories (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    contact_person VARCHAR(100),
                    phone VARCHAR(50),
                    email VARCHAR(100),
                    address TEXT,
                    notes TEXT,
                    status VARCHAR(20) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create inventory items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT,
                    supplier_id INT,
                    item_code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    unit VARCHAR(20),
                    unit_cost DECIMAL(10, 2),
                    quantity INT DEFAULT 0,
                    minimum_quantity INT DEFAULT 0,
                    reorder_point INT DEFAULT 0,
                    location VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'Active',
                    last_restock_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES inventory_categories(category_id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
                )
            """)

            # Create inventory transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT,
                    work_order_id INT NULL,
                    transaction_type VARCHAR(20),  -- 'IN', 'OUT', 'ADJUST'
                    quantity INT,
                    unit_cost DECIMAL(10, 2),
                    total_cost DECIMAL(10, 2),
                    reference_number VARCHAR(50),
                    notes TEXT,
                    performed_by VARCHAR(100),
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
                    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
                )
            """)

            # Create tool checkout table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_checkouts (
                    checkout_id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT,
                    craftsman_id INT,
                    work_order_id INT NULL,
                    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expected_return_date TIMESTAMP,
                    actual_return_date TIMESTAMP NULL,
                    status VARCHAR(20) DEFAULT 'Checked Out',
                    notes TEXT,
                    FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id),
                    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
                )
            """)

            # Create maintenance schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_schedules (
                    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
                    frequency INT NOT NULL,
                    frequency_unit VARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    last_generated DATE,
                    notification_days_before INT DEFAULT 2,
                    notification_emails JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create work order templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_order_templates (
                    template_id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    equipment_id INT,
                    priority VARCHAR(20) DEFAULT 'Medium',
                    estimated_hours FLOAT,
                    assignment_type VARCHAR(20) DEFAULT 'Individual',
                    craftsman_id INT,
                    team_id INT,
                    tools_required JSON,
                    spares_required JSON,
                    schedule_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id),
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id),
                    FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id),
                    FOREIGN KEY (schedule_id) REFERENCES maintenance_schedules(schedule_id)
                )
            """)

            # Add schedule_id and notification_sent fields to work_orders table
            try:
                # Check if columns exist first
                cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'schedule_id'")
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE work_orders
                        ADD COLUMN schedule_id INT,
                        ADD FOREIGN KEY (schedule_id) REFERENCES maintenance_schedules(schedule_id)
                    """)
                
                cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'notification_sent'")
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE work_orders
                        ADD COLUMN notification_sent BOOLEAN DEFAULT 0
                    """)
                
                connection.commit()
            except Error as e:
                print(f"Error adding columns to work_orders table: {e}")

            # Create email settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_settings (
                    setting_id INT AUTO_INCREMENT PRIMARY KEY,
                    enabled BOOLEAN DEFAULT 0,
                    server VARCHAR(100) NOT NULL,
                    port INT NOT NULL,
                    use_tls BOOLEAN DEFAULT 1,
                    username VARCHAR(100),
                    password VARCHAR(100),
                    from_address VARCHAR(100) NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create inventory personnel table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_personnel (
                    personnel_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    role VARCHAR(50),
                    access_level VARCHAR(20) DEFAULT 'Standard',
                    hire_date DATE,
                    status VARCHAR(20) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create purchase orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    po_id INT AUTO_INCREMENT PRIMARY KEY,
                    po_number VARCHAR(50) UNIQUE NOT NULL,
                    supplier_id INT,
                    status VARCHAR(20) DEFAULT 'Pending',
                    total_amount DECIMAL(10, 2),
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expected_delivery DATE,
                    notes TEXT,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                    FOREIGN KEY (created_by) REFERENCES inventory_personnel(personnel_id)
                )
            """)

            # Create purchase order items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_order_items (
                    po_item_id INT AUTO_INCREMENT PRIMARY KEY,
                    po_id INT,
                    item_id INT,
                    quantity INT,
                    unit_price DECIMAL(10, 2),
                    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
                    FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
                )
            """)

            # Update inventory transactions to track who performed the transaction
            try:
                cursor.execute("SHOW COLUMNS FROM inventory_transactions LIKE 'personnel_id'")
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE inventory_transactions
                        ADD COLUMN personnel_id INT,
                        ADD FOREIGN KEY (personnel_id) REFERENCES inventory_personnel(personnel_id)
                    """)
                connection.commit()
            except Error as e:
                print(f"Error adding personnel_id to inventory_transactions: {e}")

            # Create maintenance reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_reports (
                    report_id INT AUTO_INCREMENT PRIMARY KEY,
                    work_order_id INT NOT NULL,
                    equipment_id INT NOT NULL,
                    craftsman_id INT NOT NULL,
                    report_date DATETIME NOT NULL,
                    report_data JSON NOT NULL,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id) ON DELETE CASCADE,
                    FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id) ON DELETE CASCADE
                )
            """)

            # Create report attachments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_attachments (
                    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_id INT NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_type VARCHAR(100),
                    file_size INT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES maintenance_reports(report_id) ON DELETE CASCADE
                )
            """)

            # Create notifications tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(255) NOT NULL,
                    recipient VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL,  -- 'sent', 'failed', 'pending'
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP NULL,
                    notification_type VARCHAR(100),  -- 'work_order', 'purchase_order', etc.
                    reference_id INT,  -- ID of related entity (work order ID, PO ID, etc.)
                    attachments TEXT  -- JSON array of attachment paths
                )
            """)

            connection.commit()
            msg = "Database initialized successfully"
            self.console_logger.info(msg)
            return True
        except Error as e:      
            msg = f"Error initializing database: {e} Traceback: {traceback.format_exc()}"
            self.console_logger.error(msg)
            return False
        finally:
            self.close(connection)

    def migrate_work_orders(self):
        """Migrate existing work orders to handle new columns"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get all work orders
            cursor.execute("SELECT work_order_id FROM work_orders")
            work_orders = cursor.fetchall()
            
            # Update each work order with default JSON values
            for work_order in work_orders:
                cursor.execute("""
                    UPDATE work_orders 
                    SET tools_required = %s,
                        spares_required = %s
                    WHERE work_order_id = %s
                    AND (tools_required IS NULL OR spares_required IS NULL)
                """, ('[]', '[]', work_order[0]))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error migrating work orders: {e}")
            return False
        finally:
            self.close(connection)
