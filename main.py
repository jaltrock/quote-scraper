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
                chapter_title TEXT,
                chapter_url TEXT UNIQUE,
                quote TEXT
            )
        """)
        conn.commit()

init_db()

# Function to get all chapter links and titles
def get_chapter_links():
    response = requests.get(TOC_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    chapters = []
    
    # Find all <li> elements inside div.entry-content
    for li in soup.select("div.entry-content li"):
        link_tag = li.find("a")
        if link_tag and "href" in link_tag.attrs:
            chapter_title = link_tag.text.strip()
            chapter_url = link_tag["href"]
            chapters.append((chapter_title, chapter_url))

    return chapters

# Function to scrape the first paragraph inside "entry-content"
def get_chapter_quote(chapter_url):
    response = requests.get(chapter_url)
    if response.status_code != 200:
        return None  # Skip if page can't be loaded

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the main content div
    content_div = soup.find("div", class_="entry-content")
    if not content_div:
        return None  # If div is missing, return None
    
    # Get the first paragraph inside entry-content
    first_paragraph = content_div.find("p")
    
    return first_paragraph.get_text(strip=True) if first_paragraph else None

# Background task to scrape and store quotes
def scrape_and_store(retries=5, delay=1):
    chapter_links = get_chapter_links()
    
    for chapter_title, chapter_url in chapter_links:
        quote = get_chapter_quote(chapter_url)
        if quote:
            for attempt in range(retries):
                try:
                    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT OR IGNORE INTO quotes (chapter_title, chapter_url, quote) VALUES (?, ?, ?)", 
                            (chapter_title, chapter_url, quote)
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
        cursor.execute("SELECT chapter_title, chapter_url, quote FROM quotes ORDER BY id")
        data = cursor.fetchall()
    return [{"chapter": row[0], "url": row[1], "quote": row[2]} for row in data]

@app.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_and_store)
    return {"message": "Scraping started in the background."}
