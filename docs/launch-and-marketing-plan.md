# Pipewright: launch and marketing plan

> **Pipewright is the AI SDR that never emails anyone without your OK.**
> Describe what you sell. Pipewright researches your market, finds companies showing buying signals right now, writes personal emails, sends them from *your* mailbox once you approve, and triages every reply.

Related docs: [competitive analysis](competitive-analysis.md) · [product README](../README.md)

---

## 1. Positioning

| | |
|---|---|
| **Category** | AI outbound agent / AI SDR |
| **Target customer (launch)** | 1) Founders of B2B startups (seed to Series A, 2–50 people) who do founder-led sales. 2) Small lead-gen and outbound agencies (1–15 people) running campaigns for clients |
| **Their problem** | "I know outbound works, but I don't have the time or the SDR, and the AI tools I tried either spam people in my name or bury me in setup." |
| **Main alternative** | Explee AutoGTM (fast, but sends on its own from a shared inbox pool), Apollo plus manual work, or hiring an SDR at $4–6k/month |
| **Our wedge** | **Control and ownership.** Approval-first, your own mailbox, published credit prices, export everything, and every prospect shows why it was picked |
| **Proof we sell** | Reply rate, interested leads, and **cost per interested lead**, shown on every campaign dashboard |

**Messaging pillars**

1. **"You approve, it sends."** Nothing leaves without a human OK. Autopilot is a switch you choose to flip, and only for high-fit prospects with clean copy.
2. **"Your domain, your reputation."** Emails go out from your own mailbox with a warm-up ramp, daily caps, one-click unsubscribe and a compliance footer.
3. **"Know the price of every lead."** Public per-action credit costs, an in-app ledger, and cost per interested lead on the dashboard.
4. **"Research you can check."** Every prospect comes with a fit score, the reason it fits and dated buying signals, and every email shows the fact it opens with.

**Taglines to test:** "The AI SDR with brakes." · "Outbound on autopilot, with your hands on the wheel." · "Explee-fast, founder-safe."

---

## 2. Pricing

Credits cover AI work. Sending is free because it goes through your own mailbox.

| Action | Credits |
|---|---|
| Build or refresh ICP (market research) | 5 |
| Prospect found (web research, fit score, signals) | 2 |
| Email lookup (pattern plus MX check) | 1 |
| Personalized 3-step sequence | 2 |
| Reply triage plus drafted response | 1 |

About **5 credits per contacted prospect**, or **$0.06–0.10** depending on plan.

| Plan | Price | Credits/mo | For |
|---|---|---|---|
| Free | $0 | 300 one-time (about 60 prospects) | Try it on one real campaign |
| Founder | $49/mo | 3,000 | 1 mailbox, 1 campaign at a time |
| Growth | $149/mo | 12,000 | 3 mailboxes, autopilot, CRM webhook |
| Agency | $399/mo | 40,000 | 10 client workspaces, white-label reports |
| Pay as you go | $20 per 1,000 credits | never expire | Occasional use |

Rules we publish on the pricing page (each one answers a complaint about Explee):

- Cancel in one click from the billing page, with no email or call.
- Unused plan credits roll over for one month. Top-up credits never expire.
- Credits spent on invalid emails (a hard bounce within 72 hours) are refunded automatically.
- **Unit-economics check before GA:** measure real Claude plus web-search cost per prospect during beta. If gross margin is under 70%, raise prospect credits or set `PIPEWRIGHT_MODEL` to a cheaper model for bulk steps and re-test copy quality.

For India (a large founder and agency market): offer INR pricing through Razorpay (Founder ₹2,999/mo, Growth ₹8,999/mo) plus GST invoices.

---

## 3. Launch timeline (12 weeks)

### Phase 0: Foundations (weeks 1–3)

