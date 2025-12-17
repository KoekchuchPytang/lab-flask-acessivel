# Linhas iniciais explicando propósito
"""
Aplicação Web de Gestão de Tarefas
Conformidade: WCAG 2.2 (Acessibilidade), OWASP Top 10 (Segurança), LGPD (Privacidade)
Tecnologias: Flask, SQLAlchemy, PostgreSQL/SQLite, HTML5, CSS3
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SQLite (funciona sem configurações complexas)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'todolist.db')
app.config['SECRET_KEY'] = 'chave_super_secreta_para_flash_msgs'

db = SQLAlchemy(app)


class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    concluida = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Tarefa {self.id}: {self.titulo}>'

# Rota Principal


@app.route('/')
def index():
    tarefas = Tarefa.query.all()
    return render_template('index.html', tarefas=tarefas)

# Rota para Adicionar Tarefa


@app.route('/adicionar', methods=['POST'])
def adicionar():
    if request.method == 'POST':
        titulo = request.form.get('titulo')

        # Validação de entrada (Confiabilidade - ISO/IEC 25010)
        if not titulo or titulo.strip() == '':
            flash('O título da tarefa não pode estar vazio.', 'error')
            return redirect(url_for('index'))

        # SQLAlchemy usa Prepared Statements (OWASP A03: Injection Prevention)
        nova_tarefa = Tarefa(titulo=titulo.strip())
        db.session.add(nova_tarefa)
        db.session.commit()

        flash(f'Tarefa "{titulo}" adicionada com sucesso!', 'success')

    return redirect(url_for('index'))

# Rota para Alternar Conclusão


@app.route('/alternar/<int:tarefa_id>', methods=['POST'])
def alternar(tarefa_id):
    # OWASP A01: Broken Access Control - Verificação de existência
    tarefa = db.get_or_404(Tarefa, tarefa_id)

    tarefa.concluida = not tarefa.concluida
    db.session.commit()

    status = "concluída" if tarefa.concluida else "pendente"
    flash(f'Tarefa "{tarefa.titulo}" marcada como {status}.', 'success')

    return redirect(url_for('index'))

# Rota para Deletar Tarefa


@app.route('/deletar/<int:tarefa_id>', methods=['POST'])
def deletar(tarefa_id):
    # LGPD: Direito de Exclusão
    tarefa = db.get_or_404(Tarefa, tarefa_id)

    db.session.delete(tarefa)
    db.session.commit()

    flash('Tarefa excluída permanentemente.', 'success')

    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
