from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Case, When, IntegerField, F, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
import traceback
import csv
import json
import os
import mysql.connector
from mysql.connector import Error

from .models import (
    User, Craftsman, InventoryPersonnel, Equipment, WorkOrder, 
    MaintenanceReport, ReportAttachment, InventoryCategory, 
    Supplier, InventoryItem, InventoryTransaction, 
    PurchaseOrder, PurchaseOrderItem, CraftsmanSkill, CraftsmanTraining, CraftsmanTeam
)

# Helper functions to replace db_ops functionality
def get_db_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cmms_db',
            user='CMMS',
            password='cmms'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_craftsman_by_employee_id(employee_id):
    """Get craftsman details by employee ID"""
    try:
        connection = get_db_connection()
        if connection is None:
            return None
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM craftsmen 
            WHERE employee_id = %s
        """, (employee_id,))
        
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error getting craftsman: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_inventory_personnel_by_id(employee_id):
    """Get inventory personnel details by employee ID"""
    try:
        connection = get_db_connection()
        if connection is None:
            return None
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM inventory_personnel 
            WHERE employee_id = %s
        """, (employee_id,))
        
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error getting inventory personnel: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Custom template filter for newlines to breaks
def nl2br(value):
    """
    Convert newlines to <br> tags
    """
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Main routes
def index(request):
    """Home page route redirects to appropriate dashboard or login"""
    if request.user.is_authenticated:
        if request.user.role == 'inventory':
            return redirect('inventory_dashboard')
        else:
            return redirect('dashboard')
    return redirect('login')

