# ------------------------------------------------------------
# Pomodoro Pro — ;ajri Salma 
# ------------------------------------------------------------
import os, time, re
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pomodoro Pro", page_icon="⏱️", layout="wide")
DATA_FILE = "sessions.csv"

THEMES = {
    "Classic": {"accent":"#ff6680","accent2":"#ffad78","bg":"#10111f","bg2":"#24121f","emoji":"⏱️","desc":"Classic focus atmosphere","visual":"classic"},
    "Rain": {"accent":"#66b8ff","accent2":"#c4e7ff","bg":"#071827","bg2":"#0a3450","emoji":"🌧️","desc":"Rain falling on a window","visual":"rain"},
    "Thunderstorm": {"accent":"#9bb7ff","accent2":"#d6dcff","bg":"#11182b","bg2":"#303957","emoji":"⛈️","desc":"A moody stormy night","visual":"rain"},
    "Forest": {"accent":"#61d69a","accent2":"#c2f5a5","bg":"#09251c","bg2":"#174734","emoji":"🌲","desc":"Quiet forest ambience","visual":"forest"},
    "Fireplace": {"accent":"#ff9b55","accent2":"#ffd08a","bg":"#28140d","bg2":"#522719","emoji":"🔥","desc":"Warm fireplace ambience","visual":"fire"},
    "Ocean": {"accent":"#35c7d8","accent2":"#8de8e5","bg":"#061d2a","bg2":"#07566a","emoji":"🌊","desc":"Deep-blue ocean atmosphere","visual":"ocean"},
    "Brown noise": {"accent":"#d7a477","accent2":"#f2d0a8","bg":"#21170f","bg2":"#50321d","emoji":"〰️","desc":"Warm, soft noise for focus","visual":"waves"},
    "Lo-fi": {"accent":"#c084fc","accent2":"#ff9ecf","bg":"#1b102b","bg2":"#45205c","emoji":"🎹","desc":"Purple night and lo-fi mood","visual":"lofi"},
    "Piano": {"accent":"#b9c5ff","accent2":"#f4d7ff","bg":"#17182b","bg2":"#34304e","emoji":"🎹","desc":"Soft piano-inspired theme","visual":"lofi"},
    "Jazz": {"accent":"#f0bd69","accent2":"#ffe4a3","bg":"#211a13","bg2":"#45301b","emoji":"🎷","desc":"Warm late-night jazz mood","visual":"fire"},
    "Ambient": {"accent":"#8ad7d0","accent2":"#d0fff1","bg":"#102426","bg2":"#204347","emoji":"✨","desc":"Dreamy ambient atmosphere","visual":"ocean"},
}
PHASES = {
    "focus": {"label":"Focus","icon":"🔥","accent":"#ff6680","accent2":"#ffad78"},
    "short": {"label":"Short Break","icon":"🌿","accent":"#31d6ad","accent2":"#9be56e"},
    "long": {"label":"Long Break","icon":"🌊","accent":"#7d8cff","accent2":"#c084fc"},
}
ss = st.session_state
DEFAULTS = {"phase":"focus","running":False,"end_time":0.0,"remaining":1500,"total":1500,"cycles":0,"notice":"","theme":"Classic","task":"","yt_url":""}
for k,v in DEFAULTS.items():
    if k not in ss: ss[k] = v

# Sidebar settings
st.sidebar.markdown("## ⚙️ Settings")
focus_min = st.sidebar.slider("Focus (minutes)", 1, 60, 25)
short_min = st.sidebar.slider("Short break (minutes)", 1, 30, 5)
long_min = st.sidebar.slider("Long break (minutes)", 5, 45, 15)
long_every = st.sidebar.slider("Long break every N sessions", 2, 8, 4)
daily_goal = st.sidebar.slider("Daily goal (sessions)", 1, 16, 8)
auto_start = st.sidebar.checkbox("Auto-start next phase", value=False)
chime_on = st.sidebar.checkbox("Show notification when phase ends", value=True)
DURATIONS = {"focus":focus_min*60,"short":short_min*60,"long":long_min*60}
if not ss.running and ss.remaining == ss.total and ss.total != DURATIONS[ss.phase]:
    ss.total = DURATIONS[ss.phase]; ss.remaining = ss.total

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty and "timestamp" in df:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df
        except Exception: pass
    return pd.DataFrame(columns=["timestamp","task","minutes"])

