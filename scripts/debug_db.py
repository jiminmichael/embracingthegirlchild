#!/usr/bin/env python
import os
import sys
import sqlite3
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

def debug_images():
    # Connect to SQLite database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get all posts directly
    c.execute("SELECT * FROM main_post")
    rows = c.fetchall()
    
    # Get column names
    c.execute("PRAGMA table_info('main_post')")
    columns = c.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Found {len(rows)} posts in database")
    print(f"Columns: {', '.join(column_names)}\n")
    
    for row in rows:
        row_dict = dict(zip(column_names, row))
        print(f"Post ID: {row_dict['id']}")
        print(f"Title: {row_dict['title']}")
        print(f"Image: {row_dict['image']}")
        print("--------------------------------------------------")
    
    # After examining tables and columns
    c.execute('SELECT * FROM main_post')
    rows = c.fetchall()
    print(f"\nFound {len(rows)} total posts in database")
    
    conn.close()