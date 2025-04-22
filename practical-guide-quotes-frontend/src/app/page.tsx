"use client";

import { useEffect, useState } from "react";

type Quote = {
  chapter: string;
  quote: string;
};

export default function HomePage() {
  const [quotes, setQuotes] = useState<Quote[]>([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/quotes`)
      .then((res) => res.json())
      .then((data) => setQuotes(data))
      .catch((err) => console.error("Failed to load quotes:", err));
  }, []);

  let currentBook = 1;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Quotes from "A Practical Guide to Evil"
      </h1>

      {quotes.map((item, index) => {
        const isPrologue = item.chapter.toLowerCase().includes("prologue");
        let bookHeading = null;

        if (isPrologue) {
          bookHeading = (
            <h2 key={`book-${currentBook}`} className="text-2xl font-semibold mt-8 mb-4">
              Book {currentBook}
            </h2>
          );
          currentBook++;
        }

        return (
          <div key={index} className="mb-6">
            {bookHeading}
            <p className="text-lg italic">"{item.quote}"</p>
            <p className="text-sm text-gray-600 mt-2">— {item.chapter}</p>
          </div>
        );
      })}
    </div>
  );
}
