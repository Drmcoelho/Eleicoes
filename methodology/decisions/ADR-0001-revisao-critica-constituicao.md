# ADR-0001 — Revisão crítica da constituição (PROMPT.md v0.2.0 / AGENTS.md v1.0.0)

**Data:** 2026-09-11
**Status:** PROPOSTO
**Tipo:** revisão metodológica (não é bugfix, não é hipótese nova)
**Escopo:** `PROMPT.md` 0.2.0 (`0d52c4b`), `AGENTS.md` 1.0.0 (`628bea6`), rascunho v0.1 (`966c54e`)
**Classificação epistêmica deste documento:** `INFERÊNCIA` sobre os artefatos versionados; nenhum dado eleitoral foi consultado.

## 1. Contexto

Os dois documentos canônicos foram commitados em 2026-09-10. O primeiro turno de 2026 ocorre em
2026-10-04 e o segundo em 2026-10-25. Este ADR registra a primeira leitura adversarial da constituição,
conforme exigido por AGENTS §26 ("grandes mudanças de metodologia exigem changelog/ADR"), e propõe
correções antes de qualquer ingestão.

## 2. O que a constituição acerta

Preregistro com SHA e timestamp; dois cofres; missingness tipada; ancoragem temporal em `fieldwork_end`;
escala composicional (logit/ILR) em vez de K multiplicativo como modelo principal; hipóteses espelho
obrigatórias; `família ≠ onda`; portão de identificabilidade antes de estimar. Esses pontos não devem ser
afrouxados.

## 3. Problemas identificados

### 3.1 O calendário torna a ordem "inviolável" inexequível para 2026

AGENTS §1 e PROMPT §39 exigem coleta, inventário, auditoria, normalização e preregistro **antes** de
qualquer previsão. Faltam 23 dias para o primeiro turno. Se `pre-election-freeze-2026` não existir antes
da urna, o único teste prospectivo verdadeiro do projeto é perdido até 2030.

**Decisão proposta:** preregistrar o **estimador**, não a estimativa. O Cofre A é congelado como função
declarada sobre dados ainda não coletados, com regras de coleta fixadas no próprio prereg. Especificação
mínima aceitável:

- média simples de pesquisas com `fieldwork_end` nos últimos N dias (N preregistrado);
- house effect fixado em zero;
- incerteza tomada da distribuição empírica de `e_logit` de 2018 e 2022 (mesma janela, mesmo denominador);
- denominador único declarado (válidos), com regra explícita de conversão totais→válidos.

Crueza é aceitável. Ausência de freeze não é.

### 3.2 "Inventário cego ao desfecho" é ficção para eleições já conhecidas

O analista sabe o resultado de 2014, 2018 e 2022. O viés de HARKing reside na memória de quem escreve o
prereg, não na tabela bloqueada. Bloquear o join protege contra vazamento de dados; não protege contra
seleção de hipótese informada pelo desfecho.

**Decisão proposta:** substituir o rótulo único `CONFIRMATÓRIO` por dois:

- `CONFIRMATORY_RETROSPECTIVE` — prereg anterior ao join, mas desfecho publicamente conhecido; evidência
  no máximo de grau B salvo replicação prospectiva;
- `CONFIRMATORY_PROSPECTIVE` — desfecho desconhecido no momento do freeze; único caminho para grau A em
  hipóteses direcionais.

PROMPT §3 e AGENTS §11 devem ser emendados nessa direção.

### 3.3 Painel de governador não é permutável com o presidencial sem teste

27 UFs × 3 ciclos parece amostra rica, mas a distribuição de pesquisas por UF é extremamente assimétrica
(SP, MG, RJ, RS, BA dominam; vários estados têm uma ou duas pesquisas por ciclo, frequentemente de
instituto regional que não pesquisa presidencial). House effect só é transportável entre cargos para
famílias que pesquisam ambos no mesmo ciclo.

**Decisão proposta:** antes de o painel estadual informar qualquer parâmetro presidencial, preregistrar um
teste de exchangeability: correlação do erro por família entre cargo estadual e presidencial dentro do mesmo
ciclo, restrito a famílias presentes em ambos. Sem esse teste, o painel só alimenta sensibilidade.

### 3.4 `rho_BF` é parâmetro errado para o Cofre A e pergunta certa para o projeto

