from flask import Flask, render_template
import subprocess

app = Flask(__name__, static_folder='static', template_folder='templates')
current_process = None

# Serve your frontend HTML file
@app.route('/')
def serve_index():
    return render_template('index2.html')  # ✅ auto-load with CSS support

@app.route('/start_keyboard')
def start_keyboard():
    return launch_process("virtual_keyboard.py", "Gesture Keyboard")

@app.route('/start_voice')
def start_voice():
    return launch_process("speechrecog.py", "Voice Assistant")

@app.route('/stop_feature')
def stop_feature():
    global current_process
    if current_process:
        try:
            current_process.terminate()
        except:
            pass
        current_process = None
    return "✅ Stopped everything"

def launch_process(script, feature_name):
    global current_process

    if current_process:
        try:
            current_process.terminate()
        except:
            pass

    import psutil
    current_process = subprocess.Popen(
        ["python", script],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        start_new_session=True
    )


    return f"✅ {feature_name} Started"

if __name__ == '__main__':
    app.run(debug=True)
