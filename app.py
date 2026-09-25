from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3, os, hashlib, random, time, random, time
from functools import wraps

app = Flask(__name__)
app.secret_key = "icare-secret-2025"
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icare.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE NOT NULL, name TEXT NOT NULL, pin TEXT NOT NULL, balance REAL DEFAULT 0, is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, amount REAL, balance_after REAL, note TEXT, related_user_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, stock INTEGER, category TEXT, image TEXT, is_active INTEGER DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total REAL, status TEXT DEFAULT 'PENDING', created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, product_name TEXT, price REAL, quantity INTEGER, subtotal REAL)")
    if c.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        c.execute("INSERT INTO admins (username,password) VALUES (?,?)", ("admin", hashlib.sha256(b"admin123").hexdigest()))
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        items = [("iPhone 15","Latest iPhone",2500000,10,"Electronics","PHONE"),("AirPods Pro","ANC Wireless",350000,25,"Electronics","EAR"),("Coffee 1kg","Arabica Premium",25000,50,"Food","COFFEE"),("T-Shirt","Cotton M/L/XL",15000,100,"Fashion","SHIRT"),("Headphones","BT 5.0",85000,30,"Electronics","EAR"),("Python Book","Learn Python",18000,40,"Books","BOOK")]
        for i in items: c.execute("INSERT INTO products (name,description,price,stock,category,image) VALUES (?,?,?,?,?,?)", i)
    conn.commit(); conn.close()

def hp(p): return hashlib.sha256(p.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*a, **k)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("is_admin"): return redirect(url_for("admin_login"))
        return f(*a, **k)
    return w

