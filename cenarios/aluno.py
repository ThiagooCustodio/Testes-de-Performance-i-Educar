import os
import random
import string
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
        nome = "AlunoTeste" + "".join(
            random.choices(string.ascii_uppercase, k=8)
        )

        print(f"NOME GERADO: {nome}")

        with self.client.post(
            "/module/Api/Pessoa",
            data={
                "oper": "post",
                "resource": "pessoa",
                "nome": nome,
                "sexo": "M",
                "datanasc": "01/01/2000",
            },
            allow_redirects=False,
            catch_response=True,
            name="POST /module/Api/Pessoa [criar]",
            timeout=60,
        ) as resp:
            if resp.status_code in (200, 302):
                try:
                    data = resp.json()

                    print("\n=== RESPOSTA API PESSOA ===")
                    print(data)
                    print("==========================\n")

                    pessoa_id = data.get("pessoa_id") or data.get("id")

                    if pessoa_id:
                        resp.success()
                        return pessoa_id

                except Exception as e:
                    print("\n=== ERRO AO LER JSON PESSOA ===")
                    print(resp.text)
                    print(e)
                    print("========================\n")

                resp.failure("pessoa_id não retornado")
            else:
                resp.failure(f"Criar pessoa falhou — status {resp.status_code}")

        return None

    def _criar_aluno(self, pessoa_id):
        with self.client.post(
            "/module/Api/Aluno",
            # Usando lista de tuplas para permitir chaves repetidas (notação array PHP)
            data=[
                ("oper", "post"),
                ("resource", "aluno"),
                ("id_pessoa", pessoa_id),
                ("pessoa_id", pessoa_id),
                ("tipo_responsavel", "mae"),
                ("tipo_transporte", "nenhum"),
                ("deficiencias[]", ""),
                ("transtornos[]", ""),
                ("beneficios[]", ""),
                ("analfabeto", "0"),
                ("emancipado", "0"),
            ],
            allow_redirects=False,
            catch_response=True,
            name="POST /module/Api/Aluno [inserir]",
            timeout=60,
        ) as resp:
            if resp.status_code in (200, 302):
                try:
                    data = resp.json()
                    aluno_id = data.get("id") or data.get("aluno_id")

                    if aluno_id and not data.get("any_error_msg"):
                        resp.success()
                        return True
                    else:
                        msgs = data.get("msgs", [])
                        erro = msgs[0]["msg"] if msgs else "Erro interno no JSON"
                        resp.failure(f"Erro ao criar aluno: {erro}")
                        return False
                except Exception:
                    resp.failure("Resposta 200 ok, mas não enviou JSON válido")
            else:
                resp.failure(
                    f"Criar aluno falhou — status {resp.status_code}. "
                    f"Resposta: {resp.text[:200]}"
                )
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
        ok = fazer_login(self.client, USUARIO_VALIDO, SENHA_VALIDA, "POST /login [consulta aluno]")
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
                resp.failure(f"Consulta retornou {resp.status_code}")