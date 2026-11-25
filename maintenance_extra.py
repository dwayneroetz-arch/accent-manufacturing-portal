# ---------- EXTENDED MAINTENANCE (Tasks, Quotes, Fuel, Tracking, Suppliers) ----------

@app.route("/maintenance/hub")
def maintenance_hub():
    """Main upgraded maintenance home"""
    conn = get_db()
    open_tasks = conn.execute("SELECT * FROM tasks WHERE status IN ('Open','In Progress') ORDER BY due_date IS NULL, due_date LIMIT 10").fetchall()
    pending_quotes = conn.execute("SELECT q.*, s.company FROM quotes q LEFT JOIN suppliers s ON s.id=q.supplier_id WHERE q.status IN ('Requested','Waiting') ORDER BY q.created_at DESC LIMIT 8").fetchall()
    open_tracking = conn.execute("SELECT * FROM tracking WHERE status IN ('Open','In Progress') ORDER BY created_at DESC LIMIT 10").fetchall()
    recent_fuel = conn.execute("SELECT * FROM fuel_orders ORDER BY created_at DESC LIMIT 5").fetchall()
    assets = conn.execute("SELECT * FROM assets WHERE asset_type IN ('line_b','line_l','mixer','support') ORDER BY sort_order").fetchall()
    suppliers = conn.execute("SELECT * FROM suppliers ORDER BY company").fetchall()
    conn.close()
    return render_template("maintenance_hub.html",
        open_tasks=open_tasks, pending_quotes=pending_quotes,
        open_tracking=open_tracking, recent_fuel=recent_fuel,
        assets=assets, suppliers=suppliers)

@app.route("/maintenance/task/new", methods=["GET", "POST"])
def task_new():
    conn = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        asset_code = request.form.get("asset_code") or None
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date") or None
        description = request.form.get("description", "")
        if not title:
            flash("Title required", "error")
            return redirect(url_for("task_new"))
        tracking_no = next_tracking_no(conn)
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute("INSERT INTO tracking (tracking_no, created_at, type, asset_code, title, status) VALUES (?,?,?,?,?,?)",
                     (tracking_no, now, "Task", asset_code, title, "Open"))
        conn.execute("""INSERT INTO tasks (tracking_no, asset_code, title, description, priority, status, due_date, created_at)
                        VALUES (?,?,?,?,?,?,?,?)""",
                     (tracking_no, asset_code, title, description, priority, "Open", due_date, now))
        log_activity(conn, tracking_no, "Task created", f"Task: {title}")
        conn.commit()
        conn.close()
        flash(f"Task created with Tracking {tracking_no}", "success")
        return redirect(url_for("maintenance_hub"))
    assets = conn.execute("SELECT code, name FROM assets ORDER BY sort_order").fetchall()
    conn.close()
    return render_template("maintenance_form_task.html", assets=assets)

@app.route("/maintenance/quote/new", methods=["GET", "POST"])
def quote_new():
    conn = get_db()
    if request.method == "POST":
        supplier_id = request.form.get("supplier_id")
        asset_code = request.form.get("asset_code") or None
        description = request.form.get("description", "").strip()
        message = request.form.get("message", "").strip()
        if not supplier_id or not description:
            flash("Supplier and description required", "error")
            return redirect(url_for("quote_new"))
        tracking_no = next_tracking_no(conn)
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute("INSERT INTO tracking (tracking_no, created_at, type, asset_code, title, status) VALUES (?,?,?,?,?,?)",
                     (tracking_no, now, "Quote", asset_code, description[:80], "Open"))
        conn.execute("""INSERT INTO quotes (tracking_no, supplier_id, asset_code, description, message, status, created_at)
                        VALUES (?,?,?,?,?,?,?)""",
                     (tracking_no, supplier_id, asset_code, description, message, "Requested", now))
        log_activity(conn, tracking_no, "Quote requested", description)
        conn.commit()
        supplier = conn.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
        asset = conn.execute("SELECT * FROM assets WHERE code=?", (asset_code,)).fetchone() if asset_code else None
        conn.close()
        asset_info = f"{asset['name']} ({asset['code']})" if asset else "N/A"
        body = f"""Hi {supplier['contact_name'] or 'there'},

Please provide a quote for the following:

Asset: {asset_info}
Requirement: {description}

{message}

Reference / Tracking: {tracking_no}

Please reply with price, lead time and validity.

Regards,
Dwayne Roetz
Maintenance - Accent Manufacturing
dwayneroetz@gmail.com
WhatsApp: +27743502410"""
        import urllib.parse
        subject = f"Quote request - {tracking_no}"
        to_email = supplier['email'] or ''
        mailto = f"mailto:{to_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        gmail = None
        if to_email:
            gmail = (
                "https://mail.google.com/mail/?view=cm&fs=1"
                f"&to={urllib.parse.quote(to_email)}"
                f"&su={urllib.parse.quote(subject)}"
                f"&body={urllib.parse.quote(body)}"
            )
        phone = (supplier['phone'] or '').replace(' ', '').replace('+', '')
        if phone.startswith('0'):
            phone = '27' + phone[1:]
        wa = f"https://wa.me/{phone}?text={urllib.parse.quote(f'Hi, quote request {tracking_no} for {description}. Please see email or reply here.')}" if phone else None
        return render_template("maintenance_quote_sent.html", tracking_no=tracking_no, mailto=mailto, gmail=gmail, wa=wa, supplier=supplier, body=body)
    suppliers = conn.execute("SELECT * FROM suppliers ORDER BY company").fetchall()
    assets = conn.execute("SELECT code, name FROM assets ORDER BY sort_order").fetchall()
    conn.close()
    return render_template("maintenance_form_quote.html", suppliers=suppliers, assets=assets)

