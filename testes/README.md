# Testes do banco — Oficina Mecânica

**Resultado: 34 de 34 testes passaram.**

Todos os testes rodam no **PostgreSQL 16** dentro de `BEGIN … ROLLBACK` (o banco não é alterado). Cada um compara o resultado esperado com o **código SQLSTATE** devolvido pelo banco. O print abaixo de cada teste é a saída real do `psql`.

Como rodar: `./scripts/rodar_tudo.sh` (Linux/Mac) ou `scripts\rodar_tudo_windows.bat` (Windows). O GitHub Actions roda tudo a cada push.

Códigos de erro usados: `22001` texto longo demais · `22003` número fora do limite · `22P02` valor inválido para o tipo · `22008` data inválida · `23502` NOT NULL · `23503` chave estrangeira · `23505` duplicado (UNIQUE/PK) · `23514` CHECK · `P0001` erro levantado por trigger.

## Índice

| ID | Categoria | Teste | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|
| [T01](#t01) | Tipo | Placa com 8 caracteres não cabe em CHAR(7) | ERRO 22001 | ERRO 22001 | ✅ PASSOU |
| [T02](#t02) | Tipo | Placa fora do padrão (domínio dm_placa) | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [T03](#t03) | Tipo | Placa Mercosul válida é aceita | OK | OK | ✅ PASSOU |
| [T04](#t04) | Tipo | Texto em coluna SMALLINT (ano) | ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |
| [T05](#t05) | Tipo | Ano 40000 estoura o limite de SMALLINT | ERRO 22003 | ERRO 22003 | ✅ PASSOU |
| [T06](#t06) | Tipo | Valor acima de NUMERIC(10,2) é rejeitado | ERRO 22003 | ERRO 22003 | ✅ PASSOU |
| [T07](#t07) | Tipo | NUMERIC(10,2) arredonda 10,555 para 10,56 (sem erro de ponto flutuante) | OK | OK | ✅ PASSOU |
| [T08](#t08) | Tipo | Status fora do ENUM status_os | ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |
| [T09](#t09) | Tipo | Data inexistente (30/02) em TIMESTAMP | ERRO 22008 | ERRO 22008 | ✅ PASSOU |
| [T10](#t10) | Tipo | CPF com pontuação viola o domínio dm_doc | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [T11](#t11) | Tipo | Telefone com letras viola o domínio dm_telefone | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R01](#r01) | Restrição | NOT NULL: cliente sem nome | ERRO 23502 | ERRO 23502 | ✅ PASSOU |
| [R02](#r02) | Restrição | UNIQUE: CPF/CNPJ repetido | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| [R03](#r03) | Restrição | UNIQUE: placa repetida | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| [R04](#r04) | Restrição | FOREIGN KEY: veículo de cliente inexistente | ERRO 23503 | ERRO 23503 | ✅ PASSOU |
| [R05](#r05) | Restrição | ON DELETE RESTRICT: excluir cliente que tem veículos | ERRO 23503 | ERRO 23503 | ✅ PASSOU |
| [R06](#r06) | Restrição | CHECK: km do veículo negativo | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R07](#r07) | Restrição | CHECK: conclusão antes da abertura | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R08](#r08) | Restrição | CHECK: OS CONCLUIDA sem data de conclusão | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R09](#r09) | Restrição | CHECK: desconto maior que a mão de obra | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R10](#r10) | Restrição | PRIMARY KEY composta: mesma peça duas vezes na OS | ERRO 23505 | ERRO 23505 | ✅ PASSOU |
| [R11](#r11) | Restrição | CHECK: quantidade zero de peça | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R12](#r12) | Restrição | CHECK: e-mail sem @ | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [R13](#r13) | Restrição | ON DELETE CASCADE: excluir OS aberta remove seus itens | OK | OK | ✅ PASSOU |
| [G01](#g01) | Regra | Lançar peça na OS baixa o estoque automaticamente | OK | OK | ✅ PASSOU |
| [G02](#g02) | Regra | Estoque insuficiente bloqueia o lançamento | ERRO 23514 | ERRO 23514 | ✅ PASSOU |
| [G03](#g03) | Regra | Preço da peça é copiado do catálogo quando omitido | OK | OK | ✅ PASSOU |
| [G04](#g04) | Regra | OS CONCLUIDA não aceita novas peças | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| [G05](#g05) | Regra | Mecânico inativo não pode assumir OS | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| [G06](#g06) | Regra | Hodômetro não pode voltar (km_entrada < km_atual) | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| [G07](#g07) | Regra | OS CONCLUIDA não pode ser reaberta | ERRO P0001 | ERRO P0001 | ✅ PASSOU |
| [G08](#g08) | Regra | Cancelar a OS devolve as peças ao estoque | OK | OK | ✅ PASSOU |
| [G09](#g09) | Regra | Mão de obra = horas trabalhadas x valor/hora do mecânico | OK | OK | ✅ PASSOU |
| [G10](#g10) | Regra | Fluxo completo: abrir, lançar peças, concluir e faturar | OK | OK | ✅ PASSOU |

## 1. Testes de tipos de dados (T01–T11)

Cada teste tenta gravar um valor que o tipo ou o domínio deve aceitar ou recusar.

<a id="t01"></a>

### T01 — Placa com 8 caracteres não cabe em CHAR(7)

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22001 | ERRO 22001 | ✅ PASSOU |

**Resposta do banco:** `value too long for type character(7)`

Arquivos: [SQL do teste](T01_placa_com_8_caracteres_nao_cabe_em_char_7.sql) · [log completo](../evidencias/resultados/T01_placa_com_8_caracteres_nao_cabe_em_char_7.txt)

![T01](../evidencias/capturas/T01_placa_com_8_caracteres_nao_cabe_em_char_7.png)

[↑ voltar ao índice](#índice)

<a id="t02"></a>

### T02 — Placa fora do padrão (domínio dm_placa)

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `value for domain dm_placa violates check constraint "dm_placa_check"`

Arquivos: [SQL do teste](T02_placa_fora_do_padrao_dominio_dm_placa.sql) · [log completo](../evidencias/resultados/T02_placa_fora_do_padrao_dominio_dm_placa.txt)

![T02](../evidencias/capturas/T02_placa_fora_do_padrao_dominio_dm_placa.png)

[↑ voltar ao índice](#índice)

<a id="t03"></a>

### T03 — Placa Mercosul válida é aceita

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](T03_placa_mercosul_valida_e_aceita.sql) · [log completo](../evidencias/resultados/T03_placa_mercosul_valida_e_aceita.txt)

![T03](../evidencias/capturas/T03_placa_mercosul_valida_e_aceita.png)

[↑ voltar ao índice](#índice)

<a id="t04"></a>

### T04 — Texto em coluna SMALLINT (ano)

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |

**Resposta do banco:** `invalid input syntax for type smallint: "dois mil"`

Arquivos: [SQL do teste](T04_texto_em_coluna_smallint_ano.sql) · [log completo](../evidencias/resultados/T04_texto_em_coluna_smallint_ano.txt)

![T04](../evidencias/capturas/T04_texto_em_coluna_smallint_ano.png)

[↑ voltar ao índice](#índice)

<a id="t05"></a>

### T05 — Ano 40000 estoura o limite de SMALLINT

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22003 | ERRO 22003 | ✅ PASSOU |

**Resposta do banco:** `smallint out of range`

Arquivos: [SQL do teste](T05_ano_40000_estoura_o_limite_de_smallint.sql) · [log completo](../evidencias/resultados/T05_ano_40000_estoura_o_limite_de_smallint.txt)

![T05](../evidencias/capturas/T05_ano_40000_estoura_o_limite_de_smallint.png)

[↑ voltar ao índice](#índice)

<a id="t06"></a>

### T06 — Valor acima de NUMERIC(10,2) é rejeitado

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22003 | ERRO 22003 | ✅ PASSOU |

**Resposta do banco:** `numeric field overflow`

Arquivos: [SQL do teste](T06_valor_acima_de_numeric_10_2_e_rejeitado.sql) · [log completo](../evidencias/resultados/T06_valor_acima_de_numeric_10_2_e_rejeitado.txt)

![T06](../evidencias/capturas/T06_valor_acima_de_numeric_10_2_e_rejeitado.png)

[↑ voltar ao índice](#índice)

<a id="t07"></a>

### T07 — NUMERIC(10,2) arredonda 10,555 para 10,56 (sem erro de ponto flutuante)

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](T07_numeric_10_2_arredonda_10_555_para_10_56_sem_.sql) · [log completo](../evidencias/resultados/T07_numeric_10_2_arredonda_10_555_para_10_56_sem_.txt)

![T07](../evidencias/capturas/T07_numeric_10_2_arredonda_10_555_para_10_56_sem_.png)

[↑ voltar ao índice](#índice)

<a id="t08"></a>

### T08 — Status fora do ENUM status_os

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22P02 | ERRO 22P02 | ✅ PASSOU |

**Resposta do banco:** `invalid input value for enum status_os: "FINALIZADA"`

Arquivos: [SQL do teste](T08_status_fora_do_enum_status_os.sql) · [log completo](../evidencias/resultados/T08_status_fora_do_enum_status_os.txt)

![T08](../evidencias/capturas/T08_status_fora_do_enum_status_os.png)

[↑ voltar ao índice](#índice)

<a id="t09"></a>

### T09 — Data inexistente (30/02) em TIMESTAMP

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 22008 | ERRO 22008 | ✅ PASSOU |

**Resposta do banco:** `date/time field value out of range: "2026-02-30 10:00"`

Arquivos: [SQL do teste](T09_data_inexistente_30_02_em_timestamp.sql) · [log completo](../evidencias/resultados/T09_data_inexistente_30_02_em_timestamp.txt)

![T09](../evidencias/capturas/T09_data_inexistente_30_02_em_timestamp.png)

[↑ voltar ao índice](#índice)

<a id="t10"></a>

### T10 — CPF com pontuação viola o domínio dm_doc

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `value for domain dm_doc violates check constraint "dm_doc_check"`

Arquivos: [SQL do teste](T10_cpf_com_pontuacao_viola_o_dominio_dm_doc.sql) · [log completo](../evidencias/resultados/T10_cpf_com_pontuacao_viola_o_dominio_dm_doc.txt)

![T10](../evidencias/capturas/T10_cpf_com_pontuacao_viola_o_dominio_dm_doc.png)

[↑ voltar ao índice](#índice)

<a id="t11"></a>

### T11 — Telefone com letras viola o domínio dm_telefone

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `value for domain dm_telefone violates check constraint "dm_telefone_check"`

Arquivos: [SQL do teste](T11_telefone_com_letras_viola_o_dominio_dm_telefo.sql) · [log completo](../evidencias/resultados/T11_telefone_com_letras_viola_o_dominio_dm_telefo.txt)

![T11](../evidencias/capturas/T11_telefone_com_letras_viola_o_dominio_dm_telefo.png)

[↑ voltar ao índice](#índice)

## 2. Testes de restrições (R01–R13)

NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY (RESTRICT/CASCADE) e CHECK.

<a id="r01"></a>

### R01 — NOT NULL: cliente sem nome

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23502 | ERRO 23502 | ✅ PASSOU |

**Resposta do banco:** `null value in column "nome" of relation "cliente" violates not-null constraint`

Arquivos: [SQL do teste](R01_not_null_cliente_sem_nome.sql) · [log completo](../evidencias/resultados/R01_not_null_cliente_sem_nome.txt)

![R01](../evidencias/capturas/R01_not_null_cliente_sem_nome.png)

[↑ voltar ao índice](#índice)

<a id="r02"></a>

### R02 — UNIQUE: CPF/CNPJ repetido

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23505 | ERRO 23505 | ✅ PASSOU |

**Resposta do banco:** `duplicate key value violates unique constraint "uq_cliente_doc"`

Arquivos: [SQL do teste](R02_unique_cpf_cnpj_repetido.sql) · [log completo](../evidencias/resultados/R02_unique_cpf_cnpj_repetido.txt)

![R02](../evidencias/capturas/R02_unique_cpf_cnpj_repetido.png)

[↑ voltar ao índice](#índice)

<a id="r03"></a>

### R03 — UNIQUE: placa repetida

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23505 | ERRO 23505 | ✅ PASSOU |

**Resposta do banco:** `duplicate key value violates unique constraint "uq_veiculo_placa"`

Arquivos: [SQL do teste](R03_unique_placa_repetida.sql) · [log completo](../evidencias/resultados/R03_unique_placa_repetida.txt)

![R03](../evidencias/capturas/R03_unique_placa_repetida.png)

[↑ voltar ao índice](#índice)

<a id="r04"></a>

### R04 — FOREIGN KEY: veículo de cliente inexistente

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23503 | ERRO 23503 | ✅ PASSOU |

**Resposta do banco:** `insert or update on table "veiculo" violates foreign key constraint "veiculo_id_cliente_fkey"`

Arquivos: [SQL do teste](R04_foreign_key_veiculo_de_cliente_inexistente.sql) · [log completo](../evidencias/resultados/R04_foreign_key_veiculo_de_cliente_inexistente.txt)

![R04](../evidencias/capturas/R04_foreign_key_veiculo_de_cliente_inexistente.png)

[↑ voltar ao índice](#índice)

<a id="r05"></a>

### R05 — ON DELETE RESTRICT: excluir cliente que tem veículos

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23503 | ERRO 23503 | ✅ PASSOU |

**Resposta do banco:** `update or delete on table "cliente" violates foreign key constraint "veiculo_id_cliente_fkey" on table "veiculo"`

Arquivos: [SQL do teste](R05_on_delete_restrict_excluir_cliente_que_tem_ve.sql) · [log completo](../evidencias/resultados/R05_on_delete_restrict_excluir_cliente_que_tem_ve.txt)

![R05](../evidencias/capturas/R05_on_delete_restrict_excluir_cliente_que_tem_ve.png)

[↑ voltar ao índice](#índice)

<a id="r06"></a>

### R06 — CHECK: km do veículo negativo

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "veiculo" violates check constraint "veiculo_km_atual_check"`

Arquivos: [SQL do teste](R06_check_km_do_veiculo_negativo.sql) · [log completo](../evidencias/resultados/R06_check_km_do_veiculo_negativo.txt)

![R06](../evidencias/capturas/R06_check_km_do_veiculo_negativo.png)

[↑ voltar ao índice](#índice)

<a id="r07"></a>

### R07 — CHECK: conclusão antes da abertura

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "ordem_servico" violates check constraint "ck_os_datas"`

Arquivos: [SQL do teste](R07_check_conclusao_antes_da_abertura.sql) · [log completo](../evidencias/resultados/R07_check_conclusao_antes_da_abertura.txt)

![R07](../evidencias/capturas/R07_check_conclusao_antes_da_abertura.png)

[↑ voltar ao índice](#índice)

<a id="r08"></a>

### R08 — CHECK: OS CONCLUIDA sem data de conclusão

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "ordem_servico" violates check constraint "ck_os_concluida"`

Arquivos: [SQL do teste](R08_check_os_concluida_sem_data_de_conclusao.sql) · [log completo](../evidencias/resultados/R08_check_os_concluida_sem_data_de_conclusao.txt)

![R08](../evidencias/capturas/R08_check_os_concluida_sem_data_de_conclusao.png)

[↑ voltar ao índice](#índice)

<a id="r09"></a>

### R09 — CHECK: desconto maior que a mão de obra

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "ordem_servico" violates check constraint "ck_os_desconto"`

Arquivos: [SQL do teste](R09_check_desconto_maior_que_a_mao_de_obra.sql) · [log completo](../evidencias/resultados/R09_check_desconto_maior_que_a_mao_de_obra.txt)

![R09](../evidencias/capturas/R09_check_desconto_maior_que_a_mao_de_obra.png)

[↑ voltar ao índice](#índice)

<a id="r10"></a>

### R10 — PRIMARY KEY composta: mesma peça duas vezes na OS

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23505 | ERRO 23505 | ✅ PASSOU |

**Resposta do banco:** `duplicate key value violates unique constraint "pk_os_peca"`

Arquivos: [SQL do teste](R10_primary_key_composta_mesma_peca_duas_vezes_na.sql) · [log completo](../evidencias/resultados/R10_primary_key_composta_mesma_peca_duas_vezes_na.txt)

![R10](../evidencias/capturas/R10_primary_key_composta_mesma_peca_duas_vezes_na.png)

[↑ voltar ao índice](#índice)

<a id="r11"></a>

### R11 — CHECK: quantidade zero de peça

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "os_peca" violates check constraint "os_peca_quantidade_check"`

Arquivos: [SQL do teste](R11_check_quantidade_zero_de_peca.sql) · [log completo](../evidencias/resultados/R11_check_quantidade_zero_de_peca.txt)

![R11](../evidencias/capturas/R11_check_quantidade_zero_de_peca.png)

[↑ voltar ao índice](#índice)

<a id="r12"></a>

### R12 — CHECK: e-mail sem @

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "cliente" violates check constraint "cliente_email_check"`

Arquivos: [SQL do teste](R12_check_e_mail_sem.sql) · [log completo](../evidencias/resultados/R12_check_e_mail_sem.txt)

![R12](../evidencias/capturas/R12_check_e_mail_sem.png)

[↑ voltar ao índice](#índice)

<a id="r13"></a>

### R13 — ON DELETE CASCADE: excluir OS aberta remove seus itens

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](R13_on_delete_cascade_excluir_os_aberta_remove_se.sql) · [log completo](../evidencias/resultados/R13_on_delete_cascade_excluir_os_aberta_remove_se.txt)

![R13](../evidencias/capturas/R13_on_delete_cascade_excluir_os_aberta_remove_se.png)

[↑ voltar ao índice](#índice)

## 3. Testes de regras de negócio (G01–G10)

Regras implementadas com gatilhos (triggers) em `sql/02_regras_triggers.sql`.

<a id="g01"></a>

### G01 — Lançar peça na OS baixa o estoque automaticamente

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](G01_lancar_peca_na_os_baixa_o_estoque_automaticam.sql) · [log completo](../evidencias/resultados/G01_lancar_peca_na_os_baixa_o_estoque_automaticam.txt)

![G01](../evidencias/capturas/G01_lancar_peca_na_os_baixa_o_estoque_automaticam.png)

[↑ voltar ao índice](#índice)

<a id="g02"></a>

### G02 — Estoque insuficiente bloqueia o lançamento

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO 23514 | ERRO 23514 | ✅ PASSOU |

**Resposta do banco:** `new row for relation "peca" violates check constraint "ck_peca_estoque_nao_negativo"`

Arquivos: [SQL do teste](G02_estoque_insuficiente_bloqueia_o_lancamento.sql) · [log completo](../evidencias/resultados/G02_estoque_insuficiente_bloqueia_o_lancamento.txt)

![G02](../evidencias/capturas/G02_estoque_insuficiente_bloqueia_o_lancamento.png)

[↑ voltar ao índice](#índice)

<a id="g03"></a>

### G03 — Preço da peça é copiado do catálogo quando omitido

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](G03_preco_da_peca_e_copiado_do_catalogo_quando_om.sql) · [log completo](../evidencias/resultados/G03_preco_da_peca_e_copiado_do_catalogo_quando_om.txt)

![G03](../evidencias/capturas/G03_preco_da_peca_e_copiado_do_catalogo_quando_om.png)

[↑ voltar ao índice](#índice)

<a id="g04"></a>

### G04 — OS CONCLUIDA não aceita novas peças

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO P0001 | ERRO P0001 | ✅ PASSOU |

**Resposta do banco:** `OS 1 está CONCLUIDA e não aceita alteração de peças`

Arquivos: [SQL do teste](G04_os_concluida_nao_aceita_novas_pecas.sql) · [log completo](../evidencias/resultados/G04_os_concluida_nao_aceita_novas_pecas.txt)

![G04](../evidencias/capturas/G04_os_concluida_nao_aceita_novas_pecas.png)

[↑ voltar ao índice](#índice)

<a id="g05"></a>

### G05 — Mecânico inativo não pode assumir OS

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO P0001 | ERRO P0001 | ✅ PASSOU |

**Resposta do banco:** `Mecânico 23 está inativo e não pode assumir OS`

Arquivos: [SQL do teste](G05_mecanico_inativo_nao_pode_assumir_os.sql) · [log completo](../evidencias/resultados/G05_mecanico_inativo_nao_pode_assumir_os.txt)

![G05](../evidencias/capturas/G05_mecanico_inativo_nao_pode_assumir_os.png)

[↑ voltar ao índice](#índice)

<a id="g06"></a>

### G06 — Hodômetro não pode voltar (km_entrada < km_atual)

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO P0001 | ERRO P0001 | ✅ PASSOU |

**Resposta do banco:** `km_entrada (72000) menor que o km já registrado do veículo (73000)`

Arquivos: [SQL do teste](G06_hodometro_nao_pode_voltar_km_entrada_km_atual.sql) · [log completo](../evidencias/resultados/G06_hodometro_nao_pode_voltar_km_entrada_km_atual.txt)

![G06](../evidencias/capturas/G06_hodometro_nao_pode_voltar_km_entrada_km_atual.png)

[↑ voltar ao índice](#índice)

<a id="g07"></a>

### G07 — OS CONCLUIDA não pode ser reaberta

| Esperado | Obtido | Resultado |
|---|---|---|
| ERRO P0001 | ERRO P0001 | ✅ PASSOU |

**Resposta do banco:** `OS 1 já está CONCLUIDA e não pode mudar para ABERTA`

Arquivos: [SQL do teste](G07_os_concluida_nao_pode_ser_reaberta.sql) · [log completo](../evidencias/resultados/G07_os_concluida_nao_pode_ser_reaberta.txt)

![G07](../evidencias/capturas/G07_os_concluida_nao_pode_ser_reaberta.png)

[↑ voltar ao índice](#índice)

<a id="g08"></a>

### G08 — Cancelar a OS devolve as peças ao estoque

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](G08_cancelar_a_os_devolve_as_pecas_ao_estoque.sql) · [log completo](../evidencias/resultados/G08_cancelar_a_os_devolve_as_pecas_ao_estoque.txt)

![G08](../evidencias/capturas/G08_cancelar_a_os_devolve_as_pecas_ao_estoque.png)

[↑ voltar ao índice](#índice)

<a id="g09"></a>

### G09 — Mão de obra = horas trabalhadas x valor/hora do mecânico

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](G09_mao_de_obra_horas_trabalhadas_x_valor_hora_do.sql) · [log completo](../evidencias/resultados/G09_mao_de_obra_horas_trabalhadas_x_valor_hora_do.txt)

![G09](../evidencias/capturas/G09_mao_de_obra_horas_trabalhadas_x_valor_hora_do.png)

[↑ voltar ao índice](#índice)

<a id="g10"></a>

### G10 — Fluxo completo: abrir, lançar peças, concluir e faturar

| Esperado | Obtido | Resultado |
|---|---|---|
| OK | OK | ✅ PASSOU |

**Resposta do banco:** `verificação = PASSOU`

Arquivos: [SQL do teste](G10_fluxo_completo_abrir_lancar_pecas_concluir_e_.sql) · [log completo](../evidencias/resultados/G10_fluxo_completo_abrir_lancar_pecas_concluir_e_.txt)

![G10](../evidencias/capturas/G10_fluxo_completo_abrir_lancar_pecas_concluir_e_.png)

[↑ voltar ao índice](#índice)
