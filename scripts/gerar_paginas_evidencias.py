"""Gera as páginas de evidências do GitHub a partir dos resultados reais:

  testes/README.md      -> os 34 testes (tipos, restrições, regras) com print de cada um
  evidencias/README.md  -> índices (antes/depois), view e consultas C01–C08 com prints

Lê evidencias/resultados/*.csv e o cabeçalho dos arquivos .sql; não inventa números.
Uso: python3 scripts/gerar_paginas_evidencias.py
"""
import csv
import glob
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "evidencias", "resultados")
CAP = os.path.join(RAIZ, "evidencias", "capturas")


def ler_csv(nome, sep=","):
    with open(os.path.join(RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter=sep))


def esc(txt):
    return (txt or "").replace("|", "\\|").replace("\n", " ")


def arquivo_do_teste(tid):
    achados = sorted(glob.glob(os.path.join(RAIZ, "testes", tid + "_*.sql")))
    return os.path.splitext(os.path.basename(achados[0]))[0] if achados else None


def selo(res):
    return "✅ PASSOU" if res == "PASSOU" else "❌ " + res


# ------------------------------------------------------------------ testes
CATEGORIAS = [
    ("Tipo", "1. Testes de tipos de dados (T01–T11)",
     "Cada teste tenta gravar um valor que o tipo ou o domínio deve aceitar ou recusar."),
    ("Restrição", "2. Testes de restrições (R01–R13)",
     "NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY (RESTRICT/CASCADE) e CHECK."),
    ("Regra", "3. Testes de regras de negócio (G01–G10)",
     "Regras implementadas com gatilhos (triggers) em `sql/02_regras_triggers.sql`."),
]


def pagina_testes():
    testes = ler_csv("resumo_testes.csv")
    total = len(testes)
    ok = sum(t["resultado"] == "PASSOU" for t in testes)
    L = []
    L.append("# Testes do banco — Oficina Mecânica\n")
    L.append(f"**Resultado: {ok} de {total} testes passaram.**\n")
    L.append("Todos os testes rodam no **PostgreSQL 16** dentro de `BEGIN … ROLLBACK` "
             "(o banco não é alterado). Cada um compara o resultado esperado com o "
             "**código SQLSTATE** devolvido pelo banco. O print abaixo de cada teste é a "
             "saída real do `psql`.\n")
    L.append("Como rodar: `./scripts/rodar_tudo.sh` (Linux/Mac) ou "
             "`scripts\\rodar_tudo_windows.bat` (Windows). O GitHub Actions roda tudo a cada push.\n")
    L.append("Códigos de erro usados: `22001` texto longo demais · `22003` número fora do limite · "
             "`22P02` valor inválido para o tipo · `22008` data inválida · `23502` NOT NULL · "
             "`23503` chave estrangeira · `23505` duplicado (UNIQUE/PK) · `23514` CHECK · "
             "`P0001` erro levantado por trigger.\n")

    L.append("## Índice\n")
    L.append("| ID | Categoria | Teste | Esperado | Obtido | Resultado |")
    L.append("|---|---|---|---|---|---|")
    for t in testes:
        L.append(f"| [{t['id']}](#{t['id'].lower()}) | {t['categoria']} | {esc(t['descricao'])} | "
                 f"{t['esperado']} | {t['obtido']} | {selo(t['resultado'])} |")
    L.append("")

    for cat, titulo, intro in CATEGORIAS:
        L.append(f"## {titulo}\n")
        L.append(intro + "\n")
        for t in (x for x in testes if x["categoria"] == cat):
            base = arquivo_do_teste(t["id"])
            L.append(f'<a id="{t["id"].lower()}"></a>\n')
            L.append(f"### {t['id']} — {t['descricao']}\n")
            L.append("| Esperado | Obtido | Resultado |")
            L.append("|---|---|---|")
            L.append(f"| {t['esperado']} | {t['obtido']} | {selo(t['resultado'])} |\n")
            L.append(f"**Resposta do banco:** `{t['mensagem_do_banco']}`\n")
            if base:
                L.append(f"Arquivos: [SQL do teste]({base}.sql) · "
                         f"[log completo](../evidencias/resultados/{base}.txt)\n")
                if os.path.exists(os.path.join(CAP, base + ".png")):
                    L.append(f"![{t['id']}](../evidencias/capturas/{base}.png)\n")
            L.append("[↑ voltar ao índice](#índice)\n")
    return "\n".join(L)


# ------------------------------------------------------------------ evidências
def titulo_consulta(arq):
    with open(arq, encoding="utf-8") as fh:
        linha = fh.readline().strip()
    return linha.lstrip("-").strip()


