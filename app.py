from flask import Flask , render_template, request , session, redirect
from werkzeug.security import generate_password_hash , check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "therezinha"

@app.route("/")
def home():
    return "VGC Team Manager is running!"

#ROTA CADASTRO
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        senha_hash = generate_password_hash(senha)

        try:
            conexao = sqlite3.connect("vgc.db")
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)", (nome, email, senha_hash))
            conexao.commit()
            conexao.close()
            return render_template("cadastro.html", mensagem="Conta criada com sucesso!")
        except sqlite3.IntegrityError:
            return render_template("cadastro.html", mensagem="Erro: Email já cadastrado.")
    return render_template("cadastro.html", mensagem="")

#ROTA LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = sqlite3.connect("vgc.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, senha_hash FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conexao.close()

        if usuario and check_password_hash(usuario[2], senha):
            session["id_usuario"] = usuario[0]
            session["nome"] = usuario[1]
            return redirect("/times")
        else:
            return render_template("login.html", mensagem="Email ou senha incorretos.")
        
    return render_template("login.html", mensagem="")

#DEBUG   
if __name__ == "__main__":
    app.run(debug=True)
