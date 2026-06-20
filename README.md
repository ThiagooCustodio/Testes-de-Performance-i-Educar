# Testes de Performance — i-Educar

Testes de carga e performance realizados no sistema i-Educar utilizando [Locust](https://locust.io/), cobrindo 5 cenários de uso realista (login, cadastro de aluno, consulta, exportação e navegação) em diferentes níveis de carga.

## Sobre o projeto

Este repositório contém os scripts, cenários, resultados e documentação dos testes de performance realizados no sistema i-Educar.

O i-Educar é um software livre de gestão escolar desenvolvido para instituições públicas de ensino, utilizado por prefeituras e secretarias de educação brasileiras. O projeto é mantido pela comunidade open source e disponibilizado publicamente através do GitHub oficial.

## Objetivo

O objetivo deste trabalho é avaliar o comportamento do sistema sob carga concorrente, identificando:

- Percentis de tempo de resposta (P90, P95) por endpoint
- Throughput (requisições por segundo) em cada cenário e carga
- Comportamento de escalabilidade se a resposta do sistema é linear ou apresenta saturação
- Gargalos e endpoints mal otimizados
- Regressões de performance conforme a carga aumenta

## Sistema avaliado
 
| Atributo            | Valor                                  |

| Nome                | i-Educar                               |
| Tipo                | Sistema de Gestão Escolar              |
| Licença             | GPL-2.0                                |
| Linguagem principal | PHP                                    |
| Framework           | Laravel 13.15.0                        |
| Banco de dados      | PostgreSQL                             |
| Cache               | Redis                                  |
| Servidor web        | Nginx                                  |
| Repositório oficial | https://github.com/portabilis/i-educar |

**Versão avaliada:**
- Branch: `2.12`
- Commit: `49d9311`
- Data da coleta: junho de 2026

> Como o i-Educar é um projeto open source em constante evolução, novas versões podem apresentar comportamentos e resultados diferentes dos registrados neste estudo.

## Cenários de teste

| Cenário    | Método                  | Endpoints principais                      | Descrição                                        |

| Login      | GET + POST              | `/login`                                  | Autenticação com credenciais válidas e inválidas |
| Aluno      | POST x2                 | `/module/Api/Pessoa`, `/module/Api/Aluno` | Criação de pessoa e cadastro como aluno          |
| Consulta   | GET                     | `/module/Api/Aluno`                       | Busca por nome, ID e matrículas                  |
| Exportação | GET (fluxo de 5 etapas) | `/intranet/*`, `/module/Api/*`            | Fluxo completo de exportação de usuários         |
| Navegação  | GET                     | `/intranet/*` (várias páginas)            | Navegação livre simulando uso real               |

Os testes foram executados com **1, 5, 10, 50 e 100 usuários simultâneos**, com duração de 60 segundos por execução, totalizando 25 cenários de teste.

## Pré-requisitos

- [Docker](https://www.docker.com/products/docker-desktop/) e Docker Compose instalados
- Uma instância do i-Educar rodando localmente ou em rede acessível (veja o [repositório oficial](https://github.com/portabilis/i-educar) para subir o ambiente)

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/ThiagooCustodio/Testes-de-Performance-i-Educar.git
cd Testes-de-Performance-i-Educar
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e edite com os dados do seu ambiente:

```bash
cp .env.example .env
```

```env
TARGET_HOST=http://host.docker.internal
IEDUCAR_USER=admin
IEDUCAR_PASS=admin
IEDUCAR_COD_INSTITUICAO=1
TEST_DURATION=60s
SPAWN_RATE=5
```

> `http://host.docker.internal` aponta para a máquina host a partir de dentro do container — use esse valor se o i-Educar estiver rodando localmente. Se estiver em outro servidor, substitua pela URL correspondente.

### 3. Execute os testes

```bash
docker compose --profile headless up --build
```

Isso vai rodar os 5 cenários para cada nível de carga (1, 5, 10, 50 e 100 usuários), aguardando 5 segundos entre cada execução.

### 4. Veja os resultados

Os relatórios são gerados automaticamente na pasta `results/`:

- `*.html` — relatório visual interativo com gráficos de tempo de resposta e throughput (abra direto no navegador)
- `*_stats.csv` — métricas agregadas (percentis, throughput, falhas) por endpoint
- `*_stats_history.csv` — histórico detalhado por segundo de execução
- `*_failures.csv` — detalhamento de falhas, se houver

Exemplo: para ver o relatório do cenário de login com 10 usuários, abra `results/login_10u.html`.

## Estrutura do repositório

```
.
├── locustfile.py        
├── run_test.sh           
├── Dockerfile             
├── docker-compose.yml    
├── requirements.txt    
├── .env.example           
├── results/                
└── README.md
```

## Modos de execução disponíveis

Além do modo headless padrão, o `docker-compose.yml` oferece outros perfis:

```bash
docker compose --profile distributed up --scale locust-worker=4

TARGET_HOST=http://192.168.1.100 IEDUCAR_COD_INSTITUICAO=2 docker compose --profile headless up
```

## Relatório completo

A análise detalhada dos resultados — incluindo gráficos, percentis por cenário, identificação de gargalos, regressões de performance e conclusão crítica — está disponível no relatório em PDF/Word incluído neste repositório.

## Licença

Este projeto é distribuído para fins educacionais. O i-Educar é licenciado sob GPL-2.0 pelo seu projeto original.
