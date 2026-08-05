# RBAC (Role-Based Access Control) Implementation Plan
## PSALMS Food Industries ICMS - Comprehensive Access Control System

---

## 1. Executive Summary

### 1.1 Overview
This document outlines the complete implementation plan for a configurable Role-Based Access Control (RBAC) system for the ICMS application. The system will enable administrators to define granular permissions for different roles and automatically enforce access control across the entire application.

### 1.2 Key Design Decisions
- **Hide vs Disable**: Unauthorized components will be **hidden** (not rendered)
- **Permission Templates**: Provide pre-configured role templates (Manager, Operator, Inspector, etc.)
- **Permission Inheritance**: Implement automatic permission inheritance (e.g., `edit` implies `view`)
- **User Overrides**: No user-specific permission overrides - permissions only at role level
- **Audit Logging**: Log all permission checks and access denial attempts

### 1.3 Core Principles
1. **Security by Default**: Deny access unless explicitly granted
2. **Least Privilege**: Users receive minimum permissions needed for their role
3. **Separation of Concerns**: Permission logic separated from business logic
4. **Configurability**: Admins can configure permissions via UI without code changes
5. **Performance**: Minimal overhead on component rendering and API calls
6. **Developer Experience**: Simple, intuitive API for checking permissions

---

## 2. Permission Structure

### 2.1 Permission Format
Permissions follow a hierarchical dot notation: `resource.action`

**Format**: `{resource}.{action}`
- **resource**: The entity or module (e.g., `equipment`, `inventory`, `production`)
- **action**: The operation (e.g., `view`, `create`, `edit`, `delete`)

**Examples**:
- `equipment.view` - View equipment list and details
- `equipment.create` - Create new equipment
- `equipment.edit` - Edit existing equipment
- `equipment.delete` - Delete equipment
- `inventory.transaction` - Create inventory transactions
- `reports.financial` - Access financial reports

### 2.2 Special Permissions
- `*` or `admin.full_access` - Full system access (superadmin)
- `dashboard.view` - Access to main dashboard
- `settings.roles` - Manage roles and permissions (admin function)

### 2.3 Permission Categories
Permissions are organized into logical categories for easier management:

1. **Dashboard**: `dashboard.*`
2. **Equipment Management**: `equipment.*`
3. **Inventory Management**: `inventory.*`
4. **Production Management**: `production.*`
5. **Quality Management**: `quality.*`
6. **Maintenance Management**: `maintenance.*`
7. **Work Orders**: `work_orders.*`
8. **Personnel Management**: `craftsmen.*`
9. **Reporting**: `reports.*`
10. **System Settings**: `settings.*`
11. **Administration**: `admin.*`

---

## 3. Complete Permission Registry

### 3.1 Dashboard Permissions
```typescript
{
  "dashboard.view": {
    "name": "View Dashboard",
    "description": "Access main dashboard and overview metrics",
    "category": "Dashboard",
    "implies": []
  }
}
```

### 3.2 Equipment Permissions
```typescript
{
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
  }
}
```

### 3.3 Inventory Permissions
```typescript
{
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
  }
}
```

### 3.4 Production Permissions
```typescript
{
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
  }
}
```

### 3.5 Quality Permissions
```typescript
{
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
  }
}
```

### 3.6 Maintenance Permissions
```typescript
{
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
  }
}
```


### 3.7 Work Order Permissions
```typescript
{
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
  }
}
```

### 3.8 Personnel (Craftsmen) Permissions
```typescript
{
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
  }
}
```

### 3.9 Reports Permissions
```typescript
{
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
  }
}
```

### 3.10 Settings Permissions
```typescript
{
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
  }
}
```

### 3.11 Administration Permissions
```typescript
{
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
  }
}
```

---

## 4. Permission Inheritance Rules

### 4.1 Inheritance Logic
When a permission is granted, all permissions in its `implies` array are automatically granted.

**Example Inheritance Chain**:
```
inventory.adjust
  → implies: inventory.view, inventory.transaction
    → inventory.transaction implies: inventory.view
```

