# ICMS Backend - FastAPI Application

Modern Python backend for ICMS (Industry Computerized Management System) built with FastAPI, SQLAlchemy, and Pydantic.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

### Installation

```bash
# Navigate to Backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor

# Initialize database
alembic upgrade head

# Run development server (Method 1 - Direct Python)
python core/main.py

# OR (Method 2 - Using Uvicorn CLI)
uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

---

## 🐳 Docker

From the project root:

```bash
docker compose up --build backend
```

The API will be available at:

- `http://localhost:8000`
- `http://localhost:8000/docs`

The compose setup keeps local runtime data outside the image:

- `postgres_data` -> PostgreSQL database volume
- `Backend/uploads` -> uploaded files
- `Backend/logs` -> backend logs

Default local database settings are:

- database: `icms`
- user: `icms`
- password: `icms_password`
- internal URL: `postgresql+psycopg2://icms:icms_password@db:5432/icms`

For stronger local secrets, start it like this:

```bash
SECRET_KEY="$(openssl rand -hex 32)" POSTGRES_PASSWORD="change-me" docker compose up --build backend
```

When testing from a phone, keep the frontend running with host exposure:

```bash
cd icms-web
npm run dev:host
```

---

## 📂 Project Structure

```
Backend/
├── core/                    # Core application configuration
│   ├── main.py             # FastAPI app instance & startup
│   ├── config.py           # Configuration settings
│   ├── security.py         # Authentication & authorization
│   └── dependencies.py     # Dependency injection
│
├── api/                     # API routes
│   └── v1/                 # API version 1
│       ├── auth.py         # Authentication endpoints
│       ├── craftsmen.py    # Craftsmen management
│       ├── equipment.py    # Equipment management
│       ├── inventory.py    # Inventory management
│       ├── work_orders.py  # Work order management
│       ├── maintenance.py  # Maintenance operations
│       ├── production.py   # Production management
│       ├── quality.py      # Quality control
│       ├── reports.py      # Reporting & analytics
│       └── users.py        # User management
│
├── models/                  # SQLAlchemy ORM models
│   ├── base.py             # Base model class
│   ├── user.py             # User model
│   ├── craftsman.py        # Craftsman model
│   ├── equipment.py        # Equipment model
│   ├── inventory.py        # Inventory model
│   ├── work_order.py       # Work order model
│   └── maintenance.py      # Maintenance report model
│
├── schemas/                 # Pydantic schemas (request/response)
│   ├── user.py
│   ├── craftsman.py
│   ├── equipment.py
│   ├── inventory.py
│   └── work_order.py
│
├── services/                # Business logic layer
│   ├── craftsman_service.py
│   ├── equipment_service.py
│   ├── inventory_service.py
│   └── work_order_service.py
│
├── db/                      # Database configuration
│   ├── session.py          # Database session management
│   ├── base.py             # Declarative base
│   └── migrations/         # Alembic migrations
│       └── versions/       # Migration files
│
├── middleware/              # Custom middleware
│   └── error_handler.py    # Global error handling
│
├── utils/                   # Utility functions
│   ├── email.py            # Email utilities
│   ├── file_handler.py     # File upload/download
│   └── validators.py       # Custom validators
│
├── tests/                   # Unit and integration tests
│   ├── test_auth.py
│   ├── test_craftsmen.py
│   └── test_equipment.py
│
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Application
APP_NAME=ICMS Backend
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./icms.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/icms_db
# For MySQL:
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/icms_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=./uploads

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@icms.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/icms.log
```

---

## 🗃️ Database

### Supported Databases
- **SQLite** (default for development)
- **PostgreSQL** (recommended for production)
- **MySQL/MariaDB**
- **Microsoft SQL Server**

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Initial Data Seeding

```bash
# Run seed script to create initial data
python scripts/seed_data.py
```

---

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user

### Craftsmen
- `GET /api/v1/craftsmen` - List all craftsmen
- `POST /api/v1/craftsmen` - Create new craftsman
- `GET /api/v1/craftsmen/{id}` - Get craftsman details
- `PUT /api/v1/craftsmen/{id}` - Update craftsman
- `DELETE /api/v1/craftsmen/{id}` - Delete craftsman
- `GET /api/v1/craftsmen/{id}/work-orders` - Get craftsman's work orders
- `GET /api/v1/craftsmen/{id}/skills` - Get craftsman's skills

### Equipment
- `GET /api/v1/equipment` - List all equipment
- `POST /api/v1/equipment` - Add new equipment
- `GET /api/v1/equipment/{id}` - Get equipment details
- `PUT /api/v1/equipment/{id}` - Update equipment
- `DELETE /api/v1/equipment/{id}` - Delete equipment
- `GET /api/v1/equipment/{id}/maintenance-history` - Get maintenance history
- `GET /api/v1/equipment/{id}/downtime` - Get downtime statistics

