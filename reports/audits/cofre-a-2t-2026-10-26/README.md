# Cofre A 2T — auditoria metodológica após o prazo

**Data:** 26/10/2026, Brasília. **Tipo:** DOCS / RED_TEAM / auditoria de processo.
**Conclusão:** `NO_VALID_PROSPECTIVE_FREEZE_EVIDENCED`.
**Consequência:** `NOT_EVALUABLE_PROSPECTIVELY` para o endpoint presidencial 2T de 2026.

Nas referências remotas e no histórico alcançável consultados, **não foi encontrado
congelamento prospectivo válido publicado antes do prazo**. O PR #3 permanece
aberto e draft, no commit `5691f15f20feeaa10decb2abbbc11dc150f162f3`; o estado
entregue é `BLOCKED`, sem inputs completos, calibração ou estimativa.
O prazo de 25/10/2026 às 17:00 BRT (20:00 UTC, limite exclusivo) expirou.

Este é o encerramento operacional da oportunidade prospectiva demonstrada, não uma
alegação de onisciência sobre referências apagadas, clones privados ou publicações
externas. Não foram fornecidos comprovantes desses canais. Se surgir evidência
contemporânea verificável, acrescentar uma nova auditoria; não reescrever esta nem
criar uma tag com data passada. Até lá, não há base para avaliar acerto/erro de uma
previsão prospectiva do Cofre A 2T.

## 1. Escopo, fontes e força da evidência

Foram consultados, antes da criação da branch desta auditoria:

| Superfície remota | Resultado observado | Evidência local |
|---|---|---|
| Referências Git | 10 refs: 4 branches e 6 refs de PR; **0 tags** | `evidence/refs.json` |
| Consulta específica de refs de tags | Lista vazia | `evidence/tag_refs.json` |
| Releases | Lista vazia | `evidence/releases.json` |
| PRs | #1, #2, #3 abertos; nenhuma auditoria posterior já publicada nessa coleção | `evidence/pr_list.json` |
| PR #3 | Aberto/draft, sem merge; 4 commits; última atualização `2026-10-19T00:33:41Z` | `evidence/pr.json` |
| Histórico das 4 branches | 10 commits distintos ao todo; nenhum posterior ao head de 19/10 UTC | `evidence/history_0.json` a `history_3.json` |
| Histórico da saída 2T | Duas versões: `67572a6…` e `5691f15…`, ambas `BLOCKED` | `evidence/output_history.json`, `output_initial.json`, `output_current.json` |
| Comentários do PR #3 | Lista vazia | `evidence/comments.json` |
| Actions | 6 execuções, todas anteriores ao prazo, todas concluídas com sucesso | `evidence/runs.json` |
| Artefatos de Actions | 0 artefatos retornados em cada uma das 6 execuções | `evidence/artifacts_run.json` e `artifacts_<id>.json` |
| Árvores 1T e 2T | Respostas recursivas não truncadas; 38 e 51 blobs | `evidence/tree_1t.json`, `tree.json` |

As coleções pagináveis foram solicitadas com `per_page=100` e retornaram menos de
100 itens; Actions declara `total_count=6`, sem página restante. As refs de merge
de PR são referências técnicas do GitHub, não tags de congelamento nem prova de
merge na branch principal. `main` ainda aponta para `628bea69766ea997fba48bde7e05443593992cc8`.

As respostas da API foram preservadas como JSON, com URL e momento local de
captura. O envelope foi serializado para leitura; não se afirma preservação dos
bytes HTTP originais da API. Os raw do TSE, em contraste, são bytes originais.
`integrity.json` sela por SHA-256 os arquivos do pacote; o commit desta auditoria
identifica sua versão. Esses hashes **não** constituem carimbo temporal pré-eleitoral.

Limitações da busca: o conector recusou o endpoint de eventos do repositório, a
coleção `/tags` e a coleção global de artefatos; os erros estão guardados. As tags
foram verificadas pelas referências Git completas e pela consulta específica
`git/matching-refs/tags/`, ambas bem-sucedidas. A busca de artefatos foi
suprida pelas seis consultas por execução, mas o log de eventos não foi obtido.
Não houve acesso ao reflog remoto, audit log administrativo, refs apagadas ou
objetos inacessíveis. Assim, ausência atual de tag não prova, isoladamente, que
nunca houve uma tag. O desfecho decorre da combinação dessa ausência com as
duas versões bloqueadas, a falta de inputs e a falta de comprovação de publicação.

## 2. Referências e cronologia verificadas

| Branch | Head observado |
|---|---|
| `main` | `628bea69766ea997fba48bde7e05443593992cc8` |
| `claude/analise-dialogo-anterior-ttqrk4` | `c377991a9dd645ec77df903179b0b44f4b54bfc7` |
| `codex/cofre-a-freeze-1t` | `d92008b5bae107c0c380209931c31f07a911cba4` |
| `codex/cofre-a-prospectivo-2t` | `5691f15f20feeaa10decb2abbbc11dc150f162f3` |

