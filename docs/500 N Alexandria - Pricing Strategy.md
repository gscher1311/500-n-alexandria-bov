# Pricing Strategy: 500 N Alexandria Ave
## 7 Units | RSO Value-Add | Koreatown / East Hollywood

**Generated:** February 17, 2026
**Methodology:** Per `LAAA-AI-Prompts/pricing/pricing_strategy.md` v1.0
**Prerequisites Met:** Underwriting (Phase 2A) + Comp Analysis (Phase 1B) complete

---

## INPUTS USED

### Subject Metrics (from Underwriting Output)
| Metric | Current | Pro Forma |
|--------|---------|-----------|
| GSR | $141,036/yr | $167,100/yr |
| EGI (5% vacancy) | $133,984 | $158,745 |
| Non-Tax OpEx | $49,203 | $49,203 |
| Units | 7 | 7 |
| Building SF | 4,360 | 4,360 |

**Note:** NOI is price-dependent (property taxes reassess at 1.17% of purchase price). Cap rates and NOI are calculated dynamically below.

### Comp Anchors (from Comp Analysis Output)

**Closed Sales — High-Confidence Set (Comps #2 and #3 only):**
| Metric | Comp 2 (212 S Berendo) | Comp 3 (101 S Kenmore) | Average |
|--------|----------------------|----------------------|---------|
| $/Unit | $190,625 | $199,375 | $195,000 |
| $/SF | $228.29 | $204.33 | $216.31 |
| Cap Rate (adj) | 4.15% | 7.29% | 5.72% |
| GRM | 12.61x | 9.08x | 10.85x |

**Closed Sales — All Non-Distressed (Comps #1, #2, #3):**
| Metric | Average | Median |
|--------|---------|--------|
| $/Unit | $168,889 | $190,625 |
| GRM | 10.43x | 9.59x |

**On-Market — Pending Comp (502 N Serrano, most actionable):**
- LP $1,795,000 | 8 units | $/Unit $224,375 | Cap 5.57% | GRM 10.97x

---

## STEP 1: DERIVE PRICE BANDS

### Method A: Cap-Implied Price

Since taxes are reassessed to the sale price, NOI is a function of price. Solving for price at target cap rates:

**Formula:** Price = (EGI − Non-Tax OpEx) / (Cap Rate + Tax Rate)
= ($133,984 − $49,203) / (Cap + 0.0117)
= $84,781 / (Cap + 0.0117)

| Target Cap | Implied Price | NOI at Price | $/Unit | GRM |
|-----------|--------------|-------------|--------|-----|
| 6.50% | $1,355,000 | $86,915 | $193,571 | 9.61x |
| 6.00% | $1,295,000 | $84,784 | $185,000 | 9.19x |
| 5.75% | $1,268,000 | $83,844 | $181,143 | 8.99x |
| 5.50% | $1,242,000 | $82,932 | $177,429 | 8.81x |
| 5.25% | $1,217,000 | $82,027 | $173,857 | 8.63x |
| 5.00% | $1,194,000 | $81,201 | $170,571 | 8.47x |

**Comp-supported cap range:** 5.00%–7.29% from closed comps. The subject's small size, limited parking, and RSO drag suggests cap should be in the 5.25%–5.75% range for a well-marketed deal. This implies **$1,225,000–$1,275,000**.

### Method B: $/Unit-Implied Price

| Anchor | $/Unit | × 7 Units | Adjustment | Adjusted Price |
|--------|--------|-----------|------------|----------------|
| High-confidence avg | $195,000 | $1,365,000 | -10% (smaller bldg, limited parking, mixed mix) | **$1,228,500** |
| Comp 3 (Kenmore, best) | $199,375 | $1,395,625 | -12% (Kenmore has 8 1BR, 7,806 SF, 0 parking vs subject's 7 mixed, 4,360 SF, ~1 parking) | **$1,228,150** |
| Comp 2 (Berendo) | $190,625 | $1,334,375 | -5% (Berendo has 8 2BR, deep RSO, bigger lot) | **$1,267,656** |
| Comp 1 (New Hampshire) | $116,667 | $816,667 | +20% (NH is 12 studios, off-market, worst comp) | **$980,000** (floor only) |

**$/Unit consensus: $1,225,000–$1,275,000**

**ADU Value Component:** The subject has a 2025 ADU that adds ~$22,500/yr income ($1,875/mo). Capitalizing at 5.5% yields ~$215,000 incremental value. This is already embedded in the $/unit and GRM calculations above (the ADU is one of the 7 units). But it's worth noting: without the ADU, the property would be a 6-unit building at $1,050K-$1,100K ($175K-$183K/unit), which aligns with the lower end of comps.

### Method C: GRM-Implied Price

| Target GRM | GSR × GRM | Price |
|-----------|-----------|-------|
| 9.5x | $141,036 × 9.5 | **$1,339,842** |
| 9.25x | $141,036 × 9.25 | **$1,304,583** |
| 9.0x | $141,036 × 9.0 | **$1,269,324** |
| 8.75x | $141,036 × 8.75 | **$1,234,065** |
| 8.5x | $141,036 × 8.5 | **$1,198,806** |

**Comp-supported GRM range:** Non-distressed closed comps range 9.08x–12.61x, median 9.59x. But Comp 2 (Berendo) at 12.61x is inflated by deeply below-market rents. Comp 3 (Kenmore) at 9.08x is the most reliable anchor. Subject GRM of 8.75x–9.25x is appropriate given similar vintage but smaller scale.

**GRM consensus: $1,225,000–$1,300,000**

---

## STEP 2: CONSENSUS PRICING

| Method | Low End | Central | High End |
|--------|---------|---------|----------|
| Cap-Implied | $1,225,000 | $1,250,000 | $1,275,000 |
| $/Unit-Implied | $1,225,000 | $1,250,000 | $1,275,000 |
| GRM-Implied | $1,225,000 | $1,275,000 | $1,300,000 |
| **Consensus** | **$1,225,000** | **$1,250,000** | **$1,300,000** |

All three methods converge remarkably tightly in the **$1,225,000–$1,300,000** corridor.

---

## PRICING LADDER

| Tier | Price | Cap Rate | $/Unit | GRM | $/SF |
|------|-------|----------|--------|-----|------|
| **Stretch List** | **$1,325,000** | 5.09% | $189,286 | 9.40x | $303.90 |
| **Suggested List** | **$1,275,000** | 5.48% | $182,143 | 9.04x | $292.43 |
| **Expected Sale (High)** | **$1,275,000** | 5.48% | $182,143 | 9.04x | $292.43 |
| **Expected Sale (Low)** | **$1,200,000** | 5.98% | $171,429 | 8.51x | $275.23 |

### Price Increment: $25,000 (sub-$3M property per workflow spec)

### Full Pricing Matrix ($25K Steps)

| Price | Cap (Current) | Cap (PF) | $/Unit | GRM | $/SF | DSCR (55% LTV, 6.00%) |
|-------|-------------|---------|--------|-----|------|----------------------|
| $1,150,000 | 6.22% | 8.49% | $164,286 | 8.16x | $263.76 | 1.57x |
| $1,175,000 | 6.04% | 8.28% | $167,857 | 8.33x | $269.50 | 1.53x |
| $1,200,000 | 5.89% | 8.08% | $171,429 | 8.51x | $275.23 | 1.49x |
| $1,225,000 | 5.75% | 7.89% | $175,000 | 8.69x | $280.96 | 1.45x |
| $1,250,000 | 5.61% | 7.71% | $178,571 | 8.86x | $286.70 | 1.42x |
| **$1,275,000** | **5.48%** | **7.42%** | **$182,143** | **9.04x** | **$292.43** | **1.38x** |
| $1,300,000 | 5.35% | 7.35% | $185,714 | 9.22x | $298.17 | 1.35x |
| $1,325,000 | 5.23% | 7.17% | $189,286 | 9.40x | $303.90 | 1.32x |
| $1,350,000 | 5.11% | 7.02% | $192,857 | 9.57x | $309.63 | 1.29x |
| $1,375,000 | 4.99% | 6.87% | $196,429 | 9.75x | $315.37 | 1.26x |
| $1,400,000 | 4.89% | 6.73% | $200,000 | 9.93x | $321.10 | **1.23x** ⚠ |

**⚠ Financing Threshold:** At $1,375,000+, DSCR approaches the 1.25x lender minimum. At $1,400,000, DSCR drops to 1.23x — financing would be DCR-constrained, reducing actual LTV below 55%. This creates buyer resistance above $1,350,000.

---

## RATIONALE

### Primary Anchors Used
1. **Comp 3 (101 S Kenmore)** — Anchor comp, best data quality (9/10). 8 units, 1925, RSO, $199,375/unit, cap 7.29%, GRM 9.08x. Sold 7/21/2025. Subject trades at a discount due to smaller scale, mixed unit types, and tighter lot.
2. **Comp 2 (212 S Berendo)** — Best unit-mix match (2BR-heavy). 8 units, 1923, RSO, $190,625/unit, GRM 12.61x. Subject has similar value-add profile but less dramatic upside (18.5% vs 108%).
3. **Pending Comp H (502 N Serrano)** — Market validation at $224,375/unit (LP). 8 units, 1956, RSO. Higher $/unit reflects better condition (copper, seismic retrofit, larger units).

### Adjustments Applied
| Factor | Direction | Magnitude | Rationale |
|--------|-----------|-----------|-----------|
| Smaller unit count (7 vs 8-12) | Discount | -5% | Less diversified, harder to finance at small loan size |
| ADU (2025 CofO) | Premium | +8-10% | Modern legal unit, income-producing, TOC Tier 3 development potential |
| Limited parking (~0.14 ratio) | Discount | -3-5% | Below market (comps avg 0-0.50 ratio); K-town/transit mitigates somewhat |
| Pre-war vintage (1923/1929) | Discount | -3% | Oldest in comp set; higher maintenance expectations |
| Small lot (4,558 SF) | Discount | -2-3% | Limited expansion potential; comps avg 7,000-9,000 SF lots |
| RSO upside (18.5%) | Premium | +3-5% | Value-add appeal; 4 RSO units with turnover upside |
| 100% occupied | Premium | +2% | No immediate vacancy risk; immediate cash flow |

**Net adjustment from raw comp average:** -5% to -8% (adjustments largely offset)

### Market Context
- **Inventory:** 7 active listings + 1 pending in 90004 zip for multifamily (5-12 units). Moderate supply — not distressed but not tight.
- **DOM trends:** Closed comps averaged 13 DOM (excl. distressed). On-market averaging 79 DOM, with two stale listings (133 and 285 days) dragging up the average. Fresh listings (121/127 S Oxford) at 1 DOM suggest continued market activity.
- **SP/LP trend:** Non-distressed closed at 94.96% avg SP/LP. Suggests expect 3-5% negotiation from list price.
- **Rate environment:** Fed at 3.50-3.75%, 5Y UST at 3.75%. Rates have declined from 2024 peaks, improving buyer purchasing power. Two more 25bp cuts priced in for 2026. Favorable for sellers.
- **Measure ULA:** Not applicable (property well below $5M threshold).
- **Buyer pool:** Primarily 1031 exchange investors, local operators, and small portfolio consolidators. Small-balance financing (~$700K loan) limits some institutional buyers.

---

## COMP SUPPORT

| Comp Address | Sale Price | Units | Cap | $/Unit | GRM | Relevance to Subject |
|-------------|-----------|-------|-----|--------|-----|---------------------|
| 101 S Kenmore Ave (SOLD) | $1,595,000 | 8 | 7.29% | $199,375 | 9.08x | **Primary anchor.** Same vintage, RSO, zip. Subject discounted for smaller scale + parking. |
| 212 S Berendo St (SOLD) | $1,525,000 | 8 | 4.15% | $190,625 | 12.61x | Best unit-mix match. Deep RSO rents inflate GRM. Subject has less extreme upside. |
| 247 N New Hampshire (SOLD) | $1,400,000 | 12 | 5.21%* | $116,667 | 9.59x | Floor reference. 12 studios, off-market. Subject's 2BR mix commands premium. |
| 502 N Serrano (PENDING) | $1,795,000 | 8 | 5.57% | $224,375 | 10.97x | **Market validation.** Pending sale confirms buyer interest at higher $/unit for better product. |
| 310 N St Andrews (ACTIVE) | $2,490,000 | 8 | 5.06% | $311,250 | 13.72x | ADU comp (2 ADUs, 2025). Premium pricing reflects full renovation + ADU value. |

---

## CONFIDENCE LEVEL

**Confidence:** **Medium-High**

**Rationale:**
- Three methods converge within a tight $75K band ($1,225K-$1,300K) — strong internal consistency
- Best closed comp (Kenmore, 9/10 quality) provides a solid anchor
- Pending comp (Serrano) validates active buyer demand in the submarket
- Key limitation: only 3 usable closed comps (excluding distressed); ideally would want 5-7 for higher confidence

**Key Risks to Pricing:**
1. **Financing constraint at $1,350K+:** DSCR drops below 1.25x at $1,375K+, creating a hard ceiling for leveraged buyers. Only cash or low-leverage buyers could go above this.
2. **No T-12:** Expenses are 100% benchmark-derived. If actual expenses are materially higher (e.g., master-metered gas adding $4K+), NOI drops and pricing support weakens.
3. **RSO turnover timeline:** The 18.5% rent upside is real but tenant-dependent. If RSO tenants don't turn over within buyer's investment horizon (3-5 years), the value-add thesis weakens.
4. **Parking deficiency:** Only ~1 space for 7 units (0.14 ratio). In a neighborhood with difficult street parking, this could be a meaningful buyer objection. Mitigated somewhat by transit access (Walk Score 85, Metro B Line 0.6 mi).
5. **Small loan size:** ~$700K loan at 55% LTV. Some lenders have $1M minimums for commercial loans. May need to target credit unions or Chase CTL. Limits buyer pool somewhat.

---

## RECOMMENDED STRATEGY

**Suggested List Price: $1,275,000** ($182,143/unit | 5.48% cap | 9.04x GRM)

This positions the property:
- At the midpoint of the three-method consensus range
- 4.5% above the Expected Sale Low ($1,200K), allowing negotiation room
- Below the $1,350K+ financing constraint zone
- At a cap rate (5.48%) that is competitive with on-market inventory
- At a $/unit ($182K) below the Kenmore closed comp ($199K), reflecting appropriate size/parking discount
- At a GRM (9.04x) tight to the Kenmore benchmark (9.08x), reflecting similar rent quality

**Marketing Positioning:**
- Lead with pro forma cap (7.42% at $1,275K) — very attractive for value-add buyers
- Lead with ADU narrative (newly completed, CofO 2025, legal income)
- Lead with TOC Tier 3 development upside for long-term holders
- Acknowledge RSO; position as "stable current income with turnover upside"
- Target 1031 exchange buyers and local operators within 60-day close timeline

---

*Generated by Cursor | Phase 2B | February 17, 2026 | LAAA BOV Web Presentation System*
