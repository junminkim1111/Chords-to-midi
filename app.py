import streamlit as st
import os
from agent import MusicToMidiAgent
import traceback

st.set_page_config(page_title="CHORDS2MIDI", page_icon="🎸", layout="centered")

with st.sidebar:
    st.header("🔑 API settings")
    
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="",
        placeholder="AIzasRb..."
    )
    
    st.markdown("---")
    st.markdown("[👉 Get API Key](https://aistudio.google.com/app/apikey)")

st.title("CHORDS 2 MIDI")
st.markdown("---")

st.subheader("1️⃣ Link")
url_input = st.text_input(
    "put in the Ultimate Guitar tab link:", 
    placeholder="https://tabs.ultimate-guitar.com/tab/..."
)

is_valid_url = False

if url_input:
    if "ultimate-guitar.com" in url_input and "/tab/" in url_input:
        st.success("✅ Valid URL.")
        is_valid_url = True
    else:
        st.warning("⚠️ Invalid URL. Please enter a valid Ultimate Guitar tab link.")

if is_valid_url:
    st.markdown("---")
    st.subheader("2️⃣ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_bpm = st.number_input(
            "BPM", 
            min_value=0, max_value=300, value=0, 
            help="0 = AI auto detects BPM"
        )
        if user_bpm == 0:
            st.caption("🤖 AI auto detects BPM")
        else:
            st.caption(f"⚡{user_bpm} BPM")


    with col2:
        
        custom_name = st.text_input(
            "file name (optional):",
            placeholder=f"{url_input.split('/')[-1].split('-chords-')[0] if '-chords-' in url_input else 'Unknown'}",
            help="if left blank, the AI will use the detected song title."
        )
        st.caption("💾 .mid extension is automatically added.")

    st.write("") 
    start_btn = st.button("🎵 CONVERT!", type="primary", use_container_width=True)

    if start_btn:
        try:
            agent = MusicToMidiAgent(url_input, api_key_input)
        except ValueError:
            st.error("❌ API Key ERROR!  please check your .env file.")
            st.stop()

        status = st.status("start converting...", expanded=True)
        
        try:
            status.write(f"Fetching Data from...{url_input}")
            raw_text = agent.fetch_tab()
            
            if not raw_text:
                status.update(label="Failed to fetch tab data", state="error")
                st.error("failed to fetch tab data from the provided URL.")
                st.stop()


            status.write("Analyzing with Gemini ...")
            song_data = agent.analyze(raw_text)
            
            if not song_data:
                status.update(label="failed to analyze", state="error")
                st.stop()
            
            detected_title = song_data.get('title', 'Unknown')
            status.write(f"Success! Saved as {detected_title}.mid")
            status.write("Generating MIDI file...")
            bpm_to_use = user_bpm if user_bpm > 0 else None

            if custom_name and custom_name.strip() == "":
                custom_name = url_input.split('/')[-1].split('-chords-')[0] if '-chords-' in url_input else 'Unknown'
            output_filename = agent.compose(song_data, user_bpm=bpm_to_use, custom_filename=custom_name)
            
            status.update(label="Success!", state="complete", expanded=False)
            
            st.success(f"Successfully generated: {output_filename}")
            
            with open(output_filename, "rb") as f:
                st.download_button(
                    label="💾 DOWNLOAD",
                    data=f,
                    file_name=output_filename,
                    mime="audio/midi",
                    use_container_width=True
                )
                
        except Exception as e:  
            status.update(label="Error occurred", state="error")

            err_msg = traceback.format_exc()
            
            print("------------ ERROR LOG ------------")
            print(err_msg)
            print("--------------------------------------")