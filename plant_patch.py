
# ---------- PLANT: show breakdown reasons on overview ----------
# (replaces landing / line_detail after package restore)

@app.route("/")
def landing():
    conn = get_db()
    lines_b = conn.execute("SELECT * FROM assets WHERE asset_type='line_b' ORDER BY sort_order").fetchall()
    lines_l = conn.execute("SELECT * FROM assets WHERE asset_type='line_l' ORDER BY sort_order").fetchall()
    mixers = conn.execute("SELECT * FROM assets WHERE asset_type='mixer' ORDER BY sort_order").fetchall()
    support = conn.execute("SELECT * FROM assets WHERE asset_type='support' ORDER BY sort_order").fetchall()
    bd_rows = conn.execute("""
        SELECT b.asset_id, b.reason, b.repair_minutes, a.code, a.name, a.asset_type, a.parent_code
        FROM breakdowns b JOIN assets a ON a.id=b.asset_id
        WHERE b.status='open' ORDER BY b.start_time DESC
    """).fetchall()
    open_bd = {r["asset_id"]: r["reason"] for r in bd_rows}
    parent_reasons = {}
    for r in bd_rows:
        if r["parent_code"] and r["parent_code"] not in parent_reasons:
            parent_reasons[r["parent_code"]] = f"{r['code']}: {r['reason']}"

    def enrich(rows):
        out = []
        for a in rows:
            st = a["status"]
            reason = open_bd.get(a["id"])
            if reason:
                st = "breakdown"
            elif a["code"] in parent_reasons:
                st = "breakdown"
                reason = parent_reasons[a["code"]]
            elif st == "breakdown" and not reason:
                reason = parent_reasons.get(a["code"]) or "Breakdown (see Maintenance)"
            out.append({**dict(a), "effective": st, "color": line_status_color(st), "bd_reason": reason})
        return out

    orders_active = conn.execute("""
        SELECT o.*, p.name as product_name FROM orders o JOIN products p ON p.id=o.product_id
        WHERE o.status NOT IN ('shipped','ready') ORDER BY o.created_at DESC LIMIT 8
    """).fetchall()
    open_breakdowns = [dict(r) for r in bd_rows]
    conn.close()
    return render_template("landing.html",
        lines_b=enrich(lines_b), lines_l=enrich(lines_l),
        mixers=enrich(mixers), support=enrich(support),
        orders_active=orders_active, open_breakdowns=open_breakdowns)

@app.route("/line/<code>")
def line_detail(code):
    conn = get_db()
    line = conn.execute("SELECT * FROM assets WHERE code=?", (code,)).fetchone()
    if not line:
        conn.close()
        flash("Line not found", "error")
        return redirect(url_for("landing"))
    components = conn.execute(
        "SELECT * FROM assets WHERE parent_code=? ORDER BY sort_order", (code,)).fetchall()
    bd_rows = conn.execute("""
        SELECT b.*, a.code, a.name FROM breakdowns b
        JOIN assets a ON a.id=b.asset_id
        WHERE b.status='open'
    """).fetchall()
    open_bd = {r["asset_id"]: r for r in bd_rows}
    comps = []
    for c in components:
        row = open_bd.get(c["id"])
        st = "breakdown" if row else c["status"]
        comps.append({
            **dict(c),
            "effective": st,
            "color": line_status_color(st),
            "bd_reason": row["reason"] if row else None,
        })
    order = conn.execute("""
        SELECT o.*, p.name as product_name, p.unit_label FROM orders o
        JOIN products p ON p.id=o.product_id
        WHERE o.production_line=? AND o.status IN ('extrusion','packaging','lab','mixing')
        ORDER BY o.created_at DESC LIMIT 1
    """, (code,)).fetchone()
    materials_used = []
    if order:
        materials_used = conn.execute("""
            SELECT m.name, m.unit, ROUND(ri.weight_g_per_unit * o.quantity_units / 1000.0, 2) as qty_needed
            FROM recipe_items ri
            JOIN materials m ON m.id=ri.material_id
            JOIN orders o ON o.product_id=ri.product_id
            WHERE o.id=?
        """, (order["id"],)).fetchall()
    line_bd = open_bd.get(line["id"])
    line_st = "breakdown" if line_bd or any(c["effective"]=="breakdown" for c in comps) else line["status"]
    line_bd_reason = None
    if line_bd:
        line_bd_reason = line_bd["reason"]
    else:
        for c in comps:
            if c.get("bd_reason"):
                line_bd_reason = f"{c['code']}: {c['bd_reason']}"
                break
    open_on_line = []
    for r in bd_rows:
        if r["asset_id"] == line["id"] or any(c["id"] == r["asset_id"] for c in components):
            open_on_line.append(dict(r))
    conn.close()
    return render_template(
        "line_detail.html",
        line=line,
        components=comps,
        line_st=line_st,
        line_color=line_status_color(line_st),
        line_bd_reason=line_bd_reason,
        open_on_line=open_on_line,
        order=order,
        materials_used=materials_used,
    )
