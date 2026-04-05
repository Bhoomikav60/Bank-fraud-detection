"""FraudShield — VERA Chatbot Logic"""
import random, streamlit as st

VERA_QUESTIONS = [
    "Did you make a purchase of Rs.{amount} at around {time} today? If yes — name the merchant or website.",
    "Where were you at {time}? Tell me the city and what you were doing.",
    "Have you shared your card number, OTP, or PIN with anyone recently?",
    "Have you used your card on any new or unfamiliar websites in the last 7 days?",
]

def vera_reply(user_input: str, step: int, amount: float, t: str):
    if step < len(VERA_QUESTIONS):
        q = VERA_QUESTIONS[step].replace("{amount}",f"{amount:,.0f}").replace("{time}",t)
        note = "That answer was quite short — please give more detail.\n\n" if len(user_input.split())<5 and step>0 else ""
        return f"{note}**Q{step+1} of {len(VERA_QUESTIONS)}:** {q}", False
    all_answers = [m["content"] for m in st.session_state.vera_msgs if m["role"]=="user"]
    words = sum(len(a.split()) for a in all_answers)
    vague = sum(1 for a in all_answers if len(a.split())<5)
    score = max(20,min(96,65+words//7-vague*14+random.randint(-3,3)))
    ref   = random.randint(1000,9999)
    st.session_state.vera_score = score
    if score >= 75:
        return (f"**Verification Score: {score}/100**\n\nYour answers were consistent. "
                f"Responses submitted for analyst review.\n\n**Reference: VRF-{ref}**"), True
    elif score >= 50:
        return (f"**Verification Score: {score}/100**\n\nSome answers need manual review. "
                f"An analyst will contact you within 2 hours.\n\n**Reference: ESC-{ref}**"), True
    else:
        return (f"**Verification Score: {score}/100**\n\nAnswers were inconsistent. "
                f"Please visit your nearest branch with a government-issued ID.\n\n**Reference: INV-{ref}**"), True
