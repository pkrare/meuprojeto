from flask import Flask, render_template, request, jsonify 
import threading
import datetime
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

lock = threading.Lock()

# Função que salva a mensagem (em thread separada)
def salvar_em_background(mensagem):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with lock:
        with open("entradas.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {mensagem}\n")
    print(f"[Thread] Mensagem salva: {mensagem}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/salvar", methods=["POST"])
def salvar():
    data = request.json
    mensagem = data.get("mensagem", "")
    
    if not mensagem.strip():
        return jsonify({"status": "erro", "mensagem": "Mensagem vazia"}), 400

    thread = threading.Thread(target=salvar_em_background, args=(mensagem,))
    thread.start()

    return jsonify({"status": "ok"})

@app.route("/mensagens")
def mensagens():
    if not os.path.exists("entradas.txt"):
        return render_template("mensagens.html", mensagens=[], total=0)

    with open("entradas.txt", "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    return render_template("mensagens.html", mensagens=linhas, total=len(linhas))

@app.route("/api/mensagens")
def api_mensagens():
    if not os.path.exists("entradas.txt"):
        return jsonify({"mensagens": [], "total": 0})

    with open("entradas.txt", "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    return jsonify({"mensagens": linhas, "total": len(linhas)})

@app.route("/limpar", methods=["POST"])
def limpar():
    if os.path.exists("entradas.txt"):
        open("entradas.txt", "w", encoding="utf-8").close()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
