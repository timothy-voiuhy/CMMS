from django.urls import path, re_path
from django.shortcuts import redirect
from django.http import Http404
from . import views

urlpatterns = [
    # Main routes
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('craftsmen/logout/', views.craftsmen_logout_view, name='craftsmen_logout'),
    path('craftsmen/dashboard/', views.craftsmen_dashboard, name='craftsmen_dashboard'),

    # Work order routes
    path('craftsmen/work_orders/', views.craftsmen_work_orders, name='craftsmen_work_orders'),
    path('craftsmen/view_work_order/<int:work_order_id>/', views.craftsmen_view_work_order, name='craftsmen_view_work_order'),
    path('update_work_order_status/<int:work_order_id>/', views.craftsmen_update_work_order_status, name='craftsmen_update_work_order_status'),
    
    # Maintenance report routes
    path('craftsmen/add_report/<int:work_order_id>/', views.craftsmen_add_report, name='craftsmen_add_report'),
    path('craftsmen/view_report/<int:report_id>/', views.craftsmen_view_report, name='craftsmen_view_report'),
    path('craftsmen/print_report/<int:report_id>/', views.craftsmen_print_report, name='craftsmen_print_report'),
    path('craftsmen/download_attachment/<int:attachment_id>/', views.craftsmen_download_attachment, name='craftsmen_download_attachment'),
    
    # Maintenance history
    path('craftsmen/maintenance_history/', views.craftsmen_maintenance_history, name='craftsmen_maintenance_history'),
    
    # Skills and notifications
    path('craftsmen/skills/', views.craftsmen_skills, name='craftsmen_skills'),
    path('craftsmen/notifications/', views.craftsmen_notifications, name='craftsmen_notifications'),
    
    # Inventory management routes
    path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/items/', views.inventory_items, name='inventory_items'),
    path('inventory/purchase_orders/', views.purchase_orders, name='purchase_orders'),
    path('inventory/reports/', views.inventory_reports, name='inventory_reports'),
    path('inventory/item/<int:item_id>/', views.item_details, name='item_details'),
    path('inventory/edit_item/<int:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/add_item/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/save_item/', views.save_inventory_item, name='save_inventory_item'),
    path('inventory/update_quantity/<int:item_id>/', views.update_item_quantity, name='update_item_quantity'),
    path('inventory/create_purchase_order/', views.create_purchase_order, name='create_purchase_order'),
    path('inventory/purchase_order/<int:po_id>/', views.view_purchase_order, name='view_purchase_order'),
    path('inventory/receive_purchase_order/<int:po_id>/', views.receive_purchase_order, name='receive_purchase_order'),
    path('inventory/notifications/', views.inventory_notifications, name='inventory_notifications'),
    path('inventory/delete_item/', views.delete_inventory_item, name='delete_inventory_item'),
    path('receive-items/', views.receive_items, name='receive_items'),
    path('export-purchase-orders/', views.export_purchase_orders, name='export_purchase_orders'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('inventory/import/', views.import_items, name='import_items'),
    path('inventory/export/', views.export_items, name='export_items'),
    # API routes for mobile app integration
    path('api/login/', views.api_login, name='api_login'),
    path('api/work_orders/<int:craftsman_id>/', views.api_work_orders, name='api_work_orders'),

    # other paths that redirect to login
    path('craftsmen/', views.craftsmen, name='craftsmen'),
    path('inventory/', views.inventory, name='inventory'),

    # Add this to your urlpatterns
    path('craftsmen/equipment/', views.craftsmen_equipment, name='craftsmen_equipment'),
    path('craftsmen/profile/', views.craftsmen_profile, name='craftsmen_profile'),
] 

def redirect_to_login_or_404(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        raise Http404("Page not found")

urlpatterns += [re_path(r'^.*$', redirect_to_login_or_404), ]