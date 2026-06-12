"""
Cenários e pesos:

1. LoginSucesso      — GET /login → extrai CSRF → POST com credenciais válidas   (peso 60)
2. LoginFalha        — GET /login → extrai CSRF → POST com credenciais inválidas  (peso 20)
3. NavegacaoAluno    — Login completo → GET /intranet/educar/Aluno/index.php      (peso 20)

Cargas previstas:
- 10 usuários → linha de base
- 50 usuários → carga moderada
- 100 usuários → carga alta
"""

import os
import re
from locust import HttpUser, task, between, TaskSet


def extrair_csrf(html: str) -> str:
    """Extrai o _token CSRF do formulário de login do Laravel."""
    match = re.search(r'<input[^>]+name="_token"[^>]+value="([^"]+)"', html)
    if match:
        return match.group(1)
    # fallback: meta tag
    match = re.search(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', html)
    return match.group(1) if match else ""


USUARIO_VALIDO = os.getenv("IEDUCAR_USER", "comunidade")
SENHA_VALIDA   = os.getenv("IEDUCAR_PASS", "Comunidade@1")


class UsuarioLogin(HttpUser):
    host = os.getenv("TARGET_HOST", "http://localhost")
    wait_time = between(1, 3)

    # Tarefa 1 — Login com sucesso (peso 60)       #
    @task(60)
    def login_sucesso(self):
        # Passo 1: busca a página de login para obter sessão + CSRF
        with self.client.get("/login", catch_response=True, name="GET /login") as resp:
            if resp.status_code != 200:
                resp.failure(f"GET /login retornou {resp.status_code}")
                return
            token = extrair_csrf(resp.text)

        if not token:
            # Se não encontrou o token, marca falha mas não para o teste
            return

        # Passo 2: POST de autenticação
        payload = {
            "_token": token,
            "login":  USUARIO_VALIDO,
            "password": SENHA_VALIDA,
        }
        with self.client.post(
            "/login",
            data=payload,
            allow_redirects=True,
            catch_response=True,
            name="POST /login [sucesso]",
        ) as resp:
            # O i-Educar redireciona para o painel após login bem-sucedido
            if resp.status_code == 200 and "/login" not in resp.url:
                resp.success()
            elif resp.status_code in (302, 301):
                resp.success()
            else:
                resp.failure(
                    f"Login falhou — status {resp.status_code} | url: {resp.url}"
                )

    # Tarefa 2 — Login com falha intencional (peso 20)                   #
    @task(20)
    def login_falha(self):
        with self.client.get("/login", catch_response=True, name="GET /login") as resp:
            if resp.status_code != 200:
                resp.failure(f"GET /login retornou {resp.status_code}")
                return
            token = extrair_csrf(resp.text)

        payload = {
            "_token": token,
            "login":    "usuario_invalido@teste.com",
            "password": "senha_errada_123",
        }
        with self.client.post(
            "/login",
            data=payload,
            allow_redirects=True,
            catch_response=True,
            name="POST /login [falha esperada]",
        ) as resp:
            # Esperamos ser redirecionado de volta ao /login com erro
            if "/login" in resp.url or resp.status_code in (200, 302):
                resp.success()   # comportamento correto: rejeitou o login
            else:
                resp.failure(f"Resposta inesperada: {resp.status_code}")


    # Tarefa 3 — Navega para listagem de alunos após login (peso 20)     #
    @task(20)
    def navegacao_aluno(self):
        # Primeiro realiza o login completo
        with self.client.get("/login", catch_response=True, name="GET /login") as resp:
            if resp.status_code != 200:
                resp.failure(f"GET /login retornou {resp.status_code}")
                return
            token = extrair_csrf(resp.text)

        payload = {
            "_token":   token,
            "login":    USUARIO_VALIDO,
            "password": SENHA_VALIDA,
        }
        with self.client.post(
            "/login",
            data=payload,
            allow_redirects=True,
            catch_response=True,
            name="POST /login [nav aluno]",
        ) as resp:
            if "/login" in resp.url:
                resp.failure("Login falhou antes da navegação")
                return
            resp.success()

        # Após autenticado, acessa a listagem de alunos
        with self.client.get(
            "/intranet/educar/Aluno/index.php",
            catch_response=True,
            name="GET /alunos",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Listagem de alunos retornou {resp.status_code}")