import os
import uuid
from locust import task, between, HttpUser
from cenarios.login import fazer_login

USUARIO_VALIDO = os.getenv("IEDUCAR_USER", "admin")
SENHA_VALIDA   = os.getenv("IEDUCAR_PASS", "admin")


class UsuarioAlunoTeste(HttpUser):
    host = os.getenv("TARGET_HOST", "http://host.docker.internal")
    wait_time = between(1, 3)
    network_timeout = 120.0
    connection_timeout = 120.0

    def _criar_pessoa(self):
        nome = f"Aluno Teste {uuid.uuid4().hex[:8].upper()}"
        with self.client.post(
            "/intranet/api/",
            data={
                "acao": "post",
                "resource": "pessoa",
                "nome": nome,
                "sexo": "M",
                "datanasc": "01/01/2000",
            },
            allow_redirects=False,
            catch_response=True,
            name="POST /api pessoa [criar]",
            timeout=60,
        ) as resp:
            if resp.status_code in (200, 302):
                try:
                    pessoa_id = resp.json().get("pessoa_id")
                    if pessoa_id:
                        resp.success()
                        return pessoa_id
                except Exception:
                    pass
                resp.failure("pessoa_id não retornado")
            else:
                resp.failure(f"Criar pessoa falhou — status {resp.status_code}")
        return None

    def _criar_aluno(self, pessoa_id):
        with self.client.post(
            "/intranet/api/",
            data={
                "acao": "post",
                "resource": "aluno",
                "pessoa_id": pessoa_id,
                "tipo_responsavel": "mae",
                "tipo_transporte": "nenhum",
            },
            allow_redirects=False,
            catch_response=True,
            name="POST /api aluno [inserir]",
            timeout=60,
        ) as resp:
            if resp.status_code in (200, 302):
                try:
                    if resp.json().get("id"):
                        resp.success()
                        return True
                except Exception:
                    pass
                resp.failure("id do aluno não retornado")
            else:
                resp.failure(f"Criar aluno falhou — status {resp.status_code}")
        return False

    @task(60)
    def cadastrar_aluno(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [cadastro aluno]")
        if not ok:
            return
        pessoa_id = self._criar_pessoa()
        if not pessoa_id:
            return
        self._criar_aluno(pessoa_id)

    @task(40)
    def consultar_alunos(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta]")
        if not ok:
            return
        with self.client.get(
            "/intranet/api/?acao=get&resource=aluno-search&nome=Teste",
            catch_response=True,
            name="GET /api aluno [consultar]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Consulta retornou {resp.status_code}")