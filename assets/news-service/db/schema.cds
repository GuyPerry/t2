namespace news;

entity NewsItems {
  key id          : UUID;
      headline    : String(500);
      summary     : String(2000);
      source      : String(200);
      url         : String(1000);
      publishedAt : DateTime;
      fetchedAt   : DateTime;
      category    : String(100);
      impactScore : Integer;
}

entity FetchLog {
  key id        : UUID;
      fetchedAt : DateTime;
      itemCount : Integer;
      status    : String(50);
      message   : String(500);
}
