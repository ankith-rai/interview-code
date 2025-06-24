#!/usr/bin/env python3
"""
Library Management System - API Only
Supports REST API interface with file-based persistence
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
import uuid

# Data Models
@dataclass
class Book:
    id: str
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class User:
    id: str
    name: str
    email: str
    borrowed_books: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.borrowed_books is None:
            self.borrowed_books = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class BorrowRecord:
    id: str
    user_id: str
    book_id: str
    isbn: str
    borrowed_at: str
    returned_at: str = None
    
    def __post_init__(self):
        if self.borrowed_at is None:
            self.borrowed_at = datetime.now().isoformat()

# Data Access Layer
class LibraryDataStore:
    def __init__(self, data_file: str = "library_data.json"):
        self.data_file = data_file
        self.data = {
            "books": {},
            "users": {},
            "borrow_records": {}
        }
        self.load_data()
    
    def load_data(self):
        """Load data from file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load data from {self.data_file}, starting fresh")
    
    def save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def add_book(self, book: Book) -> bool:
        """Add a book to the library"""
        self.data["books"][book.id] = asdict(book)
        self.save_data()
        return True
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """Get book by ISBN"""
        for book_data in self.data["books"].values():
            if book_data["isbn"] == isbn:
                return Book(**book_data)
        return None
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get book by ID"""
        book_data = self.data["books"].get(book_id)
        if book_data:
            return Book(**book_data)
        return None
    
    def get_all_books(self) -> List[Book]:
        """Get all books"""
        return [Book(**book_data) for book_data in self.data["books"].values()]
    
    def update_book(self, book: Book) -> bool:
        """Update a book"""
        if book.id in self.data["books"]:
            self.data["books"][book.id] = asdict(book)
            self.save_data()
            return True
        return False
    
    def remove_book(self, book_id: str) -> bool:
        """Remove a book"""
        if book_id in self.data["books"]:
            del self.data["books"][book_id]
            self.save_data()
            return True
        return False
    
    def add_user(self, user: User) -> bool:
        """Add a user"""
        self.data["users"][user.id] = asdict(user)
        self.save_data()
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self.data["users"].get(user_id)
        if user_data:
            return User(**user_data)
        return None
    
    def update_user(self, user: User) -> bool:
        """Update a user"""
        if user.id in self.data["users"]:
            self.data["users"][user.id] = asdict(user)
            self.save_data()
            return True
        return False
    
    def add_borrow_record(self, record: BorrowRecord) -> bool:
        """Add a borrow record"""
        self.data["borrow_records"][record.id] = asdict(record)
        self.save_data()
        return True
    
    def get_active_borrow_record(self, user_id: str, isbn: str) -> Optional[BorrowRecord]:
        """Get active borrow record for user and book"""
        for record_data in self.data["borrow_records"].values():
            if (record_data["user_id"] == user_id and 
                record_data["isbn"] == isbn and 
                record_data["returned_at"] is None):
                return BorrowRecord(**record_data)
        return None
    
    def update_borrow_record(self, record: BorrowRecord) -> bool:
        """Update a borrow record"""
        if record.id in self.data["borrow_records"]:
            self.data["borrow_records"][record.id] = asdict(record)
            self.save_data()
            return True
        return False

# Business Logic Layer
class LibraryManager:
    def __init__(self, datastore: LibraryDataStore):
        self.datastore = datastore
    
    def add_book(self, title: str, author: str, isbn: str, copies: int) -> Dict:
        """Add a new book to the library"""
        # Check if book with same ISBN already exists
        existing_book = self.datastore.get_book_by_isbn(isbn)
        if existing_book:
            # Update copies for existing book
            existing_book.total_copies += copies
            existing_book.available_copies += copies
            self.datastore.update_book(existing_book)
            return {
                "success": True,
                "message": f"Added {copies} more copies. Total: {existing_book.total_copies}",
                "book": asdict(existing_book)
            }
        
        # Create new book
        book = Book(
            id=str(uuid.uuid4()),
            title=title,
            author=author,
            isbn=isbn,
            total_copies=copies,
            available_copies=copies
        )
        
        self.datastore.add_book(book)
        return {
            "success": True,
            "message": "Book added successfully",
            "book": asdict(book)
        }
    
    def remove_book(self, isbn: str) -> Dict:
        """Remove a book from the library"""
        book = self.datastore.get_book_by_isbn(isbn)
        if not book:
            return {"success": False, "message": "Book not found"}
        
        if book.available_copies < book.total_copies:
            return {
                "success": False,
                "message": f"Cannot remove book. {book.total_copies - book.available_copies} copies are currently borrowed"
            }
        
        self.datastore.remove_book(book.id)
        return {"success": True, "message": "Book removed successfully"}
    
    def borrow_book(self, user_id: str, isbn: str) -> Dict:
        """Borrow a book"""
        # Check if user exists
        user = self.datastore.get_user(user_id)
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Check if book exists and is available
        book = self.datastore.get_book_by_isbn(isbn)
        if not book:
            return {"success": False, "message": "Book not found"}
        
        if book.available_copies <= 0:
            return {"success": False, "message": "No copies available"}
        
        # Check if user already borrowed this book
        existing_record = self.datastore.get_active_borrow_record(user_id, isbn)
        if existing_record:
            return {"success": False, "message": "User has already borrowed this book"}
        
        # Create borrow record
        borrow_record = BorrowRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            book_id=book.id,
            isbn=isbn
        )
        
        # Update book availability
        book.available_copies -= 1
        
        # Update user's borrowed books
        user.borrowed_books.append(book.id)
        
        # Save changes
        self.datastore.add_borrow_record(borrow_record)
        self.datastore.update_book(book)
        self.datastore.update_user(user)
        
        return {
            "success": True,
            "message": "Book borrowed successfully",
            "borrow_record": asdict(borrow_record)
        }
    
    def return_book(self, user_id: str, isbn: str) -> Dict:
        """Return a borrowed book"""
        # Check if user exists
        user = self.datastore.get_user(user_id)
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Check if book exists
        book = self.datastore.get_book_by_isbn(isbn)
        if not book:
            return {"success": False, "message": "Book not found"}
        
        # Check if user has borrowed this book
        borrow_record = self.datastore.get_active_borrow_record(user_id, isbn)
        if not borrow_record:
            return {"success": False, "message": "No active borrow record found"}
        
        # Update borrow record
        borrow_record.returned_at = datetime.now().isoformat()
        
        # Update book availability
        book.available_copies += 1
        
        # Update user's borrowed books
        if book.id in user.borrowed_books:
            user.borrowed_books.remove(book.id)
        
        # Save changes
        self.datastore.update_borrow_record(borrow_record)
        self.datastore.update_book(book)
        self.datastore.update_user(user)
        
        return {
            "success": True,
            "message": "Book returned successfully",
            "borrow_record": asdict(borrow_record)
        }
    
    def list_books(self) -> List[Dict]:
        """List all books"""
        books = self.datastore.get_all_books()
        return [asdict(book) for book in books]
    
    def add_user(self, name: str, email: str, user_id: str = None) -> Dict:
        """Add a new user"""
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        # Check if user already exists
        existing_user = self.datastore.get_user(user_id)
        if existing_user:
            return {"success": False, "message": "User already exists"}
        
        user = User(id=user_id, name=name, email=email)
        self.datastore.add_user(user)
        
        return {
            "success": True,
            "message": "User added successfully",
            "user": asdict(user)
        }



# API Interface
def create_app(manager: LibraryManager) -> Flask:
    app = Flask(__name__)
    
    @app.route('/books', methods=['POST'])
    def add_book():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['title', 'author', 'isbn']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        copies = data.get('copies', 1)
        result = manager.add_book(data['title'], data['author'], data['isbn'], copies)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    @app.route('/books', methods=['GET'])
    def get_books():
        books = manager.list_books()
        return jsonify({"books": books})
    
    @app.route('/borrow', methods=['POST'])
    def borrow_book():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['user_id', 'isbn']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = manager.borrow_book(data['user_id'], data['isbn'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @app.route('/return', methods=['POST'])
    def return_book():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['user_id', 'isbn']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = manager.return_book(data['user_id'], data['isbn'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @app.route('/users', methods=['POST'])
    def add_user():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = data.get('user_id')
        result = manager.add_user(data['name'], data['email'], user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "Library Management System"})
    
    return app

# Main execution
if __name__ == "__main__":
    # Initialize components
    datastore = LibraryDataStore()
    manager = LibraryManager(datastore)
    
    # Start API server
    app = create_app(manager)
    print("Starting Library Management API server...")
    print("Endpoints:")
    print("  POST /books - Add a book")
    print("  GET /books - List all books")
    print("  POST /borrow - Borrow a book")
    print("  POST /return - Return a book")
    print("  POST /users - Add a user")
    print("  GET /health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
