from flask import Flask , render_template, request , session, redirect
from werkzeug.security import generate_password_hash , check_password_hash
import sqlite3
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

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

#ROTA LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#ROTA TIMES
@app.route("/times")
def times():
    if "id_usuario" not in session:
        return redirect("/login")
    
    conexao = sqlite3.connect("vgc.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome ,formato FROM times WHERE id_usuario = ?", (session["id_usuario"],))
    lista_times = cursor.fetchall()
    conexao.close()

    return render_template("times.html", times = lista_times, nome = session["nome"])

#ROTA CRIAR TIME
@app.route("/times/novo", methods=["GET", "POST"])
def novo_time():
    if "id_usuario" not in session:
        return redirect("/login")
    
    if request.method == "POST":
        nome = request.form["nome"]
        formato = request.form["formato"]

        conexao = sqlite3.connect("vgc.db")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO times (nome, formato, id_usuario) VALUES (?, ?, ?)", (nome, formato, session["id_usuario"]))
        conexao.commit()
        conexao.close()
        return redirect("/times")
    
    return render_template("novo_time.html")

#ROTA REGRAS
@app.route("/times/<int:id_time>/pokemon/novo", methods=["GET", "POST"])
def novo_pokemon(id_time):
    if "id_usuario" not in session:
        return redirect("/login")
    
    conexao = sqlite3.connect("vgc.db")
    cursor = conexao.cursor()

    #confere se o time existe e pertence ao usuário logado
    cursor.execute("SELECT id, nome FROM times WHERE id = ? AND id_usuario = ?", (id_time, session["id_usuario"]))
    time = cursor.fetchone()
    if not time:
        conexao.close()
        return redirect("/times")
    
    if request.method == "POST":
        especie = request.form["especie"].strip()
        item = request.form["item"].strip()

        #busca os pokemons já existentes no time
        cursor.execute("SELECT especie, item FROM pokemons_do_time WHERE id_time = ?", (id_time,))
        atuais = cursor.fetchall()
        erro = None

        #regra 1 - maximo 6 pokemons
        if len(atuais) >= 6:
            erro = "Erro: Um time não pode ter mais de 6 pokémons."

        #regra 2 - não pode ter pokemons repetidos
        elif especie.lower() in [p[0].lower() for p in atuais]:
            erro = f"Erro (species clause): {especie} ja está no time."

        #regra 3 - não pode ter itens repetidos
        elif item and item.lower() in [p[1].lower() for p in atuais if p[1]]:
            erro = f"Erro (item clause): {item} ja está em uso no time."
        
        if erro:
            conexao.close()
            return render_template("novo_pokemon.html", time=time, mensagem=erro)
        
        cursor.execute(
            """INSERT INTO pokemons_do_time
               (id_time, especie, item, habilidade, natureza, tera_type,
                golpe1, golpe2, golpe3, golpe4)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id_time, especie, item,
             request.form["habilidade"], request.form["natureza"],
             request.form["tera_type"], request.form["golpe1"],
             request.form["golpe2"], request.form["golpe3"],
             request.form["golpe4"])
        )
        conexao.commit()
        conexao.close()
        return redirect(f"/times/{id_time}")
    
    conexao.close()
    return render_template("novo_pokemon.html", time=time, mensagem="")

#ROTA VISUALIZAR TIME
@app.route("/times/<int:id_time>")
def time_detalhe(id_time):
    if "id_usuario" not in session:
        return redirect("/login")
    
    conexao = sqlite3.connect("vgc.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome, formato FROM times WHERE id = ? AND id_usuario = ?", (id_time, session["id_usuario"]))
    time = cursor.fetchone()
    if not time:
        conexao.close()
        return redirect("/times")
    
    cursor.execute(
        """SELECT id, especie, item, habilidade, natureza, tera_type,
                  golpe1, golpe2, golpe3, golpe4
           FROM pokemons_do_time WHERE id_time = ?""",
        (id_time,)
    )
    pokemons = cursor.fetchall()
    conexao.close()

    return render_template("time_detalhe.html", time=time, pokemons=pokemons)

#DEBUG E RUNNING
if __name__ == "__main__":
    app.run(debug=True)
