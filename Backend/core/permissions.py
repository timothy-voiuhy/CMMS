"""
Central permission registry and template definitions for RBAC.
Single source of truth for all permission definitions, role templates,
and permission resolution logic.
"""

from typing import List, Dict, Optional, Set


# ==================== PERMISSION REGISTRY ====================
# Complete permission definitions with inheritance chains

PERMISSION_REGISTRY: Dict[str, Dict] = {
    # ---- Dashboard ----
    "dashboard.view": {
        "name": "View Dashboard",
        "description": "Access main dashboard and overview metrics",
        "category": "Dashboard",
        "implies": []
    },

    # ---- Equipment ----
    "equipment.view": {
        "name": "View Equipment",
        "description": "View equipment list and details",
        "category": "Equipment",
        "implies": []
    },
    "equipment.create": {
        "name": "Create Equipment",
        "description": "Add new equipment to the system",
        "category": "Equipment",
        "implies": ["equipment.view"]
    },
    "equipment.edit": {
        "name": "Edit Equipment",
        "description": "Modify existing equipment details",
        "category": "Equipment",
        "implies": ["equipment.view"]
    },
    "equipment.delete": {
        "name": "Delete Equipment",
        "description": "Remove equipment from the system",
        "category": "Equipment",
        "implies": ["equipment.view"]
    },
    "equipment.assign": {
        "name": "Assign Equipment",
        "description": "Assign equipment to craftsmen or work orders",
        "category": "Equipment",
        "implies": ["equipment.view"]
    },

    # ---- Inventory ----
    "inventory.view": {
        "name": "View Inventory",
        "description": "View inventory items and stock levels",
        "category": "Inventory",
        "implies": []
    },
    "inventory.create": {
        "name": "Create Inventory Items",
        "description": "Add new inventory items",
        "category": "Inventory",
        "implies": ["inventory.view"]
    },
    "inventory.edit": {
        "name": "Edit Inventory Items",
        "description": "Modify inventory item details",
        "category": "Inventory",
        "implies": ["inventory.view"]
    },
    "inventory.delete": {
        "name": "Delete Inventory Items",
        "description": "Remove inventory items",
        "category": "Inventory",
        "implies": ["inventory.view"]
    },
    "inventory.transaction": {
        "name": "Create Transactions",
        "description": "Record inventory transactions (in/out/transfer)",
        "category": "Inventory",
        "implies": ["inventory.view"]
    },
    "inventory.adjust": {
        "name": "Adjust Stock Levels",
        "description": "Perform manual stock adjustments",
        "category": "Inventory",
        "implies": ["inventory.view", "inventory.transaction"]
    },
    "inventory.categories": {
        "name": "Manage Categories",
        "description": "Create and manage inventory categories",
        "category": "Inventory",
        "implies": ["inventory.view"]
    },

    # ---- Production ----
    "production.view": {
        "name": "View Production",
        "description": "View production lines, orders, and packaging",
        "category": "Production",
        "implies": []
    },
    "production.create": {
        "name": "Create Production Orders",
        "description": "Create new production orders",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.edit": {
        "name": "Edit Production Orders",
        "description": "Modify production order details",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.delete": {
        "name": "Delete Production Orders",
        "description": "Remove production orders",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.start": {
        "name": "Start Production",
        "description": "Start production orders and lines",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.complete": {
        "name": "Complete Production",
        "description": "Mark production orders as completed",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.lines": {
        "name": "Manage Production Lines",
        "description": "Create and configure production lines",
        "category": "Production",
        "implies": ["production.view"]
    },
    "production.packaging": {
        "name": "Manage Packaging",
        "description": "Access and manage packaging operations",
        "category": "Production",
        "implies": ["production.view"]
    },

    # ---- Quality ----
    "quality.view": {
        "name": "View Quality Records",
        "description": "View quality inspections and NCRs",
        "category": "Quality",
        "implies": []
    },
    "quality.inspect": {
        "name": "Perform Inspections",
        "description": "Create and complete quality inspections",
        "category": "Quality",
        "implies": ["quality.view"]
    },
    "quality.ncr_create": {
        "name": "Create NCRs",
        "description": "Create Non-Conformance Reports",
        "category": "Quality",
        "implies": ["quality.view"]
    },
    "quality.ncr_close": {
        "name": "Close NCRs",
        "description": "Review and close Non-Conformance Reports",
        "category": "Quality",
        "implies": ["quality.view", "quality.ncr_create"]
    },
    "quality.approve": {
        "name": "Approve Quality Records",
        "description": "Approve quality inspections and reports",
        "category": "Quality",
        "implies": ["quality.view"]
    },

    # ---- Maintenance ----
    "maintenance.view": {
        "name": "View Maintenance",
        "description": "View maintenance schedules and reports",
        "category": "Maintenance",
        "implies": []
    },
    "maintenance.create": {
        "name": "Create Maintenance Records",
        "description": "Create maintenance schedules and reports",
        "category": "Maintenance",
        "implies": ["maintenance.view"]
    },
    "maintenance.edit": {
        "name": "Edit Maintenance Records",
        "description": "Modify maintenance records",
        "category": "Maintenance",
        "implies": ["maintenance.view"]
    },
    "maintenance.complete": {
        "name": "Complete Maintenance",
        "description": "Mark maintenance tasks as completed",
        "category": "Maintenance",
        "implies": ["maintenance.view"]
    },
    "maintenance.schedule": {
        "name": "Schedule Maintenance",
        "description": "Create and modify maintenance schedules",
        "category": "Maintenance",
        "implies": ["maintenance.view", "maintenance.create"]
    },

    # ---- Work Orders ----
    "work_orders.view": {
        "name": "View Work Orders",
        "description": "View work order list and details",
        "category": "Work Orders",
        "implies": []
    },
    "work_orders.create": {
        "name": "Create Work Orders",
        "description": "Create new work orders",
        "category": "Work Orders",
        "implies": ["work_orders.view"]
    },
    "work_orders.assign": {
        "name": "Assign Work Orders",
        "description": "Assign work orders to craftsmen",
        "category": "Work Orders",
        "implies": ["work_orders.view"]
    },
    "work_orders.complete": {
        "name": "Complete Work Orders",
        "description": "Mark work orders as completed",
        "category": "Work Orders",
        "implies": ["work_orders.view"]
    },
    "work_orders.edit": {
        "name": "Edit Work Orders",
        "description": "Modify work order details",
        "category": "Work Orders",
        "implies": ["work_orders.view"]
    },
    "work_orders.delete": {
        "name": "Delete Work Orders",
        "description": "Remove work orders",
        "category": "Work Orders",
        "implies": ["work_orders.view"]
    },

    # ---- Personnel (Craftsmen) ----
    "craftsmen.view": {
        "name": "View Craftsmen",
        "description": "View craftsmen list and profiles",
        "category": "Personnel",
        "implies": []
    },
    "craftsmen.create": {
        "name": "Create Craftsmen",
        "description": "Add new craftsmen to the system",
        "category": "Personnel",
        "implies": ["craftsmen.view"]
    },
    "craftsmen.edit": {
        "name": "Edit Craftsmen",
        "description": "Modify craftsmen details",
        "category": "Personnel",
        "implies": ["craftsmen.view"]
    },
    "craftsmen.delete": {
        "name": "Delete Craftsmen",
        "description": "Remove craftsmen from the system",
        "category": "Personnel",
        "implies": ["craftsmen.view"]
    },
    "craftsmen.assign_role": {
        "name": "Assign Roles",
        "description": "Assign roles to craftsmen",
        "category": "Personnel",
        "implies": ["craftsmen.view", "craftsmen.edit"]
    },

    # ---- Reports ----
    "reports.view": {
        "name": "View Reports",
        "description": "Access basic reporting dashboard",
        "category": "Reports",
        "implies": []
    },
    "reports.equipment": {
        "name": "Equipment Reports",
        "description": "View equipment-related reports",
        "category": "Reports",
        "implies": ["reports.view", "equipment.view"]
    },
    "reports.maintenance": {
        "name": "Maintenance Reports",
        "description": "View maintenance reports",
        "category": "Reports",
        "implies": ["reports.view", "maintenance.view"]
    },
    "reports.inventory": {
        "name": "Inventory Reports",
        "description": "View inventory reports",
        "category": "Reports",
        "implies": ["reports.view", "inventory.view"]
    },
    "reports.production": {
        "name": "Production Reports",
        "description": "View production reports",
        "category": "Reports",
        "implies": ["reports.view", "production.view"]
    },
    "reports.quality": {
        "name": "Quality Reports",
        "description": "View quality reports",
        "category": "Reports",
        "implies": ["reports.view", "quality.view"]
    },
    "reports.financial": {
        "name": "Financial Reports",
        "description": "View financial and cost reports",
        "category": "Reports",
        "implies": ["reports.view"]
    },
    "reports.export": {
        "name": "Export Reports",
        "description": "Export reports to PDF/Excel",
        "category": "Reports",
        "implies": ["reports.view"]
    },

    # ---- Settings ----
    "settings.view": {
        "name": "View Settings",
        "description": "Access settings page",
        "category": "Settings",
        "implies": []
    },
    "settings.company": {
        "name": "Manage Company Settings",
        "description": "Edit company profile and preferences",
        "category": "Settings",
        "implies": ["settings.view"]
    },
    "settings.users": {
        "name": "Manage Users",
        "description": "Create and manage user accounts",
        "category": "Settings",
        "implies": ["settings.view"]
    },
    "settings.roles": {
        "name": "Manage Roles",
        "description": "Create and configure roles and permissions",
        "category": "Settings",
        "implies": ["settings.view"]
    },
    "settings.facilities": {
        "name": "Manage Facilities",
        "description": "Manage facilities and departments",
        "category": "Settings",
        "implies": ["settings.view"]
    },
    "settings.system": {
        "name": "System Settings",
        "description": "Configure system-wide settings",
        "category": "Settings",
        "implies": ["settings.view"]
    },

    # ---- Administration ----
    "admin.full_access": {
        "name": "Full System Access",
        "description": "Complete access to all system features",
        "category": "Administration",
        "implies": ["*"]
    },
    "admin.audit_logs": {
        "name": "View Audit Logs",
        "description": "Access system audit logs",
        "category": "Administration",
        "implies": []
    },
    "admin.backup": {
        "name": "Backup Management",
        "description": "Perform system backups and restores",
        "category": "Administration",
        "implies": []
    },
}


