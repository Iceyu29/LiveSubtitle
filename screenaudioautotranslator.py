import asyncio
import time
import audioop
import keyboard
import speech_recognition as sr
from googletrans import Translator
from tkinter import Tk, Label, Canvas
import threading

print(r"""  ____                              _             _ _     _____                    _       _             
 / ___|  ___ _ __ ___  ___ _ __    / \  _   _  __| (_) __|_   _| __ __ _ _ __  ___| | __ _| |_ ___  _ __ 
 \___ \ / __| '__/ _ \/ _ \ '_ \  / _ \| | | |/ _` | |/ _ \| || '__/ _` | '_ \/ __| |/ _` | __/ _ \| '__|
  ___) | (__| | |  __/  __/ | | |/ ___ \ |_| | (_| | | (_) | || | | (_| | | | \__ \ | (_| | || (_) | |   
 |____/ \___|_|  \___|\___|_| |_/_/   \_\__,_|\__,_|_|\___/|_||_|  \__,_|_| |_|___/_|\__,_|\__\___/|_|   """)
print("-----------------------------------")
print("-Copyright of Iceyu29, 2025       -")
print("-https:/https://github.com/Iceyu29-")
print("-----------------------------------\n")
time.sleep(1)
print("This program uses the 'Stereo Mix' device to capture your system audio.")
print("Ensure it is enabled in your system's sound settings and set to max volume.\n")
time.sleep(1)

mic_names = sr.Microphone.list_microphone_names()
stereo_mix_index = next((index for index, name in enumerate(mic_names) if "stereo mix" in name.lower()), None)

if stereo_mix_index is None:
    print("Stereo Mix device not found. Please ensure it is enabled and try again.\n")
    print("Closing in 10 seconds...")
    time.sleep(10)
    exit()

recognizer = sr.Recognizer()

try:
    mic = sr.Microphone(device_index=stereo_mix_index)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
except AttributeError as e:
    if "NoneType" in str(e):
        print("Stereo Mix appears to be disabled. Enable it in your system's sound settings and try again.\n")
        print("Closing in 10 seconds...")
        time.sleep(10)
        exit()
    else:
        raise

print(f"Using device '{mic_names[stereo_mix_index]}' (index {stereo_mix_index}).\n")

def listen_until_break(source, break_key='.', silence_threshold=300, silence_duration=0.3):
    frames = []
    chunk = getattr(source, "CHUNK", 1024)
    sample_rate = getattr(source, "SAMPLE_RATE", 16000)
    sample_width = getattr(source, "SAMPLE_WIDTH", 2)
    silence_start_time = None
    voice_detected = False
    while True:
        try:
            data = source.stream.read(chunk)
        except Exception as e:
            print("Error reading audio data:", e)
            break
        frames.append(data)
        if keyboard.is_pressed(break_key):
            print(f"Break key '{break_key}' pressed.")
            time.sleep(0.05)
            break
        rms_value = audioop.rms(data, sample_width)
        if rms_value >= silence_threshold:
            voice_detected = True
            silence_start_time = None
        else:
            if voice_detected:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time >= silence_duration:
                    break
    audio_chunk = b"".join(frames)
    return sr.AudioData(audio_chunk, sample_rate, sample_width), voice_detected

time.sleep(2)

print(
    "Language codes list:\n"
    "-------------------------------------------------------------------------\n"
    "| Code | Language       | Code | Language       | Code | Language       |\n"
    "-------------------------------------------------------------------------\n"
    "| en   | English        | ja   | Japanese       | ko   | Korean         |\n"
    "| zh-CN| Chinese        | fr   | French         | de   | German         |\n"
    "| es   | Spanish        | it   | Italian        | ru   | Russian        |\n"
    "| pt   | Portuguese     | vi   | Vietnamese     | th   | Thai           |\n"
    "| id   | Indonesian     | ms   | Malay          | ar   | Arabic         |\n"
    "| hi   | Hindi          | bn   | Bengali        | ur   | Urdu           |\n"
    "| fa   | Persian        | tr   | Turkish        | nl   | Dutch          |\n"
    "| pl   | Polish         | sv   | Swedish        | no   | Norwegian      |\n"
    "| da   | Danish         | fi   | Finnish        | cs   | Czech          |\n"
    "| hu   | Hungarian      | el   | Greek          | he   | Hebrew         |\n"
    "| ro   | Romanian       | sk   | Slovak         | sl   | Slovenian      |\n"
    "| bg   | Bulgarian      | uk   | Ukrainian      | hr   | Croatian       |\n"
    "| sr   | Serbian        | ca   | Catalan        | eu   | Basque         |\n"
    "| gl   | Galician       | et   | Estonian       | lv   | Latvian        |\n"
    "| lt   | Lithuanian     | tl   | Filipino       | km   | Khmer          |\n"
    "| my   | Burmese        | ne   | Nepali         | si   | Sinhala        |\n"
    "| am   | Amharic        | sw   | Swahili        | so   | Somali         |\n"
    "| ha   | Hausa          | ig   | Igbo           | yo   | Yoruba         |\n"
    "-------------------------------------------------------------------------"
)
valid_lang_codes = {
    "en", "ja", "ko", "zh-CN", "fr", "de", "es", "it", "ru", "pt", "vi", "th", "id", "ms", "ar", "hi", "bn", "ur",
    "fa", "tr", "nl", "pl", "sv", "no", "da", "fi", "cs", "hu", "el", "he", "ro", "sk", "sl", "bg", "uk", "hr", "sr",
    "ca", "eu", "gl", "et", "lv", "lt", "tl", "km", "my", "ne", "si", "am", "sw", "so", "ha", "ig", "yo"
}
print("------------------------------")

