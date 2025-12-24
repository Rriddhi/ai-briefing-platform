'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getTopicStories, TopicStories } from '@/lib/api';
import StoryCard from '@/components/StoryCard';
import Link from 'next/link';

export default function TopicPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [data, setData] = useState<TopicStories | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTopicStories() {
      try {
        const result = await getTopicStories(slug);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load topic stories');
      } finally {
        setLoading(false);
      }
    }
    fetchTopicStories();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading topic stories...</div>
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
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {data?.topic.name}
          </h1>
          <p className="text-lg text-gray-600">
            {data?.total || 0} stories
          </p>
        </div>

        {data && data.stories.length === 0 ? (
          <p className="text-gray-600">No stories found for this topic.</p>
        ) : (
          data?.stories.map((story) => (
            <StoryCard key={story.id} story={story} />
          ))
        )}
      </div>
    </main>
  );
}