# ==================== ROLE TEMPLATES ====================

ROLE_TEMPLATES: Dict[str, Dict] = {
    "general_manager": {
        "name": "General Manager",
        "description": "Complete system access for top management",
        "level": 10,
        "category": "Management",
        "permissions": ["admin.full_access"]
    },
    "production_manager": {
        "name": "Production Manager",
        "description": "Manages production operations",
        "level": 9,
        "category": "Management",
        "permissions": [
            "dashboard.view",
            "production.*",
            "equipment.view", "equipment.assign",
            "inventory.view", "inventory.transaction",
            "quality.view",
            "maintenance.view",
            "work_orders.view", "work_orders.assign",
            "craftsmen.view",
            "reports.view", "reports.production", "reports.equipment", "reports.export"
        ]
    },
    "quality_manager": {
        "name": "Quality Manager",
        "description": "Manages quality assurance operations",
        "level": 9,
        "category": "Management",
        "permissions": [
            "dashboard.view",
            "quality.*",
            "production.view",
            "inventory.view",
            "reports.view", "reports.quality", "reports.production", "reports.export",
            "craftsmen.view"
        ]
    },
    "maintenance_manager": {
        "name": "Maintenance Manager",
        "description": "Manages maintenance operations",
        "level": 8,
        "category": "Management",
        "permissions": [
            "dashboard.view",
            "maintenance.*",
            "work_orders.*",
            "equipment.*",
            "inventory.view", "inventory.transaction",
            "craftsmen.view",
            "reports.view", "reports.maintenance", "reports.equipment", "reports.export"
        ]
    },
    "production_team_leader": {
        "name": "Production Team Leader",
        "description": "Supervises production team",
        "level": 6,
        "category": "Supervision",
        "permissions": [
            "dashboard.view",
            "production.view", "production.start", "production.complete", "production.packaging",
            "equipment.view",
            "inventory.view", "inventory.transaction",
            "quality.view",
            "work_orders.view",
            "craftsmen.view",
            "reports.view", "reports.production"
        ]
    },
    "maintenance_team_leader": {
        "name": "Maintenance Team Leader",
        "description": "Supervises maintenance team",
        "level": 6,
        "category": "Supervision",
        "permissions": [
            "dashboard.view",
            "maintenance.view", "maintenance.complete",
            "work_orders.view", "work_orders.complete",
            "equipment.view", "equipment.edit",
            "inventory.view", "inventory.transaction",
            "craftsmen.view",
            "reports.view", "reports.maintenance"
        ]
    },
    "quality_inspector": {
        "name": "Quality Inspector",
        "description": "Performs quality inspections",
        "level": 4,
        "category": "Technical",
        "permissions": [
            "dashboard.view",
            "quality.view", "quality.inspect", "quality.ncr_create",
            "production.view",
            "inventory.view",
            "reports.view", "reports.quality"
        ]
    },
    "maintenance_technician": {
        "name": "Maintenance Technician",
        "description": "Performs maintenance work",
        "level": 4,
        "category": "Technical",
        "permissions": [
            "dashboard.view",
            "maintenance.view", "maintenance.complete",
            "work_orders.view", "work_orders.complete",
            "equipment.view",
            "inventory.view", "inventory.transaction"
        ]
    },
    "machine_operator": {
        "name": "Machine Operator",
        "description": "Operates production machinery",
        "level": 3,
        "category": "Operations",
        "permissions": [
            "dashboard.view",
            "production.view", "production.start", "production.complete",
            "equipment.view",
            "inventory.view",
            "quality.view",
            "work_orders.view"
        ]
    },
    "inventory_clerk": {
        "name": "Inventory Clerk",
        "description": "Manages inventory operations",
        "level": 3,
        "category": "Operations",
        "permissions": [
            "dashboard.view",
            "inventory.*",
            "production.view",
            "reports.view", "reports.inventory"
        ]
    },
    "general_worker": {
        "name": "General Worker",
        "description": "Basic view-only access",
        "level": 2,
        "category": "Operations",
        "permissions": [
            "dashboard.view",
            "production.view",
            "equipment.view",
            "inventory.view",
            "work_orders.view"
        ]
    },
    "admin": {
        "name": "System Administrator",
        "description": "Full system and settings access",
        "level": 10,
        "category": "Administration",
        "permissions": [
            "admin.full_access",
            "settings.*"
        ]
    },
}


