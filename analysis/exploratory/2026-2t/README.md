# Segundo turno de 2026 — trilha pós-eleição

**EXPLORATORY_POST_ELECTION. Não é previsão prospectiva nem recuperação do freeze.**

Esta trilha começa em 26/10/2026, depois do prazo do Cofre A 2T. O resultado de
2026 já foi acessado. Nenhum trabalho daqui pode adquirir retrospectivamente o
status `CONFIRMATORY_PROSPECTIVE` do PREREG-0001. O encerramento metodológico
está em [auditoria](../../../reports/audits/cofre-a-2t-2026-10-26/README.md).

## Entrega inicial

- `sources.json`: URLs, momentos de aquisição, cabeçalhos HTTP, hashes SHA-256 e caminhos.
- `raw/`: bytes originais do TSE, sem transformação ou sobrescrita.
- `official-outcome.json`: resultado nacional de Presidente/2T, Brasil incluindo exterior,
  normalizado do JSON oficial EA20, eleição 6258, geração `4241309`.
- `reproduce.py`: transformação e checagens determinísticas; não acessa rede nem escreve arquivos.
- `validation.json`: verificações locais e rejeição de entradas inconsistentes.

O JSON obtido às 14:46:22 de Brasília de 26/10/2026 informa geração em
25/10/2026 às 23:27:02, `tf=s`, `and=f` e 100% das seções totalizadas.
É a versão observada, sujeita a retotalizações futuras. Não implica homologação
judicial imutável nem auditoria independente dos boletins de urna.

O ZIP do relatório nacional também foi preservado: a versão baixada contém
`6257_BR_BRASIL_2026_T1_PRESIDENTE.pdf` e `_leiame.pdf`, sem relatório T2.
Por isso, os números de 2T foram obtidos do EA20 oficial, e não desse PDF de 1T.
Documentação EA20 e configuração de eleições acompanham os dados.

## Reprodução

Na raiz do repositório, com Python 3.11 ou posterior, sem dependências externas:

```bash
python analysis/exploratory/2026-2t/reproduce.py --check
python analysis/exploratory/2026-2t/reproduce.py
```

O segundo comando apenas imprime a reprodução; não sobrescreve a versão guardada.
O script valida hashes de todas as fontes, eleição, turno, fase oficial, abrangência,
cargo, finalização, identidades distintas e reconciliação das contagens.

| Campo de saída | Origem / transformação |
|---|---|
| Votos por candidato | `carg[0].agr[].par[].cand[].vap`, com `dvt=Válido` |
| Denominador de R | `v.vv`, votos válidos; nunca eleitorado, comparecimento ou total de votos |
| R | `vap / v.vv`; numerador e denominador inteiros também preservados |
| Percentual publicado | `pvapn`, cujo denominador EA20 é `vvc`; não substituir automaticamente R |
| Estado da fonte | `tf`, `and`, `s.st`, `s.ts`, `s.snt`, `idg`, `dg`, `hg` |
| P, intervalos e parâmetros do Cofre A | `null`, indisponíveis; zero não é missing |

Não se calcula erro `R−P`, cobertura de intervalo ou decisão BLOCO/CANDIDATO:
não existe P prospectivo validamente congelado demonstrado. Uma estatística
calculada agora será uma reconstrução retrospectiva, mesmo se aplicar o estimador antigo.

## Próximas etapas, sem compromissos ou revisões retroativas

1. Inventariar todas as pesquisas e localizar originais PesqEle/institutos antes de
   selecionar ondas; registrar registro, URL, raw, página/pergunta, datas de campo
   e publicação, modo, CNPJ/família, cenário, denominador e decisão de inclusão.
   Criar os novos inventários **nesta trilha**, sem preencher o status prospectivo antigo.
2. Distinguir publicação antes do cutoff de aquisição após a eleição. Ambas as datas
   são necessárias: uma fonte antiga descoberta agora não vira input congelado antigo.
   Na ausência de um selo válido, chamar o ledger de `post_deadline_discovery`,
   sem inventar um SHA de freeze para o mecanismo `late_discovery` original.
3. Reconciliar registros, duplicações, âmbito nacional, candidaturas e famílias;
   publicar cobertura e missingness tipada. Inventário vazio não prova zero pesquisas.
4. Completar a coleta histórica dos dois turnos de 2014/2018/2022 em versões novas.
   Os anos excluídos do artefato antigo continuam excluídos naquele artefato.
5. Se houver dados suficientes, reconstruir como benchmark exploratório a regra
   original (11–24/10, publicação até 25/10 12h BRT, estimulada, dois classificados,
   válidos, uma onda por família, média simples, piso de três famílias). Registrar
   versão, código e dependências. A semelhança com o prereg não recupera prospectividade.
6. Reportar todas as sensibilidades do §9 original separadamente, inclusive as que
   desfavoreçam a interpretação inicial. Alterações de método recebem nova especificação
   exploratória; nunca edição do PREREG-0001. Não escolher janelas/pesos pelo resultado.
7. Hipóteses surgidas nesta exploração exigem outro preregistro e dados ainda não
   usados para descoberta; 2026 não pode ser reutilizado como holdout intacto.

Cada análise futura deve indicar dataset/versão, universo, famílias e ondas, janela,
denominador, transformação, missingness, incerteza, heterogeneidade, sensibilidades,
multiplicidade, limitações e teto de evidência. Neste início, universo observado é
apenas o resultado oficial nacional; famílias/ondas de pesquisas são **não coletadas**,
modelo e incerteza preditiva são **não disponíveis**, classificação da hipótese é
**não avaliada**. Interpretação política e alegações causais não foram realizadas.

## Atualizações de fonte

Novo download diferente gera outro nome com SHA-256, outro registro de aquisição
e nova normalização explicitamente versionada. Conservar todos os snapshots,
registrar diferenças e explicar a reconciliação. Nunca editar `raw/` in-place.
O normalizador v1 é deliberadamente restrito ao snapshot auditado; mudanças no
destino dos votos, no schema ou em categorias devem falhar e exigir revisão.

Fontes oficiais: [portal de dados](https://dadosabertos.tse.jus.br/dataset/resultados-2026),
[instruções técnicas](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados),
[resultado EA20](https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.json).
