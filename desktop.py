import os
import sys
import threading
import time
import webview
from webview.dom import DOMEventHandler
from app import app, init_db, BASE_DIR

# --- JS API Bridge: exposes Python functions to JavaScript in the webview ---
class Api:
    def open_file_dialog(self):
        """Opens a native OS file picker and returns the selected file path (or None).
        Used as the primary file selection method in the desktop EXE.
        """
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=('Excel Files (*.xlsx)',)
        )
        if result and len(result) > 0:
            return result[0]
        return None

api = Api()

# 1. Ensure database initialization is complete
init_db()

# 2. Start the Flask server in a background thread
def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# 3. Small pause to allow the port to bind
time.sleep(1.0)

# 4. Bind function: called after the webview window finishes loading
#    Registers OS-level drag-and-drop handlers using pywebview's DOMEventHandler.
#    This gives us the real file system path via e['dataTransfer']['files'][n]['pywebviewFullPath'].
def bind(w):
    def on_drop(e):
        try:
            files = e.get('dataTransfer', {}).get('files', [])
            for f in files:
                path = f.get('pywebviewFullPath', '')
                if path and path.lower().endswith('.xlsx'):
                    # Escape backslashes for JS string
                    js_path = path.replace('\\', '\\\\')
                    w.evaluate_js(f"window.handleDroppedFilePath('{js_path}');")
                    break
        except Exception as ex:
            print(f"Drop handler error: {ex}")

    def on_dragover(e):
        pass  # Just needs to be registered with prevent_default=True

    # Register on the whole document so drops anywhere on the window work
    w.dom.document.events.drop += DOMEventHandler(
        on_drop, prevent_default=True, stop_propagation=True
    )
    w.dom.document.events.dragover += DOMEventHandler(
        on_dragover, prevent_default=True
    )

# 5. Launch the native desktop window pointing to localhost
print("Launching Chit Fund Desktop Window...")
window = webview.create_window(
    title='Chit Fund Management Desktop',
    url='http://127.0.0.1:5000',
    width=1100,
    height=800,
    resizable=True,
    min_size=(900, 650),
    js_api=api
)
webview.start(bind, window, debug=False)
