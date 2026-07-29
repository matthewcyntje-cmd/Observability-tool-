# GEO Observability Demo, Master Doc

## Purpose

This is the engineering demo, not the product demo. Per Philip's own framing: product demo leads with customer, problem, alternatives. Engineering demo leads with tools, platforms, scripts, and an interface that shows how it actually works. This doc exists to lock the screens, content, and fake vs real mechanics before build, so Claude Code has a full spec instead of improvised layout decisions mid session.

## Demo Philosophy

Hybrid, not fully live. Three tiers:

1. **Real:** the analysis dashboards. Pull from Button's actual output data. This is the part that has to feel true, since it's the whole point of the demo.
2. **Staged as live, actually canned:** query generation. You already have the question sets prepared. The screen should look like it's generating them, but it's really just revealing a pre-built list at a natural pace.
3. **Real but lightweight:** brand description input and edit. Cheap to make actually live, low risk, and it's the one moment where "does the LLM already know us correctly" lands well in the room.

Nobody in the room can tell staged from live if the transition feels natural and the underlying data is real.

## User Flow

1. Brand Input
2. Query Set Reveal (brand focus and market focus)
3. Run Scan (staged progress)
4. Brand Focus Dashboard
5. Market Focus Dashboard

## Screen 1: Brand Input

**Purpose:** establish the brand being analyzed, and let the presenter show the "does the LLM know us" moment.

**Contents:**
- Text field prefilled with Button's actual self description
- Editable, so presenter can tweak wording live
- Small affordance: "agree with this description" or "edit it" (this is the moment worth lingering on live, since it doubles as a gut check on brand narrative accuracy)
- Continue button

**Fake vs real:** fully static, no API call needed. It's just a form.

## Screen 2: Query Set Reveal

**Purpose:** show the brand focus and market focus question sets being built, without an actual generation call.

**Mechanics:**
- Two tabs or two stacked sections: Brand Focus Questions, Market Focus Questions
- Questions populate from your pre built lists, one at a time or in small batches, at a pace that reads as generation (roughly 150 to 300ms per row, not instant)
- Each row editable and deletable after it lands, so presenter can show "user can edit the question set" without needing true generation underneath
- Small label under each set: "30 questions, run 4x per model" so the volume is visible without narrating it

**Fake vs real:** fully canned. No API call. This is the one place where faking it outright is the right call, since it removes all live demo risk with zero loss of impressiveness.

## Screen 3: Run Scan

**Purpose:** sell the pipeline without needing the pipeline to run in real time.

**Mechanics:**
- Trigger button: "Run Scan"
- Staged status lines ticking through, each visible for 1 to 2 seconds:
  - Querying ChatGPT...
  - Querying Gemini...
  - Querying Perplexity...
  - Extracting descriptors...
  - Normalizing paraphrased phrasing...
  - Scoring narrative alignment...
- Ends by transitioning into the dashboard

**Fake vs real:** fully staged. This is theater, and it's fine for it to be theater, since the real work already happened once to produce the data you're about to show.

## Screen 4: Brand Focus Dashboard

**Purpose:** show what LLMs say when asked directly about the brand.

**Sections, pulled from real Button output:**
- Top 15 descriptor phrases: canonical phrase, total frequency, % of total occurrences, % of responses containing it
- Top 10 figures: value, what it refers to, frequency, % of responses
- Source domains: domain, frequency, % of responses
- Top 10 specific URLs: normalized URL, frequency, % of responses

**Fake vs real:** fully real data. This is the payload of the demo.

**Optional stretch:** a toggle that reveals the extraction instruction used for that section (e.g. the Facts and Figures normalization rule). Nice engineering flavor, low build cost, skip if time is tight.

## Screen 5: Market Focus Dashboard

**Purpose:** show how the brand appears in comparative, landscape level queries.

**Sections, pulled from real Button output:**
- Competitor mentions: entity, count of responses mentioning it, % of total market queries
- Visibility/presence rate: single percentage, denominator stated
- Average ranking/position: single average, denominator stated separately from visibility denominator
- Top 15 descriptor phrases (brand specific, market context): canonical phrase, frequency, % of responses where brand appeared
- Source domains: domain, frequency, % of responses

**Fake vs real:** fully real data.

## Data Handling

- `button.json`: full real analysis output, used whenever the brand input is left as Button or close to it. This is your one fully fleshed out path.
- Fallback state: if someone types a brand you don't have real data for, show a graceful "insufficient query volume, showing sample structure" state rather than breaking or faking numbers for an unknown brand. This is the one thing that would actually embarrass the demo if skipped.

### Confirmed dashboard schema, based on real Button output

**Brand Focus Dashboard**
- Descriptor phrases: rank, canonical phrase, total frequency, % of total occurrences (top 15), % of responses containing
- Figures: rank, value, what it refers to, frequency, % of responses (note ties share a rank number, note any figures excluded for appearing only in a URL slug rather than response body)
- Source domains: domain (subdomains rolled up), frequency, % of responses
- Top URLs: rank, normalized URL, frequency, % of responses

**Market Focus Dashboard**
- Competitor mentions: entity, responses mentioning it, % of total market queries
- Visibility/presence rate: single %, denominator stated (e.g. "57 of 120")
- Average ranking/position: mean and median, denominator stated separately from visibility denominator (note the median is usually the more representative number when a few long tables skew the mean)
- Descriptor phrases: rank, descriptor, count, % of responses where brand appeared (not total responses)
- Source domains: domain, frequency, % of total responses

### Query set input, finalized

`query_sets.json` holds the deduped 30 brand-focused and 30 market-focused questions, text only, no responses attached. This feeds Screen 2's staged reveal.

`button_analysis.json` holds the full real aggregated output for both dashboards, structured to match the confirmed schema above: descriptor phrases, figures with excluded-figure notes, source domains, top URLs for Brand Focus, and competitor mentions, visibility rate, average ranking, descriptor phrases, source domains for Market Focus. This is the file Claude Code should read directly for Screens 4 and 5 rather than having any of it re-typed into a prompt.

`theme.json` holds Button's real brand tokens pulled from the Button Design System brand page: brand blue `#0077FF`, white, canvas `#FAFAFA`, dark `#181818`, and the Inter Black wordmark spec. Chart series colors and muted/border tones are derived, not official, since the source page only defines the four approved surfaces. Claude Code should style every screen off this file rather than inventing a palette. If a fuller Button palette shows up later, swap the `derivedForUi` block only, the `core` and `approvedSurfaces` blocks are the real brand data and shouldn't change.

Not needed for v1: the full 240 raw query/response pairs. The aggregated output above is the real payload; individual pairs are intermediate data that already did their job producing it.

**Stretch, not v1:** a drill down affordance where clicking a descriptor or figure surfaces the specific responses behind it. Genuinely nice for proving the data is real, but requires tagging every response against canonical phrases, which is judgment work, not a lookup. Worth scoping only if time allows after the core five screens work.

## What Still Needs Deciding

- Does the brand input field's edit actually call the API live to check agreement with the description, or is that also staged
- Whether to include the extraction instruction toggle on the dashboards
- Single page app vs multi step flow with URL routing between screens
