# Test run: FinIntelligence AI (finintelligenceai.com)

_Manual run of Pipewright's steps, September 2026. The site itself was unreachable from the build environment, so the ICP is based on the founder's one-line description:_
> "Financial intelligence for companies building the future of finance. We turn thousands of signals across regulation, competitors, products, technology and markets into concise, decision-ready insight."

## 1. ICP (paste into "Edit as JSON")

```json
{
  "product_summary": "AI financial-intelligence service that turns regulation, competitor, product, technology and market signals into concise, decision-ready briefs for fintechs and financial institutions.",
  "value_props": [
    "Know about competitor launches and regulatory changes (RBI, SEBI, IRDAI, NPCI) the week they happen, not the quarter after",
    "Replaces hours of analyst reading with a short brief tied to your roadmap",
    "Board- and investor-ready market context without hiring a strategy team"
  ],
  "target_industries": ["Fintech (lending, payments, wealth, insurtech)", "Digital banks and NBFCs", "Banking-as-a-service / fintech infrastructure", "Fintech-focused VCs"],
  "company_size": "20-2,000 employees",
  "geographies": ["India", "Singapore", "UAE", "United Kingdom"],
  "buyer_titles": ["Founder / CEO", "Chief Strategy Officer", "Head of Strategy", "Head of Product", "Chief Compliance Officer", "Head of Corporate Development", "VC Partner / Principal (fintech)"],
  "pain_points": [
    "Regulatory changes land faster than a small team can read and interpret them",
    "Competitor launches are discovered late, from customers or the press",
    "Strategy and board decks take days of manual research"
  ],
  "buying_signals": [
    "Just raised a round (new board, new plan to justify)",
    "Entering a new market or country",
    "Launching a new product line or getting a new licence",
    "Hiring strategy, market-intelligence or regulatory-affairs roles",
    "Directly affected by a recent regulator circular"
  ],
  "disqualifiers": ["Pre-product startups with no funding", "Non-financial companies", "Large banks with in-house research departments (long sales cycle, not a first target)"],
  "search_queries": ["India fintech raises funding 2026", "fintech expands to Singapore UAE 2026", "NBFC acquires housing finance company 2026", "fintech hiring head of strategy India"]
}
```

## 2. Prospects found (real, with dated signals)

| # | Company | Why it fits | Signal (source) | Fit |
|---|---|---|---|---|
| 1 | **Spense** | Builds secured-credit infrastructure for banks, so it has to track RBI credit-card and lending rules closely | $2.8M seed led by Arkam Ventures, with Razorpay Ventures participating, July 2026; says it works with 7 banks ([Inc42](https://inc42.com/buzz/spense-raises-2-8-mn-from-arkam-ventures-to-build-secured-lending-infra/), [FinSMEs](https://www.finsmes.com/2026/07/spense-raises-2-8m-in-seed-funding.html)) | 90 |
| 2 | **Weaver Services** | Housing-finance fintech in the middle of acquiring a regulated housing-finance company, with a heavy compliance and market-mapping load | ₹1,450 cr ($156M) raised, co-led by Premji Invest and Lightspeed; acquiring Centrum Housing Finance, March 2026 ([YourStory](https://yourstory.com/2026/03/housing-finance-platform-weaver-services-raises-rs-1450-cr), [Entrackr](https://entrackr.com/news/weaver-services-raises-rs-1450-cr-led-by-premji-invest-and-lightspeed-11224855)) | 88 |
| 3 | **KreditBee** | Digital lender that has just become a unicorn; faces constant RBI digital-lending rule changes and competitive pressure | $220M Series E in H1 2026 ([Business Standard](https://www.business-standard.com/finance/news/india-s-fintech-sector-raises-2-bn-in-h1-2026-led-by-late-stage-funding-126071601258_1.html)) | 80 |
| 4 | **Razorpay** | Expanding into Malaysia and Singapore, so it needs to understand new regulators and competitors | 2026 focus on international expansion and embedded finance ([UpForge](https://www.upforge.org/blog/fintech-startups-india-2026)) | 75 |
| 5 | **Arkam Ventures** (VC) | Fintech-heavy VC; pre-investment market scans are the use case | Led Spense's seed round, July 2026 | 70 |
| 6 | **CRED** | Very large round means new product bets, and its strategy team would use competitor and regulation tracking | $900M Series H, H1 2026 ([Business Standard](https://www.business-standard.com/finance/news/india-s-fintech-sector-raises-2-bn-in-h1-2026-led-by-late-stage-funding-126071601258_1.html)) | 60, since it may already have in-house research |

**Named decision makers found in coverage:** Spense co-founders Pawan Kumar and Srinivas Krishnamurthy. Weaver co-founders Satrajit Siva Bhattacharya and Anil Kothuri.
Emails are **not** included. Verify them with Pipewright's lookup and MX check, or with a data provider, before sending.

## 3. Draft emails for review

**To Pawan Kumar, Spense.** Subject: *spense + rbi changes*
> Hi Pawan,
>
> Congratulations on the seed round with Arkam. Building secured credit for 7 banks means every RBI circular on cards and secured lending lands on your desk too.
>
> FinIntelligence AI reads regulator, competitor and market updates for fintechs and sends a short brief on what changed and what it means for your roadmap. It replaces hours of reading each week.
>
> Would a sample brief on secured-credit and co-branded-card changes from the last 90 days be useful?

**To Satrajit Siva Bhattacharya, Weaver.** Subject: *centrum integration intel*
> Hi Satrajit,
>
> Congratulations on the Premji and Lightspeed round and the Centrum Housing Finance acquisition. Taking on a regulated HFC usually brings a wave of NHB and RBI compliance changes, plus a new set of competitors to watch in tier II and III markets.
>
> FinIntelligence AI turns those signals into a short weekly brief, so the team isn't stitching it together by hand.
>
> Open to a sample brief on affordable-housing-finance competitors and recent regulation?

Follow-ups (+3 and +7 days): offer the free sample brief. Then close the loop by asking if someone in strategy or compliance is the better contact.

## 4. CSV to import into Pipewright (add verified emails first)

```csv
company,website,contact_name,contact_title,email
Spense,,Pawan Kumar,Co-founder,
Weaver Services,,Satrajit Siva Bhattacharya,Co-founder,
KreditBee,https://www.kreditbee.in,,,
Razorpay,https://razorpay.com,,,
```
Spense and Weaver websites were not verified here, so fill them in before importing. Pipewright skips rows without a website or an email.
