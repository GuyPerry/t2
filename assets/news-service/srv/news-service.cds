using news from '../db/schema';

service NewsService @(path: '/api') {

  @readonly
  entity LatestNews as projection on news.NewsItems
    order by fetchedAt desc, impactScore desc;

  entity NewsItems as projection on news.NewsItems;

  @readonly
  entity FetchLog   as projection on news.FetchLog;

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
