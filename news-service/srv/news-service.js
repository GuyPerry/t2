const cds = require('@sap/cds');

module.exports = class NewsService extends cds.ApplicationService {

  async init() {
    const { NewsItems, FetchLog } = this.entities;

    // ingestNews action — called by the Python agent every hour
    this.on('ingestNews', async (req) => {
      const { items } = req.data;
      if (!items || items.length === 0) {
        return 'No items provided';
      }

      const now = new Date().toISOString();

      // Persist each news item
      for (const item of items) {
        await INSERT.into(NewsItems).entries({
          id:          cds.utils.uuid(),
          headline:    item.headline,
          summary:     item.summary,
          source:      item.source,
          url:         item.url,
          publishedAt: item.publishedAt || now,
          fetchedAt:   now,
          category:    item.category || 'Science & Technology',
          impactScore: item.impactScore || 5
        });
      }

      // Log the fetch
      await INSERT.into(FetchLog).entries({
        id:        cds.utils.uuid(),
        fetchedAt: now,
        itemCount: items.length,
        status:    'success',
        message:   `Ingested ${items.length} items`
      });

      return `Successfully ingested ${items.length} news items`;
    });

    // Clean up items older than 24 hours to keep the DB lean
    this.on('READ', 'LatestNews', async (req, next) => {
      const cutoff = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      await DELETE.from(NewsItems).where({ fetchedAt: { '<': cutoff } });
      return next();
    });

    await super.init();
  }
};
