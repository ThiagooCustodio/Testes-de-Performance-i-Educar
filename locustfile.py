"""
i-Educar — Testes de Performance
=================================
Cenários disponíveis (use --class-picker para selecionar):
  - UsuarioLoginTeste      : login válido, inválido e navegação básica
  - UsuarioAlunoTeste      : cadastro e consulta de alunos
  - UsuarioConsultaTeste   : busca e consulta via API
  - UsuarioExportacaoTeste : fluxo completo de exportação de usuários
  - UsuarioNavegacaoTeste  : navegação livre pelo sistema
"""

import os
import random
import string
from locust import HttpUser, between, task

# ---------------------------------------------------------------------------
# Configuração — sobrescrita via variáveis de ambiente ou .env
# ---------------------------------------------------------------------------
HOST           = os.getenv("TARGET_HOST",            "http://host.docker.internal")
USUARIO        = os.getenv("IEDUCAR_USER",           "admin")
SENHA          = os.getenv("IEDUCAR_PASS",           "admin")
COD_INSTITUICAO = os.getenv("IEDUCAR_COD_INSTITUICAO", "1")


# ---------------------------------------------------------------------------
# Classe base — evita repetir host/timeouts em cada cenário
# ---------------------------------------------------------------------------
class IEducarUser(HttpUser):
    abstract    = True
    host        = HOST
    wait_time   = between(1, 3)
    network_timeout    = 120.0
    connection_timeout = 120.0

    # -- login ---------------------------------------------------------------
    def login(self, nome_tarefa="POST /login"):
        """Faz GET /login + POST /login. Retorna True se autenticou."""
        with self.client.get(
            "/login",
            catch_response=True,
            name="GET /login",
            timeout=30,
        ) as r:
            if r.status_code != 200:
                r.failure(f"GET /login retornou {r.status_code}")
                return False

        with self.client.post(
            "/login",
            data={"login": USUARIO, "password": SENHA},
            allow_redirects=False,
            catch_response=True,
            name=nome_tarefa,
            timeout=60,
        ) as r:
            if r.status_code == 302:
                r.success()
                return True
            r.failure(f"Login falhou — status {r.status_code}")
            return False

    # -- GET genérico --------------------------------------------------------
    def get(self, url, nome, timeout=30, ok_codes=(200,)):
        """GET simples com validação de status. Retorna True se ok."""
        with self.client.get(
            url,
            catch_response=True,
            name=nome,
            timeout=timeout,
        ) as r:
            if r.status_code in ok_codes:
                r.success()
                return True
            r.failure(f"{nome} — status {r.status_code}")
            return False

    # -- POST genérico -------------------------------------------------------
    def post(self, url, dados, nome, timeout=60, ok_codes=(200, 302)):
        """POST com validação de status. Retorna (sucesso, response_json_ou_None)."""
        with self.client.post(
            url,
            data=dados,
            allow_redirects=False,
            catch_response=True,
            name=nome,
            timeout=timeout,
        ) as r:
            if r.status_code in ok_codes:
                try:
                    data = r.json()
                    if data.get("any_error_msg"):
                        msgs = data.get("msgs", [])
                        erro = msgs[0]["msg"] if msgs else "Erro interno"
                        r.failure(erro)
                        return False, None
                    r.success()
                    return True, data
                except Exception:
                    r.success()
                    return True, None
            r.failure(f"{nome} — status {r.status_code}")
            return False, None


# ===========================================================================
# Cenário 1 — Login
# ===========================================================================
class UsuarioLoginTeste(IEducarUser):

    @task(60)
    def login_sucesso(self):
        self.login("POST /login [sucesso]")

    @task(20)
    def login_falha(self):
        self.get("/login", "GET /login", timeout=30)
        with self.client.post(
            "/login",
            data={"login": "usuario_invalido", "password": "senha_errada"},
            allow_redirects=False,
            catch_response=True,
            name="POST /login [falha esperada]",
            timeout=60,
        ) as r:
            # 302 = redirecionou mesmo com credenciais erradas (comportamento do app)
            r.success() if r.status_code == 302 else r.failure(f"Status inesperado: {r.status_code}")

    @task(20)
    def login_e_listagem_alunos(self):
        if not self.login("POST /login [nav aluno]"):
            return
        self.get("/intranet/educar/Aluno/index.php", "GET /alunos")


