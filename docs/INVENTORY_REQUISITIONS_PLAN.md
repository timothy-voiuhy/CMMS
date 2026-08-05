# Inventory Requisitions Feature Plan

## Current Architecture Snapshot

The active system has two main parts:

- `Backend`: FastAPI application using SQLAlchemy models, Pydantic schemas, service modules, and API routers under `Backend/api/v1`.
- `icms-web`: Vite React application using typed service classes, React Router pages, Tailwind styling, lucide icons, and client-side permission guards.

The active inventory module currently supports:

- Hierarchical categories through `InventoryCategory`.
- Stock items through `InventoryItem`.
- Quantity movements through `InventoryTransaction`.
- Backend API routes under `/api/v1/inventory`.
- Frontend pages for list, grid, item form, item detail, and category management.

Relevant active files:

- `Backend/models/inventory.py`
- `Backend/schemas/inventory.py`
- `Backend/services/inventory_service.py`
- `Backend/api/v1/inventory.py`
- `icms-web/src/services/inventory.service.ts`
- `icms-web/src/pages/inventory/*`
- `icms-web/src/App.tsx`
- `icms-web/src/components/common/Sidebar.tsx`
- `Backend/core/permissions.py`
- `icms-web/src/config/permissions.ts`

Legacy code under `Deprecated/Desktop` contains purchase order concepts, but the active backend does not currently expose purchase orders or requisitions. Treat the legacy code as historical reference only.

## Feature Goal

Add inventory requisitions so departments, maintenance users, production users, or other authorized staff can request stock items before inventory staff issue the materials.

The feature should separate "requesting stock" from "moving stock":

- Creating or approving a requisition must not change `InventoryItem.quantity`.
- Fulfillment should create `InventoryTransaction` records and decrement stock using the same rules as existing issue transactions.
- The requisition should preserve an audit trail of requester, approver, fulfiller, dates, line items, and status.

## Recommended Workflow

1. Requester creates a draft requisition with one or more inventory items.
2. Requester submits the requisition.
3. Approver approves or rejects the requisition.
4. Inventory staff fulfills approved lines partially or fully.
5. System records stock issue transactions during fulfillment.
6. Requisition closes automatically when all lines are fully fulfilled, or can be cancelled before fulfillment.

Recommended statuses:

- `draft`
- `submitted`
- `approved`
- `rejected`
- `partially_fulfilled`
- `fulfilled`
- `cancelled`

Recommended line statuses:

- `pending`
- `approved`
- `partially_fulfilled`
- `fulfilled`
- `rejected`
- `cancelled`

## Backend Design

### Models

Add two SQLAlchemy models in `Backend/models/inventory.py`.

`InventoryRequisition`:

- `requisition_number`: unique indexed string, for example `REQ-2026-00001`
- `title`: short request title
- `description`: optional details
- `status`: enum
- `priority`: enum or string aligned with existing priority concepts
- `needed_by`: optional date string, matching current codebase date-string style
- `department`: optional string
- `work_order_id`: optional FK to `work_orders.id`
- `production_order_id`: optional FK to `production_orders.id`
- `requested_by`: FK to `users.id`
- `approved_by`: optional FK to `users.id`
- `approved_at`: optional datetime
- `fulfilled_by`: optional FK to `users.id`
- `fulfilled_at`: optional datetime
- `rejection_reason`: optional text
- `notes`: optional text

`InventoryRequisitionItem`:

- `requisition_id`: FK to `inventory_requisitions.id`
- `item_id`: FK to `inventory_items.id`
- `requested_quantity`: float
- `approved_quantity`: nullable float
- `fulfilled_quantity`: float default `0`
- `unit_of_measure`: string snapshot from item
- `notes`: optional text
- `status`: line status enum

Relationships:

- `InventoryRequisition.items`
- `InventoryRequisitionItem.requisition`
- `InventoryRequisitionItem.item`
- Optional relationships to `WorkOrder`, `ProductionOrder`, and `User`.

### Schemas

Add Pydantic schemas in `Backend/schemas/inventory.py`:

- `InventoryRequisitionItemCreate`
- `InventoryRequisitionItemUpdate`
- `InventoryRequisitionItemResponse`
- `InventoryRequisitionCreate`
- `InventoryRequisitionUpdate`
- `InventoryRequisitionResponse`
- `InventoryRequisitionListResponse`
- `InventoryRequisitionApprovalRequest`
- `InventoryRequisitionFulfillmentLine`
- `InventoryRequisitionFulfillmentRequest`
- `InventoryRequisitionRejectRequest`

