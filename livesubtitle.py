import time
import speech_recognition as sr
from deep_translator import GoogleTranslator
from tkinter import Tk, Label, Button, Frame, ttk, Text, Scrollbar, Canvas, END
import threading
import queue

# Function to log messages to the console
def log_message(console, message_key, extra_info=""):
    message = console_log_texts.get(message_key, message_key) + extra_info
    console.config(state="normal")
    console.insert(END, message + "\n")
    console.see(END)
    console.config(state="disabled")

# Function to initialize the Stereo Mix device
mic = None
stereo_mix_index = None
# Define reinit_button globally
reinit_button = None
def initialize_stereomix(console):
    global mic, stereo_mix_index
    mic_names = sr.Microphone.list_microphone_names()
    stereo_mix_index = next((index for index, name in enumerate(mic_names) if "stereo mix" in name.lower()), None)
    if stereo_mix_index is None:
        log_message(console, "stereo_mix_error")
        return False
    try:
        mic = sr.Microphone(device_index=stereo_mix_index)
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        # Print credit after successful initialization
        log_message(console, "-------------------------------------")
        log_message(console, "- Copyright of Iceyu29, 2025        -")
        log_message(console, "- https:/https://github.com/Iceyu29 -")
        log_message(console, "-------------------------------------")
        return True
    except Exception:
        log_message(console, "stereo_mix_error")
        return False

def disable_controls():
    source_combobox.config(state="disabled")
    target_combobox.config(state="disabled")
    subtitle_button.config(state="disabled")
    display_button.config(state="disabled")

def enable_controls():
    source_combobox.config(state="readonly")
    target_combobox.config(state="readonly")
    subtitle_button.config(state="normal")
    display_button.config(state="normal")

def reinitialize_stereomix(console, reinit_button):
    """Attempt to reinitialize Stereo Mix."""
    if initialize_stereomix(console):
        enable_controls()
        reinit_button.destroy()

# Function to toggle subtitles visibility
subtitles_visible = False
def toggle_subtitles(subtitles, subtitle_button):
    global subtitles_visible
    subtitles_visible = not subtitles_visible
    ui_texts = console_log_texts
    subtitle_button.config(text=ui_texts["hide_subtitles"] if subtitles_visible else ui_texts["show_subtitles"])
    if subtitles_visible:
        subtitles.deiconify()
    else:
        subtitles.withdraw()

# Function to toggle display mode
display_both = True
def toggle_display_mode(display_button):
    global display_both
    display_both = not display_both
    ui_texts = console_log_texts
    display_button.config(text=ui_texts["show_translated_only"] if not display_both else ui_texts["show_both"])

# Function to update the translation text in the subtitles
subtitle_clear_timer = None
def update_translation(label, recognized_text, translation_text, root):
    global subtitle_clear_timer
    if display_both:
        label.config(text=f"{recognized_text}\n{translation_text}")
    else:
        label.config(text=f"{translation_text}")
    label.update_idletasks()

    # Reset the subtitle clear timer
    if subtitle_clear_timer is not None:
        subtitle_clear_timer.cancel()
    subtitle_clear_timer = threading.Timer(3.0, clear_subtitle, args=(label, root))
    subtitle_clear_timer.start()

# Function to clear the subtitle text
def clear_subtitle(label, root):
    # Schedule clearing the subtitle text in the main thread
    root.after(0, lambda: label.config(text=""))
    root.after(0, label.update_idletasks)

# Recognizer thread for continuous listening
recognizer_thread_running = False
recognizer = sr.Recognizer()
phrase_queue = queue.Queue()
def recognizer_thread(console):
    global recognizer_thread_running, mic
    try:
        with mic as source:
            log_message(console, "calibrating")
            recognizer.adjust_for_ambient_noise(source)
            log_message(console, "calibration_complete")
            while recognizer_thread_running:
                try:
                    audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    recognized_text = recognizer.recognize_google(audio_data, language=source_lang)
                    phrase_queue.put(recognized_text)
                    log_message(console, "Recognized: ", recognized_text)
                except Exception:
                    log_message(console, "recognition_error")
    except Exception:
        pass