CSS = """
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;font-family:-apple-system,"SF Pro Display","SF Pro Text",sans-serif;-webkit-font-smoothing:antialiased}
body{background:linear-gradient(135deg,#e5e5ea,#f2f2f7);min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;color:#1c1c1e}
.phone{width:390px;height:844px;background:#fff;border-radius:54px;box-shadow:0 50px 100px -20px rgba(0,0,0,.25),0 0 0 11px #000,0 0 0 13px #3a3a3c;position:relative;overflow:hidden;display:flex;flex-direction:column}
.notch{position:absolute;top:0;left:50%;transform:translateX(-50%);width:120px;height:34px;background:#000;border-radius:0 0 22px 22px;z-index:100}
.status{height:54px;display:flex;justify-content:space-between;align-items:center;padding:0 32px 0 40px;font-size:16px;font-weight:600;position:relative;z-index:50;flex-shrink:0}
.screen{flex:1;overflow-y:auto;padding-bottom:110px;background:#f2f2f7;scrollbar-width:none}
.screen::-webkit-scrollbar{display:none}
.balance-wrap{padding:8px 16px 0}
.balance-card{background:linear-gradient(135deg,#ff3b30,#d70015);border-radius:24px;padding:24px;color:#fff;position:relative;overflow:hidden;box-shadow:0 12px 32px -8px rgba(255,59,48,.5)}
.bc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.bc-head .brand{font-size:16px;font-weight:700}
.bc-label{font-size:13px;opacity:.9;font-weight:500}
.bc-amount{font-size:40px;font-weight:700;margin:4px 0 6px;letter-spacing:-1.5px}
.bc-user{font-size:14px;opacity:.9;font-weight:500}
.bc-actions{display:flex;gap:10px;margin-top:22px}
.bc-actions a{flex:1;padding:12px;background:rgba(255,255,255,.25);border-radius:14px;text-align:center;color:#fff;text-decoration:none;font-size:14px;font-weight:600;border:.5px solid rgba(255,255,255,.35)}
.section{padding:24px 16px 0}
.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding:0 4px}
.section-head h3{font-size:20px;font-weight:700;letter-spacing:-.5px}
.section-head a{font-size:15px;color:#ff3b30;text-decoration:none;font-weight:500}
.actions-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.action{display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 4px;background:#fff;border-radius:18px;text-decoration:none;color:#1c1c1e;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.action .ico{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;background:linear-gradient(135deg,#ffe5e3,#ffd0cc)}
.action .lbl{font-size:11px;font-weight:600;text-align:center}
.txn-list{background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.txn{display:flex;align-items:center;padding:14px 16px;border-bottom:.5px solid #e5e5ea;gap:14px}
.txn:last-child{border-bottom:none}
.txn .av{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.txn .info{flex:1}
.txn .info .t{font-size:15px;font-weight:600;margin-bottom:2px}
.txn .info .d{font-size:12px;color:#8e8e93}
.txn .amt{font-size:15px;font-weight:700}
.in{color:#34c759}.out{color:#ff3b30}
.bg-in{background:rgba(52,199,89,.12)}.bg-out{background:rgba(255,59,48,.12)}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:8px 16px 0}
.stat{background:#fff;border-radius:18px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.stat .v{font-size:22px;font-weight:700;margin-bottom:2px}
.stat .l{font-size:12px;color:#8e8e93}
.nav{position:absolute;bottom:0;left:0;right:0;height:88px;background:rgba(255,255,255,.88);backdrop-filter:blur(30px);border-top:.5px solid rgba(0,0,0,.12);display:flex;justify-content:space-around;align-items:flex-start;padding:8px 8px 22px;z-index:60}
.nav a{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;color:#8e8e93;text-decoration:none;padding:6px 4px;font-size:10px;font-weight:500;position:relative}
.nav a.on{color:#ff3b30}
.nav a .ni{font-size:22px;line-height:1}
.badge-dot{position:absolute;top:0;right:calc(50% - 22px);background:#ff3b30;color:#fff;font-size:10px;font-weight:700;min-width:16px;height:16px;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:0 4px;border:2px solid #fff}
.appbar{padding:56px 20px 12px;background:rgba(255,255,255,.88);backdrop-filter:blur(30px);display:flex;align-items:center;gap:12px;border-bottom:.5px solid rgba(0,0,0,.12)}
.appbar a{width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:50%;color:#ff3b30;text-decoration:none;font-size:22px}
.appbar h2{font-size:17px;font-weight:600;flex:1;text-align:center;padding-right:36px}
.form-wrap{padding:20px 16px}
.form-wrap label{display:block;font-size:13px;color:#8e8e93;margin-bottom:8px;margin-top:20px;padding-left:4px}
.form-wrap input{width:100%;padding:14px 16px;background:#fff;border:none;border-radius:14px;font-size:17px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.form-wrap input:focus{outline:none;box-shadow:0 0 0 3px rgba(255,59,48,.18)}
.btn{width:100%;padding:16px;background:linear-gradient(135deg,#ff453a,#d70015);color:#fff;border:none;border-radius:14px;font-size:17px;font-weight:600;margin-top:24px;cursor:pointer;box-shadow:0 8px 20px -4px rgba(255,59,48,.4);text-decoration:none;display:block;text-align:center}
.alert{padding:14px 16px;border-radius:14px;margin:16px;font-size:14px;font-weight:500}
.al-ok{background:rgba(52,199,89,.15);color:#248a3d}
.al-err{background:rgba(255,59,48,.15);color:#c7000e}
.auth-logo{text-align:center;padding:60px 20px 40px}
.auth-logo .lbox{width:88px;height:88px;background:linear-gradient(135deg,#ff453a,#d70015);border-radius:24px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;font-size:44px;color:#fff;box-shadow:0 20px 40px -10px rgba(255,59,48,.5)}
.auth-logo h1{font-size:32px;font-weight:700;letter-spacing:-1px}
.auth-logo p{font-size:14px;color:#8e8e93;margin-top:8px;font-weight:500}
.auth-form{padding:0 20px 40px}
.auth-form h3{font-size:22px;margin-bottom:4px;font-weight:700}
.auth-form label{display:block;font-size:13px;color:#8e8e93;margin-bottom:8px;margin-top:18px;padding-left:4px}
.auth-form input{width:100%;padding:16px;background:#fff;border:none;border-radius:14px;font-size:17px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.auth-form input:focus{outline:none;box-shadow:0 0 0 3px rgba(255,59,48,.18)}
.cat-scroll{display:flex;gap:8px;padding:12px 16px;overflow-x:auto;scrollbar-width:none}
.cat-scroll::-webkit-scrollbar{display:none}
.cat-chip{padding:8px 16px;background:#fff;border-radius:20px;font-size:13px;font-weight:600;color:#1c1c1e;text-decoration:none;white-space:nowrap;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.cat-chip.on{background:linear-gradient(135deg,#ff453a,#d70015);color:#fff}
.product-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:8px 16px}
.product{background:#fff;border-radius:18px;overflow:hidden;text-decoration:none;color:#1c1c1e;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.product .pimg{aspect-ratio:1;background:linear-gradient(135deg,#f2f2f7,#e5e5ea);display:flex;align-items:center;justify-content:center;font-size:48px;position:relative}
.product .pimg .stock-tag{position:absolute;top:8px;right:8px;background:rgba(0,0,0,.6);color:#fff;font-size:10px;font-weight:600;padding:3px 8px;border-radius:10px}
.product .pbody{padding:12px}
.product .ptitle{font-size:13px;font-weight:600;margin-bottom:4px;line-height:1.3;height:34px;overflow:hidden}
.product .pcat{font-size:11px;color:#8e8e93;margin-bottom:6px}
.product .pprice{font-size:15px;font-weight:700;color:#ff3b30}
.product-detail{padding:16px}
.product-detail .big-img{aspect-ratio:1;background:linear-gradient(135deg,#f2f2f7,#e5e5ea);border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:120px;margin-bottom:20px}
.product-detail h2{font-size:24px;font-weight:700;margin-bottom:4px}
.product-detail .price{font-size:28px;font-weight:700;color:#ff3b30;margin:12px 0}
.product-detail .desc{font-size:15px;color:#3a3a3c;line-height:1.5;margin:12px 0}
.product-detail .stock-info{font-size:13px;color:#8e8e93;margin-bottom:16px}
.qty-box{display:flex;align-items:center;justify-content:center;padding:12px;background:#fff;border-radius:14px;box-shadow:0 1px 3px rgba(0,0,0,.04);margin-top:16px}
.qty-box input{width:60px;text-align:center;font-size:17px;font-weight:700;border:none;background:transparent}
.cart-item{display:flex;gap:12px;padding:16px;background:#fff;border-bottom:.5px solid #e5e5ea;align-items:center}
.cart-item:last-child{border-bottom:none}
.cart-item .cinfo{flex:1}
.cart-item .cinfo .n{font-size:14px;font-weight:600;margin-bottom:2px}
.cart-item .cinfo .p{font-size:14px;font-weight:700;color:#ff3b30}
.cart-item .cinfo .q{font-size:12px;color:#8e8e93;margin-top:2px}
.cart-item .del{color:#ff3b30;font-size:20px;text-decoration:none;padding:8px}
.order-summary{background:#fff;border-radius:18px;padding:20px;margin:16px}
.order-summary .row{display:flex;justify-content:space-between;padding:8px 0;font-size:15px}
.order-summary .row.total{border-top:.5px solid #e5e5ea;margin-top:8px;padding-top:14px;font-size:20px;font-weight:700}
.order-summary .row.total .val{color:#ff3b30}
.order-card{background:#fff;border-radius:18px;padding:18px;margin-bottom:12px}
.order-card .oh{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.order-card .oid{font-size:12px;color:#8e8e93;font-weight:600}
.order-card .oitems{font-size:13px;color:#3a3a3c;margin:8px 0;line-height:1.5}
.order-card .ofoot{display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:.5px solid #e5e5ea;margin-top:10px}
.order-card .ototal{font-size:17px;font-weight:700;color:#ff3b30}
.status-badge{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700}
.status-PENDING{background:rgba(255,149,0,.15);color:#c56a00}
.status-CONFIRMED{background:rgba(0,122,255,.15);color:#0062cc}
.status-DELIVERED{background:rgba(52,199,89,.15);color:#248a3d}
.status-CANCELLED{background:rgba(255,59,48,.15);color:#c7000e}
.admin-frame{width:1200px;max-width:95vw;background:#f2f2f7;border-radius:20px;box-shadow:0 30px 80px -20px rgba(0,0,0,.35);overflow:hidden;min-height:600px}
.admin-nav{background:rgba(255,255,255,.85);padding:16px 28px;display:flex;justify-content:space-between;align-items:center;border-bottom:.5px solid rgba(0,0,0,.12);flex-wrap:wrap;gap:8px}
.admin-nav h1{font-size:18px;font-weight:700}
.admin-nav a{color:#1c1c1e;text-decoration:none;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:500;margin-left:4px}
.admin-nav a:hover{background:rgba(0,0,0,.05)}
.admin-body{padding:24px 28px}
.admin-table{width:100%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.admin-table table{width:100%;border-collapse:collapse;font-size:14px}
.admin-table th,.admin-table td{padding:14px 18px;text-align:left;border-bottom:.5px solid #e5e5ea}
.admin-table th{background:#f9f9fb;color:#8e8e93;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.admin-table tr:hover{background:#f9f9fb}
.admin-table tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600}
.b-in{background:rgba(52,199,89,.15);color:#248a3d}
.b-out{background:rgba(255,59,48,.15);color:#c7000e}
.b-info{background:rgba(0,122,255,.15);color:#0062cc}
.admin-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.acard{background:#fff;border-radius:16px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.acard .v{font-size:28px;font-weight:700;margin-bottom:4px;letter-spacing:-.8px}
.acard .l{font-size:12px;color:#8e8e93;font-weight:500}
.btn-sm{padding:8px 14px;font-size:13px;border-radius:10px;display:inline-block;text-decoration:none;color:#fff;font-weight:600;border:none;cursor:pointer}

/* ===== MOBILE: Hide phone frame on real phones ===== */
@media (max-width: 500px) {
  body {
    padding: 0 !important;
    background: #f2f2f7 !important;
    align-items: stretch !important;
  }
  .phone {
    width: 100% !important;
    height: 100vh !important;
    height: 100dvh !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    max-width: 100% !important;
  }
  .notch {
    display: none !important;
  }
  .status {
    display: none !important;
  }
  .screen {
    padding-bottom: 100px !important;
  }
  .appbar {
    padding-top: 16px !important;
  }
  .auth-logo {
    padding-top: 40px !important;
  }
  .nav {
    padding-bottom: max(22px, env(safe-area-inset-bottom)) !important;
  }
}

@media (max-width: 500px){
  body{padding:0 !important;background:#f2f2f7 !important;display:block !important;align-items:initial !important;min-height:100vh !important}
  .phone{width:100% !important;height:100vh !important;height:100dvh !important;border-radius:0 !important;box-shadow:none !important;max-width:100% !important;min-height:100vh !important}
  .notch{display:none !important}
  .status{display:none !important}
  .appbar{padding-top:20px !important}
  .auth-logo{padding-top:50px !important}
  .screen{padding-bottom:100px !important}
}

@media (max-width:600px){html,body{padding:0!important;margin:0!important;background:#f2f2f7!important;display:block!important}.phone{width:100vw!important;max-width:100vw!important;height:100vh!important;border-radius:0!important;box-shadow:none!important;margin:0!important;background:#fff!important}.notch,.status{display:none!important}.screen{padding-bottom:90px!important}.appbar{padding-top:20px!important}.auth-logo{padding-top:50px!important}}
"""

