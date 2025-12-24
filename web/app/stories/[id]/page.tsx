'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getStory, Story } from '@/lib/api';
import Link from 'next/link';

export default function StoryDetailPage() {
  const params = useParams();
  const id = parseInt(params.id as string);
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRationale, setShowRationale] = useState(false);
  const [showBreakdown, setShowBreakdown] = useState(false);

  useEffect(() => {
    async function fetchStory() {
      try {
        const data = await getStory(id);
        setStory(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load story');
      } finally {
        setLoading(false);
      }
    }
    fetchStory();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading story...</div>
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-600">Error: {error || 'Story not found'}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Home
        </Link>

        <article className="bg-white rounded-lg shadow-md p-8">
          <div className="flex justify-between items-start mb-4">
            <h1 className="text-3xl font-bold text-gray-900">{story.title}</h1>
            <span className="text-sm font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded">
              Score: {story.score.toFixed(2)}
            </span>
          </div>

          <div className="flex flex-wrap gap-2 mb-6">
            {story.topics.map((topic) => (
              <Link
                key={topic.id}
                href={`/topics/${topic.slug}`}
                className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200"
              >
                {topic.name}
              </Link>
            ))}
          </div>

          {story.summary && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Summary</h2>
              <p className="text-gray-700 leading-relaxed">{story.summary}</p>
            </div>
          )}

          {story.why_this_matters && (
            <div className="mb-6 bg-blue-50 p-4 rounded-lg">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Why This Matters</h2>
              <p className="text-gray-700 leading-relaxed">{story.why_this_matters}</p>
            </div>
          )}

          {story.what_to_watch_next && (
            <div className="mb-6 bg-yellow-50 p-4 rounded-lg">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">What to Watch Next</h2>
              <p className="text-gray-700 leading-relaxed">{story.what_to_watch_next}</p>
            </div>
          )}

          {story.ranking_rationale && (
            <div className="mb-6">
              <button
                onClick={() => setShowRationale(!showRationale)}
                className="text-lg font-semibold text-blue-600 hover:text-blue-800"
              >
                {showRationale ? '▼' : '▶'} Why Ranked?
              </button>
              {showRationale && (
                <p className="mt-2 text-gray-700 bg-gray-50 p-4 rounded">
                  {story.ranking_rationale}
                </p>
              )}
            </div>
          )}

          {story.score_breakdown && (
            <div className="mb-6">
              <button
                onClick={() => setShowBreakdown(!showBreakdown)}
                className="text-lg font-semibold text-blue-600 hover:text-blue-800"
              >
                {showBreakdown ? '▼' : '▶'} Score Breakdown
              </button>
              {showBreakdown && (
                <div className="mt-2 bg-gray-50 p-4 rounded">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="font-medium text-gray-700">Relevance (30%)</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(story.score_breakdown.relevance_score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Impact (25%)</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(story.score_breakdown.impact_score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Credibility (20%)</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(story.score_breakdown.credibility_score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Novelty (15%)</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(story.score_breakdown.novelty_score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="col-span-2">
                      <div className="font-medium text-gray-700">Corroboration (10%)</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(story.score_breakdown.corroboration_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {story.citations.length > 0 && (
            <div className="border-t pt-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Citations</h2>
              <ul className="space-y-3">
                {story.citations.map((citation) => (
                  <li key={citation.id} className="flex items-start">
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline flex-1"
                    >
                      {citation.citation_text || citation.url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </article>
      </div>
    </main>
  );
}

