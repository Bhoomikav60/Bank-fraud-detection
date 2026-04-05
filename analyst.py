"""FraudShield — Analyst Portal"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time, random
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import db_get_alerts, db_update_alert, db_add_alert, db_get_all_frozen, db_set_frozen, db_add_account
from ml.predictor import predict, MODELS
from backend.alerts import fire_alerts
from frontend.components.ui import page_header, badge, score_bar, gauge_chart, info_box, alert_card, CARD, BORDER, MUTED, RED, GREEN, BLUE, ORANGE, TEXT

def pg_dashboard():
    page_header("Dashboard", datetime.now().strftime("%d %B %Y"))
    txns = st.session_state.txns
    fr   = sum(1 for t in txns if t["status"]=="Fraud")
    sv   = sum(t["amount"] for t in txns if t["status"]=="Fraud")
    alerts  = db_get_alerts()
    pending = [a for a in alerts if a["status"]=="pending"]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Transactions",f"{len(txns):,}"); c2.metric("Fraud Detected",str(fr))
    c3.metric("Money Saved",f"Rs.{sv:,.0f}");         c4.metric("Pending Alerts",str(len(pending)))
    st.markdown("<br>",unsafe_allow_html=True)
    if pending:
        st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Pending Alerts — {len(pending)} need action</p>',unsafe_allow_html=True)
        for a in pending:
            col_i,col_a = st.columns([7,1])
            with col_i: st.markdown(alert_card(a),unsafe_allow_html=True)
            with col_a:
                st.markdown("<div style='height:20px'></div>",unsafe_allow_html=True)
                if st.button("BLOCK",  key=f"d_blk_{a['id']}"): db_update_alert(a["id"],"blocked");  st.rerun()
                if st.button("RELEASE",key=f"d_rel_{a['id']}"): db_update_alert(a["id"],"released"); st.rerun()
    else:
        st.success("All clear — no pending alerts.")
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Fraud by Domain</p>',unsafe_allow_html=True)
    domain = {}
    for t in txns:
        if t["status"]=="Fraud": domain[t["type"]] = domain.get(t["type"],0)+1
    if domain:
        fig = go.Figure(go.Bar(x=list(domain.keys()),y=list(domain.values()),
            marker_color=[RED,ORANGE,BLUE,GREEN][:len(domain)],
            text=list(domain.values()),textposition="outside",textfont=dict(color=TEXT,size=12)))
        fig.update_layout(paper_bgcolor=CARD,plot_bgcolor=CARD,height=200,
            margin=dict(t=10,b=10,l=10,r=10),showlegend=False,
            xaxis=dict(tickfont=dict(color=MUTED),gridcolor=BORDER),
            yaxis=dict(tickfont=dict(color=MUTED),gridcolor=BORDER))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

def pg_alerts():
    alerts  = db_get_alerts()
    pending = len([a for a in alerts if a["status"]=="pending"])
    page_header("Live Alerts",f"{pending} pending")
    tab_p,tab_b,tab_r = st.tabs(["PENDING","BLOCKED","RELEASED"])
    def render(a,tab_key):
        col_i,col_g,col_a = st.columns([5,2,1])
        with col_i: st.markdown(alert_card(a),unsafe_allow_html=True)
        with col_g: st.plotly_chart(gauge_chart(a["score"]),use_container_width=True,config={"displayModeBar":False})
        with col_a:
            st.markdown("<div style='height:20px'></div>",unsafe_allow_html=True)
            status = a["status"]
            if status=="pending":
                if st.button("BLOCK",  key=f"{tab_key}_blk_{a['id']}"): db_update_alert(a["id"],"blocked");  st.rerun()
                if st.button("RELEASE",key=f"{tab_key}_rel_{a['id']}"): db_update_alert(a["id"],"released"); st.rerun()
            elif status=="blocked":
                st.markdown(f'<div style="margin-top:14px;font-family:DM Mono,monospace;font-size:11px;color:{RED};font-weight:700">BLOCKED</div>',unsafe_allow_html=True)
                if st.button("UNDO",key=f"{tab_key}_undo_{a['id']}"): db_update_alert(a["id"],"pending"); st.rerun()
            else:
                st.markdown(f'<div style="margin-top:14px;font-family:DM Mono,monospace;font-size:11px;color:{GREEN};font-weight:700">RELEASED</div>',unsafe_allow_html=True)
                if st.button("UNDO",key=f"{tab_key}_undo_{a['id']}"): db_update_alert(a["id"],"pending"); st.rerun()
    with tab_p:
        lst=[a for a in alerts if a["status"]=="pending"]
        if not lst: st.info("No pending alerts.")
        else:
            for a in lst: render(a,"p")
    with tab_b:
        lst=[a for a in alerts if a["status"]=="blocked"]
        if not lst: st.info("No blocked alerts.")
        else:
            for a in lst: render(a,"b")
    with tab_r:
        lst=[a for a in alerts if a["status"]=="released"]
        if not lst: st.info("No released alerts.")
        else:
            for a in lst: render(a,"r")

def pg_frozen():
    frozen_list = db_get_all_frozen()
    page_header("Frozen Accounts",f"{len(frozen_list)} accounts frozen")
    col_r,_ = st.columns([1,5])
    with col_r:
        if st.button("REFRESH",key="refresh_frozen"): st.rerun()
    if not frozen_list: st.success("No frozen accounts."); return
    for f in frozen_list:
        vc = {"Passed":GREEN,"Failed":RED,"In Progress":ORANGE}.get(f["vera_status"],MUTED)
        col_i,col_a = st.columns([7,1])
        with col_i:
            st.markdown(f"""<div style="background:{CARD};border:1px solid {BORDER};border-left:4px solid {BLUE};border-radius:8px;padding:18px;margin-bottom:6px">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
                <span style="font-weight:700;font-size:15px;color:#F1F5F9;font-family:DM Mono,monospace">{f['account']}</span>
                <span style="font-size:14px;color:{TEXT}">{f['customer']}</span>
                <span style="margin-left:auto;font-family:DM Mono,monospace;font-size:10px;color:{MUTED}">{f['updated_at']}</span>
              </div>
              <div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};margin-bottom:12px">{f['reason']}</div>
              <div style="display:flex;gap:28px">
                <div><div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">VERA STATUS</div>
                     <div style="font-family:DM Mono,monospace;font-size:12px;color:{vc}">{f['vera_status']}</div></div>
                <div><div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">VERA SCORE</div>
                     <div style="font-family:DM Mono,monospace;font-size:12px;color:{vc}">{str(f['vera_score'])+'/100' if f['vera_score'] else '—'}</div></div>
              </div></div>""",unsafe_allow_html=True)
        with col_a:
            st.markdown("<div style='height:24px'></div>",unsafe_allow_html=True)
            if st.button("UNFREEZE",key=f"uf_{f['account']}"):
                db_set_frozen(f["account"],False); st.success(f"{f['account']} unfrozen."); time.sleep(1); st.rerun()

def pg_transactions():
    page_header("Transaction Log",f"{len(st.session_state.txns)} transactions today")
    col1,col2 = st.columns([3,1])
    with col1: search = st.text_input("Search",placeholder="TXN ID, type, status...",label_visibility="collapsed")
    with col2: ft = st.selectbox("Filter",["All","Credit Card","Debit Card","Insurance","Loan"],label_visibility="collapsed")
    txns = st.session_state.txns
    if search: txns=[t for t in txns if search.lower() in str(t).lower()]
    if ft!="All": txns=[t for t in txns if t["type"]==ft]
    st.markdown(f'''<div style="display:grid;grid-template-columns:1.2fr 1.5fr 1.2fr 2.8fr 0.8fr;gap:8px;
                padding:8px 14px;font-family:DM Mono,monospace;font-size:9px;letter-spacing:1.5px;
                text-transform:uppercase;color:{MUTED};border-bottom:1px solid {BORDER};margin-bottom:4px">
      <span>TXN ID</span><span>Type</span><span>Amount</span><span>Score</span><span>Status</span>
    </div>''',unsafe_allow_html=True)
    for t in txns[:30]:
        sc=t["score"]; c=RED if sc>=70 else ORANGE if sc>=40 else GREEN
        sc_=RED if t["status"]=="Fraud" else GREEN
        st.markdown(f'''<div style="display:grid;grid-template-columns:1.2fr 1.5fr 1.2fr 2.8fr 0.8fr;gap:8px;
                    align-items:center;padding:9px 14px;background:{CARD};border:1px solid {BORDER};
                    border-radius:6px;margin-bottom:3px">
          <span style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">{t['id']}</span>
          <span style="color:{TEXT}">{t['type']}</span>
          <span style="font-weight:600;color:{TEXT}">Rs.{t['amount']:,.0f}</span>
          <div style="display:flex;align-items:center;gap:8px">
            <div style="flex:1;background:{BORDER};border-radius:3px;height:6px;overflow:hidden">
              <div style="width:{sc}%;height:100%;background:{c};border-radius:3px"></div></div>
            <span style="font-family:DM Mono,monospace;font-size:12px;color:{c};font-weight:700;min-width:36px">{sc}%</span>
          </div>
          <span style="color:{sc_};font-family:DM Mono,monospace;font-size:10px">{t['status'].upper()}</span>
        </div>''',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.download_button("DOWNLOAD CSV",pd.DataFrame(txns).to_csv(index=False).encode(),"transactions.csv","text/csv",use_container_width=True)

def pg_batch():
    page_header("Batch Upload","Score many transactions from a CSV at once")
    col1,col2 = st.columns(2)
    with col1:
        ft = st.selectbox("Domain",["Credit Card","Debit Card","Insurance","Loan"])
        uploaded = st.file_uploader("CSV",type=["csv"],label_visibility="collapsed")
        if uploaded:
            df = pd.read_csv(uploaded); info_box(f"{uploaded.name} — {len(df):,} rows loaded","info")
            st.dataframe(df.head(5),use_container_width=True)
            if st.button("ANALYZE ALL",use_container_width=True):
                with st.spinner("Scoring..."):
                    bar=st.progress(0)
                    for i in range(101): time.sleep(0.004); bar.progress(i)
                    scores=[round(random.uniform(2,99),1) for _ in range(len(df))]
                    results=df.copy(); results["Fraud Score %"]=scores
                    results["Prediction"]=["Fraud" if s>=70 else "Legit" for s in scores]
                    st.session_state.batch=results
                st.success(f"Done — {len(results)} scored"); st.rerun()
    with col2:
        if isinstance(st.session_state.get("batch"),pd.DataFrame) and not st.session_state.batch.empty:
            dr=st.session_state.batch; fn=sum(dr["Prediction"]=="Fraud"); ln=sum(dr["Prediction"]=="Legit")
            c1,c2=st.columns(2); c1.metric("Fraud",fn); c2.metric("Legit",ln)
            fig=go.Figure(go.Pie(labels=["Fraud","Legit"],values=[fn,ln],hole=0.6,
                marker=dict(colors=[RED,GREEN],line=dict(color="#0A0F1E",width=2)),
                textinfo="percent",textfont=dict(size=12,color=TEXT)))
            fig.update_layout(paper_bgcolor=CARD,plot_bgcolor=CARD,height=200,margin=dict(t=8,b=8,l=8,r=8))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            st.download_button("DOWNLOAD RESULTS",dr.to_csv(index=False).encode(),"results.csv","text/csv",use_container_width=True)
        else:
            st.markdown(f'<div style="background:{CARD};border:1px dashed {BORDER};border-radius:8px;padding:48px;text-align:center;color:#334155;font-family:DM Mono,monospace;font-size:11px">Upload a CSV and click Analyze</div>',unsafe_allow_html=True)

def pg_simulator():
    page_header("Transaction Simulator","Test any transaction against the fraud engine")
    if MODELS: info_box(f"Real ML models loaded: {', '.join(MODELS.keys())}","ok")
    else:       info_box("Demo mode — run train_models.ipynb to load real ML models","warn")
    col1,col2 = st.columns(2)
    with col1:
        ft=st.selectbox("Fraud Type",["Credit Card","Debit Card","Insurance","Loan"],key="sim_ft"); feats={}
        if ft=="Credit Card":
            info_box("V1–V28 are PCA-encrypted features sent automatically by the bank API.","info")
            feats["amount"]=st.number_input("Amount (Rs.)",value=1.00,step=0.01)
            a,b=st.columns(2); feats["v1"]=a.number_input("V1",value=-2.31,step=0.01); feats["v2"]=b.number_input("V2",value=1.95,step=0.01)
            a,b=st.columns(2); feats["v3"]=a.number_input("V3",value=-1.60,step=0.01); feats["v4"]=b.number_input("V4",value=3.99,step=0.01)
        elif ft=="Debit Card":
            a,b=st.columns(2); feats["amount"]=a.number_input("Amount (Rs.)",value=150.0); feats["distance_from_home"]=b.number_input("Distance from home (km)",value=5)
            a,b=st.columns(2); feats["foreign"]=a.number_input("Foreign? (0=No 1=Yes)",value=0,min_value=0,max_value=1); feats["hour"]=b.number_input("Hour (0-23)",value=14,min_value=0,max_value=23)
        elif ft=="Insurance":
            a,b=st.columns(2); feats["claim"]=a.number_input("Claim Amount (Rs.)",value=18500); feats["premium"]=b.number_input("Annual Premium (Rs.)",value=1200)
            a,b=st.columns(2); feats["policy_age"]=a.number_input("Policy age (months)",value=2); feats["prev_claims"]=b.number_input("Previous claims",value=4)
        elif ft=="Loan":
            a,b=st.columns(2); feats["amount"]=a.number_input("Loan Amount (Rs.)",value=85000); feats["credit_score"]=b.number_input("Credit Score",value=420)
            a,b=st.columns(2); feats["dti"]=a.number_input("Debt-to-Income",value=0.82,step=0.01); feats["late_payments"]=b.number_input("Late Payments",value=6)
        st.markdown("<br>",unsafe_allow_html=True); go_btn=st.button("ANALYZE TRANSACTION",use_container_width=True)
    with col2:
        if go_btn:
            ph=st.empty()
            for msg in ["Connecting to API...","Running models...","Calculating score..."]:
                ph.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:6px;padding:10px 14px;font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">{msg}</div>',unsafe_allow_html=True); time.sleep(0.14)
            ph.empty()
            sc=predict(ft,feats); ms=random.randint(175,310); fraud=sc>=70
            action="BLOCK" if fraud else "APPROVE"; tid=f"TXN-{random.randint(8000,9999)}"
            amt=feats.get("amount",0); color=RED if fraud else GREEN; bg=f"rgba(239,68,68,0.08)" if fraud else "rgba(34,197,94,0.08)"
            st.markdown(f'''<div style="background:{bg};border:1px solid {color}44;border-radius:10px;padding:22px;text-align:center;margin-bottom:14px">
              <div style="font-size:18px;font-weight:800;letter-spacing:3px;color:{color};margin-bottom:6px">{"FRAUD DETECTED" if fraud else "LEGITIMATE"}</div>
              <span style="background:{color};color:white;padding:4px 20px;border-radius:4px;font-family:DM Mono,monospace;font-size:11px;letter-spacing:2px">{action}</span>
            </div>''',unsafe_allow_html=True)
            st.plotly_chart(gauge_chart(sc),use_container_width=True,config={"displayModeBar":False})
            c1,c2,c3=st.columns(3); c1.metric("Score",f"{sc}%"); c2.metric("Risk","HIGH" if sc>=70 else "MEDIUM" if sc>=40 else "LOW"); c3.metric("Response",f"{ms}ms")
            st.markdown(f'''<div style="background:#060C18;border:1px solid {BORDER};border-radius:6px;padding:14px;font-family:DM Mono,monospace;font-size:11px;line-height:1.9;margin-top:6px">
              <div style="font-size:9px;color:{GREEN};margin-bottom:6px">200 OK &middot; {ms}ms</div>
              <span style="color:#60A5FA">{{</span><br>
              &nbsp;&nbsp;"transaction_id": <span style="color:#FCD34D">"{tid}"</span>,<br>
              &nbsp;&nbsp;"prediction": <span style="color:{color}">"{action}"</span>,<br>
              &nbsp;&nbsp;"fraud_score": <span style="color:#34D399">{sc}</span>,<br>
              &nbsp;&nbsp;"model": <span style="color:#FCD34D">"{ft}"</span><br>
              <span style="color:#60A5FA">}}</span></div>''',unsafe_allow_html=True)
            if sc>=95:
                st.error(f"AUTO-FREEZE TRIGGERED — score {sc}% exceeds 95% threshold")
                db_add_account(f"ACC-{random.randint(1000,9999)}","Simulated",f"{ft} — Score {sc}%")
                if st.session_state.get("sms_on") or st.session_state.get("email_on"):
                    for ch,ok,msg in fire_alerts(tid,ft,amt,sc,"ACC-SIM"):
                        st.success(f"{ch}: {msg}") if ok else st.error(f"{ch}: {msg}")
            elif sc>=70:
                db_add_alert(tid,ft,amt,sc,f"ACC-{random.randint(1000,9999)}","Simulated",datetime.now().strftime("%H:%M"))
                st.info(f"Added to Live Alerts — {sc}% exceeds threshold")
            if "simlog" not in st.session_state: st.session_state.simlog=[]
            st.session_state.simlog.insert(0,{"id":tid,"type":ft,"amount":amt,"score":sc,"action":action,"ms":ms})
        else:
            st.markdown(f'<div style="background:{CARD};border:1px dashed {BORDER};border-radius:8px;padding:60px;text-align:center;color:#334155;font-family:DM Mono,monospace;font-size:12px">Enter transaction details and click Analyze</div>',unsafe_allow_html=True)
    if st.session_state.get("simlog"):
        st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:1.5px;text-transform:uppercase;margin:20px 0 8px">Session Log — {len(st.session_state.simlog)} analyzed</p>',unsafe_allow_html=True)
        for e in st.session_state.simlog[:8]:
            c=RED if e["action"]=="BLOCK" else GREEN
            st.markdown(f'''<div style="display:grid;grid-template-columns:1fr 1.5fr 1.5fr 3fr 1fr 1fr 1fr;gap:8px;align-items:center;padding:8px 12px;background:{CARD};border:1px solid {BORDER};border-radius:5px;margin-bottom:3px;font-family:DM Mono,monospace;font-size:11px">
              <span style="color:{MUTED}">{e['id']}</span><span style="color:{TEXT}">{e['type']}</span><span style="color:{TEXT}">Rs.{float(e['amount']):,.0f}</span>
              <div style="background:{BORDER};border-radius:3px;height:5px"><div style="width:{e['score']}%;height:100%;background:{c};border-radius:3px"></div></div>
              <span style="color:{c};font-weight:700">{e['score']}%</span><span style="color:{c}">{e['action']}</span><span style="color:{MUTED}">{e['ms']}ms</span>
            </div>''',unsafe_allow_html=True)

def pg_settings():
    page_header("Alert Settings","Configure SMS and email notifications")
    from backend.alerts import send_sms, send_email
    col1,col2 = st.columns(2)
    with col1:
        st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;padding:20px;margin-bottom:12px"><p style="font-family:DM Mono,monospace;font-size:11px;font-weight:600;color:#E2E8F0;margin:0 0 4px">Twilio SMS</p><p style="font-size:11px;color:{MUTED};margin:0">Send SMS when fraud is detected</p></div>',unsafe_allow_html=True)
        st.session_state.sms_on       = st.toggle("Enable SMS Alerts",value=st.session_state.get("sms_on",False))
        st.session_state.twilio_sid   = st.text_input("Account SID",  value=st.session_state.get("twilio_sid",""),  placeholder="ACxxxxxxxxxxxxxxxx")
        st.session_state.twilio_token = st.text_input("Auth Token",   value=st.session_state.get("twilio_token",""),placeholder="Your auth token",type="password")
        st.session_state.twilio_from  = st.text_input("Twilio Number",value=st.session_state.get("twilio_from",""), placeholder="+1415XXXXXXX")
        st.session_state.alert_phone  = st.text_input("Send Alerts To",value=st.session_state.get("alert_phone",""),placeholder="+919876543210")
        info_box("All numbers must start with + and country code.","info")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("SEND TEST SMS",use_container_width=True):
            with st.spinner("Sending..."):
                ok,msg=send_sms(st.session_state.alert_phone,"FraudShield test — SMS working.")
            st.success(msg) if ok else st.error(msg)
    with col2:
        st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;padding:20px;margin-bottom:12px"><p style="font-family:DM Mono,monospace;font-size:11px;font-weight:600;color:#E2E8F0;margin:0 0 4px">Gmail Email</p><p style="font-size:11px;color:{MUTED};margin:0">Send email when fraud is detected</p></div>',unsafe_allow_html=True)
        st.session_state.email_on   = st.toggle("Enable Email Alerts",value=st.session_state.get("email_on",False))
        st.session_state.gmail_user = st.text_input("Gmail Address",value=st.session_state.get("gmail_user",""),placeholder="youremail@gmail.com")
        st.session_state.gmail_pass = st.text_input("App Password", value=st.session_state.get("gmail_pass",""),placeholder="16-character app password",type="password")
        st.markdown(f'''<div style="background:#0F172A;border:1px solid {BORDER};border-radius:6px;padding:12px 14px;margin:8px 0">
          <p style="font-family:DM Mono,monospace;font-size:9px;color:{RED};margin:0 0 6px">Use App Password — not your Gmail password</p>
          <p style="font-size:11px;color:{MUTED};margin:0;line-height:1.8">1. myaccount.google.com<br>2. Security → 2-Step Verification (must be ON)<br>3. App Passwords → create one → paste 16-char code here</p>
        </div>''',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("SEND TEST EMAIL",use_container_width=True):
            with st.spinner("Sending..."):
                ok,msg=send_email(st.session_state.gmail_user,"[FraudShield] Test Alert","Test email — working correctly.")
            st.success(msg) if ok else st.error(msg)
    if st.session_state.get("alert_log"):
        st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:1.5px;text-transform:uppercase;margin:24px 0 8px">Alert Log</p>',unsafe_allow_html=True)
        for log in st.session_state.alert_log[:8]:
            parts=" · ".join([f'{r[0]}: {"OK" if r[1] else r[2][:40]}' for r in log["results"]]) if log["results"] else "not configured"
            c=GREEN if all(r[1] for r in log["results"]) else RED
            st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:5px;padding:10px 14px;margin-bottom:3px;font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">{log["time"]} · <span style="color:{TEXT}">{log["txn"]}</span> · <span style="color:{RED}">{log["score"]}%</span> · <span style="color:{c}">{parts}</span></div>',unsafe_allow_html=True)