# ==================== PERMISSION RESOLUTION ====================

def resolve_permissions(granted_permissions: List[str]) -> List[str]:
    """
    Resolve permissions with inheritance and wildcards.
    Returns the complete list of effective permissions including all implied ones.
    """
    resolved: Set[str] = set()

    # Handle full access
    if "*" in granted_permissions or "admin.full_access" in granted_permissions:
        return list(PERMISSION_REGISTRY.keys())

    # Handle wildcards (e.g., "equipment.*")
    for perm in granted_permissions:
        if perm.endswith(".*"):
            resource = perm.split(".")[0]
            resource_perms = [
                key for key in PERMISSION_REGISTRY.keys()
                if key.startswith(f"{resource}.")
            ]
            resolved.update(resource_perms)
        else:
            resolved.add(perm)

    # Resolve implies recursively using a processing queue
    to_process = list(resolved)
    while to_process:
        current = to_process.pop()
        if current in PERMISSION_REGISTRY:
            implies = PERMISSION_REGISTRY[current].get("implies", [])
            for implied in implies:
                if implied == "*":
                    # This permission implies full access
                    return list(PERMISSION_REGISTRY.keys())
                if implied not in resolved:
                    resolved.add(implied)
                    to_process.append(implied)

    return sorted(resolved)


