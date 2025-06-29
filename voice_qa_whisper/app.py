from flask import Flask, render_template, request, redirect, jsonify
import whisper
from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import json
import soundfile as sf
import pygame

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("small")

# Load questions JSON
with open("questions.json", encoding='utf-8') as f:
    all_questions = json.load(f)["questions"]

# Initialize state variables
current_index = 0
selected_lang = 'en'
answers = []
questions = []
upload_received = False

@app.route('/')
def home():
    return render_template("start.html")

@app.route('/start', methods=['POST'])
def start():
    global selected_lang, current_index, answers, questions, upload_received
    selected_lang = request.form['lang']
    questions = all_questions[selected_lang]
    current_index = 0
    answers = []
    upload_received = False
    return redirect("/question")

@app.route('/question')
def question():
    global current_index, selected_lang
    if current_index >= len(questions):
        return redirect("/results")

    question_text = questions[current_index]
    mp3_path = f"question_{current_index}.mp3"

    # Generate and save TTS question
    tts = gTTS(text=question_text, lang=selected_lang)
    tts.save(mp3_path)

    # Play audio using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

    os.remove(mp3_path)

    return render_template("index.html", question=question_text)

@app.route('/upload', methods=['POST'])
def upload():
    global current_index, upload_received
    audio = request.files['audio_data']
    audio_path = f"audio_files/recording{current_index}.wav"
    audio.save(audio_path)

    result = model.transcribe(audio_path)
    text = result["text"]

    # Translate to English
    translated = GoogleTranslator(source='auto', target='en').translate(text)

    answers.append({
        "question": questions[current_index],
        "answer": text,
        "translation": translated
    })

    upload_received = True  # Mark upload complete

    return jsonify({"answer": text, "translation": translated})

@app.route('/next')
def next_question():
    global current_index, upload_received
    if not upload_received:
        return "Please record and submit your answer before moving to the next question."

    current_index += 1
    upload_received = False
    return redirect("/question")

@app.route('/results')
def results():
    return render_template("results.html", answers=answers)

if __name__ == '__main__':
    os.makedirs("audio_files", exist_ok=True)
    app.run(debug=True)
