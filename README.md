# Sistema de Cotações em Tempo Real - Trabalho 2 (PPD)

Este projeto implementa uma infraestrutura distribuída para um sistema de cotações, demonstrando o uso de padrões de projeto para sistemas distribuídos.

## Arquitetura e Padrões

O sistema é composto por diversos microserviços Python comunicando-se via HTTP/REST.

1.  **Sharding (Particionamento)**:
    *   **Problema**: Banco de dados de histórico muito grande.
    *   **Solução**: `src/historical_shard` (nós de armazenamento) e `src/shard_router` (roteador).
    *   **Implementação**: O roteador distribui transações entre `shard1` (porta 5011) e `shard2` (porta 5012) baseado no hash do símbolo da ação.

2.  **Pub/Sub (Publicação/Assinatura)**:
    *   **Problema**: Notificar clientes sem acoplamento forte.
    *   **Solução**: `src/pubsub_broker`.
    *   **Implementação**: O `quote_service` publica atualizações de preço no broker. Clientes (como o `client_simulator.py`) registram URLs de callback para receber notificações.

3.  **Circuit Breaker**:
    *   **Problema**: Falhas no serviço externo não devem derrubar o sistema.
    *   **Solução**: Implementado dentro do `src/quote_service`.
    *   **Implementação**: Monitora falhas ao chamar o `external_provider`. Se o limite de erros for atingido, o circuito "abre" e retorna um valor de fallback/cache imediatamente, evitando sobrecarga e espera.

4.  **Scatter/Gather**:
    *   **Problema**: Consultas complexas que agregam dados de múltiplas fontes.
    *   **Solução**: `src/aggregator`.
    *   **Implementação**: O endpoint `/combined/<symbol>` dispara requisições paralelas para o `quote_service` (preço atual) e `shard_router` (histórico), combinando os resultados em uma única resposta JSON.

## Pré-requisitos

*   Python 3.8+
*   Pip

## Instalação

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

### Modo Automático (Recomendado)

Execute o script que inicia todos os serviços:

```bash
python run_all.py
```

Isso iniciará:
*   External Provider: http://localhost:5001
*   PubSub Broker: http://localhost:5002
*   Quote Service: http://localhost:5003
*   Shard Router: http://localhost:5010
*   Shard 1: http://localhost:5011
*   Shard 2: http://localhost:5012
*   Aggregator: http://localhost:5020

### Testando os Padrões

Abra um novo terminal para executar os testes (com o `run_all.py` rodando).

#### 1. Testar Sharding (Histórico)

Insira transações para símbolos diferentes. O roteador as enviará para shards diferentes.

```bash
# Inserir transação para AAPL (vai para um shard)
curl -X POST http://localhost:5010/transaction -H "Content-Type: application/json" -d "{\"symbol\": \"AAPL\", \"price\": 150.0, \"timestamp\": 1630000000}"

# Inserir transação para GOOGL (pode ir para outro shard)
curl -X POST http://localhost:5010/transaction -H "Content-Type: application/json" -d "{\"symbol\": \"GOOGL\", \"price\": 2800.0, \"timestamp\": 1630000000}"

# Consultar histórico
curl http://localhost:5010/transactions/AAPL
```

#### 2. Testar Pub/Sub

Inicie o simulador de cliente em um terminal separado. Ele vai escutar na porta 6000 e se inscrever no tópico `AAPL`.

```bash
python src/client_simulator.py AAPL
```

Em outro terminal, solicite uma cotação. Isso fará o `quote_service` publicar uma mensagem no broker, que notificará o cliente.

```bash
curl http://localhost:5003/quote/AAPL
```

Verifique o terminal do `client_simulator.py` para ver a mensagem recebida.

#### 3. Testar Circuit Breaker

Primeiro, verifique se está tudo normal (State: CLOSED):

```bash
curl http://localhost:5003/health/circuit
curl http://localhost:5003/quote/AAPL
```

Agora, configure o provedor externo para falhar:

```bash
curl -X POST http://localhost:5001/config -H "Content-Type: application/json" -d "{\"failure_mode\": true}"
```

Tente obter cotações. Após algumas falhas (padrão: 3), o circuito abrirá.

```bash
curl http://localhost:5003/quote/AAPL
curl http://localhost:5003/quote/AAPL
curl http://localhost:5003/quote/AAPL
# Agora deve estar OPEN e retornando fallback (preço antigo ou 0) instantaneamente
curl http://localhost:5003/health/circuit
```

Restaure o serviço externo e espere o timeout (10s) para o circuito tentar novamente (HALF-OPEN -> CLOSED).

```bash
curl -X POST http://localhost:5001/config -H "Content-Type: application/json" -d "{\"failure_mode\": false}"
```

#### 4. Testar Scatter/Gather (Aggregator)

Obtenha dados combinados (Preço Atual + Histórico) em uma única chamada:

```bash
curl http://localhost:5020/combined/AAPL
```
