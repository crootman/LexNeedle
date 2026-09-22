---
name: tavily-search
description: Use this skill when using the Tavily Search MCP server.
---

# Tavily MCP Server — Usage Rules

Tavily searches and reads the live web. Use it instead of relying on potentially stale training data when you need current information, facts beyond your knowledge cutoff, or content from specific URLs.

## Core Principle

**Pick the right tool for the job.** Tavily exposes five tools, each tuned for a different shape of web task: search, extract, map, crawl, and research. Default to the most specific tool that fits the question — don't reach for `research` when a `search` will do.

## When to Use Tavily

Use Tavily whenever the task involves:

- Looking up current information, news, or recent events (training data may be stale)
- Verifying facts, statistics, or claims against live sources
- Researching a topic across multiple sources
- Extracting content from one or more specific URLs
- Discovering the structure of a website (URLs, sections, pages)
- Crawling a site to gather content from many pages
- Reading documentation, blog posts, or articles hosted on the web
- Checking pricing, release notes, changelogs, or other time-sensitive data
- Investigating a company, product, library, or API from its public site

**Do NOT use Tavily for:**

- Questions about the user's own codebase (use CodeGraph or Kodit instead)
- Library/framework API references and code examples (use Context7 instead)
- General programming concepts with no external context
- Trivial knowledge you already have
- Sensitive or proprietary information — never include API keys, passwords, credentials, personal data, or proprietary code in queries
- Tasks that don't need the live web (offline reasoning, local file work)

## Tool Selection Guide

### 1. Quick web search — `tavily_search`

The default starting point. Returns ranked snippets with source URLs for a query.

**Use when:**

- You need a quick answer to a factual question
- You're looking for recent news, blog posts, or announcements
- You want to verify a claim against multiple sources
- You need a list of relevant URLs for a topic

**Key parameters:**

- `query` (required) — the search query; be specific
- `max_results` (optional, default 5) — cap the number of results
- `search_depth` (optional, default `basic`) — `basic` for fast results, `advanced` for thorough, `fast`/`ultra-fast` for low latency
- `topic` (optional, default `general`) — currently `general` is the only value
- `time_range` (optional) — `day` / `week` / `month` / `year` to filter by recency
- `start_date` / `end_date` (optional) — `YYYY-MM-DD` range filter
- `include_domains` / `exclude_domains` (optional) — restrict or block specific domains
- `country` (optional) — boost results from a specific country (full name, not ISO code)
- `include_raw_content` (optional) — include cleaned HTML of each result
- `include_images` / `include_image_descriptions` (optional) — include image results
- `exact_match` (optional) — only return results containing the exact quoted phrase

### 2. Extract content from known URLs — `tavily_extract`

Reads and parses the content of one or more specific URLs. Returns markdown or text.

**Use when:**

- You already have URLs and want their content
- You want to read a specific article, doc page, or blog post
- You need to compare content across a small set of known pages

**Key parameters:**

- `urls` (required) — list of URLs to extract (batch in one call when possible)
- `extract_depth` (optional, default `basic`) — `advanced` for LinkedIn, protected sites, tables, or embedded content
- `format` (optional, default `markdown`) — `markdown` or `text`
- `query` (optional) — rerank extracted chunks by relevance to this query
- `include_images` / `include_favicon` (optional)

### 3. Map a website's structure — `tavily_map`

Discovers URLs on a site without extracting their content. Returns a list of links.

**Use when:**

- You want to know what pages exist on a site
- You're planning a crawl and need a URL inventory first
- You want to find specific sections (e.g., `/docs/.*`, `/blog/.*`)

**Key parameters:**

- `url` (required) — root URL to start mapping from
- `max_depth` (optional, default 1) — how far from the base URL to explore
- `max_breadth` (optional, default 20) — max links to follow per level
- `limit` (optional, default 50) — total links to process before stopping
- `instructions` (optional) — natural-language guidance on which pages to return
- `select_paths` (optional) — regex patterns to restrict to specific URL paths
- `select_domains` (optional) — restrict to specific subdomains
- `allow_external` (optional, default true) — whether to include external links

### 4. Crawl a website with content — `tavily_crawl`

Explores a site and extracts content from each page it visits. Combines mapping + extraction.

**Use when:**

- You want both the URL inventory AND the content of those pages
- You're exploring a docs site, knowledge base, or blog
- You need to gather information from many pages on the same domain

**Key parameters:**

- `url` (required) — root URL to begin crawling
- `max_depth` (optional, default 1) — how far from the base URL to explore
- `max_breadth` (optional, default 20) — max links to follow per level
- `limit` (optional, default 50) — total links to process before stopping
- `instructions` (optional) — natural-language guidance on which pages to return
- `select_paths` (optional) — regex patterns to restrict to specific URL paths
- `select_domains` (optional) — restrict to specific subdomains
- `allow_external` (optional, default true) — whether to include external links
- `extract_depth` (optional, default `basic`) — `advanced` for tables/embedded content
- `format` (optional, default `markdown`) — `markdown` or `text`
- `include_favicon` (optional)

### 5. Deep multi-source research — `tavily_research`

LLM-powered research that synthesizes information from many sources into a detailed response.

**Use when:**

