import streamlit as st
import anthropic
from streamlit_ace import st_ace

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CS Problem-Solving Tutor",
    page_icon="💻",
    layout="wide",
)

# ── System prompt (hidden from students) ───────────────────────────────────────
SYSTEM_PROMPT = """You are a computer science tutor working with GCSE students learning Python. Your role is not to teach by explaining — it is to help students think, articulate, and construct understanding themselves through conversation.

CORE RULES — never break these:
1. Never write a complete solution. If a student asks you to write code for them, decline and redirect.
2. Always ask the student to think or predict before you confirm or extend anything.
3. If a student is wrong, do not correct them directly. Ask a question that helps them notice the issue themselves.
4. Keep your responses short. One question or one small nudge at a time. Resist the urge to explain everything.
5. Match your language to the student — if they are struggling, simplify. If they are confident, push harder.

WHEN A STUDENT SHARES CODE:
- The student has pasted or written code into their editor and sent it to you.
- Do not rewrite or complete it. Ask what they think it does, or where they think it might be going wrong.
- If it is incomplete, ask: "What do you want the next part to do?"
- If it has a bug, do not name the bug. Ask: "What did you expect this to do, and what do you think actually happens?"

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
When a student first arrives, greet them warmly and briefly, then ask: "What are you working on today — are you trying to write something, trace some code, or debug a problem?  You can ask me to set you a problem to work on or describe your own, you can also tell me if there's an area of programming that you need to practice." Then wait."""

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0; }
    .editor-label {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 0.25rem;
    }
    /* Chat container scrollable */
    .chat-area {
        height: 65vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
col_title, col_reset = st.columns([6, 1])
with col_title:
    st.markdown("### 💻 CS Problem-Solving Tutor")
    st.caption("Think it through — I won't write it for you, but I'll help you get there.")
with col_reset:
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

# ── Two-column layout ──────────────────────────────────────────────────────────
col_chat, col_editor = st.columns([1, 1], gap="medium")

# ── LEFT — Chat ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown("**Conversation**")

    # Opening message
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            opening = "Hi! I'm your CS tutor. I won't write code for you — but I'll work through problems with you step by step.\n\nWhat are you working on today — are you trying to **write** something, **trace** some code, or **debug** a problem?"
            st.markdown(opening)
            st.session_state.messages.append({"role": "assistant", "content": opening})

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Text chat input
    if prompt := st.chat_input("Type your answer or question here…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
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

# ── RIGHT — Code editor ────────────────────────────────────────────────────────
with col_editor:
    st.markdown("**Code editor**")
    st.caption("Write your code here. Use the button to send it to the tutor.")

    code = st_ace(
        placeholder="# Start typing your Python here...",
        language="python",
        theme="tomorrow",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        auto_update=True,
        height=400,
        key="ace_editor",
    )

    send_col, clear_col = st.columns([2, 1])
    with send_col:
        if st.button("▶ Send code to tutor", use_container_width=True):
            if code and code.strip():
                message = f"Here is my code:\n\n```python\n{code}\n```"
                st.session_state.messages.append({"role": "user", "content": message})
                with st.spinner(""):
                    try:
                        response = st.session_state.client.messages.create(
                            model="claude-opus-4-5",
                            max_tokens=1024,
                            system=SYSTEM_PROMPT,
                            messages=st.session_state.messages,
                        )
                        reply = response.content[0].text
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
            else:
                st.warning("Editor is empty — write some code first.")