**Result**: User with `inventory.adjust` automatically gets:
- `inventory.adjust`
- `inventory.transaction`
- `inventory.view`

### 4.2 Wildcard Permissions
- `*` or `admin.full_access` grants ALL permissions
- `equipment.*` grants all equipment-related permissions
- `{resource}.*` pattern grants all actions for a resource

### 4.3 Inheritance Implementation
```typescript
// Pseudo-code for permission resolution
function resolvePermissions(grantedPermissions: string[]): string[] {
  const resolved = new Set<string>(grantedPermissions);
  
  // Handle wildcards
  if (resolved.has('*') || resolved.has('admin.full_access')) {
    return getAllPermissions();
  }
  
  // Handle resource wildcards
  for (const perm of grantedPermissions) {
    if (perm.endsWith('.*')) {
      const resource = perm.split('.')[0];
      const resourcePerms = getPermissionsByResource(resource);
      resourcePerms.forEach(p => resolved.add(p));
    }
  }
  
  // Resolve implies
  for (const perm of grantedPermissions) {
    const definition = PERMISSION_REGISTRY[perm];
    if (definition?.implies) {
      definition.implies.forEach(implied => {
        resolved.add(implied);
        // Recursive resolution
        const impliedDef = PERMISSION_REGISTRY[implied];
        if (impliedDef?.implies) {
          impliedDef.implies.forEach(p => resolved.add(p));
        }
      });
    }
  }
  
  return Array.from(resolved);
}
```

---

## 5. Role Templates

### 5.1 Template Overview
Pre-configured permission sets for common roles to speed up role creation.

### 5.2 General Manager Template
**Role**: General Manager  
**Level**: 10  
**Category**: Management  
**Permissions**: 
```json
[
  "admin.full_access"
]
```
**Description**: Complete system access for top management

### 5.3 Production Manager Template
**Role**: Production Manager  
**Level**: 9  
**Category**: Management  
**Permissions**:
```json
[
  "dashboard.view",
  "production.*",
  "equipment.view",
  "equipment.assign",
  "inventory.view",
  "inventory.transaction",
  "quality.view",
  "maintenance.view",
  "work_orders.view",
  "work_orders.assign",
  "craftsmen.view",
  "reports.view",
  "reports.production",
  "reports.equipment",
  "reports.export"
]
```

### 5.4 Quality Manager Template
**Role**: Quality Manager  
**Level**: 9  
**Category**: Management  
**Permissions**:
```json
[
  "dashboard.view",
  "quality.*",
  "production.view",
  "inventory.view",
  "reports.view",
  "reports.quality",
  "reports.production",
  "reports.export",
  "craftsmen.view"
]
```

### 5.5 Maintenance Manager Template
**Role**: Maintenance Manager  
**Level**: 8  
**Category**: Management  
**Permissions**:
```json
[
  "dashboard.view",
  "maintenance.*",
  "work_orders.*",
  "equipment.*",
  "inventory.view",
  "inventory.transaction",
  "craftsmen.view",
  "reports.view",
  "reports.maintenance",
  "reports.equipment",
  "reports.export"
]
```

### 5.6 Production Team Leader Template
**Role**: Production Team Leader  
**Level**: 6  
**Category**: Supervision  
**Permissions**:
```json
[
  "dashboard.view",
  "production.view",
  "production.start",
  "production.complete",
  "production.packaging",
  "equipment.view",
  "inventory.view",
  "inventory.transaction",
  "quality.view",
  "work_orders.view",
  "craftsmen.view",
  "reports.view",
  "reports.production"
]
```

### 5.7 Maintenance Team Leader Template
**Role**: Maintenance Team Leader  
**Level**: 6  
**Category**: Supervision  
**Permissions**:
```json
[
  "dashboard.view",
  "maintenance.view",
  "maintenance.complete",
  "work_orders.view",
  "work_orders.complete",
  "equipment.view",
  "equipment.edit",
  "inventory.view",
  "inventory.transaction",
  "craftsmen.view",
  "reports.view",
  "reports.maintenance"
]
```

