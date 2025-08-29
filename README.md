# Post-Comments Service

A RESTful API service for creating posts and enabling users to comment on them. Built with FastAPI, SQLModel, and SQLite.

## 🚀 Features

- **Posts Management**: Create, read, and delete text-based posts
- **Comments System**: Add comments to posts with full CRUD operations
- **Nested Comments**: Support for replies to comments (bonus feature)
- **Pagination**: Efficient pagination for posts and comments listings
- **Input Validation**: Comprehensive request validation with detailed error messages
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 🏗️ Architecture Overview

### Technology Stack

- **Framework**: FastAPI (Python web framework)
- **Database**: SQLite (lightweight, file-based database)
- **ORM**: SQLModel (combines SQLAlchemy and Pydantic)
- **Validation**: Pydantic (automatic request/response validation)
- **Documentation**: OpenAPI/Swagger (auto-generated)

### Project Structure

```
post-comments-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization and startup
│   ├── database.py             # Database connection and session management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── posts.py            # Post endpoints + nested comment operations
│   │   └── comments.py         # Direct comment CRUD operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── post.py             # Post database model
│   │   └── comment.py          # Comment database model
│   └── schemas/
│       ├── __init__.py
│       ├── post.py             # Post API request/response schemas
│       └── comment.py          # Comment API request/response schemas
├── database.db           # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

### Database Design

#### Posts Table

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Comments Table

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    author VARCHAR(100),
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    parent_comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Relationships:**

- One post can have many comments (1:N)
- Comments can have replies via `parent_comment_id` (self-referencing)
- Cascading deletes ensure data integrity

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone git@github.com:Ganther3301/post-comments-service.git
   cd post-comments-service
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   fastapi run
   ```

5. **Verify installation**
   - API will be available at: <http://localhost:8000>
   - Interactive API docs: <http://localhost:8000/docs>
   - Alternative docs: <http://localhost:8000/redoc>

### Dependencies

```
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # ASGI server
sqlmodel==0.0.14          # ORM and validation
python-dotenv==1.0.0      # Environment variables
pytest==7.4.3            # Testing framework
httpx==0.25.2             # HTTP client for testing
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/
```

### Posts Endpoints

#### Create Post

```http
POST /posts
Content-Type: application/json

{
  "title": "My First Post",
  "content": "This is the content of my post",
  "author": "john_doe"
}
```

#### Get All Posts (Paginated)

```http
GET /posts?page=1&limit=10
```

#### Get Single Post

```http
GET /posts/{post_id}
```

#### Delete Post

```http
DELETE /posts/{post_id}
```

### Comments Endpoints

#### Create Comment on Post

```http
POST /posts/{post_id}/comments
Content-Type: application/json

{
  "content": "This is a great post!",
  "author": "jane_doe"
}
```

#### Create Reply to Comment (Nested)

```http
POST /posts/{post_id}/comments
Content-Type: application/json

{
  "content": "I agree with your comment!",
  "author": "bob_smith",
  "parent_comment_id": 1
}
```

#### Get Comments for Post (Paginated)

```http
GET /posts/{post_id}/comments?page=1&limit=20
```

#### Get Single Comment

```http
GET /comments/{comment_id}
```

#### Update Comment

```http
PUT /comments/{comment_id}
Content-Type: application/json

{
  "content": "Updated comment content"
}
```

#### Delete Comment

```http
DELETE /comments/{comment_id}
```

### Response Examples

#### Post Response

```json
{
  "id": 1,
  "title": "My First Post",
  "content": "This is the content of my post",
  "author": "john_doe",
  "created_at": "2025-08-30T10:30:00Z",
  "updated_at": "2025-08-30T10:30:00Z",
  "comments_count": 5
}
```

#### Comment Response

```json
{
  "id": 1,
  "content": "This is a great post!",
  "author": "jane_doe",
  "post_id": 1,
  "parent_comment_id": null,
  "created_at": "2025-08-30T10:35:00Z",
  "updated_at": "2025-08-30T10:35:00Z"
}
```

### Error Responses

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
DATABASE_URL=sqlite:///./database.db
DEBUG=True
```

### Database Initialization

The database and tables are created automatically on application startup using SQLModel's `create_all()` method.

## 📝 Future Enhancements

- User authentication and authorization
- Rich text support in comments (Markdown/HTML)
- File uploads and media attachments
- Real-time notifications for new comments
- Comment voting/rating system
- Full-text search functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a pull request
