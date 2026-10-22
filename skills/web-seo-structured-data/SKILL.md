---
name: web-seo-structured-data
description: 'Write JSON-LD structured data that Google actually uses: Organization/WebSite, Article/BlogPosting, Product with Offer and ratings, BreadcrumbList, FAQPage, plus LocalBusiness, Event and HowTo. Use when a user asks for "schema markup", "rich results", "rich snippets", "JSON-LD", "schema.org", "star ratings in Google", "FAQ schema", or "knowledge panel".'
---

# Structured data with JSON-LD

Structured data tells search engines what a page *is* (a product with a price, an article with an
author, a list of questions) so they can show rich results: breadcrumbs instead of a raw URL, star
ratings, prices, FAQ dropdowns, logo and social links in a knowledge panel. Google recommends
JSON-LD in a `<script type="application/ld+json">` block because it is independent of the HTML
and easy to generate. The rule that matters: markup must describe content that is visible on the
page. Hidden or invented data gets a manual action, not a rich result.

## Pattern

One script per page is fine; `@graph` lets several entities share one block and reference each
other by `@id`. This is a product page on a site with an organization, breadcrumbs and an FAQ.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://www.acme.com/#org",
      "name": "Acme",
      "url": "https://www.acme.com/",
      "logo": "https://www.acme.com/img/logo-600.png",
      "sameAs": ["https://x.com/acme", "https://www.linkedin.com/company/acme", "https://github.com/acme"]
    },
    {
      "@type": "WebSite",
      "@id": "https://www.acme.com/#website",
      "url": "https://www.acme.com/",
      "name": "Acme",
      "publisher": { "@id": "https://www.acme.com/#org" }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.acme.com/" },
        { "@type": "ListItem", "position": 2, "name": "Bags", "item": "https://www.acme.com/bags/" },
        { "@type": "ListItem", "position": 3, "name": "Canvas Tote" }
      ]
    },
    {
      "@type": "Product",
      "@id": "https://www.acme.com/bags/canvas-tote/#product",
      "name": "Canvas Tote",
      "image": ["https://www.acme.com/img/tote-1x1.jpg", "https://www.acme.com/img/tote-4x3.jpg", "https://www.acme.com/img/tote-16x9.jpg"],
      "description": "Heavy 16 oz cotton canvas tote with a zipped inner pocket.",
      "sku": "TOTE-BLU-01",
      "brand": { "@id": "https://www.acme.com/#org" },
      "offers": {
        "@type": "Offer",
        "url": "https://www.acme.com/bags/canvas-tote/",
        "price": "39.00",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "itemCondition": "https://schema.org/NewCondition",
        "shippingDetails": { "@type": "OfferShippingDetails", "shippingRate": { "@type": "MonetaryAmount", "value": "0", "currency": "USD" }, "shippingDestination": { "@type": "DefinedRegion", "addressCountry": "US" } },
        "hasMerchantReturnPolicy": { "@type": "MerchantReturnPolicy", "applicableCountry": "US", "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 30, "returnMethod": "https://schema.org/ReturnByMail", "returnFees": "https://schema.org/FreeReturn" }
      },
      "aggregateRating": { "@type": "AggregateRating", "ratingValue": "4.6", "reviewCount": "128" }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Is the tote machine washable?",
          "acceptedAnswer": { "@type": "Answer", "text": "Yes. Wash cold, hang dry; the canvas softens after the first wash." }
        }
      ]
    }
  ]
}
</script>
```

The article shape, for blog posts and docs:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Why we charge per seat",
  "description": "The reasoning behind Acme's pricing model.",
  "image": "https://www.acme.com/og/per-seat.png",
  "datePublished": "2026-10-01T09:00:00+00:00",
  "dateModified": "2026-10-15T14:30:00+00:00",
  "author": { "@type": "Person", "name": "Jane Doe", "url": "https://www.acme.com/team/jane" },
  "publisher": { "@id": "https://www.acme.com/#org" },
  "mainEntityOfPage": "https://www.acme.com/blog/per-seat"
}
```

Why these fields: Google's rich-result eligibility depends on specific required properties
(`Product` needs `name` plus `offers`, `review` or `aggregateRating`; `Article` needs `headline`,
`image`, `datePublished`, `author`; `BreadcrumbList` needs `position` and `name`, with `item`
optional on the last entry). Dates are ISO 8601 with timezone. Images are absolute URLs and, for
Article/Product, ideally in 1:1, 4:3 and 16:9 so Google can pick per surface.

## Variations

- **LocalBusiness** (shops, restaurants, agencies): `@type: "LocalBusiness"` or a subtype
  (`Restaurant`, `Dentist`), with `address` (PostalAddress), `geo`, `telephone`, `openingHoursSpecification`,
  `priceRange`. Keep NAP (name, address, phone) identical to your Google Business Profile.
- **Event**: `name`, `startDate`, `endDate`, `eventStatus`, `eventAttendanceMode`, `location`
  (`Place` with address, or `VirtualLocation` with `url`), `offers` with ticket URL.
- **HowTo / Recipe**: `step` array of `HowToStep` with `text`, or `recipeIngredient` plus
  `recipeInstructions`. Note Google retired most HowTo rich results in 2023; keep the markup only
  if the content truly is a how-to.
- **SoftwareApplication / VideoObject / Course** follow the same shape; check the current Google
  "structured data features" list before investing, since eligible types change.

## Pitfalls

- Markup for content that is not on the page: FAQs the user cannot see, reviews that do not exist,
  a "Product" on a category page. This is the main cause of manual actions.
- FAQ rich results now show only for well-known authoritative government and health sites; the
  markup is still valid and harmless, but do not expect dropdowns in results for a normal business.
- Invalid JSON: trailing commas, unescaped quotes in descriptions, smart quotes from a CMS. Pipe
  server-side data through `JSON.stringify` and escape `</script>` as `<\/script>` inside strings.
- Relative URLs or `http://` where the site is `https://`; `@id` values that differ between pages
  for the same organization (then Google sees multiple organizations).
- Duplicating with microdata or RDFa on the same page; conflicting values make Google ignore both.
  Pick JSON-LD only.
- Shipping the markup only through client-side JS after load. Googlebot usually executes it, but
  other engines and link scrapers do not; emit it in the HTML.
- Not testing. Run every template through Google's Rich Results Test and the Schema Markup
  Validator, then watch Search Console's "Enhancements" reports after deploy.

## Related skills

- `web-seo-meta-tags`
- `web-seo-content-structure`
- `web-nav-breadcrumbs`
- `web-layout-pricing-table`
- `web-ui-accordion`
- `web-ship-launch-checklist`
