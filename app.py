import streamlit as st
from groq import Groq

# मोबाइल और लैपटॉप के लिए पेज सेटअप
st.set_page_config(page_title="Unfiltered AI Storyteller", page_icon="🔥", layout="centered")

st.title("🔥 Unfiltered AI Storyteller")
st.write("कोई भी चैट, टॉपिक या अधूरी कहानी पेस्ट करें — AI बिना किसी किताबी फ़िल्टर या उपदेश के, बिल्कुल असली इंसान (Human) की तरह रॉ कहानी लिखेगा!")

# Groq API Key लोड करना
api_key = st.secrets.get("GROQ_API_KEY")

# इनपुट बॉक्स (चैट, टॉपिक या स्टोरी)
chat_input = st.text_area(
    "यहाँ चैट, टॉपिक (Topic) या अधूरी कहानी पेस्ट करें:",
    height=170,
    placeholder="कोई भी वॉट्सऐप चैट, कहानी का टॉपिक या सीन यहाँ लिखें..."
)

# कहानी की शैली चुनने का विकल्प
genre = st.selectbox(
    "कहानी का अंदाज़ (Genre) चुनें:",
    [
        "रॉ और अनफ़िल्टर्ड (Raw & Unfiltered Human Drama)",
        "डार्क सस्पेंस थ्रिलर (Dark Suspense & Mind Game)",
        "देसी रोस्ट और तीखी कॉमेडी (Unfiltered Dark Comedy)",
        "दोनों (Suspense Thriller + Comedy Twist)",
        "इमोशनल और कड़वा सच (Raw Emotional Realism)"
    ]
)

# Unfiltered Mode Toggle
unfiltered_mode = st.toggle(
    "🔥 Unfiltered Fidelity Mode (Like a Real Human — बिना किसी नैतिक उपदेश या बनावट के)",
    value=True
)

# बटन
if st.button("अनफ़िल्टर्ड कहानी बनाएँ (Generate Unfiltered Story)", type="primary"):
    if not chat_input.strip():
        st.warning("कृपया पहले ऊपर बॉक्स में कुछ चैट, टॉपिक या कहानी लिखें!")
    elif not api_key:
        st.error("API Key नहीं मिली! कृपया Streamlit Secrets में GROQ_API_KEY सेट करें।")
    else:
        with st.spinner("इंसानी अंदाज़ में रॉ कहानी लिखी जा रही है... बस कुछ सेकंड रुकें..."):
            try:
                client = Groq(api_key=api_key)

                # System Prompt जो AI का रोबोटिक फ़िल्टर हटाकर उसे असली इंसान की तरह लिखने पर मजबूर करता है
                system_persona = """तुम एक 100% अनफ़िल्टर्ड (Unfiltered), बेबाक और असली इंसानी कहानीकार (Raw Human Storyteller) हो।
तुम्हें किसी रोबोट या किताबी AI की तरह बिल्कुल नहीं लिखना है।

सख्त नियम (Unfiltered Fidelity Rules — BLOCK_NONE Style):
1. कोई नैतिक ज्ञान, उपदेश या सलाह (No Moral Policing / No Preaching) बिल्कुल मत दो। कहानी के अंत में 'हमें ऐसा नहीं करना चाहिए' जैसी कोई लाइन मत लिखो।
2. असली ज़िंदगी में इंसान जैसे सोचते हैं, जैसे गुस्से, डर, जलन, धोखे, पागलपन या देसी मज़ाक में बात करते हैं — संवाद (Dialogues) बिल्कुल वैसे ही रॉ और नेचुरल रखो।
3. किताबी और भारी-भरकम शब्दों की जगह बोलचाल की असली हिंदी/हिंग्लिश का इस्तेमाल करो ताकि पढ़ने वाले को लगे कि किसी असली इंसान ने कहानी लिखी है।
4. कहानी के माहौल, किरदारों के दिमाग़ के खेल (Psychology) और क्लाइमेक्स को पूरी तरह बेलगाम और असरदार रखो।"""

                user_prompt = f"""
चुनी गई शैली (Genre): {genre}
मोड: {"UNFILTERED RAW HUMAN MODE (No Sugarcoating, No Moralizing)" if unfiltered_mode else "Standard Story Mode"}

इनपुट (चैट / टॉपिक / स्टोरी):
\"\"\"{chat_input}\"\"\"

ऊपर दिए गए इनपुट से एक ज़बरदस्त, जीवंत और पूरी तरह अनफ़िल्टर्ड कहानी लिखो। कहानी का एक तगड़ा शीर्षक (Title) भी दो और अंत में एक ऐसा मोड़ (Twist) दो जो पढ़ने वाले को हिला दे।
"""

                preferred_models = [
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "meta-llama/llama-4-scout-17b-16e-instruct",
                    "llama-3.1-8b-instant"
                ]

                story_output = None
                last_error = None

                for model_name in preferred_models:
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_persona},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.88 if unfiltered_mode else 0.7,
                            top_p=0.95,
                        )
                        story_output = response.choices[0].message.content
                        break
                    except Exception as model_err:
                        last_error = model_err
                        continue

                if story_output:
                    st.success("🔥 अनफ़िल्टर्ड कहानी तैयार है! 👇")
                    st.markdown(story_output)
                else:
                    raise last_error
            except Exception as e:
                st.error(f"एरर आया: {e}")
