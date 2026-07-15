import streamlit as st
from openai import OpenAI
import re

# Page config
st.set_page_config(page_title="Email Workspace", layout="wide")

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
        
        /* Header structure spacing adjustments */
        h1 {
            font-size: max(2vw, 18px) !important;
            margin-top: 10px !important; 
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

# Initialize Session State values for views and outputs
if "current_view" not in st.session_state:
    st.session_state.current_view = "Polisher"
if "generated_email" not in st.session_state:
    st.session_state.generated_email = ""
if "read_summary" not in st.session_state:
    st.session_state.read_summary = ""

# Setup API Key access
if "OPENROUTER_API_KEY" in st.secrets:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
else:
    OPENROUTER_API_KEY = "sk-or-v1-YOUR_LOCAL_KEY_HERE"

# ----------------- TOP MAIN HEADER ROW -----------------
head_col1, head_col2 = st.columns([5, 3])

with head_col1:
    # Changes dynamically based on selected mode
    if st.session_state.current_view == "Polisher":
        st.title("Email Polisher")
    else:
        st.title("Email Reader")

with head_col2:
    # Domain Legit / Scam Checker input window
    domain_input = st.text_input("Verify Domain Risk (e.g., bcc.uk):", placeholder="example.com", label_visibility="visible")
    
    if domain_input:
        domain_clean = domain_input.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
        domain_pattern = re.compile(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
        scam_flags = ["xyz", "top", "work", "click", "tempemail", "sharklasers", "mailinator", "guerrillamail"]
        
        if not domain_pattern.match(domain_clean):
            st.caption("⚠️ Invalid format pattern.")
        elif any(flag in domain_clean for flag in scam_flags):
            st.caption("🚨 **Status:** High Risk / Known Scam Variant")
        else:
            st.caption("✅ **Status:** Domain format looks structural / Standard Legit profile")

# ----------------- NAVIGATION BUTTONS ROW (LOWERED) -----------------
nav_col1, nav_col2, nav_col3 = st.columns([2, 2, 4])
with nav_col1:
    if st.button("Email Polisher Mode", use_container_width=True, type="primary" if st.session_state.current_view == "Polisher" else "secondary"):
        st.session_state.current_view = "Polisher"
        st.rerun()
with nav_col2:
    if st.button("Email Reader Mode", use_container_width=True, type="primary" if st.session_state.current_view == "Reader" else "secondary"):
        st.session_state.current_view = "Reader"
        st.rerun()

st.markdown("---")

# ----------------- VIEW 1: EMAIL POLISHER MODE -----------------
if st.session_state.current_view == "Polisher":
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
        st.subheader("Raw Content Input")
        user_input = st.text_area(
            "Input Box Polisher",
            placeholder="Type rough points here...",
            label_visibility="collapsed"
        )
        submit_button = st.button("Generate Email", type="primary", use_container_width=True)

    with col2:
        st.subheader("Polished Output")
        
        if submit_button and user_input:
            with st.spinner("Polishing..."):
                try:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
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

        st.text_area("Output Box Polisher", value=st.session_state.generated_email, label_visibility="collapsed")
        
        st.html(f"""
            <div style="width: 100%; margin: 0; padding: 0;">
                <button onclick="navigator.clipboard.writeText(parent.document.querySelector('textarea[aria-label=\"Output Box Polisher\"]').value)" 
                        class="responsive-copy-btn">
                    Copy All Text
                </button>
            </div>
        """)

# ----------------- VIEW 2: EMAIL READER MODE -----------------
elif st.session_state.current_view == "Reader":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Long Email Input")
        email_to_read = st.text_area(
            "Input Box Reader",
            placeholder="Paste the long structural email you received here...",
            label_visibility="collapsed"
        )
        read_button = st.button("Extract Clear Instructions", type="primary", use_container_width=True)

    with col2:
        st.subheader("Actionable Summary (Point Form)")
        
        if read_button and email_to_read:
            with st.spinner("Analyzing email architecture..."):
                try:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
                    reader_instruction = (
                        "You are an efficient executive operations assistant. Your job is to parse long, wordy corporate emails "
                        "and strip them down into immediate, actionable intelligence for the receiver. "
                        "Format the output strictly in clean point-form blocks with the following headers:\n"
                        "- **CORE PURPOSE**: (1 line summary of why this email matters)\n"
                        "- **KEY INSTRUCTIONS**: (Clear point-form breakdown of what the email is instructing the reader to do/know)\n"
                        "- **ACTION ITEMS & DEADLINES**: (Explicit assignments and target dates if mentioned, otherwise state 'None specified')\n"
                        "Do not include conversational filler, meta-text, or polite opening/closing commentary."
                    )
                    response = client.chat.completions.create(
                        model="deepseek/deepseek-chat", 
                        messages=[
                            {"role": "system", "content": reader_instruction},
                            {"role": "user", "content": email_to_read}
                        ]
                    )
                    st.session_state.read_summary = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error: {e}")

        st.text_area("Output Box Reader", value=st.session_state.read_summary, label_visibility="collapsed")
        
        st.html(f"""
            <div style="width: 100%; margin: 0; padding: 0;">
                <button onclick="navigator.clipboard.writeText(parent.document.querySelector('textarea[aria-label=\"Output Box Reader\"]').value)" 
                        class="responsive-copy-btn">
                    Copy Action Items
                </button>
            </div>
        """)
