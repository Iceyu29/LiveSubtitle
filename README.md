# Overview
This program captures audio directly from your system using Stereo Mix, processes it through SpeechRecognition, translates the recognized speech into multiple languages with GoogleTrans, and displays the translated text in an adjustable subtitle window.

# Main Features
- Voice Recognition: Captures system audio using Stereo Mix with SpeechRecognition
- Translation: Supports multiple languages using GoogleTrans
- Hotkeys: Convenient keyboard shortcuts for controlling the program efficiently.
- Subtitles: Displays translated text in an adjustable subtitle window for a better viewing experience.

# Requirements
- Operating System: Windows 7/8/8.1/10/11
- Realtek Audio Driver with Stereo Mix: "Stereo Mix" must be enabled to capture system audio. You can check this in your sound settings.

# Usage
- Run directly from code (Make sure you have Python pre-installed on your system)
  + Install required Python libraries:
```shell
pip install keyboard speechrecognition googletrans
```
- Run from pre-build exe file:
  + Download latest version: https://github.com/Iceyu29/ScreenAudioTranslate/releases/latest

**Enable Stereo Mix:**
1. Right-click the speaker icon in the taskbar and select Sounds.
2. Go to the Recording tab and look for Stereo Mix.
3. If it's disabled, right-click and enable it.

# License
This project is licensed under the MIT License.
