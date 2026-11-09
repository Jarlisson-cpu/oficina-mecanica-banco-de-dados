# Evidências — Oficina Mecânica

Tudo aqui foi gerado executando os scripts de `scripts/` no PostgreSQL 16, com 300 mil ordens de serviço de teste.

| Pasta | Conteúdo |
|---|---|
| [`capturas/`](capturas) | prints (PNG) da saída real do `psql` |
| [`resultados/`](resultados) | logs `.txt`, planos de execução e tabelas `.csv` |
| [`../testes/`](../testes) | os 34 testes de tipos, restrições e regras, **com um print por teste** |

## Sumário

1. [Testes de tipos, restrições e regras](../testes/README.md)
2. [Índices: antes x depois](#2-índices-antes-x-depois)
3. [Visão de totais: GROUP BY x LATERAL](#3-visão-de-totais-group-by-x-lateral)
4. [Consultas de negócio C01–C08](#4-consultas-de-negócio-c01c08)

## 1. Testes de tipos, restrições e regras

**34 de 34 passaram.** Lista completa com o print de cada teste em [`testes/README.md`](../testes/README.md).

## 2. Índices: antes x depois

Medido com `EXPLAIN (ANALYZE, BUFFERS)`, mediana de 7 execuções (script `scripts/medir_indices.py`). O número de páginas lidas é a medida mais estável; o tempo varia um pouco entre execuções.

| ID | Índice | Consulta | Antes (ms) | Depois (ms) | Ganho | Páginas antes → depois | Acesso depois |
|---|---|---|---:|---:|---:|---|---|
| B1 | `I1 ix_os_veiculo_data` | Histórico de OS de um veículo pela placa | 30,60 | 0,25 | 120,5x | 8323 → 31 | Index Scan uq_veiculo_placa; Index Scan ix_os_veiculo_data |
| B2 | `I2 ix_os_pendentes (parcial)` | Painel: 50 OS pendentes mais antigas | 24,80 | 0,35 | 71,7x | 8276 → 52 | Index Scan ix_os_pendentes |
| B3 | `I3 ix_os_mecanico_data` | Produção de um mecânico em set/2026 | 24,32 | 0,84 | 28,8x | 8204 → 200 | Bitmap Index Scan ix_os_mecanico_data |
| B4 | `I4 ix_os_conclusao` | Faturamento de mão de obra em set/2026 | 23,52 | 6,28 | 3,7x | 8204 → 2590 | Bitmap Index Scan ix_os_conclusao |
| B5 | `I5 ix_os_peca_peca` | Consumo total de uma peça | 29,25 | 2,56 | 11,4x | 2870 → 611 | Bitmap Index Scan ix_os_peca_peca |
| B6 | `I6 ix_veiculo_cliente` | Veículos de um cliente | 2,00 | 0,14 | 14,8x | 613 → 4 | Index Scan ix_veiculo_cliente |
| B7 | `I7 ix_cliente_nome_trgm (GIN)` | Busca de cliente por parte do nome | 12,04 | 0,97 | 12,4x | 266 → 174 | Bitmap Index Scan ix_cliente_nome_trgm |
| B8 | `I8 ix_os_status (contraexemplo)` | Somar mão de obra das OS CONCLUIDAS (95% da tabela) | 46,32 | 49,09 | 0,9x | 8204 → 8204 | Seq Scan ordem_servico |
| B9 | `I8 ix_os_status` | Somar mão de obra das OS ABERTAS (0,2% da tabela) | 25,46 | 1,59 | 16,0x | 8204 → 532 | Index Scan ix_os_status |
| W1 | `todos` | INSERT de 20.000 OS (custo de escrita) | 1.250,40 | 1.577,50 | 0,8x | — | — |

Leitura dos casos especiais: **B8** mostra o índice sendo **ignorado** pelo otimizador (95% das linhas atendem ao filtro, então ler a tabela inteira é mais barato). **W1** mostra o custo dos índices na escrita (ganho menor que 1x = ficou mais lento).

Tamanho de cada índice:

| Índice | Tamanho |
|---|---|
| `ix_cliente_nome_trgm` | 824 kB |
| `ix_os_conclusao` | 7096 kB |
| `ix_os_mecanico_data` | 9968 kB |
| `ix_os_peca_peca` | 3160 kB |
| `ix_os_pendentes` | 464 kB |
| `ix_os_status` | 2792 kB |
| `ix_os_veiculo_data` | 15 MB |
| `ix_veiculo_cliente` | 1280 kB |

### Planos de execução (prints)

#### B1 — antes e depois do índice

| Antes | Depois |
|---|---|
| ![B1 antes](capturas/plano_B1_antes.png) | ![B1 depois](capturas/plano_B1_depois.png) |

#### B2 — antes e depois do índice

| Antes | Depois |
|---|---|
| ![B2 antes](capturas/plano_B2_antes.png) | ![B2 depois](capturas/plano_B2_depois.png) |

#### B4 — antes e depois do índice

| Antes | Depois |
|---|---|
| ![B4 antes](capturas/plano_B4_antes.png) | ![B4 depois](capturas/plano_B4_depois.png) |

#### B8 — antes e depois do índice

| Antes | Depois |
|---|---|
| ![B8 antes](capturas/plano_B8_antes.png) | ![B8 depois](capturas/plano_B8_depois.png) |

#### B9 — antes e depois do índice

| Antes | Depois |
|---|---|
| ![B9 antes](capturas/plano_B9_antes.png) | ![B9 depois](capturas/plano_B9_depois.png) |

Todos os planos em texto: [B1_antes](resultados/plano_B1_antes.txt) · [B1_depois](resultados/plano_B1_depois.txt) · [B2_antes](resultados/plano_B2_antes.txt) · [B2_depois](resultados/plano_B2_depois.txt) · [B3_antes](resultados/plano_B3_antes.txt) · [B3_depois](resultados/plano_B3_depois.txt) · [B4_antes](resultados/plano_B4_antes.txt) · [B4_depois](resultados/plano_B4_depois.txt) · [B5_antes](resultados/plano_B5_antes.txt) · [B5_depois](resultados/plano_B5_depois.txt) · [B6_antes](resultados/plano_B6_antes.txt) · [B6_depois](resultados/plano_B6_depois.txt) · [B7_antes](resultados/plano_B7_antes.txt) · [B7_depois](resultados/plano_B7_depois.txt) · [B8_antes](resultados/plano_B8_antes.txt) · [B8_depois](resultados/plano_B8_depois.txt) · [B9_antes](resultados/plano_B9_antes.txt) · [B9_depois](resultados/plano_B9_depois.txt)

## 3. Visão de totais: GROUP BY x LATERAL

Comparação das duas versões da view `vw_os_total` (script `scripts/comparar_views.py`).

| Consulta | v1 GROUP BY (ms) | v2 LATERAL (ms) | v1 ÷ v2 |
|---|---:|---:|---:|
| histórico de 1 placa | 314,46 | 0,50 | 632,7x |
| faturamento set/2026 | 343,51 | 68,57 | 5,0x |
| faturamento total (todas as OS) | 969,21 | 2.114,03 | 0,5x |

A versão LATERAL é muito mais rápida para poucas OS (histórico de uma placa), mas fica mais lenta quando precisa varrer todas as OS; por isso o relatório C06 agrega direto nas tabelas.

## 4. Consultas de negócio C01–C08

### C01 Histórico do veículo pela placa (recepção): últimas 5 OS com valor total

Arquivos: [SQL](../consultas/C01_historico_por_placa.sql) · [resultado em texto](resultados/C01_historico_por_placa.txt)

![C01_historico_por_placa](capturas/C01_historico_por_placa.png)

### C02 Faturamento mensal de 2026 (OS concluídas): peças, mão de obra e ticket médio

Arquivos: [SQL](../consultas/C02_faturamento_mensal.sql) · [resultado em texto](resultados/C02_faturamento_mensal.txt)

![C02_faturamento_mensal](capturas/C02_faturamento_mensal.png)

### C03 Ranking de mecânicos em 2026: OS concluídas, horas, tempo médio e faturamento

Arquivos: [SQL](../consultas/C03_ranking_mecanicos.sql) · [resultado em texto](resultados/C03_ranking_mecanicos.txt)

![C03_ranking_mecanicos](capturas/C03_ranking_mecanicos.png)

### C04 Peças para repor: abaixo do mínimo, com o consumo dos últimos 90 dias

Arquivos: [SQL](../consultas/C04_pecas_repor.sql) · [resultado em texto](resultados/C04_pecas_repor.txt)

![C04_pecas_repor](capturas/C04_pecas_repor.png)

### C05 OS pendentes há mais de 7 dias (painel da recepção), agrupadas por status

Arquivos: [SQL](../consultas/C05_os_atrasadas.sql) · [resultado em texto](resultados/C05_os_atrasadas.txt)

![C05_os_atrasadas](capturas/C05_os_atrasadas.png)

### C06 Top 10 clientes por gasto acumulado e participação no faturamento total.

Arquivos: [SQL](../consultas/C06_top_clientes.sql) · [resultado em texto](resultados/C06_top_clientes.txt)

![C06_top_clientes](capturas/C06_top_clientes.png)

### C07 Retrabalho: veículo que volta com o MESMO problema em até 30 dias após a conclusão.

Arquivos: [SQL](../consultas/C07_retrabalho.sql) · [resultado em texto](resultados/C07_retrabalho.txt)

![C07_retrabalho](capturas/C07_retrabalho.png)

### C08 Conferência: o total da view vw_os_total bate com a soma feita direto nas tabelas?

Arquivos: [SQL](../consultas/C08_conferencia_totais.sql) · [resultado em texto](resultados/C08_conferencia_totais.txt)

![C08_conferencia_totais](capturas/C08_conferencia_totais.png)
