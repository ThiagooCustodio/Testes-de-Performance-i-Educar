import os
from locust import task, between, HttpUser
from cenarios.login import fazer_login

USUARIO_VALIDO  = os.getenv("IEDUCAR_USER", "admin")
SENHA_VALIDA    = os.getenv("IEDUCAR_PASS", "admin")
COD_INSTITUICAO = os.getenv("IEDUCAR_COD_INSTITUICAO", "1")


class UsuarioExportacaoTeste(HttpUser):
    host = os.getenv("TARGET_HOST", "http://host.docker.internal")
    wait_time = between(1, 3)
    network_timeout = 120.0
    connection_timeout = 120.0

    def _navegar_configuracoes(self):
        with self.client.get(
            "/intranet/educar_configuracoes_index.php",
            catch_response=True,
            name="GET /intranet [configuracoes]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
                return True
            else:
                resp.failure(f"Configurações falhou — status {resp.status_code}")
                return False

    def _abrir_exportacao(self):
        with self.client.get(
            "/intranet/educar_exportacao_usuarios.php",
            catch_response=True,
            name="GET /intranet [exportacao_usuarios]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
                return True
            else:
                resp.failure(f"Abrir exportação falhou — status {resp.status_code}")
                return False

    def _buscar_escolas(self):
        """AJAX ao selecionar a instituição no dropdown."""
        with self.client.get(
            f"/module/Api/escola?oper=get&resource=escolas-para-selecao&instituicao={COD_INSTITUICAO}",
            catch_response=True,
            name="GET /module/Api/escola [escolas-para-selecao]",
            timeout=30,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if not data.get("any_error_msg"):
                        resp.success()
                        return True
                    else:
                        resp.failure(f"API retornou erro: {data.get('msgs')}")
                        return False
                except Exception:
                    resp.failure("Resposta não é JSON válido")
                    return False
            else:
                resp.failure(f"Buscar escolas falhou — status {resp.status_code}")
                return False

    def _exportar_dados(self):
        """AJAX disparado pelo botão Exportar."""
        with self.client.get(
            "/module/Api/UsuarioExport",
            params={
                "oper":        "get",
                "resource":    "exportarDados",
                "instituicao": COD_INSTITUICAO,
                "escola":      "",
                "status":      "1",
                "tipoUsuario": "",
            },
            catch_response=True,
            name="GET /module/Api/UsuarioExport [exportarDados]",
            timeout=120,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if not data.get("any_error_msg"):
                        resp.success()
                        return True
                    else:
                        resp.failure(f"Exportação retornou erro: {data.get('msgs')}")
                        return False
                except Exception:
                    # Pode retornar CSV/arquivo ao invés de JSON
                    if resp.text and len(resp.text) > 0:
                        resp.success()
                        return True
                    resp.failure("Resposta vazia ou inválida")
                    return False
            else:
                resp.failure(f"Exportar dados falhou — status {resp.status_code}. Resposta: {resp.text[:300]}")
                return False

    @task
    def exportar_usuarios(self):
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [exportacao]")
        if not ok:
            return

        ok = self._navegar_configuracoes()
        if not ok:
            return

        ok = self._abrir_exportacao()
        if not ok:
            return

        ok = self._buscar_escolas()
        if not ok:
            return

        self._exportar_dados()