def save_session(task, minutes):
    pd.DataFrame([{"timestamp":datetime.now().isoformat(timespec="seconds"),"task":task.strip() or "No task","minutes":int(minutes)}]).to_csv(DATA_FILE, mode="a", header=not os.path.exists(DATA_FILE), index=False)

def set_phase(p):
    ss.phase=p; ss.total=DURATIONS[p]; ss.remaining=ss.total; ss.running=False

def start_timer():
    if ss.remaining <= 0: ss.remaining=ss.total
    ss.running=True; ss.end_time=time.time()+ss.remaining

def pause_timer():
    if ss.running: ss.remaining=max(0,int(round(ss.end_time-time.time())))
    ss.running=False

def reset_timer():
    ss.running=False; ss.remaining=ss.total

def next_phase(log_session=True):
    if ss.phase == "focus":
        if log_session:
            save_session(ss.task, focus_min); ss.cycles += 1
        nxt = "long" if ss.cycles and ss.cycles % long_every == 0 else "short"
    else: nxt="focus"
    set_phase(nxt); ss.notice=f"Time for: {PHASES[nxt]['label']}"
    if auto_start: start_timer()

def skip_timer():
    ss.running=False; next_phase(log_session=False)

# Theme selector uses a native Streamlit control, so the outer app reruns and changes theme.
st.markdown("<div style='text-align:center;font-size:2.35rem;font-weight:850;letter-spacing:-.04em'>⏱️ Pomodoro <span style='color:#35c7d8'>Pro</span></div><div style='text-align:center;color:#c6cce2;margin-bottom:18px'>A calmer space to focus, one session at a time.</div>", unsafe_allow_html=True)
col1,col2,col3=st.columns([1,2,1])
with col2:
    category = st.radio("Choose a sound collection", ["🎹 Music", "🌧️ Nature", "▶️ YouTube"], horizontal=True, label_visibility="visible")
    if category == "🎹 Music":
        choices=["Classic","Lo-fi","Piano","Jazz","Ambient","Brown noise"]
        current=ss.theme if ss.theme in choices else "Lo-fi"
        ss.theme=st.selectbox("🎧 Music & focus atmosphere", choices, index=choices.index(current))
    elif category == "🌧️ Nature":
        choices=["Rain","Thunderstorm","Forest","Fireplace","Ocean","Brown noise"]
        current=ss.theme if ss.theme in choices else "Rain"
        ss.theme=st.selectbox("🌿 Nature sounds", choices, index=choices.index(current))
    else:
        st.caption("Paste a YouTube video or playlist link below. Some videos may block embedded playback.")
        ss.yt_url=st.text_input("YouTube URL", value=ss.yt_url, placeholder="https://www.youtube.com/watch?v=...")
        choices=["Classic","Rain","Ocean","Lo-fi","Ambient"]
        current=ss.theme if ss.theme in choices else "Lo-fi"
        ss.theme=st.selectbox("🎨 Interface atmosphere", choices, index=choices.index(current))

