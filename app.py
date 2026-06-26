import os
import ipaddress
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Create a .env file from .env.example and set SECRET_KEY."
    )


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_role") != "Admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return wrapper


def hash_password(password):
    return generate_password_hash(password)


def validate_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def validate_netmask(mask):
    try:
        ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return True
    except ValueError:
        return False


def get_device_types():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT device_type_id, type_name FROM device_types ORDER BY type_name")
    types = cursor.fetchall()
    cursor.close()
    conn.close()
    return types


def get_device_by_id(device_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM devices WHERE device_id = %s",
        (device_id,),
    )
    device = cursor.fetchone()
    cursor.close()
    conn.close()
    return device


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT u.user_id, u.username, u.password_hash, r.role_name "
            "FROM users u "
            "JOIN roles r ON u.role_id = r.role_id "
            "WHERE u.username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["user_role"] = user["role_name"]
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid login credentials.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM device_types")
    type_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        device_count=device_count,
        type_count=type_count,
        user_count=user_count,
    )


@app.route("/devices")
@login_required
def devices():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute(
            "SELECT d.device_id, d.device_name, dt.type_name, d.device_address, d.network_mask, "
            "d.default_gateway, d.location, d.notes, u.username AS created_by, d.created_at "
            "FROM devices d "
            "JOIN device_types dt ON d.device_type_id = dt.device_type_id "
            "LEFT JOIN users u ON d.created_by = u.user_id "
            "WHERE d.device_name LIKE %s OR d.device_address LIKE %s OR d.location LIKE %s "
            "OR dt.type_name LIKE %s "
            "ORDER BY d.created_at DESC",
            (like_search, like_search, like_search, like_search),
        )
    else:
        cursor.execute(
            "SELECT d.device_id, d.device_name, dt.type_name, d.device_address, d.network_mask, "
            "d.default_gateway, d.location, d.notes, u.username AS created_by, d.created_at "
            "FROM devices d "
            "JOIN device_types dt ON d.device_type_id = dt.device_type_id "
            "LEFT JOIN users u ON d.created_by = u.user_id "
            "ORDER BY d.created_at DESC"
        )

    devices = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("devices.html", devices=devices, search=search)


@app.route("/devices/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_device():
    device_types = get_device_types()

    if request.method == "POST":
        device_name = request.form.get("device_name", "").strip()
        device_type_id = request.form.get("device_type_id")
        device_address = request.form.get("device_address", "").strip()
        network_mask = request.form.get("network_mask", "").strip()
        default_gateway = request.form.get("default_gateway", "").strip()
        location = request.form.get("location", "").strip()
        notes = request.form.get("notes", "").strip()

        if not device_name or not device_type_id or not device_address or not network_mask or not default_gateway:
            flash("Please fill in all required fields.", "danger")
            return render_template("add_device.html", device_types=device_types)

        if not validate_ip(device_address):
            flash("Device IP address is invalid.", "danger")
            return render_template("add_device.html", device_types=device_types)

        if not validate_netmask(network_mask):
            flash("Network mask is invalid.", "danger")
            return render_template("add_device.html", device_types=device_types)

        if not validate_ip(default_gateway):
            flash("Default gateway is invalid.", "danger")
            return render_template("add_device.html", device_types=device_types)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO devices (device_name, device_type_id, device_address, network_mask, default_gateway, location, notes, created_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (device_name, device_type_id, device_address, network_mask, default_gateway, location, notes, session["user_id"]),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Device added successfully.", "success")
        return redirect(url_for("devices"))

    return render_template("add_device.html", device_types=device_types)


@app.route("/devices/edit/<int:device_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_device(device_id):
    device = get_device_by_id(device_id)
    if not device:
        flash("Device not found.", "danger")
        return redirect(url_for("devices"))

    device_types = get_device_types()

    if request.method == "POST":
        device_name = request.form.get("device_name", "").strip()
        device_type_id = request.form.get("device_type_id")
        device_address = request.form.get("device_address", "").strip()
        network_mask = request.form.get("network_mask", "").strip()
        default_gateway = request.form.get("default_gateway", "").strip()
        location = request.form.get("location", "").strip()
        notes = request.form.get("notes", "").strip()

        if not device_name or not device_type_id or not device_address or not network_mask or not default_gateway:
            flash("Please fill in all required fields.", "danger")
            return render_template("edit_device.html", device=device, device_types=device_types)

        if not validate_ip(device_address):
            flash("Device IP address is invalid.", "danger")
            return render_template("edit_device.html", device=device, device_types=device_types)

        if not validate_netmask(network_mask):
            flash("Network mask is invalid.", "danger")
            return render_template("edit_device.html", device=device, device_types=device_types)

        if not validate_ip(default_gateway):
            flash("Default gateway is invalid.", "danger")
            return render_template("edit_device.html", device=device, device_types=device_types)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE devices SET device_name = %s, device_type_id = %s, device_address = %s, network_mask = %s, "
            "default_gateway = %s, location = %s, notes = %s WHERE device_id = %s",
            (device_name, device_type_id, device_address, network_mask, default_gateway, location, notes, device_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Device updated successfully.", "success")
        return redirect(url_for("devices"))

    return render_template("edit_device.html", device=device, device_types=device_types)


@app.route("/devices/delete/<int:device_id>", methods=["POST"])
@login_required
@admin_required
def delete_device(device_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Device deleted successfully.", "success")
    return redirect(url_for("devices"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    # Debug mode is intended for local development only. Disable in production.
    app.run(debug=debug_mode)