### Work Orders
- `GET /api/v1/work-orders` - List all work orders
- `POST /api/v1/work-orders` - Create new work order
- `GET /api/v1/work-orders/{id}` - Get work order details
- `PUT /api/v1/work-orders/{id}` - Update work order
- `DELETE /api/v1/work-orders/{id}` - Delete work order
- `PATCH /api/v1/work-orders/{id}/status` - Update work order status
- `POST /api/v1/work-orders/{id}/assign` - Assign work order to craftsman

### Inventory
- `GET /api/v1/inventory` - List all inventory items
- `POST /api/v1/inventory` - Add new inventory item
- `GET /api/v1/inventory/{id}` - Get inventory item details
- `PUT /api/v1/inventory/{id}` - Update inventory item
- `DELETE /api/v1/inventory/{id}` - Delete inventory item
- `POST /api/v1/inventory/{id}/adjust` - Adjust inventory quantity
- `GET /api/v1/inventory/low-stock` - Get low stock items

### Maintenance Reports
- `GET /api/v1/maintenance/reports` - List all maintenance reports
- `POST /api/v1/maintenance/reports` - Create maintenance report
- `GET /api/v1/maintenance/reports/{id}` - Get report details
- `PUT /api/v1/maintenance/reports/{id}` - Update report
- `POST /api/v1/maintenance/reports/{id}/attachments` - Upload attachment

### Reports & Analytics
- `GET /api/v1/reports/dashboard` - Get dashboard KPIs
- `GET /api/v1/reports/equipment-uptime` - Equipment uptime report
- `GET /api/v1/reports/maintenance-costs` - Maintenance cost analysis
- `GET /api/v1/reports/work-order-summary` - Work order summary
- `GET /api/v1/reports/inventory-turnover` - Inventory turnover report

**Full API Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)

---

## 🔒 Authentication & Authorization

### JWT Authentication
The API uses JSON Web Tokens (JWT) for authentication.

#### Login Flow
1. Client sends credentials to `/api/v1/auth/login`
2. Server validates credentials and returns access token + refresh token
3. Client includes access token in `Authorization` header for subsequent requests
4. When access token expires, client uses refresh token to get new access token

#### Making Authenticated Requests
```python
# Python example
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'admin',
    'password': 'password123'
})
tokens = response.json()
access_token = tokens['access_token']

# Make authenticated request
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/craftsmen', headers=headers)
```

```javascript
// JavaScript example
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password123' })
});
const { access_token } = await response.json();

// Make authenticated request
const craftsmenResponse = await fetch('http://localhost:8000/api/v1/craftsmen', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const craftsmen = await craftsmenResponse.json();
```

### Role-Based Access Control (RBAC)
Users have roles that determine their permissions:
- **Admin**: Full system access
- **Manager**: View and manage all operations
- **Craftsman**: View assigned work orders, update status, create reports
- **Inventory**: Manage inventory, view work orders
- **Quality**: View production, create quality reports
- **Read-Only**: View-only access

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests in verbose mode
pytest -v
```

---

## 🐛 Debugging

### Development Mode
```bash
# Run with auto-reload and debug logging
uvicorn core.main:app --reload --log-level debug
```

### View Logs
```bash
# Tail application logs
tail -f logs/icms.log

# View error logs
grep ERROR logs/icms.log
```

### Interactive API Testing
1. Open `http://localhost:8000/docs` in browser
2. Click "Authorize" button
3. Login to get token
4. Use "Try it out" to test endpoints

---

## 📦 Dependencies

### Core
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation

### Security
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **bcrypt** - Password hashing algorithm

### Utilities
- **python-multipart** - File upload support
- **python-dotenv** - Environment variable management
- **aiofiles** - Async file operations

### Development
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for testing
- **black** - Code formatter
- **flake8** - Code linter

---

## 🚢 Deployment

### Docker Deployment
```bash
# Build image
docker build -t icms-backend .

# Run container
docker run -d -p 8000:8000 --env-file .env icms-backend
```

### Using Docker Compose
```bash
# Start all services (backend + database)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins
- [ ] Setup SSL/TLS certificate
- [ ] Enable rate limiting
- [ ] Configure log rotation
- [ ] Setup database backups
- [ ] Enable monitoring (Prometheus/Grafana)
- [ ] Setup error tracking (Sentry)

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and commit: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Create Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions/classes
- Format code with `black`
- Lint with `flake8`

---

## 📄 License

[Your License Here]

---

## 🆘 Support

- **Documentation**: [Link to full docs]
- **Issues**: [GitHub Issues]
- **Email**: support@icms.com

---

**Built with ❤️ using FastAPI**
