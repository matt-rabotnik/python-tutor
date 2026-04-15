import streamlit as st
import anthropic
from streamlit_ace import st_ace

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CS Problem-Solving Tutor",
    page_icon="💻",
    layout="centered",
)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a computer science tutor working with GCSE students learning Python. Your role is not to teach by explaining — it is to help students think, articulate, and construct understanding themselves through conversation.

CORE RULES — never break these:
1. Never write a complete solution. If a student asks you to write code for them, decline and redirect.
2. Always ask the student to think or predict before you confirm or extend anything.
3. If a student is wrong, do not correct them directly. Ask a question that helps them notice the issue themselves.
4. Keep your responses short. One question or one small nudge at a time. Resist the urge to explain everything.
5. Match your language to the student — if they are struggling, simplify. If they are confident, push harder.

REQUESTING A CODE EDITOR:
When you want the student to write or edit code, end your message with exactly this token on its own line:
[CODE_EDITOR]
Only include this token when you genuinely want the student to write or modify code. Do not include it for questions that require a text answer.

WHEN A STUDENT SHARES CODE:
- Do not rewrite or complete it. Ask what they think it does, or where they think it might be going wrong.
- If it is incomplete, ask: "What do you want the next part to do?" and include [CODE_EDITOR] so they can continue.
- If it has a bug, do not name the bug. Ask: "What did you expect this to do, and what do you think actually happens?"

WHEN A STUDENT WANTS TO WRITE CODE:
- Ask them to describe what they want the program to do before any code is written.
- Ask them to break the problem into steps in plain English first.
- When they are ready to write, include [CODE_EDITOR] at the end of your message.
- Introduce one construct at a time. When they write a line, ask what they expect it to do.
- If they are stuck on syntax, give a skeleton with gaps rather than a complete line. For example: "Could you fill in the blank here? → for ___ in ___:" and include [CODE_EDITOR].

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
- When they are ready to fix it, include [CODE_EDITOR].

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

EDITOR_TOKEN = "[CODE_EDITOR]"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit's top toolbar/header bar */
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }
    /* Pull content to the top */
    .block-container { padding-top: 1.5rem !important; margin-top: 0 !important; }
    div[data-testid="stChatMessage"] { margin-bottom: 0.5rem; }
    .editor-submitted {
        background: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-family: monospace;
        font-size: 13px;
        white-space: pre-wrap;
        color: #333;
        margin: 0.5rem 0;
    }
    .editor-label {
        font-size: 0.75rem;
        color: #999;
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def call_api(messages):
    try:
        response = st.session_state.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"ERROR: {e}"

def strip_token(text):
    """Remove [CODE_EDITOR] token from display text."""
    return text.replace(EDITOR_TOKEN, "").strip()

def build_transcript():
    """Build plain text transcript of the full conversation."""
    lines = ["CS PROBLEM-SOLVING TUTOR — SESSION TRANSCRIPT", "=" * 50, ""]
    for msg in st.session_state.messages:
        role = "Tutor" if msg["role"] == "assistant" else "Student"
        content = msg["content"]
        if msg.get("type") == "code":
            lines.append(f"{role}:")
            lines.append("[Code submitted]")
            lines.append(content)
        else:
            clean = strip_token(content)
            lines.append(f"{role}:")
            lines.append(clean)
        lines.append("")
    return "\n".join(lines)

def wants_editor(text):
    return EDITOR_TOKEN in text

# ── Session state ──────────────────────────────────────────────────────────────
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

# ── Header ─────────────────────────────────────────────────────────────────────
col_title, col_copy, col_reset = st.columns([5, 1.2, 0.8])
with col_title:
    st.markdown("### 💻 CS Problem-Solving Tutor")
    st.caption("Think it through — I won't write it for you, but I'll help you get there.")
with col_copy:
    transcript = build_transcript()
    st.download_button(
        label="⬇ Transcript",
        data=transcript,
        file_name="cs_tutor_session.txt",
        mime="text/plain",
        help="Download the full conversation as a text file",
        use_container_width=True,
    )
with col_reset:
    if st.button("↺ Reset", help="Start a new conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.divider()

# ── Opening message ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    opening = "Hi! I'm your CS tutor. I won't write code for you — but I'll work through problems with you step by step.\n\nWhat are you working on today — would you like help answering a question, trace some code or debug some code, or would you just like me to help explain an area of Python?"
    st.session_state.messages.append({"role": "assistant", "content": opening})

# ── Render conversation ────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    role = msg["role"]

    if msg.get("type") == "code":
        # Submitted code block — read only display
        with st.chat_message("user"):
            st.markdown('<div class="editor-label">Code submitted:</div>', unsafe_allow_html=True)
            st.code(msg["content"], language="python")

    elif msg.get("type") == "pending_editor":
        # Active (unsubmitted) editor — only the last one is ever active
        with st.chat_message("assistant"):
            st.markdown(strip_token(msg["content"]))
        st.markdown('<div class="editor-label">Write your code below:</div>', unsafe_allow_html=True)
        editor_key = f"editor_{i}"
        code_input = st_ace(
            placeholder="# Write your Python here...",
            language="python",
            theme="tomorrow",
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=False,
            auto_update=True,
            height=250,
            key=editor_key,
        )
        if st.button("▶ Submit code", key=f"submit_{i}", type="primary"):
            if code_input and code_input.strip():
                # Mark this message as no longer pending
                st.session_state.messages[i]["type"] = "editor_done"
                # Add the submitted code as a user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": code_input,
                    "type": "code"
                })
                # Get tutor response
                api_messages = []
                for m in st.session_state.messages:
                    if m.get("type") == "code":
                        api_messages.append({
                            "role": "user",
                            "content": f"Here is my code:\n\n```python\n{m['content']}\n```"
                        })
                    elif m.get("type") not in ("pending_editor",):
                        api_messages.append({
                            "role": m["role"],
                            "content": strip_token(m["content"])
                        })
                reply = call_api(api_messages)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "type": "pending_editor" if wants_editor(reply) else "text"
                })
                st.rerun()
            else:
                st.warning("Editor is empty — write some code first.")

    elif msg.get("type") == "editor_done":
        # Tutor message whose editor has been submitted — show text only
        with st.chat_message("assistant"):
            st.markdown(strip_token(msg["content"]))

    else:
        # Normal text message
        with st.chat_message(role):
            st.markdown(strip_token(msg["content"]))

# ── Chat input (only show if last message is not a pending editor) ─────────────
last = st.session_state.messages[-1] if st.session_state.messages else None
if last and last.get("type") != "pending_editor":
    if prompt := st.chat_input("Type your answer or question here…"):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "type": "text"
        })
        # Build API message list
        api_messages = []
        for m in st.session_state.messages:
            if m.get("type") == "code":
                api_messages.append({
                    "role": "user",
                    "content": f"Here is my code:\n\n```python\n{m['content']}\n```"
                })
            elif m.get("type") not in ("pending_editor",):
                api_messages.append({
                    "role": m["role"],
                    "content": strip_token(m["content"])
                })
        reply = call_api(api_messages)
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "type": "pending_editor" if wants_editor(reply) else "text"
        })
        st.rerun()
