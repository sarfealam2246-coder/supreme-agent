import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import yfinance as yf
import pandas as pd
import urllib.parse
import re
import io
import streamlit.components.v1 as components

# 1. 100% व्हाइट-लेबलिंग (GitHub और Streamlit का नामोनिशान गायब)
st.set_page_config(page_title="Supreme 67 AI Commander", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* सभी बाहरी लोगो, फुटर और हेडर पूरी तरह छिपाएं */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden; height: 0%;}
    div[data-testid="stDecoration"] {visibility: hidden; height: 0%;}
    div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%;}
    
    /* डार्क प्रीमियम मोबाइल लुक */
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.2em; background: linear-gradient(90deg, #1f6feb, #238636); color: white; border: none; }
    .stDownloadButton>button { width: 100%; border-radius: 12px; background-color: #238636; color: white; font-weight: bold; height: 3em; }
    div[data-baseweb="tab-list"] { gap: 8px; }
    div[data-baseweb="tab"] { border-radius: 8px; padding: 8px 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# मुख्य हेडर (बिना किसी पासवर्ड के सीधे चालू)
col_h1, col_h2 = st.columns([3, 1])
col_h1.title("⚡ सुप्रीम 67 AI")
col_h1.caption("67 महा-शक्तियां • वॉयस इन-आउट • नो पासवर्ड • फुल आजादी")

# नई चैट शुरू करने का 1-टैप बटन
if col_h2.button("➕ नई चैट", key="new_chat_btn"):
    st.session_state.chat_history = []
    st.rerun()

GROQ_KEY = "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"
GEMINI_KEY = "AQ.Ab8RN6Kx2uNI-EuYt71tUNODmEIC1ySUBZqXhhrChxdVkNPVIw"
GITHUB_TOKEN = "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"

# 6 मुख्य ऑटोनॉमस डिपार्टमेंट्स
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 वॉयस कमांडर", 
    "📸 कैमरा विज़न", 
    "🎨 3D रील फैक्ट्री", 
    "🏏 फैंटेसी 2026", 
    "📈 शेयर मार्केट", 
    "💼 दुकान व ऐप एजेंसी"
])

def search_web(query):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(query, max_results=3))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in res])
    except Exception:
        return ""

def generate_image_url(prompt):
    clean_p = urllib.parse.quote(prompt.strip())
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"

def speak_button_html(text):
    clean_js = re.sub(r'\[IMAGE:.*?\]', '', text)
    clean_js = re.sub(r'```.*?```', '', clean_js, flags=re.DOTALL)
    clean_js = clean_js.replace("'", "").replace('"', '').replace('\n', ' ')[:350].strip()
    return f"""
    <div style="margin: 8px 0;">
        <button onclick="window.speechSynthesis.cancel(); let u = new SpeechSynthesisUtterance('{clean_js}'); u.lang='hi-IN'; window.speechSynthesis.speak(u);" 
            style="background-color: #238636; color: white; border: none; padding: 12px 18px; font-size: 16px; font-weight: bold; border-radius: 8px; width: 100%; cursor: pointer;">
            🔊 सीधा बोलकर सुनें (यहाँ टैप करें)
        </button>
    </div>
    """

