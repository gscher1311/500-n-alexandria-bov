#!/usr/bin/env python3
"""
Build script for 500 N Alexandria Ave BOV — Los Angeles, CA 90004
Generates a single index.html file for the BOV web presentation.
"""
import base64, json, os, sys, time, urllib.request, urllib.parse, io, statistics, math

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
OUTPUT = os.path.join(SCRIPT_DIR, "index.html")
BOV_BASE_URL = "https://500nalexandria.laaa.com"
PDF_WORKER_URL = "https://laaa-pdf-worker.laaa-team.workers.dev"
PDF_FILENAME = "BOV - 500 N Alexandria Ave, Los Angeles.pdf"
PDF_LINK = PDF_WORKER_URL + "/?url=" + urllib.parse.quote(BOV_BASE_URL + "/", safe="") + "&filename=" + urllib.parse.quote(PDF_FILENAME, safe="")

# ============================================================
# RAG CHATBOT CONFIG
# ============================================================
ENABLE_CHATBOT = True
BOV_NAMESPACE = "alexandria-500"
CHAT_WORKER_URL = "https://laaa-chat-worker.laaa-team.workers.dev"
PROPERTY_DISPLAY_NAME = "500 N Alexandria Ave"
STARTER_QUESTIONS = [
    "What is the asking price and cap rate?",
    "Tell me about the ADU and value-add potential",
    "Summarize the rent roll and current rents",
    "What do the comparable sales show?"
]

# ============================================================
# IMAGE LOADING
# ============================================================
def load_image_b64(filename):
    path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return ""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"  Loaded image: {filename} ({len(data)//1024}KB b64)")
    return f"data:{mime};base64,{data}"

print("Loading images...")
IMG = {
    "logo": load_image_b64("LAAA_Team_White.png"),
    "glen": load_image_b64("Glen_Scher.png"),
    "filip": load_image_b64("Filip_Niculete.png"),
    "hero": load_image_b64("hero.png"),
    "grid1": load_image_b64("grid1.png"),
    "grid2": load_image_b64("grid2.png"),
    "grid3": load_image_b64("grid3.png"),
    "grid4": load_image_b64("grid4.png"),
    "loc_map": load_image_b64("location-map.png"),
    "closings_map": load_image_b64("closings-map.png"),
    "team_aida": load_image_b64("Aida_Memary_Scher.png"),
    "team_logan": load_image_b64("Logan_Ward.png"),
    "team_morgan": load_image_b64("Morgan_Wetmore.png"),
    "team_luka": load_image_b64("Luka_Leader.png"),
    "team_jason": load_image_b64("Jason_Mandel.png"),
    "team_alexandro": load_image_b64("Alexandro_Tapia.png"),
    "team_blake": load_image_b64("Blake_Lewitt.png"),
    "team_mike": load_image_b64("Mike_Palade.png"),
    "team_tony": load_image_b64("Tony_Dang.png"),
}

# ============================================================
# SUBJECT COORDINATES
# ============================================================
SUBJECT_LAT, SUBJECT_LNG = 34.079304, -118.297881

# ============================================================
# GEOCODING — Cached coordinates
# ============================================================
ADDRESSES = {
    "101 S Kenmore Ave, Los Angeles, CA 90004": (34.0728, -118.2936),
    "212 S Berendo St, Los Angeles, CA 90004": (34.0688, -118.2933),
    "247 N New Hampshire Ave, Los Angeles, CA 90004": (34.0765, -118.2927),
    "143 N Commonwealth Ave, Los Angeles, CA 90004": (34.0749, -118.2876),
    "502 N Serrano Ave, Los Angeles, CA 90004": (34.0795, -118.3068),
    "121 S Oxford Ave, Los Angeles, CA 90004": (34.0723, -118.2981),
    "127 S Oxford Ave, Los Angeles, CA 90004": (34.0721, -118.2981),
    "543 N Ardmore Ave, Los Angeles, CA 90004": (34.0807, -118.2999),
    "310 N St Andrews Pl, Los Angeles, CA 90004": (34.0774, -118.3090),
    "426 N Virgil Ave, Los Angeles, CA 90004": (34.0786, -118.2867),
    "4053 Oakwood Ave, Los Angeles, CA 90004": (34.0788, -118.2959),
    "313 N Alexandria Ave, Los Angeles, CA 90004": (34.0738, -118.2979),
    "634 N Alexandria Ave, Los Angeles, CA 90004": (34.0836, -118.2980),
    "229 S Normandie Ave, Los Angeles, CA 90004": (34.0681, -118.3009),
    "466 N Westmoreland Ave, Los Angeles, CA 90004": (34.0831, -118.2942),
    "111 N Normandie Ave, Los Angeles, CA 90004": (34.0767, -118.3010),
    "955 Fedora St, Los Angeles, CA 90005": (34.0645, -118.2966),
    "247 S Alexandria Ave, Los Angeles, CA 90004": (34.0697, -118.2978),
    "326 S Normandie Ave, Los Angeles, CA 90020": (34.0663, -118.3010),
    "520 S Mariposa Ave, Los Angeles, CA 90020": (34.0641, -118.2948),
    "739 S Normandie Ave, Los Angeles, CA 90005": (34.0577, -118.3011),
    "516 S St Andrews Pl, Los Angeles, CA 90020": (34.0642, -118.3090),
    "132 Westmoreland Ave, Los Angeles, CA 90004": (34.0750, -118.2942),
}
print(f"Using cached geocode data ({len(ADDRESSES)} addresses)")

# ============================================================
# FINANCIAL DATA
# ============================================================
LIST_PRICE = 1_275_000
TAX_RATE = 0.0117
UNITS = 7
SF = 4_360
GSR = 141_036
PF_GSR = 167_100
VACANCY_PCT = 0.05
OTHER_INCOME = 0
NON_TAX_CUR_EXP = 49_203
NON_TAX_PF_EXP = 49_203

INTEREST_RATE = 0.06
AMORTIZATION_YEARS = 30
LTV = 0.55
LOAN_CONSTANT = 0.072
LOAN_TERM_YEARS = 5
LOT_SIZE_ACRES = 0.10

def calc_principal_reduction_yr1(loan_amount, annual_rate, amort_years):
    r = annual_rate / 12
    n = amort_years * 12
    monthly_pmt = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
    balance = loan_amount
    total_principal = 0
    for _ in range(12):
        interest = balance * r
        principal = monthly_pmt - interest
        total_principal += principal
        balance -= principal
    return total_principal

def calc_metrics(price):
    taxes = price * TAX_RATE
    cur_egi = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    pf_egi = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    cur_exp = NON_TAX_CUR_EXP + taxes
    pf_exp = NON_TAX_PF_EXP + taxes
    cur_noi = cur_egi - cur_exp
    pf_noi = pf_egi - pf_exp
    loan_amount = price * LTV
    down_payment = price * (1 - LTV)
    debt_service = loan_amount * LOAN_CONSTANT
    net_cf_cur = cur_noi - debt_service
    net_cf_pf = pf_noi - debt_service
    coc_cur = net_cf_cur / down_payment * 100 if down_payment > 0 else 0
    coc_pf = net_cf_pf / down_payment * 100 if down_payment > 0 else 0
    dcr_cur = cur_noi / debt_service if debt_service > 0 else 0
    dcr_pf = pf_noi / debt_service if debt_service > 0 else 0
    prin_red = calc_principal_reduction_yr1(loan_amount, INTEREST_RATE, AMORTIZATION_YEARS)
    total_return_cur = net_cf_cur + prin_red
    total_return_pf = net_cf_pf + prin_red
    total_return_pct_cur = total_return_cur / down_payment * 100 if down_payment > 0 else 0
    total_return_pct_pf = total_return_pf / down_payment * 100 if down_payment > 0 else 0
    return {"price": price, "taxes": taxes, "cur_noi": cur_noi, "pf_noi": pf_noi,
            "cur_egi": cur_egi, "pf_egi": pf_egi, "cur_exp": cur_exp, "pf_exp": pf_exp,
            "per_unit": price / UNITS, "per_sf": price / SF,
            "cur_cap": cur_noi / price * 100, "pf_cap": pf_noi / price * 100,
            "grm": price / GSR, "pf_grm": price / PF_GSR,
            "loan_amount": loan_amount, "down_payment": down_payment,
            "debt_service": debt_service, "net_cf_cur": net_cf_cur, "net_cf_pf": net_cf_pf,
            "coc_cur": coc_cur, "coc_pf": coc_pf, "dcr_cur": dcr_cur, "dcr_pf": dcr_pf,
            "prin_red": prin_red, "total_return_cur": total_return_cur, "total_return_pf": total_return_pf,
            "total_return_pct_cur": total_return_pct_cur, "total_return_pct_pf": total_return_pct_pf}

MATRIX_PRICES = list(range(1_400_000, 1_125_000, -25_000))
MATRIX = [calc_metrics(p) for p in MATRIX_PRICES]
AT_LIST = calc_metrics(LIST_PRICE)

print(f"Financials at list ${LIST_PRICE:,.0f}: Cap {AT_LIST['cur_cap']:.2f}%")

# ============================================================
# UNIT MIX DATA
# ============================================================
RENT_ROLL = [
    ("500", "2BR/1BA", 620, 2400, 2400),
    ("502", "2BR/1BA", 620, 1290, 2200),
    ("504", "2BR/1BA", 620, 1599, 2200),
    ("506", "2BR/1BA", 620, 2200, 2300),
    ("508(1)", "Studio", 400, 1494, 1500),
    ("508(2)", "Studio", 400, 895, 1450),
    ("510", "ADU", 248, 1875, 1875),
]

SALE_COMPS = [
    {"num": 1, "addr": "101 S Kenmore Ave", "city": "Los Angeles", "units": 8, "sf": 7806, "yr": 1925, "price": 1595000, "ppu": 199375, "psf": 204.33, "cap": 7.29, "grm": 9.08, "date": "07/21/2025", "notes": "Anchor comp; 8\u00d7 1BR, RSO, on-site laundry, best data quality"},
    {"num": 2, "addr": "212 S Berendo St", "city": "Los Angeles", "units": 8, "sf": 6680, "yr": 1923, "price": 1525000, "ppu": 190625, "psf": 228.29, "cap": 4.15, "grm": 12.61, "date": "08/28/2025", "notes": "8\u00d7 2BR, deep RSO, 108% rent upside, 1031 exchange"},
    {"num": 3, "addr": "247 N New Hampshire Ave", "city": "Los Angeles", "units": 12, "sf": 7736, "yr": 1922, "price": 1400000, "ppu": 116667, "psf": 180.97, "cap": None, "grm": 9.59, "date": "08/27/2025", "notes": "12 studios, off-market, financial data unreliable"},
    {"num": 4, "addr": "143 N Commonwealth Ave", "city": "Los Angeles", "units": 6, "sf": 5258, "yr": 1951, "price": 1425000, "ppu": 237500, "psf": 271.02, "cap": None, "grm": 11.10, "date": "01/21/2026", "notes": "DISTRESSED \u2014 Auction/Trust sale, SP/LP 79.2%"},
]

ACTIVE_COMPS = [
    {"num": 1, "addr": "502 N Serrano Ave", "units": 8, "price": 1795000, "ppu": 224375, "cap": 5.57, "grm": 10.97, "dom": 145, "status": "Pending", "notes": "Copper, seismic retrofit, CBRE listing"},
    {"num": 2, "addr": "121 S Oxford Ave", "units": 9, "price": 1800000, "ppu": 200000, "cap": 5.66, "grm": 13.73, "dom": 1, "status": "Active", "notes": "9\u00d7 1BR, 3 garage; brand new listing"},
    {"num": 3, "addr": "127 S Oxford Ave", "units": 8, "price": 1800000, "ppu": 225000, "cap": 5.51, "grm": 12.34, "dom": 1, "status": "Active", "notes": "8\u00d7 1BR, 0 parking; adjacent to 121 S Oxford"},
    {"num": 4, "addr": "543 N Ardmore Ave", "units": 12, "price": 2300000, "ppu": 191667, "cap": 4.77, "grm": 11.36, "dom": 12, "status": "Active", "notes": "New roof 2025, seismic retrofit, 12 parking"},
    {"num": 5, "addr": "310 N St Andrews Pl", "units": 8, "price": 2490000, "ppu": 311250, "cap": 5.06, "grm": 13.72, "dom": 20, "status": "Active", "notes": "6 main + 2 ADU (2025), renovated"},
    {"num": 6, "addr": "426 N Virgil Ave", "units": 5, "price": 1599000, "ppu": 319800, "cap": 5.95, "grm": 14.08, "dom": 133, "status": "Active", "notes": "Price reduced from $1,799K; market resistant"},
    {"num": 7, "addr": "4053 Oakwood Ave", "units": 12, "price": 2600000, "ppu": 216667, "cap": 5.83, "grm": 10.47, "dom": 285, "status": "Active", "notes": "Price reduced from $2,800K; very stale"},
]

RENT_COMPS_2BR = [
    {"addr": "313 N Alexandria Ave", "rent": 2150, "reno": "Classic", "dist": "0.4 mi", "features": "New stove, laminate floors, 2-car tandem parking"},
    {"addr": "634 N Alexandria Ave", "rent": 2200, "reno": "Classic", "dist": "0.3 mi", "features": "Newly renovated, on-site manager"},
    {"addr": "229 S Normandie Ave", "rent": 2150, "reno": "Classic", "dist": "0.7 mi", "features": "Wood-style flooring, on-site laundry"},
    {"addr": "466 N Westmoreland Ave", "rent": 2095, "reno": "Classic", "dist": "0.4 mi", "features": "Renovated, near Virgil/Melrose"},
    {"addr": "111 N Normandie Ave", "rent": 2200, "reno": "Classic", "dist": "0.6 mi", "features": "Recently renovated (within 6 yrs)"},
    {"addr": "955 Fedora St", "rent": 2350, "reno": "Classic/Premium", "dist": "0.8 mi", "features": "Modern renovated, Koreatown"},
]

RENT_COMPS_STUDIO = [
    {"addr": "247 S Alexandria Ave", "rent": 1395, "reno": "Classic", "dist": "0.5 mi", "features": "Marble tile, SS appliances, hardwood"},
    {"addr": "326 S Normandie Ave", "rent": 1445, "reno": "Classic", "dist": "0.8 mi", "features": "Granite counters, exposed brick"},
    {"addr": "520 S Mariposa Ave", "rent": 1425, "reno": "Classic", "dist": "0.9 mi", "features": "Renovated, appliances included"},
    {"addr": "739 S Normandie Ave", "rent": 1425, "reno": "Classic", "dist": "1.1 mi", "features": "Spacious renovated studio"},
    {"addr": "516 S St Andrews Pl", "rent": 1395, "reno": "Classic", "dist": "0.9 mi", "features": "Built-in shelving, charming kitchen"},
    {"addr": "132 Westmoreland Ave", "rent": 1425, "reno": "Classic", "dist": "0.5 mi", "features": "Updated kitchen + bath"},
]

# ============================================================
# OPERATING STATEMENT DATA
# ============================================================
TAXES_AT_LIST = LIST_PRICE * TAX_RATE
CUR_EGI = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
PF_EGI = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
CUR_MGMT = max(CUR_EGI * 0.04, 18000)
PF_MGMT = max(PF_EGI * 0.04, 18000)
CUR_TOTAL_EXP = TAXES_AT_LIST + NON_TAX_CUR_EXP
PF_TOTAL_EXP = TAXES_AT_LIST + NON_TAX_PF_EXP
CUR_NOI_AT_LIST = CUR_EGI - CUR_TOTAL_EXP
PF_NOI_AT_LIST = PF_EGI - PF_TOTAL_EXP