def fh():
    h = ""
    for cat, msg in session.pop("_flashes", []):
        cls = "al-ok" if cat == "success" else "al-err"
        ico = "OK" if cat == "success" else "!"
        h += '<div class="alert ' + cls + '">' + ico + ' ' + msg + '</div>'
    return h

def cart_count():
    return sum(session.get("cart", {}).values())

def pp(body, nav="home"):
    cnt = cart_count()
    badge = '<span class="badge-dot">' + str(cnt) + '</span>' if cnt > 0 else ""
    links = [
        ("wallet", "🏠", "Home", "home"),
        ("shop", "🛍️", "Shop", "shop"),
        ("cart", "🛒", "Cart", "cart"),
        ("orders", "📦", "Orders", "orders"),
        ("profile", "👤", "Me", "me"),
    ]
    nav_html = '<div class="nav">'
    for endpoint, icon, label, key in links:
        on = " on" if nav == key else ""
        b = badge if key == "cart" else ""
        nav_html += '<a href="' + url_for(endpoint) + '" class="' + on.strip() + '"><span class="ni">' + icon + '</span>' + b + '<span>' + label + '</span></a>'
    nav_html += "</div>"
    return '<!doctype html><html><head><meta charset="utf-8"><link rel="manifest" href="/static/manifest.json"><meta name="theme-color" content="#ff3b30"><meta name="viewport" content="width=device-width,initial-scale=1"><title>iCare Wallet</title><style>' + CSS + '</style></head><body><div class="phone"><div class="notch"></div><div class="status"><span>9:41</span><span>Signal</span></div><div class="screen">' + fh() + body + '</div>' + nav_html + '</div></body></html>'

