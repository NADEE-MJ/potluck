# Potluck Organizer

A web application for organizing potlucks with categories and items. Built with FastAPI and Jinja2 templates.

## Features

### Admin Features
- Create potlucks with unique shareable links
- Define categories with max item limits (e.g., "Desserts: max 5 items")
- Pre-populate items within categories
- Edit potlucks, categories, items, and claims
- Delete potlucks, categories, items, and claims

### Attendee Features
- Access potluck via shareable link (no password required)
- View all categories, items, and who's bringing what
- Claim items (provide name + optional item details)
- Multiple people can claim same item (up to item's limit)
- Add new items to categories (only if category has space)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone or download this repository

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Edit the `.env` file
   - Change `ADMIN_PASSWORD` to a secure password
   - Generate a new `SECRET_KEY`:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Update `SECRET_KEY` in `.env`

## Running the Application

### Development Server

```bash
python run.py
```

The application will be available at http://localhost:8000

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For production, consider using:
- Gunicorn with Uvicorn workers
- Nginx as a reverse proxy
- HTTPS/SSL certificates
- Environment variables instead of `.env` file

## Usage

### Creating a Potluck (Admin)

1. Visit http://localhost:8000
2. Login with the admin password
3. Click "Create New Potluck"
4. Fill in potluck details
5. Add categories (e.g., "Appetizers", "Mains", "Desserts")
6. Add items to each category
7. Share the generated link with attendees

### Attending a Potluck

1. Visit the shareable link (e.g., http://localhost:8000/p/abc123xy)
2. Browse categories and items
3. Claim items by entering your name
4. Add new items if categories have space

## Project Structure

```
potluck/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # Business logic
│   ├── routes/
│   │   ├── admin.py            # Admin routes
│   │   └── potluck.py          # Public routes
│   ├── static/
│   │   ├── css/style.css       # Custom styles
│   │   └── js/main.js          # JavaScript
│   └── templates/              # Jinja2 templates
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── run.py                      # Development server
└── README.md                   # This file
```

## Database Schema

### Models
- **Potluck**: Event with name, description, and unique URL slug
- **Category**: Groups items (e.g., "Appetizers"), has max item limit
- **Item**: Something to bring, has claim limit
- **Claim**: Attendee's commitment to bring an item

### Relationships
- Potluck → Categories (one-to-many)
- Category → Items (one-to-many)
- Item → Claims (one-to-many)

## Security

- Admin password is hashed with bcrypt
- Session-based authentication for admin
- CSRF protection via session middleware
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM
- Cryptographically secure URL slug generation

## Technology Stack

- **Backend**: FastAPI (Python)
- **Templates**: Jinja2
- **Database**: SQLite with SQLAlchemy ORM
- **CSS**: Pico CSS (classless, minimal)
- **Auth**: Session-based with bcrypt

## License

MIT License - feel free to use and modify!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub or contact the maintainer.
