import gradio as gr
import re, unidecode
from unidecode import unidecode
import yt_dlp
import os
import pydub
import numpy as np

# no space, punctuation, accent in lower string
def cleanString(string):
    cleanString = unidecode(string)
    cleanString = re.sub('\W+','_', cleanString)
    return cleanString.lower()

def read_audio(f, normalized=False):
    """MP3 to numpy array"""
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y

def download_audio(url):
    path_to_folder_audio_mp3 = "./audio/"
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': f'{path_to_folder_audio_mp3}%(title)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict['title']

        # Rename the audio file
        local_link = video_title + ".mp3"
        new_local_link = cleanString(video_title) + ".mp3"
        for filename in os.listdir(path_to_folder_audio_mp3):
            if cleanString(local_link) == cleanString(filename):
                os.rename(os.path.join(path_to_folder_audio_mp3, filename),os.path.join(path_to_folder_audio_mp3, new_local_link)) 

        file_path = path_to_folder_audio_mp3 + new_local_link

    return file_path, read_audio(file_path)

# Gradio interface
iface = gr.Interface(fn=download_audio, 
                     inputs=gr.Textbox(label="YouTube Video URL"),
                     outputs=[
                         gr.File(label="Output Audio File"),
                         gr.Audio(label="Play Audio", show_download_button=False, format="mp3"),
                     ],
                     allow_flagging="never"
                     )
iface.launch(debug=True)
