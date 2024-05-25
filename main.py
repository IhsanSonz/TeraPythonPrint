import os
import random
import time
import logging
from flask import Flask, request, jsonify
import threading
from tkinter import Tk, Label, messagebox

app = Flask(__name__)

SERVICE_STATUS = "Hello from github.com/IhsanSonz/TeraPythonPrint :8088"
SERVER_RUNNING = False
SERVER_THREAD = None

def is_readable(filename):
    try:
        with open(filename, 'r') as f:
            return True
    except Exception as e:
        return False

@app.route('/', methods=['GET'])
def service_status():
    return jsonify({'status': SERVICE_STATUS})

@app.route('/autoprint-pdf', methods=['POST'])
def autoprint_pdf():
    try:
        pdf_file = request.files['pdf']
        if pdf_file.mimetype != 'application/pdf':
            return jsonify({'error': True, 'msg': 'failed create pdf', 'hint': 'params error: invalid type for file pdf (application/pdf needed)'}), 400

        pdf_dir = './pdf'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, 0o777)

        filename = time.strftime("%Y%m%d%H%M%S") + str(random.randint(10000, 99999)) + '.pdf'
        filename = os.path.join(pdf_dir, filename)
        pdf_file.save(filename)

        if not os.path.exists(filename) or not is_readable(filename):
            return jsonify({'error': True, 'msg': 'failed create pdf', 'hint': 'failed to find the uploaded file'}), 500

        print_to = request.form.get('print_to')
        if not print_to:
            return jsonify({'error': True, 'msg': 'failed create pdf', 'hint': 'params error: invalid print_to'}), 400

        print_settings = request.form.get('print_settings', '1x')

        program = f'./SumatraPDF-3.3.3-64.exe'
        args = [];

        debug = request.form.get('debug')
        if debug != 't':
          args.append('-silent')

        filename = filename.replace('\\', '/')
        args.extend([f"-print-settings", f"{print_settings}", f"-print-to", f"{print_to}", f"{filename}"])

        logging.info(f'pdf: {filename}')
        logging.info(f'printTo: {print_to}')
        logging.info(f'printSettings: {print_settings}')
        logging.info(f'program: {program}')
        logging.info(f'args: {args}')

        import subprocess
        # p = subprocess.Popen(['powershell', '-Command', command], shell=True)
        p = subprocess.Popen([program] + args)
        p.wait()
        logging.info(f'p.args: {p.args}')
        os.remove(filename)

        return jsonify({'error': False, 'msg': 'AutoPrint PDF activated'}), 200

    except Exception as e:
        logging.error(str(e))
        return jsonify({'error': True, 'msg': 'failed to print pdf', 'hint': 'failed to execute print command'}), 500

def start_server():
    global SERVER_RUNNING, SERVER_THREAD
    if not SERVER_RUNNING:
        try:
            SERVER_THREAD = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8088, 'debug': False})
            SERVER_THREAD.daemon = True  # Set as daemon thread
            SERVER_THREAD.start()
            SERVER_RUNNING = True
            status_label.config(text=f"Server Started")
            info_label.config(text=f"Server is running on port 8088")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")

def on_closing():
    window.destroy()

# Create main window
window = Tk()
window.title("TeraPythonPrint Service")
window.geometry("300x150")  # Set window width to 300 and height to 150

# Status Label
status_label = Label(window, text="Server Stopped", font=("Arial", 14))
status_label.pack(pady=10)

# Status Label
info_label = Label(window, text="", font=("Arial", 14))
info_label.pack(pady=10)

# Status Label
creator_label = Label(window, text="github.com/IhsanSonz/TeraPythonPrint", font=("Arial", 8))
creator_label.pack(pady=10)

# Bind on_closing function to WM_DELETE_WINDOW event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Run the GUI
window.wait_visibility()
start_server()
window.mainloop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)