### 5.8 Quality Inspector Template
**Role**: Quality Inspector  
**Level**: 4  
**Category**: Technical  
**Permissions**:
```json
[
  "dashboard.view",
  "quality.view",
  "quality.inspect",
  "quality.ncr_create",
  "production.view",
  "inventory.view",
  "reports.view",
  "reports.quality"
]
```

### 5.9 Maintenance Technician Template
**Role**: Maintenance Technician  
**Level**: 4  
**Category**: Technical  
**Permissions**:
```json
[
  "dashboard.view",
  "maintenance.view",
  "maintenance.complete",
  "work_orders.view",
  "work_orders.complete",
  "equipment.view",
  "inventory.view",
  "inventory.transaction"
]
```

### 5.10 Machine Operator Template
**Role**: Machine Operator  
**Level**: 3  
**Category**: Operations  
**Permissions**:
```json
[
  "dashboard.view",
  "production.view",
  "production.start",
  "production.complete",
  "equipment.view",
  "inventory.view",
  "quality.view",
  "work_orders.view"
]
```

### 5.11 Inventory Clerk Template
**Role**: Inventory Clerk  
**Level**: 3  
**Category**: Operations  
**Permissions**:
```json
[
  "dashboard.view",
  "inventory.*",
  "production.view",
  "reports.view",
  "reports.inventory"
]
```

### 5.12 General Worker Template
**Role**: General Worker  
**Level**: 2  
**Category**: Operations  
**Permissions**:
```json
[
  "dashboard.view",
  "production.view",
  "equipment.view",
  "inventory.view",
  "work_orders.view"
]
```

---

## 6. JSON Schema for Permissions Storage

### 6.1 Database Storage Format
Permissions are stored in the `roles.permissions_json` field as a JSON string:

```json
{
  "version": "1.0",
  "permissions": [
    "dashboard.view",
    "equipment.view",
    "equipment.create",
    "equipment.edit",
    "inventory.view",
    "inventory.transaction"
  ],
  "template": "production_manager",
  "custom": false,
  "last_modified": "2026-08-04T10:30:00Z"
}
```

### 6.2 Schema Definition
```typescript
interface PermissionsConfig {
  version: string;              // Schema version for future migrations
  permissions: string[];        // Array of permission strings
  template?: string;            // Template used (if any)
  custom: boolean;             // true if modified from template
  last_modified: string;       // ISO timestamp
}
```

---

## 7. Backend Implementation

### 7.1 Required Changes

#### 7.1.1 Models (Backend/models/company.py)
```python
# Role model already has permissions_json field - NO CHANGES NEEDED
# Add helper method to parse permissions

from typing import List, Dict
import json

class Role(Base, BaseModel):
    # ... existing fields ...
    
    def get_permissions(self) -> List[str]:
        """Parse and return permissions from JSON."""
        if not self.permissions_json:
            return []
        try:
            data = json.loads(self.permissions_json)
            return data.get('permissions', [])
        except:
            return []
    
    def set_permissions(self, permissions: List[str], template: str = None, custom: bool = False):
        """Set permissions JSON."""
        from datetime import datetime
        config = {
            "version": "1.0",
            "permissions": permissions,
            "template": template,
            "custom": custom,
            "last_modified": datetime.utcnow().isoformat()
        }
        self.permissions_json = json.dumps(config)
```


