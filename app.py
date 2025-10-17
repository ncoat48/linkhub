from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import init_db
from models import User, Link, Category, Contact
import os


app = Flask(__name__)
app.secret_key = 'linkhub-secret-key-2023'

# Initialize database
with app.app_context():
    init_db()

@app.route('/')
def index():
    # Check if user wants to see sensitive content from session or request
    show_sensitive = session.get('show_sensitive', False)
    if request.args.get('show_sensitive'):
        show_sensitive = request.args.get('show_sensitive', 'false').lower() == 'true'
        session['show_sensitive'] = show_sensitive
    
    categories = Category.get_all_categories()
    links = Link.get_all_links(include_sensitive=show_sensitive)
    
    # Organize links by category
    categories_dict = {}
    for category in categories:
        category_links = [link for link in links if link.get('category_name') == category['name']]
        if category_links:  # Only add categories that have links
            categories_dict[category['name']] = category_links
    
    # Get user info if logged in
    user = None
    user_likes = []
    user_bookmarks = []
    
    if 'user_id' in session:
        user = User.get_user_by_id(session['user_id'])
        user_likes = Link.get_user_likes(session['user_id'])
        user_bookmarks = Link.get_user_bookmarks(session['user_id'])
    
    return render_template('index.html', 
                         categories=categories_dict,
                         user=user,
                         user_likes=user_likes,
                         user_bookmarks=user_bookmarks,
                         show_sensitive=show_sensitive)

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not all([username, email, password, full_name]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    user_id = User.create_user(username, email, password, full_name)
    
    if user_id:
        session['user_id'] = user_id
        return jsonify({'success': True, 'message': 'User created successfully'})
    else:
        return jsonify({'success': False, 'message': 'Username or email already exists'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.verify_user(username, password)
    
    if user:
        session['user_id'] = user['id']
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('show_sensitive', None)
    return redirect(url_for('index'))

# Link management routes
@app.route('/api/links', methods=['GET'])
def get_links():
    category_id = request.args.get('category_id')
    include_sensitive = request.args.get('include_sensitive', 'false').lower() == 'true'
    
    if category_id:
        links = Link.get_links_by_category(int(category_id), include_sensitive)
    else:
        links = Link.get_all_links(include_sensitive)
    
    return jsonify(links)

@app.route('/api/links', methods=['POST'])
def create_link():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    data = request.get_json()
    title = data.get('title')
    url = data.get('url')
    description = data.get('description')
    image_url = data.get('image_url')
    category_id = data.get('category_id')
    is_sensitive = data.get('is_sensitive', False)
    
    if not all([title, url, category_id]):
        return jsonify({'success': False, 'message': 'Title, URL, and category are required'})
    
    link_id = Link.create_link(title, url, description, image_url, int(category_id), session['user_id'], is_sensitive)
    
    if link_id:
        return jsonify({'success': True, 'message': 'Link created successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to create link'})

# Like/Bookmark routes
@app.route('/api/links/<int:link_id>/like', methods=['POST'])
def like_link(link_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    success = Link.like_link(session['user_id'], link_id)
    return jsonify({'success': success, 'message': 'Link liked' if success else 'Already liked'})

@app.route('/api/links/<int:link_id>/unlike', methods=['POST'])
def unlike_link(link_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    success = Link.unlike_link(session['user_id'], link_id)
    return jsonify({'success': success, 'message': 'Link unliked'})

@app.route('/api/links/<int:link_id>/bookmark', methods=['POST'])
def bookmark_link(link_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    success = Link.bookmark_link(session['user_id'], link_id)
    return jsonify({'success': success, 'message': 'Link bookmarked' if success else 'Already bookmarked'})

@app.route('/api/links/<int:link_id>/unbookmark', methods=['POST'])
def unbookmark_link(link_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    success = Link.unbookmark_link(session['user_id'], link_id)
    return jsonify({'success': success, 'message': 'Link unbookmarked'})

# Filter preference route
@app.route('/api/filter/preference', methods=['POST'])
def set_filter_preference():
    data = request.get_json()
    show_sensitive = data.get('show_sensitive', False)
    
    session['show_sensitive'] = show_sensitive
    
    return jsonify({'success': True, 'show_sensitive': show_sensitive})

# Categories route
@app.route('/api/categories')
def get_categories():
    categories = Category.get_all_categories()
    return jsonify(categories)

# User profile and link management routes
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.get_user_by_id(session['user_id'])
    user_links = Link.get_user_links(session['user_id'])
    user_likes = Link.get_user_likes(session['user_id'])
    user_bookmarks = Link.get_user_bookmarks(session['user_id'])
    
    return render_template('profile.html', 
                         user=user,
                         user_links=user_links,
                         user_likes=user_likes,
                         user_bookmarks=user_bookmarks)

@app.route('/api/links/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    # Verify the link belongs to the user
    link = Link.get_link_by_id(link_id)
    if not link or link['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Link not found or access denied'})
    
    success = Link.delete_link(link_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Link deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete link'})
    
# Static pages
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Contact and data requests
@app.route('/api/contact', methods=['POST'])
def contact():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    data = request.get_json()
    request_type = data.get('type', 'general')
    subject = data.get('subject', '')
    message = data.get('message', '')
    user_email = data.get('email', '')
    content_reference = data.get('content_reference', '')
    
    if not message or not subject:
        return jsonify({'success': False, 'message': 'Subject and message are required'})
    
    # Add content reference to message if provided
    if content_reference and request_type == 'report':
        message = f"Content Reference: {content_reference}\n\n{message}"
    
    # Save to database
    request_id = Contact.create_contact_request(
        session['user_id'], 
        request_type, 
        subject, 
        message, 
        user_email
    )
    
    if request_id:
        # In a real application, you would also send an email notification here
        print(f"Contact request #{request_id} saved to database")
        return jsonify({
            'success': True, 
            'message': 'Your request has been submitted. We will respond within 24 hours.'
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to submit your request. Please try again.'})

@app.route('/api/data-removal', methods=['POST'])
def request_data_removal():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    data = request.get_json()
    removal_type = data.get('removal_type', 'account')
    specific_links = data.get('specific_links', [])
    reason = data.get('reason', '')
    confirmation = data.get('confirmation', False)
    
    if not confirmation:
        return jsonify({'success': False, 'message': 'Please confirm the data removal request'})
    
    # Save to database
    request_id = Contact.create_data_removal_request(
        session['user_id'],
        removal_type,
        specific_links,
        reason
    )
    
    if request_id:
        # In a real application, you would also send an email notification here
        print(f"Data removal request #{request_id} saved to database")
        
        # Different messages based on removal type
        if removal_type == 'account':
            message = 'Your account deletion request has been received and will be processed within 72 hours as required by data protection regulations.'
        elif removal_type == 'links':
            message = 'Your request to remove all your shared links has been received and will be processed within 72 hours.'
        else:
            message = 'Your request to remove specific links has been received and will be processed within 72 hours.'
            
        return jsonify({
            'success': True, 
            'message': message
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to submit your removal request. Please try again.'})

# Add a route to view user's previous requests
@app.route('/api/my-requests')
def get_my_requests():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    contact_requests = Contact.get_contact_requests_by_user(session['user_id'])
    removal_requests = Contact.get_data_removal_requests_by_user(session['user_id'])
    
    return jsonify({
        'success': True,
        'contact_requests': contact_requests,
        'removal_requests': removal_requests
    })

if __name__ == '__main__':
    app.run(debug=True)