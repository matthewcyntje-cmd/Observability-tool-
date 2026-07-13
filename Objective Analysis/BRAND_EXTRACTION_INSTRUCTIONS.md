# Brand Extraction Instructions (paste this to Claude when you have new data)

You are working in the Objective Analysis project. There is a CSV of Query,Response
pairs that needs to be turned into an extraction cache for the Brand analysis pipeline.
Do NOT call any external API for this — read the CSV directly and do the extraction yourself.

Step 1 — Read the input


Find the single CSV in Brand/Input/. There must be exactly one file there.
Read the brand name from the last non-empty line of Config.txt.
Use the Read tool to read the CSV in full so you see every response verbatim — do not
summarize or sample it.


Step 2 — For every row, extract three things

Go row by row. Every row is independent — never merge, pool, or average across rows.

Descriptors — every 1 to 4 word phrase that explicitly describes the brand itself
(the brand must be the explicit subject, not a feature described in isolation and not a
competitor). Copy each phrase exactly as written, no rewording or paraphrasing. Exclude
negations ("not a storefront platform") and standalone product/feature names.

Do a full line-by-line sweep of the ENTIRE response before moving to the next row — do
not stop after finding the first one or two strong matches. Brand-descriptive phrases
commonly appear more than once per response (an opening definition, a third-party quote
later in the body, a "bottom line" restatement at the end) — each occurrence is a
separate extraction, even if it repeats a phrase already captured elsewhere in this row
or in a different row. Pay specific attention to:


adjectives characterizing the brand ("legitimate", "trustworthy", "credible"), not
just category/noun-phrase descriptors — these are frequently missed
descriptions attributed to a third party or quoted source (e.g. "X described it as a
mobile experience platform") — these still count, the brand is still the subject
restatement/"bottom line" sentences near the end of a response, which often repeat or
rephrase an earlier descriptor and get skipped because they look redundant — they are
not redundant for extraction purposes, capture them too


IMPORTANT — do not limit extraction to a fixed set of trigger phrases like
"is a," "is used as," or "described as." Those are examples, not the full
list. Any sentence where the brand is the explicit subject and the sentence
characterizes what it is, does, is used for, or is compared to counts,
regardless of the exact verb or sentence structure. This includes:


action/role descriptions not phrased with "is a" (e.g. "Button routes
shoppers to..." → "routes shoppers to")
comparative framing (e.g. "less like a traditional affiliate network" →
"less like a traditional affiliate network")
attributed descriptions where the descriptive phrase comes several words
after the brand name or a pronoun referring to it, not just immediately
after it


If you find yourself skipping a sentence because it doesn't match one of the
example phrasings above, that is the signal to include it anyway, not to move
on. Every response with 3+ brand-characterizing sentences should produce 3+
descriptors, not 1, per the Step 4 check below.

Before writing this row's descriptors to the cache, do a second pass over the response
asking "did I capture every sentence where the brand is described as, functions as, is
called, or is characterized as something" — if a qualifying sentence exists that isn't
reflected in the list, add it.

Figures — every qualifying number: dollar amounts, percentages, counts (countries,
retailers, partners, etc.), or years. Exclude vague quantifiers ("many retailers", "a
large number"). For each figure, capture the value exactly as written plus a short
referent phrase describing specifically what THAT number measures — not the sentence
it came from. When a sentence contains multiple figures (e.g. "$100B+ in total commerce
driven, 14.4B shopping journeys, 22M app installs"), split it so each number is paired
only with the few words describing it directly ("total commerce driven", "shopping
journeys", "app installs"), never a shared block of context covering several numbers at
once. If two figures differ only in phrasing or rounding (e.g. "$1 billion" vs "$1B")
and refer to the same referent, collapse them into one entry; figures with different
referents always stay distinct even if the numeric value happens to match.

Sources — only the URLs/citations in the end-of-response source list (usually under
a heading like "Sources used:"). Ignore inline citation mentions in the body text
(bare words like "Button" or "PR Newswire" floating mid-paragraph are UI citation
artifacts, not real sources — skip them).

Step 3 — Write the extraction cache

Write one Python dict per row (in the same order as the CSV) into a script like
build_cache.py, shaped like:

python{
    "descriptors": ["phrase one", "phrase two"],
    "figures": [{"value": "$1 billion", "referent": "monthly commerce driven"}],
    "sources": ["https://example.com/post-1", "https://example.com/post-2"],
}

Pair each dict with its row via load_rows() from brand_pipeline/csv_utils.py, then
write one JSON line per row to Brand/Output/extractions_cache.jsonl with fields
row_index, query, response, descriptors, figures, sources. This must match
the row count of the input CSV exactly — assert on it before writing.

Step 4 — Verify your own extraction before trusting it


Descriptors: for every row, re-read the response one more time independently of
your extraction pass and count how many brand-as-subject descriptive sentences you can
find (definition sentences, "described as" attributions, adjective characterizations,
action/role descriptions, comparative framing, bottom-line restatements). If that
count is higher than the number of descriptors currently captured for that row, go
back and add the missing ones before moving on. A response with 3+ sentences that
describe/define/characterize the brand should essentially never end up with only 1
descriptor captured — treat that outcome as a signal you under-extracted, not as a
valid result.
Figures: regex-sweep every response for numeric patterns ($, %, counts, years,
"Nx") and confirm every match is either captured as a figure (with its own specific
referent, not a shared sentence-level context) or correctly excluded as vague.
Sources: diff your captured sources arrays against a regex extraction of
everything after the literal "Sources used:" text in each response. They must match
exactly.
Report any mismatches before moving on — do not silently proceed if something's off.


Step 5 — Run the aggregation

python3 -m brand_pipeline.run

This reads extractions_cache.jsonl and writes Brand/Output/brand_analysis.csv —
one file with DESCRIPTORS, FIGURES, FIGURES SUMMARY, SOURCES, and
SOURCES SUMMARY sections, each separated by a blank line.

Where the user puts files


Input CSV (raw Query/Response export from the query-capture tool): drop it into
Objective Analysis/Brand/Input/. Remove any other CSVs from that folder first — the
pipeline expects exactly one.
Brand name: Objective Analysis/Config.txt, brand name on the last non-empty line.
Output: after running the aggregation, results land at
Objective Analysis/Brand/Output/brand_analysis.csv — nothing else to move.