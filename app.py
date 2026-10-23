import streamlit as st
from groq import Groq

# मोबाइल और लैपटॉप के लिए पेज सेटअप
st.set_page_config(page_title="AI Story Agent", page_icon="📖", layout="centered")

st.title("📖 AI Storyteller Agent")
st.write("अपनी कोई भी चैट या टेक्स्ट यहाँ डालें, AI उससे बेहतरीन कहानियाँ बनाएगा!")

# Groq API Key लोड करना
api_key = st.secrets.get("GROQ_API_KEY")

# इनपुट बॉक्स
chat_input = st.text_area(
    "यहाँ चैट या कहानी का आइडिया पेस्ट करें:",
    height=160,
    placeholder="राहुल: सुनो, मुझे लगता है कि कोई हमारा पीछा कर रहा है...\nप्रिया: क्या बकवास कर रहे हो? कैफे में हैं हम..."
)

# कहानी की शैली चुनने का विकल्प
genre = st.selectbox(
    "कहानी का अंदाज़ चुनें:",
    [
        "दोनों (Suspense Thriller + Comedy Twist)",
        "सिर्फ Suspense Thriller",
        "सिर्फ Comedy / Funny Twist",
        "Emotional Drama"
    ]
)

# बटन
if st.button("कहानी तैयार करें (Generate Story)", type="primary"):
    if not chat_input.strip():
        st.warning("कृपया पहले ऊपर बॉक्स में कुछ चैट या टेक्स्ट लिखें!")
    elif not api_key:
        st.error("API Key नहीं मिली! कृपया Streamlit Secrets में GROQ_API_KEY सेट करें।")
    else:
        with st.spinner("एजेंट कहानी सोचकर लिख रहा है... बस कुछ सेकंड रुकें..."):
            try:
                client = Groq(api_key=api_key)
                
                prompt = f"""
                तुम एक बेहतरीन कहानीकार (Storyteller) हो।
                तुम्हें नीचे दी गई चैट/टेक्स्ट को गहराई से समझना है, उसके किरदारों की भावनाएं पहचाननी हैं और एक बहुत ही रोचक और जीवंत कहानी लिखनी है।
                
                चुनी गई शैली (Genre): {genre}
                
                इनपुट चैट / टेक्स्ट:
                \"\"\"{chat_input}\"\"\"
                
                निर्देश:
                1. कहानी सरल, स्पष्ट और रोचक हिंदी में लिखें।
                2. बैकग्राउंड का माहौल (मौसम, जगह, चेहरे के भाव) बहुत अच्छे से जोड़ें।
                3. कहानी पढ़ते वक्त ऐसा लगना चाहिए जैसे कोई फ़िल्म चल रही हो।
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                
                story_output = response.choices[0].message.content
                st.success("कहानी तैयार है! 👇")
                st.markdown(story_output)
            except Exception as e:
                st.error(f"एरर आया: {e}")
