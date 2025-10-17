import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('linkhub.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')
    
    # Links table
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            category_id INTEGER,
            user_id INTEGER,
            likes INTEGER DEFAULT 0,
            is_sensitive BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User likes table (many-to-many)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            link_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (link_id) REFERENCES links (id),
            UNIQUE(user_id, link_id)
        )
    ''')
    
    # User bookmarks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            link_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (link_id) REFERENCES links (id),
            UNIQUE(user_id, link_id)
        )
    ''')
    
    # Contact requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS contact_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            request_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            user_email TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Data removal requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS data_removal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            removal_type TEXT NOT NULL,
            specific_links TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    
    # Insert default categories
    categories = [
        ('Technology', 'Latest in tech and programming'),
        ('Design', 'Creative design and UX/UI'),
        ('Business', 'Business and entrepreneurship'),
        ('Health', 'Health and wellness'),
        ('Gaming', 'Gaming and entertainment')
    ]
    
    c.executemany('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', categories)
    
    # Create a default user with proper password hashing
    import hashlib
    import secrets
    
    default_username = 'demo'
    default_email = 'demo@example.com'
    default_password = 'password123'
    default_full_name = 'Demo User'
    
    # Check if default user already exists
    c.execute('SELECT id FROM users WHERE username = ?', (default_username,))
    if not c.fetchone():
        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((default_password + salt).encode()).hexdigest()
        
        c.execute('''
            INSERT INTO users (username, email, password, full_name, salt)
            VALUES (?, ?, ?, ?, ?)
        ''', (default_username, default_email, hashed_password, default_full_name, salt))
    
    # Get the user ID for sample links
    c.execute('SELECT id FROM users WHERE username = ?', (default_username,))
    user_result = c.fetchone()
    user_id = user_result[0] if user_result else 1
    
    sample_links = []
    
    c.executemany('''
        INSERT OR IGNORE INTO links (title, url, description, image_url, category_id, user_id, is_sensitive) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_links)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('linkhub.db')
    conn.row_factory = sqlite3.Row
    return conn