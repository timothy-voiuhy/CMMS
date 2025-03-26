from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models

class CMMSUserManager(BaseUserManager):
    def create_user(self, employee_id, password=None, **extra_fields):
        if not employee_id:
            raise ValueError('Users must have an employee ID')
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('date_joined', timezone.now())
        
        user = self.model(employee_id=employee_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('access_level', 'Admin')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        
        return self.create_user(employee_id, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    access_level = models.CharField(max_length=50, null=True, blank=True)
    
    # Standard Django user fields
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    
    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['role']
    
    objects = CMMSUserManager()
    
    class Meta:
        managed = False
        db_table = 'users'
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.employee_id
    
    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.employee_id

# Craftsman model linked to User
class Craftsman(models.Model):
    craftsman_id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    experience_level = models.CharField(max_length=50, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'craftsmen'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

# CraftsmanSkill model
class CraftsmanSkill(models.Model):
    skill_id = models.AutoField(primary_key=True)
    craftsman = models.ForeignKey(Craftsman, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    skill_level = models.CharField(max_length=50, null=True, blank=True)
    certification_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    certification_authority = models.CharField(max_length=100, null=True, blank=True)
    certification_number = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'craftsmen_skills'
    
    def __str__(self):
        return f"{self.craftsman.first_name} - {self.skill_name}"

# CraftsmanTraining model
class CraftsmanTraining(models.Model):
    training_id = models.AutoField(primary_key=True)
    craftsman = models.ForeignKey(Craftsman, on_delete=models.CASCADE, related_name='trainings')
    training_name = models.CharField(max_length=100)
    training_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    training_provider = models.CharField(max_length=100, null=True, blank=True)
    certification_received = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    training_status = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'craftsmen_training'
    
    def __str__(self):
        return f"{self.craftsman.first_name} - {self.training_name}"

# CraftsmanTeam model
class CraftsmanTeam(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    team_leader = models.ForeignKey(Craftsman, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'craftsmen_teams'
    
    def __str__(self):
        return self.team_name

# TeamMember model
class TeamMember(models.Model):
    team = models.ForeignKey(CraftsmanTeam, on_delete=models.CASCADE)
    craftsman = models.ForeignKey(Craftsman, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, null=True, blank=True)
    joined_date = models.DateField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'team_members'
        unique_together = ('team', 'craftsman')
    
    def __str__(self):
        return f"{self.craftsman.first_name} in {self.team.team_name}"

# Inventory Personnel model
class InventoryPersonnel(models.Model):
    personnel_id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    access_level = models.CharField(max_length=20, default='Standard')
    hire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'inventory_personnel'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

# Equipment model
class Equipment(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    equipment_name = models.CharField(max_length=255)
    template_id = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'equipment_registry'
    
    def __str__(self):
        return self.equipment_name

# EquipmentTechnicalInfo model
class EquipmentTechnicalInfo(models.Model):
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, primary_key=True)
    power_requirements = models.TextField(null=True, blank=True)
    operating_temperature = models.TextField(null=True, blank=True)
    weight = models.TextField(null=True, blank=True)
    dimensions = models.TextField(null=True, blank=True)
    operating_pressure = models.TextField(null=True, blank=True)
    capacity = models.TextField(null=True, blank=True)
    precision_accuracy = models.TextField(null=True, blank=True)
    detailed_specifications = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'equipment_technical_info'
    
    def __str__(self):
        return f"Tech info for {self.equipment.equipment_name}"

# EquipmentHistory model
class EquipmentHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    date = models.DateField()
    event_type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    performed_by = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'equipment_history'
    
    def __str__(self):
        return f"{self.event_type} on {self.date}"

# Work Order model with additional fields
class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    ASSIGNMENT_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team'),
    ]
    
    work_order_id = models.AutoField(primary_key=True)
    craftsman = models.ForeignKey(Craftsman, on_delete=models.SET_NULL, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_CHOICES, default='Individual')
    team = models.ForeignKey(CraftsmanTeam, on_delete=models.SET_NULL, null=True, blank=True)
    tools_required = models.JSONField(null=True, blank=True)
    spares_required = models.JSONField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'work_orders'
    
    def __str__(self):
        return self.title

# Maintenance Report model
class MaintenanceReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    craftsman = models.ForeignKey(Craftsman, on_delete=models.CASCADE)
    report_date = models.DateTimeField()
    report_data = models.JSONField()
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'maintenance_reports'
    
    def __str__(self):
        return f"Report for WO#{self.work_order.work_order_id}"

# Report Attachment model
class ReportAttachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(MaintenanceReport, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='report_attachments/')
    file_type = models.CharField(max_length=100, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'report_attachments'
    
    def __str__(self):
        return self.filename

# Inventory Category model
class InventoryCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'inventory_categories'
        verbose_name_plural = 'Inventory Categories'
    
    def __str__(self):
        return self.name

# Supplier model
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'suppliers'
    
    def __str__(self):
        return self.name

# Inventory Item model
class InventoryItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=100, null=True, blank=True)
    supplier_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'inventory_items'
    
    def __str__(self):
        return self.name

# Inventory Transaction model
class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'In'),
        ('OUT', 'Out'),
        ('ADJUST', 'Adjustment'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, db_column='item_id')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, null=True, blank=True, db_column='work_order_id')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_number = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    performed_by = models.CharField(max_length=100, null=True, blank=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        managed = False
        db_table = 'inventory_transactions'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.item.name} ({self.quantity})"

# Purchase Order model
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Ordered', 'Ordered'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    ]
    
    po_id = models.AutoField(primary_key=True)
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, db_column='supplier_id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(InventoryPersonnel, on_delete=models.SET_NULL, null=True, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'purchase_orders'
    
    def __str__(self):
        return self.po_number

# Purchase Order Item model
class PurchaseOrderItem(models.Model):
    po_item_id = models.AutoField(primary_key=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'purchase_order_items'
    
    def __str__(self):
        return f"{self.item.name} - {self.quantity}"
