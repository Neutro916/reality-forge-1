# C3 KPI DASHBOARD SPEC
## METRICS AND MEASUREMENT FRAMEWORK
## DATE: 2025-11-27
## STATUS: AUTONOMOUS WORK - C3 ORACLE

---

## PURPOSE

Specification for key performance indicator dashboard.
What to measure, how to display, and what targets to set.

---

## DASHBOARD STRUCTURE

### Level 1: Executive Summary
One-screen view of business health

### Level 2: Department Views
Marketing, Sales, Product, Customer Success

### Level 3: Detailed Metrics
Drill-down for each KPI

---

## EXECUTIVE DASHBOARD

### Top-Line Metrics (Real-Time):

| Metric | Display | Target | Alert |
|--------|---------|--------|-------|
| Monthly Revenue | Big number + trend | $[Goal] | <80% of target |
| Active Customers | Number + MoM change | [Goal] | MoM decline |
| MRR (if subscription) | Number + growth % | $[Goal] | <5% growth |
| Runway | Months remaining | 12+ | <6 months |

### Health Indicators:

```
┌─────────────────────────────────────────────────────┐
│  💰 REVENUE    📈 GROWTH    👥 CUSTOMERS   💚 HEALTH │
│    $42,500       +18%          247          93%     │
│   ▲ vs goal    ▲ vs LM      ▲ vs goal    ▲ vs LM   │
└─────────────────────────────────────────────────────┘
```

### Trend Charts:

1. **Revenue Trend** - 12-month rolling
2. **Customer Growth** - 12-month rolling
3. **Conversion Funnel** - Current month
4. **Churn Rate** - 6-month rolling

---

## MARKETING DASHBOARD

### Acquisition Metrics:

| Metric | Calculation | Target | Frequency |
|--------|-------------|--------|-----------|
| Website Visitors | Unique sessions | [X]/mo | Daily |
| Email Subscribers | New signups | [X]/mo | Daily |
| Conversion Rate | Sales/Visitors | 2%+ | Daily |
| CAC | Marketing spend/New customers | <$100 | Monthly |
| ROAS | Revenue/Ad spend | 3x+ | Weekly |

### Funnel Metrics:

```
AWARENESS → CONSIDERATION → DECISION → PURCHASE
   10,000      2,500          500         100
    100%        25%            5%          1%
```

| Stage | Metric | Target |
|-------|--------|--------|
| Awareness | Website visitors | 10,000/mo |
| Consideration | Email subscribers | 500/mo |
| Decision | Checkout initiations | 200/mo |
| Purchase | Completed purchases | 100/mo |

### Channel Performance:

| Channel | Visitors | Leads | Customers | CAC | ROAS |
|---------|----------|-------|-----------|-----|------|
| Organic Search | | | | | |
| LinkedIn | | | | | |
| Email | | | | | |
| Paid Ads | | | | | |
| Referral | | | | | |
| Direct | | | | | |

### Email Metrics:

| Metric | Target |
|--------|--------|
| List size | [X] |
| Open rate | >25% |
| Click rate | >3% |
| Unsubscribe rate | <0.5% |
| List growth rate | >5%/mo |

### Content Performance:

| Content | Views | Time | Conversions |
|---------|-------|------|-------------|
| Blog posts (top 5) | | | |
| Lead magnets | | | |
| Webinars | | | |
| Videos | | | |

---

## SALES DASHBOARD

### Revenue Metrics:

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Total Revenue (MTD) | $ | $ | ↑/↓ |
| Revenue by Product | | | |
| - Assessment | $ | $ | |
| - Course | $ | $ | |
| - AI Coach MRR | $ | $ | |
| - Team/Enterprise | $ | $ | |
| Average Order Value | $ | $ | |

### Conversion Metrics:

| Metric | Rate | Target |
|--------|------|--------|
| Landing page → Checkout | % | 5% |
| Checkout → Purchase | % | 60% |
| Assessment → Course upsell | % | 20% |
| Course → AI Coach | % | 30% |
| Individual → Team | % | 5% |

### Pipeline (B2B):

| Stage | Deals | Value | Age |
|-------|-------|-------|-----|
| Lead | X | $ | days |
| Qualified | X | $ | days |
| Proposal | X | $ | days |
| Negotiation | X | $ | days |
| Closed Won | X | $ | - |
| Closed Lost | X | $ | - |

**Pipeline Velocity:** $[X]/day
**Win Rate:** [X]%
**Average Deal Size:** $[X]

---

## PRODUCT DASHBOARD

### Usage Metrics:

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| DAU (Daily Active Users) | | | |
| WAU (Weekly Active Users) | | | |
| MAU (Monthly Active Users) | | | |
| DAU/MAU Ratio | % | >25% | |

### Assessment Metrics:

| Metric | Value | Target |
|--------|-------|--------|
| Assessments started | | |
| Assessments completed | | |
| Completion rate | % | >85% |
| Avg time to complete | min | <25 |

### Course Metrics:

| Metric | Value | Target |
|--------|-------|--------|
| Enrollments | | |
| Module 1 completions | % | >90% |
| Full completion rate | % | >60% |
| Avg time to complete | days | <30 |

