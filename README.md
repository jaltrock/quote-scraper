# Practical Guide to Evil Quote Scraper

This program will collect the quotes from the beginning of each chapter of the series A Practical Guide to Evil:

https://practicalguidetoevil.wordpress.com/summary/

The quotes will then be compiled in a single page.

For the backend, I used Python and FastAPI to handle the scraping and API requests. 
On the frontend, I've displayed the quotes using Next.js.

## Backend Setup and Usage

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation
1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Backend
1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
The server will start at `http://localhost:8000`

2. Initialize the database and trigger scraping:
```bash
# Using curl:
curl -X POST http://localhost:8000/scrape

# Or using Python requests:
python -c "import requests; requests.post('http://localhost:8000/scrape')"
```

3. Verify the quotes are being collected:
```bash
# Using curl:
curl http://localhost:8000/quotes

# Or using Python requests:
python -c "import requests; print(requests.get('http://localhost:8000/quotes').json())"
```

### API Endpoints
- `GET /`: Health check endpoint
- `GET /quotes`: Retrieve all collected quotes
- `POST /scrape`: Trigger the scraping process (runs in background)

## Frontend Setup and Usage

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Deployment

### Backend Deployment (Render.com)

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `PYTHON_VERSION`: `3.8.0`
4. Deploy the service
5. Once deployed, note the service URL (e.g., `https://your-app.onrender.com`)

### Frontend Deployment (Vercel)

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Configure the project:
   - Framework Preset: Next.js
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL`: Your Render.com backend URL (e.g., `https://your-app.onrender.com`)
4. Deploy the project

### Post-Deployment Steps

1. After both services are deployed, trigger the scraping process:
```bash
curl -X POST https://your-app.onrender.com/scrape
```

2. Verify the quotes are being collected:
```bash
curl https://your-app.onrender.com/quotes
```

3. Visit your Vercel deployment URL to see the quotes displayed

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
