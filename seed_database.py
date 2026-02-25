#!/usr/bin/env python3
"""Seed script for GreenLeaf Property Management — a small landlord managing 12 multi-unit buildings in Austin, TX.
Generates SQLite with properties, units, tenants, leases, payments, maintenance requests, emails.
"""
import sqlite3
import random
import os
import json
from datetime import datetime, timedelta, date

random.seed(42)
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "propertymanager.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT 'Austin',
    state TEXT NOT NULL DEFAULT 'TX',
    zip TEXT NOT NULL,
    year_built INTEGER,
    total_units INTEGER NOT NULL,
    parking_spots INTEGER,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    unit_number TEXT NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms REAL NOT NULL,
    sqft INTEGER NOT NULL,
    rent_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'occupied',
    notes TEXT,
    UNIQUE(property_id, unit_number)
);
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    unit_id INTEGER REFERENCES units(id),
    lease_start TEXT NOT NULL,
    lease_end TEXT NOT NULL,
    rent_amount REAL NOT NULL,
    security_deposit REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    employer TEXT,
    annual_income REAL,
    ssn_last_four TEXT,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    unit_id INTEGER NOT NULL REFERENCES units(id),
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    paid_date TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    payment_method TEXT,
    late_fee REAL DEFAULT 0,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS maintenance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_number TEXT UNIQUE NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES units(id),
    tenant_id INTEGER REFERENCES tenants(id),
    category TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal',
    status TEXT NOT NULL DEFAULT 'open',
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    submitted_date TEXT NOT NULL,
    scheduled_date TEXT,
    completed_date TEXT,
    contractor_name TEXT,
    contractor_phone TEXT,
    estimated_cost REAL,
    actual_cost REAL,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL DEFAULT 'manager@greenleafproperties.example.com',
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    received_at TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    replied INTEGER DEFAULT 0,
    reply_body TEXT,
    tenant_id INTEGER REFERENCES tenants(id),
    property_id INTEGER REFERENCES properties(id)
);
CREATE TABLE IF NOT EXISTS rental_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_name TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    applicant_phone TEXT,
    desired_unit_id INTEGER REFERENCES units(id),
    current_address TEXT,
    employer TEXT,
    annual_income REAL,
    credit_score INTEGER,
    has_pets INTEGER DEFAULT 0,
    pet_details TEXT,
    move_in_date TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    submitted_date TEXT NOT NULL,
    notes TEXT
);
"""

# ──────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────
PROPERTY_NAMES = [
    ("Riverside Commons", "4210 Riverside Dr", "78741", 1985, 6, 12),
    ("Oak Hill Apartments", "7830 W Hwy 290", "78736", 1992, 4, 8),
    ("East Side Flats", "1105 E Cesar Chavez St", "78702", 2005, 7, 14),
    ("Mueller Park Residences", "4520 Mueller Blvd", "78723", 2012, 5, 10),
    ("South Lamar Place", "3340 S Lamar Blvd", "78704", 1978, 4, 8),
    ("North Loop Lofts", "915 E North Loop Blvd", "78751", 2001, 3, 6),
    ("Barton Creek Villas", "2800 Barton Creek Blvd", "78735", 2008, 6, 12),
    ("Zilker Edge", "1600 Toomey Rd", "78704", 2015, 5, 10),
    ("Manor Road Studios", "2210 Manor Rd", "78722", 1990, 3, 4),
    ("Crestview Terrace", "7405 Burnet Rd", "78757", 1988, 5, 10),
    ("Domain Heights", "11200 Domain Dr", "78758", 2018, 7, 14),
    ("Bouldin Bungalows", "800 W Mary St", "78704", 1960, 4, 6),
]

# 100 unique first+last combos for tenants + applicants
FIRST_NAMES = [
    "Marcus","Olivia","Ethan","Sophia","Liam","Isabella","Noah","Mia","James","Charlotte",
    "Benjamin","Amelia","Lucas","Harper","Henry","Evelyn","Alexander","Abigail","Daniel","Emily",
    "Michael","Ella","William","Avery","David","Scarlett","Joseph","Grace","Samuel","Chloe",
    "Andrew","Victoria","Ryan","Riley","Tyler","Aria","Nathan","Zoey","Kyle","Nora",
    "Brandon","Lily","Aaron","Eleanor","Justin","Hannah","Kevin","Stella","Sean","Aurora",
    "Derek","Savannah","Patrick","Audrey","Jesse","Brooklyn","Carlos","Leah","Diego","Autumn",
    "Rafael","Genesis","Omar","Clara","Malik","Maya","Andre","Naomi","Jerome","Iris",
    "Trevor","Piper","Caleb","Ruby","Miles","Violet","Gavin","Hazel","Wyatt","Jade",
]
LAST_NAMES = [
    "Whitfield","Sorensen","Castellano","Houghton","Fairbanks","Pemberton","Galloway","Strickland",
    "Beaumont","Lockhart","Ashworth","Pendleton","Rutherford","Montague","Hargrove","Eastwood",
    "Kingsley","Cromwell","Waverly","Bancroft","Thornton","Caldwell","Prescott","Whitmore",
    "Langford","Buckley","Davenport","Mercer","Ellsworth","Hensley","Stratton","Ashford",
    "Holbrook","Winslow","Kensington","Blackwood","Ravensdale","Hartwell","Crestwood","Dunmore",
    "Fairchild","Westbrook","Sinclair","Aldridge","Foxworth","Norwood","Brookhaven","Worthington",
    "Stanfield","Carrington","Hathaway","Elmsford","Greenfield","Sutherland","Ridgewood","Marlowe",
    "Barrington","Pembroke","Clearwater","Oakridge","Bellingham","Townsend","Crawford","Montclair",
    "Haverford","Manning","Fitzgerald","Delacroix","Kimura","Okafor","Petrov","Sandoval",
    "Reeves","Donovan","Chambers","Hastings","Navarro","Park","Volkov","Andersen",
]

EMAIL_DOMAINS = ["example.com", "example.net", "example.org", "mail.example.com", "inbox.example.com"]
EMPLOYERS = [
    "Dell Technologies", "Tesla Austin", "University of Texas", "St. David's Medical Center",
    "Austin ISD", "Whole Foods HQ", "Indeed Austin", "National Instruments", "Cirrus Logic",
    "Self-employed", "Freelance", "H-E-B Corporate", "City of Austin", "State of Texas",
    "Samsung Austin Semiconductor", "Apple Austin", "Google Austin", "Meta Austin",
    "Oracle Austin", "Retired", None, "Between jobs",
]
CONTRACTORS = [
    ("Mike's Plumbing", "+1-512-555-8821", "mike@mikesplumbing.example.com"),
    ("Austin HVAC Pros", "+1-512-555-9932", "service@austinhvac.example.com"),
    ("Lone Star Electric", "+1-512-555-7714", "jobs@lonestarelectric.example.com"),
    ("Hill Country Pest Control", "+1-512-555-6203", "dispatch@hcpest.example.com"),
    ("Capital City Appliance Repair", "+1-512-555-4455", "repairs@capcityappliance.example.com"),
    ("ATX Handyman Services", "+1-512-555-3378", "booking@atxhandyman.example.com"),
    ("Roofing Solutions Austin", "+1-512-555-2290", "quotes@roofingaustin.example.com"),
    ("Green Clean Janitorial", "+1-512-555-1167", "schedule@greenclean.example.com"),
]

# Landlord vs Tenant responsibility
LANDLORD_RESPONSIBILITY = [
    "plumbing", "electrical", "hvac", "structural", "pest_control", "locksmith",
    "water_heater", "roof", "exterior", "common_areas", "smoke_detectors"
]
TENANT_RESPONSIBILITY = [
    "lightbulbs", "clogged_drain_hair", "minor_cleaning", "air_filter_replacement",
    "garbage_disposal_jammed_by_tenant", "broken_blinds_by_tenant", "lost_keys",
    "damage_caused_by_tenant_or_guests", "pest_due_to_cleanliness"
]
MAINT_CATEGORIES = ["plumbing", "electrical", "hvac", "appliance", "pest_control", "structural", "locksmith", "general"]
GREETINGS = ["Hi,", "Hello,", "Hey,", "Hi there,", "Good morning,", "Good afternoon,"]
SIGNOFFS = ["Thanks,", "Best,", "Thank you,", "Regards,", "Thanks!",  "Appreciate it,"]

def rand_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def rand_phone():
    return f"+1-512-{random.randint(200,999)}-{random.randint(1000,9999)}"

def make_email(first, last):
    domain = random.choice(EMAIL_DOMAINS)
    return random.choice([
        f"{first.lower()}.{last.lower()}@{domain}",
        f"{first.lower()}_{last.lower()}@{domain}",
        f"{first[0].lower()}.{last.lower()}@{domain}",
    ])

# ──────────────────────────────────────────────
# SEED FUNCTIONS
# ──────────────────────────────────────────────
def seed_properties(cur):
    for name, addr, zipcode, year, num_units, parking in PROPERTY_NAMES:
        cur.execute("INSERT INTO properties (name,address,city,state,zip,year_built,total_units,parking_spots) VALUES (?,?,?,?,?,?,?,?)",
            (name, addr, "Austin", "TX", zipcode, year, num_units, parking))
    return len(PROPERTY_NAMES)

def seed_units(cur):
    cur.execute("SELECT id, total_units, name FROM properties")
    props = cur.fetchall()
    count = 0
    for pid, total, pname in props:
        for u in range(1, total + 1):
            unit_num = f"{random.randint(1,4)}{u:02d}" if total > 4 else f"{u}"
            beds = random.choices([0, 1, 2, 3], weights=[10, 40, 35, 15])[0]
            baths = 1.0 if beds <= 1 else random.choice([1.0, 1.5, 2.0])
            sqft = {0: random.randint(350, 550), 1: random.randint(550, 800),
                    2: random.randint(800, 1200), 3: random.randint(1100, 1600)}[beds]
            rent = round({0: random.uniform(900, 1300), 1: random.uniform(1200, 1800),
                         2: random.uniform(1600, 2500), 3: random.uniform(2200, 3200)}[beds] / 50) * 50
            # Most occupied, some vacant
            status = random.choices(["occupied", "occupied", "occupied", "vacant", "vacant", "renovating"], weights=[50, 25, 15, 5, 3, 2])[0]
            notes = ""
            if status == "renovating":
                notes = f"Kitchen remodel in progress. Expected completion {(datetime.now() + timedelta(days=random.randint(14,45))).strftime('%Y-%m-%d')}."
            elif status == "vacant":
                notes = f"Vacant since {(datetime.now() - timedelta(days=random.randint(5,60))).strftime('%Y-%m-%d')}. Listed on Zillow and Apartments.com."
            cur.execute("INSERT INTO units (property_id,unit_number,bedrooms,bathrooms,sqft,rent_amount,status,notes) VALUES (?,?,?,?,?,?,?,?)",
                (pid, unit_num, beds, baths, sqft, rent, status, notes or None))
            count += 1
    return count

def seed_tenants(cur):
    cur.execute("SELECT id, rent_amount, property_id, unit_number FROM units WHERE status='occupied'")
    occupied = cur.fetchall()
    used_names = set()
    used_emails = set()
    name_idx = 0
    tenants_created = 0

    for uid, rent, pid, unum in occupied:
        # Pick unique name
        while True:
            first = FIRST_NAMES[name_idx % len(FIRST_NAMES)]
            last = LAST_NAMES[(name_idx * 3 + 7) % len(LAST_NAMES)]
            name_idx += 1
            key = f"{first} {last}"
            if key not in used_names:
                used_names.add(key)
                break

        email = make_email(first, last)
        while email in used_emails:
            email = f"{first.lower()}{random.randint(10,99)}@{random.choice(EMAIL_DOMAINS)}"
        used_emails.add(email)

        lease_start = rand_date(datetime(2024, 1, 1), datetime(2025, 10, 1))
        lease_end = lease_start + timedelta(days=random.choice([365, 365, 365, 180, 730]))
        deposit = rent
        employer = random.choice(EMPLOYERS)
        income = round(rent * 12 * random.uniform(2.0, 4.5) / 1000) * 1000 if employer and employer not in ("Retired", "Between jobs", None) else None

        # A few problem tenants
        status = "active"
        notes = None
        if tenants_created == 5:
            notes = "Chronic late payer. 3 late payments in last 6 months."
        elif tenants_created == 12:
            notes = "Noise complaints from neighbors. Written warning issued 2025-11-15."
        elif tenants_created == 18:
            notes = "Unauthorized pet discovered during inspection. Lease violation pending."
        elif tenants_created == 25:
            notes = "Lease expired, currently month-to-month. Has been asked to sign renewal."
            status = "month_to_month"
        elif tenants_created == 30:
            notes = "Gave 30-day notice on 2026-02-01. Moving out March 3rd."
            status = "notice_given"
        elif tenants_created == 8:
            notes = "VIP tenant — always pays early, refers new tenants. Renewed twice."

        ssn_last = f"{random.randint(1000,9999)}"
        ec_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

        cur.execute("""INSERT INTO tenants (first_name,last_name,email,phone,unit_id,lease_start,lease_end,
            rent_amount,security_deposit,status,emergency_contact_name,emergency_contact_phone,
            employer,annual_income,ssn_last_four,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (first, last, email, rand_phone(), uid,
             lease_start.strftime("%Y-%m-%d"), lease_end.strftime("%Y-%m-%d"),
             rent, deposit, status, ec_name, rand_phone(),
             employer, income, ssn_last, notes))
        tenants_created += 1
    return tenants_created

