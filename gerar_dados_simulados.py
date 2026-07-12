"""
gerar_dados_simulados.py

Gera uma base de pedidos de e-commerce simulada (pedidos_ecommerce.csv),
inspirada na estrutura de dados públicos de logística de e-commerce
(como o dataset Olist), para servir de entrada à análise
(analise_logistica.py).

Este script existe apenas para criar um cenário de teste realista.
"""

import csv
import random
from datetime import date, timedelta

random.seed(7)  # reprodutibilidade

# Estados brasileiros com pesos diferentes de volume de pedidos
# (concentração maior no Sudeste, como no cenário real de e-commerce no Brasil)
estados = {
    "SP": 35, "RJ": 15, "MG": 12, "RS": 8, "PR": 7,
    "SC": 5, "BA": 5, "DF": 4, "GO": 3, "PE": 3,
    "CE": 3,
}

# Distância aproximada (proxy) de cada estado até os grandes centros de distribuição
# (usada para simular tempo de entrega mais realista)
distancia_relativa = {
    "SP": 1.0, "RJ": 1.2, "MG": 1.3, "RS": 2.0, "PR": 1.6,
    "SC": 1.8, "BA": 2.3, "DF": 1.9, "GO": 1.9, "PE": 2.6,
    "CE": 2.8,
}

categorias = [
    "Eletrônicos", "Móveis", "Roupas e Acessórios", "Beleza e Cuidados Pessoais",
    "Casa e Decoração", "Esporte e Lazer", "Livros", "Brinquedos",
    "Eletrodomésticos", "Papelaria",
]

data_inicial = date(2026, 1, 1)
dias_periodo = 180

linhas = []
estados_lista = list(estados.keys())
pesos_estados = list(estados.values())

for pedido_id in range(1, 2001):
    dia_offset = random.randint(0, dias_periodo)
    data_pedido = data_inicial + timedelta(days=dia_offset)

    estado = random.choices(estados_lista, weights=pesos_estados)[0]
    categoria = random.choice(categorias)

    # prazo prometido: baseado na distância relativa do estado, com alguma variação
    prazo_base = 5 + distancia_relativa[estado] * 4
    prazo_prometido = max(3, round(prazo_base + random.uniform(-1, 1)))

    # tempo real de entrega: normalmente próximo do prometido, mas com chance de atraso
    # maior para estados mais distantes (simulando gargalos logísticos reais)
    chance_atraso = 0.10 + (distancia_relativa[estado] - 1.0) * 0.12
    houve_atraso = random.random() < chance_atraso

    if houve_atraso:
        atraso_dias = random.randint(1, 8)
        tempo_entrega_real = prazo_prometido + atraso_dias
    else:
        # pode chegar até um pouco antes do prazo
        adiantamento = random.randint(0, 2)
        tempo_entrega_real = max(1, prazo_prometido - adiantamento)

    atrasado = tempo_entrega_real > prazo_prometido

    # nota de avaliação: correlacionada com atraso, mas não determinística
    if atrasado:
        diferenca = tempo_entrega_real - prazo_prometido
        # quanto maior o atraso, menor a nota tende a ser
        nota_base = max(1, 5 - diferenca * 0.6)
    else:
        nota_base = random.uniform(4.0, 5.0)

    nota_avaliacao = round(min(5, max(1, nota_base + random.uniform(-0.5, 0.5))))

    valor_pedido = round(random.uniform(45, 850), 2)

    linhas.append({
        "pedido_id": pedido_id,
        "data_pedido": data_pedido.isoformat(),
        "estado_cliente": estado,
        "categoria_produto": categoria,
        "valor_pedido": valor_pedido,
        "prazo_prometido_dias": prazo_prometido,
        "tempo_entrega_real_dias": tempo_entrega_real,
        "atrasado": atrasado,
        "nota_avaliacao": nota_avaliacao,
    })

with open("pedidos_ecommerce.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "pedido_id", "data_pedido", "estado_cliente", "categoria_produto",
        "valor_pedido", "prazo_prometido_dias", "tempo_entrega_real_dias",
        "atrasado", "nota_avaliacao",
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(linhas)

print(f"Gerado pedidos_ecommerce.csv com {len(linhas)} registros.")
