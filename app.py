import re
import urllib.parse
import urllib.request
import json
import streamlit as st
from groq import Groq

st.set_page_config(page_title="YouTube + Web Search Story Agent", page_icon="🎬", layout="centered")

st.title("🎬 YouTube + Google/Web Search Original Story Agent")
st.write("किसी भी YouTube वीडियो का लिंक डालें — यह एजेंट वीडियो को समझेगा, इंटरनेट पर नया असली डेटा (Original Facts) खोजेगा और एक 100% नई कहानी लिखेगा!")

api_key = st.secrets.get("GROQ_API_KEY")

def extract_video_id(url: str):
    match = re.search(r'(?:v=|youtu.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_youtube_info(video_id: str):
    title = "YouTube Video"
    author = "YouTube Creator"
    description = ""
    transcript_text = ""

    # 1. Fetch Title & Channel via YouTube oEmbed
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            title = data.get("title", title)
            author = data.get("author_name", author)
    except Exception:
        pass

    # 2. Fetch Video Description from YouTube Page
    try:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        req = urllib.request.Request(watch_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            desc_match = re.search(r'"shortDescription":"((?:\.|[^"\])*)"', html)
            if desc_match:
                description = desc_match.group(1).replace("\n", " ")[:2000]
    except Exception:
        pass

    # 3. Try fetching full subtitles if youtube-transcript-api is installed
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        try:
            ytt_api = YouTubeTranscriptApi()
            t_list = ytt_api.fetch(video_id, languages=['hi', 'en', 'en-IN'])
            transcript_text = " ".join([s.text for s in t_list])[:5000]
        except Exception:
            raw_t = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
            transcript_text = " ".join([item["text"] for item in raw_t])[:5000]
    except Exception:
        pass

    combined_context = transcript_text if transcript_text else description
    return title, author, combined_context

def search_web_facts(query: str):
    results_text = []
    # Method 1: Try duckduckgo-search if installed
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results_text.append(f"- {r.get('title')}: {r.get('body')}")
        if results_text:
            return "\n".join(results_text)
    except Exception:
        pass

    # Method 2: Built-in Wikipedia / Web API search (Zero extra packages needed)
    try:
        encoded_q = urllib.parse.quote(query)
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_q}&utf8=&format=json"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "StoryAgent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            wdata = json.loads(resp.read().decode("utf-8", errors="ignore"))
            for item in wdata.get("query", {}).get("search", [])[:4]:
                clean_snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                results_text.append(f"- {item.get('title')}: {clean_snippet}")
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

if st.button("वीडियो देखें + वेब सर्च करें + नई कहानी बनाएँ", type="primary"):
    if not yt_url.strip():
        st.warning("कृपया पहले YouTube वीडियो का लिंक डालें!")
    elif not api_key:
        st.error("API Key नहीं मिली! कृपया Streamlit Secrets में GROQ_API_KEY सेट करें।")
    else:
        vid_id = extract_video_id(yt_url)
        if not vid_id:
            st.error("कृपया सही YouTube लिंक डालें!")
        else:
            with st.spinner("स्टेप 1/3: YouTube वीडियो और उसका विवरण पढ़ा जा रहा है..."):
                v_title, v_author, v_context = get_youtube_info(vid_id)
                st.info(f"📺 **वीडियो मिला:** {v_title} ({v_author})")

            with st.spinner("स्टेप 2/3: इंटरनेट से इस विषय पर नया असली डेटा (Original Facts) खोजा जा रहा है..."):
                web_facts = search_web_facts(v_title)

            with st.spinner("स्टेप 3/3: असली डेटा के आधार पर नई ओरिजिनल कहानी लिखी जा रही है..."):
                try:
                    client = Groq(api_key=api_key)
                    prompt = f"""तुम एक बेहतरीन इन्वेस्टिगेटिव लेखक और कहानीकार हो।
नीचे एक YouTube वीडियो की जानकारी और इंटरनेट सर्च से निकाले गए असली तथ्य दिए गए हैं:

YouTube Video Title: {v_title} (by {v_author})
Video Details / Transcript:
{v_context if v_context else "वीडियो के शीर्षक और विषय का उपयोग करें।"}

Internet Search Original Data:
{web_facts if web_facts else "इस विषय से जुड़े प्रमाणिक ऐतिहासिक और वैज्ञानिक तथ्यों का उपयोग करें।"}

चुनी गई शैली: {genre}
विशेष निर्देश: {custom_angle}

अब तीन भागों में सरल और रोचक हिंदी में उत्तर दें:
1. **📺 वीडियो का सार (Video Summary):** वीडियो किस बारे में है (2-3 लाइन)।
2. **🔍 खोजे गए असली तथ्य (Original Data & Facts):** इस विषय से जुड़े 4-5 मुख्य सच्चे और रोचक तथ्य।
3. **📖 नई ओरिजिनल कहानी (Original Story):** वीडियो की नकल करने के बजाय इन असली तथ्यों के आधार पर एक बिल्कुल नई, रोचक और सिनेमाई हिंदी कहानी लिखें।"""

                    preferred_models = [
                        "meta-llama/llama-4-scout-17b-16e-instruct",
                        "llama-3.1-8b-instant",
                        "openai/gpt-oss-120b",
                        "openai/gpt-oss-20b"
                    ]
                    story_output = None
                    last_err = None

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
                        except Exception as err:
                            last_err = err
                            continue

                    if story_output:
                        st.success("🎉 नई ओरिजिनल कहानी तैयार है! 👇")
                        st.markdown(story_output)
                    else:
                        st.error(f"कहानी जनरेट करने में समस्या आई: {last_err}")
                except Exception as e:
                    st.error(f"एरर आया: {e}")