T=THEMES[ss.theme]; accent=T["accent"]; accent2=T["accent2"]
visual=T["visual"]
if visual == "rain": overlay=""".stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.32;background-image:repeating-linear-gradient(105deg,transparent 0 17px,rgba(190,225,255,.65) 18px,transparent 19px 37px),repeating-linear-gradient(105deg,transparent 0 49px,rgba(120,190,245,.4) 50px,transparent 51px 76px);background-size:170px 240px,260px 330px;animation:rainfall .65s linear infinite}@keyframes rainfall{from{background-position:0 -240px,40px -330px}to{background-position:-18px 0,10px 0}}"""
elif visual == "ocean": overlay=""".stApp::before{content:'';position:fixed;left:-10%;right:-10%;bottom:-60px;height:45vh;pointer-events:none;z-index:0;opacity:.27;background:repeating-radial-gradient(ellipse at 50% 100%,transparent 0 28px,rgba(100,240,245,.65) 30px 32px,transparent 35px 59px);animation:wave 7s ease-in-out infinite alternate}@keyframes wave{from{transform:translateX(-2%) scaleY(.8)}to{transform:translateX(2%) scaleY(1.15)}}"""
elif visual == "lofi": overlay=""".stApp::before{content:'✦      ·      ✧       ·      ✦       ·      ✧';white-space:pre;position:fixed;inset:0;pointer-events:none;z-index:0;padding:30px;color:#ffe5ff;opacity:.3;font-size:24px;letter-spacing:18px;line-height:3.5;animation:stars 4s ease-in-out infinite alternate}@keyframes stars{from{opacity:.12}to{opacity:.4}}"""
elif visual == "forest": overlay=""".stApp::before{content:'♧     ·      ♧       ·       ♧';white-space:pre;position:fixed;inset:0;pointer-events:none;z-index:0;padding:35px;color:#a8f0bb;opacity:.22;font-size:25px;letter-spacing:18px;line-height:4;animation:forest 7s ease-in-out infinite alternate}@keyframes forest{from{transform:translateY(-8px);opacity:.12}to{transform:translateY(12px);opacity:.3}}"""
elif visual == "fire": overlay=""".stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse at 50% 100%,rgba(255,115,35,.23),transparent 55%);animation:embers 3s ease-in-out infinite alternate}@keyframes embers{from{opacity:.45}to{opacity:1}}"""
else: overlay=""".stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse at 15% 85%,rgba(255,210,150,.1),transparent 45%)}"""

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
{overlay}
html,body,[class*='css']{{font-family:Inter,system-ui,sans-serif}}
.stApp,[data-testid='stAppViewContainer'],[data-testid='stMain']{{background:radial-gradient(ellipse at 15% 0%,{accent}55,transparent 48%),linear-gradient(135deg,{T['bg']} 0%,{T['bg2']} 52%,#0b0c16 100%) !important;background-attachment:fixed !important;color:#f7f8ff !important}}
[data-testid='stHeader']{{background:transparent!important}} [data-testid='stSidebar']{{background:{T['bg']}!important;border-right:1px solid {accent}77}}
[data-testid='stSidebar'] *{{color:#f7f8ff!important}} h1,h2,h3,p,label,[data-testid='stMarkdownContainer'],[data-testid='stMetricValue'],[data-testid='stMetricLabel']{{color:#f7f8ff}}
[data-testid='stTabs'] [data-baseweb='tab']{{color:#f7f8ff!important}} [data-baseweb='tab-highlight']{{background:{accent}!important}}
[data-testid='stTabs'] [aria-selected='true']{{color:{accent2}!important}}
div[data-testid='stMetric']{{background:{accent}20!important;border:1px solid {accent}66!important;border-radius:16px;padding:14px}}
.stButton>button,.stDownloadButton>button{{border-radius:999px;border:1px solid {accent}88;background:{accent}20;color:#fff;min-height:2.7rem}}
.stButton>button:hover,.stDownloadButton>button:hover{{border-color:{accent2};background:{accent}50;color:#fff}}
.stButton>button[kind='primary']{{background:linear-gradient(120deg,{accent},{accent2})!important;color:#101321!important;border:0;font-weight:800}}
[data-testid='stExpander']{{background:{accent}15!important;border:1px solid {accent}55!important;border-radius:14px}}
[data-baseweb='select']>div{{background:{T['bg2']}!important;border-color:{accent}88!important}}
[data-testid='stTextInput'] input{{background:{T['bg2']}!important;color:#fff!important;border:1px solid {accent}88!important}}
[data-testid='stProgressBar']>div>div{{background:linear-gradient(90deg,{accent},{accent2})!important}}
.block-container{{max-width:1100px;padding-top:1.5rem;padding-bottom:3rem}} footer{{visibility:hidden}}
</style>""", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center;padding:10px;border:1px solid {accent}77;background:{accent}16;border-radius:14px;margin:10px auto 18px;max-width:600px'>{T['emoji']} <b>{ss.theme}</b> — {T['desc']}</div>", unsafe_allow_html=True)

# YouTube embed is shown only when the YouTube collection is selected.
if category == "▶️ YouTube" and ss.yt_url.strip():
    match=re.search(r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})',ss.yt_url.strip())
    if match:
        video_id=match.group(1)
        components.html(f'''<div style="border:1px solid {accent}88;border-radius:16px;overflow:hidden"><iframe width="100%" height="240" src="https://www.youtube-nocookie.com/embed/{video_id}" title="YouTube music" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>''',height=250,scrolling=False)
    else:
        st.warning("Couldn't recognize this YouTube link. Paste a standard video URL, for example youtube.com/watch?v=... .")

# Web Audio sound player for ambient sounds and simple generated music.
player_html = r'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{margin:0;background:transparent;color:#f5f6ff;font:14px system-ui,sans-serif}.card{padding:16px;border-radius:18px;background:rgba(255,255,255,.055);border:1px solid __ACCENT__88}.top{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:12px}.status{opacity:.75;font-size:12px}.buttons{display:flex;gap:8px;flex-wrap:wrap}.chip{border:1px solid #ffffff30;background:#ffffff0b;color:white;border-radius:999px;padding:9px 13px;cursor:pointer}.chip:hover,.chip.active{background:__ACCENT__;color:#10111f;border-color:transparent}.vol{display:flex;align-items:center;gap:12px;margin-top:14px;font-size:12px}.vol input{flex:1;accent-color:__ACCENT__}
</style></head><body><div class="card"><div class="top"><b>🎧 Built-in sounds & generated music</b><span class="status" id="status">Choose a sound</span></div><div class="buttons">
<button class="chip" data-s="rain">🌧️ Rain</button><button class="chip" data-s="thunder">⛈️ Thunder ambience</button><button class="chip" data-s="forest">🌲 Forest</button><button class="chip" data-s="fire">🔥 Fireplace</button><button class="chip" data-s="ocean">🌊 Ocean</button><button class="chip" data-s="brown">〰️ Brown noise</button><button class="chip" data-s="lofi">🎹 Lo-fi</button><button class="chip" data-s="piano">🎼 Piano tones</button><button class="chip" data-s="jazz">🎷 Jazz tones</button><button class="chip" id="stop">■ Stop</button></div><div class="vol"><span>Volume</span><input id="volume" type="range" min="0" max="100" value="40"></div><small style="display:block;margin-top:8px;opacity:.7">Generated sounds are ambient effects/simple tones, not full commercial songs. Click a button to start audio.</small></div>
<script>(()=>{let ctx=null,master=null,nodes=[],timers=[];const $=id=>document.getElementById(id),buttons=[...document.querySelectorAll('[data-s]')];function init(){if(!ctx){ctx=new(window.AudioContext||window.webkitAudioContext)();master=ctx.createGain();master.gain.value=(+$('volume').value/100)**2*.8;master.connect(ctx.destination)}if(ctx.state==='suspended')ctx.resume()}function noise(kind){let b=ctx.createBuffer(1,ctx.sampleRate*4,ctx.sampleRate),d=b.getChannelData(0),last=0;for(let i=0;i<d.length;i++){let w=Math.random()*2-1;if(kind==='brown'){last=(last+.025*w)/1.025;d[i]=last*3}else d[i]=w*.5}return b}function stop(){nodes.forEach(n=>{try{n.stop()}catch(e){}try{n.disconnect()}catch(e){}});nodes=[];timers.forEach(clearInterval);timers=[];buttons.forEach(b=>b.classList.remove('active'));$('status').textContent='Choose a sound'}function play(name){init();stop();let out=ctx.createGain();out.gain.value=.55;out.connect(master);function src(kind,filter,freq,gain){let s=ctx.createBufferSource();s.buffer=noise(kind);s.loop=true;let f=ctx.createBiquadFilter();f.type=filter;f.frequency.value=freq;let g=ctx.createGain();g.gain.value=gain;s.connect(f).connect(g).connect(out);s.start();nodes.push(s)}if(name==='rain'){src('white','bandpass',1400,.5);src('white','highpass',4500,.12);src('brown','lowpass',240,.4)}if(name==='thunder'){src('brown','lowpass',180,.8);src('white','lowpass',500,.12)}if(name==='forest'){src('white','highpass',3500,.06);src('brown','lowpass',400,.12)}if(name==='fire'){src('brown','lowpass',700,.3);src('white','bandpass',2400,.07)}if(name==='ocean'){src('white','lowpass',450,.3);src('brown','lowpass',160,.6)}if(name==='brown'){src('brown','lowpass',650,.8)}if(['lofi','piano','jazz'].includes(name)){let chords=name==='jazz'?[[146.83,185,220,277.18],[130.81,164.81,196,246.94],[164.81,207.65,246.94,293.66]]:name==='piano'?[[261.63,329.63,392],[220,261.63,329.63],[196,246.94,293.66]]:[[220,261.63,329.63,392],[174.61,220,261.63,329.63],[261.63,329.63,392,493.88],[196,246.94,293.66,392]];let idx=0;function chord(){let now=ctx.currentTime;chords[idx++%chords.length].forEach((freq,k)=>{let o=ctx.createOscillator(),g=ctx.createGain();o.type=name==='piano'?'sine':(k?'triangle':'sine');o.frequency.value=freq;g.gain.setValueAtTime(.0001,now);g.gain.linearRampToValueAtTime(name==='piano'?.045:.025,now+.25);g.gain.exponentialRampToValueAtTime(.0001,now+(name==='jazz'?2.2:3.5));o.connect(g).connect(out);o.start(now);o.stop(now+(name==='jazz'?2.4:3.7));nodes.push(o)})}chord();timers.push(setInterval(chord,name==='jazz'?2400:3300));if(name==='lofi')src('white','lowpass',1800,.01)}buttons.forEach(b=>b.classList.toggle('active',b.dataset.s===name));$('status').textContent='Playing: '+name}buttons.forEach(b=>b.addEventListener('click',()=>{if(b.classList.contains('active'))stop();else play(b.dataset.s)}));$('stop').addEventListener('click',stop);$('volume').addEventListener('input',()=>{if(master)master.gain.value=(+$('volume').value/100)**2*.8})})();</script></body></html>'''.replace('__ACCENT__',accent)
components.html(player_html,height=230,scrolling=False)

# Timer and stats
st.divider()
tab_timer,tab_stats=st.tabs(["⏱️ Timer","📊 Statistics"])
with tab_timer:
    phase=PHASES[ss.phase]
    st.markdown(f"<div style='text-align:center;color:{accent};font-weight:800;letter-spacing:.15em;margin:15px 0'>{phase['icon']} {phase['label'].upper()}</div>",unsafe_allow_html=True)
    remaining=max(0,int(round(ss.end_time-time.time()))) if ss.running else max(0,int(ss.remaining))
    minutes,seconds=divmod(remaining,60); progress=1-remaining/ss.total if ss.total else 0
    st.markdown(f'''<div style="max-width:410px;margin:0 auto 20px;padding:34px 18px;text-align:center;border-radius:50%;background:radial-gradient(circle,{accent}20,transparent 70%);border:3px solid {accent}99;box-shadow:0 0 40px {accent}30"><div style="font-size:clamp(3.8rem,9vw,6rem);font-weight:800;letter-spacing:-.06em;font-variant-numeric:tabular-nums;line-height:1.2">{minutes:02d}:{seconds:02d}</div><div style="height:7px;background:#ffffff20;border-radius:99px;max-width:280px;margin:20px auto 0;overflow:hidden"><div style="height:100%;width:{min(100,max(0,progress*100))}%;background:linear-gradient(90deg,{accent},{accent2});border-radius:99px"></div></div><div style="margin-top:12px;color:#d4d9ed;font-size:.85rem">Session {ss.cycles+1} · {int(progress*100)}% complete</div></div>''',unsafe_allow_html=True)
    ss.task=st.text_input("What are you working on?",value=ss.task,placeholder="e.g. Study Python")
    a,b,c,d=st.columns(4)
    with a: st.button("⏸ Pause" if ss.running else "▶ Start",type="primary",use_container_width=True,on_click=pause_timer if ss.running else start_timer)
    with b: st.button("↻ Reset",use_container_width=True,on_click=reset_timer)
    with c: st.button("⏭ Skip",use_container_width=True,on_click=skip_timer)
    with d: st.button("⚡ Focus",use_container_width=True,on_click=lambda:set_phase("focus"))
    st.caption("Keep this tab open while the timer runs. Browser sleep or notebook disconnection may pause updates.")
    if ss.notice: st.info(ss.notice); ss.notice=""
with tab_stats:
    df=load_data()
    if df.empty: st.info("No finished focus sessions yet. Complete a focus session to see statistics.")
    else:
        df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce"); df=df.dropna(subset=["timestamp"]); df["date"]=df["timestamp"].dt.date
        today=date.today(); today_df=df[df["date"]==today]
        m1,m2,m3,m4=st.columns(4); m1.metric("Sessions today",f"{len(today_df)}/{daily_goal}"); m2.metric("Minutes today",int(today_df["minutes"].sum())); m3.metric("Days with sessions",len(set(df["date"]))); m4.metric("Total hours",f"{df['minutes'].sum()/60:.1f}")
        st.progress(min(len(today_df)/daily_goal,1.0),text="Daily goal progress")
        last7=pd.date_range(end=today,periods=7).date; daily=df.groupby("date")["minutes"].sum().reindex(last7,fill_value=0)
        weekly=pd.DataFrame({"Day":[d.strftime("%a %d") for d in last7],"Minutes":daily.values})
        fig=px.bar(weekly,x="Day",y="Minutes",title="Focus minutes — last 7 days",color_discrete_sequence=[accent]); fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#f0f1fb"); st.plotly_chart(fig,use_container_width=True)
        by_task=df.groupby("task",as_index=False)["minutes"].sum(); fig2=px.pie(by_task,names="task",values="minutes",hole=.55,title="Time by task"); fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#f0f1fb"); st.plotly_chart(fig2,use_container_width=True)
        with st.expander("📜 Session history"): st.dataframe(df.sort_values("timestamp",ascending=False)[["timestamp","task","minutes"]],use_container_width=True)
        x,y=st.columns(2); x.download_button("⬇ Download CSV",df.drop(columns=["date"],errors="ignore").to_csv(index=False),"sessions.csv",use_container_width=True)
        if y.button("🗑 Clear all data",use_container_width=True):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.rerun()

if ss.running:
    left=ss.end_time-time.time()
    if left<=0:
        next_phase(log_session=True)
        if chime_on: st.toast("🔔 Timer finished!")
        st.rerun()
    else:
        time.sleep(1); st.rerun()
