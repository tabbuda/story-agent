import re
import requests
import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from duckduckgo_search import DDGS

st.set_page_config(page_title="YouTube + Google Search Story Agent", page_icon="🎬", layout="centered")

st.title("🎬 YouTube + Web Search Original Story Agent")
st.write("किसी भी YouTube वीडियो का लिंक डालें — यह एजेंट वीडियो को समझेगा, इंटरनेट पर नया असली डेटा (Original Facts) खोजेगा और एक 100% नई कहानी लिखेगा!")

api_key = st.secrets.get("GROQ_API_KEY")

def extract_video_id(url: str):
    pattern = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts|live)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_info(video_id: str):
    title = "YouTube Video"
    author = "Creator"
    transcript_text = ""
    try:
        oembed = requests.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=8
        )
        if oembed.status_code == 200:
            data = oembed.json()
            title = data.get("title", title)
            author = data.get("author_name", author)
    except Exception:
        pass

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id, languages=['hi', 'en', 'en-IN'])
        transcript_text = " ".join([snippet.text for snippet in transcript_list])[:6000]
    except Exception:
        try:
            # Fallback for older youtube-transcript-api versions
            raw_t = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
            transcript_text = " ".join([item["text"] for item in raw_t])[:6000]
        except Exception:
            transcript_text = ""

    return title, author, transcript_text

def search_web_facts(query: str):
    results_text = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results_text.append(f"- {r.get('title')}: {r.get('body')} ({r.get('href')})")
    except Exception:
        pass
    return "\n".join(results_text)

yt_url = st.text_input(
    "🔗 यहाँ YouTube वीडियो का लिंक (URL) पेस्ट करें:",
    placeholder="https://www.youtube.com/watch?v=..."
)

custom_angle = st.text_input(
    "🎯 कोई खास एंगल या निर्देश (Optional):",
    placeholder="जैसे: इसके अनसुने रहस्य और असली तारीखों पर ज़्यादा फोकस करें..."
)

genre = st.selectbox(
    "कहानी का अंदाज़ चुनें:",
    [
        "डॉक्यूमेंट्री थ्रिलर और सच्ची घटना (Real-Data Thriller Story)",
        "रहस्य और इन्वेस्टिगेटिव थ्रिलर (Mystery & Investigation)",
        "सिनेमाई यूट्यूब स्क्रिप्ट स्टोरी (Cinematic YouTube Story Script)",
        "रोचक और मज़ेदार अंदाज़ (Engaging Infotainment Story)"
    ]
)

if st.button("वीडियो देखें + Google सर्च करें + नई कहानी बनाएँ", type="primary"):
    if not yt_url.strip():
        st.warning("कृपया पहले YouTube वीडियो का लिंक डालें!")
    elif not api_key:
        st.error("API Key नहीं मिली! कृपया Streamlit Secrets में GROQ_API_KEY सेट करें।")
    else:
        vid_id = extract_video_id(yt_url)
        if not vid_id:
            st.error("कृपया सही YouTube लिंक डालें!")
        else:
            with st.spinner("स्टेप 1/3: YouTube वीडियो और ट्रांसक्रिप्ट पढ़ा जा रहा है..."):
                v_title, v_author, v_transcript = get_youtube_info(vid_id)
                st.info(f"📺 **वीडियो मिला:** {v_title} ({v_author})")

            with st.spinner("स्टेप 2/3: इंटरनेट से इस विषय पर नया असली डेटा (Original Facts) खोजा जा रहा है..."):
                search_query = f"{v_title} real facts history latest details"
                web_facts = search_web_facts(search_query)

            with st.spinner("स्टेप 3/3: असली डेटा के आधार पर नई ओरिजिनल कहानी लिखी जा रही है..."):
                try:
                    client = Groq(api_key=api_key)
                    prompt = f"""
तुम एक बेहतरीन इन्वेस्टिगेटिव लेखक और कहानीकार हो।
नीचे एक YouTube वीडियो की जानकारी और इंटरनेट सर्च से निकाले गए असली तथ्य (Real Web Facts) दिए गए हैं:

YouTube Video Title: {v_title} (by {v_author})
Video Transcript / Content:
{v_transcript if v_transcript else "ट्रांसक्रिप्ट उपलब्ध नहीं है, वीडियो के शीर्षक और वेब सर्च डेटा का उपयोग करें।"}

Internet Search Original Data:
{web_facts if web_facts else "अपने ज्ञान और विषय के प्रमाणिक तथ्यों का उपयोग करें।"}

चुनी गई शैली: {genre}
विशेष निर्देश: {custom_angle}

अब तीन भागों में हिंदी में उत्तर दें:
1. **📺 वीडियो का सार (Video Summary):** वीडियो किस बारे में है (2-3 लाइन)।
2. **🔍 इंटरनेट खोज से मिले असली तथ्य (Original Data & Facts):** 4-5 मुख्य सच्चे तथ्य।
3. **📖 नई ओरिजिनल कहानी (Original Story):** वीडियो की नकल करने के बजाय इन असली तथ्यों के आधार पर एक बिल्कुल नई, रोचक और सिनेमाई हिंदी कहानी लिखें।
"""
                    preferred_models = [
                        "meta-llama/llama-4-scout-17b-16e-instruct",
                        "openai/gpt-oss-120b",
                        "llama-3.1-8b-instant"
                    ]
                    story_output = None
                    for m in preferred_models:
                        try:
                            resp = client.chat.completions.create(
                                model=m,
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.75,
                            )
                            story_output = resp.choices[0].message.content
                            if story_output:
                                break
                        except Exception:
                            continue

                    if story_output:
                        st.success("🎉 नई ओरिजिनल कहानी तैयार है! 👇")
                        st.markdown(story_output)
                    else:
                        st.error("कहानी जनरेट करने में समस्या आई।")
                except Exception as e:
                    st.error(f"एरर आया: {e}")
