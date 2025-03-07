import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
import json
import logging
import traceback
from datetime import datetime, timedelta
import os
import csv

class DatabaseManager:
    def __init__(self):
        self.console_logger = logging.getLogger('console')
        self.config = {
            'host': 'localhost',
            'user': 'CMMS',
            'password': 'cmms',
            'database': 'cmms_db',
            'charset':"utf8mb4",
            'collation':"utf8mb4_general_ci"
        }
        self.initialize_database()

    def connect(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            msg = f"Error connecting to MySQL database: {e} Traceback: {traceback.format_exc()}"
            self.console_logger.error(msg)
            return None

    def initialize_database(self):
        try:
            connection = self.connect()
            if connection is None:
                return False
            
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS cmms_db")

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
                    FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id) ON DELETE SET NULL,
                    CHECK (
                        (assignment_type = 'Individual' AND craftsman_id IS NOT NULL AND team_id IS NULL) OR
                        (assignment_type = 'Team' AND team_id IS NOT NULL AND craftsman_id IS NULL)
                    )
                )
            """)

            # Add new columns to work_orders table if they don't exist
            try:
                cursor.execute("""
                    ALTER TABLE work_orders
                    ADD COLUMN IF NOT EXISTS assignment_type VARCHAR(20) DEFAULT 'Individual',
                    ADD COLUMN IF NOT EXISTS team_id INT NULL,
                    ADD COLUMN IF NOT EXISTS tools_required JSON,
                    ADD COLUMN IF NOT EXISTS spares_required JSON,
                    ADD FOREIGN KEY (team_id) REFERENCES craftsmen_teams(team_id) ON DELETE SET NULL,
                    ADD CONSTRAINT check_assignment 
                    CHECK (
                        (assignment_type = 'Individual' AND craftsman_id IS NOT NULL AND team_id IS NULL) OR
                        (assignment_type = 'Team' AND team_id IS NOT NULL AND craftsman_id IS NULL)
                    )
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
                    
                    # Add constraint if it doesn't exist
                    try:
                        cursor.execute("""
                            ALTER TABLE work_orders
                            ADD CONSTRAINT check_assignment 
                            CHECK (
                                (assignment_type = 'Individual' AND craftsman_id IS NOT NULL AND team_id IS NULL) OR
                                (assignment_type = 'Team' AND team_id IS NOT NULL AND craftsman_id IS NULL)
                            )
                        """)
                    except Error:
                        # Constraint might already exist or not be supported
                        pass
                    
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

    def create_equipment_template(self, template_name: str, fields: List[Dict[str, Any]]) -> bool:
        try:
            connection = self.connect()
            cursor = connection.cursor()
            fields_schema = json.dumps(fields)
            cursor.execute("""
                INSERT INTO equipment_templates (template_name, fields_schema)
                VALUES (%s, %s)
            """, (template_name, fields_schema))
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating equipment template: {e}")
            return False

    def register_equipment(self, template_id: int, equipment_data: Dict[str, Any]) -> bool:
        try:
            connection = self.connect()
            cursor = connection.cursor()
            custom_fields = {k: v for k, v in equipment_data.items() 
                           if k not in ['part_number', 'equipment_name', 'location', 
                                      'installation_date', 'manufacturer', 'model', 
                                      'serial_number', 'status']}
            
            cursor.execute("""
                INSERT INTO equipment_registry (
                    template_id, part_number, equipment_name, location, 
                    installation_date, manufacturer, model, serial_number, 
                    status, custom_fields
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template_id,
                equipment_data.get('part_number'),
                equipment_data.get('equipment_name'),
                equipment_data.get('location'),
                equipment_data.get('installation_date'),
                equipment_data.get('manufacturer'),
                equipment_data.get('model'),
                equipment_data.get('serial_number'),
                equipment_data.get('status', 'Active'),
                json.dumps(custom_fields)
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error registering equipment: {e}")
            return False

    def get_equipment_templates(self) -> List[Dict[str, Any]]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM equipment_templates")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching equipment templates: {e}")
            return []

    def get_equipment_by_id(self, equipment_id: int) -> Dict[str, Any]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_registry 
                WHERE equipment_id = %s
            """, (equipment_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching equipment: {e}")
            return None

    def get_all_equipment(self) -> List[Dict[str, Any]]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_registry 
                ORDER BY last_modified DESC
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching equipment list: {e}")
            return []

    def delete_equipment(self, equipment_id: int) -> bool:
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM equipment_registry 
                WHERE equipment_id = %s
            """, (equipment_id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting equipment: {e}")
            return False

    def close(self, connection):
        if connection and connection.is_connected():
            connection.close()

    def get_equipment_by_fields(self, fields: Dict[str, str]) -> List[Dict[str, Any]]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Build the WHERE clause dynamically
            where_conditions = []
            params = []
            for field, value in fields.items():
                if value:  # Only add non-empty values to the query
                    where_conditions.append(f"{field} = %s")
                    params.append(value)
            
            if where_conditions:
                where_clause = " OR ".join(where_conditions)
                query = f"SELECT * FROM equipment_registry WHERE {where_clause}"
                cursor.execute(query, params)
                return cursor.fetchall()
            return []
        except Error as e:
            print(f"Error fetching equipment by fields: {e}")
            return []

    def get_technical_info(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_technical_info 
                WHERE equipment_id = %s
            """, (equipment_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching technical info: {e}")
            return None
        finally:
            self.close(connection)

    def save_technical_info(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO equipment_technical_info (
                    equipment_id, power_requirements, operating_temperature,
                    weight, dimensions, operating_pressure, capacity,
                    precision_accuracy, detailed_specifications
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    power_requirements = VALUES(power_requirements),
                    operating_temperature = VALUES(operating_temperature),
                    weight = VALUES(weight),
                    dimensions = VALUES(dimensions),
                    operating_pressure = VALUES(operating_pressure),
                    capacity = VALUES(capacity),
                    precision_accuracy = VALUES(precision_accuracy),
                    detailed_specifications = VALUES(detailed_specifications)
            """, (
                equipment_id, data['power_requirements'], data['operating_temperature'],
                data['weight'], data['dimensions'], data['operating_pressure'],
                data['capacity'], data['precision_accuracy'], data['detailed_specifications']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving technical info: {e}")
            return False
        finally:
            self.close(connection)

    def add_history_entry(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO equipment_history (
                    equipment_id, date, event_type, description,
                    performed_by, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                equipment_id, data['date'], data['event_type'],
                data['description'], data['performed_by'], data['notes']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding history entry: {e}")
            return False
        finally:
            self.close(connection)

    def get_equipment_history(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_history 
                WHERE equipment_id = %s 
                ORDER BY date DESC
            """, (equipment_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching equipment history: {e}")
            return []
        finally:
            self.close(connection)

    def add_maintenance_task(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO maintenance_schedule (
                    equipment_id, task_name, frequency, frequency_unit,
                    last_done, next_due, maintenance_procedure, required_parts
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                equipment_id, 
                data['task_name'],
                data['frequency'],
                data['frequency_unit'],
                data['last_done'],
                data['next_due'],
                data['maintenance_procedure'],
                data['required_parts']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding maintenance task: {e}")
            return False
        finally:
            self.close(connection)

    def get_maintenance_schedule(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_schedule 
                WHERE equipment_id = %s 
                ORDER BY next_due ASC
            """, (equipment_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching maintenance schedule: {e}")
            return []
        finally:
            self.close(connection)

    def add_special_tool(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO special_tools (
                    equipment_id, tool_name, specification,
                    purpose, location
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                equipment_id, data['tool_name'], data['specification'],
                data['purpose'], data['location']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding special tool: {e}")
            return False
        finally:
            self.close(connection)

    def get_special_tools(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM special_tools 
                WHERE equipment_id = %s
            """, (equipment_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching special tools: {e}")
            return []
        finally:
            self.close(connection)

    def save_safety_info(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO safety_information (
                    equipment_id, ppe_requirements, operating_precautions,
                    emergency_procedures, hazardous_materials, lockout_procedures
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ppe_requirements = VALUES(ppe_requirements),
                    operating_precautions = VALUES(operating_precautions),
                    emergency_procedures = VALUES(emergency_procedures),
                    hazardous_materials = VALUES(hazardous_materials),
                    lockout_procedures = VALUES(lockout_procedures)
            """, (
                equipment_id, data['ppe_requirements'], data['operating_precautions'],
                data['emergency_procedures'], data['hazardous_materials'],
                data['lockout_procedures']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving safety info: {e}")
            return False
        finally:
            self.close(connection)

    def get_safety_info(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM safety_information 
                WHERE equipment_id = %s
            """, (equipment_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching safety info: {e}")
            return None
        finally:
            self.close(connection)

    def add_attachment(self, equipment_id, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO equipment_attachments (
                    equipment_id, file_name, file_path,
                    file_type, description
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                equipment_id, data['file_name'], data['file_path'],
                data['file_type'], data['description']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding attachment: {e}")
            return False
        finally:
            self.close(connection)

    def get_attachments(self, equipment_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_attachments 
                WHERE equipment_id = %s 
                ORDER BY upload_date DESC
            """, (equipment_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching attachments: {e}")
            return []
        finally:
            self.close(connection)

    def get_equipment_history_entry(self, history_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_history 
                WHERE history_id = %s
            """, (history_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching history entry: {e}")
            return None
        finally:
            self.close(connection)

    def get_maintenance_task_by_name(self, equipment_id, task_name):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_schedule 
                WHERE equipment_id = %s AND task_name = %s
            """, (equipment_id, task_name))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching maintenance task: {e}")
            return None
        finally:
            self.close(connection)

    def get_special_tool_by_name(self, equipment_id, tool_name):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM special_tools 
                WHERE equipment_id = %s AND tool_name = %s
            """, (equipment_id, tool_name))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching special tool: {e}")
            return None
        finally:
            self.close(connection)

    def get_history_entry_by_date_desc(self, equipment_id, entry_date, description):
        """Get history entry by date and description"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM equipment_history 
                WHERE equipment_id = %s 
                AND DATE(date) = %s 
                AND description = %s
            """, (equipment_id, entry_date, description))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching history entry: {e}")
            return None
        finally:
            self.close(connection)

    def register_craftsman(self, data: Dict[str, Any]) -> bool:
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO craftsmen (
                    employee_id, first_name, last_name, phone, email,
                    specialization, experience_level, hire_date, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['employee_id'], data['first_name'], data['last_name'],
                data['phone'], data['email'], data['specialization'],
                data['experience_level'], data['hire_date'], data['status']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error registering craftsman: {e}")
            return False
        finally:
            self.close(connection)

    def get_all_craftsmen(self) -> List[Dict[str, Any]]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen 
                ORDER BY last_modified DESC
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsmen list: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_by_id(self, craftsman_id):
        """Retrieve craftsman data by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen 
                WHERE craftsman_id = %s OR employee_id = %s
            """, (craftsman_id, craftsman_id))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error retrieving craftsman: {e}")
            return None
        finally:
            self.close(connection)

    def update_craftsman(self, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if we got employee_id or craftsman_id
            if 'employee_id' in data:
                id_field = 'employee_id'
                id_value = data['employee_id']
            else:
                id_field = 'craftsman_id'
                id_value = data['craftsman_id']
            
            # Update using either ID
            cursor.execute(f"""
                UPDATE craftsmen 
                SET first_name = %s, 
                    last_name = %s, 
                    phone = %s,
                    email = %s, 
                    specialization = %s, 
                    status = %s
                WHERE {id_field} = %s
            """, (
                data['first_name'], 
                data['last_name'], 
                data['phone'],
                data['email'], 
                data['specialization'], 
                data['status'],
                id_value
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating craftsman: {e}")
            return False
        finally:
            self.close(connection)

    def add_craftsman_skill(self, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO craftsmen_skills (
                    craftsman_id, skill_name, skill_level,
                    certification, certification_date, expiry_date,
                    certification_authority
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['craftsman_id'], data['skill_name'], data['skill_level'],
                data['certification'], data['certification_date'],
                data['expiry_date'], data['certification_authority']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding craftsman skill: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_skills(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_skills 
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman skills: {e}")
            return []
        finally:
            self.close(connection)

    def add_craftsman_training(self, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO craftsmen_training (
                    craftsman_id, training_name, training_date,
                    completion_date, training_provider,
                    certification_received, training_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['craftsman_id'], data['training_name'],
                data['training_date'], data['completion_date'],
                data['training_provider'], data['certification_received'],
                data['training_status']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding craftsman training: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_training(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_training 
                WHERE craftsman_id = %s 
                ORDER BY training_date DESC
            """, (craftsman_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman training: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_work_history(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_work_history 
                WHERE craftsman_id = %s 
                ORDER BY task_date DESC
            """, (craftsman_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman work history: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_schedule(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_schedule 
                WHERE craftsman_id = %s 
                ORDER BY date ASC
            """, (craftsman_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman schedule: {e}")
            return []
        finally:
            self.close(connection)

    def add_craftsman_schedule(self, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO craftsmen_schedule (
                    craftsman_id, date, shift_start,
                    shift_end, status, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['craftsman_id'], data['date'],
                data['shift_start'], data['shift_end'],
                data['status'], data['notes']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding schedule: {e}")
            return False
        finally:
            self.close(connection)

    def get_day_schedule(self, date):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_schedule 
                WHERE date = %s 
                ORDER BY shift_start ASC
            """, (date,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching schedule: {e}")
            return []
            self.close(connection)

    # Add team management methods
    def create_team(self, data):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO craftsmen_teams (
                    team_name, team_leader_id, description
                ) VALUES (%s, %s, %s)
            """, (data['team_name'], data['team_leader_id'], data['description']))
            team_id = cursor.lastrowid
            connection.commit()
            return team_id
        except Error as e:
            print(f"Error creating team: {e}")
            return None
        finally:
            self.close(connection)

    def add_team_member(self, team_name, craftsman_id, role):
        """Add a member to a team using team name instead of ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First get the team_id from the team_name
            cursor.execute("""
                SELECT team_id FROM craftsmen_teams 
                WHERE team_name = %s
            """, (team_name,))
            
            result = cursor.fetchone()
            if not result:
                print(f"Team not found: {team_name}")
                return False
            
            team_id = result[0]
            
            # Now add the member with the correct team_id
            cursor.execute("""
                INSERT INTO team_members (
                    team_id, craftsman_id, role, joined_date
                ) VALUES (%s, %s, %s, CURDATE())
            """, (team_id, craftsman_id, role))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding team member: {e}")
            return False
        finally:
            self.close(connection)

    def get_all_teams(self):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, c.first_name, c.last_name 
                FROM craftsmen_teams t
                LEFT JOIN craftsmen c ON t.team_leader_id = c.craftsman_id
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching teams: {e}")
            return []
        finally:
            self.close(connection)

    def get_team_members(self, team_identifier):
        """Get team members by team ID or team name"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if the identifier is a number (team_id) or string (team_name)
            if isinstance(team_identifier, int) or (isinstance(team_identifier, str) and team_identifier.isdigit()):
                # It's a team ID
                team_id = int(team_identifier)
            else:
                # It's a team name, get the ID first
                cursor.execute("""
                    SELECT team_id FROM craftsmen_teams 
                    WHERE team_name = %s
                """, (team_identifier,))
                
                result = cursor.fetchone()
                if not result:
                    print(f"Team not found: {team_identifier}")
                    return []
                    
                team_id = result['team_id']
            
            # Now get the members
            cursor.execute("""
                SELECT c.*, tm.role, tm.joined_date
                FROM team_members tm
                JOIN craftsmen c ON tm.craftsman_id = c.craftsman_id
                WHERE tm.team_id = %s
            """, (team_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching team members: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_performance(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get last month's performance
            cursor.execute("""
                SELECT 
                    COUNT(*) as month_count,
                    AVG(performance_rating) as month_rating,
                    (COUNT(CASE WHEN completion_time <= 8 THEN 1 END) * 100.0 / COUNT(*)) as month_percentage
                FROM craftsmen_work_history 
                WHERE craftsman_id = %s 
                AND task_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
            """, (craftsman_id,))
            month_data = cursor.fetchone()
            
            # Get last quarter's performance
            cursor.execute("""
                SELECT 
                    COUNT(*) as quarter_count,
                    AVG(performance_rating) as quarter_rating,
                    (COUNT(CASE WHEN completion_time <= 8 THEN 1 END) * 100.0 / COUNT(*)) as quarter_percentage
                FROM craftsmen_work_history 
                WHERE craftsman_id = %s 
                AND task_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            """, (craftsman_id,))
            quarter_data = cursor.fetchone()
            
            # Get last year's performance
            cursor.execute("""
                SELECT 
                    COUNT(*) as year_count,
                    AVG(performance_rating) as year_rating,
                    (COUNT(CASE WHEN completion_time <= 8 THEN 1 END) * 100.0 / COUNT(*)) as year_percentage
                FROM craftsmen_work_history 
                WHERE craftsman_id = %s 
                AND task_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            """, (craftsman_id,))
            year_data = cursor.fetchone()
            
            return {
                'month_count': month_data['month_count'],
                'month_rating': month_data['month_rating'],
                'month_percentage': month_data['month_percentage'],
                'quarter_count': quarter_data['quarter_count'],
                'quarter_rating': quarter_data['quarter_rating'],
                'quarter_percentage': quarter_data['quarter_percentage'],
                'year_count': year_data['year_count'],
                'year_rating': year_data['year_rating'],
                'year_percentage': year_data['year_percentage']
            }
        except Error as e:
            print(f"Error fetching craftsman performance: {e}")
            return {}
        finally:
            self.close(connection)

    def get_craftsman_skills_summary(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get skills summary grouped by category
            cursor.execute("""
                SELECT 
                    skill_name as category,
                    MAX(skill_level) as level,
                    COUNT(*) as cert_count,
                    COUNT(CASE WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 3 MONTH) 
                              AND expiry_date > CURDATE() THEN 1 END) as expiring
                FROM craftsmen_skills
                WHERE craftsman_id = %s
                GROUP BY skill_name
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman skills summary: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_training_summary(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get training summary
            cursor.execute("""
                SELECT 
                    training_name as type,
                    COUNT(CASE WHEN training_status = 'Completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN training_status = 'In Progress' THEN 1 END) as in_progress,
                    COUNT(CASE WHEN training_status = 'Scheduled' THEN 1 END) as required
                FROM craftsmen_training
                WHERE craftsman_id = %s
                GROUP BY training_name
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman training summary: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_workload(self, craftsman_id, period):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Convert period to SQL interval
            interval_map = {
                'Last Week': 'WEEK',
                'Last Month': 'MONTH',
                'Last Quarter': '3 MONTH',
                'Last Year': 'YEAR'
            }
            interval = interval_map.get(period, 'MONTH')
            
            # Get workload statistics
            cursor.execute("""
                SELECT 
                    task_type as name,
                    COUNT(*) as tasks,
                    SUM(completion_time) as hours,
                    (AVG(performance_rating) * 20) as efficiency
                FROM craftsmen_work_history
                WHERE craftsman_id = %s
                AND task_date >= DATE_SUB(CURDATE(), INTERVAL 1 """ + interval + """)
                GROUP BY task_type
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman workload: {e}")
            return []
        finally:
            self.close(connection)

    def export_craftsman_reports(self, craftsman_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get all relevant data for export
            performance = self.get_craftsman_performance(craftsman_id)
            skills = self.get_craftsman_skills_summary(craftsman_id)
            training = self.get_craftsman_training_summary(craftsman_id)
            workload = self.get_craftsman_workload(craftsman_id, 'Last Year')
            
            # Create export data structure
            export_data = {
                'performance': performance,
                'skills': skills,
                'training': training,
                'workload': workload
            }
            
            # Export to JSON (you can modify this to export to CSV or other formats)
            craftsman = self.get_craftsman_by_id(craftsman_id)
            filename = f"craftsman_report_{craftsman['employee_id']}_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=4)
            
            return True
        except Error as e:
            print(f"Error exporting craftsman reports: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_performance_trend(self, craftsman_id, period='MONTH'):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get daily performance ratings for trend analysis
            cursor.execute("""
                SELECT 
                    task_date,
                    AVG(performance_rating) as avg_rating,
                    COUNT(*) as task_count,
                    AVG(completion_time) as avg_time
                FROM craftsmen_work_history
                WHERE craftsman_id = %s
                AND task_date >= DATE_SUB(CURDATE(), INTERVAL 1 """ + period + """)
                GROUP BY task_date
                ORDER BY task_date
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman performance trend: {e}")
            return []
        finally:
            self.close(connection)

    def remove_team_member(self, team_name, member_name):
        """Remove a member from a team"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First get the team_id and craftsman_id
            cursor.execute("""
                SELECT team_id FROM craftsmen_teams 
                WHERE team_name = %s
            """, (team_name,))
            team_id = cursor.fetchone()[0]
            
            # Get craftsman_id from the full name
            first_name, last_name = member_name.split(' ', 1)
            cursor.execute("""
                SELECT craftsman_id FROM craftsmen 
                WHERE first_name = %s AND last_name = %s
            """, (first_name, last_name))
            craftsman_id = cursor.fetchone()[0]
            
            # Remove the member
            cursor.execute("""
                DELETE FROM team_members 
                WHERE team_id = %s AND craftsman_id = %s
            """, (team_id, craftsman_id))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error removing team member: {e}")
            return False
        finally:
            self.close(connection)

    def get_team_performance(self, team_name):
        """Get performance metrics for a team"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get team_id first
            cursor.execute("""
                SELECT team_id FROM craftsmen_teams 
                WHERE team_name = %s
            """, (team_name,))
            team_id = cursor.fetchone()['team_id']
            
            # Get aggregated performance metrics for all team members
            cursor.execute("""
                SELECT 
                    COUNT(*) as tasks_completed,
                    AVG(completion_time) as avg_completion_time,
                    (AVG(performance_rating) * 20) as efficiency_rate,
                    (COUNT(CASE WHEN completion_time <= 8 THEN 1 END) * 100.0 / COUNT(*)) as on_time_rate
                FROM craftsmen_work_history wh
                JOIN team_members tm ON wh.craftsman_id = tm.craftsman_id
                WHERE tm.team_id = %s
                AND wh.task_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
            """, (team_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching team performance: {e}")
            return None
        finally:
            self.close(connection)

    def search_craftsmen(self, criteria):
        """Search craftsmen based on given criteria"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Build the WHERE clause dynamically based on search criteria
            where_conditions = []
            params = []
            
            if criteria.get('name'):
                where_conditions.append("(LOWER(first_name) LIKE LOWER(%s) OR LOWER(last_name) LIKE LOWER(%s))")
                name_param = f"%{criteria['name']}%"
                params.extend([name_param, name_param])
            
            if criteria.get('specialization'):
                where_conditions.append("LOWER(specialization) = LOWER(%s)")
                params.append(criteria['specialization'])
            
            if criteria.get('experience_level'):
                where_conditions.append("LOWER(experience_level) = LOWER(%s)")
                params.append(criteria['experience_level'])
            
            if criteria.get('status'):
                where_conditions.append("LOWER(status) = LOWER(%s)")
                params.append(criteria['status'])
            
            # Construct the final query
            query = "SELECT * FROM craftsmen"
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            query += " ORDER BY last_modified DESC"
            
            print(f"Executing query: {query} with params: {params}")  # Debug print
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            print(f"Found {len(results)} results")  # Debug print
            return results
            
        except Error as e:
            print(f"Error searching craftsmen: {e}")
            return []
        finally:
            self.close(connection)

    def update_team(self, data):
        """Update an existing team"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First get the team_id from the original team name
            cursor.execute("""
                SELECT team_id FROM craftsmen_teams 
                WHERE team_name = %s
            """, (data['original_name'],))
            
            result = cursor.fetchone()
            if not result:
                print(f"Team not found: {data['original_name']}")
                return False
            
            team_id = result[0]
            
            # Now update the team
            cursor.execute("""
                UPDATE craftsmen_teams
                SET team_name = %s, team_leader_id = %s, description = %s
                WHERE team_id = %s
            """, (data['team_name'], data['team_leader_id'], data['description'], team_id))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating team: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_teams(self, craftsman_id):
        """Get all teams that a craftsman belongs to"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT t.team_id, t.team_name, t.description, 
                       c.first_name as leader_first_name, c.last_name as leader_last_name,
                       tm.role, tm.joined_date
                FROM team_members tm
                JOIN craftsmen_teams t ON tm.team_id = t.team_id
                LEFT JOIN craftsmen c ON t.team_leader_id = c.craftsman_id
                WHERE tm.craftsman_id = %s
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching craftsman teams: {e}")
            return []
        finally:
            self.close(connection)

    def create_work_order(self, work_order_data):
        """Create a new work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Convert JSON fields
            tools_required = json.dumps(work_order_data.get('tools_required', []))
            spares_required = json.dumps(work_order_data.get('spares_required', []))
            
            # Insert work order
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    craftsman_id,
                    team_id,
                    assignment_type,
                    priority,
                    status,
                    created_date,
                    due_date,
                    completed_date,
                    estimated_hours,
                    actual_hours,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data['priority'],
                work_order_data.get('status', 'Open'),
                datetime.now().date(),
                work_order_data['due_date'],
                work_order_data.get('completed_date'),
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('actual_hours', 0),
                tools_required,
                spares_required,
                work_order_data.get('notes', ''),
                work_order_data.get('schedule_id')
            ))
            
            work_order_id = cursor.lastrowid
            connection.commit()

            return work_order_id
            
        except Exception as e:
            print(f"Error creating work order: {e}")
            return None
        finally:
            self.close(connection)

    def update_work_order(self, work_order_data):
        """Update an existing work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get current status and equipment_id
            cursor.execute("""
                SELECT status, equipment_id FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_data['work_order_id'],))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            current_status = result[0]
            current_equipment_id = result[1]
            
            # Update work order
            cursor.execute("""
                UPDATE work_orders SET
                    title = %s,
                    description = %s,
                    equipment_id = %s,
                    assignment_type = %s,
                    craftsman_id = %s,
                    team_id = %s,
                    priority = %s,
                    status = %s,
                    due_date = %s,
                    completed_date = %s,
                    estimated_hours = %s,
                    actual_hours = %s,
                    tools_required = %s,
                    spares_required = %s,
                    notes = %s
                WHERE work_order_id = %s
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['assignment_type'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data['priority'],
                work_order_data['status'],
                work_order_data['due_date'],
                work_order_data['completed_date'],
                work_order_data['estimated_hours'],
                work_order_data['actual_hours'],
                json.dumps(work_order_data.get('tools_required', [])),
                json.dumps(work_order_data.get('spares_required', [])),
                work_order_data['notes'],
                work_order_data['work_order_id']
            ))
            
            connection.commit()
            
            # Add to equipment history if status changed to Completed
            if current_status != "Completed" and work_order_data['status'] == "Completed" and work_order_data['equipment_id']:
                assignee = ""
                if work_order_data['assignment_type'] == 'Individual':
                    assignee = f"Completed by: {self.get_craftsman_name(work_order_data['craftsman_id'])}"
                else:
                    team_name = self.get_team_name(work_order_data['team_id'])
                    assignee = f"Completed by team: {team_name}"
                
                cursor.execute("""
                    INSERT INTO equipment_history (
                        equipment_id, date, event_type, description, performed_by, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    work_order_data['equipment_id'],
                    datetime.now().date(),
                    "Work Order Completed",
                    f"Work Order #{work_order_data['work_order_id']}: {work_order_data['title']}",
                    assignee,
                    work_order_data['notes']
                ))
                connection.commit()
            
            return True
        except Error as e:
            print(f"Error updating work order: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_name(self, craftsman_id):
        """Get craftsman name from ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT first_name, last_name FROM craftsmen
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            result = cursor.fetchone()
            if result:
                return f"{result['first_name']} {result['last_name']}"
            return "Unknown"
        except Error as e:
            print(f"Error getting craftsman name: {e}")
            return "Unknown"
        finally:
            self.close(connection)

    def update_work_order_status(self, work_order_id, new_status):
        """Update the status of a work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get current status and equipment ID
            cursor.execute("""
                SELECT status, equipment_id, craftsman_id, title
                FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            current_status, equipment_id, craftsman_id, title = result
            
            # Update status
            cursor.execute("""
                UPDATE work_orders SET
                    status = %s,
                    completed_date = CASE WHEN %s = 'Completed' THEN CURDATE() ELSE NULL END
                WHERE work_order_id = %s
            """, (new_status, new_status, work_order_id))
            
            connection.commit()
            
            # Add to equipment history if status changed to Completed
            if current_status != "Completed" and new_status == "Completed" and equipment_id:
                cursor.execute("""
                    INSERT INTO equipment_history (
                        equipment_id, date, event_type, description, performed_by
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    equipment_id,
                    datetime.now().date(),
                    "Work Order Completed",
                    f"Work Order #{work_order_id}: {title}",
                    f"Completed by: {self.get_craftsman_name(craftsman_id)}"
                ))
                connection.commit()
            
            return True
        except Error as e:
            print(f"Error updating work order status: {e}")
            return False
        finally:
            self.close(connection)

    def delete_work_order(self, work_order_id):
        """Delete a work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                DELETE FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting work order: {e}")
            return False
        finally:
            self.close(connection)

    def get_all_work_orders(self):
        """Get all work orders"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                ORDER BY wo.created_date DESC
            """)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_order_by_id(self, work_order_id):
        """Get work order by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.work_order_id = %s
            """, (work_order_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting work order: {e}")
            return None
        finally:
            self.close(connection)

    def get_recent_work_orders(self, limit=10):
        """Get recent work orders"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.work_order_id, wo.title, wo.status, wo.due_date,
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                ORDER BY wo.created_date DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting recent work orders: {e}")
            return []
        finally:
            self.close(connection)

    def get_upcoming_maintenance(self, limit=10):
        """Get upcoming scheduled maintenance tasks"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT ms.task_id, ms.task_name, ms.next_due as due_date,
                       e.equipment_name,
                       CASE 
                           WHEN DATEDIFF(ms.next_due, CURDATE()) <= 3 THEN 'Critical'
                           WHEN DATEDIFF(ms.next_due, CURDATE()) <= 7 THEN 'High'
                           WHEN DATEDIFF(ms.next_due, CURDATE()) <= 14 THEN 'Medium'
                           ELSE 'Low'
                       END as priority
                FROM maintenance_schedule ms
                JOIN equipment_registry e ON ms.equipment_id = e.equipment_id
                WHERE ms.next_due >= CURDATE()
                ORDER BY ms.next_due ASC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting upcoming maintenance: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_order_statistics(self):
        """Get work order statistics"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM work_orders")
            total = cursor.fetchone()['count']
            
            # Get open count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE status IN ('Open', 'In Progress', 'On Hold')
            """)
            open_count = cursor.fetchone()['count']
            
            # Get completed count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE status = 'Completed'
            """)
            completed = cursor.fetchone()['count']
            
            # Get overdue count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE due_date < CURDATE() AND status NOT IN ('Completed', 'Cancelled')
            """)
            overdue = cursor.fetchone()['count']
            
            return {
                'total': total,
                'open': open_count,
                'completed': completed,
                'overdue': overdue
            }
        except Error as e:
            print(f"Error getting work order statistics: {e}")
            return None
        finally:
            self.close(connection)

    def get_work_orders_by_date(self, date):
        """Get work orders for a specific date"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date = %s
                ORDER BY wo.created_date DESC
            """, (date,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders by date: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_orders_by_date_range(self, start_date, end_date):
        """Get work orders for a date range"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date BETWEEN %s AND %s
                ORDER BY wo.due_date ASC
            """, (start_date, end_date))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders by date range: {e}")
            return []
        finally:
            self.close(connection)

    def get_recent_reports(self, limit=10):
        """Get recent reports"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM work_order_reports
                ORDER BY created_date DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting recent reports: {e}")
            return []
        finally:
            self.close(connection)

    def save_report_record(self, report_name, file_path, parameters):
        """Save a record of the generated report"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Convert dates to string format in parameters
            if isinstance(parameters, dict):
                for key, value in parameters.items():
                    if hasattr(value, 'strftime'):  # Check if it's a date/datetime object
                        parameters[key] = value.strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO work_order_reports (
                    report_name, report_type, file_path, parameters
                ) VALUES (%s, %s, %s, %s)
            """, (
                report_name,
                file_path.split('.')[-1].upper(),
                file_path,
                json.dumps(parameters)
            ))
            
            connection.commit()
        except Error as e:
            print(f"Error saving report record: {e}")
        finally:
            self.close(connection)

    def export_to_csv(self, file_path, data):
        """Export data to CSV file"""
        try:
            if not data:
                return False
            
            with open(file_path, 'w', newline='') as csvfile:
                # Get column headers from first row
                headers = list(data[0].keys())
                
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_excel(self, file_path, data, summary=None):
        """Export data to Excel file"""
        try:
            import xlsxwriter
            
            if not data:
                return False
            
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet('Data')
            
            # Add headers
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header.replace('_', ' ').title())
            
            # Add data
            for row, item in enumerate(data, start=1):
                for col, header in enumerate(headers):
                    worksheet.write(row, col, item.get(header, ''))
            
            # Add summary if provided
            if summary:
                summary_sheet = workbook.add_worksheet('Summary')
                summary_sheet.write(0, 0, 'Metric')
                summary_sheet.write(0, 1, 'Value')
                
                row = 1
                for key, value in summary.items():
                    if key not in ['start_date', 'end_date']:
                        summary_sheet.write(row, 0, key.replace('_', ' ').title())
                        summary_sheet.write(row, 1, value)
                        row += 1
            
            workbook.close()
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False

    def get_work_orders_for_report(self, start_date, end_date, status_filter=None):
        """
        Get work orders for reporting within a date range and optional status filter.
        
        Args:
            start_date: Start date for the report period
            end_date: End date for the report period
            status_filter: Optional status to filter by
            
        Returns:
            List of work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    wo.work_order_id,
                    wo.title,
                    wo.description,
                    wo.status,
                    wo.priority,
                    wo.created_date,
                    wo.due_date,
                    wo.completed_date,
                    wo.estimated_hours,
                    wo.actual_hours,
                    (wo.actual_hours * 50) as labor_cost,
                    wo.total_cost as parts_cost,
                    ((wo.actual_hours * 50) + IFNULL(wo.total_cost, 0)) as total_cost,
                    e.equipment_name,
                    CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.created_date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if status_filter:
                query += " AND wo.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY wo.created_date DESC"
            
            cursor.execute(query, tuple(params))
            work_orders = cursor.fetchall()
            
            # Convert datetime objects to string for JSON serialization
            for wo in work_orders:
                if wo.get('created_date'):
                    wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
                if wo.get('due_date'):
                    wo['due_date'] = wo['due_date'].strftime('%Y-%m-%d')
                if wo.get('completed_date'):
                    wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
            
            return work_orders
        
        except Error as e:
            self.console_logger.error(f"Error getting work orders for report: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_order_costs(self, start_date, end_date, status_filter=None):
        """
        Get work order cost data for reporting.
        
        Args:
            start_date: Start date for the report period
            end_date: End date for the report period
            status_filter: Optional status to filter by
            
        Returns:
            List of work order dictionaries with cost information
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    wo.work_order_id,
                    wo.title,
                    wo.status,
                    wo.created_date,
                    wo.completed_date,
                    wo.estimated_hours,
                    wo.actual_hours,
                    wo.total_cost as parts_cost,
                    (wo.actual_hours * 50) as labor_cost,
                    ((wo.actual_hours * 50) + IFNULL(wo.total_cost, 0)) as total_cost,
                    e.equipment_name,
                    CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.created_date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if status_filter:
                query += " AND wo.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY wo.created_date DESC"
            
            cursor.execute(query, tuple(params))
            work_orders = cursor.fetchall()
            
            # Convert datetime objects to string for JSON serialization
            for wo in work_orders:
                if wo.get('created_date'):
                    wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
                if wo.get('completed_date'):
                    wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
                
                # Ensure numeric values are not None
                wo['estimated_hours'] = wo.get('estimated_hours', 0) or 0
                wo['actual_hours'] = wo.get('actual_hours', 0) or 0
                wo['labor_cost'] = wo.get('labor_cost', 0) or 0
                wo['parts_cost'] = wo.get('parts_cost', 0) or 0
                wo['total_cost'] = wo.get('total_cost', 0) or 0
            
            return work_orders
        
        except Error as e:
            self.console_logger.error(f"Error getting work order costs: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_orders_by_due_date(self, due_date):
        """
        Get work orders due on a specific date.
        
        Args:
            due_date: The due date to check
            
        Returns:
            List of work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date = %s
                ORDER BY wo.priority DESC
            """, (due_date,))
            
            return cursor.fetchall()
        except Error as e:
            self.console_logger.error(f"Error getting work orders by due date: {e}")
            return []
        finally:
            self.close(connection)

    def get_overdue_work_orders(self):
        """
        Get work orders that are overdue.
        
        Returns:
            List of overdue work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            today = datetime.now().date()
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date < %s
                AND wo.status NOT IN ('Completed', 'Cancelled')
                ORDER BY wo.due_date ASC, wo.priority DESC
            """, (today,))
            
            return cursor.fetchall()
        except Error as e:
            self.console_logger.error(f"Error getting overdue work orders: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_by_employee_id(self, employee_id):
        """
        Get craftsman by employee ID.
        
        Args:
            employee_id: The employee ID to search for
            
        Returns:
            Craftsman data dictionary or None if not found
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM craftsmen
                WHERE employee_id = %s
            """, (employee_id,))
            
            craftsman = cursor.fetchone()
            return craftsman
        except Error as e:
            self.console_logger.error(f"Error getting craftsman by employee ID: {e}")
            return None
        finally:
            self.close(connection)

    def get_craftsman_work_order_count(self, craftsman_id, status=None, due_date=None, completion_date=None):
        """
        Get count of work orders for a craftsman with optional filters.
        
        Args:
            craftsman_id: ID of the craftsman
            status: Optional status filter
            due_date: Optional due date filter
            completion_date: Optional completion date filter
            
        Returns:
            Count of work orders
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            query = """
                SELECT COUNT(*) FROM work_orders
                WHERE craftsman_id = %s
            """
            
            params = [craftsman_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if due_date:
                query += " AND due_date = %s"
                params.append(due_date)
            
            if completion_date:
                query += " AND completed_date = %s"
                params.append(completion_date)
            
            cursor.execute(query, tuple(params))
            count = cursor.fetchone()[0]
            
            return count
        except Error as e:
            self.console_logger.error(f"Error getting craftsman work order count: {e}")
            return 0
        finally:
            self.close(connection)

    def get_craftsman_pending_reports_count(self, craftsman_id):
        """
        Get count of work orders that need maintenance reports.
        
        Args:
            craftsman_id: ID of the craftsman
            
        Returns:
            Count of work orders needing reports
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First check if maintenance_reports table exists
            cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                # If table doesn't exist, count all completed/in progress work orders
                query = """
                    SELECT COUNT(*) FROM work_orders
                    WHERE craftsman_id = %s
                    AND status IN ('Completed', 'In Progress')
                """
                cursor.execute(query, (craftsman_id,))
            else:
                # Get work orders that are completed but don't have maintenance reports
                query = """
                    SELECT COUNT(*) FROM work_orders wo
                    LEFT JOIN maintenance_reports mr ON wo.work_order_id = mr.work_order_id
                    WHERE wo.craftsman_id = %s
                    AND wo.status IN ('Completed', 'In Progress')
                    AND mr.report_id IS NULL
                """
                cursor.execute(query, (craftsman_id,))
            
            count = cursor.fetchone()[0]
            return count
        except Error as e:
            self.console_logger.error(f"Error getting craftsman pending reports count: {e}")
            return 0
        finally:
            self.close(connection)

    def get_craftsman_work_orders(self, craftsman_id, due_date=None, status=None):
        """
        Get work orders assigned to a craftsman with optional filters.
        
        Args:
            craftsman_id: ID of the craftsman
            due_date: Optional due date filter
            status: Optional status filter
            
        Returns:
            List of work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT wo.*, e.equipment_name
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                WHERE wo.craftsman_id = %s
            """
            
            params = [craftsman_id]
            
            if due_date:
                query += " AND wo.due_date = %s"
                params.append(due_date)
            
            if status:
                query += " AND wo.status = %s"
                params.append(status)
            
            query += " ORDER BY wo.due_date ASC, wo.priority DESC"
            
            cursor.execute(query, tuple(params))
            work_orders = cursor.fetchall()
            
            # Convert datetime objects to string for display
            for wo in work_orders:
                if wo.get('created_date'):
                    wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
                if wo.get('due_date'):
                    wo['due_date'] = wo['due_date'].strftime('%Y-%m-%d')
                if wo.get('completed_date'):
                    wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
                
                # Check if this work order has a maintenance report
                wo['has_report'] = self.check_work_order_has_report(wo['work_order_id'])
            
            return work_orders
        except Error as e:
            self.console_logger.error(f"Error getting craftsman work orders: {e}")
            return []
        finally:
            self.close(connection)

    def check_work_order_has_report(self, work_order_id):
        """
        Check if a work order has a maintenance report.
        
        Args:
            work_order_id: ID of the work order
            
        Returns:
            Boolean indicating if report exists
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First check if maintenance_reports table exists
            cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                # If table doesn't exist, no reports exist
                return False
            
            query = """
                SELECT COUNT(*) FROM maintenance_reports
                WHERE work_order_id = %s
            """
            
            cursor.execute(query, (work_order_id,))
            count = cursor.fetchone()[0]
            
            return count > 0
        except Error as e:
            self.console_logger.error(f"Error checking if work order has report: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_recent_activity(self, craftsman_id, limit=10):
        """
        Get recent activity for a craftsman.
        
        Args:
            craftsman_id: ID of the craftsman
            limit: Maximum number of activities to return
            
        Returns:
            List of activity dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # For development, return some dummy activities
            activities = []
            today = datetime.now()
            
            # Add some work order activities
            work_orders = self.get_craftsman_work_orders(craftsman_id)
            for i, wo in enumerate(work_orders[:5]):
                activity_date = today - timedelta(days=i, hours=i*2)
                activities.append({
                    'activity_type': 'work_order',
                    'work_order_id': wo['work_order_id'],
                    'title': wo['title'],
                    'status': wo['status'],
                    'date': activity_date.strftime('%Y-%m-%d %H:%M'),
                    'description': f"Work Order #{wo['work_order_id']} - {wo['title']} - Status changed to {wo['status']}"
                })
            
            # Sort by date
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return activities[:limit]
        except Error as e:
            self.console_logger.error(f"Error getting craftsman recent activity: {e}")
            return []
        finally:
            self.close(connection)

    def get_craftsman_maintenance_history(self, craftsman_id, from_date, to_date):
        """
        Get maintenance history for a craftsman within a date range.
        
        Args:
            craftsman_id: ID of the craftsman
            from_date: Start date for the history
            to_date: End date for the history
            
        Returns:
            List of maintenance history dictionaries
        """
        try:
            # For development, return some dummy history
            history = []
            
            # Get work orders for this craftsman
            work_orders = self.get_craftsman_work_orders(craftsman_id, status="Completed")
            
            for i, wo in enumerate(work_orders):
                # Create a history entry for each completed work order
                history_date = datetime.strptime(wo['completed_date'], '%Y-%m-%d') if wo.get('completed_date') else datetime.now() - timedelta(days=i)
                
                # Skip if outside date range
                if history_date.date() < from_date or history_date.date() > to_date:
                    continue
                    
                equipment = self.get_equipment_by_id(wo['equipment_id']) if wo.get('equipment_id') else None
                equipment_name = equipment['equipment_name'] if equipment else "Unknown Equipment"
                
                history.append({
                    'report_id': i + 1,  # Dummy report ID
                    'work_order_id': wo['work_order_id'],
                    'date': history_date.strftime('%Y-%m-%d'),
                    'equipment_name': equipment_name,
                    'equipment_id': wo.get('equipment_id'),
                    'maintenance_type': "Preventive" if i % 2 == 0 else "Corrective",
                    'description': wo['title']
                })
            
            return history
        except Error as e:
            self.console_logger.error(f"Error getting craftsman maintenance history: {e}")
            return []
        finally:
            if 'connection' in locals() and connection:
                self.close(connection)

    def get_craftsman_notifications(self, craftsman_id):
        """
        Get notifications for a craftsman.
        
        Args:
            craftsman_id: ID of the craftsman
            
        Returns:
            List of notification dictionaries
        """
        try:
            # For development, return some dummy notifications
            today = datetime.now()
            connection = self.connect()
            
            notifications = [
                {
                    'notification_id': 1,
                    'craftsman_id': craftsman_id,
                    'type': 'due_today',
                    'message': 'You have work orders due today',
                    'date': today.strftime('%Y-%m-%d %H:%M'),
                    'read': False
                },
                {
                    'notification_id': 2,
                    'craftsman_id': craftsman_id,
                    'type': 'upcoming',
                    'message': 'You have upcoming work orders due in 2 days',
                    'date': (today - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
                    'read': False
                },
                {
                    'notification_id': 3,
                    'craftsman_id': craftsman_id,
                    'type': 'overdue',
                    'message': 'You have overdue work orders that need attention',
                    'date': (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                    'read': True
                }
            ]
            
            return notifications
        except Error as e:
            self.console_logger.error(f"Error getting craftsman notifications: {e}")
            return []
        finally:
            if 'connection' in locals() and connection:
                self.close(connection)

    def mark_notifications_as_read(self, craftsman_id):
        """
        Mark all notifications for a craftsman as read.
        
        Args:
            craftsman_id: ID of the craftsman
            
        Returns:
            Boolean indicating success
        """
        # For development, just return True
        return True

    def create_maintenance_report(self, work_order_id, equipment_id, craftsman_id, report_data, comments=None):
        """
        Create a maintenance report.
        
        Args:
            work_order_id: ID of the work order
            equipment_id: ID of the equipment
            craftsman_id: ID of the craftsman
            report_data: JSON data for the report
            comments: Optional comments
            
        Returns:
            ID of the created report or None if failed
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if maintenance_reports table exists
            cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
            table_exists = cursor.fetchone()
            
            # Create table if it doesn't exist
            if not table_exists:
                cursor.execute("""
                    CREATE TABLE maintenance_reports (
                        report_id INT AUTO_INCREMENT PRIMARY KEY,
                        work_order_id INT NOT NULL,
                        equipment_id INT NOT NULL,
                        craftsman_id INT NOT NULL,
                        report_date DATETIME NOT NULL,
                        report_data JSON NOT NULL,
                        comments TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id),
                        FOREIGN KEY (equipment_id) REFERENCES equipment_registry(equipment_id),
                        FOREIGN KEY (craftsman_id) REFERENCES craftsmen(craftsman_id)
                    )
                """)
                connection.commit()
            
            query = """
                INSERT INTO maintenance_reports (
                    work_order_id, equipment_id, craftsman_id, 
                    report_date, report_data, comments
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                work_order_id, equipment_id, craftsman_id,
                datetime.now(), report_data, comments
            ))
            
            connection.commit()
            report_id = cursor.lastrowid
            
            # Update work order status to completed if not already
            self.update_work_order_status({
                'work_order_id': work_order_id,
                'status': 'Completed',
                'completed_date': datetime.now().date()
            })
            
            return report_id
        except Error as e:
            self.console_logger.error(f"Error creating maintenance report: {e}")
            return None
        finally:
            self.close(connection)
    def add_report_attachment(self, report_id, file_path):
        """
        Add an attachment to a maintenance report.
        
        Args:
            report_id: ID of the report
            file_path: Path to the attachment file
            
        Returns:
            Boolean indicating success
        """
        # For development, just return True
        return True

    def get_maintenance_report(self, report_id):
        """
        Get a maintenance report by ID.
        
        Args:
            report_id: ID of the report
            
        Returns:
            Report dictionary or None if not found
        """
        # For development, return a dummy report
        return {
            'report_id': report_id,
            'work_order_id': 1,
            'equipment_id': 1,
            'craftsman_id': 1,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'report_data': json.dumps({
                'general': {
                    'maintenance_type': 'Preventive',
                    'initial_condition': 'Operational',
                    'final_condition': 'Operational'
                },
                'inspection': {
                    'visual_external_damage': False,
                    'visual_corrosion': False,
                    'operational_unusual_noise': False,
                    'additional_findings': 'No issues found'
                }
            }),
            'comments': 'Regular maintenance completed successfully.'
        }

    def update_work_order_status(self, data):
        """
        Update work order status.
        
        Args:
            data: Dictionary with work_order_id, status, and optional fields
            
        Returns:
            Boolean indicating success
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Build query dynamically based on provided fields
            query = "UPDATE work_orders SET "
            params = []
            
            if 'status' in data:
                query += "status = %s, "
                params.append(data['status'])
            
            if 'completed_date' in data:
                query += "completed_date = %s, "
                params.append(data['completed_date'])
            
            if 'notes' in data:
                query += "notes = %s, "
                params.append(data['notes'])
            
            # Remove trailing comma and space
            query = query.rstrip(', ')
            
            # Add WHERE clause
            query += " WHERE work_order_id = %s"
            params.append(data['work_order_id'])
            
            cursor.execute(query, tuple(params))
            connection.commit()
            
            return True
        except Error as e:
            self.console_logger.error(f"Error updating work order status: {e}")
            return False
        finally:
            self.close(connection)

    def get_inventory_items(self):
        """Get all inventory items"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT i.*, c.name as category, s.name as supplier_name
                FROM inventory_items i
                LEFT JOIN inventory_categories c ON i.category_id = c.category_id
                LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
                ORDER BY i.last_modified DESC
            """)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting inventory items: {e}")
            return []
        finally:
            self.close(connection)

    def get_inventory_item(self, item_id):
        """Get a single inventory item by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT i.*, c.name as category, s.name as supplier_name
                FROM inventory_items i
                LEFT JOIN inventory_categories c ON i.category_id = c.category_id
                LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
                WHERE i.item_id = %s
            """, (item_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting inventory item: {e}")
            return None
        finally:
            self.close(connection)

    def get_inventory_items_by_category(self, category_name):
        """Get inventory items by category name"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT i.*, c.name as category, s.name as supplier_name
                FROM inventory_items i
                LEFT JOIN inventory_categories c ON i.category_id = c.category_id
                LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
                WHERE c.name = %s
                ORDER BY i.last_modified DESC
            """, (category_name,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting inventory items by category: {e}")
            return []
        finally:
            self.close(connection)

    def add_inventory_item(self, data):
        """Add a new inventory item"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get category_id if category name is provided
            category_id = data.get('category_id')
            if not category_id and 'category' in data:
                cursor.execute("""
                    SELECT category_id FROM inventory_categories
                    WHERE name = %s
                """, (data['category'],))
                result = cursor.fetchone()
                if result:
                    category_id = result[0]
                else:
                    # Create new category
                    cursor.execute("""
                        INSERT INTO inventory_categories (name)
                        VALUES (%s)
                    """, (data['category'],))
                    category_id = cursor.lastrowid
            
            # Insert item
            cursor.execute("""
                INSERT INTO inventory_items (
                    category_id, supplier_id, item_code, name,
                    description, unit, unit_cost, quantity,
                    minimum_quantity, reorder_point, location
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                category_id,
                data.get('supplier_id'),
                data['item_code'],
                data['name'],
                data.get('description'),
                data.get('unit'),
                data.get('unit_cost', 0.00),
                data.get('quantity', 0),
                data.get('minimum_quantity', 0),
                data.get('reorder_point', 0),
                data.get('location')
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding inventory item: {e}")
            return False
        finally:
            self.close(connection)

    def get_tool_checkout_status(self, item_id):
        """Get the current checkout status of a tool"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT tc.*, CONCAT(c.first_name, ' ', c.last_name) as craftsman_name
                FROM tool_checkouts tc
                JOIN craftsmen c ON tc.craftsman_id = c.craftsman_id
                WHERE tc.item_id = %s
                AND tc.status = 'Checked Out'
                AND tc.actual_return_date IS NULL
                ORDER BY tc.checkout_date DESC
                LIMIT 1
            """, (item_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting tool checkout status: {e}")
            return None
        finally:
            self.close(connection)

    def checkout_tool(self, data):
        """Check out a tool"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO tool_checkouts (
                    item_id, craftsman_id, work_order_id,
                    expected_return_date, notes
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                data['item_id'],
                data['craftsman_id'],
                data.get('work_order_id'),
                data['expected_return_date'],
                data.get('notes')
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error checking out tool: {e}")
            return False
        finally:
            self.close(connection)

    def checkin_tool(self, data):
        """Check in a tool"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE tool_checkouts
                SET actual_return_date = CURRENT_TIMESTAMP,
                    status = 'Returned',
                    notes = CONCAT(IFNULL(notes, ''), '\nReturn Condition: ', %s, '\nReturn Notes: ', %s)
                WHERE item_id = %s
                AND status = 'Checked Out'
                AND actual_return_date IS NULL
            """, (
                data['condition'],
                data.get('notes', ''),
                data['item_id']
            ))
            
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error checking in tool: {e}")
            return False
        finally:
            self.close(connection)

    def get_inventory_categories(self):
        """Get all inventory categories"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM inventory_categories ORDER BY name")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting inventory categories: {e}")
            return []
        finally:
            self.close(connection)

    def get_recent_transactions(self, limit=10):
        """Get recent inventory transactions"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT tc.*, i.item_code, i.name as item_name,
                       CONCAT(c.first_name, ' ', c.last_name) as performed_by
                FROM tool_checkouts tc
                JOIN inventory_items i ON tc.item_id = i.item_id
                JOIN craftsmen c ON tc.craftsman_id = c.craftsman_id
                ORDER BY tc.checkout_date DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting recent transactions: {e}")
            return []
        finally:
            self.close(connection)

    def get_suppliers(self):
        """Get all suppliers"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM suppliers
                WHERE status = 'Active'
                ORDER BY name
            """)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting suppliers: {e}")
            return []
        finally:
            self.close(connection)

    def get_supplier_by_name(self, name):
        """Get a supplier by name"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM suppliers
                WHERE name = %s
            """, (name,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting supplier: {e}")
            return None
        finally:
            self.close(connection)

    def add_supplier(self, data):
        """Add a new supplier"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO suppliers (
                    name, contact_person, phone, email,
                    address, notes, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['name'],
                data.get('contact_person'),
                data.get('phone'),
                data.get('email'),
                data.get('address'),
                data.get('notes'),
                data.get('status', 'Active')
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding supplier: {e}")
            return False
        finally:
            self.close(connection)

    def get_team_name(self, team_id):
        """Get team name from team ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT team_name FROM craftsmen_teams
                WHERE team_id = %s
            """, (team_id,))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            return "Unknown Team"
        except Error as e:
            print(f"Error getting team name: {e}")
            return "Unknown Team"
        finally:
            self.close(connection)

    def get_team_by_name(self, team_name):
        """Get team details by team name"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT t.*, 
                       l.first_name as leader_first_name, 
                       l.last_name as leader_last_name
                FROM craftsmen_teams t
                LEFT JOIN craftsmen l ON t.team_leader_id = l.craftsman_id
                WHERE t.team_name = %s
            """, (team_name,))
            
            team = cursor.fetchone()
            if not team:
                print(f"Team not found: {team_name}")
                return None
            
            # Ensure all required fields are present
            team = {
                'team_id': team.get('team_id'),
                'team_name': team.get('team_name', 'Unknown Team'),
                'team_leader_id': team.get('team_leader_id'),
                'description': team.get('description', ''),
                'leader_first_name': team.get('leader_first_name', ''),
                'leader_last_name': team.get('leader_last_name', ''),
                'created_at': team.get('created_at')
            }
            return team
            
        except Exception as e:
            print(f"Error getting team by name: {e}")
            return None
        finally:
            if 'connection' in locals():
                self.close(connection)

    def get_work_orders_by_team(self, team_id):
        """Get work orders assigned to a team"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, e.equipment_name
                FROM work_orders wo
                LEFT JOIN equipment e ON wo.equipment_id = e.equipment_id
                WHERE wo.team_id = %s
                ORDER BY wo.created_date DESC
            """, (team_id,))
            
            work_orders = cursor.fetchall()
            return work_orders
            
        except Exception as e:
            print(f"Error getting work orders by team: {e}")
            return []
        finally:
            if 'connection' in locals():
                self.close(connection)

    def create_recurring_work_order(self, work_order_data, schedule_data):
        """Create a recurring work order with scheduling information"""
        connection = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First create the schedule record
            cursor.execute("""
                INSERT INTO maintenance_schedules (
                    frequency,
                    frequency_unit,
                    start_date,
                    end_date,
                    last_generated,
                    notification_days_before,
                    notification_emails
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                schedule_data['frequency'],
                schedule_data['frequency_unit'],
                schedule_data['start_date'],
                schedule_data.get('end_date'),
                None,
                schedule_data.get('notification_days_before', 2),
                json.dumps(schedule_data.get('notification_emails', []))
            ))
            
            schedule_id = cursor.lastrowid
            
            # Create the work order template
            cursor.execute("""
                INSERT INTO work_order_templates (
                    title,
                    description,
                    equipment_id,
                    priority,
                    estimated_hours,
                    assignment_type,
                    craftsman_id,
                    team_id,
                    tools_required,
                    spares_required,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['priority'],
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                json.dumps(work_order_data.get('tools_required', [])),
                json.dumps(work_order_data.get('spares_required', [])),
                schedule_id
            ))
            
            # Now create the first work order instance directly instead of calling create_work_order
            tools_required = json.dumps(work_order_data.get('tools_required', []))
            spares_required = json.dumps(work_order_data.get('spares_required', []))
            
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    craftsman_id,
                    team_id,
                    assignment_type,
                    priority,
                    status,
                    created_date,
                    due_date,
                    completed_date,
                    estimated_hours,
                    actual_hours,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data['priority'],
                work_order_data.get('status', 'Open'),
                datetime.now().date(),
                work_order_data['due_date'],
                work_order_data.get('completed_date'),
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('actual_hours', 0),
                tools_required,
                spares_required,
                work_order_data.get('notes', ''),
                schedule_id
            ))
            
            work_order_id = cursor.lastrowid
            
            # Update the last_generated date in the schedule
            cursor.execute("""
                UPDATE maintenance_schedules
                SET last_generated = %s
                WHERE schedule_id = %s
            """, (datetime.now().date(), schedule_id))
            
            connection.commit()
            return True
            
        except Exception as e:
            print(f"Error creating recurring work order: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                self.close(connection)

    def get_pending_scheduled_work_orders(self):
        """Get work orders that need to be generated based on schedules"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    wot.*,
                    ms.*,
                    CASE 
                        WHEN ms.last_generated IS NULL THEN ms.start_date
                        WHEN ms.frequency_unit = 'days' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency DAY)
                        WHEN ms.frequency_unit = 'weeks' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency WEEK)
                        WHEN ms.frequency_unit = 'months' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency MONTH)
                    END as next_due_date
                FROM work_order_templates wot
                JOIN maintenance_schedules ms ON wot.schedule_id = ms.schedule_id
                WHERE 
                    (ms.last_generated IS NULL AND ms.start_date <= CURDATE())
                    OR
                    (
                        CASE 
                            WHEN ms.frequency_unit = 'days' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency DAY)
                            WHEN ms.frequency_unit = 'weeks' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency WEEK)
                            WHEN ms.frequency_unit = 'months' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency MONTH)
                        END <= CURDATE()
                    )
                    AND (ms.end_date IS NULL OR ms.end_date >= CURDATE())
            """)
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting pending scheduled work orders: {e}")
            return []
        finally:
            self.close(connection)

    def generate_scheduled_work_order(self, template, due_date):
        """Generate a work order from a template"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Create the work order
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    priority,
                    status,
                    created_date,
                    due_date,
                    estimated_hours,
                    assignment_type,
                    craftsman_id,
                    team_id,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template['title'],
                template['description'],
                template['equipment_id'],
                template['priority'],
                'Open',
                datetime.now().date(),
                due_date,
                template['estimated_hours'],
                template['assignment_type'],
                template['craftsman_id'],
                template['team_id'],
                template['tools_required'],
                template['spares_required'],
                f"Auto-generated from schedule #{template['schedule_id']}",
                template['schedule_id']
            ))
            
            work_order_id = cursor.lastrowid
            
            # Update the last generated date
            cursor.execute("""
                UPDATE maintenance_schedules
                SET last_generated = %s
                WHERE schedule_id = %s
            """, (datetime.now().date(), template['schedule_id']))
            
            connection.commit()
            return work_order_id
            
        except Exception as e:
            print(f"Error generating scheduled work order: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if connection:
                self.close(connection)

    def send_work_order_notifications(self, work_order_id, recipients, notification_type):
        """Send email notifications for work orders"""
        try:
            # Get work order details
            work_order = self.get_work_order_by_id(work_order_id)
            if not work_order:
                return False
            
            # Get email settings
            settings = self.get_email_settings()
            if not settings or not settings.get('enabled'):
                return False
            
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings['from_address']
            msg['To'] = ', '.join(recipients)
            
            if notification_type == 'new_scheduled':
                msg['Subject'] = f"New Scheduled Work Order: {work_order['title']}"
                body = f"""
                A new scheduled work order has been generated:
                
                Title: {work_order['title']}
                Equipment: {work_order['equipment_name']}
                Priority: {work_order['priority']}
                Due Date: {work_order['due_date']}
                
                Please log into the CMMS system to view the full details.
                """
            elif notification_type == 'upcoming':
                msg['Subject'] = f"Upcoming Work Order Due: {work_order['title']}"
                body = f"""
                Reminder: The following work order is due soon:
                
                Title: {work_order['title']}
                Equipment: {work_order['equipment_name']}
                Priority: {work_order['priority']}
                Due Date: {work_order['due_date']}
                
                Please ensure this work order is completed on time.
                """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(settings['server'], int(settings['port'])) as server:
                if settings.get('use_tls'):
                    server.starttls()
                if settings.get('username') and settings.get('password'):
                    server.login(settings['username'], settings['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending work order notification: {e}")
            return False

    def get_email_settings(self):
        """Get email notification settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM email_settings LIMIT 1")
            settings = cursor.fetchone()
            
            return settings
            
        except Exception as e:
            print(f"Error getting email settings: {e}")
            return None
        finally:
            self.close(connection)

    def save_email_settings(self, settings):
        """Save email notification settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO email_settings (
                    enabled,
                    server,
                    port,
                    use_tls,
                    username,
                    password,
                    from_address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    enabled = VALUES(enabled),
                    server = VALUES(server),
                    port = VALUES(port),
                    use_tls = VALUES(use_tls),
                    username = VALUES(username),
                    password = VALUES(password),
                    from_address = VALUES(from_address)
            """, (
                settings['enabled'],
                settings['server'],
                settings['port'],
                settings.get('use_tls', True),
                settings.get('username'),
                settings.get('password'),
                settings['from_address']
            ))
            
            connection.commit()
            return True
            
        except Exception as e:
            print(f"Error saving email settings: {e}")
            return False
        finally:
            self.close(connection)

    def check_upcoming_work_orders(self):
        """Check for work orders due soon and send notifications"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # First check if notification_sent column exists
            cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'notification_sent'")
            has_notification_column = cursor.fetchone() is not None
            
            # Adjust query based on column existence
            base_query = """
                SELECT wo.*, ms.notification_days_before, ms.notification_emails
                FROM work_orders wo
                JOIN maintenance_schedules ms ON wo.schedule_id = ms.schedule_id
                WHERE 
                    wo.status = 'Open'
                    AND wo.due_date BETWEEN CURDATE() 
                    AND DATE_ADD(CURDATE(), INTERVAL ms.notification_days_before DAY)
            """
            
            if has_notification_column:
                base_query += " AND wo.notification_sent = 0"
            
            cursor.execute(base_query)
            upcoming_orders = cursor.fetchall()
            
            for order in upcoming_orders:
                if order.get('notification_emails'):
                    # Send notification
                    if self.send_work_order_notifications(
                        order['work_order_id'],
                        json.loads(order['notification_emails']),
                        'upcoming'
                    ):
                        # Mark notification as sent if column exists
                        if has_notification_column:
                            cursor.execute("""
                                UPDATE work_orders
                                SET notification_sent = 1
                                WHERE work_order_id = %s
                            """, (order['work_order_id'],))
                            connection.commit()
            
            return True
            
        except Exception as e:
            print(f"Error checking upcoming work orders: {e}")
            return False
        finally:
            self.close(connection)

