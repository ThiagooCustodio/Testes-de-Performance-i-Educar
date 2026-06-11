"""
Cenários e pesos:
  1. LoginSucesso   — POST de login com credenciais válidas        (peso 60)
  2. LoginFalha     — POST de login com credenciais inválidas      (peso 20)
  3. NavegacaoAluno — GET de listagem de alunos após autenticação  (peso 20)

  -  10 usuários → linha de base; comportamento esperado sem pressão.
  -  50 usuários → carga moderada; detecta primeiros gargalos.
  - 100 usuários → carga alta; revela saturação e degradação de resposta.
"""

import json
import os


from locust import HttpUser, task, between

class UsuarioLogin(HttpUser):

    host = "http://localhost"

    wait_time = between(1, 3)

    @task
    def acessar_login(self):
        self.client.get("/login")