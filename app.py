from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import iniciar_bd, execute_query, execute_one

app = Flask(__name__)
app.secret_key = 'igreja_secret_key_2024'

iniciar_bd()


def garantir_admin():
    try:    
        total = execute_one('SELECT COUNT(*) AS total FROM membros')
        if total and total['total'] > 0:
            return

        cargo = execute_one("SELECT id_cargo FROM cargos WHERE nome = %s", ('Pastor',))
        if not cargo:
            execute_query(
                "INSERT INTO cargos (nome, status, descricao) VALUES (%s, 'Ativo', %s)",
                ('Pastor', 'Liderança principal da igreja')
            )
            cargo = execute_one("SELECT id_cargo FROM cargos WHERE nome = %s", ('Pastor',))

        execute_query(
            """INSERT INTO membros (nome, cpf, email, celular, estado, senha, status, is_admin, cargo_id)
               VALUES (%s, %s, %s, %s, %s, %s, 'Ativo', 1, %s)""",
            ('Administrador', '000.000.000-00', 'admin@igreja.com',
             '(00) 00000-0000', 'SP', generate_password_hash('admin1234'), cargo['id_cargo'])
        )
        print('Admin criado: admin@igreja.com / admin1234')
    except Exception as e:
        print(f'Erro ao garantir admin: {e}')


garantir_admin()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=session.get('usuario'))


# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        usuario = execute_one(
            '''SELECT m.id_membro, m.nome, m.email, m.senha, m.status, m.is_admin,
                      c.nome AS cargo
               FROM membros AS m
               LEFT JOIN cargos AS c ON m.cargo_id = c.id_cargo
               WHERE m.email = %s''',
            (email,)
        )

        if not usuario or not check_password_hash(usuario['senha'], senha):
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('login'))

        if usuario['status'] != 'Ativo':
            flash('Acesso inativo. Contate o administrador.', 'warning')
            return redirect(url_for('login'))

        partes = usuario['nome'].split()
        iniciais = (partes[0][0] + partes[-1][0]).upper() if len(partes) > 1 else partes[0][:2].upper()

        session['usuario'] = {
            'id': usuario['id_membro'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'cargo': usuario['cargo'] or 'Membro',
            'iniciais': iniciais,
            'is_admin': usuario['is_admin'],
        }
        flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
        return redirect(url_for('home'))

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/home')
@login_required
def home():
    total_membros = execute_one('SELECT COUNT(*) AS t FROM membros WHERE status = "Ativo"')
    total_celulas = execute_one('SELECT COUNT(*) AS t FROM celulas WHERE status = "Ativa"')
    total_contribuicoes = execute_one(
        'SELECT COALESCE(SUM(valor),0) AS t FROM contribuicoes WHERE MONTH(data_pagamento) = MONTH(CURDATE()) AND YEAR(data_pagamento) = YEAR(CURDATE())'
    )
    ultimos = execute_query(
        '''SELECT m.nome, m.status, c.nome AS cargo, m.criado_em
           FROM membros AS m LEFT JOIN cargos AS c ON m.cargo_id = c.id_cargo
           ORDER BY m.criado_em DESC LIMIT 5''',
        fetch=True
    )
    return render_template('dashboard/home.html',
                           total_membros=total_membros['t'],
                           total_celulas=total_celulas['t'],
                           total_contribuicoes=total_contribuicoes['t'],
                           ultimos=ultimos)


# ── Membros ───────────────────────────────────────────────────────────────────

@app.route('/membros/listar')
@login_required
def membros_listar():
    sql = '''SELECT m.id_membro, m.nome, m.email, m.celular, m.status,
                    c.nome AS cargo, ce.nome AS celula
             FROM membros AS m
             LEFT JOIN cargos AS c ON m.cargo_id = c.id_cargo
             LEFT JOIN celulas AS ce ON m.celula_id = ce.id_celula
             ORDER BY m.nome ASC'''
    dados = execute_query(sql, fetch=True)
    return render_template('dashboard/membros/listar.html', dados=dados)


@app.route('/membros/cadastrar', methods=['GET', 'POST'])
@login_required
def membros_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip() or None
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email = request.form.get('email', '').strip() or None
        celular = request.form.get('celular', '').strip()
        cep = request.form.get('cep', '').strip()
        logradouro = request.form.get('logradouro', '').strip()
        numero = request.form.get('numero', '').strip()
        complemento = request.form.get('complemento', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()
        data_batismo = request.form.get('data_batismo', '').strip() or None
        data_ingresso = request.form.get('data_ingresso', '').strip() or None
        status = request.form.get('status', 'Ativo')
        cargo_id = request.form.get('cargo_id', '').strip() or None
        celula_id = request.form.get('celula_id', '').strip() or None
        observacoes = request.form.get('observacoes', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()

        if not all([nome, celular, senha]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('membros_cadastrar'))

        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('membros_cadastrar'))

        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('membros_cadastrar'))

        if email:
            existente = execute_one('SELECT id_membro FROM membros WHERE email = %s', (email,))
            if existente:
                flash('E-mail já cadastrado.', 'danger')
                return redirect(url_for('membros_cadastrar'))

        try:
            execute_query(
                '''INSERT INTO membros (nome, cpf, data_nascimento, email, celular,
                   cep, logradouro, numero, complemento, bairro, cidade, estado,
                   data_batismo, data_ingresso, status, cargo_id, celula_id,
                   observacoes, senha)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (nome, cpf, data_nascimento, email, celular,
                 cep, logradouro, numero, complemento, bairro, cidade, estado,
                 data_batismo, data_ingresso, status, cargo_id, celula_id,
                 observacoes, generate_password_hash(senha))
            )
            flash(f'Membro <b>{nome}</b> cadastrado com sucesso!', 'success')
            return redirect(url_for('membros_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'danger')
            return redirect(url_for('membros_cadastrar'))

    cargos = execute_query('SELECT id_cargo, nome FROM cargos WHERE status="Ativo"', fetch=True)
    celulas = execute_query('SELECT id_celula, nome FROM celulas WHERE status="Ativa"', fetch=True)
    return render_template('dashboard/membros/form.html',
                           titulo='Cadastrar Membro', modo='cadastrar',
                           item=None, cargos=cargos, celulas=celulas)


@app.route('/membros/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def membros_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip() or None
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email = request.form.get('email', '').strip() or None
        celular = request.form.get('celular', '').strip()
        cep = request.form.get('cep', '').strip()
        logradouro = request.form.get('logradouro', '').strip()
        numero = request.form.get('numero', '').strip()
        complemento = request.form.get('complemento', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()
        data_batismo = request.form.get('data_batismo', '').strip() or None
        data_ingresso = request.form.get('data_ingresso', '').strip() or None
        status = request.form.get('status', 'Ativo')
        cargo_id = request.form.get('cargo_id', '').strip() or None
        celula_id = request.form.get('celula_id', '').strip() or None
        observacoes = request.form.get('observacoes', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()

        if not all([nome, celular]):
            flash('Preencha os campos obrigatórios.', 'danger')
            return redirect(url_for('membros_alterar', id=id))

        if email:
            existente = execute_one(
                'SELECT id_membro FROM membros WHERE email = %s AND id_membro <> %s', (email, id)
            )
            if existente:
                flash('E-mail já cadastrado em outro membro.', 'danger')
                return redirect(url_for('membros_alterar', id=id))

        if senha:
            if senha != confirmar_senha:
                flash('As senhas não conferem.', 'danger')
                return redirect(url_for('membros_alterar', id=id))
            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
                return redirect(url_for('membros_alterar', id=id))

        try:
            if senha:
                execute_query(
                    '''UPDATE membros SET nome=%s, cpf=%s, data_nascimento=%s, email=%s, celular=%s,
                       cep=%s, logradouro=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s,
                       estado=%s, data_batismo=%s, data_ingresso=%s, status=%s, cargo_id=%s,
                       celula_id=%s, observacoes=%s, senha=%s WHERE id_membro=%s''',
                    (nome, cpf, data_nascimento, email, celular, cep, logradouro, numero,
                     complemento, bairro, cidade, estado, data_batismo, data_ingresso,
                     status, cargo_id, celula_id, observacoes, generate_password_hash(senha), id)
                )
            else:
                execute_query(
                    '''UPDATE membros SET nome=%s, cpf=%s, data_nascimento=%s, email=%s, celular=%s,
                       cep=%s, logradouro=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s,
                       estado=%s, data_batismo=%s, data_ingresso=%s, status=%s, cargo_id=%s,
                       celula_id=%s, observacoes=%s WHERE id_membro=%s''',
                    (nome, cpf, data_nascimento, email, celular, cep, logradouro, numero,
                     complemento, bairro, cidade, estado, data_batismo, data_ingresso,
                     status, cargo_id, celula_id, observacoes, id)
                )
            flash(f'Membro <b>{nome}</b> alterado com sucesso!', 'success')
            return redirect(url_for('membros_listar'))
        except Exception as e:
            flash(f'Erro ao alterar: {e}', 'danger')
            return redirect(url_for('membros_alterar', id=id))

    item = execute_one('SELECT * FROM membros WHERE id_membro = %s', (id,))
    if not item:
        flash('Membro não encontrado.', 'danger')
        return redirect(url_for('membros_listar'))
    cargos = execute_query('SELECT id_cargo, nome FROM cargos WHERE status="Ativo"', fetch=True)
    celulas = execute_query('SELECT id_celula, nome FROM celulas WHERE status="Ativa"', fetch=True)
    return render_template('dashboard/membros/form.html',
                           titulo='Alterar Membro', modo='alterar',
                           item=item, cargos=cargos, celulas=celulas)


@app.route('/membros/visualizar/<int:id>')
@login_required
def membros_visualizar(id):
    item = execute_one(
        '''SELECT m.*, c.nome AS cargo, ce.nome AS celula
           FROM membros AS m
           LEFT JOIN cargos AS c ON m.cargo_id = c.id_cargo
           LEFT JOIN celulas AS ce ON m.celula_id = ce.id_celula
           WHERE m.id_membro = %s''', (id,)
    )
    if not item:
        flash('Membro não encontrado.', 'danger')
        return redirect(url_for('membros_listar'))

    contribuicoes = execute_query(
        'SELECT * FROM contribuicoes WHERE membro_id = %s ORDER BY data_pagamento DESC LIMIT 10',
        (id,), fetch=True
    )
    return render_template('dashboard/membros/visualizar.html', item=item, contribuicoes=contribuicoes)


@app.route('/membros/excluir/<int:id>', methods=['POST'])
@login_required
def membros_excluir(id):
    try:
        execute_query('DELETE FROM membros WHERE id_membro = %s', (id,))
        flash('Membro excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {e}', 'danger')
    return redirect(url_for('membros_listar'))


# ── Cargos ────────────────────────────────────────────────────────────────────

@app.route('/cargos/listar')
@login_required
def cargos_listar():
    dados = execute_query('SELECT * FROM cargos ORDER BY nome ASC', fetch=True)
    return render_template('dashboard/cargos/listar.html', dados=dados)


@app.route('/cargos/cadastrar', methods=['GET', 'POST'])
@login_required
def cargos_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('cargos_cadastrar'))
        try:
            execute_query(
                'INSERT INTO cargos (nome, status, descricao) VALUES (%s, %s, %s)',
                (nome, status, descricao)
            )
            flash(f'Cargo <b>{nome}</b> cadastrado com sucesso!', 'success')
            return redirect(url_for('cargos_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'danger')
            return redirect(url_for('cargos_cadastrar'))
    return render_template('dashboard/cargos/form.html', titulo='Cadastrar Cargo', modo='cadastrar', item=None)


@app.route('/cargos/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def cargos_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('cargos_alterar', id=id))
        try:
            execute_query(
                'UPDATE cargos SET nome=%s, status=%s, descricao=%s WHERE id_cargo=%s',
                (nome, status, descricao, id)
            )
            flash(f'Cargo <b>{nome}</b> alterado com sucesso!', 'success')
            return redirect(url_for('cargos_listar'))
        except Exception as e:
            flash(f'Erro ao alterar: {e}', 'danger')
            return redirect(url_for('cargos_alterar', id=id))
    item = execute_one('SELECT * FROM cargos WHERE id_cargo = %s', (id,))
    if not item:
        flash('Cargo não encontrado.', 'danger')
        return redirect(url_for('cargos_listar'))
    return render_template('dashboard/cargos/form.html', titulo='Alterar Cargo', modo='alterar', item=item)


@app.route('/cargos/excluir/<int:id>', methods=['POST'])
@login_required
def cargos_excluir(id):
    try:
        execute_query('DELETE FROM cargos WHERE id_cargo = %s', (id,))
        flash('Cargo excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir (verifique se há membros vinculados): {e}', 'danger')
    return redirect(url_for('cargos_listar'))


# ── Células ───────────────────────────────────────────────────────────────────

@app.route('/celulas/listar')
@login_required
def celulas_listar():
    sql = '''SELECT ce.*, COUNT(m.id_membro) AS total_membros
             FROM celulas AS ce
             LEFT JOIN membros AS m ON m.celula_id = ce.id_celula AND m.status = "Ativo"
             GROUP BY ce.id_celula ORDER BY ce.nome ASC'''
    dados = execute_query(sql, fetch=True)
    return render_template('dashboard/celulas/listar.html', dados=dados)


@app.route('/celulas/cadastrar', methods=['GET', 'POST'])
@login_required
def celulas_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        lider = request.form.get('lider', '').strip()
        dia_semana = request.form.get('dia_semana', '').strip()
        horario = request.form.get('horario', '').strip() or None
        endereco = request.form.get('endereco', '').strip()
        status = request.form.get('status', 'Ativa')
        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('celulas_cadastrar'))
        try:
            execute_query(
                'INSERT INTO celulas (nome, lider, dia_semana, horario, endereco, status) VALUES (%s,%s,%s,%s,%s,%s)',
                (nome, lider, dia_semana, horario, endereco, status)
            )
            flash(f'Célula <b>{nome}</b> cadastrada com sucesso!', 'success')
            return redirect(url_for('celulas_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'danger')
            return redirect(url_for('celulas_cadastrar'))
    return render_template('dashboard/celulas/form.html', titulo='Cadastrar Célula', modo='cadastrar', item=None)


@app.route('/celulas/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def celulas_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        lider = request.form.get('lider', '').strip()
        dia_semana = request.form.get('dia_semana', '').strip()
        horario = request.form.get('horario', '').strip() or None
        endereco = request.form.get('endereco', '').strip()
        status = request.form.get('status', 'Ativa')
        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('celulas_alterar', id=id))
        try:
            execute_query(
                'UPDATE celulas SET nome=%s, lider=%s, dia_semana=%s, horario=%s, endereco=%s, status=%s WHERE id_celula=%s',
                (nome, lider, dia_semana, horario, endereco, status, id)
            )
            flash(f'Célula <b>{nome}</b> alterada com sucesso!', 'success')
            return redirect(url_for('celulas_listar'))
        except Exception as e:
            flash(f'Erro ao alterar: {e}', 'danger')
            return redirect(url_for('celulas_alterar', id=id))
    item = execute_one('SELECT * FROM celulas WHERE id_celula = %s', (id,))
    if not item:
        flash('Célula não encontrada.', 'danger')
        return redirect(url_for('celulas_listar'))
    return render_template('dashboard/celulas/form.html', titulo='Alterar Célula', modo='alterar', item=item)


@app.route('/celulas/excluir/<int:id>', methods=['POST'])
@login_required
def celulas_excluir(id):
    try:
        execute_query('DELETE FROM celulas WHERE id_celula = %s', (id,))
        flash('Célula excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {e}', 'danger')
    return redirect(url_for('celulas_listar'))


# ── Contribuições ─────────────────────────────────────────────────────────────

@app.route('/contribuicoes/listar')
@login_required
def contribuicoes_listar():
    sql = '''SELECT co.*, m.nome AS membro
             FROM contribuicoes AS co
             INNER JOIN membros AS m ON co.membro_id = m.id_membro
             ORDER BY co.data_pagamento DESC'''
    dados = execute_query(sql, fetch=True)
    total = execute_one('SELECT COALESCE(SUM(valor),0) AS total FROM contribuicoes')
    return render_template('dashboard/contribuicoes/listar.html', dados=dados, total=total['total'])


@app.route('/contribuicoes/cadastrar', methods=['GET', 'POST'])
@login_required
def contribuicoes_cadastrar():
    if request.method == 'POST':
        membro_id = request.form.get('membro_id', '').strip()
        tipo = request.form.get('tipo', '').strip()
        valor = request.form.get('valor', '').strip()
        data_pagamento = request.form.get('data_pagamento', '').strip()
        forma_pagamento = request.form.get('forma_pagamento', 'Dinheiro')
        observacao = request.form.get('observacao', '').strip()

        if not all([membro_id, tipo, valor, data_pagamento]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('contribuicoes_cadastrar'))
        try:
            execute_query(
                '''INSERT INTO contribuicoes (membro_id, tipo, valor, data_pagamento, forma_pagamento, observacao)
                   VALUES (%s,%s,%s,%s,%s,%s)''',
                (membro_id, tipo, valor, data_pagamento, forma_pagamento, observacao)
            )
            flash('Contribuição registrada com sucesso!', 'success')
            return redirect(url_for('contribuicoes_listar'))
        except Exception as e:
            flash(f'Erro ao registrar: {e}', 'danger')
            return redirect(url_for('contribuicoes_cadastrar'))

    membros = execute_query(
        'SELECT id_membro, nome FROM membros WHERE status="Ativo" ORDER BY nome', fetch=True
    )
    return render_template('dashboard/contribuicoes/form.html',
                           titulo='Registrar Contribuição', item=None, membros=membros)


@app.route('/contribuicoes/excluir/<int:id>', methods=['POST'])
@login_required
def contribuicoes_excluir(id):
    try:
        execute_query('DELETE FROM contribuicoes WHERE id_contribuicao = %s', (id,))
        flash('Contribuição excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {e}', 'danger')
    return redirect(url_for('contribuicoes_listar'))


@app.route('/equipe')
@login_required
def equipe():
    return render_template('dashboard/equipe.html')


if __name__ == '__main__':
    app.run(debug=True)
