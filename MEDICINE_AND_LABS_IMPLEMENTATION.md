# Medicine × AI and Frontier Labs Implementation Summary

## Implementation Complete

This document summarizes the structural changes made to treat Medicine × AI as a first-class vertical and Frontier Labs as primary sources.

---

## PART 1: MEDICINE × AI AS FIRST-CLASS VERTICAL

### 1. Medicine-Related Feeds Now Included

**RSS Feeds Added** (`worker/config/rss_feeds.json`):
- Nature Medicine News
- NEJM AI Perspectives
- STAT News - AI in Healthcare
- Healthcare IT News - AI
- FDA News - Digital Health (regulatory source)
- NIH News - AI/ML (regulatory source)

All medicine-focused feeds are marked with `"medicine_focused": true` for easy identification.

### 2. How Medicine Scoring Differs from General AI

**Editor Agent Scoring Changes** (`worker/agents/editor.py`):

**For Medicine-Tagged Clusters:**
- **Credibility Weight**: Increased from 20% to **30%** (evidence quality prioritized)
- **Novelty Weight**: Decreased from 15% to **10%** (regulatory relevance can outweigh recency)
- **Corroboration Weight**: Decreased from 10% to **5%** (regulatory sources don't need multiple confirmations)

**Credibility Scoring:**
- FDA/NIH regulatory sources: **0.95** (maximum credibility even with single source)
- Clinically validated: **0.90**
- Regulatory relevant: **0.92**
- General medicine sources: **0.85**

**Novelty Scoring:**
- Regulatory updates maintain high novelty (0.9) even for items up to 7 days old
- Regulatory relevance stays relevant longer (0.75) for items up to 30 days old

**Impact Scoring:**
- Regulatory relevant medicine items: **0.95** impact score

**Result**: FDA/NIH regulatory updates can rank above general AI model releases because:
1. Higher credibility weight (30% vs 20%)
2. Maximum credibility scores for regulatory sources
3. Regulatory relevance maintained over longer timeframes
4. Reduced novelty requirement

### 3. Data Model: Clinical Maturity Level

**New Field**: `clusters.clinical_maturity_level` (enum)

**Values**:
- `exploratory`: Initial research phase
- `clinically_validated`: Peer-reviewed, validated evidence
- `regulatory_relevant`: FDA/NIH involvement or guidance
- `approved_deployed`: Regulatory approval granted, in deployment

**Detection** (`worker/agents/tagger.py`):
- Automatic detection based on keywords (FDA, NIH, approval, clinical trial, etc.)
- Set during tagging phase for medicine-tagged clusters

**Usage**:
- Influences credibility and novelty scoring
- Used in rationale generation
- Displayed in API responses

### 4. Medicine Tagging Priority

**Tagger Agent** (`worker/agents/tagger.py`):
- Medicine keywords expanded to 20+ terms including regulatory and clinical terms
- **Lower threshold**: Medicine topics require only **1 keyword match** (vs 2 for other topics)
- Ensures comprehensive medicine coverage

---

## PART 2: FRONTIER LABS AS PRIMARY SOURCES

### 1. Frontier Lab Sources

**RSS Feeds Added** (`worker/config/rss_feeds.json`):
- Anthropic Blog (Tier 1)
- OpenAI Blog (Tier 1)
- DeepMind Blog (Tier 1)
- Google AI Blog (Tier 1)
- Meta AI Research (Tier 1)
- Microsoft Research AI (Tier 1)

All marked with `"frontier_lab"` and `"tier": 1`.

### 2. How Anthropic Content Flows Through Pipeline

**Scout Agent** (`worker/agents/scout.py`):
1. **Detection**: 
   - RSS feed URLs matched against frontier lab domains
   - arXiv author affiliations matched against lab patterns
   - Items marked with `frontier_lab = "Anthropic"` field
   - Source type set to `PRIMARY_LAB`

2. **Storage**: Raw items stored with `frontier_lab` field populated

**Tagger Agent** (`worker/agents/tagger.py`):
1. **Auto-tagging**: 
   - Anthropic items auto-tagged with: `general-ai`, `ai-policy-governance`, `human-centered-ai`
   - Policy/safety content gets both `ai-policy-governance` AND `human-centered-ai`
   - Domain-specific tags (e.g., medicine) preserved if applicable

2. **No topic drop**: Medicine or other domain tags retained if content matches

**Editor Agent** (`worker/agents/editor.py`):
1. **Credibility Boost**: Maximum credibility (0.95) for frontier lab sources
2. **Impact Boost**: High impact (0.95) even for single-item clusters
3. **Reduced Corroboration**: 0.9 score even with single source (no external confirmation needed)
4. **Rationale**: Includes "primary announcement from Anthropic" in ranking rationale

**Writer Agent** (`worker/agents/writer.py`):
1. **First Sentence**: Explicitly names lab - "Anthropic announced..." or "Anthropic released..."
2. **Primary Framing**: Presented as primary announcement, not secondary reporting
3. **Implications**: Includes downstream research, deployment, and policy implications

### 3. Why Frontier Lab Announcements Can Rank #1 Without External Confirmation

**Scoring Logic**:
- **Credibility**: 0.95 (maximum) - Frontier labs are authoritative sources
- **Impact**: 0.95 (high) - Lab announcements shape the field
- **Corroboration**: 0.9 (high) - Single source is sufficient (no external validation needed)

**Overall Score Calculation**:
```
Standard weights: 0.30 relevance + 0.25 impact + 0.20 credibility + 0.15 novelty + 0.10 corroboration
```

Even with conservative novelty (0.7) and relevance (0.8), a frontier lab announcement scores:
```
0.30 * 0.8 + 0.25 * 0.95 + 0.20 * 0.95 + 0.15 * 0.7 + 0.10 * 0.9 = 0.855
```

This is sufficient to rank above most general AI news that requires multiple sources for corroboration.

**Rationale**: Frontier labs drive AI research direction. Their primary announcements don't need media echo chamber validation to be authoritative.

---

## Why Neither FDA Updates Nor Anthropic Announcements Can Be Buried

### FDA/NIH Regulatory Updates

**Protection Mechanisms**:
1. **Higher Credibility Weight** (30% vs 20%) - Evidence quality prioritized
2. **Maximum Credibility** (0.95) - Regulatory sources are authoritative
3. **Extended Novelty** - Stay relevant up to 30 days (vs 7 days for general content)
4. **High Impact** (0.95) - Regulatory decisions affect entire ecosystem
5. **Reduced Corroboration Need** - Single FDA/NIH source is sufficient

**Example Score** (FDA approval announcement):
- Relevance: 0.85 (medicine priority)
- Impact: 0.95 (regulatory significance)
- Credibility: 0.95 (FDA source)
- Novelty: 0.75 (even if 2 weeks old)
- Corroboration: 0.9 (single source sufficient)

**Medicine-weighted score**:
```
0.30 * 0.85 + 0.25 * 0.95 + 0.30 * 0.95 + 0.10 * 0.75 + 0.05 * 0.9 = 0.8975
```

This ranks above general AI model releases (typically 0.75-0.85).

### Anthropic Announcements

**Protection Mechanisms**:
1. **Maximum Credibility** (0.95) - Primary lab source
2. **High Impact** (0.95) - Shapes field direction
3. **Reduced Corroboration** (0.9) - Single source sufficient
4. **Explicit Lab Naming** - Framed as primary announcement

**Example Score** (Anthropic model release):
- Relevance: 0.8
- Impact: 0.95 (lab announcement)
- Credibility: 0.95 (primary source)
- Novelty: 0.9 (recent)
- Corroboration: 0.9 (single source sufficient)

**Standard-weighted score**:
```
0.30 * 0.8 + 0.25 * 0.95 + 0.20 * 0.95 + 0.15 * 0.9 + 0.10 * 0.9 = 0.89
```

This ranks #1 even without media echo chamber coverage.

---

## Files Modified

### Data Model
- `api/models.py`: Added `ClinicalMaturityLevel` enum, `frontier_lab` field to RawItem, `clinical_maturity_level` field to Cluster, `PRIMARY_LAB` to SourceType

### Migrations
- `api/alembic/versions/20241224_add_medicine_lab_fields.py`: Migration for new fields

### Configuration
- `worker/config/rss_feeds.json`: Added medicine feeds and frontier lab blogs

### Agents
- `worker/agents/scout.py`: Frontier lab detection from URLs and arXiv affiliations
- `worker/agents/tagger.py`: Medicine priority tagging, clinical maturity detection, frontier lab auto-tagging
- `worker/agents/editor.py`: Medicine-specific scoring weights, frontier lab boosts
- `worker/agents/writer.py`: Explicit lab naming, primary announcement framing, medicine-specific content

### API
- `api/schemas.py`: Added `clinical_maturity_level` to StoryItemResponse
- `api/routers/briefing.py`: Include clinical_maturity_level in responses

### Documentation
- `ARCHITECTURE.md`: Added special handling section
- `MEDICINE_AND_LABS_IMPLEMENTATION.md`: This summary document

---

## Testing Recommendations

1. **Test Medicine Tagging**: Verify FDA/NIH items get medicine tag with regulatory_relevant maturity level
2. **Test Frontier Lab Detection**: Verify Anthropic blog posts are marked with frontier_lab field
3. **Test Scoring**: Verify FDA updates and Anthropic announcements rank above general AI news
4. **Test Writer**: Verify lab announcements start with "Anthropic announced..." format

---

## Summary

✅ Medicine × AI is now a first-class vertical with:
- Expanded feed coverage (6 medicine-focused sources)
- Specialized scoring (30% credibility weight, extended novelty for regulatory)
- Clinical maturity tracking
- Priority tagging (lower threshold)

✅ Frontier Labs are now primary sources with:
- Tier 1 RSS feed coverage (6 major labs)
- Automatic detection and marking
- Maximum credibility and impact scores
- Single-source ranking capability
- Explicit lab naming in summaries

Neither FDA/NIH regulatory updates nor Anthropic announcements can be buried by secondary news due to their specialized scoring and reduced corroboration requirements.

