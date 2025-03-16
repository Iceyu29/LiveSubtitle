import asyncio
import time
import audioop
import keyboard
import speech_recognition as sr
from googletrans import Translator
from tkinter import Tk, Label, Canvas
import threading
import sys
import os

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

# Get the index of the 'Stereo Mix' device
mic_names = sr.Microphone.list_microphone_names()
stereo_mix_index = next((index for index, name in enumerate(mic_names) if "stereo mix" in name.lower()), None)

if stereo_mix_index is None:
    print("Stereo Mix device not found. Please ensure it is enabled and try again.\n")
    print("Closing in 10 seconds...")
    time.sleep(10)
    exit()

# Try to initialize the 'Stereo Mix' device
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

time.sleep(2)

print(
    "Language codes list:\n"
    "-------------------------------------------------------------------------\n"
    "| Code | Language       | Code | Language       | Code | Language       |\n"
    "-------------------------------------------------------------------------\n"
    "| en   | English        | ja   | Japanese       | ko   | Korean         |\n"
    "| cn   | Chinese        | fr   | French         | de   | German         |\n"
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
    "-------------------------------------------------------------------------\n"
)

# Translation settings
valid_lang_codes = {
    "en", "ja", "ko", "cn", "fr", "de", "es", "it", "ru", "pt", "vi", "th", "id", "ms", "ar", "hi", "bn", "ur",
    "fa", "tr", "nl", "pl", "sv", "no", "da", "fi", "cs", "hu", "el", "he", "ro", "sk", "sl", "bg", "uk", "hr", "sr",
    "ca", "eu", "gl", "et", "lv", "lt", "tl", "km", "my", "ne", "si", "am", "sw", "so", "ha", "ig", "yo"
}
print("------------------------------")

def select_language(prompt, valid_options):
    while (user_input := input(prompt).strip()) not in valid_options:
        print("Invalid input. Please try again.\n")
    return user_input

def enable_shortcuts(label, subtitle):
    global enable_shortcuts
    while (user_input := input("Do you want to enable keyboard shortcuts? (y/n): ").strip().lower()) not in {"y", "n"}:
        print("Invalid input. Please enter 'y' or 'n'.\n")
    enable_shortcuts = user_input == "y"
    print("------------------------------")
    if enable_shortcuts:
        keyboard.add_hotkey('p', lambda: toggle_pause(label))
        keyboard.add_hotkey('d', lambda: toggle_display_mode(label))
        keyboard.add_hotkey('l', lambda: return_to_language_selection(label))
        keyboard.add_hotkey('s', lambda: toggle_subtitle_visibility(subtitle))
        keyboard.add_hotkey('b', lambda: None)

source_lang = select_language("Enter the source language code: ", valid_lang_codes)
target_lang = select_language("Enter the target language code: ", valid_lang_codes)
font_size = 14
src_lang_for_trans = source_lang.split("-")[0].lower()
translator = Translator()

# Control pause and resume
paused = False

def toggle_pause(label):
    global paused
    paused = not paused
    if paused:
        print("------------------------------")
        print("Paused.")
        print("------------------------------\n")
        show_temp_message(label, "Paused.")
    else:
        print("------------------------------")
        print("Resumed.")
        print("------------------------------\n")
        show_temp_message(label, "Resumed.")

# Control subtitle visibility
subtitle_visible = True

def toggle_subtitle_visibility(subtitle):
    global subtitle_visible
    subtitle_visible = not subtitle_visible
    if subtitle_visible:
        subtitle.deiconify()
        print("------------------------------")
        print("Subtitle is visible.")
        print("------------------------------\n")
    else:
        subtitle.withdraw()
        print("------------------------------")
        print("Subtitle is hidden.")
        print("------------------------------\n")
        
# Control text display mode
display_both = True

def toggle_display_mode(label):
    global display_both
    display_both = not display_both
    if display_both:
        print("------------------------------")
        print("Displaying both recognized and translated text.")
        print("------------------------------\n")
        show_temp_message(label, "Displaying both recognized and translated text.")
    else:
        print("------------------------------")
        print("Displaying only translated text.")
        print("------------------------------\n")
        show_temp_message(label, "Displaying only translated text.")

# Listen to audio until a break key is pressed or silence is detected
def listen_until_break(source, label, break_key='b', silence_threshold=300, silence_duration=0.5):
    global paused
    frames = []
    chunk = getattr(source, "CHUNK", 1024)
    sample_rate = getattr(source, "SAMPLE_RATE", 16000)
    sample_width = getattr(source, "SAMPLE_WIDTH", 2)
    silence_start_time = None
    voice_detected = False
    while True:
        if paused:
            time.sleep(0.1)
            continue
        try:
            data = source.stream.read(chunk)
        except Exception as e:
            print("------------------------------")
            print("Error reading audio data:", e)
            print("------------------------------\n")
            break
        frames.append(data)
        # Check if the break key is pressed
        if enable_shortcuts and keyboard.is_pressed(break_key):
            print("------------------------------")
            print(f"Break key pressed.")
            print("------------------------------\n")
            show_temp_message(label, f"Break key pressed.")
            time.sleep(0.05)
            break
        rms_value = audioop.rms(data, sample_width)
        # Check if silence is detected
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

