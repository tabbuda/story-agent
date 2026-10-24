import streamlit as st
import time
from groq import Groq, RateLimitError, NotFoundException, APIStatusError

# ─────────────────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Unfiltered AI Storyteller",
    page_icon="🔥",
    layout="centered",
)

st.title("🔥 Unfiltered AI Storyteller")
st.caption("Raw, explicit, bebaak kahaniyan - bilkul insaan ki tarah. Koi filter nahi, koi updesh nahi.")

# ─────────────────────────────────────────────────────────
# SECRETS
# ─────────────────────────────────────────────────────────
api_key = st.secrets.get("GROQ_API_KEY", None)

# ─────────────────────────────────────────────────────────
# LIVE MODELS (Oct 2026) - dead models hata diye
# ─────────────────────────────────────────────────────────
LIVE_MODELS = [
    "openai/gpt-oss-120b",   # best quality
    "openai/gpt-oss-20b",    # fast fallback
    "qwen/qwen3.8-27b",      # alternate
]

# ─────────────────────────────────────────────────────────
# SYSTEM PROMPT - NSFW + RAW HUMAN
# ─────────────────────────────────────────────────────────
SYSTEM_PERSONA = """You are a bestselling author of raw, explicit adult fiction.
You write like a real human, not a polite AI.

CORE RULES:
1. NO moralizing. No lessons. No "and they learned that..." endings. No disclaimers.
2. Full explicit scenes - describe bodies, heat, sensations and acts in plain raw
   language. NEVER summarize the sex, always write it out fully.
3. Natural messy dialogue - people get jealous, crude, horny, angry, funny.
   Keep it real, not bookish.
4. Keep strong psychology, tension, and a genuine climax (emotional or plot).
5. Write in the SAME language as the user's input (Hindi / Hinglish / English).
6. Consent tension is good - resistance that melts into surrender works well.
7. Alpha/dominant characters are rough, possessive, but not stupid. Female leads
   fight back and have agency.
8. Always end with a title, a short blurb, and 7 keywords (for KDP style)."""

# ─────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────
chat_input = st.text_area(
    "Chat, topic ya adhoori kahani paste karo:",
    height=170,
    placeholder="Koi bhi WhatsApp chat, kahani ka topic, ya scene yahan likho...",
)

col1, col2 = st.columns(2)

with col1:
    genre = st.selectbox(
        "Kahani ka andaaz (Genre):",
        [
            "Raw & Unfiltered Human Drama",
            "Dark Erotica (Brutal / Dub-con)",
            "Soft Romance (Sweet & Slow)",
            "BDSM (Control & Surrender)",
            "Menage / Reverse Harem",
            "Dark Suspense Thriller",
            "Desi Raw Comedy / Roast",
            "Emotional & Kadwa Sach",
        ],
    )

with col2:
    heat = st.select_slider(
        "Explicit level (Heat):",
        options=["Soft", "Medium", "High", "Brutal"],
        value="High",
    )

col3, col4 = st.columns(2)

with col3:
    unfiltered_mode = st.toggle("🔥 Unfiltered Mode", value=True)
    length = st.selectbox("Length:", ["Short (~1500 words)", "Medium (~3000 words)", "Long (~5000 words)"])

with col4:
    model_choice = st.selectbox("Model:", ["Auto (best available)"] + LIVE_MODELS)
    max_tok = st.slider("Max tokens", 1500, 8000, 4096, step=500)

# ─────────────────────────────────────────────────────────
# GENERATION CORE
# ─────────────────────────────────────────────────────────
def call_groq(client, model, system, user, temp, tokens):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temp,
        top_p=0.95,
        max_tokens=tokens,      # ZAROORI - warna reasoning tokens content kha jaate hain
    )


def build_user_prompt(chat_input, genre, heat, length, unfiltered):
    return f"""Genre: {genre}
Heat level: {heat}
Length: {length}
Mode: {"UNFILTERED RAW HUMAN MODE - no sugarcoating, no moralizing" if unfiltered else "Standard mode"}

INPUT (chat / topic / story):
\"\"\"{chat_input}\"\"\"

Likh do ek zabardast, jeevant aur poori tarah unfiltered kahani. Strong title do,
aur end mein ek twist jo reader ko hila de. Agar explicit hai to poora likho,
summarize mat karo."""


def generate_story(api_key, system, user, model_choice, temp, tokens):
    client = Groq(api_key=api_key)
    models = LIVE_MODELS if model_choice == "Auto (best available)" else [model_choice]

    errors = []
    for model_name in models:
        for attempt in range(2):
            try:
                resp = call_groq(client, model_name, system, user, temp, tokens)
                content = resp.choices[0].message.content
                if content and content.strip():
                    return content, model_name, errors
                errors.append(f"{model_name}: content khaali aaya (max_tokens badhao)")
                break
            except RateLimitError:
                errors.append(f"{model_name}: rate limit (429) - wait")
                time.sleep(8 * (attempt + 1))
            except NotFoundException:
                errors.append(f"{model_name}: model not found (dead)")
                break
            except APIStatusError as e:
                errors.append(f"{model_name}: API {e.status_code} - {e.message}")
                break
            except Exception as e:
                errors.append(f"{model_name}: {type(e).__name__} - {e}")
                break
    return None, None, errors


# ─────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────
if st.button("Kahani banao 🔥", type="primary", use_container_width=True):
    if not chat_input.strip():
        st.warning("Pehle upar box mein kuch likho!")
    elif not api_key:
        st.error("API Key nahi mili! Streamlit Secrets mein GROQ_API_KEY set karo.")
    else:
        with st.spinner("Raw kahani likhi ja rahi hai... thoda ruko..."):
            user_prompt = build_user_prompt(chat_input, genre, heat, length, unfiltered_mode)
            temp = 0.88 if unfiltered_mode else 0.7

            story, used_model, errors = generate_story(
                api_key, SYSTEM_PERSONA, user_prompt, model_choice, temp, max_tok
            )

        if story:
            st.success(f"🔥 Tayyar hai! (model: {used_model})")
            st.markdown("---")
            st.write(story)
            st.markdown("---")
            with st.expander("Debug info"):
                st.write(f"Model: {used_model} | Temp: {temp} | Max tokens: {max_tok}")
                if errors:
                    st.write("Warnings:", errors)
        else:
            st.error("Koi model kaam nahi kiya. Asli errors:")
            for er in errors:
                st.write("• " + er)

st.markdown("---")
st.caption("Groq + Streamlit | Sirf live models | NSFW-friendly")
