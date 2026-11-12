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
      impactScore : Integer;  // AI-assigned 1-10
}

entity FetchLog {
  key id        : UUID;
      fetchedAt : DateTime;
      itemCount : Integer;
      status    : String(50);  // success | error
      message   : String(500);
}
