import asyncio
import time
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
print("-------------------------------------")
print("- Copyright of Iceyu29, 2025        -")
print("- https:/https://github.com/Iceyu29 -")
print("-------------------------------------\n")
time.sleep(1)
print("This program uses the 'Stereo Mix' device to capture your system audio")
print("Ensure it is enabled in your system's sound settings and set to max volume\n")
time.sleep(1)

# Get the index of the 'Stereo Mix' device
mic_names = sr.Microphone.list_microphone_names()
stereo_mix_index = next((index for index, name in enumerate(mic_names) if "stereo mix" in name.lower()), None)
if stereo_mix_index is None:
    print("Stereo Mix device not found. Please ensure it is enabled and try again\n")
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
        print("Stereo Mix appears to be disabled. Enable it in your system's sound settings and try again\n")
        print("Closing in 10 seconds...")
        time.sleep(10)
        exit()
    else:
        raise

print(f"Using device '{mic_names[stereo_mix_index]}' (index {stereo_mix_index})\n")
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

def select_language(prompt, valid_options):
    while (user_input := input(prompt).strip()) not in valid_options:
        print("Invalid input. Please try again\n")
    return user_input

def enable_shortcuts(label, subtitles):
    global enable_shortcuts
    while (user_input := input("Do you want to enable keyboard shortcuts? (y/n): ").strip().lower()) not in {"y", "n"}:
        print("Invalid input. Please enter 'y' or 'n'\n")
    enable_shortcuts = user_input == "y"
    if enable_shortcuts:
        keyboard.add_hotkey('p', lambda: toggle_pause(label))
        keyboard.add_hotkey('d', lambda: toggle_display_mode(label))
        keyboard.add_hotkey('l', lambda: return_to_language_selection(label))
        keyboard.add_hotkey('s', lambda: toggle_subtitles_visibility(subtitles))
        keyboard.add_hotkey('b', lambda: None)

source_lang = select_language("Enter the source language code: ", valid_lang_codes)
target_lang = select_language("Enter the target language code: ", valid_lang_codes)
src_lang_for_trans = source_lang.split("-")[0].lower()

# Control pause and resume
paused = False
def toggle_pause(label):
    global paused
    paused = not paused
    if paused:
        print("Paused\n")
        show_temp_message(label, "Paused")
    else:
        print("Resumed\n")
        show_temp_message(label, "Resumed")

# Control subtitles visibility
subtitles_visible = True
def toggle_subtitles_visibility(subtitles):
    global subtitles_visible
    subtitles_visible = not subtitles_visible
    if subtitles_visible:
        subtitles.deiconify()
        print("Subtitles is visible\n")
    else:
        subtitles.withdraw()
        print("Subtitles is hidden\n")
        
# Control text display mode
display_both = True
def toggle_display_mode(label):
    global display_both
    display_both = not display_both
    if display_both:
        print("Displaying both recognized and translated text\n")
        show_temp_message(label, "Displaying both recognized and translated text")
    else:
        print("Displaying only translated text\n")
        show_temp_message(label, "Displaying only translated text")

# Show a temporary message on the label
def show_temp_message(label, message, duration=0.5):
    original_text = label.cget("text")
    label.config(text=message)
    label.update_idletasks()
    label.update()
    time.sleep(duration)
    label.config(text=original_text)
    label.update_idletasks()
    label.update()

