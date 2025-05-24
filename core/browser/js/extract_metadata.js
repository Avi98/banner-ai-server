() => {
  const metadata = {
    description:
      document.querySelector('meta[name="description"]')?.content || null,
    keywords: document.querySelector('meta[name="keywords"]')?.content || null,
    author: document.querySelector('meta[name="author"]')?.content || null,
    canonical: document.querySelector('link[rel="canonical"]')?.href || null,
    og_tags: {},
    twitter_tags: {},
    schema_org: null,
  };

  // Extract Open Graph tags
  const ogTags = document.querySelectorAll('meta[property^="og:"]');
  ogTags.forEach((tag) => {
    const property = tag.getAttribute("property").substring(3);
    metadata.og_tags[property] = tag.content;
  });

  // Extract Twitter tags
  const twitterTags = document.querySelectorAll('meta[name^="twitter:"]');
  twitterTags.forEach((tag) => {
    const property = tag.getAttribute("name").substring(8);
    metadata.twitter_tags[property] = tag.content;
  });

  // Extract Schema.org structured data
  const schemaScripts = document.querySelectorAll(
    'script[type="application/ld+json"]'
  );
  if (schemaScripts.length > 0) {
    try {
      const schemaData = [];
      schemaScripts.forEach((script) => {
        try {
          schemaData.push(JSON.parse(script.textContent));
        } catch (e) {
          // Skip invalid JSON
        }
      });
      metadata.schema_org = schemaData;
    } catch (e) {
      // Failed to parse JSON
    }
  }

  return metadata;
}