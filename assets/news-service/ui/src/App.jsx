import React, { useState, useEffect, useCallback } from 'react';
import {
  ShellBar,
  Card,
  CardHeader,
  Text,
  Badge,
  Button,
  BusyIndicator
} from '@ui5/webcomponents-react';
import './App.css';

const POLL_INTERVAL_MS = 60 * 1000;

function impactLabel(score) {
  if (score >= 8) return { text: 'Critical', colorScheme: '3' };
  if (score >= 5) return { text: 'High Impact', colorScheme: '2' };
  return { text: 'Notable', colorScheme: '6' };
}

function timeAgo(isoString) {
  if (!isoString) return '';
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 60000);
  if (diff < 1) return 'Just now';
  if (diff < 60) return `${diff}m ago`;
  const h = Math.floor(diff / 60);
  return h === 1 ? '1 hour ago' : `${h} hours ago`;
}

export default function App() {
  const [news, setNews] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchNews = useCallback(async () => {
    try {
      const res = await fetch('/api/LatestNews?$top=3&$orderby=fetchedAt%20desc,impactScore%20desc');
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      setNews(data.value || []);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch news:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNews();
    const timer = setInterval(fetchNews, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [fetchNews]);

  const handleRefresh = () => {
    setLoading(true);
    fetchNews();
  };

  return (
    <div className="app">
      <ShellBar
        logo={<span style={{ fontSize: '1.4rem' }}>🔬</span>}
        primaryTitle="Breaking Science & Tech"
        secondaryTitle="Top 3 Global Stories — Updated Every Hour"
      />

      <div className="content">
        <div className="toolbar">
          <Text className="update-time">
            {lastUpdate ? `Last refreshed: ${lastUpdate.toLocaleTimeString()}` : 'Loading…'}
          </Text>
          <Button icon="refresh" onClick={handleRefresh} design="Transparent">
            Refresh
          </Button>
        </div>

        {loading && (
          <div className="loading-center">
            <BusyIndicator active size="Large" text="Fetching latest stories…" />
          </div>
        )}

        {!loading && news.length === 0 && (
          <div className="empty-state">
            <span style={{ fontSize: '3rem' }}>📡</span>
            <Text style={{ marginTop: '1rem', fontSize: '1.1rem', color: '#666' }}>
              No stories yet — the AI agent will post the top 3 stories at the next run.
            </Text>
          </div>
        )}

        <div className="news-grid">
          {news.map((item, idx) => {
            const impact = impactLabel(item.impactScore);
            return (
              <Card
                key={item.id || idx}
                className="news-card"
                header={
                  <CardHeader
                    titleText={item.headline}
                    subtitleText={`${item.source || 'Unknown'} · ${timeAgo(item.publishedAt)}`}
                    action={
                      <Badge colorScheme={impact.colorScheme}>{impact.text}</Badge>
                    }
                  />
                }
              >
                <div className="card-body">
                  <Text className="summary-text">{item.summary}</Text>
                  <div className="card-footer">
                    <Badge colorScheme="8">{item.category || 'Science & Technology'}</Badge>
                    {item.url && item.url !== 'N/A' && (
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="read-more">
                        Read full story →
                      </a>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
