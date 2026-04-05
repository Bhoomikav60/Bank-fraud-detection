import sqlite3
from datetime import datetime

DB_PATH = "fraudshield.db"

def db_init():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS account_status (
        account TEXT PRIMARY KEY, customer TEXT, frozen INTEGER DEFAULT 0,
        reason TEXT DEFAULT '', vera_status TEXT DEFAULT 'Pending',
        vera_score INTEGER DEFAULT NULL, updated_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY, type TEXT, amount REAL, score REAL,
        account TEXT, customer TEXT, time TEXT,
        status TEXT DEFAULT 'pending', created_at TEXT)""")
    cur.execute("SELECT COUNT(*) FROM account_status")
    if cur.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.executemany("INSERT OR IGNORE INTO account_status VALUES (?,?,?,?,?,?,?)", [
            ("ACC-1193","Rahul Verma",  1,"Credit Card — Score 98.4%","Pending",    None,now),
            ("ACC-0552","Priya Nair",   0,"Debit Card — Score 96.1%", "Passed",     87,  now),
            ("ACC-3381","Karan Mehta",  1,"Loan — Score 92.7%",       "Pending",    None,now),
            ("ACC-7712","Sneha Reddy",  1,"Insurance — Score 88.3%",  "In Progress",61,  now),
            ("ACC-4490","Arjun Pillai", 1,"Credit Card — Score 95.1%","Pending",    None,now),
            ("ACC-2267","Meera Iyer",   0,"Debit Card — Score 71.4%", "Passed",     82,  now),
            ("ACC-6634","Vikram Nair",  0,"Insurance — Score 74.9%",  "Passed",     79,  now),
            ("ACC-9901","Divya Sharma", 1,"Credit Card — Score 97.8%","Failed",     32,  now),
            ("ACC-5523","Rohit Das",    0,"Loan — Score 69.2%",       "Passed",     88,  now),
            ("ACC-8845","Anita Bose",   1,"Debit Card — Score 91.5%", "Pending",    None,now),
        ])
    cur.execute("SELECT COUNT(*) FROM alerts")
    if cur.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.executemany("INSERT OR IGNORE INTO alerts VALUES (?,?,?,?,?,?,?,?,?)", [
            ("TXN-8842","Credit Card",2340.0, 98.4,"ACC-1193","Rahul Verma", "14:32","pending", now),
            ("TXN-8819","Insurance",  18500.0,91.2,"ACC-0881","Suresh Kumar","13:58","pending", now),
            ("TXN-8801","Loan",       45000.0,76.8,"ACC-0440","Priya Nair",  "13:21","pending", now),
            ("TXN-8755","Debit Card", 8200.0, 88.6,"ACC-3381","Karan Mehta", "11:44","blocked", now),
            ("TXN-8731","Credit Card",650.0,  72.1,"ACC-4490","Arjun Pillai","10:19","released",now),
        ])
    con.commit(); con.close()

def db_get_account(account):
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    cur = con.cursor(); cur.execute("SELECT * FROM account_status WHERE account=?",(account,))
    row = cur.fetchone(); con.close(); return dict(row) if row else None

def db_set_frozen(account, frozen: bool):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE account_status SET frozen=?,updated_at=? WHERE account=?",
                (1 if frozen else 0,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),account))
    con.commit(); con.close()

def db_update_vera(account, vera_status, vera_score):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE account_status SET vera_status=?,vera_score=?,updated_at=? WHERE account=?",
                (vera_status,vera_score,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),account))
    con.commit(); con.close()

def db_get_all_frozen():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    cur = con.cursor(); cur.execute("SELECT * FROM account_status WHERE frozen=1 ORDER BY updated_at DESC")
    rows = [dict(r) for r in cur.fetchall()]; con.close(); return rows

def db_add_account(account, customer, reason):
    con = sqlite3.connect(DB_PATH); now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con.execute("INSERT OR REPLACE INTO account_status (account,customer,frozen,reason,vera_status,vera_score,updated_at) VALUES (?,?,1,?,'Pending',NULL,?)",
                (account,customer,reason,now)); con.commit(); con.close()

def db_get_alerts():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    cur = con.cursor(); cur.execute("SELECT * FROM alerts ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]; con.close(); return rows

def db_update_alert(alert_id, status):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE alerts SET status=? WHERE id=?",(status,alert_id))
    con.commit(); con.close()

def db_add_alert(alert_id, atype, amount, score, account, customer, t):
    con = sqlite3.connect(DB_PATH); now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con.execute("INSERT OR IGNORE INTO alerts VALUES (?,?,?,?,?,?,?,?,?)",
                (alert_id,atype,amount,score,account,customer,t,"pending",now))
    con.commit(); con.close()