@app.route("/maintenance/fuel/new", methods=["GET", "POST"])
def fuel_new():
    conn = get_db()
    if request.method == "POST":
        litres = request.form.get("litres")
        notes = request.form.get("notes", "")
        try:
            litres = float(litres)
        except Exception:
            flash("Valid litres required", "error")
            return redirect(url_for("fuel_new"))
        tracking_no = next_tracking_no(conn)
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute("INSERT INTO tracking (tracking_no, created_at, type, title, status) VALUES (?,?,?,?,?)",
                     (tracking_no, now, "Fuel", f"Fuel order {litres} L", "Open"))
        conn.execute("INSERT INTO fuel_orders (tracking_no, litres, status, created_at, notes) VALUES (?,?,?,?,?)",
                     (tracking_no, litres, "Submitted", now, notes))
        log_activity(conn, tracking_no, "Fuel ordered", f"{litres} litres")
        conn.commit()
        conn.close()
        import urllib.parse
        body = f"""Hi Accounts,

Please order {litres} litres of diesel/fuel for the plant.

Tracking / Reference: {tracking_no}
Notes: {notes or 'None'}

Thank you,
Dwayne Roetz
Maintenance - Accent Manufacturing
dwayneroetz@gmail.com
WhatsApp: +27743502410"""
        subject = f"Fuel Order - {tracking_no}"
        to_email = "accounts.dept@accentmanuf.com"
        gmail = (
            "https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={urllib.parse.quote(to_email)}"
            f"&su={urllib.parse.quote(subject)}"
            f"&body={urllib.parse.quote(body)}"
        )
        mailto = f"mailto:{to_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        return render_template(
            "maintenance_fuel_sent.html",
            tracking_no=tracking_no,
            litres=litres,
            mailto=mailto,
            gmail=gmail,
            body=body,
            to_email=to_email,
            subject=subject,
        )
    conn.close()
    return render_template("maintenance_form_fuel.html")

@app.route("/maintenance/suppliers", methods=["GET", "POST"])
def suppliers():
    conn = get_db()
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        if company:
            conn.execute("""INSERT INTO suppliers (company, contact_name, email, phone, speciality, notes, created_at)
                            VALUES (?,?,?,?,?,?,?)""",
                         (company, request.form.get("contact_name"), request.form.get("email"),
                          request.form.get("phone"), request.form.get("speciality"),
                          request.form.get("notes"), datetime.now().isoformat(timespec="seconds")))
            conn.commit()
            flash("Supplier added", "success")
        return redirect(url_for("suppliers"))
    rows = conn.execute("SELECT * FROM suppliers ORDER BY company").fetchall()
    conn.close()
    return render_template("maintenance_suppliers.html", suppliers=rows)

@app.route("/maintenance/history")
def maintenance_history():
    tracking_no = request.args.get("tracking")
    conn = get_db()
    if tracking_no:
        logs = conn.execute("SELECT * FROM activity_log WHERE tracking_no=? ORDER BY created_at DESC", (tracking_no,)).fetchall()
        tracking = conn.execute("SELECT * FROM tracking WHERE tracking_no=?", (tracking_no,)).fetchone()
    else:
        logs = conn.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 50").fetchall()
        tracking = None
    all_tracking = conn.execute("SELECT tracking_no, title, type, status FROM tracking ORDER BY created_at DESC LIMIT 30").fetchall()
    conn.close()
    return render_template("maintenance_history.html", logs=logs, tracking=tracking, all_tracking=all_tracking, selected=tracking_no)

@app.route("/maintenance/assets/list")
def assets_list():
    conn = get_db()
    assets = conn.execute("SELECT * FROM assets ORDER BY sort_order, code").fetchall()
    conn.close()
    return render_template("maintenance_assets_list.html", assets=assets)
