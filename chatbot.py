import pyttsx3
import speech_recognition as sr
import openai
import time
from gtts import gTTS
import os
import sys
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import pygame
import tempfile

# Varijable
apiKey = "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"
openai.api_key = apiKey
name = "Sparky"
your_name = None
language = None
r = sr.Recognizer()

custom_voice_properties = {
    'voice': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0',
    'rate': 190,
    'volume': 1,
    'pitch': 200,
}

stop_event = threading.Event()


# Funkcija za prikaz kamere uzivo
def start_camera(panel):
    cap = cv2.VideoCapture(0)  # 0 je za obicnu kameru

    def update_frame():
        if stop_event.is_set():
            cap.release()
            return
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            panel.imgtk = imgtk
            panel.config(image=imgtk)
        panel.after(10, update_frame)

    update_frame()


# Funkcija za prikaz videa
def start_looping_video(video_path, panel):
    cap = cv2.VideoCapture(video_path)

    def update_video():
        if stop_event.is_set():
            cap.release()
            return
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restartovanje klipa u loop
            ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            panel.imgtk = imgtk
            panel.config(image=imgtk)

        panel.after(30, update_video)

    update_video()


# TTS funkcija za Engleski
def say_text(text, voice_properties=None):
    text_speech = pyttsx3.init()

    if voice_properties:
        for property_name, property_value in voice_properties.items():
            text_speech.setProperty(property_name, property_value)

    text_speech.say(text)
    text_speech.runAndWait()


# TTS funkcija za Srpski
def say_text_serbian(text):
    filename = f"../response_{int(time.time())}.mp3"
    tts = gTTS(text=text, lang='sr')
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()

    try:
        os.remove(filename)
    except OSError as e:
        print(f"Error deleting file: {e}")


# Centriranje GUI-ja
def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f'{width}x{height}+{x}+{y}')


# Odabir jezika
def language_selector():
    def select_language(language):
        nonlocal selected_language
        selected_language = language
        root.destroy()

    selected_language = None

    root = tk.Tk()
    root.geometry('500x250')
    root.resizable(width=False, height=False)
    root.title("Language Selector")

    center_window(root, 500, 250)

    label = tk.Label(root, text="Please select a language:", font=('Helvetica', 30, 'bold'))
    label.pack(pady=10)

    button1 = tk.Button(root, text="English", font=('Helvetica', 20, 'bold'),
                        command=lambda: select_language("English"))
    button1.pack(pady=5)

    button2 = tk.Button(root, text="Serbian", font=('Helvetica', 20, 'bold'),
                        command=lambda: select_language("Serbian"))
    button2.pack(pady=5)

    root.mainloop()

    return selected_language


# Unos imena
def get_name():
    def submit_name():
        nonlocal user_name
        user_name = entry.get()
        root.destroy()

    user_name = None

    root = tk.Tk()
    if language == "English":
        root.title("Enter Your Name")
    else:
        root.title("Unesi svoje ime")

    root.geometry("300x150")

    center_window(root, 300, 150)

    if language == "English":
        label = tk.Label(root, text="Please enter your name:", font=('Helvetica', 12))
    else:
        label = tk.Label(root, text="Unesi svoje ime", font=('Helvetica', 12))
    label.pack(pady=10)

    entry = tk.Entry(root, font=('Helvetica', 12))
    entry.pack(pady=5)

    submit_button = tk.Button(root, text="OK", font=('Helvetica', 12), command=submit_name)
    submit_button.pack(pady=10)

    root.mainloop()

    return user_name


# Pomocne funkcije
def kazi_i_napisi(text):
    print(text)
    say_text(text, voice_properties=custom_voice_properties)

def kazi_i_napisi_sr(text):
    print(text)
    say_text_serbian(text)


# Funkcija za snimanje zvuka
def record_text(lang):
    while True:
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.2)
                print("listening...")
                audio2 = r.listen(source2, timeout=4)
                print("Done listening")
                try:
                    my_text = r.recognize_google(audio2, language='en' if lang == "English" else 'sr-RS')
                    print("Done recognizing")

                    if my_text.lower() in ["sparky quit", "sparky exit", "sparky bye", "sparky izađi",
                                           "sparky zatvori"]:
                        return "exit"
                    if my_text.lower().startswith("sparky"):
                        print(my_text)
                        return my_text
                    else:
                        kazi_i_napisi("Please start your command with 'Sparky'")
                except sr.UnknownValueError:
                    kazi_i_napisi("Sorry, I didn't catch that. Could you repeat?")
                except sr.RequestError:
                    kazi_i_napisi("Sorry, there was an error recognizing your speech. Please try again.")
        except KeyboardInterrupt:
            print("exiting...")
        except sr.RequestError:
            print("Error")
        except sr.UnknownValueError:
            print("error")