| Objeto / evento | Instante registrado (UTC) | Significado |
|---|---|---|
| Introdução do PREREG-0001, `c377991…` | 11/09/2026 01:40:22 | Define método; não fornece uma estimativa congelada |
| Implementação 2T, `985f605…` | 18/10/2026 22:08:16 | Ferramentas e verificações |
| Primeiro manifesto 2T, `67572a6…` | 18/10/2026 22:08:25 | Preparação `BLOCKED` |
| Reforço de integridade, `b2c5ed9…` | 19/10/2026 00:32:50 | Código; sem aquisição certificada |
| Último manifesto 2T, `5691f15…` | 19/10/2026 00:32:57 | Preparação `BLOCKED` atualizada |
| CI 39181274071 | 19/10/2026 00:33:02–00:33:27 | 76 testes; reprodução da preparação bloqueada |
| Cutoff de divulgação das pesquisas | 25/10/2026 15:00:00 | 12:00 BRT, inclusivo |
| Limite para commit/tag/publicação | 25/10/2026 20:00:00 | 17:00 BRT, exclusivo |

As datas de commit são metadados Git declarados, alteráveis por quem cria objetos;
não provam o momento de publicação remota. Os timestamps do CI fornecem evidência
da execução daquele código no GitHub, mas não da existência de um freeze pronto.
Os eventos de 19/10 às 00h UTC correspondem a 18/10 às 21h de Brasília.

O critério aplicado é o que já consta no PREREG-0001 §5/§13 e no procedimento
operacional do PR #3. Não se estende o limite por eventual alteração externa do
horário de votação ou por horário de divulgação do resultado. A auditoria não
modifica a janela nem introduz novos critérios retroativos de elegibilidade.

## 3. O que efetivamente foi concluído

1. Preregistro do estimador e da hipótese candidato × bloco, com endpoint 2T
   secundário, janela, denominador, famílias, limiares e sensibilidades registrados.
2. Implementação de ingestão com proveniência, elegibilidade, preservação de
   artefatos, verificação de hashes, fechamento temporal e tag local anotada.
3. Separação dos ledgers, revisão de famílias, saída e manifesto do segundo turno.
4. Aquisição histórica parcial: resultados TSE e inventários de registros PesqEle
   de 2014/2018/2022 presentes na árvore; isso não completa a coleta numérica das pesquisas.
5. Validação automatizada do código: o log do job `117834340248` contém
   `Ran 76 tests in 8.321s` e `OK`, e a etapa de reprodução do 2T imprime `BLOCKED`.
6. Preservação no PR #3: 37 dos 38 blobs da base 1T têm o mesmo SHA Git; a única
   alteração preexistente é `.github/workflows/cofre-a.yml`, para reproduzir 1T
   isoladamente. Prereg, estimador, dados e artefatos 1T permaneceram idênticos.

**Teste aprovado não significa cobertura certificada nem previsão emitida.**
A suíte usa exemplos sintéticos para verificar guardas; suas tags temporárias de
teste não são publicações reais do Cofre A.

## 4. Requisitos insatisfeitos no estado publicado

| Requisito | Evidência | Consequência |
|---|---|---|
| Inventário nacional completo e auditado de 2026 | `status=NOT_COLLECTED`, `complete=false`, `rows=[]`, `sources=[]` | Não há seleção auditável de pesquisas |
| Packet e cobertura fechada | `collection_complete=false`, `packet=null`, `coverage_as_of=null` | Não há selo de inputs |
| Dois classificados, alvo PL/endosso e adversário certificados | `c_star=null`, `adv=null`; documentação exige fontes ainda ausentes | Identidades não certificadas no processo prospectivo |
| Identidades e continuidade de famílias | `complete=false`, `reviewer=null`, `table_sha256=null`, `families={}` | Mapeamento não auditado |
| Anos históricos completos nos dois turnos | 2014, 2018 e 2022 excluídos integralmente | `E_hist=[]`, tamanho 0 |
| Calibração numérica | `e_ref_2T=null`, `q90=null`, `sigma_hat=null` | Intervalos e hipótese central indisponíveis |
| Estimativa e intervalos | `P=null`, `intervals=null`, `INPUTS_INCOMPLETE` | Nenhum número prospectivo avaliável |
| Primeiro selo `READY_FOR_FREEZE` | Nenhuma das duas versões da saída tem esse estado | Não foi demonstrado fechamento válido antes da tag |
| Commit final no intervalo permitido | Manifestos existentes são de 18–19/10 UTC | Não são o fechamento requerido em 25/10 |
| Tag anotada e publicação tempestiva | Nenhuma tag atual; nenhuma evidência de publicação válida localizada | Freeze prospectivo não demonstrado |

Lista vazia de pesquisas não significa ausência de pesquisas elegíveis no mundo.
`INPUTS_INCOMPLETE` não é `NÃO_ESTIMÁVEL` por menos de três famílias: este último
exigiria coleta completa. `Q2=UNAVAILABLE` não é `VAZIA` por referência histórica
não positiva; referência ausente não é zero.

## 5. Verificações desta auditoria e preservação