def get_valid_input(prompt, valid_options):
    while (user_input := input(prompt).strip()) not in valid_options:
        print("Invalid input. Please try again.\n")
    return user_input

source_lang = get_valid_input("Enter the source language code: ", valid_lang_codes)
target_lang = get_valid_input("Enter the target language code: ", valid_lang_codes)
display_option_input = input("Enter 'y' to display only translated text, or press Enter to display both recognized and translated text: ").strip()
display_option = '1' if display_option_input.lower() == 'y' else '2'
disable_tkinter_input = input("Enter 'y' to disable the subtitle window, or press Enter to keep it enabled: ").strip()
disable_tkinter = disable_tkinter_input.lower() == 'y'

font_size = 14
src_lang_for_trans = source_lang.split("-")[0].lower()
translator = Translator()

print("------------------------------")

def create_translation_window(font_size=14):
    window = Tk()
    window.title("Translation")
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.attributes("-alpha", 0.7)
    window.configure(bg='black')
    window.minsize(500, 50)
    label = Label(window, text="", font=("Arial", font_size), wraplength=1480, fg='white', bg='black')
    label.pack(expand=True, fill='both')

    resize_button = Canvas(window, width=15, height=15, bg='black', highlightthickness=0, cursor='size_nw_se')
    resize_button.place(relx=1.0, rely=1.0, anchor='se')
    resize_button.create_polygon(0, 15, 15, 0, 15, 15, fill='grey')

    def start_resize(event):
        window.x = event.x_root
        window.y = event.y_root

    def do_resize(event):
        new_width = window.winfo_width() + (event.x_root - window.x)
        new_height = window.winfo_height() + (event.y_root - window.y)
        window.geometry(f"{new_width}x{new_height}")
        window.x = event.x_root
        window.y = event.y_root

    resize_button.bind("<Button-1>", start_resize)
    resize_button.bind("<B1-Motion>", do_resize)

    def start_move(event):
        window.x = event.x
        window.y = event.y

    def do_move(event):
        x = window.winfo_pointerx() - window.x
        y = window.winfo_pointery() - window.y
        window.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)

    return window, label

def update_translation(label, recognized_text, translation, display_option, source_lang, target_lang):
    if display_option == '1':
        print("------------------------------")
        print(f"{target_lang}: {translation.text}")
        print("------------------------------\n")
        if not disable_tkinter:
            label.config(text=f"{target_lang}: {translation.text}")
    else:
        print("------------------------------")
        print(f"{source_lang}: {recognized_text}\n")
        print(f"{target_lang}: {translation.text}")
        print("------------------------------\n")
        if not disable_tkinter:
            label.config(text=f"{source_lang}: {recognized_text}\n{target_lang}: {translation.text}")
    if not disable_tkinter:
        label.update_idletasks()
        label.update()

async def main_loop(label):
    with sr.Microphone(device_index=stereo_mix_index) as source:
        print("------------------------------")
        print("Calibrating for speech recognition...")
        recognizer.adjust_for_ambient_noise(source)
        print("Calibration complete. Press '.' to break sentence.")
        print("------------------------------\n")
        while True:
            audio_data, voice_detected = listen_until_break(source)
            if not voice_detected:
                print("------------------------------")
                print("No voice detected.")
                print("------------------------------\n")
                continue
            try:
                recognized_text = recognizer.recognize_google(audio_data, language=source_lang)
                translation = await translator.translate(
                    recognized_text,
                    src=src_lang_for_trans,
                    dest=target_lang
                )
                update_translation(label, recognized_text, translation, display_option, source_lang, target_lang)
            except sr.UnknownValueError:
                print("Could not understand audio.\n")
            except sr.RequestError as req_err:
                print(f"Could not request results; {req_err}\n")

def run_main(font_size):
    if disable_tkinter:
        asyncio.run(main_loop(None))
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        window, label = create_translation_window(font_size)
        threading.Thread(target=loop.run_until_complete, args=(main_loop(label),), daemon=True).start()
        window.mainloop()
        
if __name__ == "__main__":
    keyboard.add_hotkey('.', lambda: None)
    run_main(font_size)