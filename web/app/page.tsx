'use client';

import { useEffect, useState } from 'react';
import { getTodayBriefing, Briefing } from '@/lib/api';
import StoryCard from '@/components/StoryCard';
import Link from 'next/link';

export default function Home() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBriefing() {
      try {
        const data = await getTodayBriefing();
        setBriefing(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load briefing');
      } finally {
        setLoading(false);
      }
    }
    fetchBriefing();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading daily briefing...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Briefing Platform
          </h1>
          <p className="text-lg text-gray-600">
            Daily briefing for {briefing && new Date(briefing.briefing_date).toLocaleDateString()}
          </p>
        </div>

        <nav className="mb-6 flex gap-4">
          <Link href="/search" className="text-blue-600 hover:text-blue-800">
            Search
          </Link>
        </nav>

        {briefing && briefing.content && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <p className="text-gray-700">{briefing.content}</p>
          </div>
        )}

        <div className="mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Today's Stories ({briefing?.stories.length || 0})
          </h2>
          {briefing?.stories.length === 0 ? (
            <p className="text-gray-600">No stories available for today.</p>
          ) : (
            briefing?.stories.map((story) => (
              <StoryCard key={story.id} story={story} />
            ))
          )}
        </div>
      </div>
    </main>
  );
}
