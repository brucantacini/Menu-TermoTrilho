# Sistema de Monitoramento de Trilhos Ferroviários

Este projeto é um sistema de monitoramento de trilhos ferroviários que realiza a verificação de riscos, gerenciamento de manutenções, monitoramento de alertas e status das linhas, utilizando um banco de dados Oracle para armazenar as informações.

## Funcionalidades

1. **Verificação de riscos de flambagem**: Verifica a temperatura atual e emite alertas sobre o risco de flambagem nos trilhos.
2. **Exibição de status das linhas**: Mostra o status das linhas do sistema ferroviário.
3. **Cadastro e alteração de trilhos e manutenções**: Permite cadastrar, alterar e consultar trilhos e manutenções no banco de dados.
4. **Histórico de manutenções**: Exibe o histórico completo de manutenções realizadas.
5. **Alertas no sistema**: Permite visualizar, excluir ou consultar alertas de segurança no sistema ferroviário.
6. **Exportação de dados**: Exporta informações sobre estações e manutenções para arquivos JSON.
7. **Consultas e relatórios personalizados**: Consultas específicas, como manutenções por tipo, e exportação de dados por linha.

## Pré-requisitos

- Python 3.x
- Banco de dados Oracle
- Bibliotecas Python:
  - `oracledb`
  - `requests`
  - `json`