def show_temp_message(label, message, duration=0.5):
    original_text = label.cget("text")
    label.config(text=message)
    label.update_idletasks()
    label.update()
    time.sleep(duration)
    label.config(text=original_text)
    label.update_idletasks()
    label.update()

# Create a tkinter subtitle for displaying subtitles
def create_subtitle(font_size=14):
    subtitle = Tk()
    subtitle.title("Translation")
    subtitle.overrideredirect(True)
    subtitle.attributes("-topmost", True)
    subtitle.attributes("-alpha", 0.7)
    subtitle.configure(bg='black')
    subtitle.minsize(500, 50)
    label = Label(subtitle, text="", font=("Arial", font_size), wraplength=1480, fg='white', bg='black')
    label.pack(expand=True, fill='both')

    # Resize the wraplength of the label when the subtitle is resized
    def update_wraplength(event):
        label.config(wraplength=subtitle.winfo_width() - 20)

    subtitle.bind("<Configure>", update_wraplength)

    resize_button = Canvas(subtitle, width=15, height=15, bg='black', highlightthickness=0, cursor='size_nw_se')
    resize_button.place(relx=1.0, rely=1.0, anchor='se')
    resize_button.create_polygon(0, 15, 15, 0, 15, 15, fill='grey')

    # Allow the subtitle to be moved and resized
    def start_move(event):
        subtitle.x = event.x
        subtitle.y = event.y

    def do_move(event):
        x = subtitle.winfo_pointerx() - subtitle.x
        y = subtitle.winfo_pointery() - subtitle.y
        subtitle.geometry(f"+{x}+{y}")

    def start_resize(event):
        subtitle.x = event.x_root
        subtitle.y = event.y_root

    def do_resize(event):
        new_width = subtitle.winfo_width() + (event.x_root - subtitle.x)
        new_height = subtitle.winfo_height() + (event.y_root - subtitle.y)
        subtitle.geometry(f"{new_width}x{new_height}")
        subtitle.x = event.x_root
        subtitle.y = event.y_root

    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)
    resize_button.bind("<Button-1>", start_resize)
    resize_button.bind("<B1-Motion>", do_resize)

    return subtitle, label

# Update the translation text in the subtitle
def update_translation(label, recognized_text, translation):
    print("------------------------------")
    if display_both:
        print(f"{recognized_text}\n")
    print(f"{translation.text}")
    print("------------------------------\n")
    if display_both:
        label.config(text=f"{recognized_text}\n{translation.text}")
    else:
        label.config(text=f"{translation.text}")
    label.update_idletasks()
    label.update()
    reset_clear_timer(label)

# Reset the label text after a certain duration of inactivity
def reset_clear_timer(label):
    def clear_label_text():
        label.config(text="")
        label.update_idletasks()
        label.update()

    if hasattr(reset_clear_timer, 'timer'):
        reset_clear_timer.timer.cancel()
    reset_clear_timer.timer = threading.Timer(5.0, clear_label_text)
    reset_clear_timer.timer.start()

# Main loop for speech recognition and translation
async def main_loop(label):
    with sr.Microphone(device_index=stereo_mix_index) as source:
        print("------------------------------")
        print("Calibrating for speech recognition...")
        recognizer.adjust_for_ambient_noise(source)
        print("Calibration complete.")
        time.sleep(1)
        if enable_shortcuts:
            print("\nKeyboard Shortcuts:\n"
                  "--------------------------------------------------\n"
                  "| Key | Function                                 |\n"
                  "--------------------------------------------------\n"
                  "| p   | Pause/Resume                             |\n"
                  "| d   | Toggle display mode                      |\n"
                  "| s   | Show/Hide subtitles                      |\n"
                  "| b   | Break sentence                           |\n"
                  "| l   | Return to language selection             |\n"
                  "--------------------------------------------------")
        print(f"\nTranslating from ({source_lang}) to ({target_lang})")
        print("------------------------------\n")
        while True:
            audio_data, voice_detected = listen_until_break(source, label)
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
                update_translation(label, recognized_text, translation)
            except sr.UnknownValueError:
                print("------------------------------")
                print("Could not understand audio.")
                print("------------------------------\n")
            except sr.RequestError as req_err:
                print("------------------------------")
                print(f"Could not request results; {req_err}")
                print("------------------------------\n")

def clear_input_buffer():
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def return_to_language_selection(label):
    global source_lang, target_lang, src_lang_for_trans, paused
    paused = True
    print("------------------------------")
    print("Returning to language selection...")
    show_temp_message(label, "Returning to language selection...", duration=2)
    time.sleep(2)
    # Clear user input buffer before requesting language
    clear_input_buffer()
    source_lang = select_language("Enter the source language code: ", valid_lang_codes)
    target_lang = select_language("Enter the target language code: ", valid_lang_codes)
    src_lang_for_trans = source_lang.split("-")[0].lower()
    print(f"Translating from ({source_lang}) to ({target_lang})")
    print("------------------------------\n")
    show_temp_message(label, f"Translating from ({source_lang}) to ({target_lang})", duration=2)
    paused = False

def run_main(font_size):
    subtitle, label = create_subtitle(font_size)
    enable_shortcuts(label, subtitle)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threading.Thread(target=loop.run_until_complete, args=(main_loop(label),), daemon=True).start()
    subtitle.mainloop()

if __name__ == "__main__":
    run_main(font_size)