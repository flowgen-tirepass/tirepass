# TIREPASS Setup Instructions

## Prerequisites
- Python 3.13 or higher
- MariaDB 10.x or higher
- Git (optional)

## Installation Steps

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration

#### MariaDB Settings
Update `itire/settings.py` with your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'itiredb',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### Initialize Database
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Create Test User
```bash
python create_test_user.py
```
Test credentials:
- Business Number: 1234567890
- Password: 67890

### 7. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8080
```

Access the application:
- PC Version: http://localhost:8080/goods/
- Mobile Version: http://localhost:8080/mobile/

## Project Structure
```
1.0_tirepass/
├── itire/              # Django project settings
├── tire_data/          # Main app (PC version)
│   ├── models.py       # Data models
│   ├── views.py        # View logic
│   └── templates/      # HTML templates
├── mobile/             # Mobile app
│   ├── views.py        # Mobile views
│   └── templates/      # Mobile templates
├── static/             # Static files
│   └── brands/         # Brand logo images
├── data/               # Database files
│   └── ITIRE.GDB       # Firebird database
└── work/               # Utility scripts

## Features
- Tire inventory management
- Customer management with authentication
- Year-based allocation system (2021-2025)
- Brand filtering and search
- Mobile-optimized interface
- Bulk user registration

## Management Commands

### Register All Customers
```bash
python manage.py register_customers
```

### Dry Run (Test Mode)
```bash
python manage.py register_customers --dry-run
```

## Troubleshooting

### Database Connection Issues
- Ensure MariaDB service is running
- Check database credentials in settings.py
- Verify database 'itiredb' exists

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Port Already in Use
Change port number:
```bash
python manage.py runserver 0.0.0.0:8001
```

## Security Notes
- Change SECRET_KEY in production
- Set DEBUG=False in production
- Configure ALLOWED_HOSTS properly
- Use environment variables for sensitive data

## Support
For issues and questions, please contact the development team.