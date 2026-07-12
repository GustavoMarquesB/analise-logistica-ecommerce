# Análise de Logística de E-commerce

Análise exploratória de dados de pedidos e entregas de e-commerce,
investigando onde a operação logística perde mais pontos de satisfação
do cliente — e por quê.

## A pergunta de negócio

Atrasos na entrega acontecem em qualquer operação de e-commerce. Mas
**onde** eles acontecem mais, **o quanto** eles impactam a satisfação do
cliente, e **quais categorias de produto** são mais afetadas? Sem
responder isso com dados, é difícil priorizar onde investir para
melhorar a logística.

## A análise

Este projeto usa uma base de pedidos (inspirada na estrutura de dados
públicos de e-commerce, como o dataset Olist) para responder:

- Qual a **taxa de atraso** geral e por estado?
- Pedidos atrasados recebem **nota de avaliação** pior que pedidos no
  prazo? Quanto pior?
- Quais **categorias de produto** têm mais atraso?
- Qual estado deveria ser **prioridade** para melhorias logísticas?

## Principais conclusões (com os dados simulados)

- Pedidos atrasados recebem, em média, uma nota **bem inferior** à de
  pedidos entregues no prazo — o atraso tem impacto direto e mensurável
  na satisfação do cliente
- A taxa de atraso **varia bastante entre estados**, refletendo a
  distância até os centros de distribuição — estados mais distantes
  concentram os maiores atrasos
- Algumas categorias de produto têm taxa de atraso consistentemente
  maior que outras, o que pode indicar gargalos específicos (ex:
  fornecedor, embalagem, fragilidade do produto)

O relatório completo, com números exatos e gráficos, é gerado em
`analise_logistica.pdf`.

## Como funciona

1. `gerar_dados_simulados.py` cria uma base de pedidos fictícia
   (`pedidos_ecommerce.csv`), simulando 2000 pedidos em 6 meses, com
   estado do cliente, categoria do produto, prazo prometido, tempo real
   de entrega e nota de avaliação — apenas para servir de exemplo de
   entrada
2. `analise_logistica.py` lê essa base, calcula as métricas com
   **pandas**, gera os gráficos com **matplotlib** e exporta o relatório
   final em **PDF** (com **reportlab**)

Em um cenário real, bastaria substituir `pedidos_ecommerce.csv` pela
base de dados real da operação (ex: exportação do sistema de pedidos) —
o script funciona com qualquer planilha no mesmo formato de colunas.

## Como rodar

```bash
# instalar dependências
pip install pandas matplotlib reportlab

# (opcional) gerar uma nova base de exemplo
python3 gerar_dados_simulados.py

# rodar a análise
python3 analise_logistica.py
```

O arquivo `analise_logistica.pdf` é criado na raiz do projeto, e um
resumo rápido também aparece no terminal.

## Estrutura do projeto

```
analise-logistica-ecommerce/
├── pedidos_ecommerce.csv      # dados de entrada (exemplo simulado)
├── gerar_dados_simulados.py   # gera a base de exemplo
├── analise_logistica.py       # script principal: análise e exportação
├── analise_logistica.pdf      # relatório gerado
├── graficos/                  # gráficos gerados (.png)
└── README.md
```

## Tecnologias

- Python 3
- pandas — leitura, agregação e análise dos dados
- matplotlib — geração dos gráficos
- reportlab — geração do PDF

## Possíveis evoluções

- Usar o dataset real do Olist (disponível publicamente no Kaggle) no
  lugar dos dados simulados
- Investigar também o tempo entre a compra e o despacho do pedido
  (não só o transporte), para isolar em qual etapa o atraso ocorre
- Cruzar com dados de frete para avaliar custo-benefício de mudar de
  transportadora em regiões com mais atraso