EXPENSE_ITEMS = [
    ("Real Estate Taxes", TAXES_AT_LIST, 2),
    ("Insurance", 6300, 3),
    ("Water / Sewer", 5500, 4),
    ("Trash", 2800, 5),
    ("Common Area Electric", 1500, 6),
    ("Repairs &amp; Maintenance", 9100, 7),
    ("Contract Services", 1500, 8),
    ("Administrative", 1000, 9),
    ("Marketing", 500, 10),
    ("Management Fee", 18000, 11),
    ("Reserves", 2450, 12),
    ("LAHD Registration", 303, 13),
    ("Other", 250, 14),
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def fc(n):
    if n is None: return "n/a"
    return f"${n:,.0f}"
def fp(n):
    if n is None: return "n/a"
    return f"{n:.2f}%"

def build_map_js(map_id, comps, comp_color, subject_lat, subject_lng):
    js = f"var {map_id} = L.map('{map_id}').setView([{subject_lat}, {subject_lng}], 14);\n"
    js += f"L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution: '&copy; OpenStreetMap'}}).addTo({map_id});\n"
    js += f"""L.marker([{subject_lat}, {subject_lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:#C5A258;color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">&#9733;</div>', iconSize: [32, 32], iconAnchor: [16, 16]}})}})\n.addTo({map_id}).bindPopup('<b>500 N Alexandria Ave</b><br>Subject Property<br>7 Units | 4,360 SF');\n"""
    for i, c in enumerate(comps):
        lat, lng = None, None
        for a, coords in ADDRESSES.items():
            if c["addr"].lower() in a.lower() and coords:
                lat, lng = coords
                break
        if lat is None: continue
        label = str(i + 1)
        popup = f"<b>#{label}: {c['addr']}</b><br>{c.get('units', '')} Units | {fc(c.get('price', 0))}"
        js += f"""L.marker([{lat}, {lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:{comp_color};color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #fff;box-shadow:0 2px 4px rgba(0,0,0,0.3);">{label}</div>', iconSize: [26, 26], iconAnchor: [13, 13]}})}})\n.addTo({map_id}).bindPopup('{popup}');\n"""
    return js

sale_map_js = build_map_js("saleMap", SALE_COMPS, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
active_map_js = build_map_js("activeMap", ACTIVE_COMPS, "#2E7D32", SUBJECT_LAT, SUBJECT_LNG)
rent_comps_for_map = [{"addr": c["addr"], "price": 0, "units": ""} for c in RENT_COMPS_2BR + RENT_COMPS_STUDIO]
rent_map_js = build_map_js("rentMap", rent_comps_for_map, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)

# ============================================================
# COMP NARRATIVES
# ============================================================
COMP_NARRATIVES = [
    """<p><strong>101 S Kenmore Ave (8 units, $1,595,000, 07/2025):</strong> The anchor comparable and highest-quality data point in the comp set. This 1925-vintage 8-unit building features all one-bedroom units under RSO with on-site laundry. At $199,375/unit with a 7.29% adjusted cap rate, it establishes the premium end of the market for well-maintained vintage RSO buildings in the 90004 zip code. The strong cap rate reflects reliable income documentation and stabilized operations. The subject at $182,143/unit represents an 8.6% discount to this benchmark, an appropriate adjustment for the smaller building size (7 vs 8 units), mixed unit types, and limited parking. Sold at 94.1% SP/LP, this comp confirms approximately 3&ndash;6% negotiation from list price in the current market.</p>""",
    """<p><strong>212 S Berendo St (8 units, $1,525,000, 08/2025):</strong> An 8-unit building composed entirely of 2-bedroom units, making it the closest unit-mix match to the subject&rsquo;s 2BR-heavy configuration. Built in 1923 &mdash; the same year as the subject&rsquo;s front building &mdash; this comp traded at $190,625/unit with a deeply compressed 4.15% cap rate. The low cap reflects 108% rent upside embedded in deeply below-market RSO leases, demonstrating that buyers willingly accept lower current yields when the embedded upside is substantial and clearly documented. Purchased by a 1031 exchange buyer, confirming the active exchange market at this price point. The subject offers a more balanced risk-return profile: higher current yield (5.48% cap) with a more moderate 18.5% rent upside. Sold at 90.8% SP/LP after significant negotiation.</p>""",
    """<p><strong>247 N New Hampshire Ave (12 units, $1,400,000, 08/2025):</strong> An off-market sale of 12 studios with unreliable financial data. At $116,667/unit, this represents the floor of the comp range and reflects the significant discount applied to studio-heavy buildings with limited income transparency. The off-market nature (100% SP/LP) suggests a relationship sale or principal-to-principal transaction. While the per-unit price is dramatically below the subject&rsquo;s $182,143, the comparison is of limited direct relevance due to the fundamentally different unit mix (100% studios vs. subject&rsquo;s 57% 2BR / 29% studio / 14% ADU) and the absence of verifiable income data. This comp serves primarily as a floor reference.</p>""",
    """<p><strong>143 N Commonwealth Ave (6 units, $1,425,000, 01/2026):</strong> A DISTRESSED sale through auction/trust with an SP/LP ratio of just 79.2%, indicating significant negotiation from the original ask. The 1951 vintage is newer than the subject (1923/1929), and the $237,500/unit price is the highest in the comp set &mdash; but the distressed circumstances and smaller unit count (6 units) make it an outlier. The absence of verifiable cap rate or financial data limits its analytical utility. This comp is used as a ceiling reference for distressed pricing, demonstrating that even under duress, Koreatown multifamily commands $237K+ per unit for post-war product. The subject&rsquo;s non-distressed, fully occupied positioning supports a more favorable marketing outcome.</p>""",
]

# ============================================================
# GENERATE DYNAMIC TABLE HTML
# ============================================================

# Pricing matrix
matrix_html = ""
for m in MATRIX:
    cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
    matrix_html += f'<tr{cls}><td class="num">{fc(m["price"])}</td><td class="num">{fp(m["cur_cap"])}</td><td class="num">{fp(m["pf_cap"])}</td><td class="num">{fp(m["coc_cur"])}</td><td class="num">${m["per_sf"]:.0f}</td><td class="num">{fc(m["per_unit"])}</td><td class="num">{m["pf_grm"]:.2f}x</td></tr>\n'

# Summary page expense rows (at list price, Current vs Pro Forma)
sum_taxes = AT_LIST['taxes']
sum_expense_items = [
    ("Real Estate Taxes", sum_taxes, sum_taxes),
    ("Insurance", 6300, 6300),
    ("Water / Sewer", 5500, 5500),
    ("Trash", 2800, 2800),
    ("Common Area Electric", 1500, 1500),
    ("Repairs &amp; Maintenance", 9100, 9100),
    ("Contract Services", 1500, 1500),
    ("Administrative", 1000, 1000),
    ("Marketing", 500, 500),
    ("Management Fee", 18000, 18000),
    ("Reserves", 2450, 2450),
    ("LAHD Registration", 303, 303),
    ("Other", 250, 250),
]
sum_expense_html = ""
for label, cur_val, pf_val in sum_expense_items:
    sum_expense_html += f'<tr><td>{label}</td><td class="num">${cur_val:,.0f}</td><td class="num">${pf_val:,.0f}</td></tr>\n'

# Unit summary for summary page (aggregated from rent roll)
br2_units = [(u, s, c, m) for u, t, s, c, m in RENT_ROLL if t == "2BR/1BA"]
studio_units = [(u, s, c, m) for u, t, s, c, m in RENT_ROLL if t == "Studio"]
adu_units = [(u, s, c, m) for u, t, s, c, m in RENT_ROLL if t == "ADU"]
br2_avg_cur = sum(c for _, _, c, _ in br2_units) / len(br2_units) if br2_units else 0
br2_avg_mkt = sum(m for _, _, _, m in br2_units) / len(br2_units) if br2_units else 0
studio_avg_cur = sum(c for _, _, c, _ in studio_units) / len(studio_units) if studio_units else 0
studio_avg_mkt = sum(m for _, _, _, m in studio_units) / len(studio_units) if studio_units else 0
adu_avg_cur = sum(c for _, _, c, _ in adu_units) / len(adu_units) if adu_units else 0
adu_avg_mkt = sum(m for _, _, _, m in adu_units) / len(adu_units) if adu_units else 0

# Rent roll
rent_roll_html = ""
total_sf = total_cur = total_mkt = 0
for unit, utype, sqft, cur, mkt in RENT_ROLL:
    rent_roll_html += f"<tr><td>{unit}</td><td>{utype}</td><td>{sqft:,}</td><td>${cur:,}</td><td>${cur/sqft:.2f}</td><td>${mkt:,}</td><td>${mkt/sqft:.2f}</td></tr>\n"
    total_sf += sqft; total_cur += cur; total_mkt += mkt
rent_roll_html += f'<tr style="font-weight:700;background:#1B3A5C;color:#fff;"><td>TOTAL</td><td>7 Units</td><td>{total_sf:,}</td><td>${total_cur:,}</td><td>${total_cur/total_sf:.2f}</td><td>${total_mkt:,}</td><td>${total_mkt/total_sf:.2f}</td></tr>'

# Sale comps table
sale_comps_html = ""
sale_comps_html += f'<tr class="highlight" style="font-weight:700;"><td>S</td><td>500 N Alexandria Ave</td><td>Los Angeles</td><td>{UNITS}</td><td>Proposed</td><td>{fc(LIST_PRICE)}</td><td>{fc(LIST_PRICE // UNITS)}</td><td>${LIST_PRICE / SF:.0f}</td><td>{AT_LIST["cur_cap"]:.2f}%</td><td>{AT_LIST["grm"]:.2f}</td><td>1923</td><td style="font-size:11px;">Subject Property</td></tr>\n'
for c in SALE_COMPS:
    cap_str = fp(c["cap"]) if c["cap"] else "n/a"
    grm_str = f'{c["grm"]:.2f}' if c["grm"] else "n/a"
    hl = ' class="highlight"' if "Anchor" in (c.get("notes") or "") else ""
    sale_comps_html += f'<tr{hl}><td>{c["num"]}</td><td>{c["addr"]}</td><td>{c["city"]}</td><td>{c["units"]}</td><td>{c["date"]}</td><td>{fc(c["price"])}</td><td>{fc(c["ppu"])}</td><td>${c["psf"]:.0f}</td><td>{cap_str}</td><td>{grm_str}</td><td>{c["yr"]}</td><td style="font-size:11px;">{c["notes"]}</td></tr>\n'
caps = [c["cap"] for c in SALE_COMPS if c["cap"]]
grms = [c["grm"] for c in SALE_COMPS if c["grm"]]
ppus = [c["ppu"] for c in SALE_COMPS]
psfs = [c["psf"] for c in SALE_COMPS]
prices = [c["price"] for c in SALE_COMPS]
units_list = [c["units"] for c in SALE_COMPS]
sale_comps_html += f'<tr style="font-weight:600;background:#f0f4f8;"><td></td><td>Averages</td><td></td><td>{sum(units_list)//len(units_list)}</td><td></td><td>{fc(sum(prices)//len(prices))}</td><td>{fc(sum(ppus)//len(ppus))}</td><td>${sum(psfs)/len(psfs):.0f}</td><td>{fp(sum(caps)/len(caps)) if caps else "n/a"}</td><td>{sum(grms)/len(grms):.2f}</td><td></td><td></td></tr>'
med_units = int(statistics.median(units_list))
med_price = int(statistics.median(prices))
med_ppu = int(statistics.median(ppus))
med_psf = statistics.median(psfs)
med_cap = statistics.median(caps) if caps else None
med_grm = statistics.median(grms)
sale_comps_html += f'<tr style="font-weight:600;background:#f0f4f8;"><td></td><td>Medians</td><td></td><td>{med_units}</td><td></td><td>{fc(med_price)}</td><td>{fc(med_ppu)}</td><td>${med_psf:.0f}</td><td>{fp(med_cap) if med_cap else "n/a"}</td><td>{med_grm:.2f}</td><td></td><td></td></tr>'

# Operating statement
income_lines = [
    ("Gross Scheduled Rent", GSR, False, None),
    ("Less: Vacancy (5%)", -(GSR * VACANCY_PCT), False, None),
    ("Other Income", OTHER_INCOME, False, 1),
]
expense_lines = [
    ("Real Estate Taxes", TAXES_AT_LIST, 2),
    ("Insurance", 6300, 3),
    ("Water / Sewer", 5500, 4),
    ("Trash", 2800, 5),
    ("Common Area Electric", 1500, 6),
    ("Repairs & Maintenance", 9100, 7),
    ("Contract Services", 1500, 8),
    ("Administrative", 1000, 9),
    ("Marketing", 500, 10),
    ("Management Fee", 18000, 11),
    ("Reserves", 2450, 12),
    ("LAHD Registration", 303, 13),
    ("Other", 250, 14),
]

op_income_html = ""
for label, val, _, note_num in income_lines:
    v_str = f"${val:,.0f}" if val >= 0 else f"(${abs(val):,.0f})"
    pu = f"${val/UNITS:,.0f}" if val >= 0 else f"(${abs(val)/UNITS:,.0f})"
    note_ref = f'<span class="note-ref">[{note_num}]</span>' if note_num else ""
    op_income_html += f"<tr><td>{label} {note_ref}</td><td class='num'>{v_str}</td><td class='num'>{pu}</td><td class='num'> - </td></tr>\n"
op_income_html += f'<tr class="summary"><td><strong>Effective Gross Income</strong></td><td class="num"><strong>${CUR_EGI:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/UNITS:,.0f}</strong></td><td class="num"><strong>100.0%</strong></td></tr>'

op_expense_html = ""
for label, val, note_num in expense_lines:
    pct = f"{val/CUR_EGI*100:.1f}%"
    note_ref = f'<span class="note-ref">[{note_num}]</span>' if note_num else ""
    op_expense_html += f"<tr><td>{label} {note_ref}</td><td class='num'>${val:,.0f}</td><td class='num'>${val/UNITS:,.0f}</td><td class='num'>{pct}</td></tr>\n"
op_expense_html += f'<tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${CUR_TOTAL_EXP:,.0f}</strong></td><td class="num"><strong>${CUR_TOTAL_EXP/UNITS:,.0f}</strong></td><td class="num"><strong>{CUR_TOTAL_EXP/CUR_EGI*100:.1f}%</strong></td></tr>'
op_expense_html += f'\n<tr class="summary"><td><strong>Net Operating Income</strong></td><td class="num"><strong>${CUR_NOI_AT_LIST:,.0f}</strong></td><td class="num"><strong>${CUR_NOI_AT_LIST/UNITS:,.0f}</strong></td><td class="num"><strong>{CUR_NOI_AT_LIST/CUR_EGI*100:.1f}%</strong></td></tr>'

print("Building HTML...")

# ============================================================
# ASSEMBLE FULL HTML
# ============================================================
html_parts = []

# HEAD + CSS
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BOV - 500 N Alexandria Ave, Los Angeles | LAAA Team</title>
<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;color:#333;line-height:1.6;background:#fff;}}
html{{scroll-padding-top:50px;}}
.cover{{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;color:#fff;overflow:hidden;}}
.cover-bg{{position:absolute;inset:0;background-size:cover;background-position:center;filter:brightness(0.45);z-index:0;}}
.cover-content{{position:relative;z-index:2;padding:60px 40px;max-width:860px;}}
.cover-logo{{width:320px;margin:0 auto 30px;display:block;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.3));}}
.cover-label{{font-size:13px;font-weight:500;letter-spacing:3px;text-transform:uppercase;color:#C5A258;margin-bottom:18px;}}
.cover-title{{font-size:46px;font-weight:700;letter-spacing:1px;margin-bottom:8px;text-shadow:0 2px 12px rgba(0,0,0,0.3);}}
.cover-subtitle{{font-size:20px;font-weight:300;color:rgba(255,255,255,0.8);margin-bottom:28px;}}
.cover-price{{font-size:48px;font-weight:700;color:#C5A258;margin-bottom:28px;text-shadow:0 2px 8px rgba(0,0,0,0.2);}}
.cover-stats{{display:flex;gap:32px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;}}
.cover-stat{{text-align:center;}}.cover-stat-value{{display:block;font-size:26px;font-weight:600;color:#fff;}}.cover-stat-label{{display:block;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-top:4px;}}
.client-greeting{{font-size:16px;font-weight:400;letter-spacing:2px;text-transform:uppercase;color:#C5A258;margin-top:16px;}}
.cover-headshots{{display:flex;justify-content:center;gap:40px;margin-top:24px;margin-bottom:16px;}}
.cover-headshot-wrap{{text-align:center;}}
.cover-headshot{{width:80px;height:80px;border-radius:50%;border:3px solid #C5A258;object-fit:cover;box-shadow:0 4px 16px rgba(0,0,0,0.4);}}
.cover-headshot-name{{font-size:12px;font-weight:600;margin-top:6px;color:#fff;}}
.cover-headshot-title{{font-size:10px;color:#C5A258;}}
.gold-line{{height:3px;background:#C5A258;margin:20px 0;}}
.pdf-float-btn{{position:fixed;bottom:24px;right:24px;z-index:9999;padding:14px 28px;background:#C5A258;color:#1B3A5C;font-size:14px;font-weight:700;text-decoration:none;border-radius:8px;letter-spacing:0.5px;box-shadow:0 4px 16px rgba(0,0,0,0.35);transition:background 0.2s,transform 0.2s;display:flex;align-items:center;gap:8px;}}.pdf-float-btn:hover{{background:#fff;transform:translateY(-2px);}}.pdf-float-btn svg{{width:18px;height:18px;fill:currentColor;}}
.toc-nav{{background:#1B3A5C;padding:0 12px;display:flex;flex-wrap:nowrap;gap:0;justify-content:center;align-items:stretch;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.15);overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;-ms-overflow-style:none;}}
.toc-nav::-webkit-scrollbar{{display:none;}}
.toc-nav a{{color:rgba(255,255,255,0.85);text-decoration:none;font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;padding:12px 8px;border-bottom:2px solid transparent;transition:all 0.2s ease;white-space:nowrap;display:flex;align-items:center;}}
.toc-nav a:hover{{color:#fff;background:rgba(197,162,88,0.12);border-bottom-color:rgba(197,162,88,0.4);}}.toc-nav a.toc-active{{color:#C5A258;font-weight:600;border-bottom-color:#C5A258;}}
.section{{padding:50px 40px;max-width:1100px;margin:0 auto;}}.section-alt{{background:#f8f9fa;}}
.section-title{{font-size:26px;font-weight:700;color:#1B3A5C;margin-bottom:6px;}}.section-subtitle{{font-size:13px;color:#C5A258;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;font-weight:500;}}
.section-divider{{width:60px;height:3px;background:#C5A258;margin-bottom:30px;}}.sub-heading{{font-size:18px;font-weight:600;color:#1B3A5C;margin:30px 0 16px;}}
.metrics-grid,.metrics-grid-4{{display:grid;gap:16px;margin-bottom:30px;}}.metrics-grid{{grid-template-columns:repeat(3,1fr);}}.metrics-grid-4{{grid-template-columns:repeat(4,1fr);}}
.metric-card{{background:#1B3A5C;border-radius:12px;padding:24px;text-align:center;color:#fff;}}
.metric-value{{display:block;font-size:28px;font-weight:700;color:#fff;margin-bottom:4px;}}.metric-label{{display:block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.6);margin-top:6px;}}.metric-sub{{display:block;font-size:12px;color:#C5A258;margin-top:4px;}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px;}}th{{background:#1B3A5C;color:#fff;padding:10px 12px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;}}td{{padding:8px 12px;border-bottom:1px solid #eee;}}tr:nth-child(even){{background:#f5f5f5;}}tr.highlight{{background:#FFF8E7 !important;border-left:3px solid #C5A258;}}
.table-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-bottom:24px;}}.table-scroll table{{min-width:700px;margin-bottom:0;}}
.info-table{{width:100%;}}.info-table td{{padding:8px 12px;border-bottom:1px solid #eee;font-size:13px;}}.info-table td:first-child{{font-weight:600;color:#1B3A5C;width:40%;}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:30px;}}
.photo-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:30px;border-radius:8px;overflow:hidden;}}.photo-grid img{{width:100%;height:180px;object-fit:cover;border-radius:4px;}}
.condition-note{{background:#FFF8E7;border-left:4px solid #C5A258;padding:16px 20px;margin:24px 0;border-radius:0 4px 4px 0;font-size:13px;line-height:1.6;}}
.buyer-profile{{background:#f0f4f8;border-left:4px solid #1B3A5C;padding:20px 24px;margin:24px 0;border-radius:0 4px 4px 0;}}.buyer-profile-label{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#1B3A5C;margin-bottom:12px;}}.buyer-profile ul{{list-style:none;padding:0;margin:0;}}.buyer-profile li{{padding:8px 0;border-bottom:1px solid #dce3eb;font-size:14px;line-height:1.6;color:#333;}}.buyer-profile li:last-child{{border-bottom:none;}}.buyer-profile li strong{{color:#1B3A5C;}}.buyer-profile .bp-closing{{font-size:13px;color:#555;margin-top:12px;font-style:italic;}}
.leaflet-map{{height:400px;border-radius:4px;border:1px solid #ddd;margin-bottom:30px;z-index:1;}}.map-fallback{{display:none;font-size:12px;color:#666;font-style:italic;margin-bottom:30px;}}
.embed-map-wrap{{position:relative;width:100%;margin-bottom:20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.embed-map-wrap iframe{{display:block;width:100%;height:420px;border:0;}}.embed-map-caption{{font-size:12px;color:#888;text-align:center;margin-top:8px;font-style:italic;}}.embed-map-fallback{{display:none;font-size:12px;color:#666;font-style:italic;margin-bottom:30px;}}
.adu-img-wrap{{margin-bottom:20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.adu-img-wrap img{{width:100%;display:block;}}
.footer{{background:#1B3A5C;color:#fff;padding:50px 40px;text-align:center;}}.footer-logo{{width:180px;margin-bottom:30px;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.3));}}.footer-team{{display:flex;justify-content:center;gap:40px;margin-bottom:30px;flex-wrap:wrap;}}.footer-person{{text-align:center;flex:1;min-width:280px;}}.footer-headshot{{width:70px;height:70px;border-radius:50%;border:2px solid #C5A258;margin-bottom:10px;object-fit:cover;}}.footer-name{{font-size:16px;font-weight:600;}}.footer-title{{font-size:12px;color:#C5A258;margin-bottom:8px;}}.footer-contact{{font-size:12px;color:rgba(255,255,255,0.7);line-height:1.8;}}.footer-contact a{{color:rgba(255,255,255,0.7);text-decoration:none;}}.footer-office{{font-size:12px;color:rgba(255,255,255,0.5);margin-top:20px;}}.footer-disclaimer{{font-size:10px;color:rgba(255,255,255,0.35);margin-top:20px;max-width:800px;margin-left:auto;margin-right:auto;line-height:1.6;}}
p{{margin-bottom:16px;font-size:14px;line-height:1.7;}}
.highlight-box{{background:#f0f4f8;border:1px solid #dce3eb;border-radius:8px;padding:20px 24px;margin:24px 0;}}
.highlight-box h4{{color:#1B3A5C;font-size:14px;margin-bottom:10px;}}
.highlight-box ul{{margin:0;padding-left:20px;}}.highlight-box li{{font-size:13px;margin-bottom:6px;line-height:1.5;}}
td.num,th.num{{text-align:right;}}
.broker-insight{{background:#f8f4eb;border-left:4px solid #C5A258;padding:16px 20px;margin:24px 0;border-radius:0 4px 4px 0;font-size:13px;line-height:1.7;color:#444;}}
.broker-insight-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-bottom:8px;display:block;}}
.costar-badge{{text-align:center;background:#FFF8E7;border:2px solid #C5A258;border-radius:8px;padding:20px 24px;margin:30px auto 24px;max-width:600px;}}
.costar-badge-title{{font-size:22px;font-weight:700;color:#1B3A5C;line-height:1.2;}}
.costar-badge-sub{{font-size:12px;color:#C5A258;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-top:6px;}}
.bio-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:24px 0;}}
.bio-card{{display:flex;gap:16px;align-items:flex-start;}}
.bio-headshot{{width:100px;height:100px;border-radius:50%;border:3px solid #C5A258;object-fit:cover;flex-shrink:0;}}
.bio-name{{font-size:16px;font-weight:700;color:#1B3A5C;margin-bottom:2px;}}
.bio-title{{font-size:11px;color:#C5A258;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}}
.bio-text{{font-size:13px;line-height:1.6;color:#444;}}
.press-strip{{display:flex;justify-content:center;align-items:center;gap:28px;flex-wrap:wrap;margin:24px 0;padding:16px 20px;background:#f0f4f8;border-radius:6px;}}
.press-strip-label{{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#888;font-weight:600;}}
.press-logo{{font-size:13px;font-weight:700;color:#1B3A5C;letter-spacing:0.5px;}}
.condition-note-label{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;margin-bottom:8px;}}.achievements-list{{font-size:13px;line-height:1.8;}}
.img-float-right{{float:right;width:48%;margin:0 0 16px 20px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.img-float-right img{{width:100%;display:block;}}
.os-two-col{{display:grid;grid-template-columns:55% 45%;gap:24px;align-items:stretch;margin-bottom:24px;}}.os-right{{font-size:10.5px;line-height:1.45;color:#555;background:#f8f9fb;border:1px solid #e0e4ea;border-radius:6px;padding:16px 20px;}}.os-right h3{{font-size:13px;margin:0 0 8px;}}.os-right p{{margin-bottom:4px;}}.note-ref{{font-size:9px;color:#C5A258;font-weight:700;vertical-align:super;}}
.loc-grid{{display:grid;grid-template-columns:58% 42%;gap:28px;align-items:start;}}.loc-left{{max-height:380px;overflow:hidden;}}.loc-left p{{font-size:13.5px;line-height:1.7;margin-bottom:14px;}}.loc-right{{display:block;max-height:380px;overflow:hidden;}}.loc-wide-map{{width:100%;height:200px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-top:20px;}}.loc-wide-map img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}
.tr-tagline{{font-size:24px;font-weight:600;color:#1B3A5C;text-align:center;padding:16px 24px;margin-bottom:20px;border-left:4px solid #C5A258;background:#FFF8E7;border-radius:0 4px 4px 0;font-style:italic;}}.tr-map-print{{display:none;}}.tr-service-quote{{margin:24px 0;}}.tr-service-quote h3{{font-size:18px;font-weight:700;color:#1B3A5C;margin-bottom:8px;line-height:1.3;}}.tr-service-quote p{{font-size:14px;line-height:1.7;}}.tr-mission{{background:#f0f4f8;border-left:4px solid #1B3A5C;padding:20px 24px;margin-bottom:24px;border-radius:0 4px 4px 0;}}.tr-mission h3{{font-size:18px;font-weight:700;color:#1B3A5C;margin-bottom:12px;}}.tr-mission p{{font-size:13px;line-height:1.7;margin-bottom:10px;}}
.inv-split{{display:grid;grid-template-columns:50% 50%;gap:24px;}}.inv-left .metrics-grid-4{{grid-template-columns:repeat(2,1fr);}}.inv-text p{{font-size:13px;line-height:1.6;margin-bottom:10px;}}.inv-logo{{width:200px;margin-top:16px;opacity:0.7;}}.inv-right{{display:flex;flex-direction:column;gap:16px;padding-top:70px;}}.inv-photo{{height:280px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);}}.inv-photo img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}.inv-highlights{{background:#f0f4f8;border:1px solid #dce3eb;border-radius:8px;padding:16px 20px;flex:1;}}.inv-highlights h4{{color:#1B3A5C;font-size:13px;margin-bottom:8px;}}.inv-highlights ul{{margin:0;padding-left:18px;}}.inv-highlights li{{font-size:12px;line-height:1.5;margin-bottom:5px;}}
.buyer-split{{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start;}}.buyer-objections .obj-item{{margin-bottom:14px;}}.buyer-objections .obj-q{{font-weight:700;color:#1B3A5C;margin-bottom:4px;font-size:14px;}}.buyer-objections .obj-a{{font-size:13px;color:#444;line-height:1.6;}}.buyer-photo{{width:100%;height:220px;border-radius:8px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-top:24px;}}.buyer-photo img{{width:100%;height:100%;object-fit:cover;object-position:center;display:block;}}
.prop-tables-bottom{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px;}}.prop-tables-bottom .sub-heading{{font-size:15px;margin:0 0 10px;}}.prop-grid-4{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:20px;}}
.summary-page{{margin-top:24px;border:1px solid #dce3eb;border-radius:8px;padding:20px;background:#fff;}}.summary-banner{{text-align:center;background:#1B3A5C;color:#fff;padding:10px 16px;font-size:14px;font-weight:700;letter-spacing:2px;text-transform:uppercase;border-radius:4px;margin-bottom:16px;}}.summary-two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;}}.summary-table{{width:100%;border-collapse:collapse;margin-bottom:12px;font-size:12px;border:1px solid #dce3eb;}}.summary-table th,.summary-table td{{padding:4px 8px;border-bottom:1px solid #e8ecf0;text-align:left;}}.summary-table td.num{{text-align:right;}}.summary-table th.num{{text-align:right;}}.summary-header{{background:#1B3A5C;color:#fff;padding:5px 8px !important;font-size:10px !important;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;border-bottom:none !important;}}.summary-table tr.summary td{{border-top:2px solid #1B3A5C;font-weight:700;background:#f0f4f8;}}.summary-table tr:nth-child(even){{background:#fafbfc;}}.summary-trade-range{{text-align:center;margin:24px auto;padding:16px 24px;border:2px solid #1B3A5C;border-radius:6px;max-width:480px;}}.summary-trade-label{{font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#555;font-weight:600;margin-bottom:6px;}}.summary-trade-prices{{font-size:26px;font-weight:700;color:#1B3A5C;}}
.page-break-marker{{height:4px;background:repeating-linear-gradient(90deg,#ddd 0,#ddd 8px,transparent 8px,transparent 16px);margin:0;}}
.team-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0;}}.team-card{{text-align:center;padding:8px;}}.team-headshot{{width:60px;height:60px;border-radius:50%;border:2px solid #C5A258;object-fit:cover;margin:0 auto 4px;display:block;}}.team-card-name{{font-size:13px;font-weight:700;color:#1B3A5C;}}.team-card-title{{font-size:10px;color:#C5A258;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;}}
.mkt-quote{{background:#FFF8E7;border-left:4px solid #C5A258;padding:16px 24px;margin:20px 0;border-radius:0 4px 4px 0;font-size:15px;font-style:italic;line-height:1.6;color:#1B3A5C;}}.mkt-channels{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;}}.mkt-channel{{background:#f0f4f8;border-radius:8px;padding:16px 20px;}}.mkt-channel h4{{color:#1B3A5C;font-size:14px;margin-bottom:8px;}}.mkt-channel ul{{margin:0;padding-left:18px;}}.mkt-channel li{{font-size:13px;line-height:1.5;margin-bottom:4px;}}
.perf-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;}}.perf-card{{background:#f0f4f8;border-radius:8px;padding:16px 20px;}}.perf-card h4{{color:#1B3A5C;font-size:14px;margin-bottom:8px;}}.perf-card ul{{margin:0;padding-left:18px;}}.perf-card li{{font-size:13px;line-height:1.5;margin-bottom:4px;}}.platform-strip{{display:flex;justify-content:center;align-items:center;gap:20px;flex-wrap:wrap;margin-top:24px;padding:14px 20px;background:#1B3A5C;border-radius:6px;}}.platform-strip-label{{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#C5A258;font-weight:600;}}.platform-name{{font-size:12px;font-weight:600;color:#fff;letter-spacing:0.5px;}}
@media(max-width:768px){{.cover-content{{padding:30px 20px;}}.cover-title{{font-size:32px;}}.cover-price{{font-size:36px;}}.cover-logo{{width:220px;}}.cover-headshots{{gap:24px;}}.cover-headshot{{width:60px;height:60px;}}.pdf-float-btn{{padding:10px 18px;font-size:12px;bottom:16px;right:16px;}}.section{{padding:30px 16px;}}.photo-grid{{grid-template-columns:1fr;}}.two-col{{grid-template-columns:1fr;}}.metrics-grid,.metrics-grid-4{{grid-template-columns:repeat(2,1fr);gap:12px;}}.metric-card{{padding:14px 10px;}}.metric-value{{font-size:22px;}}.footer-team{{flex-direction:column;align-items:center;}}.leaflet-map{{height:300px;}}.embed-map-wrap iframe{{height:320px;}}.toc-nav{{padding:0 6px;}}.toc-nav a{{font-size:10px;padding:10px 6px;letter-spacing:0.2px;}}.table-scroll table{{min-width:560px;}}.bio-grid{{grid-template-columns:1fr;gap:16px;}}.bio-headshot{{width:60px;height:60px;}}.press-strip{{gap:16px;}}.press-logo{{font-size:11px;}}.costar-badge-title{{font-size:18px;}}.img-float-right{{float:none;width:100%;margin:0 0 16px 0;}}.os-two-col{{grid-template-columns:1fr;}}.loc-grid{{grid-template-columns:1fr;}}.loc-wide-map{{height:180px;margin-top:16px;}}.inv-split{{grid-template-columns:1fr;}}.inv-photo{{height:240px;}}.buyer-split{{grid-template-columns:1fr;}}.mkt-channels,.perf-grid{{grid-template-columns:1fr;}}.summary-two-col{{grid-template-columns:1fr;}}.prop-grid-4{{grid-template-columns:1fr;}}}}
@media(max-width:420px){{.cover-content{{padding:24px 16px;}}.cover-logo{{width:180px;}}.cover-title{{font-size:24px;}}.cover-subtitle{{font-size:15px;}}.cover-price{{font-size:28px;}}.cover-stats{{gap:10px;}}.cover-stat-value{{font-size:18px;}}.cover-stat-label{{font-size:9px;}}.cover-label{{font-size:11px;}}.cover-headshots{{gap:16px;margin-top:16px;}}.cover-headshot{{width:50px;height:50px;}}.pdf-float-btn{{padding:10px 14px;font-size:0;bottom:14px;right:14px;}}.pdf-float-btn svg{{width:22px;height:22px;}}.metrics-grid,.metrics-grid-4{{grid-template-columns:1fr;}}.metric-card{{padding:12px 10px;}}.metric-value{{font-size:20px;}}.section{{padding:24px 12px;}}.section-title{{font-size:20px;}}.footer{{padding:24px 12px;}}.footer-team{{gap:16px;}}.toc-nav{{padding:0 4px;}}.toc-nav a{{font-size:8px;padding:10px 4px;letter-spacing:0;}}.leaflet-map{{height:240px;}}}}
@media print{{
@page{{size:letter landscape;margin:0.4in 0.5in;}}
.pdf-float-btn,.toc-nav,.leaflet-map,.embed-map-wrap,.embed-map-caption,.embed-map-fallback,.page-break-marker{{display:none !important;}}
.map-fallback{{display:block !important;}}
body{{font-size:11px;line-height:1.5;color:#222;}}
p{{font-size:11px;line-height:1.5;margin-bottom:8px;orphans:3;widows:3;}}
.section{{padding:20px 20px;max-width:100%;}}
.section-title{{font-size:18px;margin-bottom:2px;}}
.section-subtitle{{font-size:10px;letter-spacing:1px;margin-bottom:6px;}}
.section-divider{{margin-bottom:10px;height:2px;}}
.sub-heading{{font-size:13px;margin:10px 0 6px;}}
h2,h3,.section-title,.sub-heading{{page-break-after:avoid;}}
table{{page-break-inside:auto;font-size:10px;margin-bottom:8px;}}
thead{{display:table-header-group;}}
tr{{page-break-inside:avoid;}}
th{{padding:4px 8px;font-size:8px;}}
td{{padding:4px 8px;font-size:10px;}}
.table-scroll{{overflow:visible;}}.table-scroll table{{min-width:0 !important;width:100%;}}
.info-table td{{padding:4px 8px;font-size:10px;}}
.two-col{{gap:14px;margin-bottom:10px;}}
.narrative{{column-count:2;column-gap:20px;}}
.narrative p{{font-size:10.5px;line-height:1.4;margin-bottom:6px;}}
.cover{{min-height:7.5in;padding:0;page-break-after:always;display:flex;align-items:center;justify-content:center;}}
.cover-bg{{filter:brightness(0.35);-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.cover-headshots{{display:flex;gap:20px;}}.cover-headshot{{width:55px;height:55px;}}.cover-headshot-name{{font-size:10px;}}.cover-headshot-title{{font-size:8px;}}
.metrics-grid,.metrics-grid-4{{gap:8px;margin-bottom:10px;page-break-inside:avoid;}}
.metrics-grid{{grid-template-columns:repeat(3,1fr);}}
.metrics-grid-4{{grid-template-columns:repeat(4,1fr);}}
.metric-card{{padding:8px 6px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.metric-value{{font-size:18px;}}
.metric-label{{font-size:8px;margin-top:2px;}}
.metric-sub{{font-size:9px;}}
.tr-page2{{page-break-before:always;}}
#marketing{{page-break-before:always;}}
#investment{{page-break-before:always;page-break-after:always;}}
#prop-details{{page-break-before:always;}}#buyer-profile{{page-break-before:always;}}
#location{{page-break-before:always;}}
#sale-comps{{page-break-before:always;}}
#financials{{page-break-before:always;}}
.price-reveal{{page-break-before:always;}}
.footer{{page-break-before:always;}}
.tr-tagline{{font-size:15px;padding:8px 14px;margin-bottom:8px;}}
.tr-map-print{{display:block;width:100%;height:240px;border-radius:4px;overflow:hidden;margin-bottom:8px;}}.tr-map-print img{{width:100%;height:100%;object-fit:cover;object-position:center;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.tr-service-quote{{margin:10px 0;}}.tr-service-quote h3{{font-size:13px;margin-bottom:4px;}}.tr-service-quote p{{font-size:11px;line-height:1.45;}}
.tr-mission{{padding:10px 14px;margin-bottom:12px;}}.tr-mission h3{{font-size:13px;margin-bottom:5px;}}.tr-mission p{{font-size:11px;line-height:1.4;margin-bottom:4px;}}
.bio-grid{{gap:14px;margin:10px 0;}}.bio-headshot{{width:75px;height:75px;}}.bio-name{{font-size:13px;}}.bio-title{{font-size:9px;}}.bio-text{{font-size:10px;line-height:1.4;}}
.costar-badge{{padding:8px 14px;margin:6px auto;}}.costar-badge-title{{font-size:15px;}}.costar-badge-sub{{font-size:9px;}}
.condition-note{{padding:8px 12px;margin:8px 0;font-size:10px;line-height:1.45;}}.achievements-list{{font-size:10px;line-height:1.45;}}
.press-strip{{padding:8px 14px;margin:8px 0;gap:14px;}}.press-strip-label{{font-size:8px;}}.press-logo{{font-size:10px;}}
.team-grid{{gap:8px;margin:8px 0;}}.team-card{{padding:4px;}}.team-headshot{{width:45px;height:45px;}}.team-card-name{{font-size:10px;}}.team-card-title{{font-size:8px;}}
.mkt-quote{{padding:8px 14px;margin:8px 0;font-size:12px;line-height:1.5;}}
.mkt-channels{{gap:10px;margin-top:10px;}}.mkt-channel{{padding:10px 14px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.mkt-channel h4{{font-size:12px;margin-bottom:4px;}}.mkt-channel ul{{margin:0;padding-left:16px;}}.mkt-channel li{{font-size:10px;line-height:1.4;margin-bottom:2px;}}
.perf-grid{{gap:10px;margin-top:10px;}}.perf-card{{padding:10px 14px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.perf-card h4{{font-size:12px;margin-bottom:4px;}}.perf-card ul{{margin:0;padding-left:16px;}}.perf-card li{{font-size:10px;line-height:1.4;margin-bottom:2px;}}
.platform-strip{{padding:6px 12px;margin-top:10px;gap:10px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.platform-strip-label{{font-size:8px;}}.platform-name{{font-size:9px;}}
.inv-split{{grid-template-columns:50% 50%;gap:14px;}}.inv-left .metrics-grid-4{{gap:6px;margin-bottom:6px;}}
.inv-text p{{font-size:10px;line-height:1.4;margin-bottom:4px;}}.inv-logo{{width:140px;margin-top:6px;}}
.inv-right{{padding-top:30px;}}.inv-photo{{height:170px;}}.inv-photo img{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.inv-highlights{{padding:8px 12px;}}.inv-highlights h4{{font-size:10px;margin-bottom:3px;}}.inv-highlights li{{font-size:8.5px;line-height:1.25;margin-bottom:1px;}}
.loc-grid{{display:grid;grid-template-columns:58% 42%;gap:14px;page-break-inside:avoid;}}.loc-left{{max-height:340px;overflow:hidden;}}.loc-left p{{font-size:10.5px;line-height:1.4;margin-bottom:5px;}}.loc-right{{max-height:340px;overflow:hidden;}}
.loc-wide-map{{height:220px;margin-top:8px;}}.loc-wide-map img{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.loc-right .info-table td{{padding:3px 8px;font-size:10px;}}.loc-right .info-table{{margin-bottom:0;}}
.prop-tables-bottom{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px;}}.prop-tables-bottom table{{font-size:9px;margin-bottom:4px;}}.prop-tables-bottom th{{font-size:7.5px;padding:3px 6px;}}.prop-tables-bottom td{{padding:3px 6px;font-size:9px;}}.prop-tables-bottom .sub-heading{{font-size:11px;margin:0 0 4px;}}.prop-grid-4{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:10px;page-break-inside:avoid;}}.prop-grid-4 table{{font-size:9px;margin-bottom:0;}}.prop-grid-4 th{{font-size:7.5px;padding:3px 6px;}}.prop-grid-4 td{{padding:3px 6px;font-size:9px;}}.prop-grid-4 .info-table td{{padding:3px 6px;font-size:9px;}}
.buyer-split{{grid-template-columns:1fr 1fr;gap:14px;page-break-inside:avoid;}}
.buyer-profile{{padding:8px 12px;margin:6px 0;}}.buyer-profile-label{{font-size:10px;margin-bottom:5px;}}.buyer-profile li{{padding:4px 0;font-size:10.5px;line-height:1.4;}}.bp-closing{{font-size:10px;}}
.buyer-objections .obj-item{{margin-bottom:8px;}}.buyer-objections .obj-q{{font-size:11px;margin-bottom:2px;}}.buyer-objections .obj-a{{font-size:10px;line-height:1.4;}}
.buyer-photo{{height:180px;margin-top:8px;border-radius:4px;overflow:hidden;}}.buyer-photo img{{width:100%;height:100%;object-fit:cover;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.summary-page{{margin-top:8px;page-break-before:always;border:none;padding:0;background:transparent;}}.summary-banner{{text-align:center;background:#1B3A5C;color:#fff;padding:6px 10px;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;border-radius:2px;margin-bottom:8px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.summary-two-col{{display:grid;grid-template-columns:1fr 1fr;gap:8px;align-items:start;}}
.summary-table{{width:100%;border-collapse:collapse;margin-bottom:6px;font-size:8px;border:1px solid #ccc;}}.summary-table th,.summary-table td{{padding:2px 5px;border-bottom:1px solid #ddd;text-align:left;}}.summary-table td.num{{text-align:right;}}.summary-table th.num{{text-align:right;}}.summary-table th{{font-size:6.5px;text-transform:uppercase;letter-spacing:0.5px;}}
.summary-header{{background:#1B3A5C;color:#fff;padding:3px 5px !important;font-size:7px !important;font-weight:700;letter-spacing:1px;border-bottom:none !important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.summary-table tr.summary td{{border-top:1.5px solid #1B3A5C;font-weight:700;background:#f0f4f8;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.summary-table tr:nth-child(even){{background:#fafbfc;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.summary-trade-range{{text-align:center;margin:8px auto;padding:8px 14px;border:2px solid #1B3A5C;border-radius:3px;max-width:350px;page-break-inside:avoid;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.summary-trade-label{{font-size:7px;letter-spacing:1.5px;color:#333;font-weight:600;margin-bottom:3px;}}.summary-trade-prices{{font-size:14px;font-weight:700;color:#1B3A5C;}}
.highlight-box{{padding:8px 12px;margin:8px 0;}}.highlight-box h4{{font-size:11px;margin-bottom:4px;}}.highlight-box li{{font-size:10px;margin-bottom:2px;line-height:1.4;}}
.photo-grid{{gap:6px;margin-bottom:8px;}}.photo-grid img{{height:140px;}}
.adu-img-wrap{{margin-bottom:8px;}}.adu-img-wrap img{{max-height:200px;width:auto;margin:0 auto;display:block;}}
.img-float-right{{float:right;width:40%;margin:0 0 8px 12px;}}.img-float-right img{{max-height:180px;width:auto;}}
.os-two-col{{page-break-before:always;page-break-inside:avoid;grid-template-columns:55% 45%;gap:14px;align-items:stretch;}}.os-right{{font-size:9px;line-height:1.3;padding:8px 12px;background:#f8f9fb;border:1px solid #ddd;border-radius:4px;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}.os-right p{{margin-bottom:2px;}}.os-right h3{{font-size:10px;margin:0 0 4px;}}.note-ref{{font-size:7px;color:#C5A258;font-weight:700;vertical-align:super;}}
.price-reveal .condition-note{{padding:6px 10px;margin:6px 0;font-size:10px;line-height:1.35;}}
.footer{{padding:20px 30px;}}.footer-logo{{width:120px;margin-bottom:10px;}}.footer-headshot{{width:50px;height:50px;}}.footer-name{{font-size:13px;}}.footer-title{{font-size:10px;}}.footer-contact{{font-size:10px;line-height:1.5;}}.footer-disclaimer{{font-size:8px;}}
}}
</style>
</head>
<body>
""")

# ==================== COVER ====================
html_parts.append(f"""
<div class="cover">
<div class="cover-bg" style="background-image:url('{IMG['hero']}');"></div>
<div class="cover-content">
<img src="{IMG['logo']}" class="cover-logo" alt="LAAA Team">
<div class="cover-label">Confidential Broker Opinion of Value</div>
<div class="cover-title">500 N Alexandria Avenue</div>
<div class="cover-address" style="font-size:20px;font-weight:300;margin-bottom:28px;color:rgba(255,255,255,0.8);">Los Angeles, California 90004</div>
<div class="gold-line" style="width:80px;margin:0 auto 24px;"></div>
<div class="cover-stats">
<div class="cover-stat"><span class="cover-stat-value">7</span><span class="cover-stat-label">Units</span></div>
<div class="cover-stat"><span class="cover-stat-value">4,360</span><span class="cover-stat-label">Square Feet</span></div>
<div class="cover-stat"><span class="cover-stat-value">1923/1929</span><span class="cover-stat-label">Year Built</span></div>
<div class="cover-stat"><span class="cover-stat-value">0.10 Ac</span><span class="cover-stat-label">Acres</span></div>
</div>
<p class="client-greeting" id="client-greeting"></p>
<div class="cover-headshots">
<div class="cover-headshot-wrap">
<img class="cover-headshot" src="{IMG['glen']}" alt="Glen Scher">
<div class="cover-headshot-name">Glen Scher</div>
<div class="cover-headshot-title">SMDI</div>
</div>
<div class="cover-headshot-wrap">
<img class="cover-headshot" src="{IMG['filip']}" alt="Filip Niculete">
<div class="cover-headshot-name">Filip Niculete</div>
<div class="cover-headshot-title">SMDI</div>
</div>
</div>
<p style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px;">February 2026</p>
</div>
</div>
""")

# ==================== TOC NAV ====================
html_parts.append(f"""
<nav class="toc-nav" id="toc-nav">
<a href="#track-record">Track Record</a>
<a href="#marketing">Marketing</a>
<a href="#investment">Investment</a>
<a href="#location">Location</a>
<a href="#prop-details">Property</a>
<a href="#txn-history">History</a>
<a href="#buyer-profile">Buyers</a>
<a href="#sale-comps">Sale Comps</a>
<a href="#on-market">On-Market</a>
<a href="#rent-comps">Rent Comps</a>
<a href="#financials">Financials</a>
<a href="#contact">Contact</a>
</nav>
<a href="{PDF_LINK}" class="pdf-float-btn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zm-1 13l-4-4h3V9h2v4h3l-4 4z"/></svg>Download PDF</a>
""")

# ==================== TRACK RECORD — Page 1 ====================
html_parts.append(f"""
<div class="section section-alt" id="track-record">
<div class="section-title">Team Track Record</div>
<div class="section-subtitle">LA Apartment Advisors at Marcus &amp; Millichap</div>
<div class="section-divider"></div>

<div class="tr-tagline"><span style="display:block;font-size:1.2em;font-weight:700;margin-bottom:4px;">LAAA Team of Marcus &amp; Millichap</span>Expertise, Execution, Excellence.</div>

<div class="metrics-grid metrics-grid-4">
<div class="metric-card"><span class="metric-value">501</span><span class="metric-label">Closed Transactions</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">$1.6B</span><span class="metric-label">Total Sales Volume</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">5,000+</span><span class="metric-label">Units Sold</span><span class="metric-sub">All-Time</span></div>
<div class="metric-card"><span class="metric-value">34</span><span class="metric-label">Median Days on Market</span><span class="metric-sub">Apartments</span></div>
</div>

<div class="embed-map-wrap"><iframe src="https://www.google.com/maps/d/u/0/embed?mid=1ewCjzE3QX9p6m2MqK-md8b6fZitfIzU&ehbc=2E312F" allowfullscreen loading="lazy"></iframe></div>
<div class="embed-map-caption">All-Time Closings Map  -  LA Apartment Advisors</div>
<div class="embed-map-fallback">View our interactive closings map at <strong>www.LAAA.com</strong></div>
<div class="tr-map-print"><img src="{IMG['closings_map']}" alt="LAAA Team All-Time Closings Map - LA County"></div>

<div class="tr-service-quote">
<h3>We Didn&rsquo;t Invent Great Service, We Just Work Relentlessly to Provide It</h3>
<p>At LAAA Team, we are dedicated to delivering expert multifamily brokerage services in Los Angeles, helping investors navigate the market with precision, strategy, and results-driven execution. With over 500 closed transactions and $1.6B in total sales volume, our team thrives on providing data-driven insights, strategic deal structuring, and hands-on client service to maximize value for our clients.</p>
<p>Founded by Glen Scher and Filip Niculete, LAAA Team operates with a commitment to transparency, efficiency, and unmatched market expertise. We take a relationship-first approach, guiding property owners, investors, and developers through every stage of acquisition, disposition, and asset repositioning.</p>
<p>Our mission is simple: To be the most trusted and results-oriented multifamily advisors in Los Angeles, leveraging deep market knowledge, innovative technology, and a proactive deal-making strategy to drive long-term success for our clients.</p>
</div>

<div class="tr-page2">

<div style="text-align:center;margin-bottom:8px;">
<div class="section-title" style="margin-bottom:4px;">Our Team</div>
<div class="section-divider" style="margin:0 auto 12px;"></div>
</div>

<div class="costar-badge" style="margin-top:4px;margin-bottom:8px;">
<div class="costar-badge-title">#1 Most Active Multifamily Sales Team in LA County</div>
<div class="costar-badge-sub">CoStar &bull; 2019, 2020, 2021 &bull; #4 in California</div>
</div>

<div class="bio-grid">
<div class="bio-card">
<img id="bio-glen-headshot" class="bio-headshot" src="{IMG['glen']}" alt="Glen Scher">
<div>
<div class="bio-name">Glen Scher</div>
<div class="bio-title">Senior Managing Director Investments</div>
<div class="bio-text">Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team. Over 500 transactions and $1.6B in closed sales across LA and the Ventura &amp; Santa Barbara counties, consistently closing 40+ deals per year. Glen joined M&amp;M in 2014 after graduating from UC Santa Barbara with a degree in Economics. Before real estate, he was a Division I golfer at UCSB, earning three individual titles, a national top-50 ranking, and UCSB Male Athlete of the Year.</div>
</div>
</div>
<div class="bio-card">
<img id="bio-filip-headshot" class="bio-headshot" src="{IMG['filip']}" alt="Filip Niculete">
<div>
<div class="bio-name">Filip Niculete</div>
<div class="bio-title">Senior Managing Director Investments</div>
<div class="bio-text">Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team. Together, Glen and Filip have closed over $1.6B in transactions and consistently lead the market in inventory. Born in Romania and raised in the San Fernando Valley, Filip studied Finance at San Diego State University and joined M&amp;M in 2011. He has built a reputation for execution, integrity, and relentless work ethic across 15 years in Los Angeles multifamily.</div>
</div>
</div>
</div>

<div class="team-grid">
<div class="team-card"><img class="team-headshot" src="{IMG['team_aida']}" alt="Aida Memary Scher"><div class="team-card-name">Aida Memary Scher</div><div class="team-card-title">Senior Associate</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_morgan']}" alt="Morgan Wetmore"><div class="team-card-name">Morgan Wetmore</div><div class="team-card-title">Associate</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_alexandro']}" alt="Alexandro Tapia"><div class="team-card-name">Alexandro Tapia</div><div class="team-card-title">Associate Investments</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_logan']}" alt="Logan Ward"><div class="team-card-name">Logan Ward</div><div class="team-card-title">Associate</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_jason']}" alt="Jason Mandel"><div class="team-card-name">Jason Mandel</div><div class="team-card-title">Associate</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_luka']}" alt="Luka Leader"><div class="team-card-name">Luka Leader</div><div class="team-card-title">Associate</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_blake']}" alt="Blake Lewitt"><div class="team-card-name">Blake Lewitt</div><div class="team-card-title">Associate Investments</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_mike']}" alt="Mike Palade"><div class="team-card-name">Mike Palade</div><div class="team-card-title">Agent Assistant</div></div>
<div class="team-card"><img class="team-headshot" src="{IMG['team_tony']}" alt="Tony H. Dang"><div class="team-card-name">Tony H. Dang</div><div class="team-card-title">Business Operations Manager</div></div>
</div>

<div class="condition-note" style="margin-top:20px;">
<div class="condition-note-label">Key Achievements</div>
<p class="achievements-list">
&bull; <strong>Chairman's Club</strong>  -  Marcus &amp; Millichap's top-tier annual honor (Glen: 2021; Filip: 2018, 2021)<br>
&bull; <strong>National Achievement Award</strong>  -  Glen: 5 years; Filip: 8 consecutive years<br>
&bull; <strong>Sales Recognition Award</strong>  -  Glen: 10 consecutive years; Filip: 12 years total<br>
&bull; <strong>Traded.co National Rankings</strong>  -  Glen Scher: #8 Deal Junkies, #8 Hot List, #8 Rising Talent<br>
&bull; <strong>Connect CRE Next Generation Award</strong>  -  Filip Niculete (2019)<br>
&bull; <strong>SFVBJ Rookie of the Year</strong>  -  Glen Scher
</p>
</div>

</div>
</div>
""")

# ==================== MARKETING & RESULTS ====================
html_parts.append("""
<div class="page-break-marker"></div>
<div class="section" id="marketing">
<div class="section-title">Our Marketing Approach &amp; Results</div>
<div class="section-subtitle">How We Market Your Listing</div>
<div class="section-divider"></div>

<div class="metrics-grid-4">
<div class="metric-card"><span class="metric-value">30,000+</span><span class="metric-label">Emails Sent</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">10,000+</span><span class="metric-label">Online Views</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">3.7</span><span class="metric-label">Average Offers</span><span class="metric-sub">Per Listing</span></div>
<div class="metric-card"><span class="metric-value">18</span><span class="metric-label">Days to Escrow</span><span class="metric-sub">Per Listing Average</span></div>
</div>

<div class="mkt-quote">
<p>"We are <strong>PROACTIVE</strong> marketers, not reactive. We don't list online and wait for calls. We pick up the phone, call every probable buyer, and explain why your property is a good investment for them."</p>
</div>

<div class="mkt-channels">
<div class="mkt-channel">
<h4>Direct Phone Outreach</h4>
<ul>
<li><strong>30+ probable buyers</strong> called directly per listing</li>
<li><strong>1,500 cold calls per week</strong> across our team of 8 agents</li>
<li>Focus on 1031 exchange buyers, recent purchasers, and nearby property owners</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Email Campaigns</h4>
<ul>
<li><strong>30,000+ verified</strong> investor and broker email addresses</li>
<li><strong>~8,000 unique opens</strong> per "Just Listed" email blast</li>
<li><strong>~800 clicks</strong> per campaign downloading the full marketing package</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Online Platforms</h4>
<ul>
<li><strong>9 listing platforms</strong> with highest-tier exposure on each</li>
<li><strong>10,000+ views per listing</strong> across all platforms combined</li>
<li>Custom profile on MLS, CoStar, LoopNet, Crexi, Brevitas, Redfin, M&amp;M, LAAA.com, ApartmentBuildings.com</li>
</ul>
</div>
<div class="mkt-channel">
<h4>Additional Channels</h4>
<ul>
<li><strong>"Just Listed" postcards</strong> mailed to nearby property owners</li>
<li><strong>Social media</strong> across Facebook, LinkedIn, Instagram, and X</li>
<li><strong>Current inventory attachment</strong> sent ~25 times/day by all team members</li>
</ul>
</div>
</div>

<div class="perf-grid">
<div class="perf-card">
<h4>Pricing Accuracy</h4>
<ul>
<li><strong>97.6%</strong> average sale-price-to-list-price ratio</li>
<li><strong>1 in 5 listings</strong> sell at or above the asking price</li>
<li>Our pricing methodology is data-driven and comp-backed</li>
</ul>
</div>
<div class="perf-card">
<h4>Marketing Speed</h4>
<ul>
<li><strong>18 days</strong> average to open escrow after hitting the market</li>
<li><strong>17.5%</strong> of our listings sell in the first week</li>
<li><strong>3.7 signed offers</strong> per listing on average</li>
</ul>
</div>
<div class="perf-card">
<h4>Contract Strength</h4>
<ul>
<li><strong>10-day average</strong> contingency period</li>
<li>We almost never allow a loan or appraisal contingency</li>
<li><strong>Less than 60 days</strong> average escrow timeframe</li>
<li><strong>10%</strong> open escrow with zero contingencies</li>
</ul>
</div>
<div class="perf-card">
<h4>Exchange Expertise</h4>
<ul>
<li><strong>61%</strong> of our sellers complete a 1031 exchange</li>
<li><strong>29%</strong> of listings sell to a 1031 exchange buyer</li>
<li><strong>76%</strong> of transactions involve at least one exchange</li>
</ul>
</div>
</div>

<div class="platform-strip">
<span class="platform-strip-label">Advertised On</span>
<span class="platform-name">MLS</span>
<span class="platform-name">CoStar</span>
<span class="platform-name">LoopNet</span>
<span class="platform-name">Crexi</span>
<span class="platform-name">Brevitas</span>
<span class="platform-name">Redfin</span>
<span class="platform-name">Marcus &amp; Millichap</span>
<span class="platform-name">LAAA.com</span>
<span class="platform-name">ApartmentBuildings.com</span>
</div>

</div>
""")

# ==================== INVESTMENT OVERVIEW ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="investment">
<div class="inv-split">
<div class="inv-left">
<div class="section-title">Investment Overview</div>
<div class="section-subtitle">500 N Alexandria Ave  -  Los Angeles, CA 90004</div>
<div class="section-divider"></div>

<div class="metrics-grid-4">
<div class="metric-card"><span class="metric-value">7</span><span class="metric-label">Total Units</span></div>
<div class="metric-card"><span class="metric-value">4,360</span><span class="metric-label">Building SF</span></div>
<div class="metric-card"><span class="metric-value">0.10 Ac</span><span class="metric-label">Lot Size</span></div>
<div class="metric-card"><span class="metric-value">1923</span><span class="metric-label">Year Built</span></div>
</div>

<div class="inv-text">
<p>The LAAA Team of Marcus &amp; Millichap is pleased to present for sale 500 N Alexandria Avenue, a 7-unit multifamily investment opportunity in the heart of Los Angeles&rsquo; Koreatown-East Hollywood corridor. Situated on a quiet residential block between Rosewood Avenue and Clinton Street, the property comprises a well-maintained two-story front building (1923) and a rear accessory dwelling unit completed in 2025. The property offers immediate cash flow with significant embedded rent upside through tenant turnover.</p>

<p>The property features a diverse unit mix of four 2-bedroom/1-bathroom apartments, two studios, and one recently completed ADU &mdash; all 100% occupied. In-place rents range from $895 to $2,400 per month, with three units already at or near market levels and four rent-stabilized units offering substantial upside as tenants vacate naturally. The building benefits from recent capital improvements including a full electrical upgrade (400 amps, 6 panels) and the newly constructed ADU.</p>

<p>Zoned R3-1 with TOC Tier 3 overlay and located within a federally designated Opportunity Zone, 500 N Alexandria presents a compelling value-add opportunity. At a suggested list price of $1,275,000, the property delivers a current-year cap rate of 5.48% with a pro forma cap rate of 7.42% upon full renovation and turnover &mdash; offering investors attractive risk-adjusted returns with meaningful upside in one of LA&rsquo;s strongest rental markets.</p>
</div>
<img class="inv-logo" src="{IMG['logo']}" alt="LAAA Team">
</div>

<div class="inv-right">
<div class="inv-photo"><img src="{IMG['grid1']}" alt="500 N Alexandria Ave - Property Photo"></div>
<div class="inv-highlights">
<h4>Investment Highlights</h4>
<ul>
<li><strong>Value-Add Upside</strong>  -  18.5% rent lift potential ($26,064/yr) through natural RSO turnover and classic unit renovations ($18K&ndash;$25K per unit)</li>
<li><strong>Newly Completed ADU</strong>  -  2025 Certificate of Occupancy; fully legal 248 SF studio generating $1,875/month ($22,500/yr)</li>
<li><strong>100% Occupied</strong>  -  Immediate cash flow from day one with zero vacancy risk; $141,036 annual gross rent</li>
<li><strong>TOC Tier 3 &amp; Opportunity Zone</strong>  -  Enhanced development potential and tax benefits for qualified investors holding 10+ years</li>
<li><strong>Strong Koreatown Location</strong>  -  Walk Score 85, 0.6 miles to Metro B Line, premier dining and retail within blocks</li>
<li><strong>Recent Capital Improvements</strong>  -  New electrical system (2024), ADU conversion (2025), reducing near-term capital expenditure requirements</li>
</ul>
</div>
</div>
</div>
</div>
""")

# ==================== LOCATION OVERVIEW ====================
loc_wide_map_html = f'<div class="loc-wide-map"><img src="{IMG["loc_map"]}" alt="Property Location - 500 N Alexandria Ave, Los Angeles"></div>' if IMG.get("loc_map") else ''
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="location">
<div class="section-title">Location Overview</div>
<div class="section-subtitle">Koreatown / East Hollywood  -  90004</div>
<div class="section-divider"></div>

<div class="loc-grid">
<div class="loc-left">
<p>500 N Alexandria Avenue occupies a prime position at the intersection of two of Los Angeles&rsquo; most dynamic neighborhoods &mdash; Koreatown and East Hollywood. This area has experienced a remarkable transformation over the past decade, evolving into one of the city&rsquo;s most desirable rental markets driven by proximity to major employment centers, world-class dining, and unparalleled transit access. The neighborhood&rsquo;s dense urban fabric and walkable streetscape attract a young, professional tenant base that values convenience and lifestyle amenities. Koreatown consistently ranks among the lowest-vacancy multifamily submarkets in Los Angeles County.</p>

<p>The property benefits from exceptional connectivity. The Metro B (Red) Line station at Vermont/Beverly is just 0.6 miles away, providing direct access to Hollywood, Downtown LA, and North Hollywood. Major arterials including Vermont Avenue, Western Avenue, and the 101 Freeway are all within minutes. Residents enjoy walkable access to hundreds of restaurants, caf&eacute;s, and shops along Vermont and Western corridors, Wilshire Boulevard&rsquo;s commercial district, and cultural institutions including the Wilshire Country Club, Barnsdall Art Park, and the forthcoming Metro Purple Line extension stations that will further enhance connectivity.</p>

<p>The property sits in a clean environmental zone &mdash; outside of flood, landslide, liquefaction, fire hazard, methane, and Alquist-Priolo earthquake fault zones per ZIMAS records. The location scores highly across walkability and transit metrics, reflecting the urban density and infrastructure that make this submarket particularly attractive to car-optional tenants.</p>
</div>
<div class="loc-right">
<table class="info-table">
<thead><tr><th colspan="2">Location Details</th></tr></thead>
<tbody>
<tr><td>Walk Score</td><td>85</td></tr>
<tr><td>Transit Score</td><td>Good</td></tr>
<tr><td>Nearest Metro</td><td>Vermont/Beverly (B Line) &mdash; 0.6 mi</td></tr>
<tr><td>Council District</td><td>CD 13 (Hugo Soto-Martinez)</td></tr>
<tr><td>Community Plan</td><td>Wilshire</td></tr>
<tr><td>Neighborhood</td><td>Koreatown / East Hollywood</td></tr>
<tr><td>ZIP Code</td><td>90004</td></tr>
<tr><td>Major Cross Streets</td><td>Vermont Ave &amp; Beverly Blvd</td></tr>
<tr><td>Freeway Access</td><td>US-101 (0.8 mi)</td></tr>
<tr><td>Promise Zone</td><td>Yes</td></tr>
</tbody>
</table>
</div>
</div>
{loc_wide_map_html}

</div>
""")

# ==================== PROPERTY DETAILS ====================
html_parts.append("""
<div class="page-break-marker"></div>
<div class="section" id="prop-details">
<div class="section-title">Property Details</div>
<div class="section-subtitle">500 N Alexandria Ave, Los Angeles, CA 90004</div>
<div class="section-divider"></div>

<div class="prop-grid-4">
<div>
<table class="info-table">
<thead><tr><th colspan="2">Property Overview</th></tr></thead>
<tbody>
<tr><td>Address</td><td>500 N Alexandria Ave, Los Angeles, CA 90004</td></tr>
<tr><td>APN</td><td>5520-009-026</td></tr>
<tr><td>Year Built</td><td>1923 (Front) / 1929 (Rear)</td></tr>
<tr><td>Units</td><td>7 (incl. 1 ADU)</td></tr>
<tr><td>Building SF</td><td>4,360</td></tr>
<tr><td>Lot Size</td><td>4,558 SF (0.10 acres)</td></tr>
<tr><td>Construction</td><td>Wood Frame (Type V-B)</td></tr>
<tr><td>Stories</td><td>2 (Front), 1 (Rear ADU)</td></tr>
<tr><td>Parking</td><td>Garage (~1 space)</td></tr>
<tr><td>Occupancy</td><td>100%</td></tr>
</tbody>
</table>
</div>
<div>
<table class="info-table">
<thead><tr><th colspan="2">Site &amp; Zoning</th></tr></thead>
<tbody>
<tr><td>Zoning</td><td>R3-1</td></tr>
<tr><td>General Plan</td><td>Medium Residential</td></tr>
<tr><td>TOC Tier</td><td>Tier 3</td></tr>
<tr><td>TOIA Tier</td><td>Tier 2</td></tr>
<tr><td>Opportunity Zone</td><td>Yes</td></tr>
<tr><td>Promise Zone</td><td>Yes</td></tr>
<tr><td>AB 2097 / AB 2334</td><td>Eligible</td></tr>
<tr><td>Community Plan</td><td>Wilshire</td></tr>
<tr><td>Council District</td><td>CD 13</td></tr>
<tr><td>HPOZ</td><td>No</td></tr>
</tbody>
</table>
</div>
<div>
<table class="info-table">
<thead><tr><th colspan="2">Building Systems</th></tr></thead>
<tbody>
<tr><td>Roof</td><td>Composition (last replaced ~1993)</td></tr>
<tr><td>Electrical</td><td>Upgraded 2024 &mdash; 400 amps, 6 panels</td></tr>
<tr><td>Plumbing</td><td>Original (galvanized)</td></tr>
<tr><td>Foundation</td><td>Concrete perimeter</td></tr>
<tr><td>Exterior</td><td>Stucco over wood frame</td></tr>
<tr><td>Water Heater</td><td>Central (gas)</td></tr>
<tr><td>HVAC</td><td>Wall heaters (individual)</td></tr>
<tr><td>Metering</td><td>Electric: Individual (6 meters)</td></tr>
<tr><td>ADU</td><td>248 SF, CofO 7/14/2025</td></tr>
</tbody>
</table>
</div>
<div>
<table class="info-table">
<thead><tr><th colspan="2">Regulatory &amp; Compliance</th></tr></thead>
<tbody>
<tr><td>Rent Stabilization</td><td>Yes &mdash; RSO (pre-10/1/1978)</td></tr>
<tr><td>Soft-Story Retrofit</td><td>NOT Required (LADBS)</td></tr>
<tr><td>Code Enforcement</td><td>0 open cases (LADBS)</td></tr>
<tr><td>Seismic Zone</td><td>Zone 4</td></tr>
<tr><td>Flood Zone</td><td>Not in flood zone</td></tr>
<tr><td>Fire Hazard</td><td>Not in fire hazard zone</td></tr>
<tr><td>Methane Zone</td><td>Not in methane zone</td></tr>
<tr><td>ADU Certificate</td><td>Issued 7/14/2025 (#239092)</td></tr>
<tr><td>LAHD Registration</td><td>Required (RSO property)</td></tr>
</tbody>
</table>
</div>
</div>

</div>
""")

# ==================== TRANSACTION HISTORY ====================
html_parts.append("""
<div class="page-break-marker"></div>
<div class="section section-alt" id="txn-history">
<div class="section-title">Transaction History</div>
<div class="section-subtitle">Ownership Chain &amp; Price Appreciation</div>
<div class="section-divider"></div>

<div class="table-scroll"><table>
<thead><tr><th>Date</th><th>Event</th><th>Price / Details</th></tr></thead>
<tbody>
<tr><td>10/09/2017</td><td>Teddy Management LLC acquired from Cho, Eric S.</td><td>$800,000 (Grant Deed)</td></tr>
<tr><td>04/06/2021</td><td>Refinance</td><td>$728,750 loan from Bank of Hope (variable rate)</td></tr>
<tr><td>09/02/2015</td><td>Cho, Eric S. acquired from Cheng, Yen Nien</td><td>$550,000 (Grant Deed)</td></tr>
<tr><td>05/02/2012</td><td>Cheng, Yen Nien acquired from SB Holdings LLC</td><td>$390,000 (Grant Deed)</td></tr>
<tr><td>Prior</td><td>Multiple transfers</td><td>Dating back to early 2000s</td></tr>
</tbody>
</table></div>

<h3 class="sub-heading">Price Appreciation</h3>

<p>500 N Alexandria Avenue has demonstrated consistent value appreciation over the past decade. The property last traded in October 2017 for $800,000 ($114,286/unit) when Teddy Management LLC acquired it from Cho, Eric S. Prior to that, the property traded twice in rapid succession &mdash; $390,000 in 2012 and $550,000 in 2015 &mdash; reflecting the broader market recovery following the Great Recession and growing investor appetite for rent-controlled assets with upside.</p>

<p>Since the 2017 acquisition, the current ownership has added significant value through the construction of a legal ADU (Certificate of Occupancy issued July 2025), effectively increasing the unit count from 6 to 7 and adding approximately $22,500 in annual rental income. The existing financing &mdash; a $728,750 variable-rate loan from Bank of Hope originated in April 2021 &mdash; suggests the owner refinanced to fund improvements, positioning the property for its current market-rate potential.</p>

<p>The property&rsquo;s assessed value of $1,707,340 (2025) represents a 113% increase from the $800,000 acquisition price, reflecting both the ADU addition and assessed value growth. At the suggested list price of $1,275,000, the owner would realize approximately 59% appreciation over their 8.5-year hold period &mdash; a strong outcome for a rent-controlled asset.</p>

</div>
""")

# ==================== BUYER PROFILE & OBJECTIONS ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="buyer-profile">
<div class="section-title">Buyer Profile &amp; Anticipated Objections</div>
<div class="section-subtitle">Target Investors &amp; Data-Backed Responses</div>
<div class="section-divider"></div>

<div class="buyer-split">
<div class="buyer-split-left">
<div class="buyer-profile">
<div class="buyer-profile-label">Target Buyer Profile</div>
<ul>
<li><strong>1031 Exchange Investor</strong>  -  Time-constrained exchangers seeking a stabilized asset with immediate cash flow. The 100% occupancy, diverse unit mix, and sub-$1.5M price point make this an ideal downleg replacement within a 45-day identification window.</li>
<li><strong>Local Value-Add Operator</strong>  -  Hands-on investors targeting RSO turnover plays. With 4 below-market units and a proven renovation playbook ($18K&ndash;$25K per unit), an experienced operator can capture $26,064 in annual rent lift through natural tenant turnover.</li>
<li><strong>Portfolio Consolidator</strong>  -  Small to mid-size multifamily investors adding an income-producing asset to an existing LA portfolio. R3-1 zoning, TOC Tier 3 overlay, and Opportunity Zone designation offer long-term optionality.</li>
<li><strong>ADU-Focused Investor</strong>  -  Investors drawn to the recently completed ADU (CofO 2025) as proof of concept for LA&rsquo;s growing ADU market. The legal unit adds $22,500/yr income and demonstrates the property&rsquo;s ability to support additional density.</li>
</ul>
<p class="bp-closing">Broad appeal across buyer segments supports competitive pricing and a compressed marketing timeline.</p>
</div>
</div>

<div class="buyer-split-right">
<h3 class="sub-heading" style="margin-top:0;">Anticipated Buyer Objections</h3>
<div class="buyer-objections">

<div class="obj-item">
<p class="obj-q">&ldquo;The building is over 100 years old &mdash; won&rsquo;t maintenance costs be astronomical?&rdquo;</p>
<p class="obj-a">While the building&rsquo;s pre-war vintage requires responsible stewardship, several factors mitigate maintenance risk: the electrical system was fully upgraded in 2024 (400 amps, 6 panels), the ADU was professionally constructed with a 2025 Certificate of Occupancy, and LADBS records show zero code enforcement cases. The building is NOT on the soft-story retrofit list. Pre-war construction in Los Angeles has proven remarkably durable &mdash; the original 1923 building has stood for over a century.</p>
</div>

<div class="obj-item">
<p class="obj-q">&ldquo;Only ~1 parking space for 7 units &mdash; won&rsquo;t that scare buyers and tenants?&rdquo;</p>
<p class="obj-a">Parking is the most common objection in Koreatown, yet it rarely affects occupancy or rents in practice. The property has maintained 100% occupancy, and comp buildings with zero parking (212 S Berendo, 101 S Kenmore) have traded at $191K&ndash;$199K/unit. The Walk Score of 85 and proximity to Metro B Line (0.6 mi) attract the growing population of car-optional renters. AB 2097 further reduces parking requirements for transit-adjacent development.</p>
</div>

<div class="obj-item">
<p class="obj-q">&ldquo;RSO limits my ability to increase rents.&rdquo;</p>
<p class="obj-a">RSO is an advantage for sellers, not a liability. Vacancy decontrol under Costa-Hawkins allows owners to reset rents to market upon natural tenant turnover. The 4 RSO tenants represent $2,172/month ($26,064/year) in embedded upside &mdash; a built-in value-add that doesn&rsquo;t require entitlements, approvals, or construction.</p>
</div>

<div class="obj-item">
<p class="obj-q">&ldquo;Why is the price per unit lower than other recent sales?&rdquo;</p>
<p class="obj-a">The $182,143/unit price reflects the property&rsquo;s unique position as a 7-unit building with limited parking and a mixed unit mix (studios, 2BRs, and ADU). However, this is precisely what creates the opportunity: the pro forma cap rate of 7.42% exceeds comparable closed sales, and the ADU &mdash; which adds ~$215K in capitalized value &mdash; is a premium feature not available in most vintage comp properties.</p>
</div>

</div>
</div>
</div>

<div class="buyer-photo"><img src="{IMG['grid2']}" alt="500 N Alexandria Ave - Property Photo"></div>

</div>
""")

# ==================== SALE COMPS ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="sale-comps">
<div class="section-title">Comparable Sales Analysis</div>
<div class="section-subtitle">4 Confirmed Closed Sales in Koreatown / Mid-Wilshire  -  Past 8 Months</div>
<div class="section-divider"></div>

<div id="saleMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>City</th><th>Units</th><th>Sale Date</th><th>Price</th><th>$/Unit</th><th>$/SF</th><th>Cap</th><th>GRM</th><th>Yr Built</th><th>Notes</th></tr></thead>
<tbody>
{sale_comps_html}
</tbody>
</table></div>

<h3 class="sub-heading">Individual Comp Analysis</h3>

{''.join(COMP_NARRATIVES)}

<h3 class="sub-heading">Market Narrative</h3>

<p>The Koreatown-Mid Wilshire multifamily market has demonstrated resilience through the rate cycle. Three arm&rsquo;s-length closed sales within the past eight months provide a clear pricing framework for vintage RSO apartment buildings in the 90004 zip code. The anchor comparable &mdash; 101 S Kenmore Avenue, an 8-unit 1925-vintage building &mdash; traded at $199,375 per unit with a 7.29% adjusted cap rate, establishing the premium end of the market for well-maintained properties with reliable financial data.</p>

<p>Pricing dynamics reflect a market that rewards income quality. 212 S Berendo &mdash; with 8 deeply rent-controlled 2BR units and 108% rent upside &mdash; traded at a compressed 4.15% cap rate, demonstrating that buyers are willing to accept lower current yields when the embedded upside is substantial and clearly documented. In contrast, 247 N New Hampshire&rsquo;s off-market sale at $116,667/unit illustrates the discount applied to smaller units (studios) with unreliable financial data.</p>

<p>At $182,143 per unit, 500 N Alexandria is competitively positioned within the closed comp range. The subject&rsquo;s mixed unit types (2BR + studio + ADU), limited parking, and smaller building footprint justify a modest discount to the Kenmore benchmark, while the 2025 ADU, TOC Tier 3 overlay, and Opportunity Zone status provide upside optionality not available in any closed comp. The SP/LP ratio averaging 95% suggests list-to-close negotiation of approximately 3&ndash;5%.</p>

</div>
""")

# ==================== ON-MARKET COMPS ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="on-market">
<div class="section-title">On-Market Comparables</div>
<div class="section-subtitle">Active &amp; Pending Listings in Koreatown / Mid-Wilshire</div>
<div class="section-divider"></div>

<div id="activeMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Units</th><th>List Price</th><th>$/Unit</th><th>Cap</th><th>GRM</th><th>DOM</th><th>Status</th><th>Notes</th></tr></thead>
<tbody>
""")
for c in ACTIVE_COMPS:
    html_parts.append(f'<tr><td>{c["num"]}</td><td>{c["addr"]}</td><td>{c["units"]}</td><td>{fc(c["price"])}</td><td>{fc(c["ppu"])}</td><td>{fp(c["cap"])}</td><td>{c["grm"]:.2f}x</td><td>{c["dom"]}</td><td>{c["status"]}</td><td style="font-size:11px;">{c["notes"]}</td></tr>\n')
html_parts.append(f"""
</tbody>
</table></div>

<h3 class="sub-heading">Competitive Positioning</h3>

<p>The active on-market inventory provides important context for the subject&rsquo;s competitive positioning. The pending sale at 502 N Serrano ($224,375/unit) validates buyer demand in the submarket at a higher price point, while fresh listings at 121 and 127 S Oxford ($200K&ndash;$225K/unit) will test the market&rsquo;s appetite for post-war 1BR product. Two stale listings &mdash; 426 N Virgil (133 DOM) and 4053 Oakwood (285 DOM) &mdash; have both reduced their asking prices, suggesting the market has a clear ceiling for aggressive pricing.</p>

<p>At $182,143 per unit, 500 N Alexandria is priced below every active and pending comparable in the submarket, creating an immediate competitive advantage. The most relevant on-market comparable &mdash; 310 N St Andrews Place, which also features 2025 ADUs &mdash; is asking $311,250/unit, nearly 70% higher than the subject. While St Andrews benefits from a more extensive renovation program, the pricing gap highlights the value proposition available at 500 N Alexandria for buyers seeking ADU exposure at an accessible price point.</p>

</div>
""")

# ==================== RENT COMPS ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="rent-comps">
<div class="section-title">Rent Comparables</div>
<div class="section-subtitle">Current Market Rents in Koreatown / East Hollywood</div>
<div class="section-divider"></div>

<div id="rentMap" class="leaflet-map"></div>
<p class="map-fallback">Interactive map available at the live URL.</p>

<h3 class="sub-heading">2-Bedroom Rent Comparables</h3>
<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Rent</th><th>Reno Level</th><th>Distance</th><th>Key Features</th></tr></thead>
<tbody>
""")
for i, rc in enumerate(RENT_COMPS_2BR):
    html_parts.append(f'<tr><td>{i+1}</td><td>{rc["addr"]}</td><td>${rc["rent"]:,}</td><td>{rc["reno"]}</td><td>{rc["dist"]}</td><td style="font-size:11px;">{rc["features"]}</td></tr>\n')
br2_rents = [rc["rent"] for rc in RENT_COMPS_2BR]
html_parts.append(f'<tr style="font-weight:600;background:#FFF8E7;"><td></td><td><strong>Summary</strong></td><td>${min(br2_rents):,}&ndash;${max(br2_rents):,}</td><td></td><td></td><td>Avg ${sum(br2_rents)//len(br2_rents):,} | <strong>Median ${int(statistics.median(br2_rents)):,}</strong></td></tr>\n')
html_parts.append("""
</tbody>
</table></div>

<h3 class="sub-heading">Studio Rent Comparables</h3>
<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Address</th><th>Rent</th><th>Reno Level</th><th>Distance</th><th>Key Features</th></tr></thead>
<tbody>
""")
for i, rc in enumerate(RENT_COMPS_STUDIO):
    html_parts.append(f'<tr><td>{i+1}</td><td>{rc["addr"]}</td><td>${rc["rent"]:,}</td><td>{rc["reno"]}</td><td>{rc["dist"]}</td><td style="font-size:11px;">{rc["features"]}</td></tr>\n')
studio_rents = [rc["rent"] for rc in RENT_COMPS_STUDIO]
html_parts.append(f'<tr style="font-weight:600;background:#FFF8E7;"><td></td><td><strong>Summary</strong></td><td>${min(studio_rents):,}&ndash;${max(studio_rents):,}</td><td></td><td></td><td>Avg ${sum(studio_rents)//len(studio_rents):,} | <strong>Median ${int(statistics.median(studio_rents)):,}</strong></td></tr>\n')
html_parts.append(f"""
</tbody>
</table></div>

<h3 class="sub-heading">Pro Forma Rent Narrative</h3>

<p>The rent comp survey confirms meaningful upside for 500 N Alexandria&rsquo;s below-market units. Renovated 2-bedroom apartments in pre-war Koreatown buildings are consistently achieving $2,095 to $2,350 per month, with the median settling at $2,200 &mdash; the basis for our pro forma assumption on the RSO 2BR units (502 and 504). This represents a conservative approach, positioned at the center rather than the top of the comparable range.</p>

<p>Studios in the same vintage-building profile lease at $1,395 to $1,445 post-renovation, with the median at $1,425. The subject&rsquo;s ADU at $1,875 for 248 SF ($7.56/SF) is already at or near the market ceiling for micro-unit product. No additional rent lift is assumed for the ADU, reflecting a realistic assessment of the size constraint. The overall pro forma rent schedule of $13,925/month ($167,100/year) represents an 18.5% increase over current in-place rents &mdash; achievable through natural RSO turnover and a classic renovation scope of $18K&ndash;$25K per unit.</p>

<p>Confidence level is moderate-conservative. The pro forma rents are set at or slightly below the median comp range to account for the subject&rsquo;s smaller lot, limited parking, and absence of premium amenities like in-unit washer/dryers or central air. Vintage small buildings in this submarket are largely insulated from new Class A competition, which targets a different tenant demographic at a higher price point.</p>

</div>
""")

# ==================== FINANCIAL ANALYSIS ====================
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="financials">
<div class="section-title">Financial Analysis</div>
<div class="section-subtitle">Investment Underwriting</div>
<div class="section-divider"></div>

<!-- SCREEN 1: RENT ROLL -->
<h3 class="sub-heading">Unit Mix &amp; Rent Roll</h3>
<div class="table-scroll"><table>
<thead><tr><th>Unit</th><th>Type</th><th>SF</th><th>Current Rent</th><th>Rent/SF</th><th>Market Rent</th><th>Market/SF</th></tr></thead>
<tbody>{rent_roll_html}</tbody>
</table></div>
<p style="font-size:11px;color:#888;font-style:italic;margin-top:-16px;margin-bottom:20px;">Note: All 7 units are 100% occupied. Total SF reflects approximate livable area per unit; the 4,360 SF used in $/SF calculations is gross building area per LA County Assessor records.</p>

<!-- SCREEN 2: OPERATING STATEMENT + NOTES (side-by-side) -->
<div class="os-two-col">
<div class="os-left">
<h3 class="sub-heading">Operating Statement</h3>
<table>
<thead><tr><th>Income</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">% EGI</th></tr></thead>
<tbody>{op_income_html}</tbody>
</table>
<table>
<thead><tr><th>Expenses</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">% EGI</th></tr></thead>
<tbody>{op_expense_html}</tbody>
</table>
<p style="font-size:10px;color:#888;font-style:italic;margin-top:-12px;">Note: Property taxes reassessed at the $1,275,000 list price. The pricing matrix recalculates taxes at each price point.</p>
</div>
<div class="os-right">
<h3 class="sub-heading">Notes to Operating Statement</h3>
<p><strong>[1] Other Income:</strong> None. No laundry, no separate parking income, no RUBS.</p>
<p><strong>[2] Real Estate Taxes:</strong> Reassessed to list price at 1.17% LA County rate. Seller&rsquo;s Prop 13 basis: $21,283 on $1.707M assessed.</p>
<p><strong>[3] Insurance:</strong> $900/unit. Broker-optimistic $800 + $100 pre-1950 adjustment. Wood frame, soft-story NOT required.</p>
<p><strong>[4] Water / Sewer:</strong> $500/bedroom &times; 11 bedrooms. Always landlord-paid. No pool.</p>
<p><strong>[5] Trash:</strong> $400/unit &times; 7. LA recycling/organic bins included.</p>
<p><strong>[6] Common Area Electric:</strong> $1,500 flat (Tier 1). Minimal common area, no elevator/pool.</p>
<p><strong>[7] Repairs &amp; Maintenance:</strong> $1,300/unit. Base $1,200 + $150 pre-1940 adj (50%) &minus; $50 ADU/electrical CapEx credit.</p>
<p><strong>[8] Contract Services:</strong> $1,500 flat (Tier 1). Small lot, minimal landscaping.</p>
<p><strong>[9] Administrative:</strong> $1,000 flat (Tier 1). Accounting, legal, bank fees, permits.</p>
<p><strong>[10] Marketing:</strong> $500 flat. 100% occupied, strong rental submarket.</p>
<p><strong>[11] Management Fee:</strong> MAX(4% EGI, $18,000). Minimum binding at $18K for this small property.</p>
<p><strong>[12] Reserves:</strong> $350/unit. Pre-1940 base $400 &minus; $50 recent CapEx credit.</p>
<p><strong>[13] LAHD Registration:</strong> $43.32/unit &times; 7. RSO property, partially passable to tenants.</p>
<p><strong>[14] Other:</strong> $250 flat (Tier 1). Miscellaneous catch-all.</p>
</div>
</div>

<!-- SCREEN 3: FINANCIAL SUMMARY -->
<div class="summary-page">
<div class="summary-banner">Summary</div>

<div class="summary-two-col">

<div class="summary-left">
<table class="summary-table">
<thead><tr><th colspan="2" class="summary-header">OPERATING DATA</th></tr></thead>
<tbody>
<tr><td>Price</td><td class="num">${LIST_PRICE:,}</td></tr>
<tr><td>Down Payment ({1-LTV:.0%})</td><td class="num">${AT_LIST['down_payment']:,.0f}</td></tr>
<tr><td>Number of Units</td><td class="num">{UNITS}</td></tr>
<tr><td>Price Per Unit</td><td class="num">${AT_LIST['per_unit']:,.0f}</td></tr>
<tr><td>Price Per SqFt</td><td class="num">${AT_LIST['per_sf']:,.2f}</td></tr>
<tr><td>Gross SqFt</td><td class="num">{SF:,}</td></tr>
<tr><td>Lot Size</td><td class="num">{LOT_SIZE_ACRES} Acres</td></tr>
<tr><td>Approx. Year Built</td><td class="num">1923/1929</td></tr>
</tbody>
</table>

<table class="summary-table">
<thead><tr><th class="summary-header">RETURNS</th><th class="num summary-header">Current</th><th class="num summary-header">Pro Forma</th></tr></thead>
<tbody>
<tr><td>CAP Rate</td><td class="num">{AT_LIST['cur_cap']:.2f}%</td><td class="num">{AT_LIST['pf_cap']:.2f}%</td></tr>
<tr><td>GRM</td><td class="num">{AT_LIST['grm']:.2f}</td><td class="num">{AT_LIST['pf_grm']:.2f}</td></tr>
<tr><td>Cash-on-Cash</td><td class="num">{AT_LIST['coc_cur']:.2f}%</td><td class="num">{AT_LIST['coc_pf']:.2f}%</td></tr>
<tr><td>Debt Coverage Ratio</td><td class="num">{AT_LIST['dcr_cur']:.2f}</td><td class="num">{AT_LIST['dcr_pf']:.2f}</td></tr>
</tbody>
</table>

<table class="summary-table">
<thead><tr><th colspan="2" class="summary-header">FINANCING</th></tr></thead>
<tbody>
<tr><td>Loan Amount</td><td class="num">${AT_LIST['loan_amount']:,.0f}</td></tr>
<tr><td>Loan Type</td><td class="num">New</td></tr>
<tr><td>Interest Rate</td><td class="num">{INTEREST_RATE:.2%}</td></tr>
<tr><td>Amortization</td><td class="num">{AMORTIZATION_YEARS} Years</td></tr>
<tr><td>Loan Constant</td><td class="num">{LOAN_CONSTANT:.2%}</td></tr>
<tr><td>Year Due</td><td class="num">2031</td></tr>
</tbody>
</table>

<table class="summary-table">
<thead><tr><th class="summary-header">UNIT SUMMARY</th><th class="num summary-header">#</th><th class="num summary-header">Avg SF</th><th class="num summary-header">Sched.</th><th class="num summary-header">Market</th></tr></thead>
<tbody>
<tr><td>2 Bed / 1 Bath</td><td class="num">{len(br2_units)}</td><td class="num">620</td><td class="num">${br2_avg_cur:,.0f}</td><td class="num">${br2_avg_mkt:,.0f}</td></tr>
<tr><td>Studio</td><td class="num">{len(studio_units)}</td><td class="num">400</td><td class="num">${studio_avg_cur:,.0f}</td><td class="num">${studio_avg_mkt:,.0f}</td></tr>
<tr><td>ADU</td><td class="num">{len(adu_units)}</td><td class="num">248</td><td class="num">${adu_avg_cur:,.0f}</td><td class="num">${adu_avg_mkt:,.0f}</td></tr>
</tbody>
</table>
</div>

<div class="summary-right">
<table class="summary-table">
<thead><tr><th class="summary-header">INCOME</th><th class="num summary-header">Current</th><th class="num summary-header">Pro Forma</th></tr></thead>
<tbody>
<tr><td>Gross Scheduled Rent</td><td class="num">${GSR:,}</td><td class="num">${PF_GSR:,}</td></tr>
<tr><td>Less: Vacancy (5%)</td><td class="num">(${ GSR * VACANCY_PCT:,.0f})</td><td class="num">(${ PF_GSR * VACANCY_PCT:,.0f})</td></tr>
<tr><td>Effective Rental Income</td><td class="num">${GSR * (1-VACANCY_PCT):,.0f}</td><td class="num">${PF_GSR * (1-VACANCY_PCT):,.0f}</td></tr>
<tr><td>Other Income</td><td class="num">${OTHER_INCOME:,}</td><td class="num">${OTHER_INCOME:,}</td></tr>
<tr class="summary"><td><strong>Effective Gross Income</strong></td><td class="num"><strong>${AT_LIST['cur_egi']:,.0f}</strong></td><td class="num"><strong>${AT_LIST['pf_egi']:,.0f}</strong></td></tr>
</tbody>
</table>

<table class="summary-table">
<thead><tr><th class="summary-header">CASH FLOW</th><th class="num summary-header">Current</th><th class="num summary-header">Pro Forma</th></tr></thead>
<tbody>
<tr><td>Net Operating Income</td><td class="num">${AT_LIST['cur_noi']:,.0f}</td><td class="num">${AT_LIST['pf_noi']:,.0f}</td></tr>
<tr><td>Less: Debt Service</td><td class="num">(${ AT_LIST['debt_service']:,.0f})</td><td class="num">(${ AT_LIST['debt_service']:,.0f})</td></tr>
<tr><td>Net Cash Flow</td><td class="num">${AT_LIST['net_cf_cur']:,.0f}</td><td class="num">${AT_LIST['net_cf_pf']:,.0f}</td></tr>
<tr><td>Cash-on-Cash Return</td><td class="num">{AT_LIST['coc_cur']:.2f}%</td><td class="num">{AT_LIST['coc_pf']:.2f}%</td></tr>
<tr><td>Principal Reduction (Yr 1)</td><td class="num" colspan="2">${AT_LIST['prin_red']:,.0f}</td></tr>
<tr class="summary"><td><strong>Total Return (Yr 1)</strong></td><td class="num"><strong>{AT_LIST['total_return_pct_cur']:.2f}%</strong></td><td class="num"><strong>{AT_LIST['total_return_pct_pf']:.2f}%</strong></td></tr>
</tbody>
</table>

<table class="summary-table">
<thead><tr><th class="summary-header">EXPENSES</th><th class="num summary-header">Current</th><th class="num summary-header">Pro Forma</th></tr></thead>
<tbody>
{sum_expense_html}<tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${AT_LIST['cur_exp']:,.0f}</strong></td><td class="num"><strong>${AT_LIST['pf_exp']:,.0f}</strong></td></tr>
<tr><td>Expenses as % of EGI</td><td class="num">{AT_LIST['cur_exp']/AT_LIST['cur_egi']*100:.1f}%</td><td class="num">{AT_LIST['pf_exp']/AT_LIST['pf_egi']*100:.1f}%</td></tr>
<tr><td>Expenses / Unit</td><td class="num">${AT_LIST['cur_exp']/UNITS:,.0f}</td><td class="num">${AT_LIST['pf_exp']/UNITS:,.0f}</td></tr>
<tr><td>Expenses / SF</td><td class="num">${AT_LIST['cur_exp']/SF:,.2f}</td><td class="num">${AT_LIST['pf_exp']/SF:,.2f}</td></tr>
</tbody>
</table>
</div>

</div>
</div>

<!-- SCREEN 4: PRICE REVEAL + PRICING MATRIX -->
<div class="price-reveal">
<div style="text-align:center; margin-bottom:32px;">
<div style="font-size:13px; text-transform:uppercase; letter-spacing:2px; color:#C5A258; font-weight:600; margin-bottom:8px;">Suggested List Price</div>
<div style="font-size:56px; font-weight:700; color:#1B3A5C; line-height:1;">${LIST_PRICE:,}</div>
</div>

<div class="metrics-grid metrics-grid-4">
<div class="metric-card"><span class="metric-value">${AT_LIST['per_unit']:,.0f}</span><span class="metric-label">Price Per Unit</span></div>
<div class="metric-card"><span class="metric-value">${AT_LIST['per_sf']:,.0f}</span><span class="metric-label">Price Per SF</span></div>
<div class="metric-card"><span class="metric-value">{AT_LIST['cur_cap']:.2f}%</span><span class="metric-label">Current Cap Rate</span></div>
<div class="metric-card"><span class="metric-value">{AT_LIST['grm']:.2f}</span><span class="metric-label">Current GRM</span></div>
</div>

<h3 class="sub-heading">Pricing Matrix</h3>
<p style="font-size:12px;color:#666;margin-bottom:12px;"><em>Highlighted row represents the suggested list price. Cap rates are tax-adjusted (property taxes recalculated at 1.17% of sale price per LA County Prop 13 reassessment), which adjusts NOI and cap rate at every row.</em></p>
<div class="table-scroll"><table>
<thead><tr><th class="num">Purchase Price</th><th class="num">Current Cap</th><th class="num">Pro Forma Cap</th><th class="num">Cash-on-Cash</th><th class="num">$/SF</th><th class="num">$/Unit</th><th class="num">PF GRM</th></tr></thead>
<tbody>{matrix_html}</tbody>
</table></div>

<div class="summary-trade-range">
<div class="summary-trade-label">A TRADE PRICE IN THE CURRENT INVESTMENT ENVIRONMENT OF</div>
<div class="summary-trade-prices">$1,200,000 &mdash; $1,275,000</div>
</div>

<h3 class="sub-heading">Pricing Rationale</h3>

<p>The suggested list price of <strong>$1,275,000</strong> positions 500 N Alexandria as one of the most compelling value-add opportunities currently available in the Koreatown submarket. At $182,143 per unit and a 5.48% current cap rate, the pricing falls within the established range of comparable closed sales while offering a materially superior pro forma return of 7.42% upon full renovation and turnover &mdash; an outcome supported by 12 building-level and 16 unit-level rent comparables.</p>

<p>The pricing strategy balances seller optimization with buyer accessibility. At 55% LTV, a buyer can secure conventional financing at approximately 6.00% with a comfortable 1.38x debt service coverage ratio, generating positive cash flow from day one. The $573,750 equity requirement is accessible to the 1031 exchange investor pool that comprises 61% of LAAA Team&rsquo;s closed transactions, ensuring a deep bench of qualified buyers.</p>

<p>Three independent valuation methods &mdash; cap rate, price-per-unit, and gross rent multiplier &mdash; converge tightly around the $1,225,000&ndash;$1,300,000 range, providing high confidence in the suggested price. On-market competition is limited at this price point (every comparable listing exceeds $1,595,000), giving the subject a meaningful competitive advantage that should drive strong buyer interest and a compressed marketing timeline.</p>

<div class="condition-note"><strong>Assumptions &amp; Conditions:</strong> Financing terms are estimates and subject to change; contact your Marcus &amp; Millichap Capital Corporation representative. Vacancy modeled at 5.0% based on Koreatown market conditions. Management fee at MAX(4% EGI, $18,000) reflects third-party professional management minimum for small properties. Real estate taxes estimated at 1.17% of sale price reflecting Proposition 13 reassessment at close of escrow. Operating reserves at $350/unit. All information believed reliable but not guaranteed; buyer to verify independently.</div>
</div>

</div>
""")

# ==================== FOOTER ====================
html_parts.append(f"""
<div class="footer" id="contact">
<img src="{IMG['logo']}" class="footer-logo" alt="LAAA Team">
<div class="footer-team">
<div class="footer-person">
<img src="{IMG['glen']}" class="footer-headshot" alt="Glen Scher">
<div class="footer-name">Glen Scher</div>
<div class="footer-title">Senior Managing Director Investments</div>
<div class="footer-contact"><a href="tel:8182122808">(818) 212-2808</a><br><a href="mailto:Glen.Scher@marcusmillichap.com">Glen.Scher@marcusmillichap.com</a><br>CA License: 01962976</div>
</div>
<div class="footer-person">
<img src="{IMG['filip']}" class="footer-headshot" alt="Filip Niculete">
<div class="footer-name">Filip Niculete</div>
<div class="footer-title">Senior Managing Director Investments</div>
<div class="footer-contact"><a href="tel:8182122748">(818) 212-2748</a><br><a href="mailto:Filip.Niculete@marcusmillichap.com">Filip.Niculete@marcusmillichap.com</a><br>CA License: 01905352</div>
</div>
</div>
<div class="footer-office">16830 Ventura Blvd, Ste. 100, Encino, CA 91436 | (818) 212-2700</div>
<div class="footer-disclaimer">This information has been secured from sources we believe to be reliable, but we make no representations or warranties, expressed or implied, as to the accuracy of the information. Buyer must verify the information and bears all risk for any inaccuracies. Marcus &amp; Millichap Real Estate Investment Services, Inc. | License: CA 01930580.</div>
</div>
""")

# ==================== JAVASCRIPT ====================
html_parts.append(f"""
<script>
var params = new URLSearchParams(window.location.search);
var client = params.get('client');
if (client) {{ var el = document.getElementById('client-greeting'); if (el) el.textContent = 'Prepared Exclusively for ' + client; }}
document.querySelectorAll('.toc-nav a').forEach(function(link) {{ link.addEventListener('click', function(e) {{ e.preventDefault(); var target = document.querySelector(this.getAttribute('href')); if (target) {{ var navHeight = document.getElementById('toc-nav').offsetHeight; var targetPos = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 4; window.scrollTo({{ top: targetPos, behavior: 'smooth' }}); }} }}); }});
var tocLinks = document.querySelectorAll('.toc-nav a'); var tocSections = []; tocLinks.forEach(function(link) {{ var id = link.getAttribute('href').substring(1); var section = document.getElementById(id); if (section) tocSections.push({{ link: link, section: section }}); }});
function updateActiveTocLink() {{ var navHeight = document.getElementById('toc-nav').offsetHeight + 20; var scrollPos = window.pageYOffset + navHeight; var current = null; tocSections.forEach(function(item) {{ if (item.section.offsetTop <= scrollPos) current = item.link; }}); tocLinks.forEach(function(link) {{ link.classList.remove('toc-active'); }}); if (current) current.classList.add('toc-active'); }}
window.addEventListener('scroll', updateActiveTocLink); updateActiveTocLink();
{sale_map_js}
{active_map_js}
{rent_map_js}
</script>
""")

# ============================================================
# FALLBACK CHAT WIDGET (used when rag_pipeline deps missing)
# ============================================================
def _fallback_chat_widget():
    """Return self-contained chat widget HTML/CSS/JS without RAG pipeline."""
    starters_js = ", ".join(f'"{q}"' for q in STARTER_QUESTIONS)
    return f"""
<!-- LAAA BOV AI Chat Widget -->
<style>
@media print {{ .bov-chat-widget, .bov-chat-bubble {{ display: none !important; }} }}
.bov-chat-bubble {{ position: fixed; bottom: 90px; right: 24px; width: 56px; height: 56px; border-radius: 50%; background: #1B3A5C; color: #fff; border: none; cursor: pointer; box-shadow: 0 4px 16px rgba(0,0,0,0.25); z-index: 10000; display: flex; align-items: center; justify-content: center; transition: transform 0.2s, background 0.2s; }}
.bov-chat-bubble:hover {{ transform: scale(1.08); background: #244a6e; }}
.bov-chat-bubble svg {{ width: 26px; height: 26px; fill: #fff; }}
.bov-chat-widget {{ position: fixed; bottom: 90px; right: 24px; width: 390px; height: 540px; background: #fff; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.2); z-index: 10001; display: none; flex-direction: column; overflow: hidden; font-family: 'Inter', -apple-system, sans-serif; }}
.bov-chat-widget.open {{ display: flex; }}
.bov-chat-header {{ background: #1B3A5C; color: #fff; padding: 16px 18px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }}
.bov-chat-header-title {{ font-size: 14px; font-weight: 600; line-height: 1.3; }}
.bov-chat-header-sub {{ font-size: 11px; opacity: 0.75; margin-top: 2px; }}
.bov-chat-close {{ background: none; border: none; color: #fff; cursor: pointer; font-size: 22px; padding: 0 0 0 12px; opacity: 0.8; line-height: 1; }}
.bov-chat-close:hover {{ opacity: 1; }}
.bov-chat-messages {{ flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }}
.bov-chat-starters {{ display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }}
.bov-chat-starter {{ background: #f0f4f8; border: 1px solid #d8e1eb; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #1B3A5C; cursor: pointer; text-align: left; transition: background 0.15s, border-color 0.15s; line-height: 1.4; }}
.bov-chat-starter:hover {{ background: #e2eaf2; border-color: #b0c4de; }}
.bov-chat-msg {{ max-width: 88%; padding: 10px 14px; border-radius: 12px; font-size: 13px; line-height: 1.55; word-wrap: break-word; }}
.bov-chat-msg.user {{ align-self: flex-end; background: #1B3A5C; color: #fff; border-bottom-right-radius: 4px; }}
.bov-chat-msg.bot {{ align-self: flex-start; background: #f0f4f8; color: #1a1a1a; border-bottom-left-radius: 4px; }}
.bov-chat-msg.bot p {{ margin: 0 0 8px 0; }} .bov-chat-msg.bot p:last-child {{ margin-bottom: 0; }}
.bov-chat-msg.bot ul, .bov-chat-msg.bot ol {{ margin: 4px 0 8px 18px; padding: 0; }}
.bov-chat-msg.bot li {{ margin-bottom: 3px; }} .bov-chat-msg.bot strong {{ font-weight: 600; }}
.bov-chat-msg.bot table {{ border-collapse: collapse; margin: 6px 0; width: 100%; font-size: 12px; }}
.bov-chat-msg.bot th, .bov-chat-msg.bot td {{ border: 1px solid #d0d7de; padding: 4px 8px; text-align: left; }}
.bov-chat-msg.bot th {{ background: #e8edf2; font-weight: 600; }}
.bov-chat-sources {{ font-size: 11px; color: #6b7280; margin-top: 6px; cursor: pointer; user-select: none; }}
.bov-chat-sources-list {{ display: none; margin-top: 4px; padding: 6px 10px; background: #f9fafb; border-radius: 6px; font-size: 11px; line-height: 1.5; }}
.bov-chat-sources.expanded .bov-chat-sources-list {{ display: block; }}
.bov-chat-disclaimer {{ font-size: 10px; color: #9ca3af; margin-top: 4px; font-style: italic; line-height: 1.4; }}
.bov-chat-typing {{ display: flex; gap: 5px; padding: 10px 14px; align-self: flex-start; background: #f0f4f8; border-radius: 12px; border-bottom-left-radius: 4px; }}
.bov-chat-typing span {{ width: 7px; height: 7px; background: #94a3b8; border-radius: 50%; animation: bovTyping 1.2s ease-in-out infinite; }}
.bov-chat-typing span:nth-child(2) {{ animation-delay: 0.2s; }}
.bov-chat-typing span:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes bovTyping {{ 0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }} 30% {{ transform: translateY(-6px); opacity: 1; }} }}
.bov-chat-input-area {{ display: flex; padding: 12px; border-top: 1px solid #e5e7eb; gap: 8px; flex-shrink: 0; background: #fff; }}
.bov-chat-input {{ flex: 1; border: 1px solid #d1d5db; border-radius: 10px; padding: 10px 14px; font-size: 13px; font-family: inherit; outline: none; transition: border-color 0.15s; resize: none; }}
.bov-chat-input:focus {{ border-color: #1B3A5C; }} .bov-chat-input::placeholder {{ color: #9ca3af; }}
.bov-chat-send {{ background: #1B3A5C; color: #fff; border: none; border-radius: 10px; padding: 0 16px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.15s; flex-shrink: 0; }}
.bov-chat-send:hover {{ background: #244a6e; }} .bov-chat-send:disabled {{ background: #94a3b8; cursor: not-allowed; }}
.bov-chat-limit-msg {{ text-align: center; padding: 12px; font-size: 12px; color: #6b7280; background: #f9fafb; border-top: 1px solid #e5e7eb; flex-shrink: 0; }}
.bov-chat-limit-msg a {{ color: #1B3A5C; font-weight: 600; }}
@media (max-width: 480px) {{ .bov-chat-widget {{ bottom: 0; right: 0; width: 100%; height: 100%; border-radius: 0; }} .bov-chat-bubble {{ bottom: 80px; right: 16px; }} }}
</style>
<button class="bov-chat-bubble" id="bovChatBubble" aria-label="Ask about this property">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
</button>
<div class="bov-chat-widget" id="bovChatWidget">
    <div class="bov-chat-header">
        <div><div class="bov-chat-header-title">Ask about {PROPERTY_DISPLAY_NAME}</div>
        <div class="bov-chat-header-sub">AI assistant - answers from BOV materials only</div></div>
        <button class="bov-chat-close" id="bovChatClose">&times;</button>
    </div>
    <div class="bov-chat-messages" id="bovChatMessages">
        <div class="bov-chat-msg bot">Hi! I can answer questions about the investment details, financials, comparable sales, rent analysis, and more for this property. What would you like to know?</div>
        <div class="bov-chat-starters" id="bovChatStarters"></div>
    </div>
    <div class="bov-chat-input-area" id="bovChatInputArea">
        <input type="text" class="bov-chat-input" id="bovChatInput" placeholder="Ask a question..." autocomplete="off">
        <button class="bov-chat-send" id="bovChatSend">Send</button>
    </div>
</div>
<script>
(function() {{
    'use strict';
    var WORKER_URL = '{CHAT_WORKER_URL}';
    var NAMESPACE = '{BOV_NAMESPACE}';
    var STARTERS = [{starters_js}];
    var PRECOMPUTED = {{}};
    var MAX_MESSAGES = 30;
    var DISCLAIMER = 'Information sourced from BOV materials. Verify independently before making investment decisions.';
    var history = [], messageCount = 0, isStreaming = false;
    var bubble = document.getElementById('bovChatBubble'), widget = document.getElementById('bovChatWidget');
    var closeBtn = document.getElementById('bovChatClose'), messagesEl = document.getElementById('bovChatMessages');
    var startersEl = document.getElementById('bovChatStarters'), inputEl = document.getElementById('bovChatInput');
    var sendBtn = document.getElementById('bovChatSend'), inputArea = document.getElementById('bovChatInputArea');
    STARTERS.forEach(function(q) {{ var pill = document.createElement('button'); pill.className = 'bov-chat-starter'; pill.textContent = q; pill.addEventListener('click', function() {{ sendMessage(q); }}); startersEl.appendChild(pill); }});
    bubble.addEventListener('click', function() {{ widget.classList.add('open'); bubble.style.display = 'none'; inputEl.focus(); }});
    closeBtn.addEventListener('click', function() {{ widget.classList.remove('open'); bubble.style.display = 'flex'; }});
    inputEl.addEventListener('keydown', function(e) {{ if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(inputEl.value); }} }});
    sendBtn.addEventListener('click', function() {{ sendMessage(inputEl.value); }});
    function renderMarkdown(text) {{ text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>'); text = text.replace(/`([^`]+)`/g, '<code style="background:#e8edf2;padding:1px 4px;border-radius:3px;font-size:12px;">$1</code>'); text = text.replace(/^[\\-\\*] (.+)$/gm, '<li>$1</li>'); text = text.replace(/(<li>.*<\\/li>\\n?)+/gs, '<ul>$&</ul>'); text = text.replace(/^\\d+[\\.\\)] (.+)$/gm, '<li>$1</li>'); text = text.replace(/^### (.+)$/gm, '<strong style="font-size:14px;">$1</strong>'); text = text.replace(/^## (.+)$/gm, '<strong style="font-size:14px;">$1</strong>'); text = text.replace(/\\n\\n+/g, '</p><p>'); text = '<p>' + text + '</p>'; text = text.replace(/<p><\\/p>/g, ''); return text; }}
    function addMessage(role, html, sources) {{ if (role === 'user' && startersEl) {{ startersEl.style.display = 'none'; }} var msgDiv = document.createElement('div'); msgDiv.className = 'bov-chat-msg ' + role; msgDiv.innerHTML = html; messagesEl.appendChild(msgDiv); if (role === 'bot' && sources && sources.length > 0) {{ var srcDiv = document.createElement('div'); srcDiv.className = 'bov-chat-sources'; var uniqueSources = [], seen = {{}}; sources.forEach(function(s) {{ var key = s.source + ' - ' + s.page; if (!seen[key]) {{ seen[key] = true; uniqueSources.push(key); }} }}); srcDiv.innerHTML = '<span>&#128196; Sources (' + uniqueSources.length + ')</span><div class="bov-chat-sources-list">' + uniqueSources.join('<br>') + '</div>'; srcDiv.addEventListener('click', function() {{ srcDiv.classList.toggle('expanded'); }}); messagesEl.appendChild(srcDiv); }} if (role === 'bot') {{ var discDiv = document.createElement('div'); discDiv.className = 'bov-chat-disclaimer'; discDiv.textContent = DISCLAIMER; messagesEl.appendChild(discDiv); }} messagesEl.scrollTop = messagesEl.scrollHeight; }}
    function showTyping() {{ var el = document.createElement('div'); el.className = 'bov-chat-typing'; el.id = 'bovTyping'; el.innerHTML = '<span></span><span></span><span></span>'; messagesEl.appendChild(el); messagesEl.scrollTop = messagesEl.scrollHeight; }}
    function hideTyping() {{ var el = document.getElementById('bovTyping'); if (el) el.remove(); }}
    function showRateLimit() {{ inputArea.style.display = 'none'; var limitDiv = document.createElement('div'); limitDiv.className = 'bov-chat-limit-msg'; limitDiv.innerHTML = 'You have reached the question limit for this session. For more information, <a href="#contact">contact the LAAA Team</a>.'; widget.appendChild(limitDiv); }}
    function sendMessage(text) {{ text = (text || '').trim(); if (!text || isStreaming) return; if (messageCount >= MAX_MESSAGES) {{ showRateLimit(); return; }} inputEl.value = ''; addMessage('user', text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')); messageCount++; if (PRECOMPUTED[text]) {{ var pc = PRECOMPUTED[text]; history.push({{ role: 'user', content: text }}); history.push({{ role: 'assistant', content: pc.answer }}); addMessage('bot', renderMarkdown(pc.answer), pc.sources || []); return; }} isStreaming = true; sendBtn.disabled = true; showTyping(); var trimmedHistory = history.slice(-12); fetch(WORKER_URL + '/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ question: text, namespace: NAMESPACE, history: trimmedHistory }}) }}).then(function(response) {{ if (!response.ok) throw new Error('Server error: ' + response.status); hideTyping(); var reader = response.body.getReader(); var decoder = new TextDecoder(); var fullText = '', sources = []; var botDiv = document.createElement('div'); botDiv.className = 'bov-chat-msg bot'; messagesEl.appendChild(botDiv); function readStream() {{ return reader.read().then(function(result) {{ if (result.done) {{ botDiv.innerHTML = renderMarkdown(fullText); messagesEl.scrollTop = messagesEl.scrollHeight; history.push({{ role: 'user', content: text }}); history.push({{ role: 'assistant', content: fullText }}); isStreaming = false; sendBtn.disabled = false; if (sources.length > 0) {{ var srcDiv = document.createElement('div'); srcDiv.className = 'bov-chat-sources'; var uniqueSources = [], seen = {{}}; sources.forEach(function(s) {{ var key = s.source + (s.page ? ' - ' + s.page : ''); if (!seen[key]) {{ seen[key] = true; uniqueSources.push(key); }} }}); srcDiv.innerHTML = '<span>&#128196; Sources (' + uniqueSources.length + ')</span><div class="bov-chat-sources-list">' + uniqueSources.join('<br>') + '</div>'; srcDiv.addEventListener('click', function() {{ srcDiv.classList.toggle('expanded'); }}); messagesEl.appendChild(srcDiv); }} var discDiv = document.createElement('div'); discDiv.className = 'bov-chat-disclaimer'; discDiv.textContent = DISCLAIMER; messagesEl.appendChild(discDiv); return; }} var chunk = decoder.decode(result.value, {{ stream: true }}); chunk.split('\\n').forEach(function(line) {{ line = line.trim(); if (line.startsWith('data: ')) {{ var data = line.substring(6); if (data === '[DONE]') return; try {{ var parsed = JSON.parse(data); if (parsed.type === 'text') {{ fullText += parsed.content; botDiv.innerHTML = renderMarkdown(fullText) + '<span style="opacity:0.4;">&#9608;</span>'; messagesEl.scrollTop = messagesEl.scrollHeight; }} else if (parsed.type === 'sources') {{ sources = parsed.sources || []; }} else if (parsed.type === 'error') {{ fullText = 'Sorry, I encountered an error. Please try again.'; botDiv.innerHTML = renderMarkdown(fullText); }} }} catch(e) {{}} }} }}); return readStream(); }}); }} return readStream(); }}).catch(function(err) {{ hideTyping(); addMessage('bot', 'Sorry, I could not reach the server. Please try again in a moment.'); isStreaming = false; sendBtn.disabled = false; console.error('BOV Chat error:', err); }}); }}
}})();
</script>
"""


# ============================================================
# RAG CHATBOT
# ============================================================
if ENABLE_CHATBOT:
    try:
        from rag_pipeline import (
            run_rag_pipeline, generate_chat_widget, capture_build_context
        )

        build_data = {
            "property_name": "500 N Alexandria Ave, Los Angeles, CA 90004",
            "list_price": LIST_PRICE,
            "units": UNITS,
            "sf": SF,
            "rent_roll": RENT_ROLL,
            "sale_comps": SALE_COMPS,
            "financial_summary": (
                f"Property: 500 N Alexandria Ave, Los Angeles, CA 90004\n"
                f"List Price: ${LIST_PRICE:,.0f}\n"
                f"Units: {UNITS}\n"
                f"Square Footage: {SF:,.0f} SF\n"
                f"Lot Size: 0.10 Acres\n"
                f"Year Built: 1923/1929\n"
                f"Gross Scheduled Rent (Current): ${GSR:,.0f}\n"
                f"Gross Scheduled Rent (Pro Forma): ${PF_GSR:,.0f}\n"
                f"Vacancy: {VACANCY_PCT*100:.0f}%\n"
                f"Current NOI: ${CUR_NOI_AT_LIST:,.0f}\n"
                f"Pro Forma NOI: ${PF_NOI_AT_LIST:,.0f}\n"
                f"Current Cap Rate at List: {AT_LIST['cur_cap']:.2f}%\n"
                f"Pro Forma Cap Rate at List: {AT_LIST['pf_cap']:.2f}%\n"
                f"GRM: {AT_LIST['grm']:.2f}x\n"
                f"Price Per Unit: ${LIST_PRICE // UNITS:,.0f}\n"
                f"Price Per SF: ${LIST_PRICE / SF:,.0f}\n"
            ),
            "operating_statement": (
                f"Operating Statement at List Price ${LIST_PRICE:,.0f}:\n"
                f"Gross Scheduled Rent: ${GSR:,.0f}\n"
                f"Less Vacancy (5%): -${GSR * VACANCY_PCT:,.0f}\n"
                f"Other Income: ${OTHER_INCOME:,.0f}\n"
                f"Effective Gross Income: ${CUR_EGI:,.0f}\n"
                f"Real Estate Taxes: ${TAXES_AT_LIST:,.0f}\n"
                f"Insurance: $6,300\n"
                f"Water / Sewer: $5,500\n"
                f"Trash: $2,800\n"
                f"Common Area Electric: $1,500\n"
                f"Repairs & Maintenance: $9,100\n"
                f"Contract Services: $1,500\n"
                f"Administrative: $1,000\n"
                f"Marketing: $500\n"
                f"Management Fee: $18,000\n"
                f"Reserves: $2,450\n"
                f"LAHD Registration: $303\n"
                f"Other: $250\n"
                f"Total Expenses: ${CUR_TOTAL_EXP:,.0f}\n"
                f"Net Operating Income: ${CUR_NOI_AT_LIST:,.0f}\n"
            ),
            "sections": {},
        }

        docs_dir = os.path.join(SCRIPT_DIR, "docs")
        chunks, vectors = run_rag_pipeline(
            docs_dir=docs_dir,
            namespace=BOV_NAMESPACE,
            build_data=build_data,
            verbose=True,
        )

        chat_html = generate_chat_widget(
            worker_url=CHAT_WORKER_URL,
            namespace=BOV_NAMESPACE,
            property_name=PROPERTY_DISPLAY_NAME,
            starter_questions=STARTER_QUESTIONS,
        )
        html_parts.append(chat_html)
        print(f"Chat widget injected for namespace: {BOV_NAMESPACE}")

    except ImportError as e:
        print(f"\nWARNING: RAG dependencies not installed ({e}).")
        print("Injecting standalone chat widget (no RAG pipeline). Install deps for full RAG: pip install -r requirements.txt")
        html_parts.append(_fallback_chat_widget())
    except Exception as e:
        print(f"\nWARNING: RAG pipeline failed ({e}).")
        print("Injecting standalone chat widget. Check your .env API keys for full RAG.")
        html_parts.append(_fallback_chat_widget())

# Close the HTML document
html_parts.append("</body></html>")

# Write output
html = "".join(html_parts)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nBOV generated: {OUTPUT}")
print(f"File size: {os.path.getsize(OUTPUT) / 1024 / 1024:.2f} MB")
print("Done!")