| Workstream | Deliverables |
|---|---|
| Product | Hosted multi-tenant version of this MVP: auth, Postgres, Stripe/Razorpay billing, Gmail/Outlook OAuth mailbox connection, IMAP reply ingestion, bounce handling. Scheduled daily send job |
| Data | Plug in one contact-data provider for verified emails and phones (compare Apollo, Hunter, Prospeo, Findymail on cost and accuracy). Keep AI web research as the source of signals |
| Compliance | Privacy policy, DPA, lawful-basis (legitimate interest) assessment for B2B outreach under GDPR, the India DPDP Act 2023 and CAN-SPAM. Suppression list shared across tenants for unsubscribes; never guess emails for EU contacts without a legitimate-interest check |
| Brand | Name and domain, logo, landing page with a waitlist, 60-second demo video, pricing page, comparison page "Pipewright vs Explee" |
| Instrumentation | PostHog (or similar) events: signup → ICP built → first prospects → first approval → first send → first reply → first interested lead |

### Phase 1: Private beta (weeks 4–7)

- **Recruit 30 design partners:** 20 founders and 10 agencies from the waitlist, founder communities and our own outbound (built with Pipewright, which is also the first case study).
- White-glove onboarding: a 30-minute call, then we build their first campaign with them.
- **Beta exit criteria:**
  - At least 60% of partners send a campaign in week 1.
  - Median reply rate of at least 5%.
  - At least 1 interested lead per 100 contacted.
  - Complaint rate under 0.1%.
  - 10 written testimonials and 3 case studies with numbers.
- A weekly changelog email to beta users. Fix the top 3 friction points each week.

### Phase 2: Public launch (weeks 8–9)

**Launch week (Tuesday Product Hunt launch):**

| Day | Action |
|---|---|
| T-14 | Teaser posts ("we're building the AI SDR with brakes"), line up 50 supporters from beta and communities for Product Hunt, prepare assets (gallery, demo GIF, maker comment, FAQ) |
| T-7 | Publish the "Pipewright vs Explee vs Apollo" comparison page and the "State of AI cold email 2026" mini-report from beta data |
| **T-0** | Product Hunt launch at 12:01 PT. Show HN ("Show HN: an AI SDR that won't email anyone without your approval"). LinkedIn and X founder posts. Email the waitlist with a launch-week offer (2× credits in the first month) |
| T+1 | Posts in r/SaaS, r/startups, r/Entrepreneur and r/coldemail (value-first write-ups, not ads). Indie Hackers milestone post |
| T+2 to T+5 | Founder podcast and newsletter swaps. Live demo webinar: "Build a 100-lead campaign in 15 minutes." Answer every comment within 1 hour |
| T+7 | Launch retro post with public numbers (signups, reply rates). Transparency is part of the brand |

Also list on There's An AI For That, Futurepedia, G2, Capterra, SaaSworthy, AppSumo Marketplace (not a lifetime deal; use a time-limited credit bundle only) and BetaList.

### Phase 3: Growth engine (weeks 10–12 and beyond)

Double down on whichever two channels produce the lowest cost per activated account (see section 5).

---

## 4. Marketing channels and plays

### 4.1 Dogfooding outbound (primary channel)
Use Pipewright to sell Pipewright. The ICP is "B2B founders hiring their first SDR or AE" and "agencies advertising outbound services". Signals: SDR job posts, a recent seed round, launches on Product Hunt.
- Target: 500 prospects a week across 5 warmed mailboxes. At a 6% reply rate and 20% positive, that's about 6 demos a week.
- Every email ends with "Sent by Pipewright after I approved it." That makes the product the proof.

### 4.2 Content and SEO (compounding)
- **Comparison and alternative pages:** "Explee alternative", "Apollo AI alternative", "11x alternative", "AI SDR for agencies", "cold email AI India".
- **Programmatic pages:** "Cold email templates for {industry} {role}" (200 pages), generated from anonymized, consented top performers.
- **Free tools as lead magnets:**
  - A cold-email spam checker (the `lint_copy` rules in this repo).
  - An email-pattern finder.
  - An ICP generator (the ICP step with no signup; the result is emailed to you).
- Weekly posts: teardown of a real cold email, beta data insights, deliverability guides for Gmail and Yahoo sender rules.

