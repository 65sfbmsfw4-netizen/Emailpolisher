import streamlit as st
from openai import OpenAI

# Page config
st.set_page_config(page_title="Email Polisher", layout="wide")

# CSS to lock the layout height and force everything onto a single, non-scrolling screen
st.markdown("""
    <style>
        /* Locks the entire app body to the window view and hides trailing scroll overflow */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
        }
        
        /* Maximize tight usable area spacing */
        #root > div:nth-child(1) > div > div > div > div > section > div {
            padding-top: 0.5rem !important;
            padding-left: 2% !important;
            padding-right: 2% !important;
            padding-bottom: 0px !important;
        }
        
        /* Header margin */
        h1 {
            font-size: max(2vw, 18px) !important;
            margin-top: 25px !important; 
            margin-bottom: 0px !important; 
            padding-bottom: 0px !important;
        }

        /* Tightens the selection toggle block spacing */
        div[data-testid="stRadio"] {
            margin-top: 0px !important;
            padding-top: 0px !important;
            margin-bottom: 5px !important; 
        }
        div[data-testid="stRadio"] label {
            margin-bottom: 2px !important;
        }

        /* Tightens the space above and below subheaders */
        h3 {
            font-size: max(1.4vw, 14px) !important;
            margin-top: 0px !important;
            margin-bottom: 2px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        
        /* Forces columns to behave evenly */
        div[data-testid="column"] {
            flex: 1 1 auto !important;
            width: 100% !important;
        }

        /* Responsive text fields: strictly capped height */
        textarea {
            height: 40vh !important; 
            min-height: 200px !important; 
            font-size: max(1vw, 12px) !important; 
        }

        /* Wipes out native bottom margin spaces injected by Streamlit components */
        div[data-testid="stElementContainer"] {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }

        /* Custom alignment layer to force the injected HTML row into the exact layout height line of native buttons */
        iframe {
            display: block;
            margin: 0 !important;
            padding: 0 !important;
            height: 38px !important;
        }

        /* Custom styling for the horizontal row button alignment */
        .responsive-copy-btn {
            width: 100%; 
            height: 38px; 
            background-color: transparent; 
            border: 1px solid #4A5568; 
            color: inherit; 
            border-radius: 4px; 
            font-weight: 500; 
            cursor: pointer;
            font-size: max(0.9vw, 12px); 
            transition: background-color 0.2s;
            box-sizing: border-box;
        }
        .responsive-copy-btn:hover {
            background-color: rgba(128, 128, 128, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.title("Email Polisher")

# BACKEND SECRET INJECTION: Looks inside Streamlit Cloud's hidden vault for the key safely
if "OPENROUTER_API_KEY" in st.secrets:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
else:
    # Fallback option if running locally
    OPENROUTER_API_KEY = "sk-or-v1-YOUR_LOCAL_KEY_HERE"

# Length Selection Toggle
email_length = st.radio(
    "Select Email Length Style:",
    ["Short & On-Point", "Traditional & Polished"],
    horizontal=True,
    index=0
)

if email_length == "Short & On-Point":
    length_instruction = (
        "The email must be brief, precise, and directly on point. Avoid unnecessary filler words, "
        "keep sentences short, and ensure the recipient can grasp the core message instantly."
    )
else:
    length_instruction = (
        "The email should be traditional, thorough, and highly polished. Use professional transitional "
        "phrases, elegant business courtesy, and a complete corporate structure."
    )

# Dual-window responsive columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    user_input = st.text_area(
        "Input Box",
        placeholder="",
        label_visibility="collapsed"
    )
    submit_button = st.button("Generate Email", type="primary", use_container_width=True)

with col2:
    st.subheader("Polished")
    
    if "generated_email" not in st.session_state:
        st.session_state.generated_email = ""
        
    if submit_button and user_input:
        with st.spinner("Processing..."):
            try:
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=OPENROUTER_API_KEY,
                )
                
                system_instruction = (
                    f"You are an expert corporate communications manager. "
                    f"Translate the user's rough notes or broken text into a flawless, professional business email. "
                    f"Provide a clear 'Subject:' line and the full email body. "
                    f"Do not include any conversational introduction or out-of-character comments. "
                    f"CRITICAL LENGTH RULE: {length_instruction}"
                )
                
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat", 
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_input}
                    ]
                )
                st.session_state.generated_email = response.choices[0].message.content
                
            except Exception as e:
                st.error(f"Error: {e}")

    # Output window
    st.text_area("Output Box", value=st.session_state.generated_email, label_visibility="collapsed")
    
    # Places the Copy button directly inline on the same horizon line as the Generate button
    st.html(f"""
        <div style="width: 100%; margin: 0; padding: 0;">
            <button onclick="navigator.clipboard.writeText(parent.document.querySelector('textarea[aria-label=\"Output Box\"]').value)" 
                    class="responsive-copy-btn">
                Copy All Text
            </button>
        </div>
    """)
