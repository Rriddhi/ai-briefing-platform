'use client';

import { Story } from '@/lib/api';
import Link from 'next/link';
import { useState } from 'react';

interface StoryCardProps {
  story: Story;
  showScore?: boolean;
}

export default function StoryCard({ story, showScore = true }: StoryCardProps) {
  const [showRationale, setShowRationale] = useState(false);
  const [showBreakdown, setShowBreakdown] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-2">
        <Link href={`/stories/${story.id}`}>
          <h3 className="text-xl font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
            {story.title}
          </h3>
        </Link>
        {showScore && (
          <span className="text-sm font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded">
            Score: {story.score.toFixed(2)}
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        {story.topics.map((topic) => (
          <Link
            key={topic.id}
            href={`/topics/${topic.slug}`}
            className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200"
          >
            {topic.name}
          </Link>
        ))}
      </div>

      {story.summary && (
        <p className="text-gray-700 mb-4">{story.summary}</p>
      )}

      {story.ranking_rationale && (
        <div className="mb-4">
          <button
            onClick={() => setShowRationale(!showRationale)}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showRationale ? '▼' : '▶'} Why ranked?
          </button>
          {showRationale && (
            <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded">
              {story.ranking_rationale}
            </p>
          )}
        </div>
      )}

      {story.score_breakdown && (
        <div className="mb-4">
          <button
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showBreakdown ? '▼' : '▶'} Score Breakdown
          </button>
          {showBreakdown && (
            <div className="mt-2 bg-gray-50 p-3 rounded text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>Relevance: {(story.score_breakdown.relevance_score * 100).toFixed(0)}%</div>
                <div>Impact: {(story.score_breakdown.impact_score * 100).toFixed(0)}%</div>
                <div>Credibility: {(story.score_breakdown.credibility_score * 100).toFixed(0)}%</div>
                <div>Novelty: {(story.score_breakdown.novelty_score * 100).toFixed(0)}%</div>
                <div className="col-span-2">Corroboration: {(story.score_breakdown.corroboration_score * 100).toFixed(0)}%</div>
              </div>
            </div>
          )}
        </div>
      )}

      {story.citations.length > 0 && (
        <div className="border-t pt-3">
          <p className="text-xs font-medium text-gray-500 mb-2">Citations:</p>
          <ul className="space-y-1">
            {story.citations.map((citation) => (
              <li key={citation.id}>
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                >
                  {citation.citation_text || citation.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