# ===========================================================================
# Cenário 2 — Aluno
# ===========================================================================
class UsuarioAlunoTeste(IEducarUser):

    def _criar_pessoa(self):
        nome = "AlunoTeste" + "".join(random.choices(string.ascii_uppercase, k=8))
        ok, data = self.post(
            "/module/Api/Pessoa",
            {
                "oper": "post", "resource": "pessoa",
                "nome": nome, "sexo": "M", "datanasc": "01/01/2000",
            },
            "POST /module/Api/Pessoa [criar]",
        )
        if ok and data:
            return data.get("pessoa_id") or data.get("id")
        return None

    def _criar_aluno(self, pessoa_id):
        ok, _ = self.post(
            "/module/Api/Aluno",
            [
                ("oper", "post"), ("resource", "aluno"),
                ("id_pessoa", pessoa_id), ("pessoa_id", pessoa_id),
                ("tipo_responsavel", "mae"), ("tipo_transporte", "nenhum"),
                ("deficiencias[]", ""), ("transtornos[]", ""),
                ("beneficios[]", ""), ("analfabeto", "0"), ("emancipado", "0"),
            ],
            "POST /module/Api/Aluno [inserir]",
        )
        return ok

    @task(60)
    def cadastrar_aluno(self):
        if not self.login("POST /login [cadastro aluno]"):
            return
        pessoa_id = self._criar_pessoa()
        if pessoa_id:
            self._criar_aluno(pessoa_id)

    @task(40)
    def consultar_aluno(self):
        if not self.login("POST /login [consulta aluno]"):
            return
        with self.client.get(
            "/module/Api/Aluno?oper=get&resource=aluno&id=3",
            catch_response=True,
            name="GET /module/Api/Aluno [por id]",
            timeout=30,
        ) as r:
            if r.status_code == 200:
                data = r.json() if r.text else {}
                r.success() if not data.get("any_error_msg") else r.failure("API retornou erro")
            else:
                r.failure(f"Consulta retornou {r.status_code}")


# ===========================================================================
# Cenário 3 — Consulta
# ===========================================================================
class UsuarioConsultaTeste(IEducarUser):

    @task(40)
    def buscar_por_nome(self):
        if not self.login("POST /login [consulta nome]"):
            return
        self.get(
            "/module/Api/Aluno?oper=get&resource=aluno-search&query=Teste",
            "GET /module/Api/Aluno [aluno-search]",
        )

    @task(40)
    def consultar_por_id(self):
        if not self.login("POST /login [consulta id]"):
            return
        self.get(
            "/module/Api/Aluno?oper=get&resource=aluno&id=3",
            "GET /module/Api/Aluno [por id]",
        )

    @task(20)
    def consultar_matriculas(self):
        if not self.login("POST /login [consulta matriculas]"):
            return
        self.get(
            "/module/Api/Aluno?oper=get&resource=matriculas&aluno_id=3",
            "GET /module/Api/Aluno [matriculas]",
        )


# ===========================================================================
# Cenário 4 — Exportação
# ===========================================================================
class UsuarioExportacaoTeste(IEducarUser):

    @task
    def exportar_usuarios(self):
        if not self.login("POST /login [exportacao]"):
            return
        if not self.get("/intranet/educar_configuracoes_index.php", "GET /intranet [configuracoes]"):
            return
        if not self.get("/intranet/educar_exportacao_usuarios.php", "GET /intranet [exportacao_usuarios]"):
            return
        if not self.get(
            f"/module/Api/escola?oper=get&resource=escolas-para-selecao&instituicao={COD_INSTITUICAO}",
            "GET /module/Api/escola [escolas-para-selecao]",
        ):
            return
        with self.client.get(
            "/module/Api/UsuarioExport",
            params={"oper": "get", "resource": "exportarDados",
                    "instituicao": COD_INSTITUICAO, "escola": "", "status": "1", "tipoUsuario": ""},
            catch_response=True,
            name="GET /module/Api/UsuarioExport [exportarDados]",
            timeout=120,
        ) as r:
            if r.status_code == 200:
                r.success() if r.text else r.failure("Resposta vazia")
            else:
                r.failure(f"Exportar dados falhou — status {r.status_code}")


# ===========================================================================
# Cenário 5 — Navegação
# ===========================================================================
class UsuarioNavegacaoTeste(IEducarUser):
    wait_time = between(2, 8)  # simula usuário lendo a tela

    _paginas = [
        ("/intranet/index.php",                      "dashboard",    5),
        ("/intranet/educar_pessoas_index.php",        "pessoas",      4),
        ("/intranet/educar_enderecamento_index.php",  "enderecamento",3),
        ("/intranet/educar_configuracoes_index.php",  "configuracoes",2),
        ("/intranet/educar_exportacao_usuarios.php",  "exportacao",   1),
    ]

    @task
    def navegar(self):
        if not self.login("POST /login [navegacao]"):
            return

        # Sempre começa pelo dashboard
        self.get("/intranet/index.php", "GET /intranet [dashboard]", timeout=30, ok_codes=(200, 301, 302))

        # Visita 2 a 5 páginas aleatórias com peso por frequência de acesso
        urls, nomes, pesos = zip(*self._paginas)
        for idx in random.choices(range(len(self._paginas)), weights=pesos, k=random.randint(2, 5)):
            self.get(urls[idx], f"GET /intranet [{nomes[idx]}]", timeout=30, ok_codes=(200, 301, 302))