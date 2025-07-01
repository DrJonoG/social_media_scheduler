import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Create and return a MySQL database connection.
    
    Returns:
        mysql.connector.connection: Database connection object
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def execute_query(query, params=None, fetch=False, dictionary=False):
    """
    Execute a SQL query with optional parameters.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch (bool): Whether to fetch and return results
        dictionary (bool): Whether to return results as dictionaries
        
    Returns:
        list or None: Query results if fetch=True, None otherwise
    """
    conn = get_connection()
    cursor_class = conn.cursor(dictionary=True) if dictionary else conn.cursor()
    cursor = cursor_class

    cursor.execute(query, params or ())

    result = None
    if fetch:
        result = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return result

def insert_post(platform, content, media_path, scheduled_time, status="scheduled"):
    """
    Insert a new post into the posts table.
    
    Args:
        platform (str): Social media platform name
        content (str): Post content text
        media_path (str): Path to media file (if any)
        scheduled_time (datetime): When the post should be published
        status (str): Post status (default: "scheduled")
    """
    conn = get_connection()
    cursor = conn.cursor()
    sql = '''
        INSERT INTO posts (platform, content, media_path, scheduled_time, status)
        VALUES (%s, %s, %s, %s, %s)
    '''
    cursor.execute(sql, (platform, content, media_path, scheduled_time, status))
    conn.commit()
    cursor.close()
    conn.close()

def get_due_posts(current_time):
    """
    Get all posts that are due for publishing.
    
    Args:
        current_time (datetime): Current timestamp to compare against
        
    Returns:
        list: List of posts due for publishing
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = '''
        SELECT * FROM posts
        WHERE scheduled_time <= %s AND status = 'scheduled'
    '''
    cursor.execute(sql, (current_time,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def update_post_status(post_id, new_status):
    """
    Update the status of a post.
    
    Args:
        post_id (int): ID of the post to update
        new_status (str): New status value (e.g., 'published', 'failed')
    """
    conn = get_connection()
    cursor = conn.cursor()
    sql = '''
        UPDATE posts
        SET status = %s
        WHERE id = %s
    '''
    cursor.execute(sql, (new_status, post_id))
    conn.commit()
    cursor.close()
    conn.close() 