#### 7.1.2 Schemas (Backend/schemas/role.py)
```python
from pydantic import BaseModel, validator
from typing import Optional, List

# Add new schemas for permission management

class PermissionsConfig(BaseModel):
    """Permission configuration schema."""
    version: str = "1.0"
    permissions: List[str]
    template: Optional[str] = None
    custom: bool = False
    last_modified: str

class RolePermissionsUpdate(BaseModel):
    """Schema for updating role permissions."""
    permissions: List[str]
    template: Optional[str] = None
    custom: bool = False
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permission format."""
        for perm in v:
            if not perm or '.' not in perm:
                raise ValueError(f"Invalid permission format: {perm}")
        return v

class RoleWithPermissions(RoleResponse):
    """Role response with parsed permissions."""
    parsed_permissions: List[str]

class PermissionDefinition(BaseModel):
    """Individual permission definition."""
    key: str
    name: str
    description: str
    category: str
    implies: List[str] = []

class PermissionRegistry(BaseModel):
    """Complete permission registry."""
    permissions: List[PermissionDefinition]
    categories: List[str]
```

#### 7.1.3 Services (Backend/services/company_service.py)
```python
# Add permission-related services

def get_role_with_permissions(db: Session, role_id: int) -> Optional[dict]:
    """Get role with parsed permissions."""
    role = get_role(db, role_id)
    if not role:
        return None
    
    return {
        **role.__dict__,
        "parsed_permissions": role.get_permissions()
    }

def update_role_permissions(
    db: Session, 
    role_id: int, 
    permissions: List[str],
    template: str = None,
    custom: bool = False
) -> Optional[Role]:
    """Update role permissions."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Prevent modifying system roles
    if db_role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify permissions of system roles"
        )
    
    db_role.set_permissions(permissions, template, custom)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_role_from_template(
    db: Session,
    name: str,
    template: str,
    template_permissions: List[str],
    description: str = None,
    level: int = 1,
    category: str = None
) -> Role:
    """Create a new role from a template."""
    # Check uniqueness
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    # Create role
    db_role = Role(
        name=name,
        description=description,
        level=level,
        category=category,
        is_active=True,
        is_system_role=False
    )
    db_role.set_permissions(template_permissions, template=template, custom=False)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
```

#### 7.1.4 API Endpoints (Backend/api/v1/company.py)
```python
# Add new permission-related endpoints

from schemas.role import (
    RolePermissionsUpdate, 
    RoleWithPermissions,
    PermissionRegistry,
    PermissionDefinition
)

@router.get("/roles/{role_id}/permissions", response_model=RoleWithPermissions)
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get role with parsed permissions."""
    role_data = company_service.get_role_with_permissions(db, role_id)
    if not role_data:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_data

@router.put("/roles/{role_id}/permissions", response_model=RoleWithPermissions)
async def update_role_permissions(
    role_id: int,
    permissions_update: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update role permissions."""
    updated = company_service.update_role_permissions(
        db, 
        role_id, 
        permissions_update.permissions,
        permissions_update.template,
        permissions_update.custom
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {
        **updated.__dict__,
        "parsed_permissions": updated.get_permissions()
    }

@router.get("/permissions/registry", response_model=PermissionRegistry)
async def get_permission_registry(
    current_user: User = Depends(get_current_active_user)
):
    """Get complete permission registry."""
    # This will be populated from a static registry file
    from core.permissions import get_permission_registry
    return get_permission_registry()

@router.get("/permissions/templates")
async def get_permission_templates(
    current_user: User = Depends(get_current_active_user)
):
    """Get available role templates."""
    from core.permissions import get_role_templates
    return get_role_templates()

@router.post("/roles/from-template", response_model=RoleResponse)
async def create_role_from_template(
    name: str,
    template: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new role from a template."""
    from core.permissions import get_template_permissions, get_template_metadata
    
    template_perms = get_template_permissions(template)
    if not template_perms:
        raise HTTPException(status_code=404, detail="Template not found")
    
    metadata = get_template_metadata(template)
    
    return company_service.create_role_from_template(
        db,
        name=name,
        template=template,
        template_permissions=template_perms,
        description=description or metadata.get('description'),
        level=metadata.get('level', 1),
        category=metadata.get('category')
    )
```