# ==================== HELPER FUNCTIONS ====================

def get_permission_registry() -> Dict:
    """Return the complete permission registry formatted for API response."""
    categories = sorted(set(p["category"] for p in PERMISSION_REGISTRY.values()))
    permissions = [
        {"key": key, **value}
        for key, value in PERMISSION_REGISTRY.items()
    ]
    return {
        "permissions": permissions,
        "categories": categories
    }


def get_role_templates() -> Dict:
    """Return available role templates."""
    return ROLE_TEMPLATES


def get_template_permissions(template_key: str) -> Optional[List[str]]:
    """Get permissions for a specific template."""
    template = ROLE_TEMPLATES.get(template_key)
    return template["permissions"] if template else None


def get_template_metadata(template_key: str) -> Dict:
    """Get metadata for a template (name, description, level, category)."""
    template = ROLE_TEMPLATES.get(template_key, {})
    return {
        "name": template.get("name", ""),
        "description": template.get("description", ""),
        "level": template.get("level", 1),
        "category": template.get("category", ""),
    }


def get_all_permission_keys() -> List[str]:
    """Return all registered permission keys."""
    return sorted(PERMISSION_REGISTRY.keys())


def get_permissions_by_category() -> Dict[str, List[Dict]]:
    """Group permissions by their category."""
    grouped: Dict[str, List[Dict]] = {}
    for key, value in PERMISSION_REGISTRY.items():
        category = value["category"]
        if category not in grouped:
            grouped[category] = []
        grouped[category].append({"key": key, **value})
    return grouped
