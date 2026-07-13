import json
import sys

sys.path.insert(0, ".")
from brand_pipeline.csv_utils import load_rows

rows = load_rows("Brand/Input/Button qs Brand focus - Sheet1_output.csv")

EXTRACTIONS = [
    {
        "descriptors": ["commerce optimization platform", "AI-powered commerce optimization platform"],
        "figures": [{"value": "$1 billion", "referent": "2024 monthly commerce driven through the platform"}],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
        ],
    },
    {
        "descriptors": ["commerce optimization layer", "used in ecommerce", "Improve attribution"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/post/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023",
            "https://www.prnewswire.com/news-releases/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023-302006644.html",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
            "https://martechrecord.com/interviews/leadership-series/qa-how-button-is-powering-creator-commerce-in-a-fractured-ecosystem/",
        ],
    },
    {
        "descriptors": ["optimization and routing layer"],
        "figures": [
            {"value": "$100B+", "referent": "total commerce driven"},
            {"value": "14.4B", "referent": "shopping journeys"},
            {"value": "22M", "referent": "app installs"},
            {"value": "38%", "referent": "conversion lift"},
            {"value": "42%", "referent": "sales-per-tap lift"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://developer.usebutton.com/",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
        ],
    },
    {
        "descriptors": [
            "marketing / commerce optimization tool",
            "marketing technology platform",
            "Marketing tool",
            "Commerce optimization platform",
            "Affiliate / creator marketing infrastructure",
            "commerce optimization layer",
        ],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/button-the-worlds-leading-mobile-experience-platform-surpasses-8b-in-commerce-driven",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
            "https://www.prnewswire.com/news-releases/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023-302006644.html",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
        ],
    },
    {
        "descriptors": [],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://www.usebutton.com/full-service-network",
            "https://www.prnewswire.com/news-releases/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023-302006644.html",
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
        ],
    },
    {
        "descriptors": [],
        "figures": [
            {"value": "$1B", "referent": "monthly commerce driven"},
            {"value": "$25B", "referent": "all-time commerce on the platform"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://www.usebutton.com/post/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
        ],
    },
    {
        "descriptors": ["commerce optimization infrastructure", "optimization layer"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/post/buttons-commerce-optimization-platform-launches-button-for-publishers",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
        ],
    },
    {
        "descriptors": ["affiliate / creator-commerce monetization layer"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/",
            "https://www.prnewswire.com/news-releases/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023-302006644.html",
            "https://www.usebutton.com/tap",
            "https://www.usebutton.com/post/buttons-creator-network-and-publisher-solutions-are-the-easiest-way-to-maximize-revenue-from-your-commerce-strategies",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://www.posttap.com/",
            "https://martechrecord.com/interviews/leadership-series/qa-how-button-is-powering-creator-commerce-in-a-fractured-ecosystem/",
        ],
    },
    {
        "descriptors": ["AI-powered commerce optimization technology", "AI-powered tool", "commerce optimization layer", "no-code approach"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://buttonandbrew.com/full-service-network.html",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/post/button-surpasses-1-billion-in-commerce-driven-monthly-as-retailers-and-publishers-leverage-buttons-ai-powered-commerce-optimization-platform",
        ],
    },
    {
        "descriptors": [],
        "figures": [],
        "sources": [
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
        ],
    },
    {
        "descriptors": ["custom-priced performance/commerce optimization platform", "tailored commerce optimization"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/for-creators",
            "https://www.usebutton.com/dynamic-decisioning",
            "https://impact.com/technology-partners/directory/button",
            "https://www.trustradius.com/products/button/pricing",
        ],
    },
    {
        "descriptors": ["custom / enterprise pricing", "professional-grade platform"],
        "figures": [
            {"value": "$100B+", "referent": "total commerce driven"},
            {"value": "5,000+", "referent": "apps optimized"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/for-creators",
            "https://www.usebutton.com/full-service-network",
            "https://www.trustradius.com/products/button/pricing",
        ],
    },
    {
        "descriptors": [],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/product-listing-ads",
            "https://www.trustradius.com/products/button/pricing",
        ],
    },
    {
        "descriptors": [],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/contact-us",
            "https://www.usebutton.com/for-creators",
            "https://www.usebutton.com/product-listing-ads",
            "https://building.usebutton.com/button-ios/latest/index.html",
            "https://www.usebutton.com/dynamic-decisioning",
        ],
    },
    {
        "descriptors": ["commerce optimization platform"],
        "figures": [
            {"value": "$25B", "referent": "all-time commerce"},
            {"value": "$2.9B", "referent": "2025 app gross merchandise sales"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://www.prnewswire.com/news-releases/large-retailer-wins-and-growth-in-the-creator-economy-drive-button-to-surpass-10-billion-in-mobile-commerce-driven-in-2023-302006644.html",
        ],
    },
    {
        "descriptors": ["commerce optimization platform"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/",
            "https://www.prnewswire.com/news-releases/buttons-commerce-optimization-platform-launches-button-for-publishers-302119089.html",
            "https://martech360.com/news/buttons-commerce-optimization-platform-launches-button-for-publishers/",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
            "https://www.norwest.com/?case_studies=button-win-win-win-mobile-commerce-solution",
            "https://impact.com/",
            "https://rakutenadvertising.com/",
            "https://www.cj.com/",
        ],
    },
    {
        "descriptors": [
            "affiliate/mobile commerce platform",
            "legitimate company",
            "mobile commerce technology company",
            "mobile commerce platform",
            "legitimate",
        ],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/full-service-network",
            "https://www.norwest.com/?case_studies=button-win-win-win-mobile-commerce-solution",
            "https://www.cbinsights.com/company/button",
            "https://pitchbook.com/profiles/company/63693-37",
            "https://craft.co/button",
            "https://www.scam-detector.com/validator/button-com-review/",
        ],
    },
    {
        "descriptors": [
            "trustworthy",
            "legitimate",
            "B2B commerce/affiliate marketing company",
            "AI-powered commerce optimization platform",
            "a mobile experience platform",
            "marketing/commerce technology vendor",
            "legitimate",
            "credible",
        ],
        "figures": [
            {"value": "2014", "referent": "year Button began operating"},
            {"value": "$25B+", "referent": "all-time commerce (2025 announcement)"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.cbinsights.com/company/button",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://www.norwest.com/?case_studies=button-win-win-win-mobile-commerce-solution",
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
            "https://impact.com/marketing-intelligence/ai-driven-affiliate-marketing-button-and-impact-com-integration/",
            "https://www.usebutton.com/support/privacy-policy",
        ],
    },
    {
        "descriptors": [],
        "figures": [
            {"value": "2014", "referent": "year Button was founded"},
            {"value": "12 years", "referent": "how long Button has been operating as of July 2026"},
        ],
        "sources": [
            "https://www.usebutton.com/post/button-raises-30-million-in-series-c-funding-to-build-the-future-of-mobile-commerce",
            "https://www.cbinsights.com/company/button",
            "https://tracxn.com/d/companies/button/__XVH3wS1CMICt-WSn5jt7vPEdQu9HCfVjIP_wzMJp9vA",
        ],
    },
    {
        "descriptors": [],
        "figures": [
            {"value": "2x", "referent": "Uber affiliate-program revenue increase via PostTap App"},
            {"value": "165%", "referent": "Sam's Club total mobile affiliate revenue increase"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/walmart-buzzfeed-and-others-join-buttons-growing-marketplace",
            "https://www.usebutton.com/post/drop-doubles-down-on-personalized-content-in-partnership-with-button",
            "https://www.usebutton.com/post/powering-mobile-commerce-for-leading-shopping-app-ibotta",
            "https://www.usebutton.com/post/how-button-doubled-affiliate-revenue-for-uber",
            "https://www.usebutton.com/post/sams-club-experienced-a-165-increase-in-total-mobile-affiliate-revenue-with-buttons-reach",
            "https://www.usebutton.com/post/hotels-com-supercharged-their-marketing-program-with-button-posttap",
            "https://www.usebutton.com/post/impact-com-leveraging-buttons-mobile-commerce-optimization-platform-sees-apps-drive-200-the-revenue-of-web-journeys",
            "https://www.usebutton.com/post/button-cj-increase-influencer-conversion-rates-by-over-400",
            "https://www.usebutton.com/post/button-launches-reach",
            "https://www.usebutton.com/post/sams-club-partners-with-button-and-rakuten-advertising-to-transform-its-affiliate-program-through-reach",
            "https://www.usebutton.com/post/case-study-how-buzzfeed-scaled-mobile-revenue-through-a-content-and-commerce-strategy",
        ],
    },
    {
        "descriptors": [],
        "figures": [
            {"value": "1.3M", "referent": "app installs"},
            {"value": "2.7x", "referent": "in-app conversion rate vs. mobile web"},
            {"value": "110%", "referent": "higher revenue per tap in app"},
            {"value": "200%", "referent": "revenue of web journeys"},
            {"value": "175%", "referent": "increase in app installs"},
            {"value": "55%", "referent": "increase in app-to-app sales"},
            {"value": "40%", "referent": "higher mobile affiliate revenue"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/awin-and-button-more-than-double-in-app-conversion-rates",
            "https://www.awin.com/us/affiliate-marketing/button-double-conversion",
            "https://www.usebutton.com/post/impact-com-leveraging-buttons-mobile-commerce-optimization-platform-sees-apps-drive-200-the-revenue-of-web-journeys",
            "https://junction.cj.com/article/cj-x-button-clients-see-incremental-value-from-improved-mobile-experiences",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://developer.usebutton.com/docs/publishers-ios-app-setup",
        ],
    },
    {
        "descriptors": [],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/post/how-button-works-with-mobile-measurement-partners",
            "https://www.accelerationpartners.com/resources/partner-qa-button/",
        ],
    },
    {
        "descriptors": ["app deep linking platform"],
        "figures": [],
        "sources": [
            "https://www.usebutton.com/dynamic-decisioning",
            "https://www.usebutton.com/post/button-launches-reach",
            "https://www.usebutton.com/post/buttons-creator-network-and-publisher-solutions-are-the-easiest-way-to-maximize-revenue-from-your-commerce-strategies",
            "https://www.posttap.com/",
        ],
    },
    {
        "descriptors": ["mobile commerce optimization platform", "enterprise/growth platform", "conversion and attribution layer"],
        "figures": [
            {"value": "$25B", "referent": "all-time commerce on the platform"},
            {"value": "$2.9B", "referent": "2025 app GMS"},
        ],
        "sources": [
            "https://www.usebutton.com/",
            "https://www.usebutton.com/full-service-network",
            "https://www.usebutton.com/post/button-launches-reach",
            "https://www.usebutton.com/category/case-studies",
            "https://psgequity.com/news/button-secures-strategic-growth-investment-from-psg",
            "https://impact.com/marketing-intelligence/ai-driven-affiliate-marketing-button-and-impact-com-integration/",
            "https://www.usebutton.com/post/button-surpasses-25-billion-in-all-time-commerce-on-the-platform-with-2025-proving-to-be-a-breakout-year-powered-by-the-creator-economy-and-continued-growth-of-commerce-media-and-affiliate-marketing",
            "https://www.posttap.com/",
            "https://tei.forrester.com/go/button/button/",
            "https://psgequity.com/portfolio/button",
            "https://www.usebutton.com/for-creators",
            "https://www.trustradius.com/products/button/pricing",
        ],
    },
]

assert len(rows) == len(EXTRACTIONS), f"{len(rows)} rows vs {len(EXTRACTIONS)} extractions"

with open("Brand/Output/extractions_cache.jsonl", "w", encoding="utf-8") as f:
    for i, (row, extraction) in enumerate(zip(rows, EXTRACTIONS)):
        record = {
            "row_index": i,
            "query": row["query"],
            "response": row["response"],
            "descriptors": extraction["descriptors"],
            "figures": extraction["figures"],
            "sources": extraction["sources"],
        }
        f.write(json.dumps(record) + "\n")

print(f"Wrote {len(rows)} records to Brand/Output/extractions_cache.jsonl")
