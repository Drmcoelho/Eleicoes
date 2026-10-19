# Cofre A — operação prospectiva do segundo turno

Implementação do PREREG-0001, sem emenda e sem alterar artefatos do primeiro turno.
A preparação inicial é **BLOCKED**: não certifica cobertura, famílias, candidaturas
nem números de pesquisa. Os anos 2014/2018/2022 continuam excluídos integralmente
por coleta incompleta; nenhum parâmetro é imputado. Não se recupera retroativamente
o freeze de 1T, cujo prazo expirou. O 2T é o endpoint secundário já registrado.

## Comandos

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.statistics.freeze_2t
python -m src.statistics.freeze_2t --verify-artifacts
python -m src.statistics.freeze_2t --check
```

Preparar/regenerar e verificar reprodução não autorizam congelar. `--check` deve
falhar enquanto BLOCKED, antes do cutoff, depois do prazo ou com árvore suja.
O relógio é UTC com limites explícitos `-03:00`, independente do fuso da máquina.
Não existe argumento CLI para fingir outra hora.

## Aquisição: preservar antes de transcrever

A aquisição é deliberadamente explícita: baixar/exportar do PesqEle e da fonte
primária do instituto os originais integrais, sem filtrá-los pelo placar. Capturar
registros da janela 11–24/10, comprovar abrangência nacional (registro BR não basta),
obter divulgação numérica, questionário, modo e identidade legal. Inventariar todas
as ondas antes de selecionar uma por família. Fontes secundárias só para lacunas,
com essa condição registrada. Não buscar totalizações/votos de 2026. A comprovação
dos classificados deve conter a identidade/status dos dois candidatos, sem votos.

```bash
python -m src.ingestion.prospective --file /caminho/original.pdf \
  --url https://fonte-original/documento.pdf --kind publication \
  --location 'página 8, tabela 2, pergunta estimulada do segundo turno'