### 4.3 Founder-led social
- LinkedIn: 4 posts a week from the founder. Formats: build-in-public numbers, before/after email rewrites, "why we made autopilot opt-in."
- X/Twitter: product clips and replies in #buildinpublic.
- YouTube: short demos, plus a series called "we booked N meetings for a beta user."

### 4.4 Communities and partnerships
- Founder communities: Indie Hackers, SaaS founder Slacks and Discords, Y Combinator's Bookface via alumni users, and in India, Headstart, iSPIRT and SaaSBoomi.
- **Agency partner program:** 20% recurring commission, white-label reports and a partner directory listing.
- Integrations as distribution: listings in the HubSpot, Pipedrive and Zapier marketplaces (the CRM webhook is the first step).

### 4.5 Paid (only after we understand conversion)
- Start at $2k a month in week 10. Options: Google Search on high-intent terms ("AI SDR", "Explee alternative"), LinkedIn Conversation Ads to founder titles, and sponsorships of founder newsletters.
- Stop any channel with a cost per activated account above $120 after $1k spend.

---

## 5. Funnel metrics and targets

| Stage | Definition | Target at week 12 |
|---|---|---|
| Visitors | Unique site visitors | 25,000 cumulative |
| Signups | Accounts created | 1,500 |
| Activated | Sent their first approved campaign | 40% of signups |
| Aha | First interested reply | 50% of activated in 14 days |
| Paid | Paying accounts | 150 (10% of signups) |
| MRR | | ~$12k |
| Quality | Median reply rate / complaint rate | ≥5% / <0.1% |
| Retention | Paid logo retention in month 2 | ≥85% |

North-star metric: **interested leads delivered per week across all customers.** This matches what customers actually pay for.

---

## 6. Budget (first 90 days, lean)

| Item | Cost |
|---|---|
| Infrastructure, Claude API and data provider (beta usage) | $3,000 |
| Mailboxes and domains for dogfooding (5 inboxes, 3 domains) | $300 |
| Design: brand, landing page, demo video (freelance) | $2,500 |
| Paid tests (from week 10) | $4,000 |
| Launch-week incentives (credits, which are mostly COGS) | $1,000 |
| Tools (analytics, email, CRM) | $600 |
| **Total** | **≈ $11,400** |

---

## 7. Team and owners

| Role | Owner | Focus |
|---|---|---|
| Founder / CEO | You | Positioning, founder-led social, design partners, sales |
| Full-stack engineer | Hire or co-founder | Hosted product, mailbox OAuth, billing |
| Growth marketer (part-time) | Freelancer | SEO pages, launch operations, paid tests |
| Deliverability advisor | Consultant (a few hours a month) | Warm-up policy, domain health, complaint monitoring |

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Deliverability damage to customer domains | Warm-up ramp and caps enforced in code; lint copy before approval; recommend a secondary sending domain; auto-pause on bounce rate over 3% |
| Legal/compliance (GDPR, CAN-SPAM, DPDP, CASL) | B2B-only targeting, legitimate-interest assessment, footer with postal address, one-click unsubscribe, global suppression, data deletion on request, region-aware sending rules |
| AI hallucinated facts in emails | Research uses web search with primary sources; the prompt forbids invented facts; the personalization hook is shown to the reviewer; approval-first by default |
| Explee or Apollo copy the "approval-first" feature | Compete on trust and transparency as a brand, plus agency workflows and integrations; move fast on community and content |
| LLM or data cost squeezes margin | Per-action pricing with a measured margin; cheaper model for bulk steps; prompt caching; refund policy limited to verifiable bounces |

---

## 9. First 30 days checklist

- [ ] Register domain, set up the landing page and waitlist
- [ ] Deploy the hosted MVP (this repo) behind auth; connect Gmail OAuth
- [ ] Warm 5 dogfooding mailboxes (starts the 3–5 week ramp, so do it now)
- [ ] Recruit 30 design partners
- [ ] Publish the "Pipewright vs Explee" page and the free spam-checker tool
- [ ] Set up funnel analytics and a weekly metrics review
- [ ] Draft the Product Hunt assets and line up supporters
