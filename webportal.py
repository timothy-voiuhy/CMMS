"""
Web-based Craftsman Portal - Allows craftsmen to access their portal through a web browser
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import Error

def nl2br(value):
    """
    Convert newlines to <br> tags
    """
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.jinja_env.filters['nl2br'] = nl2br

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'CMMS',
    'password': 'cmms',
    'database': 'cmms_db',
    'charset':"utf8mb4",
    'collation':"utf8mb4_general_ci"
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, employee_id, first_name, last_name, email, role):
        self.id = id
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role

# Database connection helper
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM craftsmen WHERE craftsman_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user_data:
        return None
    
    return User(
        id=user_data['craftsman_id'],
        employee_id=user_data['employee_id'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        role='craftsman'
    )

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        
        # DEVELOPMENT BYPASS: Allow login with "dev" as employee ID
        if employee_id and employee_id.lower() == "dev":
            # Create a development user
            dev_user = User(
                id=1,  # Use ID 1 for development
                employee_id="DEV001",
                first_name="Development",
                last_name="User",
                email="dev@example.com",
                role='craftsman'
            )
            login_user(dev_user)
            flash('Logged in with development bypass', 'success')
            return redirect(url_for('dashboard'))
        
        # Normal login process
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return render_template('login.html')
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM craftsmen WHERE employee_id = %s", (employee_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # For development, accept any password
        # In production, use: if user_data and check_password_hash(user_data['password_hash'], password):
        if user_data:
            user = User(
                id=user_data['craftsman_id'],
                employee_id=user_data['employee_id'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                role='craftsman'
            )
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid employee ID or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get craftsman data
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('dashboard.html', counts={'total': 0, 'open_count': 0, 'in_progress_count': 0, 'completed_count': 0}, recent_work_orders=[], pending_reports=0)
    
    cursor = conn.cursor(dictionary=True)
    
    # Get work order counts
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_count,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_count
            FROM work_orders
            WHERE craftsman_id = %s
        """, (current_user.id,))
        
        counts = cursor.fetchone()
    except Error as e:
        print(f"Error getting work order counts: {e}")
        counts = {'total': 0, 'open_count': 0, 'in_progress_count': 0, 'completed_count': 0}
    
    # Get recent work orders
    try:
        cursor.execute("""
            SELECT wo.*, e.equipment_name
            FROM work_orders wo
            LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
            WHERE wo.craftsman_id = %s
            ORDER BY wo.due_date ASC, wo.priority DESC
            LIMIT 5
        """, (current_user.id,))
        
        recent_work_orders = cursor.fetchall()
    except Error as e:
        print(f"Error getting recent work orders: {e}")
        recent_work_orders = []
    
    # Get pending reports count - handle case where maintenance_reports table doesn't exist
    try:
        # First check if maintenance_reports table exists
        cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT COUNT(*) as pending_reports
                FROM work_orders wo
                LEFT JOIN maintenance_reports mr ON wo.work_order_id = mr.work_order_id
                WHERE wo.craftsman_id = %s
                AND wo.status IN ('Completed', 'In Progress')
                AND mr.report_id IS NULL
            """, (current_user.id,))
            
            pending_reports = cursor.fetchone()['pending_reports']
        else:
            # If table doesn't exist, count all completed/in progress work orders as needing reports
            cursor.execute("""
                SELECT COUNT(*) as pending_reports
                FROM work_orders
                WHERE craftsman_id = %s
                AND status IN ('Completed', 'In Progress')
            """, (current_user.id,))
            
            pending_reports = cursor.fetchone()['pending_reports']
    except Error as e:
        print(f"Error getting pending reports count: {e}")
        pending_reports = 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        'dashboard.html',
        user=current_user,
        counts=counts,
        recent_work_orders=recent_work_orders,
        pending_reports=pending_reports
    )

@app.route('/work_orders')
@login_required
def work_orders():
    status_filter = request.args.get('status', '')
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('work_orders.html')
    
    cursor = conn.cursor(dictionary=True)
    
    # Build query with optional status filter
    query = """
        SELECT wo.*, e.equipment_name
        FROM work_orders wo
        LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
        WHERE wo.craftsman_id = %s
    """
    
    params = [current_user.id]
    
    if status_filter:
        query += " AND wo.status = %s"
        params.append(status_filter)
    
    query += " ORDER BY wo.due_date ASC, wo.priority DESC"
    
    cursor.execute(query, tuple(params))
    work_orders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'work_orders.html',
        work_orders=work_orders,
        status_filter=status_filter
    )

@app.route('/view_work_order/<int:work_order_id>')
@login_required
def view_work_order(work_order_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('work_orders'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get work order details
    cursor.execute("""
        SELECT wo.*, e.equipment_name, e.location
        FROM work_orders wo
        LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
        WHERE wo.work_order_id = %s AND wo.craftsman_id = %s
    """, (work_order_id, current_user.id))
    
    work_order = cursor.fetchone()
    
    if not work_order:
        flash('Work order not found or you do not have permission to view it', 'error')
        return redirect(url_for('work_orders'))
    
    # Check if this work order has a maintenance report
    has_report = False
    report_id = None
    
    try:
        # First check if maintenance_reports table exists
        cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT report_id FROM maintenance_reports
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            report = cursor.fetchone()
            if report:
                has_report = True
                report_id = report['report_id']
    except Error as e:
        print(f"Error checking for maintenance report: {e}")
    
    cursor.close()
    conn.close()
    
    return render_template(
        'view_work_order.html',
        work_order=work_order,
        has_report=has_report,
        report_id=report_id
    )

@app.route('/update_work_order_status/<int:work_order_id>', methods=['GET', 'POST'])
@login_required
def update_work_order_status(work_order_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('work_orders'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get work order details
    cursor.execute("""
        SELECT wo.*, e.equipment_name
        FROM work_orders wo
        LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
        WHERE wo.work_order_id = %s AND wo.craftsman_id = %s
    """, (work_order_id, current_user.id))
    
    work_order = cursor.fetchone()
    
    if not work_order:
        flash('Work order not found or you do not have permission to update it', 'error')
        return redirect(url_for('work_orders'))
    
    if request.method == 'POST':
        status = request.form.get('status')
        notes = request.form.get('notes')
        completed_date = request.form.get('completed_date')
        
        # Validate status
        valid_statuses = ['Open', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
        if status not in valid_statuses:
            flash('Invalid status', 'error')
            return render_template('update_work_order_status.html', work_order=work_order, today=datetime.now().strftime('%Y-%m-%d'))
        
        # Update work order
        update_data = {
            'work_order_id': work_order_id,
            'status': status,
            'notes': notes
        }
        
        if status == 'Completed' and completed_date:
            update_data['completed_date'] = completed_date
        
        success = True
        try:
            # Build query dynamically based on provided fields
            query = "UPDATE work_orders SET "
            params = []
            
            if 'status' in update_data:
                query += "status = %s, "
                params.append(update_data['status'])
            
            if 'completed_date' in update_data:
                query += "completed_date = %s, "
                params.append(update_data['completed_date'])
            
            if 'notes' in update_data:
                query += "notes = %s, "
                params.append(update_data['notes'])
            
            # Remove trailing comma and space
            query = query.rstrip(', ')
            
            # Add WHERE clause
            query += " WHERE work_order_id = %s"
            params.append(update_data['work_order_id'])
            
            cursor.execute(query, tuple(params))
            conn.commit()
        except Error as e:
            print(f"Error updating work order status: {e}")
            success = False
        
        cursor.close()
        conn.close()
        
        if success:
            flash('Work order status updated successfully', 'success')
            return redirect(url_for('view_work_order', work_order_id=work_order_id))
        else:
            flash('Error updating work order status', 'error')
            return render_template('update_work_order_status.html', work_order=work_order, today=datetime.now().strftime('%Y-%m-%d'))
    
    cursor.close()
    conn.close()
    
    return render_template(
        'update_work_order_status.html',
        work_order=work_order,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@app.route('/add_report/<int:work_order_id>', methods=['GET', 'POST'])
@login_required
def add_report(work_order_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('work_orders'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get work order details - using equipment_registry instead of equipment
    cursor.execute("""
        SELECT wo.*, er.equipment_name
        FROM work_orders wo
        JOIN equipment_registry er ON wo.equipment_id = er.equipment_id
        WHERE wo.work_order_id = %s
    """, (work_order_id,))
    
    work_order = cursor.fetchone()
    
    if not work_order:
        flash('Work order not found', 'error')
        return redirect(url_for('work_orders'))
    
    # Get equipment type - using equipment_registry instead of equipment
    # Assuming equipment_registry has a field that indicates type
    cursor.execute("""
        SELECT template_id as equipment_type
        FROM equipment_registry
        WHERE equipment_id = %s
    """, (work_order['equipment_id'],))
    
    equipment_type_result = cursor.fetchone()
    equipment_type = equipment_type_result['equipment_type'] if equipment_type_result else 'unknown'
    
    # Check if this work order already has a maintenance report
    try:
        # First check if maintenance_reports table exists
        cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT report_id FROM maintenance_reports
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            report = cursor.fetchone()
            if report:
                flash('This work order already has a maintenance report', 'error')
                return redirect(url_for('view_work_order', work_order_id=work_order_id))
    except Error as e:
        print(f"Error checking for maintenance report: {e}")
    
    if request.method == 'POST':
        # Process form data
        maintenance_type = request.form.get('maintenance_type')
        initial_condition = request.form.get('initial_condition')
        final_condition = request.form.get('final_condition')
        
        # Build report data
        report_data = {
            'general': {
                'maintenance_type': maintenance_type,
                'initial_condition': initial_condition,
                'final_condition': final_condition
            },
            'inspection': {
                'visual_external_damage': 'visual_external_damage' in request.form,
                'visual_corrosion': 'visual_corrosion' in request.form,
                'visual_leaks': 'visual_leaks' in request.form,
                'visual_wear': 'visual_wear' in request.form,
                'operational_unusual_noise': 'operational_unusual_noise' in request.form,
                'operational_vibration': 'operational_vibration' in request.form,
                'operational_overheating': 'operational_overheating' in request.form,
                'operational_performance': 'operational_performance' in request.form,
                'additional_findings': request.form.get('additional_findings', '')
            }
        }
        
        # Equipment specific data
        equipment_type = work_order.get('equipment_type', '').lower()
        if equipment_type == 'mechanical':
            report_data['mechanical'] = collect_mechanical_data(request.form)
        elif equipment_type == 'electrical':
            report_data['electrical'] = collect_electrical_data(request.form)
        elif equipment_type == 'hvac':
            report_data['hvac'] = collect_hvac_data(request.form)
        elif equipment_type == 'plumbing':
            report_data['plumbing'] = collect_plumbing_data(request.form)
        
        # Measurements data
        report_data['measurements'] = collect_measurements_data(request.form)
        
        # Parts data
        report_data['parts'] = collect_parts_data(request.form)
        
        # Create maintenance report
        try:
            # First check if maintenance_reports table exists
            cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
            table_exists = cursor.fetchone()
            
            # Create table if it doesn't exist
            if not table_exists:
                connection = get_db_connection()
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
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                connection.commit()
            
            # Insert report
            query = """
                INSERT INTO maintenance_reports (
                    work_order_id, equipment_id, craftsman_id, 
                    report_date, report_data, comments
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                work_order_id, 
                work_order['equipment_id'], 
                current_user.id,
                datetime.now(), 
                json.dumps(report_data), 
                request.form.get('comments', '')
            ))
            
            conn.commit()
            report_id = cursor.lastrowid
            
            # Update work order status to completed if not already
            if work_order['status'] != 'Completed':
                cursor.execute("""
                    UPDATE work_orders
                    SET status = 'Completed', completed_date = %s
                    WHERE work_order_id = %s
                """, (datetime.now().date(), work_order_id))
                conn.commit()
            
            # Handle file uploads
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        
                        # Create attachments table if it doesn't exist
                        cursor.execute("SHOW TABLES LIKE 'report_attachments'")
                        table_exists = cursor.fetchone()
                        
                        if not table_exists:
                            cursor.execute("""
                                CREATE TABLE report_attachments (
                                    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
                                    report_id INT NOT NULL,
                                    filename VARCHAR(255) NOT NULL,
                                    file_path VARCHAR(255) NOT NULL,
                                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (report_id) REFERENCES maintenance_reports(report_id)
                                )
                            """)
                            conn.commit()
                        
                        # Insert attachment record
                        cursor.execute("""
                            INSERT INTO report_attachments (report_id, filename, file_path)
                            VALUES (%s, %s, %s)
                        """, (report_id, filename, file_path))
                        conn.commit()
            
            flash('Maintenance report created successfully', 'success')
            return redirect(url_for('view_report', report_id=report_id))
            
        except Error as e:
            print(f"Error creating maintenance report: {e}")
            flash('Error creating maintenance report', 'error')
    
    cursor.close()
    conn.close()
    
    return render_template(
        'add_report.html',
        work_order=work_order,
        equipment_type=equipment_type,
        today=datetime.now().strftime('%Y-%m-%d'),
        now=datetime.now().strftime('%H:%M'),
        current_user=current_user
    )

