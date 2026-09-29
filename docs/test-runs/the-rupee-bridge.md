# Test run: The Rupee Bridge (therupeebridge.beehiiv.com)

_Manual run of Pipewright's steps, September 2026. The newsletter's own description:_
> "A free 5-minute read for NRIs managing money across two countries: accounts, taxes, property, retirement, and the move…" (by Finostock)

**Goal: find partners now and sponsors later, never individual subscribers.** Cold-emailing individual NRIs to subscribe would be spam and would break DPDP, GDPR and CAN-SPAM rules. The companies that want to reach NRIs are the right people to email.

## 0. Where you are now: 9 subscribers (UAE, US, India)

That's too early to sell sponsorships. Sponsors buy reach and proof, and pitching Aspora with 9 readers would use up a contact you'll want later. **Run outbound in two phases:**

| Phase | Subscribers | Who to email | What you offer | What you get |
|---|---|---|---|---|
| **1. Grow** (now) | 9 → ~1,000 | NRI tax CAs, property managers and advisors; NRI fintechs' content teams; UAE and US Indian community groups | A free, credited expert feature or co-written guide in an issue that they share with their clients or members | Distribution to their audience, plus credibility |
| **2. Monetize** | 1,000+ with a strong open rate | The sponsor list in section 2 | Paid placements with real numbers | Revenue |

Phase 1 is still B2B outreach to businesses and community organizers, not to individual NRIs, so it's legitimate cold email.

**Grow faster alongside outbound (no Pipewright needed):**
- Turn on beehiiv's recommendations network and swap recommendations with other finance newsletters of similar size.
- Put a subscribe CTA in Finostock's own channels, website and WhatsApp.
- Post each issue's most useful tip on LinkedIn, and in Indian-expat groups in Dubai and the US where the group rules allow it.
- Write evergreen issues such as "NRE vs NRO in 2026" and "Selling property in India as an NRI: the TDS trap". These are also what partners will want to share.

**Pipewright settings for Phase 1:** in the ICP JSON, set `buyer_titles` to `["Founder", "Partner (CA firm)", "Content / Community Lead", "Community Organizer"]` and add the value prop "Free credited feature in a newsletter for NRIs in the UAE, US and India".

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

### Phase 1: partner emails (send now)

**To the founder or a partner at an NRI tax or legal firm (for example India For NRI).** Subject: *nri tax feature idea*
> Hi [Name],
>
> I write The Rupee Bridge, a free 5-minute newsletter for NRIs in the UAE, US and India who manage money across two countries.
>
> I'm planning an issue on [NRI capital gains / TDS when selling property] and would love to feature your team as the expert, with your name and firm credited and a link to your NRI services.
>
> In return, would you share the issue with your NRI clients? Happy to send the draft for your review first.

**To the content or community lead at an NRI fintech (for example SBNRI, iNRI or Belong).** Subject: *co-written guide for nris*
> Hi [Name],
>
> I noticed [company] publishes a lot of NRI money content. I run The Rupee Bridge, a new free newsletter for NRIs in the UAE, US and India.
>
> Would you co-write one guide with me, for example "[NRE vs NRO in 2026]"? You'd get the expert byline and a link, and we'd both share it with our audiences.
>
> No cost. I'm building a small group of founding partners.

**To an Indian community association or group organizer in the UAE or US.** Subject: *free money guide for your members*
> Hi [Name],
>
> I write The Rupee Bridge, a free 5-minute read for NRIs on accounts, taxes, property and moving back.
>
> Could I share a one-page "[NRI money checklist for 2026]" with your members, free and with no sales pitch? If it's useful, members can subscribe for more.

Follow-ups (+4 and +10 days): share the draft or a finished sample issue. Then close the loop politely.

### Phase 2: sponsor email (keep for when you reach 1,000+)

**To the growth or partnerships lead at Aspora.** Subject: *nri readers for aspora*
> Hi [Name],
>
> I noticed Aspora is expanding into the US, Canada, Australia and Singapore after the Series B. I write The Rupee Bridge, a free 5-minute read for NRIs managing money across two countries: accounts, taxes, property and retirement.
>
> Our [X] readers open at [Y]%, mostly in the UAE, US and India, and they're reading about exactly the decisions Aspora helps with.
>
> Would a test sponsorship in one issue be worth a look? Happy to send the media kit.

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

## 5. Tax-firm contacts for Phase 1 (found September 2026)

Ready to import: [`rupee-bridge-tax-firms.csv`](rupee-bridge-tax-firms.csv). Only emails that the firms publish themselves are included. Nothing was guessed.

| Firm | Contact | Email | Pipewright check | Source |
|---|---|---|---|---|
| S Lohia & Associates (Noida/Delhi) | Sulabh Lohia, founder | sulabhlohia@slohia.com | valid (MX ok) | [slohia.com/contact](https://www.slohia.com/contact/) |
| R Pareva & Company (Delhi) | CA Rahul Pareva, founder | rahul@rpareva.com | valid | [rpareva.com founder page](https://www.rpareva.com/meet-the-founder) |
| Vidhu Duggal & Co. | Vidhu Duggal | vidhu@vidhuduggalandco.com | valid | [NRI services page](https://www.vidhuduggalandco.com/services/nri-tax-consultant-india) |
| India For NRI (Delhi, London) | Sidhant Agarwal (CA), founder; co-founder Sanyam | not published. Use the [contact form](https://indiafornri.com/contactus) or +91-9560020722 | – | [About](https://indiafornri.com/aboutus) |
| Dinesh Aarjav & Associates (Delhi) | CA Dinesh Jain, founder and mentor | not shown in search. Check the [contact page](https://www.dineshaarjav.com/contact) | – | [About](https://www.dineshaarjav.com/about) |
| CA for NRI / Zenify Consultancy | CA Ajay R. Vaswani | hidden on the site. Check [cafornri.com](https://cafornri.com/about-us/) | – | [About](https://cafornri.com/about-us/) |
| RVG Chartered Accountants (Dubai) | no name found | use the site contact | – | [NRI taxation in Dubai](https://rvguae.com/nri-taxation-services-in-dubai/) |

Notes:
- **nritaxservice.in has the same phone number as Sulabh Lohia** (+91 9811353219), so it's likely the same group. Email only one of them.
- Generic inboxes (help@slohia.com, info@rpareva.com, info@nritaxservice.in) are fallbacks. Personal addresses get more replies.
- Several firms (CA for NRI, India For NRI) run NRI webinars and masterclasses. Offering to feature one of those sessions in an issue is a warm opener.
- Rows without an email import as "missing". Add an email in the app once you find one, and Pipewright re-checks it.
