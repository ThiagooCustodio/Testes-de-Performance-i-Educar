import os
import random
from locust import task, between, HttpUser
from cenarios.login import fazer_login

USUARIO_VALIDO = os.getenv("IEDUCAR_USER", "admin")
SENHA_VALIDA   = os.getenv("IEDUCAR_PASS", "admin")


class UsuarioNavegacaoTeste(HttpUser):
    host = os.getenv("TARGET_HOST", "http://host.docker.internal")
    wait_time = between(2, 8)  # espera maior — simula usuário lendo a tela
    network_timeout = 120.0
    connection_timeout = 120.0

    # Páginas que o usuário pode visitar, com peso simulando frequência de acesso
    _paginas = [
        # (url, nome, peso)
        ("/intranet/index.php",                          "dashboard",         5),
        ("/intranet/educar_pessoas_index.php",           "pessoas",           4),
        ("/intranet/educar_enderecamento_index.php",     "enderecamento",     3),
        ("/intranet/educar_configuracoes_index.php",     "configuracoes",     2),
        ("/intranet/educar_exportacao_usuarios.php",     "exportacao",        1),
    ]

    def _visitar_pagina(self, url, nome):
        with self.client.get(
            url,
            catch_response=True,
            name=f"GET /intranet [{nome}]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
                return True
            elif resp.status_code in (301, 302):
                # Redirect pode ser normal em algumas páginas
                resp.success()
                return True
            else:
                resp.failure(f"Página {nome} falhou — status {resp.status_code}")
                return False

    @task
    def navegar(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [navegacao]")
        if not ok:
            return

        # Sempre começa pelo dashboard
        self._visitar_pagina("/intranet/index.php", "dashboard")

        # Visita entre 2 e 5 páginas aleatórias, simulando navegação livre
        urls     = [p[0] for p in self._paginas]
        nomes    = [p[1] for p in self._paginas]
        pesos    = [p[2] for p in self._paginas]
        total    = random.randint(2, 5)
        escolhas = random.choices(range(len(self._paginas)), weights=pesos, k=total)

        for idx in escolhas:
            self._visitar_pagina(urls[idx], nomes[idx])