@app.route('/view_report/<int:report_id>')
@login_required
def view_report(report_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('maintenance_history'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get report details
    try:
        cursor.execute("""
            SELECT mr.*, wo.title, wo.work_order_id, e.equipment_name
            FROM maintenance_reports mr
            JOIN work_orders wo ON mr.work_order_id = wo.work_order_id
            JOIN equipment_registry e ON mr.equipment_id = e.equipment_id
            WHERE mr.report_id = %s AND mr.craftsman_id = %s
        """, (report_id, current_user.id))
        
        report = cursor.fetchone()
        
        if not report:
            flash('Report not found or you do not have permission to view it', 'error')
            return redirect(url_for('maintenance_history'))
        
        # Parse JSON data
        report_data = json.loads(report['report_data'])
        
        # Get attachments
        cursor.execute("SHOW TABLES LIKE 'report_attachments'")
        table_exists = cursor.fetchone()
        
        attachments = []
        if table_exists:
            cursor.execute("""
                SELECT * FROM report_attachments
                WHERE report_id = %s
            """, (report_id,))
            
            attachments = cursor.fetchall()
    
    except Error as e:
        print(f"Error retrieving report: {e}")
        flash('Error retrieving report', 'error')
        return redirect(url_for('maintenance_history'))
    
    cursor.close()
    conn.close()
    
    return render_template(
        'view_report.html',
        report=report,
        report_data=report_data,
        attachments=attachments
    )

@app.route('/download_attachment/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('maintenance_history'))
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get attachment details
        cursor.execute("""
            SELECT a.*, mr.craftsman_id
            FROM report_attachments a
            JOIN maintenance_reports mr ON a.report_id = mr.report_id
            WHERE a.attachment_id = %s
        """, (attachment_id,))
        
        attachment = cursor.fetchone()
        
        if not attachment or attachment['craftsman_id'] != current_user.id:
            flash('Attachment not found or you do not have permission to download it', 'error')
            return redirect(url_for('maintenance_history'))
        
        cursor.close()
        conn.close()
        
        # Return file for download
        return send_file(attachment['file_path'], as_attachment=True, download_name=attachment['filename'])
    
    except Error as e:
        print(f"Error downloading attachment: {e}")
        flash('Error downloading attachment', 'error')
        return redirect(url_for('maintenance_history'))

@app.route('/print_report/<int:report_id>')
@login_required
def print_report(report_id):
    # Similar to view_report but with a print-friendly template
    return redirect(url_for('view_report', report_id=report_id))

# Helper functions for report data collection
def determine_equipment_type(work_order):
    """Determine equipment type based on equipment data"""
    # Check if we have a specialization field
    if 'specialization' in work_order:
        return work_order['specialization'].lower()
    
    # Try to determine from equipment name or model
    equipment_name = work_order['equipment_name'].lower()
    model = work_order.get('model', '').lower()
    
    # Check for keywords in name or model
    mechanical_keywords = ['pump', 'motor', 'engine', 'compressor', 'gear', 'valve', 'bearing']
    electrical_keywords = ['electrical', 'circuit', 'breaker', 'transformer', 'generator', 'panel', 'switch']
    hvac_keywords = ['hvac', 'air conditioner', 'heater', 'furnace', 'boiler', 'chiller', 'ventilation']
    plumbing_keywords = ['plumbing', 'pipe', 'drain', 'water', 'sewage', 'toilet', 'faucet']
    
    for keyword in mechanical_keywords:
        if keyword in equipment_name or keyword in model:
            return "mechanical"
    
    for keyword in electrical_keywords:
        if keyword in equipment_name or keyword in model:
            return "electrical"
    
    for keyword in hvac_keywords:
        if keyword in equipment_name or keyword in model:
            return "hvac"
    
    for keyword in plumbing_keywords:
        if keyword in equipment_name or keyword in model:
            return "plumbing"
    
    # Default to mechanical if we can't determine
    return "mechanical"

def collect_mechanical_data(form):
    """Collect mechanical-specific form data"""
    return {
        'lubrication_performed': 'lubrication_performed' in form,
        'lubrication_type': form.get('lubrication_type', ''),
        'alignment_checked': 'alignment_checked' in form,
        'alignment_adjusted': 'alignment_adjusted' in form,
        'bearings_inspected': 'bearings_inspected' in form,
        'bearings_condition': form.get('bearings_condition', ''),
        'belt_tension_checked': 'belt_tension_checked' in form,
        'belt_condition': form.get('belt_condition', ''),
        'coupling_inspected': 'coupling_inspected' in form,
        'coupling_condition': form.get('coupling_condition', ''),
        'mechanical_notes': form.get('mechanical_notes', '')
    }

def collect_electrical_data(form):
    """Collect electrical-specific form data"""
    return {
        'voltage_measured': 'voltage_measured' in form,
        'voltage_reading': form.get('voltage_reading', ''),
        'current_measured': 'current_measured' in form,
        'current_reading': form.get('current_reading', ''),
        'resistance_measured': 'resistance_measured' in form,
        'resistance_reading': form.get('resistance_reading', ''),
        'connections_tightened': 'connections_tightened' in form,
        'insulation_tested': 'insulation_tested' in form,
        'insulation_condition': form.get('insulation_condition', ''),
        'grounding_checked': 'grounding_checked' in form,
        'electrical_notes': form.get('electrical_notes', '')
    }

def collect_hvac_data(form):
    """Collect HVAC-specific form data"""
    return {
        'filters_replaced': 'filters_replaced' in form,
        'coils_cleaned': 'coils_cleaned' in form,
        'refrigerant_level_checked': 'refrigerant_level_checked' in form,
        'refrigerant_added': 'refrigerant_added' in form,
        'refrigerant_amount': form.get('refrigerant_amount', ''),
        'ductwork_inspected': 'ductwork_inspected' in form,
        'ductwork_condition': form.get('ductwork_condition', ''),
        'thermostat_calibrated': 'thermostat_calibrated' in form,
        'supply_temp': form.get('supply_temp', ''),
        'return_temp': form.get('return_temp', ''),
        'hvac_notes': form.get('hvac_notes', '')
    }

def collect_plumbing_data(form):
    """Collect plumbing-specific form data"""
    return {
        'water_pressure_checked': 'water_pressure_checked' in form,
        'water_pressure': form.get('water_pressure', ''),
        'leak_test_performed': 'leak_test_performed' in form,
        'leak_test_result': form.get('leak_test_result', ''),
        'drain_flow_checked': 'drain_flow_checked' in form,
        'drain_condition': form.get('drain_condition', ''),
        'valves_exercised': 'valves_exercised' in form,
        'valve_condition': form.get('valve_condition', ''),
        'seals_replaced': 'seals_replaced' in form,
        'plumbing_notes': form.get('plumbing_notes', '')
    }

def collect_measurements_data(form):
    """Collect measurements form data"""
    measurements = {
        'vibration_measured': 'vibration_measured' in form,
        'temperature_measured': 'temperature_measured' in form,
        'noise_measured': 'noise_measured' in form
    }
    
    if 'vibration_measured' in form:
        measurements['vibration_level'] = form.get('vibration_level', '')
        measurements['vibration_location'] = form.get('vibration_location', '')
    
    if 'temperature_measured' in form:
        for i in range(1, 4):  # Up to 3 temperature readings
            location_key = f'temp_location_{i}'
            temp_key = f'temperature_{i}'
            if form.get(location_key) and form.get(temp_key):
                measurements[location_key] = form.get(location_key)
                measurements[temp_key] = form.get(temp_key)
    
    if 'noise_measured' in form:
        measurements['noise_level'] = form.get('noise_level', '')
        measurements['noise_description'] = form.get('noise_description', '')
    
    # Custom measurements
    for i in range(1, 4):  # Up to 3 custom measurements
        name_key = f'custom_name_{i}'
        value_key = f'custom_value_{i}'
        unit_key = f'custom_unit_{i}'
        if form.get(name_key) and form.get(value_key):
            measurements[name_key] = form.get(name_key)
            measurements[value_key] = form.get(value_key)
            measurements[unit_key] = form.get(unit_key, '')
    
    return measurements

def collect_parts_data(form):
    """Collect parts used form data"""
    parts = []
    
    # Process parts data
    part_count = int(form.get('part_count', 0))
    for i in range(1, part_count + 1):
        part_name = form.get(f'part_name_{i}')
        part_number = form.get(f'part_number_{i}')
        quantity = form.get(f'quantity_{i}')
        
        if part_name and quantity:
            parts.append({
                'name': part_name,
                'part_number': part_number,
                'quantity': quantity
            })
    
    return parts

# API routes for mobile app integration
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    employee_id = data.get('employee_id')
    password = data.get('password')
    
    # DEVELOPMENT BYPASS: Allow login with "dev" as employee ID
    if employee_id and employee_id.lower() == "dev":
        return jsonify({
            'success': True,
            'user': {
                'id': 1,
                'employee_id': "DEV001",
                'name': "Development User",
                'email': "dev@example.com"
            }
        })
    
    # Normal login process
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM craftsmen WHERE employee_id = %s", (employee_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # For development, accept any password
    if user_data:
        return jsonify({
            'success': True,
            'user': {
                'id': user_data['craftsman_id'],
                'employee_id': user_data['employee_id'],
                'name': f"{user_data['first_name']} {user_data['last_name']}",
                'email': user_data['email']
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid employee ID or password'})

@app.route('/api/work_orders/<int:craftsman_id>', methods=['GET'])
def api_work_orders(craftsman_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT wo.*, e.equipment_name
        FROM work_orders wo
        LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
        WHERE wo.craftsman_id = %s
        ORDER BY wo.due_date ASC, wo.priority DESC
    """, (craftsman_id,))
    
    work_orders = cursor.fetchall()
    
    # Convert datetime objects to string for JSON serialization
    for wo in work_orders:
        if wo.get('created_date'):
            wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
        if wo.get('due_date'):
            wo['due_date'] = wo['due_date'].strftime('%Y-%m-%d')
        if wo.get('completed_date'):
            wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
    
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'work_orders': work_orders})

@app.route('/maintenance_history')
@login_required
def maintenance_history():
    # Get date range from query parameters
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('maintenance_history.html', history=[], from_date=from_date, to_date=to_date)
    
    cursor = conn.cursor(dictionary=True)
    
    # Get maintenance history
    history = []
    try:
        # First check if maintenance_reports table exists
        cursor.execute("SHOW TABLES LIKE 'maintenance_reports'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT mr.report_id, mr.report_date as date, wo.work_order_id, 
                       e.equipment_name, mr.report_data, wo.title as description
                FROM maintenance_reports mr
                JOIN work_orders wo ON mr.work_order_id = wo.work_order_id
                JOIN equipment_registry e ON mr.equipment_id = e.equipment_id
                WHERE mr.craftsman_id = %s
                AND DATE(mr.report_date) BETWEEN %s AND %s
                ORDER BY mr.report_date DESC
            """, (current_user.id, from_date, to_date))
            
            raw_history = cursor.fetchall()
            
            # Process the history data
            for entry in raw_history:
                report_data = json.loads(entry['report_data'])
                maintenance_type = report_data.get('general', {}).get('maintenance_type', 'Preventive')
                
                history.append({
                    'report_id': entry['report_id'],
                    'date': entry['date'].strftime('%Y-%m-%d'),
                    'work_order_id': entry['work_order_id'],
                    'equipment_name': entry['equipment_name'],
                    'maintenance_type': maintenance_type,
                    'description': entry['description']
                })
    except Error as e:
        print(f"Error retrieving maintenance history: {e}")
    
    cursor.close()
    conn.close()
    
    return render_template(
        'maintenance_history.html',
        history=history,
        from_date=from_date,
        to_date=to_date
    )

@app.route('/skills')
@login_required
def skills():
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('skills.html', skills=[], training=[], today=datetime.now().date())
    
    cursor = conn.cursor(dictionary=True)
    
    # Get craftsman skills
    skills = []
    training = []
    
    try:
        # Check if craftsman_skills table exists
        cursor.execute("SHOW TABLES LIKE 'craftsman_skills'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT * FROM craftsman_skills
                WHERE craftsman_id = %s
            """, (current_user.id,))
            
            skills = cursor.fetchall()
        
        # Check if craftsman_training table exists
        cursor.execute("SHOW TABLES LIKE 'craftsman_training'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT * FROM craftsman_training
                WHERE craftsman_id = %s
                ORDER BY training_date DESC
            """, (current_user.id,))
            
            training = cursor.fetchall()
    except Error as e:
        print(f"Error retrieving skills and training: {e}")
    
    cursor.close()
    conn.close()
    
    return render_template(
        'skills.html',
        skills=skills,
        training=training,
        today=datetime.now().date()
    )

@app.route('/notifications')
@login_required
def notifications():
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('notifications.html', notifications=[])
    
    cursor = conn.cursor(dictionary=True)
    
    # Get notifications
    notifications = []
    try:
        # Check if craftsman_notifications table exists
        cursor.execute("SHOW TABLES LIKE 'craftsman_notifications'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("""
                SELECT * FROM craftsman_notifications
                WHERE craftsman_id = %s
                ORDER BY created_at DESC
            """, (current_user.id,))
            
            notifications = cursor.fetchall()
            
            # Mark notifications as read
            cursor.execute("""
                UPDATE craftsman_notifications
                SET read = 1
                WHERE craftsman_id = %s AND read = 0
            """, (current_user.id,))
            conn.commit()
        else:
            # If table doesn't exist, return dummy notifications
            notifications = [
                {
                    'notification_id': 1,
                    'type': 'due_today',
                    'message': 'You have work orders due today',
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'read': False
                },
                {
                    'notification_id': 2,
                    'type': 'upcoming',
                    'message': 'You have upcoming work orders due in 2 days',
                    'date': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
                    'read': False
                }
            ]
    except Error as e:
        print(f"Error retrieving notifications: {e}")
    
    cursor.close()
    conn.close()
    
    return render_template('notifications.html', notifications=notifications)

# Create the uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to start the web server
def start_web_portal(host='0.0.0.0', port=5000, debug=False):
    """Start the web portal server"""
    app.run(host=host, port=port, debug=debug)

# Main entry point
if __name__ == '__main__':
    start_web_portal(debug=True)