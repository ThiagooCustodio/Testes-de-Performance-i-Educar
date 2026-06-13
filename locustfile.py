import os
from locust import HttpUser, task, between

USUARIO_VALIDO = os.getenv("IEDUCAR_USER", "admin")
SENHA_VALIDA   = os.getenv("IEDUCAR_PASS", "admin")


class UsuarioLogin(HttpUser):
    host = os.getenv("TARGET_HOST", "http://host.docker.internal")
    wait_time = between(1, 3)
    network_timeout = 120.0
    connection_timeout = 120.0

    def _fazer_login(self, usuario, senha, nome_tarefa):
        with self.client.get("/login", catch_response=True, name="GET /login", timeout=30) as resp:
            if resp.status_code != 200:
                resp.failure(f"GET /login retornou {resp.status_code}")
                return False

        with self.client.post(
            "/login",
            data={"login": usuario, "password": senha},
            allow_redirects=False,
            catch_response=True,
            name=nome_tarefa,
            timeout=60,
        ) as resp:
            if resp.status_code == 302:
                resp.success()
                return True
            else:
                resp.failure(f"Login falhou — status {resp.status_code} | url: {resp.url}")
                return False

    @task(60)
    def login_sucesso(self):
        self._fazer_login(USUARIO_VALIDO, SENHA_VALIDA, "POST /login [sucesso]")

    @task(20)
    def login_falha(self):
        with self.client.get("/login", catch_response=True, name="GET /login", timeout=30) as resp:
            if resp.status_code != 200:
                resp.failure(f"GET /login retornou {resp.status_code}")
                return

        with self.client.post(
            "/login",
            data={"login": "usuario_invalido", "password": "senha_errada"},
            allow_redirects=False,
            catch_response=True,
            name="POST /login [falha esperada]",
            timeout=60,
        ) as resp:
            if resp.status_code == 302:
                resp.success()
            else:
                resp.failure(f"Resposta inesperada: {resp.status_code}")

    @task(20)
    def navegacao_aluno(self):
        ok = self._fazer_login(USUARIO_VALIDO, SENHA_VALIDA, "POST /login [nav aluno]")
        if not ok:
            return

        with self.client.get(
            "/intranet/educar/Aluno/index.php",
            catch_response=True,
            name="GET /alunos",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Listagem de alunos retornou {resp.status_code}")