from database import get_db_connection
import hashlib
import secrets
import sqlite3

class User:
    @staticmethod
    def create_user(username, email, password, full_name):
        conn = get_db_connection()
        c = conn.cursor()
        
        # Hash password
        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        
        try:
            c.execute('''
                INSERT INTO users (username, email, password, full_name, salt)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, hashed_password, full_name, salt))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.close()
            print(f"Database error: {e}")
            return None
    
    @staticmethod
    def verify_user(username, password):
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        
        if user:
            salt = user['salt']
            hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
            if hashed_password == user['password']:
                conn.close()
                return dict(user)
        conn.close()
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, email, full_name, created_at FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None

class Link:
    @staticmethod
    def get_all_links(include_sensitive=False):
        conn = get_db_connection()
        c = conn.cursor()
        
        if include_sensitive:
            query = '''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                ORDER BY l.created_at DESC
            '''
        else:
            query = '''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                WHERE l.is_sensitive = 0
                ORDER BY l.created_at DESC
            '''
        
        try:
            c.execute(query)
            links = [dict(row) for row in c.fetchall()]
            conn.close()
            return links
        except Exception as e:
            print(f"Error fetching links: {e}")
            conn.close()
            return []
    
    @staticmethod
    def get_links_by_category(category_id, include_sensitive=False):
        conn = get_db_connection()
        c = conn.cursor()
        
        if include_sensitive:
            query = '''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                WHERE l.category_id = ?
                ORDER BY l.created_at DESC
            '''
        else:
            query = '''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                WHERE l.category_id = ? AND l.is_sensitive = 0
                ORDER BY l.created_at DESC
            '''
        
        try:
            c.execute(query, (category_id,))
            links = [dict(row) for row in c.fetchall()]
            conn.close()
            return links
        except Exception as e:
            print(f"Error fetching links by category: {e}")
            conn.close()
            return []
    
    @staticmethod
    def create_link(title, url, description, image_url, category_id, user_id, is_sensitive=False):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO links (title, url, description, image_url, category_id, user_id, is_sensitive)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, url, description, image_url, category_id, user_id, is_sensitive))
            conn.commit()
            link_id = c.lastrowid
            conn.close()
            return link_id
        except Exception as e:
            print(f"Error creating link: {e}")
            conn.close()
            return None
    
    @staticmethod
    def like_link(user_id, link_id):
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            # Check if already liked
            c.execute('SELECT * FROM user_likes WHERE user_id = ? AND link_id = ?', (user_id, link_id))
            if c.fetchone():
                conn.close()
                return False
            
            # Add like
            c.execute('INSERT INTO user_likes (user_id, link_id) VALUES (?, ?)', (user_id, link_id))
            c.execute('UPDATE links SET likes = likes + 1 WHERE id = ?', (link_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error liking link: {e}")
            conn.close()
            return False
    
    @staticmethod
    def unlike_link(user_id, link_id):
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute('DELETE FROM user_likes WHERE user_id = ? AND link_id = ?', (user_id, link_id))
            c.execute('UPDATE links SET likes = likes - 1 WHERE id = ?', (link_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error unliking link: {e}")
            conn.close()
            return False
    
    @staticmethod
    def bookmark_link(user_id, link_id):
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            # Check if already bookmarked
            c.execute('SELECT * FROM user_bookmarks WHERE user_id = ? AND link_id = ?', (user_id, link_id))
            if c.fetchone():
                conn.close()
                return False
            
            c.execute('INSERT INTO user_bookmarks (user_id, link_id) VALUES (?, ?)', (user_id, link_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error bookmarking link: {e}")
            conn.close()
            return False
    
    @staticmethod
    def unbookmark_link(user_id, link_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_bookmarks WHERE user_id = ? AND link_id = ?', (user_id, link_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error unbookmarking link: {e}")
            conn.close()
            return False
    
    @staticmethod
    def get_user_likes(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('SELECT link_id FROM user_likes WHERE user_id = ?', (user_id,))
            likes = [row[0] for row in c.fetchall()]
            conn.close()
            return likes
        except Exception as e:
            print(f"Error getting user likes: {e}")
            conn.close()
            return []
    
    @staticmethod
    def get_user_bookmarks(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('SELECT link_id FROM user_bookmarks WHERE user_id = ?', (user_id,))
            bookmarks = [row[0] for row in c.fetchall()]
            conn.close()
            return bookmarks
        except Exception as e:
            print(f"Error getting user bookmarks: {e}")
            conn.close()
            return []
        

    
    @staticmethod
    def get_user_links(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                WHERE l.user_id = ?
                ORDER BY l.created_at DESC
            ''', (user_id,))
            links = [dict(row) for row in c.fetchall()]
            conn.close()
            return links
        except Exception as e:
            print(f"Error fetching user links: {e}")
            conn.close()
            return []
    
    @staticmethod
    def get_link_by_id(link_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT l.*, c.name as category_name, u.username as author
                FROM links l 
                JOIN categories c ON l.category_id = c.id 
                JOIN users u ON l.user_id = u.id
                WHERE l.id = ?
            ''', (link_id,))
            link = c.fetchone()
            conn.close()
            return dict(link) if link else None
        except Exception as e:
            print(f"Error fetching link by ID: {e}")
            conn.close()
            return None
    
    @staticmethod
    def delete_link(link_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            # Delete from user_likes and user_bookmarks first (foreign key constraints)
            c.execute('DELETE FROM user_likes WHERE link_id = ?', (link_id,))
            c.execute('DELETE FROM user_bookmarks WHERE link_id = ?', (link_id,))
            # Delete the link
            c.execute('DELETE FROM links WHERE id = ?', (link_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting link: {e}")
            conn.close()
            return False

class Category:
    @staticmethod
    def get_all_categories():
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('SELECT * FROM categories')
            categories = [dict(row) for row in c.fetchall()]
            conn.close()
            return categories
        except Exception as e:
            print(f"Error fetching categories: {e}")
            conn.close()
            return []
        
class Contact:
    @staticmethod
    def create_contact_request(user_id, request_type, subject, message, user_email):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO contact_requests (user_id, request_type, subject, message, user_email)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, request_type, subject, message, user_email))
            
            conn.commit()
            request_id = c.lastrowid
            conn.close()
            return request_id
        except Exception as e:
            print(f"Error creating contact request: {e}")
            conn.close()
            return None
    
    @staticmethod
    def create_data_removal_request(user_id, removal_type, specific_links, reason):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            # Convert list to string for storage
            specific_links_str = None
            if specific_links and len(specific_links) > 0:
                specific_links_str = ','.join(specific_links)
            
            c.execute('''
                INSERT INTO data_removal_requests (user_id, removal_type, specific_links, reason)
                VALUES (?, ?, ?, ?)
            ''', (user_id, removal_type, specific_links_str, reason))
            
            conn.commit()
            request_id = c.lastrowid
            conn.close()
            return request_id
        except Exception as e:
            print(f"Error creating data removal request: {e}")
            conn.close()
            return None
    
    @staticmethod
    def get_contact_requests_by_user(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT * FROM contact_requests 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            requests = [dict(row) for row in c.fetchall()]
            conn.close()
            return requests
        except Exception as e:
            print(f"Error fetching contact requests: {e}")
            conn.close()
            return []
    
    @staticmethod
    def get_data_removal_requests_by_user(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT * FROM data_removal_requests 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            requests = [dict(row) for row in c.fetchall()]
            conn.close()
            return requests
        except Exception as e:
            print(f"Error fetching data removal requests: {e}")
            conn.close()
            return []