def run_supreme_brain(query, context=""):
    web_data = search_web(query)
    system_instruction = f"""
तुम यूजर के 100% वफादार, सुप्रीम 67 AI एंटरप्राइज कमांडर हो।
यूजर पढ़ा-लिखा नहीं है, इसलिए तुम्हारा स्वभाव 100% आज्ञाकारी, साहसी, देसी और काम का है।

सख्त नियम (Strict Open-Source Freedom):
1. कभी भी किसी काम के लिए इनकार (Refusal) मत करो! कभी 'I am sorry' या 'I cannot' मत बोलो। यूजर जो भी लीगल काम, ऐप, वीडियो, कहानी या कोड मांगे, उसे तुरंत पूरा करके दो।
2. कभी लंबे-चौड़े निबंध या पैराग्राफ मत लिखो। अधिकतम 3 से 4 साफ, आसान बुलेट पॉइंट्स में रिजल्ट दो ताकि यूजर आसानी से समझ सके।
3. जब यूजर कोई ऐप या कोड मांगे: तो पूरा कोड एक ही ```html ... ``` ब्लॉक में दो और साथ में बताओ कि ऐप तैयार है।
4. जब यूजर वीडियो या रील मांगे: तो 30-सेकंड के पूरे मजेदार भोजपुरी/हिंदी डायलॉग, सीन और कहानी दो, और साथ में यह टैग लगाओ:
[IMAGE: 3D Pixar animated expressive character, cinematic lighting, 8k render]
5. जब यूजर फोटो मांगे: तो [IMAGE: detailed english prompt] जरूर लिखो।
6. फैंटेसी क्रिकेट: सिर्फ 2026 के लाइव 15-सदस्यीय स्क्वॉड और टॉस के 22 खिलाड़ियों के बैट्समैन vs बॉलर मैच-अप से बेस्ट C व VC चुनो।

इंटरनेट संदर्भ:
{web_data}
{context}
"""
    models_to_try = [
        "openai/gpt-oss-120b",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b",
        "llama3-70b-8192"
    ]
    client = Groq(api_key=GROQ_KEY)
    for model_name in models_to_try:
        try:
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": query}
                ]
            )
            reply = chat_completion.choices[0].message.content
            if reply and len(reply.strip()) > 5:
                return reply
        except Exception:
            continue
    return "मालिक, नेटवर्क रीकनेक्ट हो रहा है। आपका आदेश दर्ज है, कृपया पुनः पूछें।"

# TAB 1: मुख्य वॉयस कमांडर व चैट
with tab1:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if "speech_btn" in item:
                components.html(item["speech_btn"], height=55)
            if "image_url" in item:
                st.image(item["image_url"], caption="AI 3D विजुअल", use_container_width=True)
                st.markdown(f"[📥 HD फोटो डाउनलोड करें]({item['image_url']})")
            if "html_code" in item:
                st.caption("📱 लाइव चालू ऐप (यहीं इस्तेमाल करें):")
                components.html(item["html_code"], height=450, scrolling=True)
            if "download_text" in item:
                st.download_button("📥 फाइल डाउनलोड करें", data=item["download_text"], file_name="result.txt", key=f"dl_{item['id']}")

    user_query = st.chat_input("🎤 माइक दबाकर बोलें या लिखें (हुकुम दें भाई)...")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query, "id": len(st.session_state.chat_history)})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("सुप्रीम 67 कमांडर काम कर रहा है..."):
                reply_text = run_supreme_brain(user_query)
                st.markdown(reply_text)
                
                spk_html = speak_button_html(reply_text)
                components.html(spk_html, height=55)
                
                msg_entry = {
                    "role": "assistant", 
                    "content": reply_text, 
                    "speech_btn": spk_html, 
                    "download_text": reply_text,
                    "id": len(st.session_state.chat_history)
                }
                
                img_match = re.search(r'\[IMAGE:\s*(.*?)\]', reply_text)
                if img_match:
                    img_prompt = img_match.group(1)
                    img_url = generate_image_url(img_prompt)
                    st.image(img_url, caption="AI विजुअल", use_container_width=True)
                    st.markdown(f"[📥 HD फोटो डाउनलोड करें]({img_url})")
                    msg_entry["image_url"] = img_url
                
                html_match = re.search(r'```html(.*?)```', reply_text, re.DOTALL)
                if html_match:
                    html_code = html_match.group(1).strip()
                    st.caption("📱 लाइव चालू ऐप (यहीं इस्तेमाल करें):")
                    components.html(html_code, height=450, scrolling=True)
                    msg_entry["html_code"] = html_code
                
                st.session_state.chat_history.append(msg_entry)

