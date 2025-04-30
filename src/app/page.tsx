type Quote = {
  chapter: string;
  quote: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default async function HomePage() {
  // First, trigger the scraping process
  try {
    await fetch(`${API_URL}/scrape`, {
      method: "POST",
    });
  } catch (error) {
    console.error("Failed to trigger scraping:", error);
  }

  // Then fetch the quotes
  let data: Quote[] = [];
  try {
    const res = await fetch(`${API_URL}/quotes`);
    if (!res.ok) {
      throw new Error(`Failed to fetch quotes: ${res.statusText}`);
    }
    data = await res.json();
  } catch (error) {
    console.error("Failed to fetch quotes:", error);
  }

  let currentBook = 1; // Start from Book 1

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Quotes from &quot;A Practical Guide to Evil&quot;
      </h1>

      {data.length === 0 ? (
        <div className="text-center text-gray-500">
          <p>No quotes available yet. Please wait while we collect them...</p>
          <p className="text-sm mt-2">If this message persists, check if the backend server is running.</p>
        </div>
      ) : (
        data.map((item, index) => {
          // Check if the current chapter is "Prologue" and insert a Book heading before it
          const isPrologue = item.chapter.toLowerCase().includes("prologue");
          let bookHeading = null;

          if (isPrologue) {
            bookHeading = (
              <h2 key={`book-${currentBook}`} className="text-2xl font-semibold mt-8 mb-4">
                Book {currentBook}
              </h2>
            );
            currentBook++; // Move to the next book after the Prologue
          }

          return (
            <div key={index} className="mb-6">
              {bookHeading} {/* Insert the book title before the prologue */}
              <p className="text-lg italic">{item.quote}</p>
              <p className="text-sm text-gray-600 mt-2">— {item.chapter}</p>
            </div>
          );
        })
      )}
    </div>
  );
}