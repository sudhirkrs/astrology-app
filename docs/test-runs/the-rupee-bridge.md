# Test run: The Rupee Bridge (therupeebridge.beehiiv.com)

_Manual run of Pipewright's steps, September 2026. The newsletter's own description:_
> "A free 5-minute read for NRIs managing money across two countries: accounts, taxes, property, retirement, and the move…" (by Finostock)

**Goal: find sponsors and partners, not subscribers.** Cold-emailing individual NRIs to subscribe would be spam and would break DPDP, GDPR and CAN-SPAM rules. The companies that want to reach NRIs are the right people to email.

## 1. ICP (paste into "Edit as JSON")

```json
{
  "product_summary": "The Rupee Bridge (by Finostock) is a free 5-minute newsletter for NRIs managing money across two countries: accounts, taxes, property, retirement and moving back. It sells sponsorships and partnerships to brands that serve NRIs.",
  "value_props": [
    "Reach NRIs at the moment they're making cross-border money decisions",
    "Contextual placement next to practical content on accounts, taxes and property, not a banner ad",
    "Cheaper and more trusted than paid social for NRI acquisition"
  ],
  "target_industries": ["NRI remittance and banking fintechs", "NRI investment platforms", "NRI tax filing / CA firms", "NRI property management and real estate", "Cross-border insurance and retirement products"],
  "company_size": "10-5,000 employees",
  "geographies": ["India", "United States", "United Kingdom", "UAE", "Singapore", "Canada"],
  "buyer_titles": ["Head of Growth", "Marketing Manager", "Partnerships Lead", "Head of Brand", "Founder (early-stage)"],
  "pain_points": [
    "NRI audiences are expensive and hard to target on paid social",
    "Trust is the main barrier for money products aimed at NRIs",
    "Content marketing takes time to rank"
  ],
  "buying_signals": [
    "Recently raised funding or expanding to new NRI corridors",
    "Publishing NRI-focused blog content (they already pay to reach this audience)",
    "Launching a new NRI product (accounts, FDs, tax filing)",
    "Hiring growth or partnerships roles"
  ],
  "disqualifiers": ["Products not available to NRIs", "Unregulated investment schemes or high-risk products you wouldn't want to endorse"],
  "search_queries": ["NRI fintech raises funding", "NRI investment app launch", "NRI tax filing platform", "NRI remittance app expands US UK"]
}
```

## 2. Sponsor prospects found

| # | Company | Why it fits | Signal (source) | Fit |
|---|---|---|---|---|
| 1 | **Aspora** (formerly Vance) | Remittance and banking built only for NRIs, and their product lines up with your "accounts" coverage | $53M Series B co-led by Sequoia and Greylock ($93M total); expanding to the US, Canada, Australia and Singapore; 250k+ NRI users ([FinTech Futures](https://www.fintechfutures.com/venture-capital-funding/remittance-platform-aspora-raises-53m-series-b), [YourStory](https://yourstory.com/2025/06/nri-diaspora-fintech-aspora-banking-services-series-b-funding-round)) | 95 |
| 2 | **Belong** | Investment platform for NRIs (USD fixed deposits, mutual funds), a match for your retirement and investing content | $5M round led by Elevation Capital ([getbelong.com](https://getbelong.com/)) | 92 |
| 3 | **iNRI** | NRI super-app for investing, tax filing and money management; early stage, so a newsletter sponsorship fits its budget | Y Combinator-backed, $500K pre-seed ([goinri.com](https://www.goinri.com/about-us)) | 90 |
| 4 | **SBNRI** | NRI app for banking, investments and tax, with an existing partner program | Public "partner with us" page and a past content partnership with Mint ([SBNRI partners](https://sbnri.com/partner-with-us), [Mint partnership](https://sbnri.com/blog/education/mint-sbnri-join-forces-to-simplify-financial-planning-for-nris)) | 90 |
| 5 | **Instarem** | Cross-border transfers; already writes NRI remittance content | NRI remittance blog ([Instarem](https://www.instarem.com/blog/the-smart-ways-in-which-fintech-startups-are-lowering-cost-of-remittance-for-nris/)) | 80 |
| 6 | **IDFC FIRST Bank (NRI)** | Bank actively producing NRI remittance content | NRI blog series ([IDFC FIRST](https://www.idfcfirst.bank.in/finfirst-blogs/nri/nri-remittance-trends-future-india)) | 70, since banks have slower sponsorship processes |
| 7 | **India For NRI** / NRI tax CA firms | Legal, tax and property services for NRIs, a match for your taxes and property coverage | Actively marketing NRI services ([indiafornri.com](https://indiafornri.com/)) | 70 |

**Named people from coverage:** Aspora founder Parth Garg. For the others, look for Growth, Marketing or Partnerships leads rather than founders. At Aspora's size, a growth lead is a better first contact than the CEO.

## 3. Draft emails for review

Fill in the `[ ]` numbers. Sponsors always ask for subscriber count, open rate and reader countries.

**To the growth or partnerships lead at Aspora.** Subject: *nri readers for aspora*
> Hi [Name],
>
> I noticed Aspora is expanding into the US, Canada, Australia and Singapore after the Series B. I write The Rupee Bridge, a free 5-minute read for NRIs managing money across two countries: accounts, taxes, property and retirement.
>
> Our [X] readers open at [Y]%, mostly in [countries], and they're reading about exactly the decisions Aspora helps with.
>
> Would a test sponsorship in one issue be worth a look? Happy to send the media kit.

**To the founder of iNRI.** Subject: *sponsoring the rupee bridge*
> Hi [Name],
>
> iNRI's mix of investing, tax filing and money management maps almost one-to-one onto what The Rupee Bridge covers for NRIs each week.
>
> We're a free 5-minute newsletter with [X] NRI readers and a [Y]% open rate. For an early-stage team, a single sponsored slot is usually cheaper per sign-up than paid social.
>
> Want me to send options, including a free first placement to test response?

Follow-ups (+3 and +7 days): share one past issue as a sample. Then close the loop by asking who handles partnerships.

## 4. CSV to import into Pipewright

```csv
company,website,contact_name,contact_title,email
Aspora,https://www.aspora.com,,,
Belong,https://getbelong.com,,,
iNRI,https://www.goinri.com,,,
SBNRI,https://sbnri.com,,,
Instarem,https://www.instarem.com,,,
India For NRI,https://indiafornri.com,,,
```
Add the growth or partnerships contact's name and email for each (from LinkedIn or the company site) before drafting in Pipewright. Pipewright only guesses an email when it has a name.
