"""FraudShield — Alerts service (SMS + Email)"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_OK = True
except ImportError:
    TWILIO_OK = False

def send_sms(to: str, body: str):
    if not TWILIO_OK: return False,"Twilio not installed. Run: pip install twilio"
    sid   = st.session_state.get("twilio_sid","").strip()
    token = st.session_state.get("twilio_token","").strip()
    frm   = st.session_state.get("twilio_from","").strip()
    if not sid:   return False,"Account SID is blank."
    if not token: return False,"Auth Token is blank."
    if not frm:   return False,"Twilio From number is blank."
    if not to:    return False,"Alert phone number is blank."
    if not sid.startswith("AC"): return False,f"SID must start with 'AC'. Got: {sid[:6]}..."
    for num,label in [(frm,"Twilio From"),(to,"Alert phone")]:
        if not num.startswith("+"): return False,f"{label} must start with + and country code."
    try:
        TwilioClient(sid,token).messages.create(body=body,from_=frm,to=to)
        return True,f"SMS delivered to {to}"
    except Exception as e:
        err = str(e)
        if "20003" in err or "authenticate" in err.lower(): return False,"Auth failed — check SID and Token."
        if "21608" in err: return False,f"{to} not verified. Add at twilio.com/console → Verified Caller IDs."
        if "21211" in err: return False,f"Invalid number: {to}. Use +CountryCode format."
        return False,f"Twilio error: {err}"

def send_email(to: str, subject: str, body: str):
    user = st.session_state.get("gmail_user","").strip()
    pw   = st.session_state.get("gmail_pass","").strip()
    if not user: return False,"Gmail address is blank."
    if not pw:   return False,"App Password is blank."
    if "@" not in user: return False,f"'{user}' is not a valid email."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject; msg["From"] = user; msg["To"] = to
        html = f"""<html><body style="font-family:Arial;background:#f4f4f4;padding:24px">
        <div style="max-width:520px;margin:0 auto;background:white;border-radius:8px;padding:28px;border-top:4px solid #DC2626">
          <h2 style="color:#DC2626;margin:0 0 16px">FraudShield Alert</h2>
          <pre style="font-family:Arial;font-size:14px;color:#1f2937;white-space:pre-wrap;line-height:1.7">{body}</pre>
          <p style="color:#9ca3af;font-size:11px;margin-top:20px;border-top:1px solid #e5e7eb;padding-top:12px">
          FraudShield v3.0 — {datetime.now().strftime('%d %B %Y %H:%M')}</p>
        </div></body></html>"""
        msg.attach(MIMEText(html,"html"))
        with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=10) as s:
            s.login(user,pw); s.send_message(msg)
        return True,f"Email sent to {to}"
    except smtplib.SMTPAuthenticationError:
        return False,"Gmail login failed. Use App Password — not your Gmail password.\nSetup: myaccount.google.com → Security → 2-Step Verification → App Passwords"
    except Exception as e:
        return False,f"Email error: {str(e)}"

def fire_alerts(txn_id,ftype,amount,score,account):
    body = (f"Transaction: {txn_id}\nType: {ftype}\nAmount: Rs.{amount:,.2f}\n"
            f"Fraud Score: {score}%\nAccount: {account}\nTime: {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"Log in to FraudShield to BLOCK or RELEASE.")
    sms_body = f"FraudShield: {txn_id} | {ftype} | Rs.{amount:,.0f} | Score:{score}%"
    results  = []
    if st.session_state.get("sms_on") and st.session_state.get("alert_phone","").strip():
        ok,msg = send_sms(st.session_state.alert_phone.strip(),sms_body)
        results.append(("SMS",ok,msg))
    if st.session_state.get("email_on") and st.session_state.get("gmail_user","").strip():
        ok,msg = send_email(st.session_state.gmail_user.strip(),f"[FraudShield] FRAUD ALERT — {txn_id} ({score}%)",body)
        results.append(("Email",ok,msg))
    if "alert_log" not in st.session_state: st.session_state.alert_log = []
    st.session_state.alert_log.insert(0,{"time":datetime.now().strftime("%H:%M:%S"),"txn":txn_id,"score":score,"results":results})
    return results
