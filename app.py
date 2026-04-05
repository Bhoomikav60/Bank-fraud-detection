"""
FraudShield v3.0 — Main Entry Point
Run: streamlit run app.py
"""
import streamlit as st
import random
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.db import db_init
from frontend.components.ui import inject_css, CARD, BORDER, MUTED, RED, TEXT, GREEN, BLUE

db_init()

st.set_page_config(page_title="FraudShield v3",page_icon="S",layout="wide",
                   initial_sidebar_state="expanded",menu_items={})
inject_css()

USERS = {
    "analyst":    {"pw":"fraud123",  "role":"analyst",  "name":"Ananya Sharma"},
    "manager":    {"pw":"report123", "role":"manager",  "name":"Rohit Mehta"},
    "customer1":  {"pw":"cust123",   "role":"customer", "name":"Rahul Verma",   "account":"ACC-1193","frozen":True},
    "customer2":  {"pw":"cust123",   "role":"customer", "name":"Priya Nair",    "account":"ACC-0552","frozen":False},
    "customer3":  {"pw":"cust123",   "role":"customer", "name":"Karan Mehta",   "account":"ACC-3381","frozen":True},
    "customer4":  {"pw":"cust123",   "role":"customer", "name":"Sneha Reddy",   "account":"ACC-7712","frozen":True},
    "customer5":  {"pw":"cust123",   "role":"customer", "name":"Arjun Pillai",  "account":"ACC-4490","frozen":True},
    "customer6":  {"pw":"cust123",   "role":"customer", "name":"Meera Iyer",    "account":"ACC-2267","frozen":False},
    "customer7":  {"pw":"cust123",   "role":"customer", "name":"Vikram Nair",   "account":"ACC-6634","frozen":False},
    "customer8":  {"pw":"cust123",   "role":"customer", "name":"Divya Sharma",  "account":"ACC-9901","frozen":True},
    "customer9":  {"pw":"cust123",   "role":"customer", "name":"Rohit Das",     "account":"ACC-5523","frozen":False},
    "customer10": {"pw":"cust123",   "role":"customer", "name":"Anita Bose",    "account":"ACC-8845","frozen":True},
}

NAMES = ["Rahul Verma","Priya Nair","Karan Mehta","Sneha Reddy","Arjun Pillai",
         "Meera Iyer","Vikram Nair","Divya Sharma","Rohit Das","Anita Bose",
         "Suresh Kumar","Pooja Singh","Arun Joshi","Kavya Patel","Nisha Gupta"]

def make_txns():
    random.seed(42); rows,now=[],datetime.now()
    types=["Credit Card","Debit Card","Insurance","Loan"]
    for i in range(40):
        s=round(random.uniform(72,98),1) if random.random()<0.2 else round(random.uniform(2,18),1)
        rows.append({"id":f"TXN-{8900-i}","type":random.choice(types),
                     "amount":round(random.uniform(50,45000),2),"score":s,
                     "status":"Fraud" if s>=70 else "Legit",
                     "customer":random.choice(NAMES),
                     "time":(now-timedelta(minutes=i*18)).strftime("%H:%M")})
    return rows

def init():
    defaults=dict(logged_in=False,username="",role="",user={},page="",
                  txns=make_txns(),batch=[],simlog=[],
                  vera_msgs=[],vera_step=0,vera_score=None,
                  twilio_sid="",twilio_token="",twilio_from="",alert_phone="",
                  gmail_user="",gmail_pass="",sms_on=False,email_on=False,
                  alert_log=[],frozen=[])
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

def login_page():
    _,col,_=st.columns([1,1,1])
    with col:
        st.markdown(f"""<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;
                    padding:40px;margin-top:60px;position:relative;overflow:hidden">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,#DC2626,#EF4444 50%,transparent)"></div>
          <div style="font-size:40px;font-weight:800;letter-spacing:3px;color:#F1F5F9">
            FRAUD<span style="color:{RED}">SHIELD</span></div>
          <div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:2px;color:{MUTED};
                      margin-top:4px;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid {BORDER}">
            Multi-Domain Fraud Detection — v3.0</div></div>""",unsafe_allow_html=True)
        st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-top:none;border-radius:0 0 12px 12px;padding:24px 40px 32px">',unsafe_allow_html=True)
        username=st.text_input("USERNAME",placeholder="Enter username",key="l_u")
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        password=st.text_input("PASSWORD",placeholder="Enter password",type="password",key="l_p")
        st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
        if st.button("SIGN IN",use_container_width=True):
            u=username.strip()
            if u in USERS and USERS[u]["pw"]==password.strip():
                st.session_state.logged_in=True; st.session_state.username=u
                st.session_state.role=USERS[u]["role"]; st.session_state.user=dict(USERS[u])
                st.session_state.page=""; st.session_state.vera_msgs=[]
                st.session_state.vera_step=0; st.session_state.vera_score=None; st.rerun()
            else: st.error("Invalid credentials.")
        st.markdown(f"""<div style="margin-top:16px;padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid {BORDER};border-radius:6px">
          <p style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};letter-spacing:1.5px;text-transform:uppercase;margin:0 0 8px">Demo Logins</p>
          <p style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};margin:0;line-height:2.2">
            <strong style="color:{TEXT}">analyst</strong> / fraud123 → Analyst Portal<br>
            <strong style="color:{TEXT}">manager</strong> / report123 → Manager Portal<br>
            <strong style="color:{TEXT}">customer1</strong> / cust123 → Frozen account<br>
            <strong style="color:{TEXT}">customer2</strong> / cust123 → Active account<br>
            <strong style="color:{TEXT}">customer3–10</strong> / cust123 → Various states
          </p></div></div>""",unsafe_allow_html=True)