def login_view(request):
    """Handle user login"""
    next_page = request.GET.get('next')
    
    if request.user.is_authenticated:
        if request.user.role == 'inventory':
            return redirect(next_page or 'inventory_dashboard')
        else:
            return redirect(next_page or 'craftsmen_dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        
        # Normal login process
        try:
            # Try to get user by employee_id
            user = User.objects.get(employee_id=employee_id)
            
            # In development, we don't check password
            # In production, you should uncomment this:
            # if not user.check_password(password):
            #     messages.error(request, 'Invalid employee ID or password')
            #     return render(request, 'login.html')
            if password.lower() == "dev":
                login(request, user)
                
                if request.user.role == 'inventory':
                    return redirect(next_page or 'inventory_dashboard')
                else:
                    return redirect(next_page or 'craftsmen_dashboard')
            else:
                messages.error(request, 'Invalid password')
                
        except User.DoesNotExist:
            # User doesn't exist in Django's auth system
            # Let's check if they exist in the old system
            
            # Try to find user in craftsmen table
            craftsman = get_craftsman_by_employee_id(employee_id)
            if craftsman and password.lower() == "dev":
                # Create a Django user for this craftsman
                from django.contrib.auth.hashers import make_password
                user = User.objects.create(
                    employee_id=employee_id,
                    password=make_password(password),
                    role='craftsman',
                    first_name=craftsman.get('first_name', ''),
                    last_name=craftsman.get('last_name', ''),
                    email=craftsman.get('email', '')
                )
                login(request, user)
                return redirect(next_page or 'craftsmen_dashboard')
            
            # Try to find user in inventory_personnel table
            inventory_person = get_inventory_personnel_by_id(employee_id)
            if inventory_person and password.lower() == "dev":
                # Create a Django user for this inventory personnel
                from django.contrib.auth.hashers import make_password
                user = User.objects.create(
                    employee_id=employee_id,
                    password=make_password(password),
                    role='inventory',
                    access_level=inventory_person.get('access_level', 'Standard'),
                    first_name=inventory_person.get('first_name', ''),
                    last_name=inventory_person.get('last_name', ''),
                    email=inventory_person.get('email', '')
                )
                login(request, user)
                return redirect(next_page or 'inventory_dashboard')
            
            messages.error(request, 'Invalid employee ID or password')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')

@login_required
def craftsmen_dashboard(request):
    """Dashboard for craftsmen"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Get work order counts
        work_orders = WorkOrder.objects.filter(craftsman=craftsman)
        counts = {
            'total': work_orders.count(),
            'open_count': work_orders.filter(status='Open').count(),
            'in_progress_count': work_orders.filter(status='In Progress').count(),
            'completed_count': work_orders.filter(status='Completed').count()
        }
        
        # Get recent work orders (last 5)
        recent_work_orders = work_orders.order_by('-created_date')[:5]
        
        # Get pending reports count - work orders that are completed but don't have maintenance reports
        completed_work_orders = work_orders.filter(status='Completed')
        
        # Count work orders that don't have an associated maintenance report
        pending_reports = 0
        for wo in completed_work_orders:
            try:
                # Try to find a maintenance report for this work order
                MaintenanceReport.objects.get(work_order=wo)
            except MaintenanceReport.DoesNotExist:
                # If no report exists, increment the counter
                pending_reports += 1
        
    except Craftsman.DoesNotExist:
        # If no craftsman record exists, show empty data
        messages.warning(request, "No craftsman record found for your employee ID.")
        counts = {
            'total': 0,
            'open_count': 0,
            'in_progress_count': 0,
            'completed_count': 0
        }
        recent_work_orders = []
        pending_reports = 0
    
    # Update the template path to include the craftsmen directory
    return render(request, 'craftsmen/dashboard.html', {
        'current_user': request.user,
        'counts': counts,
        'recent_work_orders': recent_work_orders,
        'pending_reports': pending_reports
    })

@login_required
def craftsmen_work_orders(request):
    """View all work orders for a craftsman"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    status_filter = request.GET.get('status', '')
    
    # First, get the craftsman record for this user
    try:
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Now use the craftsman_id to filter work orders
        work_orders_query = WorkOrder.objects.filter(craftsman_id=craftsman.craftsman_id)
        
        if status_filter:
            work_orders_query = work_orders_query.filter(status=status_filter)
        
        work_orders_list = work_orders_query.order_by('due_date')
        
    except Craftsman.DoesNotExist:
        # If no craftsman record exists, show empty list
        messages.warning(request, "No craftsman record found for your employee ID.")
        work_orders_list = []
    
    return render(request, 'craftsmen/work_orders.html', {
        'work_orders': work_orders_list,
        'status_filter': status_filter,
        'current_user': request.user
    })

@login_required
def craftsmen_view_work_order(request, work_order_id):
    """View details of a specific work order"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('logout')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Now get the work order
        work_order = WorkOrder.objects.get(work_order_id=work_order_id, craftsman=craftsman)
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        return redirect('craftsmen_dashboard')
    except WorkOrder.DoesNotExist:
        messages.error(request, 'Work order not found or you do not have permission to view it')
        return redirect('craftsmen_work_orders')
    
    # Check if this work order has a maintenance report
    has_report = False
    report_id = None
    
    try:
        report = MaintenanceReport.objects.get(work_order=work_order)
        has_report = True
        report_id = report.report_id
    except MaintenanceReport.DoesNotExist:
        pass
    
    return render(request, 'craftsmen/view_work_order.html', {
        'work_order': work_order,
        'has_report': has_report,
        'report_id': report_id
    })

@login_required
def craftsmen_update_work_order_status(request, work_order_id):
    """Update the status of a work order"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('logout')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Now get the work order
        work_order = WorkOrder.objects.get(work_order_id=work_order_id, craftsman=craftsman)
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        return redirect('craftsmen_dashboard')
    except WorkOrder.DoesNotExist:
        messages.error(request, 'Work order not found or you do not have permission to update it')
        return redirect('craftsmen_work_orders')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        completed_date = request.POST.get('completed_date')
        
        # Validate status
        valid_statuses = ['Open', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
        if status not in valid_statuses:
            messages.error(request, 'Invalid status')
            return render(request, 'craftsmen/update_work_order_status.html', {
                'work_order': work_order,
                'today': timezone.now().date()
            })
        
        # Update work order - only update the fields we're changing
        work_order.status = status
        work_order.notes = notes
        
        if status == 'Completed' and completed_date:
            work_order.completed_date = completed_date
        
        # Don't modify the priority field
        work_order.save(update_fields=['status', 'notes', 'completed_date'])
        
        messages.success(request, 'Work order status updated successfully')
        return redirect('craftsmen_view_work_order', work_order_id=work_order_id)
    
    return render(request, 'craftsmen/update_work_order_status.html', {
        'work_order': work_order,
        'today': timezone.now().date()
    })

@login_required
def craftsmen_add_report(request, work_order_id):
    """Add a maintenance report for a work order"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('logout')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Now get the work order
        work_order = WorkOrder.objects.get(work_order_id=work_order_id)
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        return redirect('craftsmen_dashboard')
    except WorkOrder.DoesNotExist:
        messages.error(request, 'Work order not found')
        return redirect('craftsmen_work_orders')
    
    # Get equipment type
    equipment_type = 'unknown'
    if work_order.equipment:
        equipment_type = work_order.equipment.template_id or 'unknown'
    
    # Check if this work order already has a maintenance report
    try:
        report = MaintenanceReport.objects.get(work_order=work_order)
        messages.error(request, 'This work order already has a maintenance report')
        return redirect('craftsmen_view_work_order', work_order_id=work_order_id)
    except MaintenanceReport.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Process form data
        maintenance_type = request.POST.get('maintenance_type')
        initial_condition = request.POST.get('initial_condition')
        final_condition = request.POST.get('final_condition')
        
        # Build report data
        report_data = {
            'general': {
                'maintenance_type': maintenance_type,
                'initial_condition': initial_condition,
                'final_condition': final_condition
            },
            'inspection': {
                'visual_external_damage': 'visual_external_damage' in request.POST,
                'visual_corrosion': 'visual_corrosion' in request.POST,
                'visual_leaks': 'visual_leaks' in request.POST,
                'visual_wear': 'visual_wear' in request.POST,
                'operational_unusual_noise': 'operational_unusual_noise' in request.POST,
                'operational_vibration': 'operational_vibration' in request.POST,
                'operational_overheating': 'operational_overheating' in request.POST,
                'operational_performance': 'operational_performance' in request.POST,
                'additional_findings': request.POST.get('additional_findings', '')
            }
        }
        
        # Equipment specific data based on type
        equipment_type = equipment_type.lower() if isinstance(equipment_type, str) else ''
        
        if equipment_type == 'mechanical':
            report_data['mechanical'] = collect_mechanical_data(request.POST)
        elif equipment_type == 'electrical':
            report_data['electrical'] = collect_electrical_data(request.POST)
        elif equipment_type == 'hvac':
            report_data['hvac'] = collect_hvac_data(request.POST)
        elif equipment_type == 'plumbing':
            report_data['plumbing'] = collect_plumbing_data(request.POST)
        
        # Measurements data
        report_data['measurements'] = collect_measurements_data(request.POST)
        
        # Parts data
        report_data['parts'] = collect_parts_data(request.POST)
        
        # Create maintenance report
        report = MaintenanceReport.objects.create(
            work_order=work_order,
            equipment=work_order.equipment,
            craftsman=craftsman,
            report_date=timezone.now(),
            report_data=report_data,
            comments=request.POST.get('comments', '')
        )
        
        # Update work order status to completed if not already
        if work_order.status != 'Completed':
            work_order.status = 'Completed'
            work_order.completed_date = timezone.now().date()
            # Only update specific fields to avoid the priority issue
            work_order.save(update_fields=['status', 'completed_date'])
        
        # Handle file uploads
        if 'attachments' in request.FILES:
            files = request.FILES.getlist('attachments')
            for file in files:
                if file and file.name:
                    attachment = ReportAttachment.objects.create(
                        report=report,
                        filename=file.name,
                        file_path=file
                    )
        
        messages.success(request, 'Maintenance report created successfully')
        return redirect('craftsmen_view_report', report_id=report.report_id)
    
    return render(request, 'craftsmen/add_report.html', {
        'work_order': work_order,
        'equipment_type': equipment_type,
        'today': timezone.now().date(),
        'now': timezone.now().strftime('%H:%M'),
        'current_user': request.user
    })

@login_required
def craftsmen_view_report(request, report_id):
    """View a maintenance report"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('logout')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Use get_object_or_404 instead of try/except for MaintenanceReport
        report = get_object_or_404(MaintenanceReport, report_id=report_id, craftsman=craftsman)
        report_data = report.report_data
        attachments = ReportAttachment.objects.filter(report=report)
        
        return render(request, 'craftsmen/view_report.html', {
            'report': report,
            'report_data': report_data,
            'attachments': attachments
        })
        
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        return redirect('craftsmen_dashboard')

def inventory(request):
    return redirect('login')

def craftsmen(request):
    return redirect('login')

@login_required
def craftsmen_download_attachment(request, attachment_id):
    """Download a report attachment"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('logout')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Get the attachment, ensuring it belongs to a report by this craftsman
        attachment = ReportAttachment.objects.get(
            attachment_id=attachment_id,
            report__craftsman=craftsman
        )
        
        return FileResponse(
            attachment.file_path.open('rb'),
            as_attachment=True,
            filename=attachment.filename
        )
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        return redirect('craftsmen_dashboard')
    except ReportAttachment.DoesNotExist:
        messages.error(request, 'Attachment not found or you do not have permission to download it')
        return redirect('maintenance_history')

@login_required
def craftsmen_print_report(request, report_id):
    """Print-friendly version of a report"""
    # Similar to view_report but with a print-friendly template
    return redirect('view_report', report_id=report_id)

@login_required
def craftsmen_maintenance_history(request):
    """View maintenance history for a craftsman"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Get date filters from request
        from_date = request.GET.get('from_date', '')
        to_date = request.GET.get('to_date', '')
        
        # Query maintenance reports for this craftsman
        reports_query = MaintenanceReport.objects.filter(craftsman=craftsman)
        
        # Apply date filters if provided
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                reports_query = reports_query.filter(report_date__gte=from_date_obj)
            except ValueError:
                messages.warning(request, 'Invalid from date format. Using all dates.')
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                # Add one day to include the end date in results
                to_date_obj = to_date_obj + timedelta(days=1)
                reports_query = reports_query.filter(report_date__lt=to_date_obj)
            except ValueError:
                messages.warning(request, 'Invalid to date format. Using all dates.')
        
        # Order by report date, newest first
        reports = reports_query.order_by('-report_date')
        
        # Format the reports for the template
        history = []
        for report in reports:
            history.append({
                'date': report.report_date.strftime('%Y-%m-%d'),
                'work_order_id': report.work_order.work_order_id,
                'equipment_name': report.equipment.equipment_name,
                'maintenance_type': report.report_data.get('maintenance_type', 'Unspecified'),
                'description': report.work_order.description[:100] + '...' if report.work_order.description and len(report.work_order.description) > 100 else report.work_order.description,
                'report_id': report.report_id
            })
        
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        history = []
    
    return render(request, 'craftsmen/maintenance_history.html', {
        'history': history,
        'from_date': from_date,
        'to_date': to_date,
        'current_user': request.user
    })

@login_required
def craftsmen_skills(request):
    """View skills and training for a craftsman"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Get skills for this craftsman
        skills = CraftsmanSkill.objects.filter(craftsman=craftsman).order_by('skill_name')
        
        # Get trainings for this craftsman
        trainings = CraftsmanTraining.objects.filter(craftsman=craftsman).order_by('-training_date')
        
        # Format skills data
        skills_data = []
        for skill in skills:
            skill_data = {
                'skill_id': skill.skill_id,
                'name': skill.skill_name,
                'level': skill.skill_level or 'Not specified',
                'certification_date': skill.certification_date,
                'expiry_date': skill.expiry_date,
                'certification_authority': skill.certification_authority or 'Not specified',
                'certification_number': skill.certification_number or 'Not specified',
                'status': 'Active'
            }
            
            # Check if certification is expired
            if skill.expiry_date and skill.expiry_date < timezone.now().date():
                skill_data['status'] = 'Expired'
            
            # Check if certification is about to expire (within 30 days)
            elif skill.expiry_date and skill.expiry_date < (timezone.now().date() + timedelta(days=30)):
                skill_data['status'] = 'Expiring Soon'
                
            skills_data.append(skill_data)
        
        # Format trainings data
        trainings_data = []
        for training in trainings:
            training_data = {
                'training_id': training.training_id,
                'name': training.training_name,
                'training_date': training.training_date,
                'completion_date': training.completion_date,
                'provider': training.training_provider or 'Not specified',
                'certification': training.certification_received or 'Not specified',
                'expiry_date': training.expiry_date,
                'status': training.training_status or 'Not specified'
            }
            
            # If status is not explicitly set, determine it based on dates
            if not training.training_status:
                if not training.completion_date:
                    training_data['status'] = 'In Progress'
                else:
                    training_data['status'] = 'Completed'
                    
                    # Check if certification is expired
                    if training.expiry_date and training.expiry_date < timezone.now().date():
                        training_data['status'] = 'Expired'
            
            trainings_data.append(training_data)
        
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        skills_data = []
        trainings_data = []
    
    return render(request, 'craftsmen/skills.html', {
        'skills': skills_data,
        'trainings': trainings_data,
        'current_user': request.user
    })

@login_required
def craftsmen_notifications(request):
    """View notifications for a craftsman"""
    # Ensure user is a craftsman
    if request.user.role != 'craftsman':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        # Get the craftsman record for this user
        craftsman = Craftsman.objects.get(employee_id=request.user.employee_id)
        
        # Get notifications for this craftsman
        notifications = []
        
        # 1. Due today work orders
        due_today = WorkOrder.objects.filter(
            craftsman=craftsman,
            due_date=timezone.now().date(),
            status__in=['Open', 'In Progress']
        )
        
        for work_order in due_today:
            notifications.append({
                'type': 'due_today',
                'message': f'Work Order #{work_order.work_order_id} ({work_order.title}) is due today',
                'date': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'read': False,
                'work_order_id': work_order.work_order_id
            })
        
        # 2. Upcoming work orders (due in the next 3 days)
        upcoming_date = timezone.now().date() + timedelta(days=1)
        upcoming_end_date = timezone.now().date() + timedelta(days=3)
        upcoming = WorkOrder.objects.filter(
            craftsman=craftsman,
            due_date__range=[upcoming_date, upcoming_end_date],
            status__in=['Open', 'In Progress']
        )
        
        for work_order in upcoming:
            days_until = (work_order.due_date - timezone.now().date()).days
            day_text = "tomorrow" if days_until == 1 else f"in {days_until} days"
            notifications.append({
                'type': 'upcoming',
                'message': f'Work Order #{work_order.work_order_id} ({work_order.title}) is due {day_text}',
                'date': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'read': False,
                'work_order_id': work_order.work_order_id
            })
        
        # 3. Overdue work orders
        overdue = WorkOrder.objects.filter(
            craftsman=craftsman,
            due_date__lt=timezone.now().date(),
            status__in=['Open', 'In Progress']
        )
        
        for work_order in overdue:
            days_overdue = (timezone.now().date() - work_order.due_date).days
            notifications.append({
                'type': 'overdue',
                'message': f'Work Order #{work_order.work_order_id} ({work_order.title}) is overdue by {days_overdue} days',
                'date': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'read': False,
                'work_order_id': work_order.work_order_id
            })
        
        # 4. Expiring certifications (within 30 days)
        expiry_date = timezone.now().date() + timedelta(days=30)
        expiring_skills = CraftsmanSkill.objects.filter(
            craftsman=craftsman,
            expiry_date__lte=expiry_date,
            expiry_date__gte=timezone.now().date()
        )
        
        for skill in expiring_skills:
            days_until = (skill.expiry_date - timezone.now().date()).days
            notifications.append({
                'type': 'system',
                'message': f'Your certification for {skill.skill_name} will expire in {days_until} days',
                'date': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'read': False,
                'skill_id': skill.skill_id
            })
        
        # Sort notifications by date (newest first)
        notifications.sort(key=lambda x: x['type'] == 'overdue', reverse=True)
        
    except Craftsman.DoesNotExist:
        messages.error(request, 'Craftsman profile not found for your account')
        notifications = []
    
    return render(request, 'craftsmen/notifications.html', {
        'notifications': notifications,
        'current_user': request.user
    })

# Inventory Management Views
@login_required
def inventory_dashboard(request):
    """Inventory personnel dashboard"""
    # Check if user has inventory role
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied. You need inventory personnel permissions.')
        return redirect('logout')
    
    # Get inventory statistics from database
    total_items = InventoryItem.objects.count()
    low_stock_count = InventoryItem.objects.filter(quantity__lte=F('minimum_quantity')).count()
    
    # Calculate total inventory value using the unit_cost field
    total_value = InventoryItem.objects.filter(
        unit_cost__isnull=False
    ).annotate(
        item_value=F('quantity') * F('unit_cost')
    ).aggregate(
        total=Sum('item_value')
    )['total'] or 0
    
    stats = {
        'total_items': total_items,
        'low_stock': low_stock_count,
        'total_value': total_value,
        'active_pos': PurchaseOrder.objects.filter(status__in=['Pending', 'Approved', 'Ordered']).count()
    }
    
    # Get low stock items with more details
    low_stock_items_query = InventoryItem.objects.filter(
        quantity__lte=F('minimum_quantity')
    ).order_by('quantity')[:10]
    
    low_stock_items = []
    for item in low_stock_items_query:
        low_stock_items.append({
            'item_id': item.item_id,
            'item_code': item.item_code,
            'name': item.name,
            'quantity': item.quantity,
            'minimum_quantity': item.minimum_quantity,
            'reorder_point': getattr(item, 'reorder_point', item.minimum_quantity),
            'unit': item.unit or 'units'
        })
    
    # Get recent activities - actual transactions from database
    recent_activities = InventoryTransaction.objects.all().order_by('-transaction_date')[:10]
    activities = []
    
    for transaction in recent_activities:
        activities.append({
            'date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M'),
            'type': transaction.transaction_type,
            'description': f"{transaction.transaction_type} - {transaction.quantity} of {transaction.item.name}",
            'status': 'Completed'
        })
    
    # Get pending purchase orders
    pending_pos = PurchaseOrder.objects.filter(
        status__in=['Pending', 'Approved', 'Ordered']
    ).order_by('-created_at')[:5]
    
    # Make sure we're using the correct template for inventory dashboard
    return render(request, 'inventory/dashboard.html', {
        'stats': stats,
        'recent_activities': activities,
        'low_stock_items': low_stock_items,
        'user': request.user
    })

@login_required
def inventory_items(request):
    """View inventory items"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Get filter parameters
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Get all categories for filter
    categories = InventoryCategory.objects.all().order_by('name')
    
    # Build query with filters
    items_query = InventoryItem.objects.all()
    
    if category:
        items_query = items_query.filter(category_id=category)
    
    if status:
        if status == 'Low Stock':
            items_query = items_query.filter(quantity__lte=F('minimum_quantity'), quantity__gt=0)
        elif status == 'Out of Stock':
            items_query = items_query.filter(quantity__lte=0)
        elif status == 'In Stock':
            items_query = items_query.filter(quantity__gt=F('minimum_quantity'))
    
    if search:
        # Use name field instead of item_code since item_code doesn't exist
        items_query = items_query.filter(name__icontains=search)
    
    # Order by name instead of item_code
    items = items_query.order_by('name')
    
    return render(request, 'inventory/items.html', {
        'items': items,
        'categories': categories,
        'selected_category': category,
        'selected_status': status,
        'search_text': search
    })

# Helper functions for report data collection
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

# API functions
def api_login(request):
    """API endpoint for mobile app login"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method allowed'})
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        password = data.get('password')
        
        # DEVELOPMENT BYPASS: Allow login with "dev" as employee ID
        if employee_id and employee_id.lower() == "dev":
            return JsonResponse({
                'success': True,
                'user': {
                    'id': 1,
                    'employee_id': "DEV001",
                    'name': "Development User",
                    'email': "dev@example.com"
                }
            })
        
        # Normal login process
        try:
            user = User.objects.get(employee_id=employee_id)
            
            # For development, accept any password
            # In production, uncomment:
            # if not user.check_password(password):
            #     return JsonResponse({'success': False, 'message': 'Invalid employee ID or password'})
            
            if hasattr(user, 'craftsman_profile'):
                craftsman = user.craftsman_profile
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': craftsman.craftsman_id,
                        'employee_id': craftsman.employee_id,
                        'name': f"{craftsman.first_name} {craftsman.last_name}",
                        'email': craftsman.email
                    }
                })
            else:
                return JsonResponse({'success': False, 'message': 'Only craftsmen can use the mobile app'})
                
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid employee ID or password'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

def api_work_orders(request, craftsman_id):
    """API endpoint to get work orders for a craftsman"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Only GET method allowed'})
    
    try:
        craftsman = Craftsman.objects.get(craftsman_id=craftsman_id)
        
        work_orders = WorkOrder.objects.filter(craftsman=craftsman).order_by('due_date', '-priority')
        
        work_orders_data = []
        for wo in work_orders:
            work_order_data = {
                'work_order_id': wo.work_order_id,
                'title': wo.title,
                'description': wo.description,
                'status': wo.status,
                'priority': wo.priority,
                'created_date': wo.created_date.strftime('%Y-%m-%d') if wo.created_date else None,
                'due_date': wo.due_date.strftime('%Y-%m-%d') if wo.due_date else None,
                'completed_date': wo.completed_date.strftime('%Y-%m-%d') if wo.completed_date else None,
                'equipment_name': wo.equipment.equipment_name if wo.equipment else None,
                'equipment_id': wo.equipment.equipment_id if wo.equipment else None,
            }
            work_orders_data.append(work_order_data)
        
        return JsonResponse({'success': True, 'work_orders': work_orders_data})
        
    except Craftsman.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Craftsman not found'})

@login_required
def item_details(request, item_id):
    """View inventory item details"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    try:
        item = InventoryItem.objects.get(item_id=item_id)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found')
        return redirect('inventory_items')
    
    # Get transaction history
    transactions = InventoryTransaction.objects.filter(item=item).order_by('-transaction_date')
    
    return render(request, 'inventory/item_details.html', {
        'item': item,
        'transactions': transactions
    })

@login_required
def edit_inventory_item(request, item_id):
    """Edit an inventory item"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Check access level for edit permissions
    if request.user.inventory_profile.access_level not in ['Admin', 'Manager']:
        messages.error(request, 'You do not have permission to edit items')
        return redirect('item_details', item_id=item_id)
    
    try:
        item = InventoryItem.objects.get(item_id=item_id)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found')
        return redirect('inventory_items')
    
    # Get categories and suppliers for dropdown
    categories = InventoryCategory.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('name')
    
    return render(request, 'inventory/item_form.html', {
        'item': item,
        'categories': categories,
        'suppliers': suppliers
    })

@login_required
def add_inventory_item(request):
    """Add a new inventory item"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Check access level for add permissions
    if request.user.inventory_profile.access_level not in ['Admin', 'Manager', 'Standard']:
        messages.error(request, 'You do not have permission to add items')
        return redirect('inventory_items')
    
    # Get categories and suppliers for dropdown
    categories = InventoryCategory.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('name')
    
    return render(request, 'inventory/item_form.html', {
        'categories': categories,
        'suppliers': suppliers
    })

@login_required
def save_inventory_item(request):
    """Save inventory item (new or edit)"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    if request.method != 'POST':
        return redirect('inventory_items')
    
    # Get form data
    item_id = request.POST.get('item_id')
    item_code = request.POST.get('item_code')
    name = request.POST.get('name')
    category_id = request.POST.get('category_id') or None
    supplier_id = request.POST.get('supplier_id') or None
    quantity = float(request.POST.get('quantity', 0))
    unit = request.POST.get('unit')
    minimum_quantity = float(request.POST.get('minimum_quantity', 0))
    reorder_point = float(request.POST.get('reorder_point', 0))
    unit_cost = float(request.POST.get('unit_cost', 0))
    location = request.POST.get('location', '')
    description = request.POST.get('description', '')
    
    try:
        if item_id:  # Update existing item
            # Check permission
            if request.user.inventory_profile.access_level not in ['Admin', 'Manager']:
                messages.error(request, 'You do not have permission to edit items')
                return redirect('item_details', item_id=item_id)
            
            item = InventoryItem.objects.get(item_id=item_id)
            item.item_code = item_code
            item.name = name
            item.category_id = category_id
            item.supplier_id = supplier_id
            item.quantity = quantity
            item.unit = unit
            item.minimum_quantity = minimum_quantity
            item.reorder_point = reorder_point
            item.unit_cost = unit_cost
            item.location = location
            item.description = description
            item.save()
            
            messages.success(request, 'Item updated successfully')
            
        else:  # Add new item
            # Check permission
            if request.user.inventory_profile.access_level not in ['Admin', 'Manager', 'Standard']:
                messages.error(request, 'You do not have permission to add items')
                return redirect('inventory_items')
            
            category = InventoryCategory.objects.get(category_id=category_id) if category_id else None
            supplier = Supplier.objects.get(supplier_id=supplier_id) if supplier_id else None
            
            item = InventoryItem.objects.create(
                item_code=item_code,
                name=name,
                category=category,
                supplier=supplier,
                quantity=quantity,
                unit=unit,
                minimum_quantity=minimum_quantity,
                reorder_point=reorder_point,
                unit_cost=unit_cost,
                location=location,
                description=description
            )
            
            # Create initial inventory transaction if quantity > 0
            if quantity > 0:
                InventoryTransaction.objects.create(
                    item=item,
                    transaction_type='Initial',
                    quantity=quantity,
                    personnel=request.user.inventory_profile,
                    transaction_date=timezone.now(),
                    notes='Initial inventory setup'
                )
                
            messages.success(request, 'Item added successfully')
    
    except Exception as e:
        messages.error(request, f'Error saving item: {str(e)}')
    
    if item_id:
        return redirect('item_details', item_id=item_id)
    else:
        return redirect('inventory_items')

@login_required
def update_item_quantity(request, item_id):
    """Update inventory item quantity"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    try:
        item = InventoryItem.objects.get(item_id=item_id)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found')
        return redirect('inventory_items')
    
    if request.method == 'POST':
        # Process form data
        transaction_type = request.POST.get('transaction_type')
        quantity = float(request.POST.get('quantity', 0))
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        
        # Validate transaction type
        valid_types = ['Incoming', 'Outgoing', 'Adjustment']
        if transaction_type not in valid_types:
            messages.error(request, 'Invalid transaction type')
            return render(request, 'inventory/update_quantity.html', {'item': item})
        
        try:
            # Update inventory quantity based on transaction type
            new_quantity = item.quantity
            
            if transaction_type == 'Incoming':
                new_quantity += quantity
            elif transaction_type == 'Outgoing':
                new_quantity -= quantity
            elif transaction_type == 'Adjustment':
                new_quantity = quantity
            
            # Update item quantity
            item.quantity = new_quantity
            item.save()
            
            # Record transaction
            InventoryTransaction.objects.create(
                item=item,
                transaction_type=transaction_type,
                quantity=quantity,
                personnel=request.user.inventory_profile,
                transaction_date=timezone.now(),
                reference=reference,
                notes=notes
            )
            
            messages.success(request, 'Quantity updated successfully')
            return redirect('item_details', item_id=item_id)
            
        except Exception as e:
            messages.error(request, f'Error updating quantity: {str(e)}')
    
    return render(request, 'inventory/update_quantity.html', {'item': item})

@login_required
def inventory_notifications(request):
    """View inventory notifications"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Placeholder for inventory notifications
    notifications = [
        {
            'id': 1,
            'message': 'Item "Fuses 10A" is now below minimum quantity',
            'created_at': timezone.now() - timedelta(hours=2),
            'is_read': False
        },
        {
            'id': 2,
            'message': 'Purchase Order #PO-20230501 has been delivered',
            'created_at': timezone.now() - timedelta(days=1),
            'is_read': True
        }
    ]
    
    return render(request, 'inventory/notifications.html', {'notifications': notifications})

@login_required
def purchase_orders(request):
    """View purchase orders"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Get filter parameters
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Build query with filters
    orders_query = PurchaseOrder.objects.all()
    
    if status:
        orders_query = orders_query.filter(status=status)
    
    if search:
        orders_query = orders_query.filter(po_number__icontains=search) | orders_query.filter(supplier__name__icontains=search)
    
    purchase_orders = orders_query.order_by('-created_at')
    
    return render(request, 'inventory/purchase_orders.html', {
        'purchase_orders': purchase_orders,
        'selected_status': status,
        'search_text': search
    })

@login_required
def create_purchase_order(request):
    """Create a new purchase order"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Check permission for creating POs
    if request.user.inventory_profile.access_level not in ['Admin', 'Manager']:
        messages.error(request, 'You do not have permission to create purchase orders')
        return redirect('purchase_orders')
    
    # Get suppliers for dropdown
    suppliers = Supplier.objects.all().order_by('name')
    
    # Get low stock items
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=F('reorder_point')
    ).order_by(
        F('quantity') / F('reorder_point'), 'name'
    )
    
    if request.method == 'POST':
        # Process form data
        supplier_id = request.POST.get('supplier_id')
        po_number = request.POST.get('po_number') or f'PO-{timezone.now().strftime("%Y%m%d%H%M")}'
        expected_delivery = request.POST.get('expected_delivery')
        shipping_address = request.POST.get('shipping_address', '')
        notes = request.POST.get('notes', '')
        
        try:
            supplier = Supplier.objects.get(supplier_id=supplier_id)
            
            # Create purchase order
            po = PurchaseOrder.objects.create(
                po_number=po_number,
                supplier=supplier,
                created_by=request.user.inventory_profile,
                status='Pending',
                expected_delivery=expected_delivery,
                shipping_address=shipping_address,
                notes=notes
            )
            
            total_amount = 0
            
            # Process items
            item_count = int(request.POST.get('item_count', 0))
            for i in range(1, item_count + 1):
                item_id = request.POST.get(f'item_id_{i}')
                quantity = float(request.POST.get(f'quantity_{i}', 0))
                unit_price = float(request.POST.get(f'unit_price_{i}', 0))
                
                if item_id and quantity > 0:
                    item = InventoryItem.objects.get(item_id=item_id)
                    
                    PurchaseOrderItem.objects.create(
                        po=po,
                        item=item,
                        quantity=quantity,
                        unit_price=unit_price
                    )
                    
                    total_amount += quantity * unit_price
            
            # Update total amount
            po.total_amount = total_amount
            po.save()
            
            messages.success(request, 'Purchase order created successfully')
            return redirect('purchase_orders')
            
        except Exception as e:
            messages.error(request, f'Error creating purchase order: {str(e)}')
    
    return render(request, 'inventory/create_purchase_order.html', {
        'suppliers': suppliers,
        'low_stock_items': low_stock_items,
        'today': timezone.now().strftime('%Y-%m-%d'),
        'min_delivery_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    })

@login_required
def view_purchase_order(request, po_id):
    """View a purchase order"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    try:
        po = PurchaseOrder.objects.get(po_id=po_id)
        items = PurchaseOrderItem.objects.filter(po=po)
    except PurchaseOrder.DoesNotExist:
        messages.error(request, 'Purchase order not found')
        return redirect('purchase_orders')
    
    return render(request, 'inventory/view_purchase_order.html', {
        'po': po,
        'items': items
    })

@login_required
def receive_purchase_order(request, po_id):
    """Receive items from a purchase order"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    try:
        po = PurchaseOrder.objects.get(po_id=po_id)
    except PurchaseOrder.DoesNotExist:
        messages.error(request, 'Purchase order not found')
        return redirect('purchase_orders')
    
    # Check if PO is in a receivable state
    if po.status not in ['Pending', 'Approved']:
        messages.error(request, 'This purchase order cannot be received')
        return redirect('view_purchase_order', po_id=po_id)
    
    # Get purchase order items
    items = PurchaseOrderItem.objects.filter(po=po)
    
    if request.method == 'POST':
        # Process form data
        received_date = request.POST.get('received_date') or timezone.now().date()
        invoice_number = request.POST.get('invoice_number', '')
        notes = request.POST.get('notes', '')
        
        try:
            # Update purchase order status
            po.status = 'Received'
            po.received_date = received_date
            po.invoice_number = invoice_number
            po.notes = notes
            po.save()
            
            # Process received items
            for item in items:
                received_quantity = float(request.POST.get(f'received_quantity_{item.item.item_id}', 0))
                
                if received_quantity > 0:
                    # Update inventory quantity
                    inventory_item = item.item
                    inventory_item.quantity += received_quantity
                    inventory_item.save()
                    
                    # Record transaction
                    InventoryTransaction.objects.create(
                        item=inventory_item,
                        transaction_type='Incoming',
                        quantity=received_quantity,
                        personnel=request.user.inventory_profile,
                        transaction_date=timezone.now(),
                        reference=f"PO #{po.po_number}",
                        notes=f"Received from PO #{po.po_number}"
                    )
            
            messages.success(request, 'Purchase order received successfully')
            return redirect('view_purchase_order', po_id=po_id)
            
        except Exception as e:
            messages.error(request, f'Error receiving purchase order: {str(e)}')
    
    return render(request, 'inventory/receive_purchase_order.html', {
        'po': po,
        'items': items,
        'today': timezone.now().strftime('%Y-%m-%d')
    })

@login_required
def inventory_reports(request):
    """View inventory reports"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    return render(request, 'inventory/reports.html')

@login_required
def delete_inventory_item(request):
    """Delete an inventory item"""
    if request.method != 'POST':
        return redirect('inventory_items')
    
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Check access level for delete permissions
    if request.user.inventory_profile.access_level not in ['Admin', 'Manager']:
        messages.error(request, 'You do not have permission to delete items')
        return redirect('inventory_items')
    
    item_id = request.POST.get('item_id')
    
    try:
        item = InventoryItem.objects.get(item_id=item_id)
        item_name = item.name
        item.delete()
        messages.success(request, f'Item "{item_name}" deleted successfully')
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found')
    
    return redirect('inventory_items')

@login_required
def receive_items(request):
    """Receive items from purchase orders"""
    # Ensure user is inventory personnel
    if request.user.role != 'inventory':
        messages.error(request, 'Access denied')
        return redirect('logout')
    
    # Get all purchase orders with status 'Received'
    received_po = PurchaseOrder.objects.filter(status='Received').order_by('-po_number')
    
    return render(request, 'inventory/receive_items.html', {
        'received_po': received_po
    })


def export_purchase_orders(request):
    # Fetch your purchase orders
    purchase_orders = PurchaseOrder.objects.all()  # Replace with the actual query to get purchase orders

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchase_orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['PO Number', 'Supplier', 'Date Created', 'Expected Delivery', 'Total Amount', 'Status', 'Created By'])  # Add your field names

    for po in purchase_orders:
        writer.writerow([po.po_number, po.supplier_name, po.created_at, po.expected_delivery, po.total_amount, po.status, po.created_by_name])

    return response

def generate_report(request):
    if request.method == "POST":
        # Handle the report generation logic here
        pass
    return render(request, 'inventory/report_result.html')