# Create a tkinter subtitles for displaying subtitles
def create_subtitles():
    subtitles = Tk()
    subtitles.title("Subtitles")
    subtitles.overrideredirect(True)
    subtitles.attributes("-topmost", True)
    subtitles.attributes("-alpha", 0.7)
    subtitles.configure(bg='black')
    subtitles.minsize(500, 50)
    label = Label(subtitles, text="", font=("Arial", 14), wraplength=1480, fg='white', bg='black')
    label.pack(expand=True, fill='both')

    # Resize the wraplength of the label when the subtitles is resized
    def update_wraplength(event):
        label.config(wraplength=subtitles.winfo_width() - 20)
    subtitles.bind("<Configure>", update_wraplength)

    # Create a resize button
    resize_button = Canvas(subtitles, width=15, height=15, bg='black', highlightthickness=0, cursor='size_nw_se')
    resize_button.place(relx=1.0, rely=1.0, anchor='se')
    resize_button.create_polygon(0, 15, 15, 0, 15, 15, fill='grey')

    # Allow the subtitles to be moved and resized
    def start_move(event):
        subtitles.x = event.x
        subtitles.y = event.y

    def do_move(event):
        x = subtitles.winfo_pointerx() - subtitles.x
        y = subtitles.winfo_pointery() - subtitles.y
        subtitles.geometry(f"+{x}+{y}")

    def start_resize(event):
        subtitles.x = event.x_root
        subtitles.y = event.y_root

    def do_resize(event):
        new_width = subtitles.winfo_width() + (event.x_root - subtitles.x)
        new_height = subtitles.winfo_height() + (event.y_root - subtitles.y)
        subtitles.geometry(f"{new_width}x{new_height}")
        subtitles.x = event.x_root
        subtitles.y = event.y_root

    # Bind the mouse events for moving and resizing
    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)
    resize_button.bind("<Button-1>", start_resize)
    resize_button.bind("<B1-Motion>", do_resize)

    return subtitles, label

# Update the translation text in the subtitles
def update_translation(label, recognized_text, translation):
    print("------------------------------")
    if display_both:
        print(f"({source_lang}): {recognized_text}\n")
    print(f"({target_lang}): {translation.text}")
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
async def main(label):
    with sr.Microphone(device_index=stereo_mix_index) as source:
        print("Calibrating for speech recognition...")
        recognizer.adjust_for_ambient_noise(source)
        print("Calibration complete")
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
        time.sleep(1)
        print(f"\nTranslating from ({source_lang}) to ({target_lang})\n")
        
        # Initialize the recognizer and translator
        context_buffer = []  # Buffer to store recognized phrases
        context_timeout = 3  # Time window (in seconds) to consider phrases as part of the same context
        last_recognition_time = time.time()
        translator = Translator()

        # Continuously listen and recognize speech
        while True:
            if paused:
                time.sleep(0.1)
                continue
            try:
                # Continuously listen and recognize speech
                audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                recognized_text = recognizer.recognize_google(audio_data, language=source_lang)
                
                # Add recognized text to the context buffer
                context_buffer.append(recognized_text)
                current_time = time.time()

                # Check if the time since the last recognition exceeds the timeout
                if current_time - last_recognition_time > context_timeout:
                    # Combine the buffer into a single context
                    full_context = " ".join(context_buffer)
                    context_buffer.clear()  # Clear the buffer

                    # Translate the full context
                    translation = await translator.translate(
                        full_context,
                        src=src_lang_for_trans,
                        dest=target_lang
                    )
                    update_translation(label, full_context, translation)

                last_recognition_time = current_time
            except Exception:
                pass

# Return to language selection
def return_to_language_selection(label):
    global source_lang, target_lang, src_lang_for_trans, paused
    paused = True
    print("Returning to language selection...")
    label.config(text='Waiting for language selection')
    label.update_idletasks()
    label.update()
    time.sleep(1)
    # Clear the input buffer
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    source_lang = select_language("Enter the source language code: ", valid_lang_codes)
    target_lang = select_language("Enter the target language code: ", valid_lang_codes)
    src_lang_for_trans = source_lang.split("-")[0].lower()
    print(f"Translating from ({source_lang}) to ({target_lang})\n")
    label.config(text="")
    label.update_idletasks()
    label.update()
    show_temp_message(label, "Language selection updated", duration=1)
    paused = False

if __name__ == "__main__":
    subtitles, label = create_subtitles()
    enable_shortcuts(label, subtitles)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threading.Thread(target=loop.run_until_complete, args=(main(label),), daemon=True).start()
    subtitles.mainloop()