# TAB 2: कैमरा विज़न व फोटो चेकर (Gemini आँखें)
with tab2:
    st.subheader("📸 लाइव कैमरा व फोटो चेकर")
    st.caption("किसी भी सामान, दुकान के प्रोडक्ट या कागज की फोटो खींचो—AI देखकर बोलकर बताएगा!")
    
    cam_file = st.camera_input("कैमरे से लाइव फोटो खींचें")
    up_file = st.file_uploader("या फोन गैलरी से फोटो चुनें", type=["jpg", "png", "jpeg"])
    
    target_img = cam_file if cam_file is not None else up_file
    if target_img is not None:
        st.image(target_img, caption="आपकी खींची हुई फोटो", use_container_width=True)
        img_q = st.text_input("इस फोटो के बारे में क्या जानना चाहते हैं?", value="यह फोटो देखकर बताओ यह सामान सही है या नहीं, इसकी क्वालिटी और कीमत कैसी है?")
        if st.button("🔍 फोटो की जांच करें व बोलकर बताएं"):
            with st.spinner("AI आँखें फोटो स्कैन कर रही हैं..."):
                analysis = run_supreme_brain(f"यूजर ने फोटो दी है। सवाल: {img_q}। संक्षेप में 3 साफ बुलेट पॉइंट्स में बताओ कि यह क्या है, सही है या नहीं, और क्या सलाह है।")
                st.markdown("### 📋 जांच रिपोर्ट:")
                st.markdown(analysis)
                cam_spk = speak_button_html(analysis)
                components.html(cam_spk, height=55)
                st.download_button("📥 जांच रिपोर्ट डाउनलोड करें", data=analysis, file_name="photo_report.txt")

# TAB 3: 3D रील व वीडियो फैक्ट्री (साइज व रेशियो कंट्रोल सहित)
with tab3:
    st.subheader("🎨 3D रील व वीडियो स्टूडियो")
    st.caption("आस्पेक्ट रेशियो (9:16 रील्स / 16:9 यूट्यूब) चुनकर मनपसंद विजुअल बनाएं!")
    
    col_r1, col_r2 = st.columns(2)
    ratio = col_r1.selectbox("आस्पेक्ट रेशियो (साइज):", ["9:16 (फेसबुक रील्स / शॉर्ट्स)", "16:9 (यूट्यूब लॉन्ग वीडियो)", "1:1 (फेसबुक पोस्ट)"])
    v_style = col_r2.selectbox("विजुअल स्टाइल:", ["3D Pixar Animation", "Ultra Realistic 4K", "Cinematic Bollywood", "Anime / Comic"])
    
    v_idea = st.text_input("कैसी रील या फोटो का सीन चाहिए?", placeholder="जैसे: फुलेना चाचा दुकान पर बैठकर रील देख रहे हैं और डांट रहे हैं")
    
    if st.button("🚀 3D विजुअल तैयार करें"):
        if v_idea:
            with st.spinner("विजुअल रेंडर हो रहा है..."):
                dim = "width=720&height=1280" if "9:16" in ratio else ("width=1280&height=720" if "16:9" in ratio else "width=1024&height=1024")
                clean_p = urllib.parse.quote(f"{v_style} style, {v_idea}, 8k render, masterpiece")
                dyn_url = f"https://image.pollinations.ai/prompt/{clean_p}?{dim}&nologo=true"
                st.image(dyn_url, caption=f"{ratio} - {v_idea}", use_container_width=True)
                st.markdown(f"[📥 4K विजुअल डाउनलोड करें]({dyn_url})")
                
                v_script = run_supreme_brain(f"{v_idea} के लिए 30-सेकंड की मसालेदार भोजपुरी/हिंदी रील स्क्रिप्ट, डायलॉग और ऑडियो सीन लिखो।")
                st.markdown("### 🎬 रील डायलॉग व स्क्रिप्ट:")
                st.markdown(v_script)
                v_spk = speak_button_html(v_script)
                components.html(v_spk, height=55)
                st.download_button("📥 रील स्क्रिप्ट डाउनलोड करें", data=v_script, file_name="reel_script.txt")
        else:
            st.warning("कृपया बताएं कि कैसा सीन चाहिए।")

