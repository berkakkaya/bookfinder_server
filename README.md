# Bookfinder Server

A Flask-based REST API server for a book discovery and recommendation platform. This server provides comprehensive book management features including user authentication, book search, personalized recommendations, and library management.

[Repository for the Mobile App](https://github.com/berkakkaya/bookfinder_app)

## Features

### 🔐 Authentication & User Management
- User registration and login with secure password hashing (Argon2)
- JWT-based authentication with access and refresh tokens
- Protected routes with authentication middleware

### 📚 Book Management
- Book search functionality with MongoDB Atlas Search integration
- Book data fetching and management
- Book library management for users
- Book tracking and reading status management

### 🎯 Personalized Recommendations
- Custom book recommendation algorithm
- Category-based filtering for recommendations
- User preference learning and adaptation

### 📰 Feed System
- User activity feed management
- Social features for book sharing and discovery

### 🗂️ Categories Support
Supports a wide range of book categories including:
- **Fiction**: Adventure, Classics, Fantasy, Horror, Mystery, Romance, Sci-Fi, Thriller, Young Adult
- **Non-Fiction**: Art, Biography, Business, Cooking, Health, History, Politics, Religion, Science, Self-Help, Travel

## Tech Stack

- **Backend Framework**: Flask 3.1.0
- **Database**: MongoDB with PyMongo 4.10.1
- **Authentication**: PyJWT 2.9.0 with Argon2-CFFI 23.1.0 for password hashing
- **Environment Management**: python-dotenv 1.0.1
- **Search**: MongoDB Atlas Search integration

## Project Structure

```
bookfinder_server/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── models/                         # Data models
│   ├── book_categories.py          # Book category enums
│   ├── feed_entries.py             # Feed entry models
│   └── tokens.py                   # Token models
├── routes/                         # API route blueprints
│   ├── auth_management/            # Authentication routes
│   │   ├── logon_routes.py         # Login/register endpoints
│   │   └── token_routes.py         # Token management endpoints
│   ├── book_data_related/          # Book data routes
│   │   └── book_data_fetching.py   # Book search and retrieval
│   ├── feed_related/               # Feed management routes
│   │   └── feed_entries_management.py
│   ├── library_related/            # User library routes
│   │   ├── book_library_routes.py  # Library management
│   │   └── book_tracking_routes.py # Reading progress tracking
│   ├── recommendation_algorithm/   # Recommendation system
│   │   └── book_recommendations.py # Book recommendation logic
│   └── user_management/            # User data routes
│       └── user_data_fetching.py   # User profile management
├── services/                       # Business logic services
│   └── database/                   # Database services
│       └── _db_service.py          # MongoDB connection and collections
└── utils/                          # Utility functions
    ├── flask_auth.py               # Authentication decorators
    ├── pool_ops.py                 # Pool operations utilities
    ├── pw_ops.py                   # Password operations
    └── token_management.py         # JWT token utilities
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bookfinder_server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   MONGO_URL=mongodb://localhost:27017/bookfinder
   JWT_SECRET_KEY=your-secret-key-here
   ```

5. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Create the required collections:
     - `users`
     - `rawBookDatas`
     - `bookLibraries`
     - `bookTrackingStatuses`
     - `feed`
     - `pools`

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
flask run --host=0.0.0.0 --port=5000
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `POST /refresh` - Refresh JWT token

### Book Operations
- `GET /bookSearch?q=<query>` - Search books by title
- `GET /recommendations` - Get personalized book recommendations
- `GET /recommendations?category=<category>` - Get category-filtered recommendations

### Library Management
- `GET /library` - Get user's book library
- `POST /library` - Add book to library
- `DELETE /library/<book_id>` - Remove book from library

### User Management
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update user profile

## Database Collections

### Users Collection
Stores user account information including hashed passwords and user preferences.

### Raw Book Datas Collection
Contains book metadata fetched from external APIs (Google Books API).

### Book Libraries Collection
Manages user's personal book collections and favorites.

### Book Tracking Statuses Collection
Tracks reading progress and status for each user's books.

### Feed Collection
Stores user activity and social interactions.

## Security Features

- **Password Security**: Argon2 hashing algorithm for secure password storage
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Protected Routes**: Authentication middleware for sensitive endpoints
- **Input Validation**: Request validation and sanitization

## License

This project is licensed under the MIT License - see the LICENSE file for details. Also, this project is part of a school assignment and is intended for educational purposes.

---

Made with ❤️ by **Berk Akkaya**.