Não existe instância histórica de transferência Bolsonaro→herdeiro; `rho_BF` é não identificável antes da
urna (PROMPT §25 aplicado a PROMPT §20). O Cofre A não deve depender dele: as pesquisas de 2026 medem
Flávio Bolsonaro diretamente.

O que 2026 oferece como experimento natural é distinto: **a subestimação observada em 2022 estava presa ao
candidato ou ao bloco eleitoral?** Se o mecanismo é nonresponse diferencial do eleitorado bolsonarista, ele
reaparece com o herdeiro. Se era pessoal, não.

**Decisão proposta:** esta é a hipótese prospectiva central do freeze, com H+/H−/H0:

- H+ (bloco): `e_logit(Flávio, 2026)` tem mesmo sinal e magnitude comparável a `e_logit(Jair, 2022)` no
  primeiro turno, sob janela e denominador idênticos;
- H− (candidato): erro de sinal oposto ou magnitude significativamente menor;
- H0: erro indistinguível de zero dentro do intervalo histórico.

Critério numérico a definir no prereg, antes do freeze.

### 3.5 Com três presidenciais e correção de multiplicidade, quase nada alcançará grau A

Isso é consequência correta das regras, não defeito. Deve ser declarado agora: a classificação
variável-por-variável tende a produzir majoritariamente C; o forecast prospectivo repousará no modelo mais
simples. Evita a tentação de afrouxar critérios em outubro (AGENTS §27).

## 4. Problemas de execução

### 4.1 A constituição foi violada no segundo commit

A compressão v0.1→v0.2 (`966c54e`→`0d52c4b`) removeu 307 linhas e adicionou 89. É mudança substantiva
sem CHANGELOG, e a primeira versão já nasceu numerada 0.2.0. O que se perdeu eram as partes executáveis:
lista literal de colunas de proveniência, janelas D-1/D-3/D-7/D-14/D-30, listas de variáveis
comportamentais e demográficas. Esse conteúdo era o embrião do schema.

**Decisão proposta:** não devolver as listas ao prompt. Restaurá-las como artefatos legíveis por máquina
(`schema/polls.yaml`, `schema/results.yaml`, `methodology/preregistration/windows.yaml`) e registrar a
compressão em `CHANGELOG.md` retroativamente.

### 4.2 Duplicação entre PROMPT e AGENTS

Denominadores, datas, hipóteses espelho, red team e formato de relatório aparecem em ambos. Dois documentos
canônicos com regras sobrepostas divergirão.

**Decisão proposta:** AGENTS passa a referenciar seções do PROMPT por número; regra substantiva vive em um
único lugar.

### 4.3 Hierarquia de fontes torna a coleta histórica de pesquisas ilimitada

PesqEle fornece registro e metadados, não resultados. Resultados históricos estão em PDFs de institutos
dispersos por uma década. Um agregador secundário estruturado é a única base contínua desde 2002.

**Decisão proposta:** admitir agregador secundário como **índice de inventário** com flag `NOT_VERIFIED`,
verificando contra fonte primária apenas o subconjunto consumido por prereg. Resultados oficiais seguem o
caminho oposto: os CSVs de dados abertos do TSE são primários, estruturados e automatizáveis, e são o ponto
de partida da ingestão.

## 5. Sequência de commits proposta

1. `methodology/preregistration/0001-cofre-A-2026.md` — estimador cru (§3.1), hipótese candidato×bloco
   (§3.4), critério numérico, N e denominador fixados. Tag `pre-election-freeze-2026` antes de 2026-10-04.
2. `src/ingestion/tse/` — resultados oficiais 2014/2018/2022 com hash, manifest e testes de schema.
3. `schema/*.yaml` — colunas restauradas do v0.1 (§4.1).
4. `CHANGELOG.md` retroativo (§4.1).
5. `AGENTS.md` reduzido a referências cruzadas (§4.2).
6. Emenda de `PROMPT.md` §3 e `AGENTS.md` §11 com os dois rótulos confirmatórios (§3.2). Gera v0.3.0.

## 6. O que este ADR não decide

Não escolhe N, não escolhe institutos, não define critérios numéricos, não abre desfechos. Tudo isso
pertence ao prereg 0001.
