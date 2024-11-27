from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = 'sala12345'

# Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'  # Coloque sua senha aqui
app.config['MYSQL_DB'] = 'doacao_comida'

mysql = MySQL(app)

# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Lista de tabelas a verificar
        tabelas = [
            {'nome': 'usuarios', 'tipo': 'usuario', 'senha_coluna': 2},  # A senha está na coluna 2 (usuarios)
            {'nome': 'restaurante', 'tipo': 'restaurante', 'senha_coluna': 5},  # A senha está na coluna 5 (restaurante)
            {'nome': 'ong', 'tipo': 'ong', 'senha_coluna': 6}  # A senha está na coluna 6 (ong)
        ]

        cur = mysql.connection.cursor()
        for tabela in tabelas:
            query = f"SELECT * FROM {tabela['nome']} WHERE email = %s"
            cur.execute(query, (email,))
            usuario = cur.fetchone()

            if usuario:
                senha_db = usuario[tabela['senha_coluna']]

                # Verifica se a senha está correta (comparação simples)
                if senha_db == senha:
                    session['tipo'] = tabela['tipo']
                    session['nome'] = usuario[1]  # Nome está na coluna 1
                    session['email'] = usuario[2]  # Email está na coluna 2
                    session['usuario_id'] = usuario[0]  # ID está na coluna 0
                    flash('Login realizado com sucesso!', 'success')
                    return redirect('/area_restrita')

        cur.close()
        flash('Email ou senha inválidos!', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Limpa todos os dados da sessão
    return redirect('/')

# Área restrita para gerenciamento de doações
@app.route('/area_restrita')
def area_restrita():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doacoes")
    doacoes = cur.fetchall()
    cur.close()
    return render_template('area_restrita.html', doacoes=doacoes)

# Cadastro de pessoa física
@app.route('/pessoa_fisica', methods=['GET', 'POST'])
def pessoa_fisica():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        localizacao = request.form['localizacao']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pessoa_fisica (nome, email, telefone, localizacao) VALUES (%s, %s, %s, %s)",
                    (nome, email, telefone, localizacao))
        mysql.connection.commit()
        cur.close()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect('/')

    return render_template('pessoa_fisica.html')

# Cadastro de restaurante
@app.route('/restaurante', methods=['GET', 'POST'])
def restaurante():
    if request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        endereco = request.form['endereco']
        email = request.form['email']
        senha = (request.form['senha'])
        telefone = request.form['telefone']

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO restaurante (nome, cnpj, endereco, email, senha, telefone) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, cnpj, endereco, email, senha, telefone))
            mysql.connection.commit()
            flash('Cadastro realizado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro no cadastro: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect('/')
    return render_template('restaurante.html')

# Cadastro de ONG
@app.route('/ong', methods=['GET', 'POST'])
def ong():
    if request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        responsavel = request.form['responsavel']
        email = request.form['email']
        senha = (request.form['senha'])
        telefone = request.form['telefone']

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO ong (nome, cnpj, responsavel, email, senha, telefone) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, cnpj, responsavel, email, senha, telefone))
            mysql.connection.commit()
            flash('Cadastro realizado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro no cadastro: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect('/')
    return render_template('ong.html')

# Rota para adicionar doações
@app.route('/doar', methods=['GET', 'POST'])
def doar():
    # Verifique se o usuário está logado e se o tipo é permitido
    if 'tipo' not in session or session['tipo'] not in ['admin', 'restaurante']:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect('/area_restrita')

    if request.method == 'POST':
        alimento = request.form['alimento']
        quantidade = request.form['quantidade']
        descricao = request.form['descricao']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO doacoes (alimento, quantidade, descricao, usuario_id) VALUES (%s, %s, %s, %s)",
                (alimento, quantidade, descricao, session.get('usuario_id'))
            )
            mysql.connection.commit()
            cur.close()

            flash('Doação cadastrada com sucesso!', 'success')
            return redirect('/area_restrita')
        except Exception as e:
            flash(f'Erro ao cadastrar doação: {str(e)}', 'danger')
            return render_template('doar.html')

    return render_template('doar.html')



# Rota para notificar pessoas sobre doações
@app.route('/notificar', methods=['POST'])
def notificar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM pessoa_fisica")
    emails = cur.fetchall()
    cur.close()

    # Simulação de envio de notificações (apenas para demonstração)
    for email in emails:
        print(f"Notificação enviada para: {email[0]}")

    flash('Notificações enviadas com sucesso!', 'success')
    return redirect('/area_restrita')

@app.route('/meus-dados', methods=['GET', 'POST'])
def meus_dados():
    restaurante_id = session.get('restaurante_id')  # Certifique-se de salvar o ID no login
    if not restaurante_id:
        flash('Faça login para acessar esta página.', 'danger')
        return redirect('/login')

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Atualiza os dados no banco de dados
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        endereco = request.form['endereco']
        email = request.form['email']
        telefone = request.form['telefone']
        cur.execute("""
            UPDATE restaurante 
            SET nome=%s, cnpj=%s, endereco=%s, email=%s, telefone=%s 
            WHERE id=%s
        """, (nome, cnpj, endereco, email, telefone, restaurante_id))
        mysql.connection.commit()
        flash('Dados atualizados com sucesso!', 'success')
    
    # Busca os dados atuais do restaurante
    cur.execute("SELECT nome, cnpj, endereco, email, telefone FROM restaurante WHERE id = %s", (restaurante_id,))
    dados = cur.fetchone()
    cur.close()

    return render_template('meus_dados.html', dados=dados)

@app.route('/criar-alerta', methods=['GET', 'POST'])
def criar_alerta():
    restaurante_id = session.get('restaurante_id')  # Certifique-se de salvar o ID no login
    if not restaurante_id:
        flash('Faça login para acessar esta página.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        data = request.form['data']
        hora = request.form['hora']
        localizacao = request.form['localizacao']
        numero = request.form['numero']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO alertas (restaurante_id, tipo, descricao, data, hora, localizacao, numero) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (restaurante_id, tipo, descricao, data, hora, localizacao, numero))
        mysql.connection.commit()
        cur.close()
        flash('Alerta criado com sucesso!', 'success')
        return redirect('/acesso-restaurante')

    return render_template('criar_alerta.html')

@app.route('/historico-doacoes')
def historico_doacoes():
    restaurante_id = session.get('restaurante_id')
    if not restaurante_id:
        flash('Faça login para acessar esta página.', 'danger')
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT tipo, descricao, data, hora 
        FROM alertas 
        WHERE restaurante_id = %s
        ORDER BY data DESC, hora DESC
    """, (restaurante_id,))
    doacoes = cur.fetchall()
    cur.close()

    return render_template('historico_doacoes.html', doacoes=doacoes)


if __name__ == '__main__':
    app.run(debug=True)
