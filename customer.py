"""FraudShield — Customer Portal"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import db_get_account, db_update_vera, db_add_account
from backend.vera import vera_reply, VERA_QUESTIONS
from frontend.components.ui import page_header, CARD, BORDER, MUTED, RED, GREEN, BLUE, ORANGE, TEXT

def pg_account():
    u=st.session_state.user; page_header(f"Welcome, {u.get('name','')}", "Your account overview")
    account_no=u.get("account",""); db_rec=db_get_account(account_no)
    if db_rec: frozen=bool(db_rec["frozen"])
    else:
        frozen=u.get("frozen",False)
        if frozen: db_add_account(account_no,u.get("name",""),"Account under review")
    if frozen:
        col_r,_=st.columns([1,5])
        with col_r:
            if st.button("CHECK STATUS",key="refresh_account"): st.rerun()
        st.markdown(f"""<div style="background:rgba(59,130,246,0.08);border:1px solid #3B82F644;
                    border-left:5px solid {BLUE};border-radius:8px;padding:22px;margin-bottom:18px">
          <div style="font-size:16px;font-weight:700;color:{BLUE};margin-bottom:8px">Account Temporarily Frozen</div>
          <div style="font-size:13px;color:#94A3B8;line-height:1.8">
            A suspicious transaction of <strong style="color:#F1F5F9">Rs.2,340</strong>
            was detected at 14:32 today.<br>Your account has been frozen to protect you.<br><br>
            Complete the VERA verification interview to request restoration.</div>
        </div>""",unsafe_allow_html=True)
        if st.button("START VERA VERIFICATION",use_container_width=True):
            st.session_state.page="vera"; st.rerun()
    else:
        st.markdown(f"""<div style="background:rgba(34,197,94,0.08);border:1px solid #22C55E44;
                    border-left:5px solid {GREEN};border-radius:8px;padding:18px;margin-bottom:18px">
          <div style="font-size:16px;font-weight:700;color:{GREEN};margin-bottom:4px">Account Active</div>
          <div style="font-size:13px;color:#94A3B8">Your account is fully active. You can make transactions normally.</div>
        </div>""",unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.metric("Account No.",account_no); c2.metric("Status","Frozen" if frozen else "Active"); c3.metric("Last Transaction","Today 14:32")

def pg_mytxns():
    u=st.session_state.user; account_no=u.get("account","")
    db_rec=db_get_account(account_no); frozen=bool(db_rec["frozen"]) if db_rec else u.get("frozen",False)
    if frozen:
        st.markdown(f"""<div style="background:rgba(239,68,68,0.08);border:1px solid #EF444444;
                    border-left:5px solid {RED};border-radius:8px;padding:22px">
          <div style="font-size:16px;font-weight:700;color:{RED};margin-bottom:6px">Account Frozen</div>
          <div style="font-size:13px;color:#94A3B8">Transactions are disabled until an analyst unfreezes your account.</div>
        </div>""",unsafe_allow_html=True); return
    page_header("My Transactions","Recent account activity")
    rows=[
        ("Today 14:32","Unknown Online Merchant","-Rs.2,340","Flagged"),
        ("Today 10:15","Swiggy",                 "-Rs.340",  "OK"),
        ("Yesterday",  "Amazon India",           "-Rs.89",   "OK"),
        ("Yesterday",  "Salary Credit",          "+Rs.52,000","OK"),
        ("2 days ago", "Uber",                   "-Rs.45",   "OK"),
        ("2 days ago", "BookMyShow",             "-Rs.120",  "OK"),
        ("3 days ago", "HDFC Bill Payment",      "-Rs.8,200","OK"),
    ]
    for date,desc,amt,status in rows:
        sc=ORANGE if status=="Flagged" else GREEN; ac=GREEN if "+" in amt else TEXT
        st.markdown(f"""<div style="display:grid;grid-template-columns:1.3fr 3fr 1.3fr 0.8fr;gap:10px;align-items:center;
                    padding:12px 16px;background:{CARD};border:1px solid {BORDER};border-radius:6px;margin-bottom:3px">
          <span style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">{date}</span>
          <span style="font-size:13px;color:{TEXT}">{desc}</span>
          <span style="font-size:13px;font-weight:700;color:{ac};text-align:right">{amt}</span>
          <span style="color:{sc};border:1px solid {sc}44;padding:2px 8px;border-radius:4px;font-family:DM Mono,monospace;font-size:9px;text-align:center">{status}</span>
        </div>""",unsafe_allow_html=True)

def pg_vera():
    u=st.session_state.user; page_header("Verify with VERA","Answer 4 questions to verify your identity")
    st.markdown(f"""<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;overflow:hidden;margin-bottom:18px">
      <div style="background:#060C18;border-bottom:1px solid {BORDER};padding:12px 20px;display:flex;align-items:center;gap:10px">
        <div style="width:8px;height:8px;border-radius:50%;background:{GREEN};box-shadow:0 0 8px {GREEN}"></div>
        <span style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};letter-spacing:1px">VERA — Verification and Evaluation Risk Agent</span>
        <span style="margin-left:auto;font-family:DM Mono,monospace;font-size:9px;color:#334155">All responses recorded</span>
      </div></div>""",unsafe_allow_html=True)
    col_chat,col_bio=st.columns([3,1])
    with col_bio:
        st.markdown(f'<p style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px">Live Biometrics</p>',unsafe_allow_html=True)
        for lbl,pct,c,val in [("Typing Speed",62,BLUE,"Normal"),("Mouse Pattern",74,GREEN,"Human"),("Bot Score",18,GREEN,"Low")]:
            st.markdown(f"""<div style="margin-bottom:14px">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">{lbl}</span>
                <span style="font-family:DM Mono,monospace;font-size:9px;color:{c}">{val}</span>
              </div>
              <div style="background:{BORDER};border-radius:3px;height:5px;overflow:hidden">
                <div style="width:{pct}%;height:100%;background:{c};border-radius:3px"></div>
              </div></div>""",unsafe_allow_html=True)
        if st.session_state.get("vera_score") is not None:
            sc=st.session_state.vera_score; c=GREEN if sc>=75 else ORANGE if sc>=50 else RED
            st.markdown(f"""<div style="background:#060C18;border:1px solid {BORDER};border-radius:8px;padding:18px;text-align:center;margin-top:12px">
              <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};margin-bottom:6px">VERA SCORE</div>
              <div style="font-size:44px;font-weight:900;color:{c};line-height:1">{sc}</div>
              <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED}">out of 100</div>
            </div>""",unsafe_allow_html=True)
    with col_chat:
        amount,t=2340.0,"14:32"
        if not st.session_state.get("vera_msgs"):
            intro=(f"Hello {u.get('name','')}. I am VERA, FraudShield's Verification Agent.\n\n"
                   f"A transaction of **Rs.{amount:,.0f}** was made on your account at {t} today at an unrecognised merchant. "
                   f"Your account has been frozen to protect you.\n\n"
                   f"I will ask you **{len(VERA_QUESTIONS)} questions**. Please answer clearly and accurately.")
            fq,_=vera_reply("",0,amount,t)
            st.session_state.vera_msgs=[{"role":"assistant","content":intro},{"role":"assistant","content":fq}]
            st.session_state.vera_step=1
        for msg in st.session_state.vera_msgs:
            if msg["role"]=="assistant":
                st.markdown(f"""<div style="margin-bottom:12px">
                  <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};letter-spacing:1px;margin-bottom:5px">VERA</div>
                  <div style="background:rgba(255,255,255,0.03);border:1px solid {BORDER};border-radius:2px 10px 10px 10px;padding:14px 16px;font-size:13px;line-height:1.7;color:{TEXT}">{msg['content']}</div>
                </div>""",unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="margin-bottom:12px;display:flex;justify-content:flex-end">
                  <div style="max-width:78%">
                    <div style="font-family:DM Mono,monospace;font-size:9px;color:{MUTED};margin-bottom:5px;text-align:right">{u.get('name','You')}</div>
                    <div style="background:rgba(239,68,68,0.07);border:1px solid #EF444433;border-radius:10px 2px 10px 10px;padding:14px 16px;font-size:13px;line-height:1.7;color:{TEXT}">{msg['content']}</div>
                  </div></div>""",unsafe_allow_html=True)
        if st.session_state.get("vera_score") is None:
            user_input=st.chat_input("Type your answer and press Enter...")
            if user_input:
                st.session_state.vera_msgs.append({"role":"user","content":user_input})
                reply,done=vera_reply(user_input,st.session_state.vera_step,amount,t)
                st.session_state.vera_msgs.append({"role":"assistant","content":reply})
                st.session_state.vera_step+=1
                if done:
                    sc=st.session_state.vera_score; account_no=u.get("account","")
                    if sc>=75:   db_update_vera(account_no,"Passed",sc)
                    elif sc>=50: db_update_vera(account_no,"In Progress",sc)
                    else:        db_update_vera(account_no,"Failed",sc)
                st.rerun()
        else:
            sc=st.session_state.vera_score
            if sc>=75:   st.success("Verification complete — responses sent to analyst. Account will be restored once approved.")
            elif sc>=50: st.warning("Responses forwarded for review. An analyst will contact you within 2 hours.")
            else:        st.error("Verification failed — please visit your nearest branch with government-issued ID.")
            if st.button("START OVER",use_container_width=True):
                st.session_state.vera_msgs=[]; st.session_state.vera_step=0; st.session_state.vera_score=None; st.rerun()
