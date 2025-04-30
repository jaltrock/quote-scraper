from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3
import requests
from bs4 import BeautifulSoup 
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ✅ Fix CORS so the frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] in development or your domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "quotes.db"
TOC_URL = "https://practicalguidetoevil.wordpress.com/table-of-contents/"

# Initialize Database
def init_db():
    try:
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
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

init_db()

# Function to get all chapter links and titles
def get_chapter_links():
    try:
        response = requests.get(TOC_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        chapters = []
        for li in soup.select("div.entry-content li"):
            link_tag = li.find("a")
            if link_tag and "href" in link_tag.attrs:
                chapter_title = link_tag.text.strip()
                chapter_url = link_tag["href"]
                chapters.append((chapter_title, chapter_url))

        logger.info(f"Found {len(chapters)} chapters")
        return chapters
    except Exception as e:
        logger.error(f"Error getting chapter links: {str(e)}")
        raise

# Function to scrape the first paragraph inside "entry-content"
def get_chapter_quote(chapter_url):
    try:
        response = requests.get(chapter_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find("div", class_="entry-content")
        if not content_div:
            logger.warning(f"No content div found for {chapter_url}")
            return None
        
        first_paragraph = content_div.find("p")
        if not first_paragraph:
            logger.warning(f"No paragraph found for {chapter_url}")
            return None
            
        quote = first_paragraph.get_text(strip=True)
        logger.info(f"Successfully scraped quote from {chapter_url}")
        return quote
    except Exception as e:
        logger.error(f"Error scraping quote from {chapter_url}: {str(e)}")
        return None

# Background task to scrape and store quotes
def scrape_and_store(retries=5, delay=1):
    try:
        chapter_links = get_chapter_links()
        logger.info(f"Starting to scrape {len(chapter_links)} chapters")
        
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
                        logger.info(f"Successfully stored quote for {chapter_title}")
                        break
                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e):
                            logger.warning(f"Database is locked, retrying {attempt+1}/{retries}...")
                            time.sleep(delay)
                        else:
                            logger.error(f"Database error for {chapter_title}: {str(e)}")
                            raise
    except Exception as e:
        logger.error(f"Error in scrape_and_store: {str(e)}")
        raise

@app.get("/quotes")
def get_quotes():
    try:
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chapter_title, chapter_url, quote FROM quotes ORDER BY id")
            data = cursor.fetchall()
            if not data:
                logger.warning("No quotes found in database")
                return []
            logger.info(f"Retrieved {len(data)} quotes")
            return [{"chapter": row[0], "url": row[1], "quote": row[2]} for row in data]
    except Exception as e:
        logger.error(f"Error getting quotes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(scrape_and_store)
        logger.info("Scraping process started in background")
        return {"message": "Scraping started in the background."}
    except Exception as e:
        logger.error(f"Error triggering scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
