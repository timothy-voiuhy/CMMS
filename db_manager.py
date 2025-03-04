import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
import json
import logging
import traceback

class DatabaseManager:
    def __init__(self):
        connection = None
        self.console_logger = logging.getLogger('console')
        self.config = {
            'host': 'localhost',
            'user': 'CMMS',
            'password': 'cmms',
            'database': 'cmms_db'
        }

        self.connect()
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