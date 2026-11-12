const cds = require('@sap/cds');

module.exports = class NewsService extends cds.ApplicationService {

  async init() {
    const { NewsItems, FetchLog } = this.entities;

    this.on('ingestNews', async (req) => {
      const { items } = req.data;
      if (!items || items.length === 0) {
        return 'No items provided';
      }

      const now = new Date().toISOString();

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

      await INSERT.into(FetchLog).entries({
        id:        cds.utils.uuid(),
        fetchedAt: now,
        itemCount: items.length,
        status:    'success',
        message:   `Ingested ${items.length} items`
      });

      return `Successfully ingested ${items.length} news items`;
    });

    this.on('READ', 'LatestNews', async (req, next) => {
      const cutoff = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      await DELETE.from(NewsItems).where({ fetchedAt: { '<': cutoff } });
      return next();
    });

    await super.init();
  }
};