#### 7.1.5 Permission Registry Module (Backend/core/permissions.py)
```python
# NEW FILE: Backend/core/permissions.py
"""
Central permission registry and template definitions.
"""

from typing import List, Dict, Optional

# Complete permission definitions
PERMISSION_REGISTRY = {
    # Dashboard
    "dashboard.view": {
        "name": "View Dashboard",
        "description": "Access main dashboard and overview metrics",
        "category": "Dashboard",
        "implies": []
    },
    
    # Equipment
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
    
    # Inventory
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
        "description": "Record inventory transactions",
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
    
    # Production
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
    
    # Quality
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
    
    # Continue with remaining permissions...
    # (Maintenance, Work Orders, Craftsmen, Reports, Settings, Admin)
}

# Role templates
ROLE_TEMPLATES = {
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
    # Add remaining templates...
}

def get_permission_registry() -> Dict:
    """Return the complete permission registry."""
    categories = list(set(p["category"] for p in PERMISSION_REGISTRY.values()))
    permissions = [
        {"key": key, **value}
        for key, value in PERMISSION_REGISTRY.items()
    ]
    return {
        "permissions": permissions,
        "categories": sorted(categories)
    }

def get_role_templates() -> Dict:
    """Return available role templates."""
    return ROLE_TEMPLATES

def get_template_permissions(template_key: str) -> Optional[List[str]]:
    """Get permissions for a specific template."""
    template = ROLE_TEMPLATES.get(template_key)
    return template["permissions"] if template else None

def get_template_metadata(template_key: str) -> Dict:
    """Get metadata for a template."""
    return ROLE_TEMPLATES.get(template_key, {})

def resolve_permissions(granted_permissions: List[str]) -> List[str]:
    """
    Resolve permissions with inheritance.
    Returns complete list including implied permissions.
    """
    resolved = set()
    
    # Handle full access
    if "*" in granted_permissions or "admin.full_access" in granted_permissions:
        return list(PERMISSION_REGISTRY.keys())
    
    # Handle wildcards
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
    
    # Resolve implies recursively
    to_process = list(resolved)
    while to_process:
        current = to_process.pop()
        if current in PERMISSION_REGISTRY:
            implies = PERMISSION_REGISTRY[current].get("implies", [])
            for implied in implies:
                if implied not in resolved:
                    resolved.add(implied)
                    to_process.append(implied)
    
    return list(resolved)
```

---

## 8. Frontend Implementation

### 8.1 File Structure
```
icms-web/src/
├── config/
│   └── permissions.ts          # Permission registry (TypeScript version)
├── hooks/
│   ├── usePermission.ts        # Main permission hook
│   ├── useHasAnyPermission.ts  # Check any of multiple permissions
│   └── useHasAllPermissions.ts # Check all permissions
├── components/
│   ├── auth/
│   │   ├── ProtectedRoute.tsx  # Route wrapper
│   │   ├── ProtectedButton.tsx # Button wrapper
│   │   └── ProtectedSection.tsx# Section wrapper
│   └── settings/
│       ├── RoleManagement.tsx  # Role CRUD interface
│       └── PermissionEditor.tsx# Permission configuration UI
├── services/
│   └── permissions.service.ts  # API calls for permissions
├── store/
│   └── authStore.ts           # Add permission methods
└── types/
    └── permissions.ts         # Permission types
```

### 8.2 Permission Types (icms-web/src/types/permissions.ts)
```typescript
export type Permission = string;

export interface PermissionDefinition {
  key: string;
  name: string;
  description: string;
  category: string;
  implies: string[];
}

export interface PermissionRegistry {
  permissions: PermissionDefinition[];
  categories: string[];
}

export interface PermissionsConfig {
  version: string;
  permissions: Permission[];
  template?: string;
  custom: boolean;
  last_modified: string;
}

export interface RoleTemplate {
  name: string;
  description: string;
  level: number;
  category: string;
  permissions: Permission[];
}

export interface RoleWithPermissions {
  id: number;
  name: string;
  description: string;
  level: number;
  category: string;
  permissions_json: string;
  parsed_permissions: Permission[];
  is_active: boolean;
  is_system_role: boolean;
  created_at: string;
  updated_at: string;
}
```
