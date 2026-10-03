# Preparação auditável do freeze prospectivo 1T

O PREREG-0001 do PR #1 é copiado sem alteração e continua sendo a regra. Este
trabalho não presume que o PR #1 já esteja mergeado nem muda sua descrição.

## Reprodução local, sem rede e sem desfecho de 2026

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.statistics.freeze_1t
python -m src.statistics.freeze_1t --check
```

O último comando deve retornar **BLOCKED** enquanto os dados estiverem incompletos.
Isso é uma barreira correta, não um teste unitário falhando. JSON e manifesto são
determinísticos, exceto os timestamps originais dos manifests de aquisição,
preservados após a primeira aquisição. Regenerar não altera os originais.

## Dados históricos efetivamente adquiridos

Os membros BR originais dos ZIPs oficiais de votação nominal por município/zona
de 2014/2018/2022 estão em `data/raw/tse/*.csv.gz`. A compressão é sem perdas e
reversível, sem normalização do texto. Incluem votos do exterior, UF ZZ. Não
somar os arquivos estaduais com BR, pois duplicaria a mesma eleição. Hashes dos
ZIPs de origem, dos membros originais e dos arquivos compactados estão nos
manifests. O ZIP inteiro contém outros cargos e não é necessário ao estimador.

`data/canonical/tse-results-*.json` pode ser reconstruído dos raw. Em edições que
publicam `QT_VOTOS_NOMINAIS_VALIDOS`, esta é a coluna usada; no arquivo de 2014,
a coluna nominal só é aceita quando a candidatura aparece como DEFERIDO.

Esses desfechos históricos, isoladamente, **não** tornam a coleta de pesquisas
completa. `historical-coverage.json` exclui explicitamente os anos inteiros.
Com todos excluídos, |E_hist|=0; ê_ref, q90 e σ̂ são null, nunca imputados.

Os ZIPs oficiais de registros PesqEle dos três anos estão em `data/raw/pesqele`.
`pesqele-inventory-*.json` preserva registros presidenciais BR nas janelas de
campo, incluindo duplicações de registros de origem, cada uma com identidade
da linha original. Um registro BR pode pesquisar Presidente apenas em uma UF:
não é certificado de abrangência nacional. Revisar escopo, divulgações, cenários
e duplicações antes de transformar esse inventário em polls consumíveis.
2014 apresenta um registro com metadados conflitantes entre linhas; 2018
repete registros por contratantes. Nenhuma duplicação vira nova onda/família.

## Contrato de entrada para concluir a coleta

Cada ano só pode receber `collection_complete: true` com packets dos dois turnos,
`packets: {"1": "...json", "2": "...json"}`, `tse_manifest` e `coverage_evidence`.
Os packets têm:

- `year`, `turn`, `official_candidates: {names, tse_ids, sources}`;
- `polls`: todas as ondas inventariadas, inclusive as que serão descartadas por
  janela/escopo; cada uma tem poll_id, registration BR-NNNNN/AAAA, institute,
  office=Presidente, scope=Brasil, mode, exit_poll boolean, sample_size, datas ISO
  de início/fim do campo, published_at com timezone, sources, scenarios;
- cenário: scenario_id, stimulated boolean, candidates, valid e/ou total em
  frações, original_values, original_denominator. As categorias brancos/nulos/
  indecisos devem permanecer em original_values; total só contém candidatos;
- `coverage: {complete, reviewer, method, sources, inventory_poll_ids,
  not_published}`. Cada exclusão deve conter poll_id, reason, detail e sources.

Toda `sources` é uma lista com `{path, sha256, url, retrieved_at, location}`.
Paths apontam raw; location preserva página/tabela/pergunta ou registro. Valores
extraídos têm de ser conferidos contra esses originais, não contra uma estimativa
prévia. A validação mecânica não prova fidelidade de uma transcrição manual.

O packet 2026 tem apenas pesquisa/candidaturas, **nenhum R**. Não adquirir resultado
2026. `target: {name, party: PL, endorser: Jair Bolsonaro, sources}` guarda a
candidatura e o endosso verificados. Adversário é calculado a partir de P.
`prospective-1t-status.json` passa a apontar esse packet ao certificar a cobertura.

## Fechamento

Concluir coleta elegível até o cutoff, regenerar saídas e conferir a auditoria de
cobertura e transcrições. Commitar raw, packets, outputs e manifests antes de
qualquer totalização. Após testes e `--check` verde sobre commit limpo, confirmar
que o manifesto contém números de ê_ref/q90/σ̂, candidatos nominais, hashes e
saídas 1T coerentes. Só então criar a tag anotada `pre-election-freeze-2026` no
commit exato, sem force, antes de 04/10/2026 17:00 BRT, e publicar uma única vez.
Não há tag no estado BLOCKED. Pesquisas descobertas depois do manifesto entram
em late_discovery sem mudar a previsão. O manifesto 2T é um novo commit separado.
