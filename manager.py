"""FraudShield — Manager Portal"""
import streamlit as st, time
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.pdf_report import make_pdf
from frontend.components.ui import page_header, CARD, BORDER, MUTED, RED, GREEN, BLUE, TEXT

def pg_summary():
    page_header("Daily Summary", datetime.now().strftime("%d %B %Y"))
    txns=st.session_state.txns; fr=sum(1 for t in txns if t["status"]=="Fraud")
    sv=sum(t["amount"] for t in txns if t["status"]=="Fraud"); fz=len(st.session_state.get("frozen",[]))
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Transactions",f"{len(txns):,}"); c2.metric("Fraud Detected",str(fr))
    c3.metric("Money Saved",f"Rs.{sv:,.0f}");   c4.metric("Frozen Accounts",str(fz))
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px">Model Performance</p>',unsafe_allow_html=True)
    for nm,auc,c in [("Credit Card",0.99,GREEN),("Debit Card",0.97,GREEN),("Insurance",0.95,BLUE),("Loan",0.93,BLUE)]:
        st.markdown(f"""<div style="margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;margin-bottom:5px">
            <span style="font-family:DM Mono,monospace;font-size:12px;color:#94A3B8">{nm}</span>
            <span style="font-family:DM Mono,monospace;font-size:13px;color:{c};font-weight:700">ROC-AUC {auc}</span>
          </div>
          <div style="background:{BORDER};border-radius:4px;height:8px;overflow:hidden">
            <div style="width:{int(auc*100)}%;height:100%;background:{c};border-radius:4px"></div>
          </div></div>""",unsafe_allow_html=True)

def pg_pdf():
    page_header("PDF Report","One-click daily fraud report")
    txns=st.session_state.txns; fr=sum(1 for t in txns if t["status"]=="Fraud")
    sv=sum(t["amount"] for t in txns if t["status"]=="Fraud"); fz=len(st.session_state.get("frozen",[]))
    st.markdown(f"""<div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:32px;text-align:center;margin-bottom:24px">
      <div style="font-size:22px;font-weight:700;color:#F1F5F9;margin-bottom:18px">Daily Fraud Report</div>
      <div style="display:flex;justify-content:center;gap:40px">
        <div><div style="font-size:28px;font-weight:800;color:{GREEN}">{len(txns):,}</div>
             <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">TRANSACTIONS</div></div>
        <div><div style="font-size:28px;font-weight:800;color:{RED}">{fr}</div>
             <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">FRAUD</div></div>
        <div><div style="font-size:24px;font-weight:800;color:{GREEN}">Rs.{sv:,.0f}</div>
             <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">SAVED</div></div>
        <div><div style="font-size:28px;font-weight:800;color:{BLUE}">{fz}</div>
             <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">FROZEN</div></div>
      </div></div>""",unsafe_allow_html=True)
    if st.button("GENERATE AND DOWNLOAD PDF REPORT",use_container_width=True):
        with st.spinner("Generating..."):
            time.sleep(0.8)
            from database.db import db_get_alerts, db_get_all_frozen
            pdf,err=make_pdf(txns,db_get_alerts(),db_get_all_frozen())
        if err: st.error(f"Failed: {err}")
        else:
            st.success("PDF ready")
            st.download_button("DOWNLOAD PDF",pdf,f"FraudShield_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf","application/pdf",use_container_width=True)
