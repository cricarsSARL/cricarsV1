# Cricars - Premium Car Rental Platform

## Overview

Cricars is a modern, full-featured car rental platform built with Django. It enables users to rent cars and hosts to list their vehicles, creating a seamless car-sharing experience.

## Features

### For Renters

- User registration and authentication
- Email verification system
- Browse available cars with detailed information
- Search and filter cars by various criteria
- Make reservations with flexible date ranges
- View booking history and status
- Profile management

### For Hosts

- Host registration and verification
- List and manage vehicles
- Upload car images and details
- Set availability and pricing
- Track bookings and rentals
- Manage host profile

### General Features

- Responsive design for all devices
- Secure authentication system
- Email notifications
- User-friendly interface
- CRUD operations for cars and bookings

## Technology Stack

- **Backend**: Django 5.2.1
- **Database**: MySQL (Production), SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Email**: SMTP (Gmail)
- **Static Files**: WhiteNoise
- **Deployment**: Railway.app
- **Version Control**: Git

## Setup and Installation

1. Clone the repository

```bash
git clone https://github.com/cricarsSARL/cricarsV1.git
cd cricarsV1
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables (.env)

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
MYSQL_DATABASE=your_db_name
MYSQLUSER=your_db_user
MYSQL_ROOT_PASSWORD=your_db_password
MYSQLHOST=your_db_host
MYSQLPORT=your_db_port
```

5. Run migrations

```bash
python manage.py migrate
```

6. Create a superuser

```bash
python manage.py createsuperuser
```

7. Run the development server

```bash
python manage.py runserver
```

## Project Structure

```
cricarsV1/
├── myapp/                 # Main application directory
│   ├── migrations/       # Database migrations
│   ├── static/          # Static files (CSS, JS, images)
│   ├── templates/       # HTML templates
│   ├── admin.py        # Admin panel configuration
│   ├── forms.py        # Form definitions
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   └── urls.py         # URL routing
├── myproject/           # Project configuration
│   ├── settings.py     # Project settings
│   ├── urls.py         # Main URL routing
│   └── wsgi.py         # WSGI configuration
├── media/              # User-uploaded files
├── requirements.txt    # Project dependencies
└── manage.py          # Django management script
```

## Deployment

The application is deployed on Railway.app. For deployment:

1. Create a Railway account
2. Set up a new project
3. Add PostgreSQL database
4. Configure environment variables
5. Deploy using Railway CLI or GitHub integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- Website: [cricars.online](https://cricars.online)
- Email: support@cricars.com

## Acknowledgments

- Django community
- Contributors and testers
- Open source packages used in this project
