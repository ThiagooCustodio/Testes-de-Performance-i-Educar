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
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta nome]")
        if not ok:
            return
        with self.client.get(
            "/module/Api/Aluno?oper=get&resource=aluno-search&query=Teste",
            catch_response=True,
            name="GET /module/Api/Aluno [aluno-search]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Busca por nome falhou — status {resp.status_code}")

    @task(40)
    def consultar_aluno_por_id(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta id]")
        if not ok:
            return
        with self.client.get(
            "/module/Api/Aluno?oper=get&resource=aluno&id=3",
            catch_response=True,
            name="GET /module/Api/Aluno [por id]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if not data.get("any_error_msg"):
                        resp.success()
                    else:
                        resp.failure("API retornou erro")
                except Exception:
                    resp.failure("Resposta inválida")
            else:
                resp.failure(f"Consulta por ID falhou — status {resp.status_code}")

    @task(20)
    def consultar_matriculas_aluno(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta matriculas]")
        if not ok:
            return
        with self.client.get(
            "/module/Api/Aluno?oper=get&resource=matriculas&aluno_id=3",
            catch_response=True,
            name="GET /module/Api/Aluno [matriculas]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if not data.get("any_error_msg"):
                        resp.success()
                    else:
                        resp.failure("API retornou erro")
                except Exception:
                    resp.failure("Resposta inválida")
            else:
                resp.failure(f"Consulta matrículas falhou — status {resp.status_code}")