def num(v, casas=2):
    return f"{float(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pagina_evidencias():
    L = []
    L.append("# Evidências — Oficina Mecânica\n")
    L.append("Tudo aqui foi gerado executando os scripts de `scripts/` no PostgreSQL 16, "
             "com 300 mil ordens de serviço de teste.\n")
    L.append("| Pasta | Conteúdo |")
    L.append("|---|---|")
    L.append("| [`capturas/`](capturas) | prints (PNG) da saída real do `psql` |")
    L.append("| [`resultados/`](resultados) | logs `.txt`, planos de execução e tabelas `.csv` |")
    L.append("| [`../testes/`](../testes) | os 34 testes de tipos, restrições e regras, "
             "**com um print por teste** |\n")
    L.append("## Sumário\n")
    L.append("1. [Testes de tipos, restrições e regras](../testes/README.md)")
    L.append("2. [Índices: antes x depois](#2-índices-antes-x-depois)")
    L.append("3. [Visão de totais: GROUP BY x LATERAL](#3-visão-de-totais-group-by-x-lateral)")
    L.append("4. [Consultas de negócio C01–C08](#4-consultas-de-negócio-c01c08)\n")

    testes = ler_csv("resumo_testes.csv")
    ok = sum(t["resultado"] == "PASSOU" for t in testes)
    L.append("## 1. Testes de tipos, restrições e regras\n")
    L.append(f"**{ok} de {len(testes)} passaram.** Lista completa com o print de cada teste em "
             "[`testes/README.md`](../testes/README.md).\n")

    # índices
    L.append("## 2. Índices: antes x depois\n")
    L.append("Medido com `EXPLAIN (ANALYZE, BUFFERS)`, mediana de 7 execuções "
             "(script `scripts/medir_indices.py`). O número de páginas lidas é a medida mais estável; "
             "o tempo varia um pouco entre execuções.\n")
    L.append("| ID | Índice | Consulta | Antes (ms) | Depois (ms) | Ganho | Páginas antes → depois | Acesso depois |")
    L.append("|---|---|---|---:|---:|---:|---|---|")
    for r in ler_csv("indices_antes_depois.csv"):
        pag = f"{r['paginas_antes']} → {r['paginas_depois']}" if r["paginas_antes"] else "—"
        L.append(f"| {r['id']} | `{esc(r['indice'])}` | {esc(r['consulta'])} | {num(r['ms_antes'])} | "
                 f"{num(r['ms_depois'])} | {num(r['ganho_x'], 1)}x | {pag} | {esc(r['acesso_depois']) or '—'} |")
    L.append("")
    L.append("Leitura dos casos especiais: **B8** mostra o índice sendo **ignorado** pelo otimizador "
             "(95% das linhas atendem ao filtro, então ler a tabela inteira é mais barato). "
             "**W1** mostra o custo dos índices na escrita (ganho menor que 1x = ficou mais lento).\n")
    L.append("Tamanho de cada índice:\n")
    L.append("| Índice | Tamanho |")
    L.append("|---|---|")
    for r in ler_csv("indices_tamanho.csv", sep=";"):
        L.append(f"| `{r['indice']}` | {r['tamanho']} |")
    L.append("")
    L.append("### Planos de execução (prints)\n")
    planos = sorted({os.path.basename(p)[len("plano_"):].split("_")[0]
                     for p in glob.glob(os.path.join(CAP, "plano_*_antes.png"))})
    for b in planos:
        L.append(f"#### {b} — antes e depois do índice\n")
        L.append("| Antes | Depois |")
        L.append("|---|---|")
        L.append(f"| ![{b} antes](capturas/plano_{b}_antes.png) | ![{b} depois](capturas/plano_{b}_depois.png) |\n")
    todos = sorted(os.path.basename(p) for p in glob.glob(os.path.join(RES, "plano_*.txt")))
    L.append("Todos os planos em texto: " + " · ".join(f"[{p[6:-4]}](resultados/{p})" for p in todos) + "\n")

    # view
    L.append("## 3. Visão de totais: GROUP BY x LATERAL\n")
    L.append("Comparação das duas versões da view `vw_os_total` (script `scripts/comparar_views.py`).\n")
    L.append("| Consulta | v1 GROUP BY (ms) | v2 LATERAL (ms) | v1 ÷ v2 |")
    L.append("|---|---:|---:|---:|")
    for r in ler_csv("view_v1_vs_v2.csv"):
        L.append(f"| {r['consulta']} | {num(r['ms_v1_groupby'])} | {num(r['ms_v2_lateral'])} | "
                 f"{num(r['razao_v1_v2'], 1)}x |")
    L.append("")
    L.append("A versão LATERAL é muito mais rápida para poucas OS (histórico de uma placa), "
             "mas fica mais lenta quando precisa varrer todas as OS; por isso o relatório C06 "
             "agrega direto nas tabelas.\n")

    # consultas
    L.append("## 4. Consultas de negócio C01–C08\n")
    for arq in sorted(glob.glob(os.path.join(RAIZ, "consultas", "C*.sql"))):
        base = os.path.splitext(os.path.basename(arq))[0]
        L.append(f"### {titulo_consulta(arq)}\n")
        L.append(f"Arquivos: [SQL](../consultas/{base}.sql) · [resultado em texto](resultados/{base}.txt)\n")
        if os.path.exists(os.path.join(CAP, base + ".png")):
            L.append(f"![{base}](capturas/{base}.png)\n")
    return "\n".join(L)


if __name__ == "__main__":
    for destino, conteudo in (("testes/README.md", pagina_testes()),
                              ("evidencias/README.md", pagina_evidencias())):
        with open(os.path.join(RAIZ, destino), "w", encoding="utf-8") as fh:
            fh.write(conteudo)
        print("gerado:", destino)
