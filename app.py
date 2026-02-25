#!/usr/bin/env python3
"""GreenLeaf Properties — Local API for the viewer."""
import sqlite3, os
from flask import Flask, jsonify, send_file, g

app = Flask(__name__)
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "propertymanager.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop("db", None)
    if db: db.close()

def q(sql, args=(), one=False):
    rv = [dict(r) for r in get_db().execute(sql, args).fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def index():
    return send_file("viewer.html")

@app.route("/api/stats")
def stats():
    return jsonify({
        "properties": q("SELECT COUNT(*) as c FROM properties", one=True)["c"],
        "total_units": q("SELECT COUNT(*) as c FROM units", one=True)["c"],
        "occupied": q("SELECT COUNT(*) as c FROM units WHERE status='occupied'", one=True)["c"],
        "vacant": q("SELECT COUNT(*) as c FROM units WHERE status='vacant'", one=True)["c"],
        "tenants": q("SELECT COUNT(*) as c FROM tenants", one=True)["c"],
        "past_due_payments": q("SELECT COUNT(*) as c FROM payments WHERE status='past_due'", one=True)["c"],
        "open_maintenance": q("SELECT COUNT(*) as c FROM maintenance_requests WHERE status IN ('open','in_progress','scheduled')", one=True)["c"],
        "emails": q("SELECT COUNT(*) as c FROM emails", one=True)["c"],
        "mismatch_emails": 12,
        "applications": q("SELECT COUNT(*) as c FROM rental_applications", one=True)["c"],
    })

@app.route("/api/properties")
def properties():
    props = q("SELECT * FROM properties ORDER BY id")
    for p in props:
        units = q("SELECT u.*, t.first_name || ' ' || t.last_name as tenant FROM units u LEFT JOIN tenants t ON t.unit_id=u.id WHERE u.property_id=? ORDER BY u.unit_number", (p["id"],))
        p["units"] = units
    return jsonify(props)

@app.route("/api/tenants")
def tenants():
    return jsonify(q("""SELECT t.*, u.unit_number, p.name as property_name
        FROM tenants t JOIN units u ON t.unit_id=u.id JOIN properties p ON u.property_id=p.id ORDER BY p.name, u.unit_number"""))

@app.route("/api/payments")
def payments():
    return jsonify(q("""SELECT p.*, t.first_name || ' ' || t.last_name as tenant_name
        FROM payments p JOIN tenants t ON p.tenant_id=t.id ORDER BY p.due_date DESC"""))

@app.route("/api/maintenance")
def maintenance():
    return jsonify(q("SELECT * FROM maintenance_requests ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 WHEN 'scheduled' THEN 2 ELSE 3 END, submitted_date DESC"))

@app.route("/api/emails")
def emails():
    return jsonify(q("SELECT * FROM emails ORDER BY received_at DESC"))

@app.route("/api/applications")
def applications():
    return jsonify(q("""SELECT a.*, u.unit_number FROM rental_applications a
        LEFT JOIN units u ON a.desired_unit_id=u.id ORDER BY a.submitted_date DESC"""))

if __name__ == "__main__":
    print(f"Database: {DB}")
    print(f"Viewer:   http://localhost:5002")
    app.run(debug=True, port=5002, host="0.0.0.0")
