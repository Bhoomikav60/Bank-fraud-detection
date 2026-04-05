"""FraudShield — Shared UI components"""
import streamlit as st
import plotly.graph_objects as go

BG="$0A0F1E"; CARD="#0D1424"; BORDER="#1E293B"; TEXT="#E2E8F0"
MUTED="#64748B"; RED="#EF4444"; GREEN="#22C55E"; BLUE="#3B82F6"; ORANGE="#F97316"

def inject_css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:#0A0F1E!important;color:#E2E8F0!important}
.stApp{background:#0A0F1E!important}
#MainMenu,footer,header{visibility:hidden}
section[data-testid="stSidebar"]>div{background:#0D1424!important;border-right:1px solid #1E293B!important}
section[data-testid="stSidebar"]{display:block!important;visibility:visible!important;min-width:260px!important;transform:translateX(0)!important}
button[data-testid="collapsedControl"]{display:none!important}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea textarea{background:#111827!important;border:1px solid #1E293B!important;border-radius:6px!important;color:#E2E8F0!important;font-size:13px!important}
.stTextInput>div>div>input:focus{border-color:#EF4444!important;box-shadow:0 0 0 2px rgba(239,68,68,0.15)!important}
.stButton>button{background:#1E293B!important;color:#E2E8F0!important;border:1px solid #334155!important;border-radius:6px!important;font-family:'DM Mono',monospace!important;font-size:11px!important;letter-spacing:1px!important;padding:10px 16px!important;width:100%!important;transition:all 0.15s!important}
.stButton>button:hover{background:#334155!important;border-color:#EF4444!important;color:white!important}
[data-testid="metric-container"]{background:#0D1424!important;border:1px solid #1E293B!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] label{font-family:'DM Mono',monospace!important;font-size:10px!important;letter-spacing:2px!important;color:#64748B!important;text-transform:uppercase!important}
[data-testid="stMetricValue"]{font-size:26px!important;font-weight:700!important;color:#E2E8F0!important}
.stTabs [data-baseweb="tab-list"]{background:#0D1424!important;border-bottom:1px solid #1E293B!important;gap:0!important;border-radius:8px 8px 0 0!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#64748B!important;font-family:'DM Mono',monospace!important;font-size:11px!important;letter-spacing:1px!important;border:none!important;padding:12px 22px!important}
.stTabs [aria-selected="true"]{color:#EF4444!important;border-bottom:2px solid #EF4444!important;background:rgba(239,68,68,0.05)!important}
.stSelectbox [data-baseweb="select"]>div{background:#111827!important;border-color:#1E293B!important;color:#E2E8F0!important;border-radius:6px!important}
::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-track{background:#0A0F1E}::-webkit-scrollbar-thumb{background:#1E293B;border-radius:4px}
</style>""", unsafe_allow_html=True)

def page_header(title,subtitle=""):
    sub = f"<p style='margin:4px 0 0;font-family:DM Mono,monospace;font-size:11px;color:#64748B'>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div style="padding-bottom:16px;margin-bottom:20px;border-bottom:1px solid #1E293B"><h2 style="margin:0;font-size:26px;font-weight:700;color:#F1F5F9">{title}</h2>{sub}</div>',unsafe_allow_html=True)

def badge(text,color):
    return f'<span style="background:{color}22;color:{color};border:1px solid {color}44;padding:2px 10px;border-radius:4px;font-family:DM Mono,monospace;font-size:10px;font-weight:600">{text}</span>'

def score_bar(score):
    c = "#EF4444" if score>=70 else "#F97316" if score>=40 else "#22C55E"
    lbl = "HIGH" if score>=70 else "MED" if score>=40 else "LOW"
    return f"""<div style="display:flex;align-items:center;gap:10px">
      <div style="flex:1;background:#1E293B;border-radius:4px;height:7px;overflow:hidden">
        <div style="width:{score}%;height:100%;background:{c};border-radius:4px"></div></div>
      <span style="font-family:DM Mono,monospace;font-size:12px;color:{c};font-weight:700;min-width:38px">{score}%</span>
      {badge(lbl,c)}</div>"""

def gauge_chart(score):
    c = "#EF4444" if score>=70 else "#F97316" if score>=40 else "#22C55E"
    fig = go.Figure(go.Indicator(mode="gauge+number",value=score,
        number={"suffix":"%","font":{"size":32,"color":"#F1F5F9","family":"DM Mono"}},
        gauge={"axis":{"range":[0,100],"tickfont":{"size":8,"color":"#64748B"}},
               "bar":{"color":c,"thickness":0.22},"bgcolor":"#0D1424","bordercolor":"#1E293B",
               "steps":[{"range":[0,40],"color":"rgba(34,197,94,0.06)"},
                        {"range":[40,70],"color":"rgba(249,115,22,0.06)"},
                        {"range":[70,100],"color":"rgba(239,68,68,0.08)"}],
               "threshold":{"line":{"color":"#EF4444","width":2},"thickness":0.75,"value":70}}))
    fig.update_layout(paper_bgcolor="#0D1424",plot_bgcolor="#0D1424",height=165,margin=dict(t=28,b=4,l=8,r=8))
    return fig

def info_box(text,kind="info"):
    colors={"info":("#3B82F6","#1E3A5F"),"warn":("#F97316","#431407"),"error":("#EF4444","#450a0a"),"ok":("#22C55E","#052e16")}
    fg,bg=colors.get(kind,colors["info"])
    st.markdown(f'<div style="background:{bg};border:1px solid {fg}44;border-radius:6px;padding:12px 16px;font-size:12px;color:{fg};margin:8px 0">{text}</div>',unsafe_allow_html=True)

def alert_card(a):
    c = "#EF4444" if a["score"]>=90 else "#F97316" if a["score"]>=70 else "#22C55E"
    return f"""<div style="background:#0D1424;border:1px solid #1E293B;border-left:4px solid {c};border-radius:8px;padding:16px;margin-bottom:4px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <span style="font-weight:700;font-size:15px;color:#F1F5F9">{a['id']}</span>
        {badge(a['type'].upper(),c)}
        <span style="margin-left:auto;font-family:DM Mono,monospace;font-size:10px;color:#64748B">{a['time']}</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:12px">
        <div><div style="font-family:DM Mono,monospace;font-size:9px;color:#64748B">AMOUNT</div>
             <div style="font-size:17px;font-weight:700;color:#F1F5F9">Rs.{a['amount']:,.0f}</div></div>
        <div><div style="font-family:DM Mono,monospace;font-size:9px;color:#64748B">ACCOUNT</div>
             <div style="font-family:DM Mono,monospace;font-size:13px;color:#F1F5F9">{a['account']}</div></div>
        <div><div style="font-family:DM Mono,monospace;font-size:9px;color:#64748B">CUSTOMER</div>
             <div style="font-size:13px;color:#F1F5F9">{a['customer']}</div></div>
      </div>
      {score_bar(a['score'])}</div>"""
