const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Topic {
  id: number;
  name: string;
  slug: string;
}

export interface Citation {
  id: number;
  citation_text: string | null;
  url: string;
}

export interface ScoreBreakdown {
  relevance_score: number;
  impact_score: number;
  credibility_score: number;
  novelty_score: number;
  corroboration_score: number;
}

export interface Story {
  id: number;
  title: string;
  summary: string | null;
  why_this_matters: string | null;
  what_to_watch_next: string | null;
  score: number;
  ranking_rationale: string | null;
  score_breakdown: ScoreBreakdown | null;
  citations: Citation[];
  topics: Topic[];
  created_at: string;
}

export interface Briefing {
  id: number;
  briefing_date: string;
  content: string | null;
  stories: Story[];
}

export interface TopicStories {
  topic: Topic;
  stories: Story[];
  total: number;
}

export interface SearchResult {
  query: string;
  stories: Story[];
  total: number;
}

export async function getTodayBriefing(): Promise<Briefing> {
  const res = await fetch(`${API_URL}/briefing/today`);
  if (!res.ok) throw new Error('Failed to fetch briefing');
  return res.json();
}

export async function getTopicStories(topicSlug: string): Promise<TopicStories> {
  const res = await fetch(`${API_URL}/topics/${topicSlug}`);
  if (!res.ok) throw new Error('Failed to fetch topic stories');
  return res.json();
}

export async function getStory(clusterId: number): Promise<Story> {
  const res = await fetch(`${API_URL}/stories/${clusterId}`);
  if (!res.ok) throw new Error('Failed to fetch story');
  return res.json();
}

export async function searchStories(query: string): Promise<SearchResult> {
  const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Failed to search stories');
  return res.json();
}