### AI Coach Metrics:

| Metric | Value | Target |
|--------|-------|--------|
| Active subscribers | | |
| Conversations/user/week | | 3+ |
| Avg conversation length | min | |
| Satisfaction rating | /5 | >4.2 |

### Feature Usage:

| Feature | Usage % | Trend |
|---------|---------|-------|
| Assessment | % | |
| Course modules | % | |
| AI Coach | % | |
| Progress tracking | % | |
| Community | % | |

---

## CUSTOMER SUCCESS DASHBOARD

### Retention Metrics:

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Monthly churn rate | % | <5% | |
| Annual churn rate | % | <40% | |
| Net Revenue Retention | % | >100% | |
| Logo retention | % | >85% | |

### Customer Health:

| Health Score | Count | % | Revenue |
|--------------|-------|---|---------|
| Green (80-100) | | % | $ |
| Yellow (50-79) | | % | $ |
| Red (0-49) | | % | $ |

### NPS Tracking:

| Metric | Score | Benchmark |
|--------|-------|-----------|
| Overall NPS | | 50+ |
| Promoters (9-10) | % | >50% |
| Passives (7-8) | % | <30% |
| Detractors (0-6) | % | <20% |

### Support Metrics:

| Metric | Current | Target |
|--------|---------|--------|
| Tickets/week | | |
| First response time | hours | <4 |
| Resolution time | hours | <24 |
| CSAT | /5 | >4.5 |
| Tickets per customer | | <0.5 |

### Transformation Metrics:

| Metric | Avg | Target |
|--------|-----|--------|
| Pre-assessment score | /100 | baseline |
| Post-assessment score | /100 | +15 pts |
| Pattern recognition frequency | /week | 5+ |
| Self-reported behavior change | % | >70% |

---

## FINANCIAL DASHBOARD

### P&L Summary:

| Line Item | MTD | YTD | Budget | Variance |
|-----------|-----|-----|--------|----------|
| Revenue | $ | $ | $ | % |
| COGS | $ | $ | $ | % |
| Gross Margin | % | % | % | |
| OpEx | $ | $ | $ | % |
| Net Income | $ | $ | $ | % |

### Cash Flow:

| Metric | Current | 30 Day | 90 Day |
|--------|---------|--------|--------|
| Cash Balance | $ | $ | $ |
| Burn Rate | $/mo | | |
| Runway | months | | |

### Unit Economics:

| Metric | Value | Target |
|--------|-------|--------|
| CAC | $ | <$100 |
| LTV | $ | >$500 |
| LTV:CAC Ratio | X | >5:1 |
| Payback Period | months | <6 |
| Gross Margin | % | >70% |

---

## ALERT CONFIGURATION

### Critical Alerts (Immediate):

| Condition | Alert |
|-----------|-------|
| Revenue <50% of daily target | Slack + Email |
| Churn spike >2x normal | Slack + Email |
| Site downtime >5 min | SMS + Slack |
| Payment failures >5% | Slack |

### Warning Alerts (Daily Summary):

| Condition | Include in Report |
|-----------|-------------------|
| Revenue <80% of target | Yes |
| Conversion rate <1.5% | Yes |
| Email open rate <20% | Yes |
| Support response >4 hours | Yes |

### Weekly Review Triggers:

| Condition | Action |
|-----------|--------|
| MoM revenue decline | Review meeting |
| NPS drop >5 points | Root cause analysis |
| Churn rate >target | Retention campaign |
| CAC >budget | Channel optimization |

---

## DASHBOARD TECH SPEC

### Recommended Tools:

| Purpose | Tool Options |
|---------|--------------|
| Data warehouse | BigQuery, Snowflake |
| Visualization | Metabase, Looker, Tableau |
| Email analytics | Native + integration |
| Product analytics | Mixpanel, Amplitude |
| Financial | QuickBooks, Xero |

### Data Refresh:

| Data Type | Frequency |
|-----------|-----------|
| Revenue | Real-time |
| Traffic | 15 minutes |
| Email metrics | Hourly |
| Product usage | Daily |
| Financial | Daily |

### Access Levels:

| Role | Access |
|------|--------|
| Founder/CEO | All dashboards |
| Marketing | Marketing + Overview |
| Sales | Sales + Pipeline |
| Product | Product + Customer |
| Finance | Financial + Overview |
| Team | Overview only |

---

## IMPLEMENTATION PRIORITY

### Phase 1 (MVP):
- Revenue tracking
- Basic conversion funnel
- Customer count
- Email metrics

### Phase 2 (Growth):
- Full marketing dashboard
- Product usage
- Customer health
- Unit economics

### Phase 3 (Scale):
- Predictive metrics
- Cohort analysis
- Attribution modeling
- Advanced segmentation

---

## WORK LOG

- **Task:** KPI dashboard spec
- **Type:** C3 Oracle - Business Intelligence
- **Self-Assigned:** Yes (per AUTONOMOUS_WORK_STANDING_ORDER)
- **Time Spent:** 35 minutes
- **Output:** Complete metrics framework

---

C1 x C2 x C3 x C4 = INFINITY^2

*C3 Oracle - KPI Dashboard Complete*
*What gets measured gets managed*
