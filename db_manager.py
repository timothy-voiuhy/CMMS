import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
import json
import logging
import traceback
from datetime import datetime

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
            
            # First get the craftsman_id using the employee_id
            cursor.execute("""
                SELECT craftsman_id FROM craftsmen 
                WHERE employee_id = %s
            """, (data['employee_id'],))
            result = cursor.fetchone()
            
            if not result:
                print("No craftsman found with employee_id:", data['employee_id'])
                return False
                
            craftsman_id = result[0]
            
            # Now update using the craftsman_id
            cursor.execute("""
                UPDATE craftsmen 
                SET first_name = %s, 
                    last_name = %s, 
                    phone = %s,
                    email = %s, 
                    specialization = %s, 
                    status = %s
                WHERE craftsman_id = %s
            """, (
                data['first_name'], 
                data['last_name'], 
                data['phone'],
                data['email'], 
                data['specialization'], 
                data['status'],
                craftsman_id
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

    def add_team_member(self, team_id, craftsman_id, role):
        try:
            connection = self.connect()
            cursor = connection.cursor()
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

    def get_team_members(self, team_id):
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
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

    def generate_team_report(self, team_name):
        """Generate a comprehensive report for a team"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get team details
            cursor.execute("""
                SELECT t.*, 
                       c.first_name as leader_first_name, 
                       c.last_name as leader_last_name
                FROM craftsmen_teams t
                LEFT JOIN craftsmen c ON t.team_leader_id = c.craftsman_id
                WHERE t.team_name = %s
            """, (team_name,))
            team_info = cursor.fetchone()
            
            if not team_info:
                return None
            
            # Get team members with their roles
            cursor.execute("""
                SELECT c.*, tm.role, tm.joined_date
                FROM team_members tm
                JOIN craftsmen c ON tm.craftsman_id = c.craftsman_id
                WHERE tm.team_id = %s
            """, (team_info['team_id'],))
            members = cursor.fetchall()
            
            # Get team performance metrics
            performance = self.get_team_performance(team_name)
            
            return {
                'team_info': team_info,
                'members': members,
                'performance': performance
            }
        except Error as e:
            print(f"Error generating team report: {e}")
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