# Translator thread for processing queued phrases
translator_thread_running = False  # Add a global flag for the translator thread
def translator_thread(label, console, root):
    global translator_thread_running
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    while translator_thread_running:  # Check the running flag
        if not phrase_queue.empty():
            try:
                recognized_text = phrase_queue.get()
                translation_text = translator.translate(recognized_text)
                
                # Schedule GUI updates in the main thread
                root.after(0, update_translation, label, recognized_text, translation_text, root)
                root.after(0, log_message, console, "Translated: ", translation_text)
            except Exception as e:
                root.after(0, log_message, console, "translation_error", str(e))
        else:
            time.sleep(0.1)

# Function to start/stop the recognizer and translator threads
def toggle_recognition(label, console, start_button, root):
    global recognizer_thread_running, translator_thread_running
    ui_texts = console_log_texts
    if recognizer_thread_running:
        recognizer_thread_running = False
        translator_thread_running = False
        start_button.config(text=ui_texts["start_button"])
        source_combobox.config(state="readonly")
        target_combobox.config(state="readonly")
    else:
        recognizer_thread_running = True
        translator_thread_running = True
        source_combobox.config(state="disabled")
        target_combobox.config(state="disabled")
        threading.Thread(target=recognizer_thread, args=(console,), daemon=True).start()
        threading.Thread(target=translator_thread, args=(label, console, root), daemon=True).start()
        start_button.config(text=ui_texts["stop_button"])

def on_close(root, subtitles):
    global recognizer_thread_running, translator_thread_running
    recognizer_thread_running = False
    translator_thread_running = False
    subtitles.destroy()
    root.destroy()

# Function to update UI language
def update_ui_language(language):
    global current_language
    current_language = language  # Track the current language
    translations = {
        "en": {
            "source_label": "Source Language:",
            "target_label": "Target Language:",
            "start_button": "Start",
            "stop_button": "Stop",
            "show_subtitles": "Show Subtitles",
            "hide_subtitles": "Hide Subtitles",
            "show_translated_only": "Show Translated Only",
            "show_both": "Show Both",
            "reinitialize": "Reinitialize",
            "calibrating": "Calibrating for speech recognition...",
            "calibration_complete": "Calibration complete",
            "recognition_error": "Recognition Error: No speech detected or unrecognized audio",
            "translation_error": "Translation Error: ",
        },
        "vi": {
            "source_label": "Ngôn ngữ nguồn:",
            "target_label": "Ngôn ngữ đích:",
            "start_button": "Bắt đầu",
            "stop_button": "Dừng",
            "show_subtitles": "Hiển thị phụ đề",
            "hide_subtitles": "Ẩn phụ đề",
            "show_translated_only": "Chỉ hiển thị bản dịch",
            "show_both": "Hiển thị cả hai",
            "reinitialize": "Khởi tạo lại",
            "calibrating": "Đang hiệu chỉnh để nhận dạng giọng nói...",
            "calibration_complete": "Hiệu chỉnh hoàn tất",
            "recognition_error": "Lỗi nhận dạng: Không phát hiện giọng nói hoặc âm thanh không nhận dạng được",
            "translation_error": "Lỗi dịch: ",
        }
    }
    ui_texts = translations.get(language, translations["en"])
    source_label.config(text=ui_texts["source_label"])
    target_label.config(text=ui_texts["target_label"])
    start_button.config(text=ui_texts["start_button"] if not recognizer_thread_running else ui_texts["stop_button"])
    subtitle_button.config(text=ui_texts["show_subtitles"] if not subtitles_visible else ui_texts["hide_subtitles"])
    display_button.config(text=ui_texts["show_translated_only"] if not display_both else ui_texts["show_both"])
    if reinit_button and reinit_button.winfo_exists():
        reinit_button.config(text=ui_texts["reinitialize"])
    global console_log_texts
    console_log_texts = ui_texts

    # Update button states
    en_button.config(state="disabled" if language == "en" else "normal")
    vi_button.config(state="disabled" if language == "vi" else "normal")