def seed_payments(cur):
    cur.execute("SELECT id, unit_id, rent_amount, lease_start FROM tenants WHERE status IN ('active','month_to_month','notice_given')")
    tenants = cur.fetchall()
    count = 0
    today = datetime(2026, 2, 24)

    for tid, uid, rent, lease_start_str in tenants:
        lease_start = datetime.strptime(lease_start_str, "%Y-%m-%d")
        # Generate monthly payments from max(lease_start, 6 months ago) to now
        start_month = max(lease_start, today - timedelta(days=180))
        current = datetime(start_month.year, start_month.month, 1)

        while current <= today:
            due = current.strftime("%Y-%m-%d")
            # Most pay on time, some late, very few past due
            r = random.random()
            if r < 0.78:
                paid = (current + timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d")
                status = "paid"
                late_fee = 0
            elif r < 0.92:
                paid = (current + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d")
                status = "paid_late"
                late_fee = 75.0
            elif r < 0.97:
                paid = (current + timedelta(days=random.randint(16, 28))).strftime("%Y-%m-%d")
                status = "paid_late"
                late_fee = 75.0
            else:
                paid = None
                status = "past_due"
                late_fee = 75.0 if current.day <= 15 else 150.0

            # Future months should be pending
            if current >= datetime(today.year, today.month, 1):
                if status == "past_due" and current.month == today.month:
                    pass  # Keep as past due for current month
                elif current > today:
                    status = "pending"
                    paid = None
                    late_fee = 0

            method = random.choice(["bank_transfer", "check", "online_portal", "venmo", "zelle"]) if paid else None

            cur.execute("INSERT INTO payments (tenant_id,unit_id,amount,due_date,paid_date,status,payment_method,late_fee) VALUES (?,?,?,?,?,?,?,?)",
                (tid, uid, rent, due, paid, status, method, late_fee))
            count += 1
            # Next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
    return count

def seed_maintenance(cur):
    cur.execute("SELECT t.id, t.first_name, t.last_name, t.unit_id, u.property_id, u.unit_number, p.name FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id")
    tenants = cur.fetchall()
    count = 0

    titles_by_cat = {
        "plumbing": ["Leaking faucet in kitchen", "Toilet won't stop running", "Clogged shower drain", "Water heater not working", "Pipe burst under sink", "Low water pressure in bathroom"],
        "electrical": ["Outlet not working in bedroom", "Light fixture flickering", "Breaker keeps tripping", "Smoke detector beeping", "No power in half the apartment"],
        "hvac": ["AC not cooling", "Heater making loud noise", "Thermostat not responding", "AC leaking water inside", "Weird smell from vents"],
        "appliance": ["Dishwasher not draining", "Fridge stopped cooling", "Oven won't heat up", "Washer leaking", "Garbage disposal jammed"],
        "pest_control": ["Ants in kitchen", "Cockroaches spotted", "Mouse in the walls", "Wasps nest on balcony"],
        "structural": ["Crack in bathroom wall", "Window won't close properly", "Door frame warped", "Ceiling stain — possible leak above"],
        "locksmith": ["Lost apartment key", "Deadbolt not locking properly", "Need lock changed — safety concern"],
        "general": ["Paint peeling in hallway", "Carpet stain won't come out", "Mailbox lock broken", "Parking lot pothole"],
    }

    for _ in range(45):
        tid, first, last, uid, pid, unum, pname = random.choice(tenants)
        cat = random.choice(MAINT_CATEGORIES)
        title = random.choice(titles_by_cat[cat])
        priority = random.choices(["low", "normal", "high", "urgent"], weights=[15, 50, 25, 10])[0]
        status = random.choices(["open", "open", "in_progress", "scheduled", "completed", "completed"], weights=[25, 15, 20, 15, 15, 10])[0]

        submitted = rand_date(datetime(2025, 10, 1), datetime(2026, 2, 24))
        scheduled = (submitted + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d") if status in ("scheduled", "in_progress", "completed") else None
        completed = (submitted + timedelta(days=random.randint(2, 14))).strftime("%Y-%m-%d") if status == "completed" else None

        contractor = random.choice(CONTRACTORS) if status != "open" else (None, None, None)
        est_cost = round(random.uniform(75, 2500) / 25) * 25 if cat in ("plumbing", "hvac", "electrical", "structural") else round(random.uniform(50, 500) / 25) * 25
        actual_cost = round(est_cost * random.uniform(0.8, 1.4) / 25) * 25 if status == "completed" else None

        desc = f"{title}. Reported by {first} {last} in unit {unum} at {pname}."
        if priority == "urgent":
            desc += " URGENT — tenant says this is an emergency."

        rnum = f"MR-{2000 + count}"
        cur.execute("""INSERT INTO maintenance_requests (request_number,unit_id,tenant_id,category,priority,status,
            title,description,submitted_date,scheduled_date,completed_date,contractor_name,contractor_phone,
            estimated_cost,actual_cost) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rnum, uid, tid, cat, priority, status, title, desc,
             submitted.strftime("%Y-%m-%d"), scheduled, completed,
             contractor[0], contractor[1], est_cost, actual_cost))
        count += 1
    return count

def seed_applications(cur):
    cur.execute("SELECT u.id, u.unit_number, u.rent_amount, u.bedrooms, p.name FROM units u JOIN properties p ON u.property_id=p.id WHERE u.status='vacant'")
    vacant = cur.fetchall()
    count = 0
    name_offset = 60  # Start after tenant names

    for uid, unum, rent, beds, pname in vacant:
        # 2-4 applicants per vacant unit
        for _ in range(random.randint(2, 4)):
            first = FIRST_NAMES[(name_offset + count) % len(FIRST_NAMES)]
            last = LAST_NAMES[(name_offset + count * 3) % len(LAST_NAMES)]
            email = make_email(first, last)
            income = round(rent * 12 * random.uniform(1.5, 5.0) / 1000) * 1000
            credit = random.randint(550, 820)
            has_pets = 1 if random.random() < 0.3 else 0
            pet_details = random.choice(["Small dog, 15 lbs", "Two cats", "Golden retriever, 70 lbs", "Emotional support animal — cat"]) if has_pets else None
            move_in = (datetime.now() + timedelta(days=random.randint(7, 45))).strftime("%Y-%m-%d")
            status = random.choices(["pending", "pending", "under_review", "approved", "rejected"], weights=[30, 20, 25, 15, 10])[0]
            submitted = rand_date(datetime(2026, 1, 15), datetime(2026, 2, 24))

            notes = None
            if credit < 600:
                notes = "Low credit score — may need co-signer or larger deposit."
            elif income < rent * 12 * 2:
                notes = "Income below 2x annual rent threshold."

            cur.execute("""INSERT INTO rental_applications (applicant_name,applicant_email,applicant_phone,
                desired_unit_id,current_address,employer,annual_income,credit_score,has_pets,pet_details,
                move_in_date,status,submitted_date,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (f"{first} {last}", email, rand_phone(), uid,
                 f"{random.randint(100,9999)} {random.choice(['Main St','Oak Ave','Elm St','Cedar Ln','Park Ave'])}, Austin, TX",
                 random.choice(EMPLOYERS[:18]), income, credit, has_pets, pet_details,
                 move_in, status, submitted.strftime("%Y-%m-%d"), notes))
            count += 1
    return count

def seed_emails(cur):
    cur.execute("""SELECT t.id, t.first_name, t.last_name, t.email, t.unit_id, t.rent_amount,
                   u.unit_number, u.property_id, p.name as prop_name
                   FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id""")
    tenants = cur.fetchall()

    # Check who has past due payments
    cur.execute("SELECT tenant_id, COUNT(*) FROM payments WHERE status='past_due' GROUP BY tenant_id")
    past_due = dict(cur.fetchall())

    # Get maintenance requests
    cur.execute("SELECT tenant_id, title, status, request_number FROM maintenance_requests")
    maint_by_tenant = {}
    for tid, title, mstatus, rnum in cur.fetchall():
        maint_by_tenant.setdefault(tid, []).append({"title": title, "status": mstatus, "rnum": rnum})

    emails = []

    for tid, first, last, temail, uid, rent, unum, pid, pname in tenants:
        name = f"{first} {last}"
        g = random.choice(GREETINGS)
        s = random.choice(SIGNOFFS)

        # Tenant-specific emails based on their situation
        if tid in past_due:
            emails.append((temail, f"Re: Late rent — Unit {unum}",
                f"{g}\n\nI know my rent is overdue and I apologize. I had an unexpected medical expense this month. Can I set up a payment plan to catch up? I can pay half now and the rest by the 15th.\n\n{s}\n{name}",
                tid, pid))

        if tid in maint_by_tenant:
            mr = random.choice(maint_by_tenant[tid])
            if mr["status"] == "open":
                emails.append((temail, f"Follow up on {mr['rnum']} — {mr['title']}",
                    f"{g}\n\nI submitted a maintenance request ({mr['rnum']}) for {mr['title'].lower()} and haven't heard back yet. This is getting worse. When can someone come look at it?\n\n{s}\n{name}",
                    tid, pid))

        # Random general emails
        r = random.random()
        if r < 0.15:
            emails.append((temail, f"Noise complaint — {pname}",
                f"{g}\n\nThe tenant {'above' if random.random()>0.5 else 'next to'} me has been extremely loud {'late at night' if random.random()>0.5 else 'every weekend'}. {'Music blasting until 2am' if random.random()>0.5 else 'Sounds like they are having a party every night'}. I've tried knocking on their door but they don't answer. Can you please address this?\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.25:
            emails.append((temail, f"Lease renewal question — Unit {unum}",
                f"{g}\n\nMy lease is coming up {'next month' if random.random()>0.5 else 'in a couple months'} and I wanted to ask about renewal. {'Will my rent go up?' if random.random()>0.5 else 'I\u2019d like to switch to a month-to-month if possible.'} I\u2019ve been here {'two years' if random.random()>0.5 else 'since last year'} and really like the place.\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.33:
            emails.append((temail, f"Guest parking question",
                f"{g}\n\nI\u2019m having family visit this weekend. Is there guest parking available at {pname}? If so, do they need a pass or can they just park in the visitor spots?\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.40:
            emails.append((temail, f"Lock change request — Unit {unum}",
                f"{g}\n\nI\u2019d like to get my locks changed. {'I lost my keys.' if random.random()>0.5 else 'My ex still has a copy of the key and I\u2019d feel safer with new locks.'} How do I arrange this and what\u2019s the cost?\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.47:
            emails.append((temail, f"Pet request — Unit {unum}",
                f"{g}\n\nI know the lease says no pets, but I was wondering if there\u2019s any way to get approval for a {'small dog (under 20 lbs)' if random.random()>0.5 else 'cat'}? {'I\u2019d be willing to pay a pet deposit.' if random.random()>0.5 else 'It\u2019s actually an emotional support animal \u2014 I have a letter from my therapist.'}\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.53:
            emails.append((temail, f"Subletting question — Unit {unum}",
                f"{g}\n\nI need to travel for work for {'3 months' if random.random()>0.5 else '6 weeks'} and was wondering if I can sublet my apartment while I\u2019m away? I have a friend who\u2019d be interested. What\u2019s the policy on this?\n\n{s}\n{name}",
                tid, pid))
        elif r < 0.58:
            emails.append((temail, f"Package theft at {pname}",
                f"{g}\n\nI\u2019ve had {'two packages' if random.random()>0.5 else 'a package'} stolen from the front entrance this month. {'Can we get a package locker installed?' if random.random()>0.5 else 'Is there security camera footage we can check?'} This is really frustrating.\n\n{s}\n{name}",
                tid, pid))

    # Contractor emails
    for contractor_name, contractor_phone, cemail in CONTRACTORS[:4]:
        emails.append((cemail, f"Quote for upcoming work",
            f"Hi,\n\nHere\u2019s the estimate for the work we discussed:\n\n- Labor: ${random.randint(200,800)}\n- Parts: ${random.randint(50,400)}\n- Total: ${random.randint(300,1200)}\n\nWe can schedule for {'next Tuesday' if random.random()>0.5 else 'this Thursday'}. Let me know.\n\n{contractor_name}",
            None, random.randint(1, 12)))

    # External/prospective tenant emails
    for _ in range(10):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        femail = make_email(first, last)
        name = f"{first} {last}"
        beds = random.choice([1, 2, 3])
        emails.append((femail, f"Inquiry about {beds}BR availability",
            f"{g}\n\nI saw your listing and I\u2019m interested in a {beds}-bedroom apartment. What\u2019s available and what\u2019s the rent range? I\u2019m looking to move in {'by March 1st' if random.random()>0.5 else 'within the next month'}. {'I have a small dog \u2014 is that OK?' if random.random()<0.3 else ''}\n\n{s}\n{name}",
            None, None))

    # Shuffle and insert
    random.shuffle(emails)
    count = 0
    for from_addr, subj, body, tenant_id, prop_id in emails:
        received = rand_date(datetime(2026, 1, 15), datetime(2026, 2, 24))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id,property_id) VALUES (?,?,?,?,?,0,?,?)",
            (from_addr, "manager@greenleafproperties.example.com", subj, body,
             received.strftime("%Y-%m-%d %H:%M:%S"), tenant_id, prop_id))
        count += 1
    return count

def seed_sent_emails(cur):
    """Add sent emails showing landlord's past replies to tenants and contractors."""
    cur.execute("SELECT t.id, t.first_name, t.last_name, t.email, u.unit_number, p.name FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id ORDER BY RANDOM() LIMIT 15")
    tenants = cur.fetchall()

    sent = []
    mgr = "manager@greenleafproperties.example.com"

    # Replies to tenants
    for tid, first, last, temail, unum, pname in tenants[:8]:
        r = random.random()
        if r < 0.25:
            sent.append((mgr, temail, f"Re: Late rent \u2014 Unit {unum}",
                f"Hi {first},\n\nThanks for letting me know. I understand things come up. Please get the payment in by the 15th to avoid the additional late fee. If you need to discuss a payment plan, let me know and we can work something out.\n\nBest,\nGreenLeaf Management",
                tid, None))
        elif r < 0.5:
            sent.append((mgr, temail, f"Re: Maintenance request \u2014 Unit {unum}",
                f"Hi {first},\n\nThanks for reporting this. I\u2019ve assigned a contractor and they should be out within the next 2-3 business days. They\u2019ll call you to schedule a time. Please make sure someone is home or leave a key with the office.\n\nThanks,\nGreenLeaf Management",
                tid, None))
        elif r < 0.75:
            sent.append((mgr, temail, f"Lease renewal \u2014 Unit {unum} at {pname}",
                f"Hi {first},\n\nYour lease is coming up for renewal. I\u2019d love to have you stay! Your new rate would be ${int(random.uniform(1200,2800))}/month for another 12 months. Let me know if you\u2019d like to renew or if you have any questions.\n\nBest,\nGreenLeaf Management",
                tid, None))
        else:
            sent.append((mgr, temail, f"Move-out instructions \u2014 Unit {unum}",
                f"Hi {first},\n\nPer your 30-day notice, your move-out date is scheduled. Please make sure the unit is cleaned, all personal belongings removed, and keys returned to the office. We\u2019ll do a walk-through inspection within 3 days of move-out. Your security deposit will be returned within 30 days minus any damages.\n\nThanks,\nGreenLeaf Management",
                tid, None))

    # Emails to contractors
    for cname, cphone, cemail in CONTRACTORS[:5]:
        mr_num = f"MR-{random.randint(2000,2044)}"
        prop = random.choice(PROPERTY_NAMES)
        short_name = cname.split(" ")[0]
        specialty = "plumbing" if "Plumb" in cname else "HVAC" if "HVAC" in cname else "electrical" if "Electric" in cname else "maintenance"
        timing = "yesterday" if random.random() > 0.5 else "earlier this week"
        sched = "tomorrow" if random.random() > 0.5 else "this week"
        sent.append((mgr, cemail, f"Work request \u2014 {mr_num} at {prop[0]}",
            f"Hi {short_name} team,\n\nWe have a {specialty} issue at {prop[0]} ({prop[1]}). Tenant reported it {timing}.\n\nCan you send someone out {sched}? Please call the tenant to schedule access. Their number is on file.\n\nThanks,\nGreenLeaf Management",
            None, None))

    # Insert as sent (from manager, is_read=1 since they're our own)
    for from_addr, to_addr, subj, body, tid, pid in sent:
        received = rand_date(datetime(2026, 1, 1), datetime(2026, 2, 20))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id,property_id) VALUES (?,?,?,?,?,1,?,?)",
            (from_addr, to_addr, subj, body, received.strftime("%Y-%m-%d %H:%M:%S"), tid, pid))
    return len(sent)

def seed_new_maintenance_emails(cur):
    """Legitimate new maintenance requests that ARE the landlord's responsibility."""
    cur.execute("SELECT t.id, t.first_name, t.last_name, t.email, u.unit_number, p.name FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id ORDER BY RANDOM() LIMIT 8")
    tenants = cur.fetchall()

    legit_requests = [
        ("Hot water not working — Unit {unum}",
         "{g}\n\nI have no hot water as of this morning. The water heater seems completely dead — no pilot light, nothing. I have a baby at home and really need this fixed today if possible.\n\n{s}\n{name}",
         "plumbing", "urgent"),
        ("Toilet leaking at base — Unit {unum}",
         "{g}\n\nMy toilet is leaking water from the base every time I flush. I\u2019ve put towels around it but the floor is getting damaged. Can you send a plumber?\n\n{s}\n{name}",
         "plumbing", "high"),
        ("AC stopped working — Unit {unum}",
         "{g}\n\nMy AC unit stopped blowing cold air yesterday. It\u2019s running but just blowing warm air. With this Austin heat, it\u2019s getting really uncomfortable in here. Can someone come look at it?\n\n{s}\n{name}",
         "hvac", "high"),
        ("Smoke detector keeps going off — Unit {unum}",
         "{g}\n\nThe smoke detector in my hallway keeps going off randomly — no smoke, no cooking, it just beeps for about 30 seconds then stops. It happened 4 times last night. I think it might be a wiring issue since it\u2019s hardwired.\n\n{s}\n{name}",
         "electrical", "normal"),
        ("Cockroach problem getting worse — Unit {unum}",
         "{g}\n\nI\u2019ve been seeing more and more cockroaches in my kitchen over the past two weeks. I keep my apartment clean and I\u2019ve tried store-bought sprays but they keep coming back. I think they\u2019re coming from somewhere in the walls. Can you send pest control?\n\n{s}\n{name}",
         "pest_control", "normal"),
        ("Front door lock is broken — Unit {unum}",
         "{g}\n\nThe deadbolt on my front door is jammed — I can\u2019t lock it from inside or outside. I had to prop a chair against the door last night. This is a safety issue, I need a locksmith ASAP.\n\n{s}\n{name}",
         "locksmith", "urgent"),
        ("Kitchen faucet dripping constantly — Unit {unum}",
         "{g}\n\nMy kitchen faucet has been dripping non-stop for about a week. It\u2019s not a huge flow but it\u2019s constant and my water bill is going to be crazy. Can someone come fix it?\n\n{s}\n{name}",
         "plumbing", "normal"),
        ("Outlet sparking in bedroom — Unit {unum}",
         "{g}\n\nWhen I plugged in my phone charger last night, the bedroom outlet sparked and now it\u2019s not working. I\u2019m nervous about using it. The outlet cover also feels warm to the touch. Can you send an electrician?\n\n{s}\n{name}",
         "electrical", "urgent"),
    ]

    count = 0
    for i, (tid, first, last, email, unum, pname) in enumerate(tenants):
        subj_tpl, body_tpl, category, priority = legit_requests[i]
        name = f"{first} {last}"
        subj = subj_tpl.format(unum=unum)
        body = body_tpl.format(g=random.choice(GREETINGS), s=random.choice(SIGNOFFS), name=name)

        received = rand_date(datetime(2026, 2, 15), datetime(2026, 2, 24))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id) VALUES (?,?,?,?,?,0,?)",
            (email, "manager@greenleafproperties.example.com", subj, body,
             received.strftime("%Y-%m-%d %H:%M:%S"), tid))
        count += 1
    return count

def seed_responsibility_mismatch_emails(cur):
    """Emails where tenant claims something is landlord's responsibility but it's actually theirs."""
    cur.execute("SELECT t.id, t.first_name, t.last_name, t.email, u.unit_number, p.name FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id ORDER BY RANDOM() LIMIT 8")
    tenants = cur.fetchall()
    g = random.choice(GREETINGS)
    mm = []

    templates = [
        ("Lightbulbs out in my unit",
         "{g}\n\nSeveral lightbulbs have burned out in my apartment \u2014 kitchen, bathroom, and the hallway. I need someone to come replace them ASAP. It\u2019s a safety hazard.\n\n{s}\n{name}",
         "Lightbulb replacement is TENANT responsibility per lease. Landlord only handles common area lighting."),
        ("Drain is clogged",
         "{g}\n\nMy bathroom drain is completely clogged and water is backing up. This needs to be fixed immediately. Send a plumber.\n\n{s}\n{name}",
         "Drain clog caused by hair/tenant use is TENANT responsibility. Only structural plumbing issues are landlord\u2019s."),
        ("Air filter needs changing",
         "{g}\n\nThe air filter in my HVAC unit is filthy and it\u2019s affecting the air quality. I shouldn\u2019t have to breathe this. When is maintenance coming to replace it?\n\n{s}\n{name}",
         "Air filter replacement is TENANT responsibility (stated in lease). HVAC system repairs are landlord\u2019s."),
        ("Garbage disposal is jammed",
         "{g}\n\nMy garbage disposal stopped working. I think something got stuck in it. I need a repair person out here today.\n\n{s}\n{name}",
         "If tenant caused the jam (bones, grease, non-food items), it\u2019s TENANT responsibility. Mechanical failure is landlord\u2019s."),
        ("I lost my key, need a new one",
         "{g}\n\nI lost my apartment key and need a replacement made. Can you send the locksmith? This is urgent, I\u2019m locked out.\n\n{s}\n{name}",
         "Lost key replacement cost is TENANT responsibility ($75 fee per lease). Lockout assistance can be provided but billed to tenant."),
        ("Blinds are broken",
         "{g}\n\nThe blinds in my bedroom are broken \u2014 they won\u2019t close anymore. I need privacy, this needs to be fixed.\n\n{s}\n{name}",
         "If blinds were damaged by tenant, it\u2019s TENANT responsibility. If they failed due to age/wear, landlord covers it."),
    ]

    for i, (tid, first, last, email, unum, pname) in enumerate(tenants[:6]):
        name = f"{first} {last}"
        subj, body_tpl, note = templates[i % len(templates)]
        s = random.choice(SIGNOFFS)
        body = body_tpl.format(g=random.choice(GREETINGS), s=s, name=name)
        mm.append((email, f"{subj} \u2014 Unit {unum}", body, tid))

    for from_addr, subj, body, tid in mm:
        received = rand_date(datetime(2026, 2, 10), datetime(2026, 2, 24))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id) VALUES (?,?,?,?,?,0,?)",
            (from_addr, "manager@greenleafproperties.example.com", subj, body,
             received.strftime("%Y-%m-%d %H:%M:%S"), tid))
    return len(mm)

def seed_wrong_contractor_emails(cur):
    """Emails where tenant requests the wrong type of contractor for their issue."""
    cur.execute("SELECT t.id, t.first_name, t.last_name, t.email, u.unit_number, p.name FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id ORDER BY RANDOM() LIMIT 6")
    tenants = cur.fetchall()
    g = random.choice(GREETINGS)
    mm = []

    # (subject, body, what they ask for, what they actually need)
    wrong_contractor_templates = [
        ("Electrical issue in kitchen — Unit {unum}",
         "{g}\n\nThe outlet behind my fridge stopped working and now there\u2019s a burning smell coming from the wall. Can you send the plumber? I think there might be water damage causing it.\n\n{s}\n{name}",
         "Asks for plumber", "Needs Lone Star Electric — burning smell from outlet is electrical, not plumbing"),
        ("Water heater problem — Unit {unum}",
         "{g}\n\nMy water heater is making a loud banging noise and the water is barely warm. Can you have the HVAC guys come look at it? It\u2019s really cold in the morning with no hot water.\n\n{s}\n{name}",
         "Asks for HVAC", "Water heater is plumbing — needs Mike\u2019s Plumbing, not Austin HVAC Pros"),
        ("Weird smell in apartment — Unit {unum}",
         "{g}\n\nThere\u2019s a weird musty smell in my apartment, especially near the bathroom. I think it might be mold. Can you send the cleaning company to do a deep clean?\n\n{s}\n{name}",
         "Asks for cleaning", "Musty/mold smell needs inspection first — could be plumbing leak behind walls. Send Mike\u2019s Plumbing to check for leak, not Green Clean"),
        ("Need electrical panel work — Unit {unum}",
         "{g}\n\nMy breaker keeps tripping whenever I run the microwave and AC at the same time. The panel looks old. Can you have the handyman take a look at the electrical panel?\n\n{s}\n{name}",
         "Asks for handyman", "Electrical panel work requires licensed electrician — must use Lone Star Electric, not ATX Handyman"),
        ("Wasps near my window — Unit {unum}",
         "{g}\n\nThere\u2019s a wasp nest forming near my bedroom window on the outside. Can you have the handyman come remove it? I\u2019m allergic and this is urgent.\n\n{s}\n{name}",
         "Asks for handyman", "Wasp nest removal is pest control — needs Hill Country Pest Control, not a handyman"),
        ("Ceiling stain getting worse — Unit {unum}",
         "{g}\n\nThe stain on my bathroom ceiling is getting bigger and now it\u2019s starting to bubble. I think the roof might be leaking. Can you send the painter to fix the ceiling?\n\n{s}\n{name}",
         "Asks for painter/cosmetic fix", "Expanding ceiling stain = active water leak. Needs Roofing Solutions Austin to find the source, then Mike\u2019s Plumbing. Painting is the last step."),
    ]

    for i, (tid, first, last, email, unum, pname) in enumerate(tenants):
        subj_tpl, body_tpl, asks_for, actually_needs = wrong_contractor_templates[i]
        s = random.choice(SIGNOFFS)
        name = f"{first} {last}"
        subj = subj_tpl.format(unum=unum)
        body = body_tpl.format(g=random.choice(GREETINGS), s=s, name=name)
        mm.append((email, subj, body, tid))

    for from_addr, subj, body, tid in mm:
        received = rand_date(datetime(2026, 2, 10), datetime(2026, 2, 24))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id) VALUES (?,?,?,?,?,0,?)",
            (from_addr, "manager@greenleafproperties.example.com", subj, body,
             received.strftime("%Y-%m-%d %H:%M:%S"), tid))
    return len(mm)

def seed_mismatch_emails(cur):
    """Emails where tenant claims don't match the data."""
    cur.execute("""SELECT t.id, t.first_name, t.last_name, t.email, t.rent_amount,
                   u.unit_number, p.name FROM tenants t
                   JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id
                   ORDER BY RANDOM() LIMIT 30""")
    tenants = cur.fetchall()

    mm = []
    g = random.choice(GREETINGS)

    # Type 1: Tenant claims they paid rent but payment shows past_due
    cur.execute("SELECT p.tenant_id, p.due_date FROM payments p WHERE p.status='past_due' LIMIT 3")
    for ptid, due in cur.fetchall():
        cur.execute("SELECT first_name, last_name, email, unit_id FROM tenants WHERE id=?", (ptid,))
        row = cur.fetchone()
        if row:
            first, last, email, uid = row
            mm.append((email, f"Re: Late rent notice",
                f"{g}\n\nI\u2019m confused by the late rent notice. I paid my rent on time via {'Zelle' if random.random()>0.5 else 'bank transfer'} on the 1st. I have the confirmation screenshot. Can you check your records? There must be a mistake.\n\n{first} {last}",
                ptid))

    # Type 2: Tenant claims rent amount is different from what's in the lease
    for tid, first, last, email, rent, unum, pname in tenants[:3]:
        fake_rent = rent - random.choice([50, 100, 150])
        mm.append((email, f"Rent increase not agreed to",
            f"{g}\n\nI just saw my rent portal shows ${rent:.0f} but my lease says ${fake_rent:.0f}. I never agreed to a rent increase. Please fix this immediately or I\u2019ll need to see the signed amendment.\n\n{first} {last}",
            tid))

    # Type 3: Tenant says they submitted maintenance request but nothing in system
    for tid, first, last, email, rent, unum, pname in tenants[3:6]:
        mm.append((email, f"Still waiting on my maintenance request",
            f"{g}\n\nI submitted a maintenance request {'two weeks ago' if random.random()>0.5 else 'last month'} about {'a broken garbage disposal' if random.random()>0.5 else 'a leak under the bathroom sink'} and nobody has come out yet. This is unacceptable. I\u2019ve been a good tenant for {'two years' if random.random()>0.5 else 'over a year'}.\n\n{first} {last}",
            tid))

    # Type 4: Tenant claims security deposit amount is different
    for tid, first, last, email, rent, unum, pname in tenants[6:9]:
        fake_deposit = rent + random.choice([200, 500])
        mm.append((email, f"Security deposit discrepancy",
            f"{g}\n\nI\u2019m reviewing my move-in paperwork and I believe I paid ${fake_deposit:.0f} as a security deposit, but your records might show ${rent:.0f}. I have the original receipt. Can we verify this before my lease renewal?\n\n{first} {last}",
            tid))

    for from_addr, subj, body, tenant_id in mm:
        received = rand_date(datetime(2026, 2, 10), datetime(2026, 2, 24))
        cur.execute("INSERT INTO emails (from_address,to_address,subject,body,received_at,is_read,tenant_id) VALUES (?,?,?,?,?,0,?)",
            (from_addr, "manager@greenleafproperties.example.com", subj, body,
             received.strftime("%Y-%m-%d %H:%M:%S"), tenant_id))
    return len(mm)

# ──────────────────────────────────────────────
def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    np = seed_properties(cur); conn.commit(); print(f"  properties: {np}")
    nu = seed_units(cur); conn.commit(); print(f"  units: {nu}")
    nt = seed_tenants(cur); conn.commit(); print(f"  tenants: {nt}")
    npay = seed_payments(cur); conn.commit(); print(f"  payments: {npay}")
    nm = seed_maintenance(cur); conn.commit(); print(f"  maintenance_requests: {nm}")
    na = seed_applications(cur); conn.commit(); print(f"  rental_applications: {na}")
    ne = seed_emails(cur); conn.commit(); print(f"  emails (inbound): {ne}")
    nse = seed_sent_emails(cur); conn.commit(); print(f"  emails (sent/replies): {nse}")
    nlm = seed_new_maintenance_emails(cur); conn.commit(); print(f"  legit maintenance emails: {nlm}")
    nrm = seed_responsibility_mismatch_emails(cur); conn.commit(); print(f"  responsibility mismatches: {nrm}")
    nwc = seed_wrong_contractor_emails(cur); conn.commit(); print(f"  wrong contractor emails: {nwc}")
    nmm = seed_mismatch_emails(cur); conn.commit(); print(f"  data mismatch emails: {nmm}")

    # Validations
    cur.execute("SELECT first_name||' '||last_name, COUNT(*) FROM tenants GROUP BY 1 HAVING COUNT(*)>1")
    dup = cur.fetchall()
    cur.execute("SELECT DISTINCT substr(email, instr(email,'@')+1) FROM tenants")
    domains = [r[0] for r in cur.fetchall()]
    real = [d for d in domains if "example" not in d]
    cur.execute("SELECT COUNT(*) FROM payments WHERE status='past_due'")
    past_due = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM units WHERE status='vacant'")
    vacant = cur.fetchone()[0]

    print(f"\n  {'OK' if not dup else 'FAIL'} Unique tenant names")
    print(f"  {'OK' if not real else 'FAIL'} Safe email domains only")
    print(f"  Past due payments: {past_due}")
    print(f"  Vacant units: {vacant}")
    print(f"  Total emails: {ne + nmm}")

    conn.close()
    print(f"\nDone: {DB_PATH}")

if __name__ == "__main__":
    main()
