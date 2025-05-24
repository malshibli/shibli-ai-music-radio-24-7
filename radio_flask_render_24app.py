from flask import Flask, Response, send_from_directory
import gradio as gr
import threading
import os
import time

# === Fixed Flask Port for Local + Render ===
FLASK_PORT = 8000

# === Flask App ===
flask_app = Flask(__name__)
LIBRARY_FOLDER = "static/song_library"

def get_mp3_files():
    files = [os.path.join(LIBRARY_FOLDER, f) for f in os.listdir(LIBRARY_FOLDER) if f.endswith(".mp3")]
    files.sort()
    return files

def generate_stream():
    while True:
        files = get_mp3_files()
        print(f"🎵 Found {len(files)} file(s).")
        if not files:
            print("⚠️ No audio files found.")
            time.sleep(2)
            continue
        for path in files:
            print(f"▶️ Now streaming: {path}")
            with open(path, "rb") as f:
                yield f.read()
            time.sleep(1)

@flask_app.route("/stream.mp3")
def stream_mp3():
    return Response(generate_stream(), mimetype="audio/mpeg")

@flask_app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

# === Run Flask in background ===
def run_flask():
    print(f"🚀 Flask running on http://localhost:{FLASK_PORT}/stream.mp3")
    flask_app.run(host="0.0.0.0", port=FLASK_PORT, threaded=True)

threading.Thread(target=run_flask, daemon=True).start()

# === Detect Render vs Local Environment ===
on_render = "PORT" in os.environ

# === Generate correct stream URL ===
stream_url = "/stream.mp3" if on_render else f"http://localhost:{FLASK_PORT}/stream.mp3"

# === Gradio UI ===
with gr.Blocks(title="📻 Shibli AI Radio Stream") as demo:
    with gr.Column():
        gr.Markdown("## 🎶 Shibli AI Radio Stream  راديو شبلي الذكي (Public)")
        gr.HTML(
            f"""
            <audio controls autoplay style='width: 100%;'>
                <source src="{stream_url}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
            """
        )
        gr.Textbox(value=f"📡 Streaming from: {stream_url}", interactive=False)

# === Launch Gradio ===
if on_render:
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ["PORT"]))
else:
    demo.launch(server_name="0.0.0.0", share=True)
