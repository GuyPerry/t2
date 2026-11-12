using news from '../db/schema';

service NewsService @(path: '/api') {

  // Latest top 3 news items (read-only for UI)
  @readonly
  entity LatestNews as projection on news.NewsItems
    order by fetchedAt desc, impactScore desc;

  // Write endpoint used by the Python agent
  entity NewsItems as projection on news.NewsItems;

  // Fetch log
  @readonly
  entity FetchLog   as projection on news.FetchLog;

  // Action: agent calls this to ingest a batch of news items
  action ingestNews(items: array of {
    headline    : String(500);
    summary     : String(2000);
    source      : String(200);
    url         : String(1000);
    publishedAt : DateTime;
    category    : String(100);
    impactScore : Integer;
  }) returns String;
}
