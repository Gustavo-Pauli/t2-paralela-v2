# Roteiro de Apresentação (Demo Script)

Este roteiro foi preparado para guiar a apresentação do trabalho, demonstrando cada um dos 4 desafios/padrões exigidos.

## Preparação

1.  **Limpar ambiente (Opcional)**: Se quiser começar do zero, apague os arquivos `shard1.db` e `shard2.db`.
2.  **Iniciar o Sistema**:
    Abra um terminal e execute:
    ```bash
    python run_all.py
    ```
    *Mantenha este terminal visível para mostrar os logs dos serviços rodando.*

3.  **Popular Dados (Seed)**:
    Em um **segundo terminal**, execute o script para criar histórico:
    ```bash
    python seed_data.py
    ```
    *Explique: "Estamos inserindo dados aleatórios que serão distribuídos entre os shards pelo roteador."*

---

## Passo 1: Apresentar a Arquitetura

*   Mostre o diagrama (se tiver) ou explique:
    *   "Temos 7 microserviços rodando localmente."
    *   "A comunicação é toda via HTTP."
    *   "Vamos demonstrar os 4 padrões agora."

---

## Passo 2: Sharding (Desafio 1)

**Objetivo**: Mostrar que dados de diferentes ações vão para lugares diferentes.

1.  **Inserção**:
    Mostre o log do terminal do `run_all.py` ou execute:
    ```bash
    curl -X POST http://localhost:5010/transaction -H "Content-Type: application/json" -d "{\"symbol\": \"TESTA\", \"price\": 100, \"timestamp\": 1000}"
    curl -X POST http://localhost:5010/transaction -H "Content-Type: application/json" -d "{\"symbol\": \"TESTB\", \"price\": 200, \"timestamp\": 1000}"
    ```
    *Explique: "O Router calcula o hash do símbolo e escolhe o Shard 1 ou Shard 2."*

2.  **Consulta**:
    ```bash
    curl http://localhost:5010/transactions/TESTA
    ```
    *Mostre que o dado retorna corretamente.*

---

## Passo 3: Pub/Sub (Desafio 2)

**Objetivo**: Mostrar o desacoplamento. O serviço de cotação não conhece o cliente.

1.  **Iniciar Cliente**:
    Abra um **terceiro terminal** (ou use o segundo):
    ```bash
    python src/client_simulator.py AAPL
    ```
    *O cliente vai dizer "Listening on port 6000..." e "Subscribing..."*

2.  **Gerar Evento**:
    No terminal de comandos, peça uma cotação:
    ```bash
    curl http://localhost:5003/quote/AAPL
    ```

3.  **Resultado**:
    Olhe para o terminal do `client_simulator`.
    *Você verá: `[CLIENT] Received update: {...}`*
    *Explique: "O Quote Service mandou para o Broker, e o Broker mandou para o Cliente. Se abrirmos mais clientes, todos recebem."*

---

## Passo 4: Circuit Breaker (Desafio 3)

**Objetivo**: Mostrar o sistema sobrevivendo a falhas.

1.  **Estado Normal**:
    ```bash
    curl http://localhost:5003/health/circuit
    ```
    *(Deve retornar `CLOSED`)*

2.  **Simular Falha**:
    Derrube o serviço externo (simulação):
    ```bash
    curl -X POST http://localhost:5001/config -H "Content-Type: application/json" -d "{\"failure_mode\": true}"
    ```

3.  **Disparar Erros**:
    Execute várias vezes (pelo menos 3):
    ```bash
    curl http://localhost:5003/quote/AAPL
    curl http://localhost:5003/quote/AAPL
    curl http://localhost:5003/quote/AAPL
    ```
    *Note que as primeiras demoram (timeout) ou dão erro 500.*

4.  **Circuito Aberto**:
    Na 4ª vez:
    ```bash
    curl http://localhost:5003/quote/AAPL
    ```
    *A resposta é INSTANTÂNEA e o campo `source` diz `cache/fallback`.*
    
    Verifique o estado:
    ```bash
    curl http://localhost:5003/health/circuit
    ```
    *(Deve retornar `OPEN`)*

5.  **Recuperação**:
    Arrume o serviço externo:
    ```bash
    curl -X POST http://localhost:5001/config -H "Content-Type: application/json" -d "{\"failure_mode\": false}"
    ```
    *Espere 10 segundos e tente de novo. O circuito fechará.*

---

## Passo 5: Scatter/Gather (Desafio 4)

**Objetivo**: Uma requisição complexa que busca dados em paralelo.

1.  **Executar**:
    ```bash
    curl http://localhost:5020/combined/AAPL
    ```

2.  **Analisar JSON**:
    *   `current_quote`: Veio do Quote Service (que pode ter pego do cache ou externo).
    *   `history`: Veio do Shard (via Router).
    *   *Explique: "O Aggregator disparou as duas chamadas ao mesmo tempo e juntou o JSON final."*

---

## Dicas para a Apresentação

*   Use o **Postman** ou **Insomnia** se preferir uma interface gráfica ao invés do `curl`. Fica mais visual.
*   Deixe as janelas organizadas lado a lado:
    *   Esq: Terminal rodando `run_all.py` (Logs do servidor)
    *   Dir Sup: Terminal do `client_simulator.py` (Cliente Pub/Sub)
    *   Dir Inf: Terminal para rodar os comandos `curl` (Sua interação)