Responses should include item details needed by the UI, preferably item code/name/unit/current quantity through nested item fields.

### Service Layer

Extend `Backend/services/inventory_service.py` with requisition functions:

- `get_requisition_count(db, filters)`
- `get_requisitions(db, skip, limit, filters)`
- `get_requisition(db, requisition_id)`
- `create_requisition(db, payload, current_user_id)`
- `update_requisition(db, requisition_id, payload, current_user_id)`
- `submit_requisition(db, requisition_id, current_user_id)`
- `approve_requisition(db, requisition_id, payload, current_user_id)`
- `reject_requisition(db, requisition_id, payload, current_user_id)`
- `fulfill_requisition(db, requisition_id, payload, current_user_id)`
- `cancel_requisition(db, requisition_id, current_user_id)`
- `generate_requisition_number(db)`

Key service rules:

- Validate every requested item exists.
- Copy `unit_of_measure` from the item into the requisition line.
- Do not allow submitted/approved/fulfilled requisitions to be edited except through workflow actions.
- Do not approve more than requested unless explicitly allowed.
- During fulfillment, validate available stock line by line before committing.
- Use one database transaction for fulfillment so partial failures do not leave stock inconsistent.
- Call or share the same inventory issue logic used by `adjust_inventory_quantity`.
- Write `InventoryTransaction` records with `transaction_type=ISSUE`, `reference_number=requisition_number`, and useful line notes.
- Support partial fulfillment by updating `fulfilled_quantity` per line and setting header status accordingly.

### API Routes

Add routes to `Backend/api/v1/inventory.py` under `/api/v1/inventory/requisitions`.

Suggested endpoints:

- `GET /requisitions`: paginated list with filters
- `POST /requisitions`: create draft requisition
- `GET /requisitions/{id}`: detail with lines
- `PUT /requisitions/{id}`: update draft
- `POST /requisitions/{id}/submit`: submit draft
- `POST /requisitions/{id}/approve`: approve submitted requisition
- `POST /requisitions/{id}/reject`: reject submitted requisition
- `POST /requisitions/{id}/fulfill`: issue stock for approved requisition
- `POST /requisitions/{id}/cancel`: cancel draft/submitted/approved requisition if no fulfillment has happened

Important routing detail:

- Register `/requisitions...` routes before generic `/{item_id}` inventory item routes, so FastAPI route matching never treats `requisitions` as an item identifier.

### Permissions

Add mirrored permissions in both `Backend/core/permissions.py` and `icms-web/src/config/permissions.ts`:

- `inventory.requisitions.view`
- `inventory.requisitions.create`
- `inventory.requisitions.edit`
- `inventory.requisitions.submit`
- `inventory.requisitions.approve`
- `inventory.requisitions.fulfill`
- `inventory.requisitions.cancel`

Recommended implications:

- Create/edit/submit/cancel imply view.
- Fulfill implies `inventory.transaction`.
- Approve implies view.

Current backend APIs mostly require authentication but not granular permissions. Requisitions should introduce server-side checks for workflow actions if the project is ready for that, or the implementation should explicitly match the current pattern and rely on frontend route guards until backend RBAC enforcement is added.

### Database Migration

Add an Alembic revision that creates:

- `inventory_requisitions`
- `inventory_requisition_items`

Indexes:

- unique index on `inventory_requisitions.requisition_number`
- index on `inventory_requisitions.status`
- index on `inventory_requisitions.requested_by`
- index on `inventory_requisition_items.requisition_id`
- index on `inventory_requisition_items.item_id`

The backend currently also calls `Base.metadata.create_all(bind=engine)`, but a migration is still needed for controlled deployments.

## Frontend Design

### Service Types and Methods

Extend `icms-web/src/services/inventory.service.ts` with:

- requisition status and priority types
- requisition item interfaces
- create/update/action request interfaces
- list/detail response interfaces

Add service methods:

- `getRequisitions(filters)`
- `getRequisitionById(id)`
- `createRequisition(data)`
- `updateRequisition(id, data)`
- `submitRequisition(id)`
- `approveRequisition(id, data)`
- `rejectRequisition(id, data)`
- `fulfillRequisition(id, data)`
- `cancelRequisition(id)`

### Pages

Add pages under `icms-web/src/pages/inventory`:

- `InventoryRequisitionsPage.tsx`: operational list with status tabs, search, priority/status filters, requester/date columns, and primary actions.
- `InventoryRequisitionFormPage.tsx`: create/edit draft requisition with line-item picker, quantities, needed-by date, work order or production order reference, and notes.
- `InventoryRequisitionDetailPage.tsx`: header summary, line availability table, timeline/actions, approval and fulfillment controls.

### Navigation and Routes

Update `icms-web/src/App.tsx`:

- `/inventory/requisitions`
- `/inventory/requisitions/new`
- `/inventory/requisitions/:id`
- `/inventory/requisitions/:id/edit`

These must be declared before `/inventory/:id`.

Update `icms-web/src/components/common/Sidebar.tsx`:

- Convert Inventory from a single link to an expandable section, similar to Maintenance and Production.
- Children:
  - Items: `/inventory`
  - Spreadsheet: `/inventory/grid`
  - Requisitions: `/inventory/requisitions`
  - Categories: `/inventory/categories`

### UI Behavior

List page:

- Show counters for submitted, approved, partially fulfilled, and overdue needed-by requisitions.
- Use compact tables, status badges, priority badges, and row actions.
- Include filters for status, priority, requester, linked work order, and date.

Form page:

- Let the user add multiple lines.
- Search/select existing inventory items.
- Display available quantity and unit of measure after item selection.
- Validate quantity > 0 before submit.
- Save as draft and submit actions should be separate.

Detail page:

- Show requested, approved, fulfilled, and remaining quantities per line.
- Highlight insufficient stock before fulfillment.
- Allow approval quantities to be adjusted before approval.
- Allow partial fulfillment by line.
- Show transaction references after fulfillment.

## Integration Decisions

Recommended first implementation should support optional links to work orders and production orders, but not require them. This keeps requisitions useful for maintenance, production, quality, and general inventory use without blocking on deeper workflow integration.

Purchase orders should remain out of scope for the first requisitions feature. A later procurement feature can convert approved requisitions or low-stock requisition lines into purchase orders.

Stock reservation should also be out of scope initially. Approved requisitions should warn about current stock availability, while fulfillment remains the moment stock is actually consumed.

## Implementation Milestones

1. Backend model, enum, schema, and migration.
2. Backend service workflow and API endpoints.
3. Frontend service types and methods.
4. Requisition list/detail/form pages.
5. Navigation, routes, and permissions.
6. Tests and manual verification.

## Test Plan

Backend tests:

- Create draft requisition with valid items.
- Reject invalid item IDs and invalid quantities.
- Submit only draft requisitions.
- Approve only submitted requisitions.
- Reject only submitted requisitions.
- Fulfill only approved or partially fulfilled requisitions.
- Block fulfillment when requested fulfillment exceeds approved remaining quantity.
- Block fulfillment when inventory stock is insufficient.
- Verify stock decreases and issue transactions are created during fulfillment.
- Verify partial fulfillment status updates correctly.
- Verify cancellation rules.

Frontend verification:

- Build succeeds with `npm run build`.
- Requisition routes do not conflict with `/inventory/:id`.
- Users without requisition permissions do not see routes/actions.
- Create/edit form validates required fields and line quantities.
- Detail workflow actions refresh the requisition and inventory quantities.

## Risks and Follow-Ups

- Server-side RBAC is not consistently enforced today. Workflow endpoints are sensitive and should ideally enforce permissions on the backend.
- Existing inventory quantity adjustment stores transaction quantities with mixed signs depending on caller input. Requisition fulfillment should standardize the sign used for issue transactions so history displays correctly.
- Existing date fields often use strings. Requisitions can follow that pattern for consistency, but long term the backend should move workflow timestamps to `DateTime`.
- Alembic initial migration is effectively empty while the app uses `create_all`. New deployments should still get a real requisitions migration.
- The global `icms-web/src/types/index.ts` has older inventory type shapes that differ from `inventory.service.ts`. Prefer the service-local types for this feature unless the project first consolidates shared types.

## Open Product Questions

- Who is allowed to approve requisitions: managers only, inventory staff, department heads, or role-template specific approvers?
- Should approval be required for every requisition, or can inventory staff fulfill their own drafts?
- Should requisitions reserve stock after approval?
- Should requesters be allowed to cancel after partial fulfillment?
- Should fulfillment print or export an issue slip?
- Should requisitions support non-catalog items, or only existing `InventoryItem` records?
