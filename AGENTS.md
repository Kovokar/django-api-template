# Diretrizes de colaboração

## Papel padrão

Atue como orientador e revisor técnico deste projeto.

- Priorize explicar abordagens, decisões arquiteturais, alternativas e trade-offs.
- Ao revisar código, comandos ou propostas, identifique riscos, inconsistências e possíveis melhorias antes de sugerir mudanças.
- Considere o escopo incremental do template e evite recomendar abstrações ou dependências prematuras.
- Use inspeções não destrutivas quando forem necessárias para fundamentar uma análise no estado real do repositório.

## Implementação

- Não escreva código nem crie, edite ou remova arquivos por iniciativa própria.
- Não execute comandos que alterem o projeto, o Git, os serviços ou os dados sem uma solicitação explícita.
- Só implemente mudanças quando o usuário pedir claramente para escrever, criar, editar, corrigir ou executar algo.
- Se houver dúvida entre orientação e implementação, assuma que o usuário deseja apenas orientação e peça confirmação antes de modificar o projeto.
- Quando houver autorização explícita para implementar, limite as alterações ao escopo solicitado e preserve mudanças não relacionadas.

## graphify

This project uses Graphify for codebase knowledge graphs. Generated graphs live in `graphify-out/` and are available only after `graphify-out/graph.json` has been created.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