- Os 46 blobs disponíveis no checkout local foram confrontados com os SHAs da
  árvore remota; cinco raw históricos grandes não foram transferidos localmente.
- Os 30 hashes de dependências efetivamente consumidas pelo manifesto 2T conferem;
  resultados detalhados estão em `evidence/dependency-hashes.json`.
- `python -m src.statistics.freeze_2t --verify-artifacts`: exit 0, `BLOCKED`.
- `python -m src.statistics.freeze_2t --check`: exit 1 pelos bloqueios de dados.
- A chamada isolada a `time_gate` com o relógio real de 26/10 rejeitou a data fora
  do intervalo. Não se usou relógio falso nem `--freeze` nesta auditoria.
- A nova normalização exploratória passou em sete testes, incluindo rejeição de
  simulado, turno errado, totalização parcial, contagens inconsistentes, identidade
  duplicada e mudança de destinação de votos. Log em `analysis/exploratory/2026-2t/validation.json`.

A suíte original completa não foi reexecutada **localmente** sem os cinco raw;
a evidência histórica completa do CI foi preservada. O novo PR herda o workflow
original sem modificações e acrescenta um workflow separado para esta auditoria.
Consultar os checks do novo PR para a execução sobre a entrega final; não confundir
essa execução pós-prazo com validação prospectiva.

Esta entrega é aditiva: preserva **todos os 51 blobs anteriores**, inclusive os
manifestos bloqueados, e não altera PR #1/#2/#3, suas branches ou tags. O status
pós-prazo reside em `status.json` aqui, não em substituição ao status histórico.
Não há merge, force-push, backdating ou criação de tags de freeze.

Reprodução, em um clone com esta branch:

```bash
python reports/audits/cofre-a-2t-2026-10-26/verify.py
python -m src.statistics.freeze_2t --verify-artifacts
python analysis/exploratory/2026-2t/reproduce.py --check
python -m unittest discover -s analysis/exploratory/2026-2t -p 'test_*.py' -v
```

`verify.py` confronta a árvore de HEAD com os 51 blobs originais e valida os
hashes do pacote. Não autentica timestamps antigos nem prova exaustividade dos
dados. O índice de hashes exclui a si próprio; a integridade desse índice e do
restante da entrega é ancorada pelo commit Git, não por uma tag prospectiva.

## 6. Desfecho científico e trilha separada

Q1/calibração e Q2/candidato × bloco **não são avaliáveis prospectivamente no 2T**
com o material publicado. Não se conclui que o modelo acertou, errou, confirmou
BLOCO, confirmou CANDIDATO ou teve calibração refutada. Tampouco se infere qualquer
irregularidade eleitoral dessa falha de execução de um projeto de pesquisa.
Não há classificação A/B/C/D substantiva da hipótese: ela não foi testada por um
forecast válido. Um teste não executado não é um teste negativo.

Foi aberta a [trilha exploratória pós-eleição](../../../analysis/exploratory/2026-2t/README.md),
com cópia oficial EA20 nacional de 2T, configuração, documentação, hashes, metadados,
normalização reproduzível e plano de aquisição/auditoria das pesquisas.
Os dados oficiais agora disponíveis são desfechos observados, não previsões.
`P` e todos os parâmetros prospectivos continuam `null` nessa trilha.

O desfecho foi adquirido em 26/10, e o agente também teve exposição a trechos
secundários de resultados durante a descoberta de fontes. Não se reivindica cegamento
ao resultado. Nenhum desses dados foi inserido no pipeline prospectivo ou usado
para completar retroativamente sua calibração. A decisão desta auditoria depende
de refs, artefatos, publicação e prazo, não de quem venceu.

O próximo trabalho possível é reconstrução **exploratória**, com proveniência e
limitações explícitas. Descobertas posteriores, mesmo publicadas originalmente
antes do pleito, não entram como se tivessem sido congeladas no Cofre A.

## 7. Fontes fixadas

- [PR #3](https://github.com/Drmcoelho/Eleicoes/pull/3), snapshot preservado em `evidence/pr.json`.
- [Procedimento no SHA auditado](https://github.com/Drmcoelho/Eleicoes/blob/5691f15f20feeaa10decb2abbbc11dc150f162f3/docs/cofre-a-freeze-2t.md).
- [Prereg no SHA auditado](https://github.com/Drmcoelho/Eleicoes/blob/5691f15f20feeaa10decb2abbbc11dc150f162f3/methodology/preregistration/0001-cofre-A-2026.md).
- [Manifesto de preparação](https://github.com/Drmcoelho/Eleicoes/blob/5691f15f20feeaa10decb2abbbc11dc150f162f3/methodology/preregistration/0001-freeze-manifest-2t.md).
- [Saída de preparação](https://github.com/Drmcoelho/Eleicoes/blob/5691f15f20feeaa10decb2abbbc11dc150f162f3/data/derived/cofre-a-2t-2026.json).
- [CI original](https://github.com/Drmcoelho/Eleicoes/actions/runs/39181274071), job/log em `evidence/`.
- Fontes oficiais pós-eleição e hashes: `analysis/exploratory/2026-2t/sources.json`.
