import streamlit as st
import subprocess
import os
import shutil

st.set_page_config(page_title="AI Vocal & Speech Isolator", page_icon="🎙️")

# إخفاء عناصر وهوية Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🎙️ أداة عزل وتصفية الصوت البشري")
st.write("ارفع ملف صوتي أو فيديو لإزالة الموسيقى والحصول على الصوت والكلام فقط.")

# قبول ملفات الصوت والفيديو معاً
uploaded_file = st.file_uploader(
    "اختر ملف صوتي أو فيديو من جهازك", 
    type=["mp3", "wav", "m4a", "ogg", "flac", "mp4", "mov", "avi", "mkv", "webm"]
)

if uploaded_file is not None:
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    is_video = file_ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    
    # معاينة الملف قبل المعالجة
    if is_video:
        st.video(uploaded_file)
    else:
        st.audio(uploaded_file)
        
    if st.button("بدء إزالة الموسيقى 🚀", type="primary"):
        with st.spinner("جاري معالجة الملف وإزالة الموسيقى... يرجى الانتظار."):
            temp_input = f"input_{uploaded_file.name}"
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            output_dir = "separated_output"
            shutil.rmtree(output_dir, ignore_errors=True)
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                # إذا كان فيديو، نستخرج الصوت أولاً للمعالجة
                if is_video:
                    extracted_audio = "extracted_audio.wav"
                    subprocess.run([
                        "ffmpeg", "-y", "-i", temp_input, 
                        "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", 
                        extracted_audio
                    ], check=True)
                    audio_to_process = extracted_audio
                    folder_name = "extracted_audio"
                else:
                    audio_to_process = temp_input
                    track_name = os.path.splitext(uploaded_file.name)[0]
                    folder_name = f"input_{track_name}"

                # تشغيل نموذج الذكاء الاصطناعي لعزل الصوت
                cmd = [
                    "demucs",
                    "--two-stems", "vocals",
                    "-d", "cpu",
                    "-o", output_dir,
                    audio_to_process
                ]
                subprocess.run(cmd, check=True)
                
                vocals_wav = os.path.join(output_dir, "htdemucs", folder_name, "vocals.wav")
                
                if os.path.exists(vocals_wav):
                    st.success("تم عزل الصوت وإزالة الموسيقى بنجاح!")
                    
                    if is_video:
                        # دمج الفيديو الأصلي مع الصوت المعزول بدون إعادة تشفير الفيديو لسرعة العملية
                        final_video = "vocals_only_video.mp4"
                        subprocess.run([
                            "ffmpeg", "-y", "-i", temp_input, "-i", vocals_wav,
                            "-map", "0:v:0", "-map", "1:a:0",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                            "-shortest", final_video
                        ], check=True)
                        
                        st.subheader("🎬 الفيديو بعد إزالة الموسيقى:")
                        st.video(final_video)
                        with open(final_video, "rb") as f:
                            st.download_button(
                                "تحميل الفيديو بدون موسيقى (MP4)", 
                                f, 
                                file_name="vocals_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        # تحويل الصوت المستخرج إلى MP3 عالي الجودة
                        final_mp3 = "vocals_only.mp3"
                        subprocess.run([
                            "ffmpeg", "-y", "-i", vocals_wav,
                            "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                            final_mp3
                        ], check=True)
                        
                        st.subheader("🎤 الصوت والكلام فقط:")
                        st.audio(final_mp3)
                        with open(final_mp3, "rb") as f:
                            st.download_button(
                                "تحميل الصوت بدون موسيقى (MP3)", 
                                f, 
                                file_name="vocals.mp3",
                                mime="audio/mp3"
                            )
                else:
                    st.error("تعذر العثور على الملف المعزول.")
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
