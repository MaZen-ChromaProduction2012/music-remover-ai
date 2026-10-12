import streamlit as st
import subprocess
import os

st.set_page_config(page_title="AI Music Remover", page_icon="🎵")

st.title("🎵 أداة عزل الصوت والموسيقى")
st.write("ارفع الملف الصوتي وسيقوم الذكاء الاصطناعي بفصل الصوت عن الموسيقى.")

uploaded_file = st.file_uploader("اختر ملفاً صوتياً من جهازك", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("بدء عزل الصوت 🚀", type="primary"):
        with st.spinner("جاري عزل الصوت... يرجى الانتظار قليلاً."):
            temp_input = f"temp_{uploaded_file.name}"
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            output_dir = "separated_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # تشغيل Demucs
            cmd = [
                "demucs",
                "--two-stems", "vocals",
                "-d", "cpu",
                "-o", output_dir,
                temp_input
            ]
            
            try:
                subprocess.run(cmd, check=True)
                
                track_name = os.path.splitext(uploaded_file.name)[0]
                result_folder = os.path.join(output_dir, "htdemucs", f"temp_{track_name}")
                
                vocals_file = os.path.join(result_folder, "vocals.wav")
                no_vocals_file = os.path.join(result_folder, "no_vocals.wav")
                
                if os.path.exists(vocals_file) and os.path.exists(no_vocals_file):
                    st.success("تم العزل بنجاح!")
                    
                    st.subheader("🎤 الصوت البشري فقط")
                    st.audio(vocals_file)
                    with open(vocals_file, "rb") as f:
                        st.download_button("تحميل الصوت البشري (WAV)", f, file_name="vocals.wav")
                        
                    st.subheader("🎸 الموسيقى فقط")
                    st.audio(no_vocals_file)
                    with open(no_vocals_file, "rb") as f:
                        st.download_button("تحميل الموسيقى (WAV)", f, file_name="instrumental.wav")
                else:
                    st.error("لم نتمكن من العثور على الملفات الناتجة.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
