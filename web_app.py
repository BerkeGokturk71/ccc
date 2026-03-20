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
    # Koyeb'in atadığı dinamik portu alıyoruz
    port = int(os.environ.get("PORT", 8000))
    # host mutlaka '0.0.0.0' olmalı, aksi halde Koyeb dışarıdan erişemez
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)