import os
from locust import task, between, HttpUser
from cenarios.login import fazer_login

USUARIO_VALIDO = os.getenv("IEDUCAR_USER", "admin")
SENHA_VALIDA   = os.getenv("IEDUCAR_PASS", "admin")


class UsuarioConsultaTeste(HttpUser):
    host = os.getenv("TARGET_HOST", "http://host.docker.internal")
    wait_time = between(1, 3)
    network_timeout = 120.0
    connection_timeout = 120.0

    @task(40)
    def buscar_aluno_por_nome(self):
        """Busca alunos pelo nome via API."""
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta nome]")
        if not ok:
            return

        with self.client.get(
            "/intranet/api/?acao=get&resource=aluno-search&nome=Teste",
            catch_response=True,
            name="GET /api aluno-search [nome]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Busca por nome falhou — status {resp.status_code}")

    @task(40)
    def consultar_aluno_por_id(self):
        """Consulta dados completos de um aluno pelo ID."""
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta id]")
        if not ok:
            return

        with self.client.get(
            "/intranet/api/?acao=get&resource=aluno&id=3",
            catch_response=True,
            name="GET /api aluno [por id]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Consulta por ID falhou — status {resp.status_code}")

    @task(20)
    def consultar_matriculas_aluno(self):
        """Consulta matrículas de um aluno específico."""
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta matriculas]")
        if not ok:
            return

        with self.client.get(
            "/intranet/api/?acao=get&resource=matriculas&aluno_id=3",
            catch_response=True,
            name="GET /api matriculas [aluno]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Consulta matrículas falhou — status {resp.status_code}")