@app.route("/")
def index():
    return redirect(url_for("wallet") if "user_id" in session else url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    step = request.args.get("step", "phone")
    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "send_otp":
            phone = request.form.get("phone", "").strip()
            if not phone.startswith("09") or len(phone) < 9:
                flash("Phone format wrong (09xxxxxxxxx)", "error")
            else:
                conn = get_db()
                exists = conn.execute("SELECT id FROM users WHERE phone=?", (phone,)).fetchone()
                conn.close()
                if exists:
                    flash("Phone already registered", "error")
                else:
                    otp = str(random.randint(100000, 999999))
                    session["otp"] = otp
                    session["otp_phone"] = phone
                    session["otp_time"] = time.time()
                    print("")
                    print("=" * 50)
                    print("SMS TO: " + phone)
                    print("OTP CODE: " + otp)
                    print("=" * 50)
                    print("")
                    flash("SMS sent! OTP in terminal", "success")
                    return redirect(url_for("register", step="verify"))

        elif action == "verify":
            otp_input = request.form.get("otp", "").strip()
            name = request.form.get("name", "").strip()
            pin = request.form.get("pin", "").strip()
            birthdate = request.form.get("birthdate", "").strip()
            saved_otp = session.get("otp", "")
            otp_time = session.get("otp_time", 0)
            phone = session.get("otp_phone", "")

            if not phone:
                flash("No phone in session", "error")
                return redirect(url_for("register"))
            elif time.time() - otp_time > 300:
                flash("OTP expired", "error")
                return redirect(url_for("register"))
            elif otp_input != saved_otp:
                flash("Wrong OTP", "error")
            elif not name:
                flash("Name required", "error")
            elif not birthdate:
                flash("Birthdate required", "error")
            elif not pin.isdigit() or not (4 <= len(pin) <= 6):
                flash("PIN 4-6 digits", "error")
            else:
                conn = get_db()
                try:
                    conn.execute("INSERT INTO users (phone,name,pin,balance,birthdate,phone_verified) VALUES (?,?,?,?,?,?)",
                                 (phone, name, hp(pin), 0, birthdate, 1))
                    conn.commit()
                    flash("Phone verified! Account created", "success")
                    session.pop("otp", None)
                    session.pop("otp_phone", None)
                    session.pop("otp_time", None)
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("Phone already exists", "error")
                finally:
                    conn.close()

    if step == "verify":
        phone = session.get("otp_phone", "")
        body = '<div class="auth-logo"><div class="lbox">&#10084;</div><h1>iCare Wallet</h1><p>VERIFY PHONE</p></div>'
        body += '<div class="auth-form"><h3>OTP Verification</h3>'
        body += '<p style="font-size:13px;color:#8e8e93;margin-bottom:8px">Check terminal for OTP code</p>'
        body += '<p style="font-size:14px;color:#1c1c1e;font-weight:600;margin-bottom:16px">Phone: ' + phone + '</p>'
        body += '<form method="post"><input type="hidden" name="action" value="verify">'
        body += '<label>OTP Code (6 digits)</label>'
        body += '<input name="otp" placeholder="000000" maxlength="6" pattern="[0-9]{6}" required style="text-align:center;font-size:24px;letter-spacing:8px;font-weight:700">'
        body += '<label>Full Name</label>'
        body += '<input name="name" placeholder="Your full name" required>'
        body += '<label>Birthdate</label>'
        body += '<input name="birthdate" type="date" required>'
        body += '<label>PIN (4-6 digits)</label>'
        body += '<input name="pin" type="password" placeholder="0000" pattern="[0-9]{4,6}" required>'
        body += '<button class="btn">Verify and Register</button></form>'
        body += '<p style="text-align:center;margin-top:20px"><a href="' + url_for("register") + '" style="color:#ff3b30;text-decoration:none;font-weight:600">Change phone</a></p></div>'
    else:
        body = '<div class="auth-logo"><div class="lbox">&#10084;</div><h1>iCare Wallet</h1><p>SECURE - TRUSTED - FAST</p></div>'
        body += '<div class="auth-form"><h3>Create Account</h3>'
        body += '<p style="font-size:13px;color:#8e8e93">Enter phone - we will send SMS OTP</p>'
        body += '<form method="post"><input type="hidden" name="action" value="send_otp">'
        body += '<label>Phone Number</label>'
        body += '<input name="phone" placeholder="09xxxxxxxxx" pattern="09[0-9]{7,9}" required autofocus>'
        body += '<button class="btn">Send SMS OTP</button></form>'
        body += '<p style="text-align:center;margin-top:20px"><a href="' + url_for("login") + '" style="color:#ff3b30;text-decoration:none;font-weight:600">Login</a></p></div>'

    return '<!doctype html><html><head><meta charset="utf-8"><link rel="manifest" href="/static/manifest.json"><meta name="theme-color" content="#ff3b30"><title>Register</title><style>' + CSS + '</style></head><body><div class="phone"><div class="notch"></div><div class="status"><span>9:41</span><span>Sig</span></div><div class="screen">' + fh() + body + '</div></div></body></html>'

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"].strip()
        pin = request.form["pin"].strip()
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE phone=? AND pin=?", (phone, hp(pin))).fetchone()
        conn.close()
        if u and u["is_active"]:
            session["user_id"] = u["id"]
            session["user_name"] = u["name"]
            return redirect(url_for("wallet"))
        flash("Phone/PIN မှားနေပါ", "error")
    body = '<div class="auth-logo"><div class="lbox">❤</div><h1>iCare Wallet</h1><p>SECURE - TRUSTED - FAST</p></div><div class="auth-form"><h3>Login</h3><form method="post"><label>Phone</label><input name="phone" placeholder="09xxxxxxxxx" required><label>PIN</label><input name="pin" type="password" required><button class="btn">ဝင်ရောက်</button></form><p style="text-align:center;margin-top:20px"><a href="' + url_for("register") + '" style="color:#ff3b30;text-decoration:none;font-weight:700">Register</a></p><p style="text-align:center;margin-top:14px"><a href="' + url_for("admin_login") + '" style="font-size:12px;color:#c7c7cc;text-decoration:none">Admin Login</a></p></div>'
    return '<!doctype html><html><head><meta charset="utf-8"><link rel="manifest" href="/static/manifest.json"><meta name="theme-color" content="#ff3b30"><title>Login</title><style>' + CSS + '</style></head><body><div class="phone"><div class="notch"></div><div class="status"><span>9:41</span><span>Sig</span></div><div class="screen">' + fh() + body + '</div></div></body></html>'

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/wallet")
@login_required
def wallet():
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    txns = conn.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5", (session["user_id"],)).fetchall()
    sent = conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE user_id=? AND type='SEND'", (session["user_id"],)).fetchone()[0]
    recv = conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE user_id=? AND type IN ('TOPUP','RECEIVE')", (session["user_id"],)).fetchone()[0]
    conn.close()
    txn_rows = ""
    for t in txns:
        is_in = t["type"] in ("TOPUP", "RECEIVE")
        cls = "in" if is_in else "out"
        bg = "bg-in" if is_in else "bg-out"
        sign = "+" if is_in else "-"
        icons = {"TOPUP": "$", "RECEIVE": "v", "WITHDRAW": "W", "SEND": "^", "ADMIN_ADJUST": "A", "PURCHASE": "C"}
        txn_rows += '<div class="txn"><div class="av ' + bg + '">' + icons.get(t["type"], "?") + '</div><div class="info"><div class="t">' + t["type"] + '</div><div class="d">' + t["created_at"][:16] + '</div></div><div class="amt ' + cls + '">' + sign + format(t["amount"], ",.0f") + '</div></div>'
    empty = '<div style="padding:40px;text-align:center;color:#c7c7cc;font-size:13px">No transactions</div>'
    body = '<div class="balance-wrap"><div class="balance-card"><div class="bc-head"><div class="brand">iCare Wallet</div><div>...</div></div><div class="bc-label">Balance</div><div class="bc-amount">' + format(u["balance"], ",.0f") + ' Ks</div><div class="bc-user">' + u["name"] + ' - ' + u["phone"] + '</div><div class="bc-actions"><a href="' + url_for("topup") + '">Top-up</a><a href="' + url_for("transfer") + '">Transfer</a></div></div></div>'
    body += '<div class="stats"><div class="stat"><div class="v" style="color:#34c759">+' + format(recv, ",.0f") + '</div><div class="l">Income</div></div><div class="stat"><div class="v" style="color:#ff3b30">-' + format(sent, ",.0f") + '</div><div class="l">Expense</div></div></div>'
    body += '<div class="section"><div class="section-head"><h3>Services</h3></div><div class="actions-grid"><a href="' + url_for("shop") + '" class="action"><div class="ico">🛍️</div><div class="lbl">Shop</div></a><a href="' + url_for("topup") + '" class="action"><div class="ico">💰</div><div class="lbl">Top-up</div></a><a href="' + url_for("transfer") + '" class="action"><div class="ico">📤</div><div class="lbl">Transfer</div></a><a href="' + url_for("history") + '" class="action"><div class="ico">📜</div><div class="lbl">History</div></a></div></div>'
    body += '<div class="section" style="padding-top:0"><div class="section-head"><h3>Recent</h3><a href="' + url_for("history") + '">All</a></div><div class="txn-list">' + (txn_rows or empty) + '</div></div>'
    return pp(body, "home")

@app.route("/topup", methods=["GET", "POST"])
@login_required
def topup():
    if request.method == "POST":
        amt = float(request.form["amount"])
        if amt <= 0:
            flash("Invalid amount", "error")
        else:
            conn = get_db()
            u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
            nb = u["balance"] + amt
            conn.execute("UPDATE users SET balance=? WHERE id=?", (nb, u["id"]))
            conn.execute("INSERT INTO transactions (user_id,type,amount,balance_after,note) VALUES (?,?,?,?,?)", (u["id"], "TOPUP", amt, nb, "Top-up"))
            conn.commit()
            conn.close()
            flash("Top-up " + format(amt, ",.0f") + " Ks success", "success")
            return redirect(url_for("wallet"))
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Top-up</h2></div><div class="form-wrap"><form method="post"><label>Amount (Ks)</label><input name="amount" type="number" required><button class="btn">Top-up</button></form></div>'
    return pp(body)

@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    if request.method == "POST":
        amt = float(request.form["amount"])
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        if amt <= 0:
            flash("Invalid", "error")
        elif amt > u["balance"]:
            flash("Insufficient balance", "error")
        else:
            nb = u["balance"] - amt
            conn.execute("UPDATE users SET balance=? WHERE id=?", (nb, u["id"]))
            conn.execute("INSERT INTO transactions (user_id,type,amount,balance_after,note) VALUES (?,?,?,?,?)", (u["id"], "WITHDRAW", amt, nb, "Withdraw"))
            conn.commit()
            conn.close()
            flash("Withdraw success", "success")
            return redirect(url_for("wallet"))
        conn.close()
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Withdraw</h2></div><div class="form-wrap"><form method="post"><label>Amount (Ks)</label><input name="amount" type="number" required><button class="btn">Withdraw</button></form></div>'
    return pp(body)

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        to = request.form["to"].strip()
        amt = float(request.form["amount"])
        pin = request.form["pin"].strip()
        conn = get_db()
        me = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        target = conn.execute("SELECT * FROM users WHERE phone=?", (to,)).fetchone()
        if not target:
            flash("Account not found", "error")
        elif target["id"] == me["id"]:
            flash("Cannot transfer to yourself", "error")
        elif me["pin"] != hp(pin):
            flash("Wrong PIN", "error")
        elif amt <= 0 or amt > me["balance"]:
            flash("Insufficient balance", "error")
        else:
            nb1 = me["balance"] - amt
            nb2 = target["balance"] + amt
            conn.execute("UPDATE users SET balance=? WHERE id=?", (nb1, me["id"]))
            conn.execute("UPDATE users SET balance=? WHERE id=?", (nb2, target["id"]))
            conn.execute("INSERT INTO transactions (user_id,type,amount,balance_after,note,related_user_id) VALUES (?,?,?,?,?,?)", (me["id"], "SEND", amt, nb1, "Send", target["id"]))
            conn.execute("INSERT INTO transactions (user_id,type,amount,balance_after,note,related_user_id) VALUES (?,?,?,?,?,?)", (target["id"], "RECEIVE", amt, nb2, "Receive", me["id"]))
            conn.commit()
            conn.close()
            flash("Transfer success", "success")
            return redirect(url_for("wallet"))
        conn.close()
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Transfer</h2></div><div class="form-wrap"><form method="post"><label>Phone</label><input name="to" required><label>Amount (Ks)</label><input name="amount" type="number" required><label>PIN</label><input name="pin" type="password" required><button class="btn">Transfer</button></form></div>'
    return pp(body)

@app.route("/history")
@login_required
def history():
    conn = get_db()
    txns = conn.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 50", (session["user_id"],)).fetchall()
    conn.close()
    rows = ""
    for t in txns:
        is_in = t["type"] in ("TOPUP", "RECEIVE")
        cls = "in" if is_in else "out"
        sign = "+" if is_in else "-"
        rows += '<div class="txn"><div class="info"><div class="t">' + t["type"] + '</div><div class="d">' + t["created_at"][:16] + '</div></div><div class="amt ' + cls + '">' + sign + format(t["amount"], ",.0f") + '</div></div>'
    empty = '<div style="padding:40px;text-align:center;color:#c7c7cc">No transactions</div>'
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>History</h2></div><div class="section"><div class="txn-list">' + (rows or empty) + '</div></div>'
    return pp(body, "history")

@app.route("/shop")
@login_required
def shop():
    cat = request.args.get("cat", "All")
    conn = get_db()
    cats = ["All"] + [r[0] for r in conn.execute("SELECT DISTINCT category FROM products WHERE is_active=1 AND category IS NOT NULL").fetchall()]
    if cat == "All":
        products = conn.execute("SELECT * FROM products WHERE is_active=1 ORDER BY id DESC").fetchall()
    else:
        products = conn.execute("SELECT * FROM products WHERE is_active=1 AND category=? ORDER BY id DESC", (cat,)).fetchall()
    conn.close()
    cat_html = ""
    for c in cats:
        on = " on" if c == cat else ""
        cat_html += '<a href="' + url_for("shop", cat=c) + '" class="cat-chip' + on + '">' + c + '</a>'
    prod_html = ""
    for p in products:
        stock_tag = '<div class="stock-tag">' + str(p["stock"]) + '</div>' if p["stock"] > 0 else '<div class="stock-tag" style="background:rgba(255,59,48,.85)">OUT</div>'
        prod_html += '<a href="' + url_for("product_detail", pid=p["id"]) + '" class="product"><div class="pimg">' + (p["image"] or "📦") + stock_tag + '</div><div class="pbody"><div class="ptitle">' + p["name"] + '</div><div class="pcat">' + (p["category"] or "General") + '</div><div class="pprice">' + format(p["price"], ",.0f") + ' Ks</div></div></a>'
    empty = '<div style="padding:40px;text-align:center;color:#c7c7cc;grid-column:span 2">No products</div>'
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Shop</h2><a href="' + url_for("cart") + '">🛒</a></div><div class="cat-scroll">' + cat_html + '</div><div class="product-grid">' + (prod_html or empty) + '</div>'
    return pp(body, "shop")

@app.route("/product/<int:pid>")
@login_required
def product_detail(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE id=? AND is_active=1", (pid,)).fetchone()
    conn.close()
    if not p:
        return redirect(url_for("shop"))
    stock_status = "Stock: " + str(p["stock"]) if p["stock"] > 0 else "Out of stock"
    disabled = "disabled" if p["stock"] <= 0 else ""
    body = '<div class="appbar"><a href="' + url_for("shop") + '">&lt;</a><h2>Product</h2><a href="' + url_for("cart") + '">🛒</a></div><div class="product-detail"><div class="big-img">' + (p["image"] or "📦") + '</div><h2>' + p["name"] + '</h2><div style="font-size:13px;color:#8e8e93">' + (p["category"] or "General") + '</div><div class="price">' + format(p["price"], ",.0f") + ' Ks</div><div class="stock-info">' + stock_status + '</div><div class="desc">' + (p["description"] or "") + '</div><form method="post" action="' + url_for("add_to_cart", pid=pid) + '"><div class="qty-box"><input type="number" name="qty" value="1" min="1" max="' + str(p["stock"]) + '"></div><button class="btn" ' + disabled + '>Add to Cart</button></form></div>'
    return pp(body, "shop")

@app.route("/cart/add/<int:pid>", methods=["POST"])
@login_required
def add_to_cart(pid):
    qty = int(request.form.get("qty", 1))
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not p or p["stock"] <= 0:
        flash("Not available", "error")
        return redirect(url_for("shop"))
    cart = session.get("cart", {})
    cart[str(pid)] = min(cart.get(str(pid), 0) + qty, p["stock"])
    session["cart"] = cart
    flash("Added to cart", "success")
    return redirect(url_for("cart"))

@app.route("/cart")
@login_required
def cart():
    cart_data = session.get("cart", {})
    conn = get_db()
    items = []
    total = 0
    for pid, qty in cart_data.items():
        p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p:
            sub = p["price"] * qty
            total += sub
            items.append({"p": p, "qty": qty, "sub": sub})
    conn.close()
    items_html = ""
    for it in items:
        items_html += '<div class="cart-item"><div class="cinfo"><div class="n">' + it["p"]["name"] + '</div><div class="p">' + format(it["p"]["price"], ",.0f") + ' Ks</div><div class="q">Qty: ' + str(it["qty"]) + '</div></div><a href="' + url_for("remove_from_cart", pid=it["p"]["id"]) + '" class="del">X</a></div>'
    empty = '<div style="padding:80px 20px;text-align:center;color:#8e8e93"><div style="font-size:64px;margin-bottom:16px">🛒</div><div style="font-size:17px;font-weight:600">Cart is empty</div></div>'
    summary = ""
    if items:
        summary = '<div class="order-summary"><div class="row total"><span>Total</span><span class="val">' + format(total, ",.0f") + ' Ks</span></div></div><div style="padding:0 16px 16px"><a href="' + url_for("checkout") + '" class="btn">Checkout</a></div>'
    body = '<div class="appbar"><a href="' + url_for("shop") + '">&lt;</a><h2>Cart</h2></div>' + (items_html and '<div style="padding:16px"><div style="background:#fff;border-radius:18px">' + items_html + '</div></div>' or empty) + summary
    return pp(body, "cart")

@app.route("/cart/remove/<int:pid>")
@login_required
def remove_from_cart(pid):
    cart_data = session.get("cart", {})
    cart_data.pop(str(pid), None)
    session["cart"] = cart_data
    flash("Removed", "success")
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_data = session.get("cart", {})
    if not cart_data:
        flash("Cart is empty", "error")
        return redirect(url_for("cart"))
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    items = []
    total = 0
    for pid, qty in cart_data.items():
        p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p:
            sub = p["price"] * qty
            total += sub
            items.append({"p": p, "qty": qty, "sub": sub})
    if request.method == "POST":
        pin = request.form["pin"].strip()
        if u["pin"] != hp(pin):
            flash("Wrong PIN", "error")
        elif u["balance"] < total:
            flash("Insufficient balance", "error")
        else:
            nb = u["balance"] - total
            cur = conn.cursor()
            cur.execute("INSERT INTO orders (user_id,total,status) VALUES (?,?,?)", (u["id"], total, "PENDING"))
            oid = cur.lastrowid
            for it in items:
                cur.execute("INSERT INTO order_items (order_id,product_name,price,quantity,subtotal) VALUES (?,?,?,?,?)", (oid, it["p"]["name"], it["p"]["price"], it["qty"], it["sub"]))
                cur.execute("UPDATE products SET stock=stock-? WHERE id=?", (it["qty"], it["p"]["id"]))
            cur.execute("UPDATE users SET balance=? WHERE id=?", (nb, u["id"]))
            cur.execute("INSERT INTO transactions (user_id,type,amount,balance_after,note) VALUES (?,?,?,?,?)", (u["id"], "PURCHASE", total, nb, "Order " + str(oid)))
            conn.commit()
            conn.close()
            session["cart"] = {}
            flash("Order placed! #" + str(oid), "success")
            return redirect(url_for("orders"))
    conn.close()
    items_html = ""
    for it in items:
        items_html += '<div class="cart-item"><div class="cinfo"><div class="n">' + it["p"]["name"] + '</div><div class="q">' + str(it["qty"]) + ' x ' + format(it["p"]["price"], ",.0f") + '</div></div><div style="font-weight:700;color:#ff3b30">' + format(it["sub"], ",.0f") + '</div></div>'
    body = '<div class="appbar"><a href="' + url_for("cart") + '">&lt;</a><h2>Checkout</h2></div><div style="padding:16px"><div style="background:#fff;border-radius:18px">' + items_html + '</div></div><div class="order-summary"><div class="row"><span>Total</span><span>' + format(total, ",.0f") + ' Ks</span></div><div class="row"><span>Your balance</span><span>' + format(u["balance"], ",.0f") + ' Ks</span></div><div class="row total"><span>Pay</span><span class="val">' + format(total, ",.0f") + ' Ks</span></div></div><div class="form-wrap"><form method="post"><label>PIN</label><input name="pin" type="password" required><button class="btn">Pay Now</button></form></div>'
    return pp(body, "cart")

@app.route("/orders")
@login_required
def orders():
    conn = get_db()
    orders_list = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    orders_html = ""
    for o in orders_list:
        items = conn.execute("SELECT * FROM order_items WHERE order_id=?", (o["id"],)).fetchall()
        items_txt = ", ".join([i["product_name"] + " x" + str(i["quantity"]) for i in items])
        orders_html += '<div class="order-card"><div class="oh"><div class="oid">Order #' + str(o["id"]) + '</div><div class="status-badge status-' + o["status"] + '">' + o["status"] + '</div></div><div class="oitems">' + items_txt + '</div><div class="ofoot"><div style="font-size:12px;color:#8e8e93">' + o["created_at"][:16] + '</div><div class="ototal">' + format(o["total"], ",.0f") + ' Ks</div></div></div>'
    conn.close()
    empty = '<div style="padding:60px 20px;text-align:center;color:#8e8e93"><div style="font-size:64px;margin-bottom:16px">📦</div><div style="font-size:17px;font-weight:600">No orders yet</div></div>'
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Orders</h2></div><div style="padding:16px">' + (orders_html or empty) + '</div>'
    return pp(body, "orders")

@app.route("/profile")
@login_required
def profile():
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    body = '<div class="appbar"><a href="' + url_for("wallet") + '">&lt;</a><h2>Profile</h2></div><div class="section"><div style="background:#fff;border-radius:20px;padding:24px;text-align:center"><div style="width:80px;height:80px;border-radius:50%;margin:0 auto 14px;background:linear-gradient(135deg,#ff453a,#d70015);color:#fff;font-size:36px;display:flex;align-items:center;justify-content:center;font-weight:700">' + u["name"][0].upper() + '</div><h3 style="font-size:20px;font-weight:700">' + u["name"] + '</h3><p style="font-size:13px;color:#8e8e93;margin-top:4px">' + u["phone"] + '</p><div style="margin-top:20px;padding:16px;background:#f2f2f7;border-radius:14px"><div style="font-size:12px;color:#8e8e93">Balance</div><div style="font-size:28px;font-weight:700;color:#ff3b30;margin-top:6px">' + format(u["balance"], ",.2f") + ' Ks</div></div></div><div style="margin-top:16px;background:#fff;border-radius:20px;overflow:hidden"><a href="' + url_for("orders") + '" style="display:block;padding:18px;text-decoration:none;color:#1c1c1e;border-bottom:.5px solid #e5e5ea;font-weight:600">My Orders</a><a href="' + url_for("history") + '" style="display:block;padding:18px;text-decoration:none;color:#1c1c1e;border-bottom:.5px solid #e5e5ea;font-weight:600">History</a><a href="' + url_for("logout") + '" style="display:block;padding:18px;text-decoration:none;color:#ff3b30;font-weight:600">Logout</a></div></div>'
    return pp(body, "me")

def admin_page(title, body):
    nav = '<div class="admin-nav"><h1>iCare Admin</h1><div><a href="' + url_for("admin_dashboard") + '">Dashboard</a><a href="' + url_for("admin_users") + '">Users</a><a href="' + url_for("admin_products") + '">Products</a><a href="' + url_for("admin_orders") + '">Orders</a><a href="' + url_for("admin_logout") + '">Logout</a></div></div>'
    return '<!doctype html><html><head><meta charset="utf-8"><link rel="manifest" href="/static/manifest.json"><meta name="theme-color" content="#ff3b30"><title>' + title + '</title><style>' + CSS + '</style></head><body><div class="admin-frame">' + nav + '<div class="admin-body">' + fh() + body + '</div></div></body></html>'

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form["username"]
        p = hashlib.sha256(request.form["password"].encode()).hexdigest()
        conn = get_db()
        a = conn.execute("SELECT * FROM admins WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if a:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials", "error")
    body = '<div style="max-width:420px;margin:60px auto;background:#fff;padding:32px;border-radius:20px"><h2 style="text-align:center;margin-bottom:20px">iCare Admin</h2><form method="post"><label style="display:block;font-size:13px;color:#8e8e93;margin-bottom:6px">Username</label><input name="username" value="admin" style="width:100%;padding:14px;background:#f2f2f7;border:none;border-radius:12px;margin-bottom:14px" required><label style="display:block;font-size:13px;color:#8e8e93;margin-bottom:6px">Password</label><input name="password" type="password" style="width:100%;padding:14px;background:#f2f2f7;border:none;border-radius:12px" required><button class="btn">Login</button></form><p style="text-align:center;margin-top:16px;font-size:12px;color:#c7c7cc">admin / admin123</p></div>'
    return admin_page("Login", body)

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    products_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status!='CANCELLED'").fetchone()[0]
    recent = conn.execute("SELECT o.*, u.name FROM orders o LEFT JOIN users u ON u.id=o.user_id ORDER BY o.id DESC LIMIT 5").fetchall()
    conn.close()
    rows = ""
    for o in recent:
        cls = "b-info" if o["status"] == "PENDING" else ("b-in" if o["status"] == "DELIVERED" else "b-out")
        rows += '<tr><td>#' + str(o["id"]) + '</td><td>' + (o["name"] or "-") + '</td><td><b>' + format(o["total"], ",.0f") + ' Ks</b></td><td><span class="badge ' + cls + '">' + o["status"] + '</span></td><td>' + o["created_at"][:16] + '</td></tr>'
    body = '<div class="admin-stats"><div class="acard"><div class="v">' + str(users_count) + '</div><div class="l">Users</div></div><div class="acard"><div class="v">' + str(products_count) + '</div><div class="l">Products</div></div><div class="acard"><div class="v">' + str(orders_count) + '</div><div class="l">Orders</div></div><div class="acard"><div class="v">' + format(revenue, ",.0f") + '</div><div class="l">Revenue (Ks)</div></div></div><div class="admin-table"><table><thead><tr><th>ID</th><th>User</th><th>Total</th><th>Status</th><th>Date</th></tr></thead><tbody>' + (rows or '<tr><td colspan="5" style="text-align:center;padding:40px;color:#c7c7cc">No orders</td></tr>') + '</tbody></table></div>'
    return admin_page("Dashboard", body)

@app.route("/admin/users")
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()
    rows = ""
    for u in users:
        st = '<span class="badge b-in">Active</span>' if u["is_active"] else '<span class="badge b-out">Disabled</span>'
        tgl = "Disable" if u["is_active"] else "Enable"
        rows += '<tr><td>' + str(u["id"]) + '</td><td><b>' + u["name"] + '</b><br><span style="color:#8e8e93;font-size:12px">' + u["phone"] + '</span></td><td><b style="color:#ff3b30">' + format(u["balance"], ",.0f") + ' Ks</b></td><td>' + st + '</td><td><a href="' + url_for("admin_toggle_user", uid=u["id"]) + '" class="btn-sm" style="background:#007aff">' + tgl + '</a></td></tr>'
    body = '<div class="admin-table"><table><thead><tr><th>ID</th><th>User</th><th>Balance</th><th>Status</th><th></th></tr></thead><tbody>' + (rows or '<tr><td colspan="5" style="text-align:center;padding:40px;color:#c7c7cc">No users</td></tr>') + '</tbody></table></div>'
    return admin_page("Users", body)

@app.route("/admin/user/<int:uid>/toggle")
@admin_required
def admin_toggle_user(uid):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (0 if u["is_active"] else 1, uid))
    conn.commit()
    conn.close()
    flash("Status changed", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/products")
@admin_required
def admin_products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    rows = ""
    for p in products:
        rows += '<tr><td style="font-size:24px">' + (p["image"] or "📦") + '</td><td><b>' + p["name"] + '</b><br><span style="color:#8e8e93;font-size:12px">' + (p["category"] or "") + '</span></td><td><b style="color:#ff3b30">' + format(p["price"], ",.0f") + ' Ks</b></td><td>' + str(p["stock"]) + '</td><td><a href="' + url_for("admin_product_edit", pid=p["id"]) + '" class="btn-sm" style="background:#007aff">Edit</a> <a href="' + url_for("admin_product_delete", pid=p["id"]) + '" class="btn-sm" style="background:#ff3b30">Del</a></td></tr>'
    body = '<div style="margin-bottom:16px"><a href="' + url_for("admin_product_new") + '" class="btn-sm" style="padding:12px 20px;background:linear-gradient(135deg,#ff453a,#d70015)">+ New Product</a></div><div class="admin-table"><table><thead><tr><th>Img</th><th>Product</th><th>Price</th><th>Stock</th><th>Actions</th></tr></thead><tbody>' + (rows or '<tr><td colspan="5" style="text-align:center;padding:40px;color:#c7c7cc">No products</td></tr>') + '</tbody></table></div>'
    return admin_page("Products", body)

@app.route("/admin/product/new", methods=["GET", "POST"])
@admin_required
def admin_product_new():
    if request.method == "POST":
        conn = get_db()
        conn.execute("INSERT INTO products (name,description,price,stock,category,image) VALUES (?,?,?,?,?,?)", (request.form["name"], request.form.get("description", ""), float(request.form["price"]), int(request.form["stock"]), request.form.get("category", ""), request.form.get("image", "📦") or "📦"))
        conn.commit()
        conn.close()
        flash("Product added", "success")
        return redirect(url_for("admin_products"))
    body = '<div class="admin-table" style="padding:28px"><h2 style="margin-bottom:20px">New Product</h2><form method="post" style="display:grid;gap:14px;max-width:600px"><label>Name</label><input name="name" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Description</label><textarea name="description" rows="3" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px;font-family:inherit"></textarea><label>Price</label><input name="price" type="number" step="1" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Stock</label><input name="stock" type="number" value="0" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Category</label><input name="category" placeholder="Electronics" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px"><label>Icon</label><input name="image" value="📦" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px"><button type="submit" class="btn" style="margin-top:0">Save</button></form></div>'
    return admin_page("New Product", body)

@app.route("/admin/product/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def admin_product_edit(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not p:
        conn.close()
        return redirect(url_for("admin_products"))
    if request.method == "POST":
        conn.execute("UPDATE products SET name=?,description=?,price=?,stock=?,category=?,image=? WHERE id=?", (request.form["name"], request.form.get("description", ""), float(request.form["price"]), int(request.form["stock"]), request.form.get("category", ""), request.form.get("image", "📦"), pid))
        conn.commit()
        conn.close()
        flash("Updated", "success")
        return redirect(url_for("admin_products"))
    conn.close()
    body = '<div class="admin-table" style="padding:28px"><h2 style="margin-bottom:20px">Edit Product</h2><form method="post" style="display:grid;gap:14px;max-width:600px"><label>Name</label><input name="name" value="' + p["name"] + '" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Description</label><textarea name="description" rows="3" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px;font-family:inherit">' + (p["description"] or "") + '</textarea><label>Price</label><input name="price" type="number" value="' + str(p["price"]) + '" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Stock</label><input name="stock" type="number" value="' + str(p["stock"]) + '" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px" required><label>Category</label><input name="category" value="' + (p["category"] or "") + '" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px"><label>Icon</label><input name="image" value="' + (p["image"] or "") + '" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px"><button type="submit" class="btn" style="margin-top:0">Save</button></form></div>'
    return admin_page("Edit Product", body)

@app.route("/admin/product/<int:pid>/delete")
@admin_required
def admin_product_delete(pid):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("Deleted", "success")
    return redirect(url_for("admin_products"))

@app.route("/admin/orders")
@admin_required
def admin_orders():
    conn = get_db()
    orders_list = conn.execute("SELECT o.*, u.name, u.phone FROM orders o LEFT JOIN users u ON u.id=o.user_id ORDER BY o.id DESC").fetchall()
    conn.close()
    rows = ""
    for o in orders_list:
        cls = "b-info" if o["status"] == "PENDING" else ("b-in" if o["status"] == "DELIVERED" else "b-out")
        rows += '<tr><td>#' + str(o["id"]) + '</td><td>' + (o["name"] or "-") + '</td><td><b>' + format(o["total"], ",.0f") + ' Ks</b></td><td><span class="badge ' + cls + '">' + o["status"] + '</span></td><td><a href="' + url_for("admin_order_detail", oid=o["id"]) + '" class="btn-sm" style="background:#007aff">View</a></td></tr>'
    body = '<div class="admin-table"><table><thead><tr><th>ID</th><th>User</th><th>Total</th><th>Status</th><th></th></tr></thead><tbody>' + (rows or '<tr><td colspan="5" style="text-align:center;padding:40px;color:#c7c7cc">No orders</td></tr>') + '</tbody></table></div>'
    return admin_page("Orders", body)

@app.route("/admin/order/<int:oid>", methods=["GET", "POST"])
@admin_required
def admin_order_detail(oid):
    conn = get_db()
    o = conn.execute("SELECT o.*, u.name FROM orders o LEFT JOIN users u ON u.id=o.user_id WHERE o.id=?", (oid,)).fetchone()
    if not o:
        conn.close()
        return redirect(url_for("admin_orders"))
    if request.method == "POST":
        conn.execute("UPDATE orders SET status=? WHERE id=?", (request.form["status"], oid))
        conn.commit()
        conn.close()
        flash("Updated", "success")
        return redirect(url_for("admin_order_detail", oid=oid))
    items = conn.execute("SELECT * FROM order_items WHERE order_id=?", (oid,)).fetchall()
    conn.close()
    items_html = ""
    for i in items:
        items_html += '<tr><td>' + i["product_name"] + '</td><td>' + format(i["price"], ",.0f") + '</td><td>' + str(i["quantity"]) + '</td><td>' + format(i["subtotal"], ",.0f") + '</td></tr>'
    options = ""
    for s in ["PENDING", "CONFIRMED", "DELIVERED", "CANCELLED"]:
        sel = " selected" if o["status"] == s else ""
        options += '<option value="' + s + '"' + sel + '>' + s + '</option>'
    body = '<div class="admin-table" style="padding:24px;margin-bottom:20px"><h3 style="margin-bottom:16px">Order #' + str(o["id"]) + ' - ' + (o["name"] or "-") + '</h3><form method="post"><select name="status" style="padding:12px;background:#f2f2f7;border:none;border-radius:10px;margin-right:10px">' + options + '</select><button type="submit" class="btn-sm" style="padding:12px 20px;background:linear-gradient(135deg,#ff453a,#d70015)">Update</button></form></div><div class="admin-table"><table><thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Subtotal</th></tr></thead><tbody>' + items_html + '</tbody></table></div>'
    return admin_page("Order", body)



@app.route("/static/manifest.json")
def manifest():
    from flask import send_from_directory
    return send_from_directory("static", "manifest.json", mimetype="application/json")

@app.route("/static/icon-192.png")
def icon192():
    from flask import send_from_directory
    return send_from_directory("static", "icon-192.png")

@app.route("/static/icon-512.png")
def icon512():
    from flask import send_from_directory
    return send_from_directory("static", "icon-512.png")



@app.route("/static/icon-192-v2.png")
def icon192v2():
    from flask import send_from_directory
    return send_from_directory("static", "icon-192-v2.png")

@app.route("/static/icon-512-v2.png")
def icon512v2():
    from flask import send_from_directory
    return send_from_directory("static", "icon-512-v2.png")

if __name__ == "__main__":
    init_db()
    print("")
    print("=" * 55)
    print("  iCare WALLET + E-COMMERCE")
    print("=" * 55)
    print("  User  : http://127.0.0.1:5000")
    print("  Admin : http://127.0.0.1:5000/admin/login")
    print("  Admin : admin / admin123")
    print("=" * 55)
    print("")
    app.run(debug=True, port=5000)