# Function to create the GUI
def create_gui():
    global source_combobox, target_combobox, start_button, subtitle_button, display_button, source_label, target_label, console_log_texts, reinit_button, en_button, vi_button
    root = Tk()
    root.title("LiveSubtitle")
    root.iconbitmap("icon.ico")
    root.geometry("600x300")
    root.resizable(False, False)

    # Left panel for controls
    control_frame = Frame(root)
    control_frame.pack(side="left", fill="y", padx=10, pady=10)

    # Language mapping
    LANGUAGES = {
        "Afrikaans": "af", "Arabic": "ar", "Bengali": "bn", "Bulgarian": "bg", "Chinese (Simplified)": "zh-CN",
        "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en",
        "Estonian": "et", "Filipino": "tl", "Finnish": "fi", "French": "fr", "German": "de",
        "Greek": "el", "Gujarati": "gu", "Hausa": "ha", "Hebrew": "he", "Hindi": "hi",
        "Hungarian": "hu", "Igbo": "ig", "Indonesian": "id", "Italian": "it", "Japanese": "ja",
        "Kannada": "kn", "Korean": "ko", "Latvian": "lv", "Lithuanian": "lt", "Malay": "ms",
        "Malayalam": "ml", "Marathi": "mr", "Norwegian": "no", "Persian": "fa", "Polish": "pl",
        "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Serbian": "sr",
        "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl", "Spanish": "es", "Swahili": "sw",
        "Swedish": "sv", "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr",
        "Ukrainian": "uk", "Urdu": "ur", "Vietnamese": "vi", "Yoruba": "yo", "Zulu": "zu"
    }

    # Source language combobox
    source_label = Label(control_frame, text="Source Language:")
    source_label.pack(anchor="w")
    source_combobox = ttk.Combobox(control_frame, values=["Select Language"] + list(LANGUAGES.keys()), state="readonly")
    source_combobox.set("Select Language")
    source_combobox.pack(anchor="w", fill="x")

    # Target language combobox
    target_label = Label(control_frame, text="Target Language:")
    target_label.pack(anchor="w")
    target_combobox = ttk.Combobox(control_frame, values=["Select Language"] + list(LANGUAGES.keys()), state="readonly")
    target_combobox.set("Select Language")
    target_combobox.pack(anchor="w", fill="x")

    # Update source_lang and target_lang when combobox values change
    def update_languages():
        global source_lang, target_lang
        source_lang = LANGUAGES.get(source_combobox.get(), "")
        target_lang = LANGUAGES.get(target_combobox.get(), "")
        # Enable Start/Stop button only if both languages are selected and not "Select Language"
        start_button.config(state="normal" if source_lang and target_lang and mic else "disabled")

    source_combobox.bind("<<ComboboxSelected>>", lambda _: update_languages())
    target_combobox.bind("<<ComboboxSelected>>", lambda _: update_languages())

    # Start/Stop button
    start_button = Button(control_frame, text="Start", state="disabled", command=lambda: toggle_recognition(label, console, start_button, root))
    start_button.pack(anchor="w", fill="x", pady=5)

    # Subtitle toggle button
    subtitle_button = Button(control_frame, text="Show Subtitles", state="disabled", command=lambda: toggle_subtitles(subtitles, subtitle_button))
    subtitle_button.pack(anchor="w", fill="x", pady=5)

    # Display mode button
    display_button = Button(control_frame, text="Show Translated Only", state="disabled", command=lambda: toggle_display_mode(display_button))
    display_button.pack(anchor="w", fill="x", pady=5)

    # Add language toggle buttons
    language_frame = Frame(control_frame)
    language_frame.pack(anchor="w", pady=5, side="bottom")
    en_button = Button(language_frame, text="EN", width=5, command=lambda: update_ui_language("en"))
    en_button.pack(side="left", padx=2)
    vi_button = Button(language_frame, text="VI", width=5, command=lambda: update_ui_language("vi"))
    vi_button.pack(side="left", padx=2)

    # Initialize UI language to English
    update_ui_language("en")

    # Right panel for console
    console_frame = Frame(root)
    console_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    console = Text(console_frame, state="disabled", wrap="word", height=10)
    console.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(console_frame, command=console.yview)
    scrollbar.pack(side="right", fill="y")
    console.config(yscrollcommand=scrollbar.set)

    # Subtitle window
    subtitles = Tk()
    subtitles.title("Subtitle")
    subtitles.overrideredirect(True)
    subtitles.attributes("-topmost", True)
    subtitles.attributes("-alpha", 0.7)
    subtitles.configure(bg='black')
    subtitles.minsize(500, 50)
    subtitles.withdraw()

    # Bind the close event to the on_close function
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, subtitles))

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

    # Initialize Stereo Mix device when GUI starts
    if not initialize_stereomix(console):
        disable_controls()

        # Add a Reinitialize button
        reinit_button = Button(control_frame, text="Reinitialize", command=lambda: reinitialize_stereomix(console, reinit_button))
        reinit_button.pack(anchor="w", fill="x", pady=5)
    else:
        enable_controls()

    root.mainloop()

if __name__ == "__main__":
    create_gui()