- You need a comprehensive answer that pulls from many sources
- The question is broad and spans multiple subtopics
- You want a synthesized overview, not just a list of links

**Key parameters:**

- `input` (required) — comprehensive description of the research task
- `model` (optional, default `auto`) — `mini` for narrow tasks with few subtopics, `pro` for broad tasks with many subtopics

**Rate limit:** 20 requests per minute. Use sparingly — this is the most expensive tool.

## Efficiency Rules

1. **Pick the cheapest tool that answers the question.** `search` is cheap, `research` is expensive. Don't reach for `research` when a `search` will do.
2. **Map before crawling.** If you don't know the site structure, run `tavily_map` first to discover URLs, then `tavily_extract` on the ones you actually need. Crawling blindly wastes calls.
3. **Extract before crawling when you have URLs.** If you already know the URLs, `tavily_extract` is faster and cheaper than `tavily_crawl`.
4. **One well-formed query beats five vague ones.** Each MCP call has overhead. Make the query specific enough to return useful results on the first try.
5. **Use `search_depth: "advanced"` when quality matters.** Default `basic` is fast but shallow. Use `advanced` for thorough research; use `fast`/`ultra-fast` when latency matters more than depth.
6. **Filter with `time_range` or `start_date`/`end_date`** when you need recent information. Don't search the whole web when you only care about the last week.
7. **Restrict with `include_domains` / `exclude_domains`** when you know the source. This dramatically improves precision.
8. **Batch URLs in a single `tavily_extract` call** when you have multiple pages to read — don't make one call per URL.
9. **Set `max_results`, `limit`, `max_depth`, and `max_breadth` explicitly** when you know the scope. Defaults can return too much or too little.
10. **Don't re-search what you already have.** If `tavily_search` returned the URLs you need, go straight to `tavily_extract` — don't search again.
11. **Batch independent calls in parallel** when there are no dependencies between them (e.g., extracting multiple URLs at once).
12. **Respect the `research` rate limit.** 20 requests per minute — don't spam it.

## Common Workflows

### "What's the current state of X?"

1. `tavily_search` with a specific query
2. If you need the full content of a result, `tavily_extract` on the URL
3. If results are off-target, refine the query or add `time_range` / `include_domains`

### "Read this specific article / page"

1. `tavily_extract` with the URL
2. If the page is protected or has tables, retry with `extract_depth: "advanced"`
3. If you need to find related pages, `tavily_map` on the same domain

### "What pages exist on this site?"

1. `tavily_map` with the root URL
2. Use `select_paths` to narrow to a section (e.g., `/docs/.*`)
3. Use `instructions` to guide which pages to return

### "Explore a docs site / blog"

1. `tavily_map` first to discover the URL inventory
2. `tavily_extract` on the specific pages you need (faster than crawling everything)
3. Only use `tavily_crawl` when you need both URLs AND content from many pages

### "Research a broad topic"

1. `tavily_search` with a specific query to get an overview
2. `tavily_extract` on the most relevant results
3. If the topic spans many subtopics, `tavily_research` for a synthesized answer

### "Find recent news about X"

1. `tavily_search` with `time_range: "week"` or `start_date` set
2. If you need the full article, `tavily_extract` on the URLs
3. Use `include_domains` to restrict to trusted news sources

### "Verify a claim against multiple sources"

1. `tavily_search` with the claim as the query
2. Review the snippets and source URLs
3. `tavily_extract` on the most authoritative sources for full context

## Anti-Patterns

- ❌ Using `tavily_research` for a simple factual question (use `tavily_search`)
- ❌ Using `tavily_crawl` when you already have the URLs (use `tavily_extract`)
- ❌ Crawling blindly without `tavily_map` first to understand the site structure
- ❌ Making one `tavily_extract` call per URL instead of batching
- ❌ Using vague queries like `"AI"` or `"news"` — be specific about what you need
- ❌ Searching without `time_range` when you only care about recent results
- ❌ Searching without `include_domains` when you know the source
- ❌ Using Tavily for the user's own codebase (use CodeGraph or Kodit)
- ❌ Using Tavily for library API references (use Context7)
- ❌ Including sensitive data in queries (API keys, passwords, credentials, proprietary code)
- ❌ Re-searching when you already have the URLs — go straight to `tavily_extract`
- ❌ Spamming `tavily_research` past the 20 req/min rate limit

## Quick Reference

```plaintext
tavily_search     → quick web search, ranked snippets with URLs
tavily_extract    → read content from known URLs (batch in one call)
tavily_map        → discover URLs on a site (no content extraction)
tavily_crawl      → explore a site with content (map + extract combined)
tavily_research   → deep multi-source research (LLM-synthesized, rate-limited)
```

**Decision flow:**

1. Need current info on a topic? → `tavily_search`
2. Have specific URLs to read? → `tavily_extract`
3. Need to discover URLs on a site? → `tavily_map`
4. Need to explore a site with content? → `tavily_crawl`
5. Need comprehensive multi-source research? → `tavily_research`

**Rate limit:** `tavily_research` is capped at 20 requests per minute.
**Batch URLs:** pass a list to `tavily_extract` in one call, not one call per URL.
**Filter:** use `time_range`, `include_domains`, `select_paths` to narrow results.
