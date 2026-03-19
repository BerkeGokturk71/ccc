import os

from flask import Flask, render_template, jsonify
import database

app = Flask(__name__)

@app.route('/')
def index():
    # Buraya bir index.html yapman lazım templates klasörüne
    return render_template('index.html')

@app.route('/api/moves')
def get_moves():
    # Socket'in güncellediği veriyi döner
    return jsonify(database.get_moves())

def run_flask():
    # Render'ın verdiği portu al, yoksa 5000 kullan
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)