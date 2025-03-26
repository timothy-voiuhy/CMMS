from django.contrib import admin
from .models import (
    User, Craftsman, InventoryPersonnel, Equipment, WorkOrder, 
    MaintenanceReport, ReportAttachment, InventoryCategory, 
    Supplier, InventoryItem, InventoryTransaction,
    PurchaseOrder, PurchaseOrderItem
)

# Register models to admin site
admin.site.register(User)
admin.site.register(Craftsman)
admin.site.register(InventoryPersonnel)
admin.site.register(Equipment)
admin.site.register(WorkOrder)
admin.site.register(MaintenanceReport)
admin.site.register(ReportAttachment)
admin.site.register(InventoryCategory)
admin.site.register(Supplier)
admin.site.register(InventoryItem)
admin.site.register(InventoryTransaction)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
