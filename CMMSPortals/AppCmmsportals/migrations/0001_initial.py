# Generated by Django 5.1.7 on 2025-03-25 10:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Craftsman',
            fields=[
                ('craftsman_id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('specialization', models.CharField(blank=True, max_length=100, null=True)),
                ('experience_level', models.CharField(blank=True, max_length=50, null=True)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'craftsmen',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CraftsmanSkill',
            fields=[
                ('skill_id', models.AutoField(primary_key=True, serialize=False)),
                ('skill_name', models.CharField(max_length=100)),
                ('skill_level', models.CharField(blank=True, max_length=50, null=True)),
                ('certification_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('certification_authority', models.CharField(blank=True, max_length=100, null=True)),
                ('certification_number', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'craftsmen_skills',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CraftsmanTeam',
            fields=[
                ('team_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'craftsmen_teams',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CraftsmanTraining',
            fields=[
                ('training_id', models.AutoField(primary_key=True, serialize=False)),
                ('training_name', models.CharField(max_length=100)),
                ('training_date', models.DateField(blank=True, null=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('training_provider', models.CharField(blank=True, max_length=100, null=True)),
                ('certification_received', models.CharField(blank=True, max_length=100, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('training_status', models.CharField(blank=True, max_length=50, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'craftsmen_training',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('equipment_id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment_name', models.CharField(max_length=255)),
                ('template_id', models.IntegerField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=100, null=True)),
                ('manufacturer', models.CharField(blank=True, max_length=100, null=True)),
                ('installation_date', models.DateField(blank=True, null=True)),
                ('warranty_expiry', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'equipment_registry',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EquipmentHistory',
            fields=[
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('event_type', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('performed_by', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'equipment_history',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryCategory',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Inventory Categories',
                'db_table': 'inventory_categories',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('quantity', models.FloatField(default=0)),
                ('unit', models.CharField(max_length=50)),
                ('minimum_quantity', models.FloatField(default=0)),
                ('reorder_point', models.FloatField(default=0)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'inventory_items',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryPersonnel',
            fields=[
                ('personnel_id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.CharField(max_length=100)),
                ('access_level', models.CharField(default='Standard', max_length=50)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'inventory_personnel',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryTransaction',
            fields=[
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('Incoming', 'Incoming'), ('Outgoing', 'Outgoing'), ('Adjustment', 'Adjustment'), ('Initial', 'Initial')], max_length=50)),
                ('quantity', models.FloatField()),
                ('transaction_date', models.DateTimeField()),
                ('reference', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'inventory_transactions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MaintenanceReport',
            fields=[
                ('report_id', models.AutoField(primary_key=True, serialize=False)),
                ('report_date', models.DateTimeField()),
                ('report_data', models.JSONField()),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'maintenance_reports',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('po_id', models.AutoField(primary_key=True, serialize=False)),
                ('po_number', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Ordered', 'Ordered'), ('Received', 'Received'), ('Cancelled', 'Cancelled')], default='Pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expected_delivery', models.DateField(blank=True, null=True)),
                ('received_date', models.DateField(blank=True, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('shipping_address', models.TextField(blank=True, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'purchase_orders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('po_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.FloatField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'purchase_order_items',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ReportAttachment',
            fields=[
                ('attachment_id', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=255)),
                ('file_path', models.FileField(upload_to='report_attachments/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'report_attachments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('contact_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'suppliers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, max_length=50, null=True)),
                ('joined_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'team_members',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('work_order_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Completed', 'Completed'), ('On Hold', 'On Hold'), ('Cancelled', 'Cancelled')], default='Open', max_length=20)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=2)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('completed_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('assignment_type', models.CharField(choices=[('Individual', 'Individual'), ('Team', 'Team')], default='Individual', max_length=20)),
                ('tools_required', models.JSONField(blank=True, null=True)),
                ('spares_required', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'work_orders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=50)),
                ('access_level', models.CharField(blank=True, max_length=50, null=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EquipmentTechnicalInfo',
            fields=[
                ('equipment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='AppCmmsportals.equipment')),
                ('power_requirements', models.TextField(blank=True, null=True)),
                ('operating_temperature', models.TextField(blank=True, null=True)),
                ('weight', models.TextField(blank=True, null=True)),
                ('dimensions', models.TextField(blank=True, null=True)),
                ('operating_pressure', models.TextField(blank=True, null=True)),
                ('capacity', models.TextField(blank=True, null=True)),
                ('precision_accuracy', models.TextField(blank=True, null=True)),
                ('detailed_specifications', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'equipment_technical_info',
                'managed': False,
            },
        ),
    ]
