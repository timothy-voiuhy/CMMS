import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
import json
import logging
import traceback
from datetime import datetime, timedelta
import os
import csv
from db_ops.admin_ops import AdminOps  # Import the admin operations class
from db_ops.work_order_ops import WorkOrder_Ops
from db_ops.db_init import DbInit

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
        # Initialize admin operations
        self.admin = AdminOps(self)  # Pass self as the parent database manager
        self.work_orders = WorkOrder_Ops(self)

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
        self.db_init  = DbInit(self)
        return self.db_init.initialize_database()

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

    def get_maintenance_task_by_id(self, task_id):
        """Get maintenance task details by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_schedule 
                WHERE task_id = %s
            """, (task_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching maintenance task: {e}")
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

            user_table_data = {
                "employee_id": data.get("employee_id"),
                "role": "craftsman",
                "access_level": None,
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "email": data.get("email", ""),
                "is_staff": False,
                "is_superuser": False
            }
            self.add_user(user_table_data)

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
        """Update craftsman information"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First update the users table
            cursor.execute("""
                UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    email = %s
                WHERE employee_id = %s
            """, (
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('email', ''),
                data.get('employee_id')
            ))
            
            # Then update the craftsmen table
            cursor.execute("""
                UPDATE craftsmen SET
                    first_name = %s,
                    last_name = %s,
                    phone = %s,
                    email = %s,
                    specialization = %s,
                    experience_level = %s,
                    hire_date = %s,
                    status = %s
                WHERE employee_id = %s
            """, (
                data.get('first_name'),
                data.get('last_name'),
                data.get('phone'),
                data.get('email'),
                data.get('specialization'),
                data.get('experience_level'),
                data.get('hire_date'),
                data.get('status'),
                data.get('employee_id')
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating craftsman: {e}")
            return False
        finally:
            self.close(connection)

    def add_craftsman_skill(self, data):
        """Add a skill to a craftsman's profile"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Ensure we're using the correct field names
            cursor.execute("""
                INSERT INTO craftsmen_skills (
                    craftsman_id, skill_name, skill_level, 
                    certification_date, expiry_date, 
                    certification_authority, certification_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['craftsman_id'],
                data['skill_name'],
                data['skill_level'],
                data['certification_date'],
                data['expiry_date'],
                data['certification_authority'],
                data.get('certification_number', '')  # Use the correct field name
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding craftsman skill: {e}")
            return False
        finally:
            self.close(connection)

    def get_craftsman_skills(self, craftsman_id):
        """Get skills for a craftsman"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM craftsmen_skills 
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting craftsman skills: {e}")
            return []
        finally:
            self.close(connection)

    def add_craftsman_training(self, data):
        """Add a training record to a craftsman's profile"""
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
                data['craftsman_id'],  # This should now be the internal ID
                data['training_name'],
                data['training_date'],
                data['completion_date'],
                data['training_provider'],
                data['certification_received'],
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
        """Get training records for a craftsman"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM craftsmen_training 
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting craftsman training: {e}")
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
        return self.work_orders.create_work_order(work_order_data)

    def update_work_order(self, work_order_data):
        return self.work_orders.update_work_order(work_order_data)

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
        return self.work_orders.update_work_order_status(work_order_id, new_status)

    def delete_work_order(self, work_order_id):
        return self.work_orders.delete_work_order(work_order_id)

    def get_all_work_orders(self):
        return self.work_orders.get_all_work_orders()

    def get_work_order_by_id(self, work_order_id):
        return self.work_orders.get_work_order_by_id(work_order_id)

    def get_recent_work_orders(self, limit=10):
        return self.work_orders.get_recent_work_orders(limit)

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
        return self.work_orders.get_work_order_statistics()

    def get_work_orders_by_date(self, date):
        return self.work_orders.get_work_orders_by_date(date)

    def get_work_orders_by_date_range(self, start_date, end_date):
        return self.work_orders.get_work_orders_by_date_range(start_date, end_date)

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
        return self.work_orders.get_work_orders_for_report(start_date, end_date, status_filter)

    def get_work_order_costs(self, start_date, end_date, status_filter=None):
        return self.work_orders.get_work_order_costs(start_date, end_date, status_filter)

    def get_work_orders_by_due_date(self, due_date):
        return self.work_orders.get_work_orders_by_due_date(due_date)

    def get_overdue_work_orders(self):
        return self.work_orders.get_overdue_work_orders()

    def get_completed_work_orders_by_equipment(self, equipment_id):
        """Get all completed work orders for a specific equipment"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM work_orders 
                WHERE equipment_id = %s 
                AND status = 'Completed'
                ORDER BY completed_date DESC
            """, (equipment_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching completed work orders: {e}")
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
        return self.work_orders.update_work_order_status(data)

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
        """Check if a tool is currently checked out"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM tool_checkouts
                WHERE item_id = %s AND status = 'Checked Out'
                LIMIT 1
            """, (item_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error checking tool checkout status: {e}")
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

    def get_team_by_id(self, team_id):
        """Get team details by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM craftsmen_teams 
                WHERE team_id = %s
            """, (team_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching team: {e}")
            return None
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
        return self.work_orders.get_work_orders_by_team(team_id)

    def create_recurring_work_order(self, work_order_data, schedule_data):
        return self.work_orders.create_recurring_work_order(work_order_data, schedule_data)

    def get_pending_scheduled_work_orders(self):
        return self.work_orders.get_pending_scheduled_work_orders()

    def generate_scheduled_work_order(self, template, due_date):
        return self.work_orders.generate_scheduled_work_order(template, due_date)

    def send_work_order_notifications(self, work_order_id, recipients, notification_type):
        """Send email notifications for work orders"""
        return self.work_orders.send_work_order_notifications(work_order_id, recipients, notification_type)

    def get_email_settings(self):
        return self.work_orders.get_email_settings()

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
        return self.work_orders.check_upcoming_work_orders()

    # Add proxy methods if needed for backward compatibility
    def verify_admin_password(self, password):
        """Proxy method to maintain compatibility"""
        return self.admin.verify_admin_password(password)
        
    def create_admin_tables(self):
        """Proxy method to maintain compatibility"""
        return self.admin.create_admin_tables()
    
    def add_audit_log_entry(self, username, action, details=None, status="Success", ip_address=None):
        """Proxy method to maintain compatibility"""
        return self.admin.add_audit_log_entry(username, action, details, status, ip_address)
    
    # Add more proxy methods as needed for backward compatibility
    def get_admin_users(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_admin_users()
    
    def get_admin_permissions(self, user_id):
        """Proxy method to maintain compatibility"""
        return self.admin.get_admin_permissions(user_id)
    
    def add_admin_user(self, user_data):
        """Proxy method to maintain compatibility"""
        return self.admin.add_admin_user(user_data)
    
    def update_admin_user(self, user_data):
        """Proxy method to maintain compatibility"""
        return self.admin.update_admin_user(user_data)
    
    def delete_admin_user(self, user_id):
        """Proxy method to maintain compatibility"""
        return self.admin.delete_admin_user(user_id)
    
    def reset_admin_password(self, user_id, new_password):
        """Proxy method to maintain compatibility"""
        return self.admin.reset_admin_password(user_id, new_password)
    
    def get_database_info(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_database_info()
    
    def get_database_tables(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_database_tables()
    
    def get_table_info(self, table_name):
        """Proxy method to maintain compatibility"""
        return self.admin.get_table_info(table_name)
    
    def get_table_data(self, table_name, limit=100, search=None, column=None):
        """Proxy method to maintain compatibility"""
        return self.admin.get_table_data(table_name, limit, search, column)
    
    def truncate_table(self, table_name):
        """Proxy method to maintain compatibility"""
        return self.admin.truncate_table(table_name)
    
    def optimize_database(self):
        """Proxy method to maintain compatibility"""
        return self.admin.optimize_database()
    
    def get_audit_logs(self, limit=100, start_date=None, end_date=None, username=None, action=None):
        """Proxy method to maintain compatibility"""
        return self.admin.get_audit_logs(limit, start_date, end_date, username, action)    
    def get_system_settings(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_system_settings()
    
    def update_system_setting(self, key, value, updated_by='System'):
        """Proxy method to maintain compatibility"""
        return self.admin.update_system_setting(key, value, updated_by)
    
    def backup_database(self, backup_path=None, include_attachments=True):
        """Proxy method to maintain compatibility"""
        return self.admin.backup_database(backup_path, include_attachments)
    
    def get_backup_history(self, limit=10):
        """Proxy method to maintain compatibility"""
        return self.admin.get_backup_history(limit)
    
    def restore_database_from_backup(self, backup_file, restore_attachments=True):
        """Proxy method to maintain compatibility"""
        return self.admin.restore_database_from_backup(backup_file, restore_attachments)
    
    def get_backup_schedule(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_backup_schedule()
    
    def update_backup_schedule(self, schedule_data):
        """Proxy method to maintain compatibility"""
        return self.admin.update_backup_schedule(schedule_data)
    
    def generate_api_key(self):
        """Proxy method to maintain compatibility"""
        return self.admin.generate_api_key()
    
    def get_last_backup_time(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_last_backup_time()
        
    def get_audit_log_users(self):
        """Proxy method to maintain compatibility"""
        return self.admin.get_audit_log_users()

    def add_user(self, data):
        try:
            connection = self.connect()
            if connection is None:
                return False

            cursor = connection.cursor()

            # Generate a default password hash if not provided
            password = data.get("password", "cmms2023")
            from django.contrib.auth.hashers import make_password
            hashed_password = make_password(password)

            query = """
                INSERT INTO users (
                    employee_id, password, role, access_level,
                    is_superuser, is_staff, is_active, 
                    date_joined, first_name, last_name, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Set default values for Django fields
            is_superuser = data.get("is_superuser", False)
            is_staff = data.get("is_staff", False)
            if data.get("role") == "admin":
                is_staff = True
            
            from datetime import datetime
            date_joined = data.get("date_joined", datetime.now())
            
            values = (
                data.get("employee_id"),
                hashed_password,
                data.get("role"),
                data.get("access_level", None),
                is_superuser,
                is_staff,
                data.get("is_active", True),
                date_joined,
                data.get("first_name", ""),
                data.get("last_name", ""),
                data.get("email", "")
            )

            cursor.execute(query, values)
            connection.commit()

            return True

        except Exception as e:
            self.console_logger.warning(f"Experienced error {e} when adding user to database")
            return False
        finally:
            self.close(connection)

    def add_inventory_personnel(self, data):
        """Add a new inventory personnel record"""
        try:
            connection = self.connect()
            if connection is None:
                return False
            
            user_table_data = {
                "employee_id": data.get("employee_id"),
                "role": "inventory",
                "access_level": data.get("access_level", "Standard"),
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "email": data.get("email", ""),
                "is_staff": True if data.get("access_level") == "Admin" else False,
                "is_superuser": False
            }
            self.add_user(user_table_data)

            cursor = connection.cursor()
            query = """
                INSERT INTO inventory_personnel (
                    employee_id, first_name, last_name, phone, 
                    email, role, access_level, hire_date, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get('employee_id'), data.get('first_name'), data.get('last_name'),
                data.get('phone'), data.get('email'), data.get('role'),
                data.get('access_level', 'Standard'), data.get('hire_date'), 
                data.get('status', 'Active')
            )
            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding inventory personnel: {e}")
            return False
        finally:
            self.close(connection)
    
    def get_inventory_personnel(self):
        """Get all inventory personnel"""
        try:
            connection = self.connect()
            if connection is None:
                return []
            
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM inventory_personnel ORDER BY last_name, first_name"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error getting inventory personnel: {e}")
            return []
        finally:
            self.close(connection)
    
    def get_personnel_by_id(self, personnel_id):
        """Get inventory personnel by ID"""
        try:
            connection = self.connect()
            if connection is None:
                return None
            
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM inventory_personnel WHERE personnel_id = %s"
            cursor.execute(query, (personnel_id,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting personnel by ID: {e}")
            return None
        finally:
            self.close(connection)
    
    def update_inventory_personnel(self, data):
        """Update inventory personnel information"""
        try:
            connection = self.connect()
            if connection is None:
                return False
            
            # First update the users table
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    access_level = %s,
                    is_staff = %s
                WHERE employee_id = %s
            """, (
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('email', ''),
                data.get('access_level', 'Standard'),
                True if data.get('access_level') == 'Admin' else False,
                data.get('employee_id')
            ))
            
            # Then update the inventory_personnel table
            query = """
                UPDATE inventory_personnel SET
                    first_name = %s,
                    last_name = %s,
                    phone = %s,
                    email = %s,
                    role = %s,
                    access_level = %s,
                    hire_date = %s,
                    status = %s
                WHERE employee_id = %s
            """
            values = (
                data.get('first_name'), 
                data.get('last_name'),
                data.get('phone'), 
                data.get('email'), 
                data.get('role'),
                data.get('access_level'), 
                data.get('hire_date'), 
                data.get('status'),
                data.get('employee_id')
            )
            cursor.execute(query, values)
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating inventory personnel: {e}")
            return False
        finally:
            self.close(connection)

    def create_purchase_order(self, data):
        """Create a new purchase order"""
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Generate PO number (e.g., PO-2024-0001)
            cursor.execute("SELECT COUNT(*) as count FROM purchase_orders WHERE YEAR(created_at) = YEAR(CURRENT_DATE)")
            count = cursor.fetchone()['count'] + 1
            po_number = f"PO-{datetime.now().year}-{count:04d}"
            
            # Insert purchase order
            query = """
                INSERT INTO purchase_orders (
                    po_number, supplier_id, status, total_amount,
                    created_by, expected_delivery, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                po_number, data['supplier_id'], 'Pending',
                data['total_amount'], data['created_by'],
                data['expected_delivery'], data.get('notes', '')
            )
            cursor.execute(query, values)
            po_id = cursor.lastrowid
            
            # Insert purchase order items
            for item in data['items']:
                query = """
                    INSERT INTO purchase_order_items (
                        po_id, item_id, quantity, unit_price
                    ) VALUES (%s, %s, %s, %s)
                """
                values = (po_id, item['item_id'], item['quantity'], item['unit_price'])
                cursor.execute(query, values)
            
            connection.commit()
            return po_id
        except Error as e:
            print(f"Error creating purchase order: {e}")
            connection.rollback()  # Add rollback on error
            return None
        finally:
            self.close(connection)

    def get_purchase_orders(self, status=None):
        """Get all purchase orders with optional status filter"""
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT po.*, s.name as supplier_name,
                    CONCAT(p.first_name, ' ', p.last_name) as created_by_name
                FROM purchase_orders po
                LEFT JOIN suppliers s ON po.supplier_id = s.supplier_id
                LEFT JOIN inventory_personnel p ON po.created_by = p.personnel_id
            """
            if status:
                query += " WHERE po.status = %s"
                cursor.execute(query, (status,))
            else:
                cursor.execute(query)
                
            return cursor.fetchall()
        finally:
            self.close(connection)

    def get_purchase_order_items(self, po_id):
        """Get items for a specific purchase order"""
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT poi.*, i.name as item_name, i.item_code
                FROM purchase_order_items poi
                JOIN inventory_items i ON poi.item_id = i.item_id
                WHERE poi.po_id = %s
            """
            cursor.execute(query, (po_id,))
            return cursor.fetchall()
        finally:
            self.close(connection)

    def update_purchase_order_status(self, po_id, status):
        """Update the status of a purchase order"""
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE purchase_orders SET status = %s WHERE po_id = %s",
                (status, po_id)
            )
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating purchase order status: {e}")
            return False
        finally:
            self.close(connection)

    def get_recent_inventory_activities(self, limit=10):
        """Get recent inventory transactions and activities"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                t.transaction_date as date,
                t.transaction_type as type,
                CONCAT(i.item_code, ' - ', i.name, ': ', t.quantity, ' ', i.unit) as description,
                CASE 
                    WHEN t.transaction_type = 'Incoming' THEN 'Added to Inventory'
                    WHEN t.transaction_type = 'Outgoing' THEN 'Removed from Inventory'
                    WHEN t.transaction_type = 'Adjustment' THEN 'Inventory Adjusted'
                    ELSE t.transaction_type
                END as status
            FROM inventory_transactions t
            JOIN inventory_items i ON t.item_id = i.item_id
            ORDER BY t.transaction_date DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            transactions = cursor.fetchall()
            
            # Also get recent purchase order activities
            po_query = """
            SELECT 
                p.created_at as date,
                'Purchase Order' as type,
                CONCAT('PO #', p.po_number, ' to ', s.name, ' (', p.status, ')') as description,
                p.status as status
            FROM purchase_orders p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.created_at DESC
            LIMIT %s
            """
            
            cursor.execute(po_query, (limit,))
            po_activities = cursor.fetchall()
            
            # Combine and sort by date
            activities = transactions + po_activities
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            # Limit to the requested number
            return activities[:limit]
            
        except Exception as e:
            print(f"Error getting recent inventory activities: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def get_inventory_personnel_notifications(self, personnel_id, limit=20):
        """Get notifications for an inventory personnel"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Check if the notifications table exists, create it if not
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    personnel_id INT,
                    message TEXT NOT NULL,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    priority VARCHAR(20) DEFAULT 'medium',
                    read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (personnel_id) REFERENCES inventory_personnel(personnel_id)
                )
            """)
            connection.commit()
            
            # Get notifications for this personnel
            query = """
            SELECT * FROM inventory_notifications
            WHERE personnel_id = %s OR personnel_id IS NULL
            ORDER BY date DESC
            LIMIT %s
            """
            
            cursor.execute(query, (personnel_id, limit))
            notifications = cursor.fetchall()
            
            # If we have less than 5 notifications, generate some system ones for demo purposes
            if len(notifications) < 5:
                # Get low stock items
                cursor.execute("""
                    SELECT item_id, name, quantity, minimum_quantity
                    FROM inventory_items
                    WHERE quantity <= minimum_quantity
                    LIMIT 10
                """)
                low_stock_items = cursor.fetchall()
                
                # Add notifications for low stock items
                for item in low_stock_items:
                    priority = "high" if item['quantity'] <= 0 else "medium"
                    message = f"{item['name']} is {'out of stock' if item['quantity'] <= 0 else 'running low'} (Qty: {item['quantity']})"
                    
                    cursor.execute("""
                        INSERT INTO inventory_notifications
                        (personnel_id, message, priority, date)
                        VALUES (%s, %s, %s, DATE_SUB(NOW(), INTERVAL RAND()*10 DAY))
                    """, (personnel_id, message, priority))
                
                # Add pending purchase order notifications
                cursor.execute("""
                    SELECT po_number, supplier_id, expected_delivery
                    FROM purchase_orders
                    WHERE status = 'Pending'
                    LIMIT 5
                """)
                pending_pos = cursor.fetchall()
                
                for po in pending_pos:
                    # Get supplier name
                    cursor.execute("SELECT name FROM suppliers WHERE supplier_id = %s", (po['supplier_id'],))
                    supplier = cursor.fetchone()
                    
                    message = f"Purchase order #{po['po_number']} to {supplier['name']} is pending approval"
                    cursor.execute("""
                        INSERT INTO inventory_notifications
                        (personnel_id, message, priority, date)
                        VALUES (%s, %s, 'medium', DATE_SUB(NOW(), INTERVAL RAND()*5 DAY))
                    """, (personnel_id, message))
                
                connection.commit()
                
                # Get the notifications again after adding demo ones
                cursor.execute(query, (personnel_id, limit))
                notifications = cursor.fetchall()
            
            return notifications
            
        except Exception as e:
            print(f"Error getting inventory personnel notifications: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def mark_personnel_notifications_read(self, personnel_id):
        """Mark all notifications as read for a personnel"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            query = """
            UPDATE inventory_notifications
            SET read = TRUE
            WHERE personnel_id = %s AND read = FALSE
            """
            
            cursor.execute(query, (personnel_id,))
            connection.commit()
            
            return True
            
        except Exception as e:
            print(f"Error marking notifications as read: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def get_personnel_by_employee_id(self, employee_id):
        """Get inventory personnel by employee ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM inventory_personnel
            WHERE employee_id = %s
            """
            
            cursor.execute(query, (employee_id,))
            return cursor.fetchone()
            
        except Exception as e:
            print(f"Error getting personnel by employee ID: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def update_inventory_item(self, data):
        """Update an existing inventory item"""
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
            
            # Update item
            cursor.execute("""
                UPDATE inventory_items SET
                    category_id = %s,
                    supplier_id = %s,
                    name = %s,
                    description = %s,
                    unit = %s,
                    unit_cost = %s,
                    quantity = %s,
                    minimum_quantity = %s,
                    reorder_point = %s,
                    location = %s
                WHERE item_id = %s
            """, (
                category_id,
                data.get('supplier_id'),
                data['name'],
                data.get('description'),
                data.get('unit'),
                data.get('unit_cost', 0.00),
                data.get('quantity', 0),
                data.get('minimum_quantity', 0),
                data.get('reorder_point', 0),
                data.get('location'),
                data['item_id']
            ))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating inventory item: {e}")
            return False
        finally:
            self.close(connection)

    def remove_inventory_item(self, item_id):
        """Remove an inventory item"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Check if item is referenced in other tables
            cursor.execute("""
                SELECT COUNT(*) FROM inventory_transactions
                WHERE item_id = %s
            """, (item_id,))
            transaction_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM tool_checkouts
                WHERE item_id = %s
            """, (item_id,))
            checkout_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM purchase_order_items
                WHERE item_id = %s
            """, (item_id,))
            po_count = cursor.fetchone()[0]
            
            # If item is referenced, mark as inactive instead of deleting
            if transaction_count > 0 or checkout_count > 0 or po_count > 0:
                cursor.execute("""
                    UPDATE inventory_items
                    SET status = 'Inactive'
                    WHERE item_id = %s
                """, (item_id,))
            else:
                # If not referenced, delete the item
                cursor.execute("""
                    DELETE FROM inventory_items
                    WHERE item_id = %s
                """, (item_id,))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error removing inventory item: {e}")
            return False
        finally:
            self.close(connection)

    def update_craftsman_training(self, data):
        """Update an existing training record for a craftsman"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE craftsmen_training SET
                    training_name = %s,
                    training_date = %s,
                    completion_date = %s,
                    training_provider = %s,
                    certification_received = %s,
                    training_status = %s
                WHERE training_id = %s AND craftsman_id = %s
            """, (
                data['training_name'],
                data['training_date'],
                data['completion_date'],
                data['training_provider'],
                data['certification_received'],
                data['training_status'],
                data['training_id'],
                data['craftsman_id']
            ))
            
            connection.commit()
            return cursor.rowcount > 0  # Return True if any rows were updated
        except Error as e:
            print(f"Error updating craftsman training: {e}")
            return False
        finally:
            self.close(connection)

    def get_inventory_item_by_name(self, item_name):
        """Get inventory item details by name"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM inventory_items
                WHERE name LIKE %s
                LIMIT 1
            """, (f"%{item_name}%",))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting inventory item by name: {e}")
            return None
        finally:
            self.close(connection)

    def get_inventory_personnel_for_po(self):
        """Get inventory personnel who can receive purchase orders"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM inventory_personnel 
            WHERE status = 'Active' 
            AND (role = 'Purchasing' OR role = 'Inventory Manager' OR role = 'Supervisor')
            """
            
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting inventory personnel for PO: {e}")
            return []
        finally:
            self.close(connection)

    def auto_create_purchase_order(self, low_stock_items):
        """Automatically create a purchase order for low stock items"""
        if not low_stock_items:
            return None
        
        try:
            # Group items by supplier
            items_by_supplier = {}
            for item in low_stock_items:
                supplier_id = item.get('supplier_id')
                if supplier_id:
                    if supplier_id not in items_by_supplier:
                        items_by_supplier[supplier_id] = []
                    items_by_supplier[supplier_id].append(item)
            
            # Get purchasing personnel
            personnel = self.get_inventory_personnel_for_po()
            if not personnel:
                print("No inventory personnel available to receive purchase orders")
                return None
            
            # Use the first available personnel
            created_by = personnel[0]['personnel_id']
            
            # Create POs for each supplier
            created_pos = []
            for supplier_id, items in items_by_supplier.items():
                # Calculate quantities to order
                po_items = []
                total_amount = 0
                
                for item in items:
                    # Calculate how many to order
                    current_qty = item.get('quantity', 0)
                    reorder_point = item.get('reorder_point', 0)
                    min_qty = item.get('minimum_quantity', 0)
                    
                    # Order enough to get back above minimum quantity
                    order_qty = max(min_qty - current_qty, 0)
                    
                    # Add a buffer (e.g., 20% more)
                    order_qty = int(order_qty * 1.2) + 1
                    
                    # Ensure we order at least 1
                    if current_qty <= reorder_point and order_qty < 1:
                        order_qty = 1
                    
                    unit_price = item.get('unit_cost', 0)
                    
                    po_items.append({
                        'item_id': item['item_id'],
                        'quantity': order_qty,
                        'unit_price': unit_price
                    })
                    
                    total_amount += order_qty * unit_price
                
                # Create the PO
                expected_delivery = datetime.now() + timedelta(days=7)  # Default to 7 days from now
                
                po_data = {
                    'supplier_id': supplier_id,
                    'total_amount': total_amount,
                    'created_by': created_by,
                    'expected_delivery': expected_delivery,
                    'notes': 'Automatically generated for low stock items',
                    'items': po_items
                }
                
                po_id = self.create_purchase_order(po_data)
                if po_id:
                    created_pos.append(po_id)
            
            return created_pos
        except Exception as e:
            print(f"Error auto-creating purchase order: {e}")
            return None

    def delete_craftsman(self, craftsman_id):
        """Delete a craftsman and all associated data"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Begin transaction
            connection.start_transaction()
            
            # First, check if this is an employee_id or craftsman_id
            if not str(craftsman_id).isdigit():
                cursor.execute("""
                    SELECT craftsman_id FROM craftsmen 
                    WHERE employee_id = %s
                """, (craftsman_id,))
                
                result = cursor.fetchone()
                if result:
                    craftsman_id = result[0]
                else:
                    return False
            
            # Delete craftsman from all tables
            # Note: Most tables have ON DELETE CASCADE, but we'll be explicit for clarity
            
            # 1. Remove from team_members
            cursor.execute("DELETE FROM team_members WHERE craftsman_id = %s", (craftsman_id,))
            
            # 2. Update teams where this craftsman is leader
            cursor.execute("""
                UPDATE craftsmen_teams 
                SET team_leader_id = NULL 
                WHERE team_leader_id = %s
            """, (craftsman_id,))
            
            # 3. Delete craftsman's schedule
            cursor.execute("DELETE FROM craftsmen_schedule WHERE craftsman_id = %s", (craftsman_id,))
            
            # 4. Delete craftsman's training records
            cursor.execute("DELETE FROM craftsmen_training WHERE craftsman_id = %s", (craftsman_id,))
            
            # 5. Delete craftsman's work history
            cursor.execute("DELETE FROM craftsmen_work_history WHERE craftsman_id = %s", (craftsman_id,))
            
            # 6. Delete craftsman's skills
            cursor.execute("DELETE FROM craftsmen_skills WHERE craftsman_id = %s", (craftsman_id,))
            
            # 7. Handle work order templates
            cursor.execute("""
                UPDATE work_order_templates
                SET craftsman_id = NULL
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            # 8. Handle work orders
            cursor.execute("""
                UPDATE work_orders
                SET craftsman_id = NULL, assignment_type = 'Unassigned'
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            # 9. Handle maintenance reports
            cursor.execute("""
                UPDATE maintenance_reports
                SET craftsman_id = NULL
                WHERE craftsman_id = %s
            """, (craftsman_id,))
            
            # 10. Finally, delete the craftsman record
            cursor.execute("DELETE FROM craftsmen WHERE craftsman_id = %s", (craftsman_id,))
            
            # Commit transaction
            connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting craftsman: {e}")
            if 'connection' in locals() and connection:
                connection.rollback()
            return False
        finally:
            if 'connection' in locals() and connection:
                self.close(connection)

    def delete_team(self, team_id):
        """Delete a team and all associated data"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Begin transaction
            connection.start_transaction()
            
            # 1. Update work orders assigned to this team
            cursor.execute("""
                UPDATE work_orders
                SET team_id = NULL, assignment_type = 'Unassigned'
                WHERE team_id = %s AND status != 'Completed'
            """, (team_id,))
            
            # 2. Delete team members
            cursor.execute("DELETE FROM team_members WHERE team_id = %s", (team_id,))
            
            # 3. Delete team schedule
            cursor.execute("DELETE FROM team_schedules WHERE team_id = %s", (team_id,))
            
            # 4. Delete team from work order templates
            cursor.execute("""
                UPDATE work_order_templates
                SET team_id = NULL
                WHERE team_id = %s
            """, (team_id,))
            
            # 5. Finally, delete the team record
            cursor.execute("DELETE FROM craftsmen_teams WHERE team_id = %s", (team_id,))
            
            # Commit transaction
            connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting team: {e}")
            if 'connection' in locals() and connection:
                connection.rollback()
            return False
        finally:
            if 'connection' in locals() and connection:
                self.close(connection)

