-- GreenLeaf Property Management — Supabase Schema

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    unit_number TEXT NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms NUMERIC(3,1) NOT NULL,
    sqft INTEGER NOT NULL,
    rent_amount NUMERIC(10,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'occupied',
    notes TEXT,
    UNIQUE(property_id, unit_number)
);

CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    unit_id INTEGER REFERENCES units(id),
    lease_start DATE NOT NULL,
    lease_end DATE NOT NULL,
    rent_amount NUMERIC(10,2) NOT NULL,
    security_deposit NUMERIC(10,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    employer TEXT,
    annual_income NUMERIC(12,2),
    ssn_last_four TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    unit_id INTEGER NOT NULL REFERENCES units(id),
    amount NUMERIC(10,2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status TEXT NOT NULL DEFAULT 'pending',
    payment_method TEXT,
    late_fee NUMERIC(10,2) DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS maintenance_requests (
    id SERIAL PRIMARY KEY,
    request_number TEXT UNIQUE NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES units(id),
    tenant_id INTEGER REFERENCES tenants(id),
    category TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal',
    status TEXT NOT NULL DEFAULT 'open',
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    submitted_date DATE NOT NULL,
    scheduled_date DATE,
    completed_date DATE,
    contractor_name TEXT,
    contractor_phone TEXT,
    estimated_cost NUMERIC(10,2),
    actual_cost NUMERIC(10,2),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL DEFAULT 'manager@greenleafproperties.example.com',
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    replied BOOLEAN DEFAULT FALSE,
    reply_body TEXT,
    tenant_id INTEGER REFERENCES tenants(id),
    property_id INTEGER REFERENCES properties(id)
);

CREATE TABLE IF NOT EXISTS rental_applications (
    id SERIAL PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    applicant_phone TEXT,
    desired_unit_id INTEGER REFERENCES units(id),
    current_address TEXT,
    employer TEXT,
    annual_income NUMERIC(12,2),
    credit_score INTEGER,
    has_pets BOOLEAN DEFAULT FALSE,
    pet_details TEXT,
    move_in_date DATE,
    status TEXT NOT NULL DEFAULT 'pending',
    submitted_date DATE NOT NULL,
    notes TEXT
);

-- Enable RLS and allow full access via anon key
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE units ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_applications ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY['properties','units','tenants','payments','maintenance_requests','emails','rental_applications'])
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "Allow full access" ON %I', t);
        EXECUTE format('CREATE POLICY "Allow full access" ON %I FOR ALL USING (true) WITH CHECK (true)', t);
    END LOOP;
END $$;
