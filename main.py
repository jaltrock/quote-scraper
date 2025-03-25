from fastapi import FastAPI, BackgroundTasks
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

app = FastAPI()
DB_FILE = "quotes.db"
TOC_URL = "https://practicalguidetoevil.wordpress.com/table-of-contents/"

# Initialize Database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter TEXT UNIQUE,
                quote TEXT
            )
        """)
        conn.commit()

init_db()

# Function to get all chapter links
def get_chapter_links():
    response = requests.get(TOC_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.select("a[href*='/201']")]
    return links

# Function to scrape quotes from chapters
def get_chapter_quote(chapter_url):
    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quote_tag = soup.find("blockquote")
    return quote_tag.text.strip() if quote_tag else None

# Background task to scrape and store quotes with retry mechanism
def scrape_and_store(retries=5, delay=1):
    chapter_links = get_chapter_links()
    
    for link in chapter_links:
        quote = get_chapter_quote(link)
        if quote:
            for attempt in range(retries):
                try:
                    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT OR IGNORE INTO quotes (chapter, quote) VALUES (?, ?)", 
                            (link, quote)
                        )
                        conn.commit()
                    break  # Success, exit retry loop
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        print(f"Database is locked, retrying {attempt+1}/{retries}...")
                        time.sleep(delay)  # Wait before retrying
                    else:
                        raise  # If it's another error, raise it

@app.get("/quotes")
def get_quotes():
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chapter, quote FROM quotes")
        data = cursor.fetchall()
    return [{"chapter": row[0], "quote": row[1]} for row in data]

@app.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_and_store)
    return {"message": "Scraping started in the background."}