# Komunikacija sa GPT-om
def ask_ai(text):
    try:
        response_ai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are {name}, an AI assistant, talking in {language}."},
                {"role": "user", "content": text}],
            max_tokens=100
        )
        return response_ai.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Varijabla da proveri da li je prozor pokrenut
window_active = True

# Main logika
def main_logic(your_name, lang):
    global window_active
    number_of_answers = 0
    if lang == "English":
        say_text(
            f"Hello {your_name}, my name is Sparky and you have three questions to ask me. How can I help you today?",
            voice_properties=custom_voice_properties)
    else:
        say_text_serbian(
            f"Zdravo {your_name}, ja sam Sparki, a ti imaš tri pitanja da mi postaviš. Kako ti mogu pomoći danas?")

    while True:
        if number_of_answers == 1:
            if lang == "English":
                kazi_i_napisi("Ask me another question!")
            else:
                kazi_i_napisi_sr("Postavi mi sledeće pitanje.")
        if number_of_answers == 2:
            if lang == "English":
                kazi_i_napisi("Ask me the last question!")
            else:
                kazi_i_napisi_sr("Postavi mi poslednje pitanje.")

        answer = record_text("en" if lang == "English" else "sr")
        number_of_answers += 1

        if answer == "exit":
            if lang == "English":
                kazi_i_napisi(f"Goodbye {your_name}. Have a nice day!")
            else:
                kazi_i_napisi_sr(f"Doviđenja {your_name}. Uživaj u danu.")

            stop_event.set()  # Signal da se sve niti zaustave
            window_active = False
            video_root.destroy()  # Automatski zatvori prozor
            return

        response = ask_ai(answer)
        if lang == "English":
            kazi_i_napisi(response)
        else:
            kazi_i_napisi_sr(response)

        if number_of_answers == 3:
            if lang == "English":
                kazi_i_napisi("I really hope I helped you today. See you next time!")
            else:
                kazi_i_napisi_sr("Stvarno se nadam da sam ti pomogao. Vidimo se sledeći put.")

            stop_event.set()
            window_active = False
            video_root.destroy()
            return

# Main funkcija
def main():
    global language, video_root

    say_text("Choose language!", voice_properties=custom_voice_properties)
    lang = language_selector()
    language = lang
    if lang is None:
        print("No language selected. Exiting.")
        return

    your_name = get_name()
    if your_name is None:
        print("No name entered. Exiting.")
        return

    global video_root
    video_root = tk.Tk()
    video_root.title("Sparky")
    video_root.configure(bg="black")

    window_width = 1200
    window_height = 600
    center_window(video_root, window_width, window_height)

    left_frame = tk.Frame(video_root, width=600, height=600, bg="black")
    left_frame.pack(side="left", padx=3, pady=3)
    right_frame = tk.Frame(video_root, width=600, height=600, bg="black")
    right_frame.pack(side="right", padx=3, pady=3)

    camera_label = tk.Label(left_frame, bg="black")
    camera_label.pack()

    video_label = tk.Label(right_frame, bg="black")
    video_label.pack()

    camera_thread = threading.Thread(target=start_camera, args=(camera_label,), daemon=True)
    camera_thread.start()

    looping_video_path = "./video1.mp4"

    if not os.path.exists(looping_video_path):
        kazi_i_napisi(f"Video file not found at {looping_video_path}. Please check the path.")
    else:
        video_thread = threading.Thread(target=start_looping_video, args=(looping_video_path, video_label), daemon=True)
        video_thread.start()

    logic_thread = threading.Thread(target=main_logic, args=(your_name, lang), daemon=True)
    logic_thread.start()

    video_root.mainloop()

    stop_event.set()
    if window_active:
        video_root.destroy()

if __name__ == "__main__":
    main()
