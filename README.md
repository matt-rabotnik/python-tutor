# CS Problem-Solving Tutor

A dialogic AI tutor for GCSE Computer Science students. The AI never writes code for students — it asks questions to help them construct solutions themselves.

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Anthropic API key to `.streamlit/secrets.toml` (see the template file).

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository (public or private).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app** → select your repo → set main file to `app.py`.
4. Under **Advanced settings → Secrets**, paste:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy**. You'll get a public URL to share with students.

## Notes

- Each student session is independent — conversation resets on page refresh or with the Reset button.
- The system prompt is server-side and not visible to students.
- No student accounts or logins required.
- Anthropic API costs are very low for this use case (typically well under £1 per class session).
