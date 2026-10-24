import re
import urllib.parse
import urllib.request
import json
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Urdu-Touch Hindi Blog Generator", page_icon="✒️", layout="centered")

st.title("✒️ YouTube to Urdu-Touch Blog Post Agent")
st.write("लिखावट देवनागरी (हिंदी) में, लेकिन लफ़्ज़, उच्चारण और कशिश ख़ूबसूरत उर्दू टच (Hindustani/Rekhta) में — ताकि पढ़ने वाला आख़िरी सतर तक बंधा रहे!")

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
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results_text.append(f"- {r.get('title')}: {r.get('body')}")
        if results_text:
            return "\n".join(results_text)
    except Exception:
        pass

    try:
        encoded_q = urllib.parse.quote(query)
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_q}&utf8=&format=json"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "BlogAgent/1.0"})
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
    "🎯 ब्लॉग पोस्ट का ख़ास पहलू या निर्देश (Optional):",
    placeholder="जैसे: इसके छुपे हुए राज़ और जज़्बाती पहलू पर ज़्यादा ज़ोर दें..."
)

blog_style = st.selectbox(
    "ब्लॉग का अंदाज़ (Style) चुनें:",
    [
        "दास्तानगोई और पुरकशिश ब्लॉग पोस्ट (Magnetic Urdu-Touch Blog Post)",
        "तहक़ीक़ात और राज़नामा ब्लॉग (Investigative Mystery Blog Post)",
        "जज़्बाती और रूहानी अफ़साना ब्लॉग (Soulful & Deep Feature Post)",
        "तेज़-तर्रार वायरल ब्लॉग पोस्ट (High-Retention Viral Reader Post)"
    ]
)

if st.button("✒️ उर्दू-टच हिंदी ब्लॉग पोस्ट तैयार करें", type="primary"):
    if not yt_url.strip():
        st.warning("कृपया पहले YouTube वीडियो का लिंक डालें!")
    elif not api_key:
        st.error("API Key नहीं मिली! कृपया Streamlit Secrets में GROQ_API_KEY सेट करें।")
    else:
        vid_id = extract_video_id(yt_url)
        if not vid_id:
            st.error("कृपया सही YouTube लिंक डालें!")
        else:
            with st.spinner("स्टेप 1/3: YouTube वीडियो के मौज़ू (Topic) को समझा जा रहा है..."):
                v_title, v_author, v_context = get_youtube_info(vid_id)
                st.info(f"📺 **वीडियो मिला:** {v_title} ({v_author})")

            with st.spinner("स्टेप 2/3: इंटरनेट से इस मौज़ू पर असली हक़ीक़त और सबूत खोजे जा रहे हैं..."):
                web_facts = search_web_facts(v_title)

            with st.spinner("स्टेप 3/3: उर्दू लफ़्ज़ों की चाशनी और देवनागरी लिखावट में ब्लॉग पोस्ट लिखा जा रहा है..."):
                try:
                    client = Groq(api_key=api_key)

                    system_persona = """तुम एक मशहूर अदीब, दास्तानगो और बेहद कामयाब ब्लॉग राइटर हो।
तुम्हें ऐसा Blog Post लिखना है जिसकी **लिखावट (Script) तो देवनागरी (हिंदी अक्षरों में) हो**, लेकिन **उच्चारण (Pronunciation), अल्फ़ाज़ और लहजा ख़ूबसूरत उर्दू टच (Hindustani / Rekhta Touch)** वाला हो।

सख़्त भाषाई नियम:
1. कठिन या किताबी संस्कृतनिष्ठ हिंदी शब्दों का इस्तेमाल बिल्कुल मत करो!
   - 'प्रारंभ' की जगह -> 'आग़ाज़' या 'शुरुआत'
   - 'रहस्य' की जगह -> 'राज़' या 'तिलिस्म'
   - 'वास्तविकता/सत्य' की जगह -> 'हक़ीक़त'
   - 'आश्चर्यजनक' की जगह -> 'हैरतअंगेज़'
   - 'दृश्य' की जगह -> 'मंज़र'
   - 'समय/प्रतीक्षा' की जगह -> 'वक़्त / इंतज़ार'
   - 'भावनाएं' की जगह -> 'जज़्बात / एहसास'
   - 'निष्कर्ष' की जगह -> 'अंजाम / लबो-लुबाब'
   - 'महत्वपूर्ण' की जगह -> 'अहम / ग़ौरतलब'
2. उर्दू शब्दों में सही जगह नुक़्ता (क़, ख़, ग़, ज़, फ़) ज़रूर लगाओ ताकि पढ़ने वाले का उच्चारण (Pronounce) अपने आप उर्दू टच वाला निकले।
3. ब्लॉग की शुरुआत ऐसी जादुई लाइन (Hook) से करो कि पाठक पूरा पोस्ट पढ़े बिना पेज बंद न कर सके।"""

                    user_prompt = f"""YouTube Video Title: {v_title} (by {v_author})
Video Details / Context:
{v_context if v_context else "वीडियो के शीर्षक और मौज़ू का उपयोग करें।"}

Internet Search Original Data:
{web_facts if web_facts else "इस मौज़ू से जुड़े असली ऐतिहासिक और सच्चे तथ्यों का उपयोग करें।"}

चुना गया ब्लॉग अंदाज़: {blog_style}
ख़ास निर्देश: {custom_angle}

अब देवनागरी लिपि में लेकिन **ख़ूबसूरत उर्दू टच और उच्चारण** के साथ एक मुकम्मल, वायरल **Blog Post** तैयार करें जिसमें ये हिस्से हों:
1. **🔥 सुर्ख़ी (Catchy Headline) और उप-शीर्षक (Sub-headline):** जिसे देखते ही लोग पढ़ने पर मजबूर हो जाएं।
2. **✨ आग़ाज़-ए-दास्तान (Magnetic Opening Hook):** जो पाठक के दिल और दिमाग़ को बांध ले।
3. **🔍 तहक़ीक़ात और असली हक़ीक़त (Original Facts & Evidence):** इंटरनेट से मिले 4-5 सच्चे और हैरतअंगेज़ पहलू।
4. **📖 मुकम्मल ब्लॉग पोस्ट (Main Blog Article with Subheadings):** 4-5 दिलकश पैराग्राफ और सब-हेडिंग्स में पूरी दास्तान।
5. **💬 अंजाम और आपका ख़याल (Closing Thought & Question for Readers):** अंत में पाठकों से कमेंट कराने के लिए एक गहरा सवाल।"""

                    preferred_models = [
                        "meta-llama/llama-4-scout-17b-16e-instruct",
                        "openai/gpt-oss-120b",
                        "llama-3.1-8b-instant",
                        "openai/gpt-oss-20b"
                    ]
                    blog_output = None
                    last_err = None

                    for m in preferred_models:
                        try:
                            resp = client.chat.completions.create(
                                model=m,
                                messages=[
                                    {"role": "system", "content": system_persona},
                                    {"role": "user", "content": user_prompt}
                                ],
                                temperature=0.82,
                                top_p=0.95,
                            )
                            blog_output = resp.choices[0].message.content
                            if blog_output:
                                break
                        except Exception as err:
                            last_err = err
                            continue

                    if blog_output:
                        st.success("✒️ आपका उर्दू-टच हिंदी ब्लॉग पोस्ट तैयार है! 👇")
                        st.markdown(blog_output)
                    else:
                        st.error(f"ब्लॉग पोस्ट बनाने में समस्या आई: {last_err}")
                except Exception as e:
                    st.error(f"एरर आया: {e}")
