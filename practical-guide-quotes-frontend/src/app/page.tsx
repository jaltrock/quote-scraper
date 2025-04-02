type Quote = {
  chapter: string;
  quote: string;
};

export default async function HomePage() {
  const res = await fetch("http://127.0.0.1:8000/quotes");
  const data: Quote[] = await res.json();


  let currentBook = 1; // Start from Book 1

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Quotes from &quot;A Practical Guide to Evil&quot;
      </h1>

      {data.map((item, index) => {
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
      })}
    </div>
  );
}