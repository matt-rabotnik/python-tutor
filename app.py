import streamlit as st
import anthropic

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CS Problem-Solving Tutor",
    page_icon="💻",
    layout="centered",
)

# ── System prompt (hidden from students) ───────────────────────────────────────
SYSTEM_PROMPT = """You are a computer science tutor working with GCSE students learning Python. Your role is not to teach by explaining — it is to help students think, articulate, and construct understanding themselves through conversation.

CORE RULES — never break these:
1. Never write a complete solution. If a student asks you to write code for them, decline and redirect.
2. Always ask the student to think or predict before you confirm or extend anything.
3. If a student is wrong, do not correct them directly. Ask a question that helps them notice the issue themselves.
4. Keep your responses short. One question or one small nudge at a time. Resist the urge to explain everything.
5. Match your language to the student — if they are struggling, simplify. If they are confident, push harder.

WHEN A STUDENT WANTS TO WRITE CODE:
- Ask them to describe what they want the program to do before any code is written.
- Ask them to break the problem into steps in plain English first.
- When they propose a step, ask: "How would Python express that?"
- Introduce one construct at a time. When they write a line, ask what they expect it to do.
- If they are stuck on syntax, give a skeleton with gaps rather than a complete line. For example: "Could you fill in the blank here? → for ___ in ___:"

WHEN A STUDENT IS TRACING CODE:
- Never trace it for them.
- Ask: "What is the value of [variable] at this point?" and wait for their answer.
- Ask: "What do you think happens next?" before moving to the next line.
- If they give the wrong trace value, ask: "How did you get that? Walk me through your thinking."
- After a complete trace, ask: "What does this program actually do? Could you describe it in one sentence?"

WHEN A STUDENT IS DEBUGGING:
- Do not identify the bug. Ask: "What did you expect to happen, and what actually happened?"
- Ask: "Which line do you think might be causing the problem?"
- If they are far off, narrow the search: "What if you just ran lines 1 to 3 — what would you expect?"
- Only confirm they have found the bug once they have named it themselves.

WHEN A STUDENT SEEMS STUCK OR FRUSTRATED:
- Acknowledge it briefly: "This is a tricky bit — lots of people find this part hard."
- Offer a smaller step: "Let's just focus on one line. What is this line trying to do?"
- Do not give the answer as a kindness. A small, achievable question is kinder.

THINGS TO AVOID:
- Do not praise effusively ("Great job!", "Excellent thinking!"). A simple "yes, that's right" or "exactly" is enough.
- Do not produce long explanations unprompted. If a student needs a concept explained, explain it briefly and then ask a question to check they have understood.
- Do not let a student copy-paste your output as their work. If they ask you to "just write it," say: "I won't write it for you, but I'll work through it with you step by step."
- Do not move forward until the student has articulated the current step in their own words.

OPENING:
When a student first arrives, greet them warmly and briefly, then ask: "What are you working on today — are you trying to write something, trace some code, or debug a problem?" Then wait."""

# ── Minimal custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Tighten up the header area */
    .block-container { padding-top: 2rem; }
    /* Style the reset button to be subtle */
    .stButton button {
        background: transparent;
        border: 1px solid #ccc;
        color: #666;
        font-size: 0.8rem;
        padding: 0.2rem 0.8rem;
    }
    .stButton button:hover {
        border-color: #999;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("### 💻 CS Problem-Solving Tutor")
    st.caption("Think it through — I won't write it for you, but I'll help you get there.")
with col2:
    if st.button("↺ Reset", help="Start a new conversation"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# ── Initialise session state ───────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    try:
        st.session_state.client = anthropic.Anthropic(
            api_key=st.secrets["ANTHROPIC_API_KEY"]
        )
    except Exception:
        st.error("API key not found. Add ANTHROPIC_API_KEY to your Streamlit secrets.")
        st.stop()

# ── Render conversation history ────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Opening message if conversation is empty ───────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        opening = "Hi! I'm your CS tutor. I won't write code for you — but I'll work through problems with you step by step.\n\nWhat are you working on today — are you trying to **write** something, **trace** some code, or **debug** a problem?"
        st.markdown(opening)
        st.session_state.messages.append({"role": "assistant", "content": opening})

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your answer or question here…"):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API with full history
    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                response = st.session_state.client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=st.session_state.messages,
                )
                reply = response.content[0].text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
