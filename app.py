import streamlit as st
import anthropic
import json
import re
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GP Insider — Story Scanner",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── STYLES ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&family=Barlow:wght@400;500&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0b0b0d;
    color: #ede9e3;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 900px; }

/* Header */
.gp-header {
    border-bottom: 1px solid #222;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.gp-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 52px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 0.02em;
    color: #ede9e3;
}
.gp-logo span { color: #e8412a; }
.gp-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: #e8412a;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.gp-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #64625e;
    margin-top: 0.3rem;
}

/* Story card */
.story-card {
    background: #141417;
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 3px solid #e8412a;
    position: relative;
}
.story-card.heat-2 { border-left-color: #f5a623; }
.story-card.heat-3 { border-left-color: #00d4aa; }

.card-rank {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #64625e;
    margin-bottom: 0.3rem;
}
.card-headline {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 26px;
    font-weight: 700;
    line-height: 1.15;
    color: #ede9e3;
    margin-bottom: 0.6rem;
    letter-spacing: 0.02em;
}
.card-why {
    font-size: 13px;
    color: #64625e;
    line-height: 1.7;
    margin-bottom: 0.8rem;
}
.card-arc {
    background: #1c1c21;
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #ede9e3;
    margin-bottom: 0.8rem;
}
.arc-label { color: #64625e; margin-right: 6px; }

.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border-radius: 3px;
    margin-right: 5px;
    margin-bottom: 6px;
    text-transform: uppercase;
}
.badge-rivalry    { background: rgba(232,65,42,0.12);  color: #ff8a78; }
.badge-tension    { background: rgba(245,166,35,0.12); color: #ffc56a; }
.badge-anomaly    { background: rgba(0,212,170,0.1);   color: #5eead4; }
.badge-controversy{ background: rgba(79,142,247,0.12); color: #93c5fd; }
.badge-narrative  { background: rgba(168,85,247,0.12); color: #c084fc; }
.badge-buzz       { background: rgba(255,255,255,0.05);color: #64625e; }

.heat-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}
.heat-label-txt {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #64625e;
    width: 80px;
    flex-shrink: 0;
}
.heat-track {
    flex: 1;
    height: 3px;
    background: #222;
    border-radius: 2px;
    overflow: hidden;
    max-width: 300px;
}
.heat-fill-r { height: 3px; background: #e8412a; border-radius: 2px; }
.heat-fill-a { height: 3px; background: #f5a623; border-radius: 2px; }
.heat-fill-t { height: 3px; background: #00d4aa; border-radius: 2px; }
.heat-pct {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #64625e;
    width: 28px;
}

.sources-row {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #3a3835;
    margin-top: 0.5rem;
}

.top-story-box {
    background: #141417;
    border: 0.5px solid #222;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1.5rem;
    font-size: 13px;
    font-style: italic;
    color: #64625e;
}

.scan-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 0.5px solid #1e1e22;
}
.scan-title-txt {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64625e;
}
.scan-time {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #3a3835;
}

/* Streamlit button overrides */
.stButton > button {
    background-color: #e8412a !important;
    color: white !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background-color: #ff5234 !important;
}

/* Selectbox / radio */
.stSelectbox label, .stRadio label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #64625e !important;
}

/* Text input */
.stTextInput input {
    background-color: #1c1c21 !important;
    color: #ede9e3 !important;
    border: 0.5px solid #2a2a2f !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    border-radius: 6px !important;
}

.stTextInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #64625e !important;
}

/* Divider */
hr { border-color: #1e1e22 !important; }

/* Status / info boxes */
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────────
TONES = {
    "🎯  Insider Analysis":    "deep insider analysis — what the paddock is really thinking, reading between the lines, consequences beyond the obvious",
    "🔥  Drama-First":         "drama-first storytelling — emotional stakes, feuds, moments that made fans jump off their seats",
    "🔧  Technical Deep-Dive": "technical depth — bike performance anomalies, tire strategy, engineering decisions and their race consequences",
}

BADGE_HTML = {
    "rivalry":     '<span class="badge badge-rivalry">rivalry</span>',
    "tension":     '<span class="badge badge-tension">tension</span>',
    "anomaly":     '<span class="badge badge-anomaly">anomaly</span>',
    "controversy": '<span class="badge badge-controversy">controversy</span>',
    "narrative":   '<span class="badge badge-narrative">narrative</span>',
    "buzz":        '<span class="badge badge-buzz">buzz</span>',
}

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="gp-header">
    <div class="gp-eyebrow">MotoGP Intelligence · 2026 Season</div>
    <div class="gp-logo">GP<span>INSIDER</span></div>
    <div class="gp-sub">STORY SCANNER — find what's viral before you film</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR — API KEY ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="Get your key at console.anthropic.com",
        value=st.session_state.get("api_key", "")
    )
    if api_key:
        st.session_state["api_key"] = api_key
        if api_key.startswith("sk-ant-"):
            masked = api_key[:16] + "..." + api_key[-4:]
            st.success(f"✓ Key saved  `{masked}`")
        else:
            st.error("Must start with sk-ant-")

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#3a3835;line-height:1.8">
    Get your free API key:<br>
    console.anthropic.com<br><br>
    Cost per scan: ~$0.05
    </div>
    """, unsafe_allow_html=True)

# ── CONTROLS ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    tone = st.selectbox("Channel Tone", list(TONES.keys()), index=0)

with col2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    scan_clicked = st.button("⚡  SCAN NOW")

st.markdown("---")

# ── SCAN LOGIC ────────────────────────────────────────────────────────────
def run_scan(api_key, tone_desc):
    client = anthropic.Anthropic(api_key=api_key)

    # Step 1 — web search
    search_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                "Search for the latest MotoGP news from the last 48 hours. "
                "Search for: 'MotoGP 2026 latest news', 'MotoGP Brazil GP 2026', "
                "'MotoGP Ducati Aprilia Marquez Bagnaia 2026'. "
                "Return a detailed factual summary of every story — rider names, "
                "specific incidents, quotes, controversies, results, what fans are debating."
            )
        }]
    )

    news_text = "\n".join(
        block.text for block in search_response.content
        if hasattr(block, "text")
    ).strip()

    # Step 2 — generate JSON angles
    json_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=(
            "You are a JSON API. Output only raw valid JSON. "
            "No explanation, no markdown, no code fences. "
            "Your entire response must be parseable by json.loads()."
        ),
        messages=[{
            "role": "user",
            "content": f"""Based on this MotoGP news, generate 6 video story angles for GP Insider YouTube channel.

NEWS:
{news_text}

TONE: {tone_desc}

Return this exact JSON structure:
{{
  "scan_context": {{
    "round": "current round name",
    "top_story": "single biggest story in one sentence"
  }},
  "stories": [
    {{
      "rank": 1,
      "heat": 1,
      "type": "rivalry",
      "badges": ["rivalry", "buzz"],
      "headline": "punchy YouTube title max 12 words",
      "why": "3-4 sentences on why this is a great video angle RIGHT NOW with specific details",
      "arc": "setup then conflict then payoff in one sentence",
      "media_heat": 90,
      "fan_heat": 85,
      "sources": ["Crash.net", "MotoGPNews"]
    }}
  ]
}}

Rules:
- heat: 1=hottest 2=warm 3=emerging
- type: rivalry/tension/anomaly/controversy/narrative
- badges: only use: rivalry, tension, anomaly, controversy, narrative, buzz
- exactly 6 stories ranked by viral potential
- media_heat and fan_heat: integers 0-100"""
        }]
    )

    raw = "\n".join(
        block.text for block in json_response.content
        if hasattr(block, "text")
    ).strip()

    match = re.search(r'\{[\s\S]*\}', raw)
    if not match:
        raise ValueError("No JSON in response")
    return json.loads(match.group(0))


def render_card(s):
    heat_class = {1: "", 2: " heat-2", 3: " heat-3"}.get(s.get("heat", 3), " heat-3")
    heat_color = {1: "r", 2: "a", 3: "t"}.get(s.get("heat", 3), "t")

    badges_html = "".join(BADGE_HTML.get(b, "") for b in s.get("badges", []))

    media_w = s.get("media_heat", 70)
    fan_w   = s.get("fan_heat", 70)
    mc = "r" if media_w > 80 else "a" if media_w > 60 else "t"
    fc = "r" if fan_w   > 80 else "a" if fan_w   > 60 else "t"

    sources = "  ·  ".join(s.get("sources", []))

    st.markdown(f"""
    <div class="story-card{heat_class}">
        <div class="card-rank">#{str(s.get('rank','?')).zfill(2)}</div>
        {badges_html}
        <div class="card-headline">{s.get('headline','')}</div>
        <div class="card-why">{s.get('why','')}</div>
        <div class="card-arc">
            <span class="arc-label">ARC</span>{s.get('arc','')}
        </div>
        <div class="heat-row">
            <span class="heat-label-txt">MEDIA BUZZ</span>
            <div class="heat-track"><div class="heat-fill-{mc}" style="width:{media_w}%"></div></div>
            <span class="heat-pct">{media_w}%</span>
        </div>
        <div class="heat-row">
            <span class="heat-label-txt">FAN HEAT</span>
            <div class="heat-track"><div class="heat-fill-{fc}" style="width:{fan_w}%"></div></div>
            <span class="heat-pct">{fan_w}%</span>
        </div>
        <div class="sources-row">{sources}</div>
    </div>
    """, unsafe_allow_html=True)

    # Copy button per card
    copy_text = f"{s.get('headline','')}\n\n{s.get('why','')}\n\nARC: {s.get('arc','')}"
    if st.button(f"Copy angle #{s.get('rank','')}", key=f"copy_{s.get('rank','')}"):
        st.code(copy_text)


# ── MAIN TRIGGER ─────────────────────────────────────────────────────────
if scan_clicked:
    key = st.session_state.get("api_key", "").strip()
    if not key or not key.startswith("sk-ant-"):
        st.error("⚠️  Add your Anthropic API key in the sidebar first (click the arrow top-left)")
    else:
        tone_desc = TONES[tone]
        with st.spinner("🔍  Searching MotoGP news outlets..."):
            try:
                data = run_scan(key, tone_desc)
                st.session_state["last_scan"] = data
                st.session_state["last_scan_time"] = datetime.now().strftime("%d %b %Y at %H:%M")
            except anthropic.AuthenticationError:
                st.error("❌  Invalid API key. Check console.anthropic.com")
                st.stop()
            except Exception as e:
                st.error(f"❌  Error: {str(e)}")
                st.stop()

# ── RENDER RESULTS ────────────────────────────────────────────────────────
if "last_scan" in st.session_state:
    data = st.session_state["last_scan"]
    scan_time = st.session_state.get("last_scan_time", "")
    ctx = data.get("scan_context", {})

    st.markdown(f"""
    <div class="scan-header">
        <span class="scan-title-txt">Story Angles — Ranked by Viral Potential</span>
        <span class="scan-time">Scanned {scan_time}</span>
    </div>
    """, unsafe_allow_html=True)

    if ctx.get("top_story"):
        st.markdown(f"""
        <div class="top-story-box">🔥 {ctx['top_story']}</div>
        """, unsafe_allow_html=True)

    for story in data.get("stories", []):
        render_card(story)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 0;color:#3a3835;font-family:'DM Mono',monospace;font-size:13px">
        Hit SCAN NOW to find what's buzzing in MotoGP right now
    </div>
    """, unsafe_allow_html=True)
