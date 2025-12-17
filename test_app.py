# test_app.py
import pytest
from app import app, db, Tarefa

# Fixture: Configura o ambiente de teste com DB em memória


@pytest.fixture(scope='module')
def client():
    # Configuração para testes
    app.config['TESTING'] = True
    # DB temporário
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Cria as tabelas
            yield client     # Executa os testes
            db.drop_all()    # Limpa o DB após os testes

# Teste 1: Verifica se a página principal carrega


def test_index_carregamento(client):
    """Testa se a rota principal retorna status 200 e conteúdo esperado."""
    response = client.get('/')

    # Verifica status HTTP (Confiabilidade - ISO/IEC 25010)
    assert response.status_code == 200

    # Verifica conteúdo da página (Acessibilidade - WCAG)
    assert b"Lista de Tarefas Acess" in response.data
    assert b"Nova Tarefa:" in response.data

# Teste 2: Adicionar uma tarefa via formulário


def test_adicionar_tarefa(client):
    """Testa o funcionamento do formulário de adição de tarefas."""
    # Dados de teste
    titulo_teste = "Tarefa de Teste 123"

    # Simula envio de formulário POST
    response = client.post('/adicionar',
                           data={'titulo': titulo_teste},
                           follow_redirects=True)

    # Verifica redirecionamento e status
    assert response.status_code == 200

    # Verifica se a tarefa foi adicionada ao banco
    with app.app_context():
        tarefa = Tarefa.query.filter_by(titulo=titulo_teste).first()
        assert tarefa is not None
        assert tarefa.titulo == titulo_teste
        assert tarefa.concluida is False

# Teste 3: Alternar estado de conclusão de uma tarefa


def test_alternar_conclusao(client):
    """Testa a funcionalidade de marcar/desmarcar tarefa como concluída."""
    # Primeiro cria uma tarefa
    with app.app_context():
        tarefa = Tarefa(titulo="Tarefa para alternar")
        db.session.add(tarefa)
        db.session.commit()
        tarefa_id = tarefa.id

    # Marca como concluída
    response = client.post(f'/alternar/{tarefa_id}', follow_redirects=True)
    assert response.status_code == 200

    # Verifica se foi alterada no banco
    with app.app_context():
        tarefa = Tarefa.query.get(tarefa_id)
        assert tarefa.concluida

    # Desmarca
    response = client.post(f'/alternar/{tarefa_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        tarefa = Tarefa.query.get(tarefa_id)
        assert tarefa.concluida is False

# Teste 4: Excluir uma tarefa


def test_excluir_tarefa(client):
    """Testa a funcionalidade de exclusão de tarefas (LGPD - Direito de Exclusão)."""
    # Cria uma tarefa
    with app.app_context():
        tarefa = Tarefa(titulo="Tarefa para excluir")
        db.session.add(tarefa)
        db.session.commit()
        tarefa_id = tarefa.id

    # Exclui a tarefa
    response = client.post(f'/deletar/{tarefa_id}', follow_redirects=True)
    assert response.status_code == 200

    # Verifica se foi removida do banco
    with app.app_context():
        tarefa = Tarefa.query.get(tarefa_id)
        assert tarefa is None

# Teste 5: Validação de entrada - título vazio


def test_adicionar_tarefa_vazia(client):
    """Testa a validação quando se tenta adicionar tarefa sem título."""
    # PRIMEIRO limpa o banco para este teste
    with app.app_context():
        Tarefa.query.delete()
        db.session.commit()

    response = client.post('/adicionar',
                           data={'titulo': ''},
                           follow_redirects=True)

    assert response.status_code == 200

    # Verifica que NÃO criou tarefa no banco
    with app.app_context():
        count = Tarefa.query.count()
        assert count == 0  # Agora deve ser 0

# Teste 6: Teste de integração completo


def test_fluxo_completo(client):
    """Testa um fluxo completo: adicionar -> marcar como concluída -> excluir."""
    # Adiciona
    client.post(
        '/adicionar',
        data={
            'titulo': 'Tarefa Fluxo'},
        follow_redirects=True)

    with app.app_context():
        tarefa = Tarefa.query.filter_by(titulo='Tarefa Fluxo').first()
        assert tarefa is not None
        tarefa_id = tarefa.id

    # Marca como concluída
    client.post(f'/alternar/{tarefa_id}', follow_redirects=True)

    with app.app_context():
        tarefa = Tarefa.query.get(tarefa_id)
        assert tarefa.concluida

    # Exclui
    client.post(f'/deletar/{tarefa_id}', follow_redirects=True)

    with app.app_context():
        tarefa = Tarefa.query.get(tarefa_id)
        assert tarefa is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
