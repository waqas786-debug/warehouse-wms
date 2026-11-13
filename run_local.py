import os, sys, webbrowser, threading

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    DATA_DIR = os.path.dirname(sys.executable)
    os.chdir(DATA_DIR)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

from app import create_app

app = create_app()
if getattr(sys, 'frozen', False):
    app.template_folder = os.path.join(BASE_DIR, 'app', 'templates')
    app.static_folder = os.path.join(BASE_DIR, 'app', 'static')

def open_browser():
    webbrowser.open("http://127.0.0.1:8080")

if __name__ == "__main__":
    print("====================================================")
    print("  Offline Warehouse Server Running on Port 8080")
    print("  Open Browser: http://127.0.0.1:8080")
    print("====================================================")
    threading.Timer(1.5, open_browser).start()
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8080)
    except ImportError:
        app.run(host="0.0.0.0", port=8080, debug=False)