def sidebar(role):
    from database.db import db_get_alerts, db_get_all_frozen
    with st.sidebar:
        st.markdown(f"""<div style="padding:16px 6px 14px;border-bottom:1px solid {BORDER};margin-bottom:10px">
          <div style="font-size:22px;font-weight:800;letter-spacing:3px;color:#F1F5F9">
            FRAUD<span style="color:{RED}">SHIELD</span></div>
          <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};margin-top:2px">v3.0</div>
        </div>""",unsafe_allow_html=True)
        u=st.session_state.user
        role_color={"analyst":RED,"manager":GREEN,"customer":BLUE}.get(role,MUTED)
        role_label={"analyst":"Analyst","manager":"Manager","customer":"Customer"}.get(role,"")
        st.markdown(f"""<div style="margin-bottom:14px;padding:10px 12px;background:rgba(255,255,255,0.02);border:1px solid {role_color}44;border-radius:6px">
          <div style="font-family:DM Mono,monospace;font-size:8px;color:{role_color};letter-spacing:1.5px">{role_label}</div>
          <div style="font-size:14px;font-weight:600;color:#F1F5F9;margin-top:2px">{u.get('name','')}</div>
        </div>""",unsafe_allow_html=True)
        if role=="analyst":
            pages=[("Dashboard","dashboard"),("Live Alerts","alerts"),("Frozen Accounts","frozen"),
                   ("Transactions","transactions"),("Batch Upload","batch"),("Simulator","simulator"),("Alert Settings","settings")]
        elif role=="manager":
            pages=[("Summary","summary"),("PDF Report","pdf")]
        else:
            pages=[("My Account","account"),("Transactions","mytxns"),("VERA Chat","vera")]
        if not st.session_state.page: st.session_state.page=pages[0][1]
        for label,key in pages:
            active=st.session_state.page==key; badge_=""
            if key=="alerts":
                n=len([a for a in db_get_alerts() if a["status"]=="pending"]); badge_=f"  ({n})" if n else ""
            if key=="frozen":
                n=len(db_get_all_frozen()); badge_=f"  ({n})" if n else ""
            if key=="vera" and role=="customer" and u.get("frozen"): badge_="  (!)"
            if active:
                st.markdown(f'<div style="padding:8px 12px;background:rgba(239,68,68,0.08);border:1px solid {RED}33;border-radius:6px;font-family:DM Mono,monospace;font-size:11px;color:{RED};letter-spacing:1px;margin-bottom:2px">{label}{badge_}</div>',unsafe_allow_html=True)
                st.markdown("<div style='height:2px'></div>",unsafe_allow_html=True)
            else:
                if st.button(label+badge_,key=f"nav_{key}",use_container_width=True):
                    st.session_state.page=key; st.rerun()
        st.markdown("<div style='height:40px'></div>",unsafe_allow_html=True)
        st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:9px;color:#334155;padding:6px 0;border-top:1px solid {BORDER}">{datetime.now().strftime("%d %b %Y  %H:%M")}</p>',unsafe_allow_html=True)
        if st.button("SIGN OUT",key="signout",use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

def main():
    init()
    if not st.session_state.logged_in: login_page(); return
    role=st.session_state.role; sidebar(role); page=st.session_state.page
    if role=="analyst":
        from frontend.pages.analyst import pg_dashboard,pg_alerts,pg_frozen,pg_transactions,pg_batch,pg_simulator,pg_settings
        {"dashboard":pg_dashboard,"alerts":pg_alerts,"frozen":pg_frozen,"transactions":pg_transactions,
         "batch":pg_batch,"simulator":pg_simulator,"settings":pg_settings}.get(page,pg_dashboard)()
    elif role=="manager":
        from frontend.pages.manager import pg_summary,pg_pdf
        {"summary":pg_summary,"pdf":pg_pdf}.get(page,pg_summary)()
    elif role=="customer":
        from frontend.pages.customer import pg_account,pg_mytxns,pg_vera
        {"account":pg_account,"mytxns":pg_mytxns,"vera":pg_vera}.get(page,pg_account)()

if __name__=="__main__": main()