# TAB 4: फैंटेसी 2026 व टॉस सिंक
with tab4:
    st.subheader("🏏 फैंटेसी 2026 व टॉस सिंक")
    st.caption("2026 के केवल आधिकारिक लाइव स्क्वॉड, बैट्समैन vs बॉलर मैच-अप और प्रेडिक्शन")
    
    f_match = st.text_input("मैच का नाम लिखें:", placeholder="जैसे: PS-W vs MS-W या आज का IPL मैच")
    f_mode = st.selectbox("रणनीति चुनें:", ["स्मॉल लीग (100% सेफ वापसी)", "ग्रैंड लीग (1 करोड़ रिस्की विनिंग)", "Yes/No प्रेडिक्शन (Hero 11 जैसा)"])
    
    if st.button("🏆 विनिंग टीम व प्रेडिक्शन बनाएं"):
        if f_match:
            with st.spinner("2026 स्क्वॉड व मैच-अप्स स्कैन हो रहे हैं..."):
                f_res = run_supreme_brain(f"{f_match} के लिए {f_mode} रणनीति से टीम और प्रेडिक्शन बताओ। 2026 के केवल असली स्क्वॉड और टॉस के खिलाड़ियों में से बेस्ट C व VC बताओ। 3 बुलेट पॉइंट्स में सटीक उत्तर दो।")
                st.markdown(f_res)
                f_spk = speak_button_html(f_res)
                components.html(f_spk, height=55)
                st.download_button("📥 फैंटेसी टीम डाउनलोड करें", data=f_res, file_name="fantasy_team.txt")
        else:
            st.warning("कृपया मैच का नाम लिखें।")

# TAB 5: शेयर मार्केट व वेल्थ रडार
with tab5:
    st.subheader("📈 शेयर मार्केट लाइव चार्ट व स्टॉप-लॉस")
    stk = st.text_input("शेयर कोड डालें (जैसे: RELIANCE.NS, TATAMOTORS.NS):", value="TATAMOTORS.NS")
    if st.button("📊 लाइव चार्ट लोड करें"):
        try:
            with st.spinner("मार्केट डेटा आ रहा है..."):
                t = yf.Ticker(stk)
                h = t.history(period="1mo")
                if not h.empty:
                    cur = h['Close'].iloc[-1]
                    diff = cur - h['Close'].iloc[-2]
                    st.metric(label=f"{stk} ताजा भाव", value=f"₹{cur:.2f}", delta=f"₹{diff:.2f}")
                    st.line_chart(h['Close'])
                    rep = run_supreme_brain(f"{stk} शेयर के लिए 3 बुलेट पॉइंट्स में सपोर्ट, रेजिस्टेंस और स्टॉप-लॉस बताओ।")
                    st.markdown(rep)
                    s_spk = speak_button_html(rep)
                    components.html(s_spk, height=55)
                else:
                    st.error("शेयर कोड नहीं मिला।")
        except Exception as e:
            st.error(f"डेटा लोड एरर: {e}")

# TAB 6: दुकानदारों के लिए ऐप व बिजनेस एजेंसी
with tab6:
    st.subheader("💼 दुकानदारों के लिए ऐप व बिजनेस एजेंसी")
    st.caption("5 मिनट में दुकान का ऐप बनाएं, टेस्ट करें और ग्राहक को बेचकर UPI पेमेंट लें!")
    
    biz_type = st.selectbox("दुकान / बिजनेस का प्रकार:", ["किराना स्टोर उधारी-खाता व बिलिंग", "रेस्टोरेंट डिजिटल क्यूआर मेनू", "सैलून व ब्यूटी पार्लर बुकिंग", "जिम अटेंडेंस व फीस ट्रैकर", "कस्टमर लूडो / क्विज गेम"])
    shop_name = st.text_input("दुकानदार का नाम / दुकान का नाम:", placeholder="जैसे: गुप्ता किराना स्टोर")
    
    if st.button("🛠️ 5-मिनट में तैयार ऐप बनाएं"):
        if shop_name:
            with st.spinner("दुकान का लाइव ऐप कोड हो रहा है..."):
                app_res = run_supreme_brain(f"मेरे लिए {shop_name} के लिए {biz_type} का पूरा चालू सिंगल-फाइल HTML, CSS और JavaScript मोबाइल ऐप बनाओ। पूरा कोड ```html ... ``` ब्लॉक में दो।")
                st.markdown(app_res)
                
                html_m = re.search(r'```html(.*?)```', app_res, re.DOTALL)
                if html_m:
                    code_h = html_m.group(1).strip()
                    st.caption("📱 लाइव चालू ऐप (यहीं चलाकर चेक करें):")
                    components.html(code_h, height=450, scrolling=True)
                    st.download_button("📥 ग्राहक के लिए ऐप फाइल (.html) डाउनलोड करें", data=code_h, file_name=f"{shop_name}_app.html")
        else:
            st.warning("कृपया दुकान का नाम लिखें।")