```

O comando importa bytes locais e imprime uma referência com `path`, `sha256`,
`url`, `retrieved_at`, `location`, `kind` e `status=UNREVIEWED`. Não declara ter
baixado a URL nem transforma um PDF em raw limpo. Repetição idêntica preserva o
primeiro registro; conteúdo ou metadados diferentes geram nova versão, nunca
sobrescrita. Tipos aceitos: registration, publication, official_candidates,
endorsement, family, coverage. O importador não decide elegibilidade nem audita
semanticamente o documento; isso exige leitura humana. Nunca importar resultados
2026 neste canal. Não fornecer um URL de exemplo como evidência real.

## Contratos versionados

1. `data/canonical/prospective-2t-inventory.json`: `year=2026`, `turn=2`, `sources`
   para a busca/inventário original e `rows`. Cada linha contém `poll_id`,
   `registration`, `institute`, `fieldwork_start`, `fieldwork_end`, `sources`,
   `office`, `scope`, `exit_poll`, `mode`, `sample_size`, `institute_legal_id` e
   `published_at`, reconciliados com o packet. Ao concluir: `status=AUDITED`, `complete=true`.
   Preservar CNPJ, escopo, contratante, duplicações de origem e decisão de auditoria
   como metadados adicionais. Consolidar duplicações do mesmo registro com evidência,
   sem multiplicar ondas. Inventário vazio inicial significa NOT_COLLECTED.
2. Packet JSON, apontado por `prospective-2t-status.json`, segue o contrato do
   `docs/cofre-a-freeze.md`, acrescentando as verificações abaixo. Não há packet
   preenchido com candidatos ou pesquisas fictícios no dataset canônico.
3. `official_candidates`: `names` com exatamente dois nomes únicos, `tse_ids`
   bijetivo, `status=CLASSIFICADOS_2T` e `sources` oficiais. `target` exige `name`,
   `party=PL`, `endorser=Jair Bolsonaro`, `sources` da candidatura e do endosso.
   Ausência do alvo no 2T bloqueia para revisão explícita, sem inventar substituto.
4. Poll: campos originais do contrato de 1T, `year=2026`, `turn=2`,
   `institute_legal_id`, `sources`; cada cenário também tem `sources` com página/
   tabela/pergunta e valores/denominador originais. Nenhum cenário hipotético,
   espontâneo ou com candidato extra vira uma disputa oficial de 2T.
5. `coverage`: `complete=true`, `reviewer`, `method`, `sources`,
   `as_of` com fuso, `inventory_sha256`, `inventory_poll_ids`, `not_published`,
   `no_2026_outcomes_used=true`. Fechar somente após 25/10 12:00 e antes de 17:00
   BRT. Reconciliar cada linha do inventário ao packet ou a exclusão tipada com
   motivo detalhado e fontes. Incluir pesquisas descartadas por janela/escopo no
   packet para o estimador registrar a exclusão, em vez de removê-las silenciosamente.
   Nenhum booleano, hash ou teste prova sozinho exaustividade ou transcrição fiel.
6. `sources/institutes/families-2t.yaml` é cópia inicial isolada da tabela de 1T.
   `families-2t-review.json`: `complete`, `reviewer`, `table_sha256` e `families`
   indexadas pela família, cada qual com `basis`, `legal_identities` e `sources`.
   Conferir identidades/controladores/sucessões usadas nos históricos e no 2T.
   Aliases exatos, sem fusão automática por semelhança. Instituto não mapeado
   continua como família própria com UNMAPPED_FAMILY, conforme §4.4.
7. `historical-coverage-2t.json`: revisão própria para o 2T, sem editar a de 1T.
   Só marcar um ano completo com packets auditados dos DOIS turnos, `tse_manifest`
   original e `coverage_evidence` como lista de referências raw. Cenários históricos
   também exigem `sources`. O normalizador original reproduz os resultados de
   2014/2018/2022; nunca usa 2026. Referências e arquivos consumidos entram nos hashes.

A calibração reutiliza `historical`, `calibrate`, `aggregate` e `intervals` do PR #2.
`ê_ref(2T)` vem da linha Jair Bolsonaro/2022/2 de E_hist. q90 e SD continuam usando
os dois turnos dos anos completos; não são recalibrados contra 2026. Referência
não positiva implica Q2 VAZIA; referência ausente implica UNAVAILABLE/BLOCKED.
Menos de três famílias, com coleta completa, produz NÃO_ESTIMÁVEL sem P; dados
incompletos produzem INPUTS_INCOMPLETE, nunca um falso piso de famílias.

## Saídas, fechamento e referência

`data/derived/cofre-a-2t-2026.json` contém P/intervalos ou null, famílias, poll_ids,
selecionadas, substituídas e excluídas, c*/adv, calibração, anos excluídos, manifesto
de entradas e hashes da cadeia de dependências. O Markdown separado é
`methodology/preregistration/0001-freeze-manifest-2t.md`. Raw de anos excluídos não
é dependência consumida; a reprodução desses raw existentes continua testada no CI.
Nenhuma chamada de 2T escreve no manifesto ou na saída de 1T.

Depois do cutoff, concluir a auditoria, regenerar, revisar e commitar inputs e
saídas. O commit final de ambos os artefatos deve estar no intervalo de fechamento.
Apenas então, antes de 25/10/2026 17:00 BRT:

```bash
python -m src.statistics.freeze_2t --check
python -m src.statistics.freeze_2t --freeze
# Publicar uma única vez, no mesmo prazo, após conferir a tag local:
git push origin refs/tags/pre-election-freeze-2026-2t
```

`--freeze` executa a suíte, repete reprodução/estado/prazo, exige descendência do
commit base e preservação dos artefatos protegidos, e cria tag anotada sem force.
A anotação registra commit, momento, hashes dos dois artefatos e inputs. Não existe
push automático nem tag quando BLOCKED. Tags são imutáveis por convenção e por
este fluxo; proteção contra administrador remoto exige regra do repositório.
O verificador não substitui carimbo de tempo externo nem detecta relógio de SO
malicioso. O prazo de publicação remota deve ser respeitado pelo operador.

Uma preparação BLOCKED não sela inputs. Após a tag, não regenerar nem incorporar
novas pesquisas: registrar descobertas em `data/audit/late-discovery-2t.json` num
commit posterior, com poll_id, fontes, discovered_at, motivo e SHA do commit selado.
Não editar `prospective-2t-status.json` nem outputs do commit congelado. Dados
posteriores são auditoria, não revisão da previsão. Nunca criar/mover a tag de 1T
para aparentar cumprimento de prazo passado.

## CI e reprodução de 1T

A implementação de 1T inclui todos os arquivos novos no hash global. Regenerá-la
na árvore do 2T modificaria seu manifesto. Por isso o CI reproduz 1T num checkout
isolado do commit base original e 2T na árvore atual, além dos testes de preservação.
Esse isolamento é operacional; o prereg e o estimador permanecem byte a byte iguais.

## Integridade adicional do fechamento

O primeiro commit com saída `READY_FOR_FREEZE` sela o manifesto, mesmo antes da
criação da tag. A preparação `BLOCKED` pode evoluir; um manifesto pronto já
commitado não pode ser substituído silenciosamente para incorporar descobertas.
O verificador consulta o histórico desse arquivo, além da existência da tag.
Depois do selo, registrar novas pesquisas separadamente como late_discovery.

Antes de congelar, cada dependência e os dois artefatos são comparados byte a byte
com o conteúdo do commit exato. Isso também detecta alterações ocultas por flags
`assume-unchanged`/`skip-worktree` que um `git status` limpo não denuncia.

JSON não aceita chaves repetidas nem NaN/Infinity/overflow numérico; YAML não
aceita redefinição de famílias por chaves duplicadas. Caminhos de evidência devem
ser relativos e canônicos. Timestamps de aquisição são verificados também para
fontes históricas e famílias: devem anteceder o prazo e não podem estar no futuro
na hora da checagem final. Datas civis de publicação são interpretadas em Brasília
mesmo quando o timestamp original está em UTC. A suíte de freeze usa o mesmo
interpretador Python que executa o comando.
