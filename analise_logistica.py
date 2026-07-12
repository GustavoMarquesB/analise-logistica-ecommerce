"""
analise_logistica.py

Análise exploratória de dados de pedidos e entregas de e-commerce,
investigando padrões de atraso na entrega e seu impacto na satisfação
do cliente (nota de avaliação).

Pergunta de negócio:
    Onde a operação logística está perdendo mais pontos de satisfação
    do cliente, e por quê?

O que este script faz:
    1. Lê os dados de pedidos (pedidos_ecommerce.csv)
    2. Calcula taxa de atraso geral e por estado
    3. Investiga a relação entre atraso e nota de avaliação
    4. Identifica quais categorias de produto mais atrasam
    5. Gera gráficos e um resumo com as principais conclusões
    6. Exporta tudo em um relatório PDF

Uso:
    python3 analise_logistica.py
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ARQUIVO_ENTRADA = "pedidos_ecommerce.csv"
PASTA_GRAFICOS = Path("graficos")
ARQUIVO_PDF_SAIDA = "analise_logistica.pdf"


def carregar_dados(caminho: str) -> pd.DataFrame:
    """Lê o CSV de pedidos e prepara os tipos de dados corretos."""
    df = pd.read_csv(caminho, parse_dates=["data_pedido"])
    df["atrasado"] = df["atrasado"].astype(bool)
    df["dias_de_atraso"] = (
        df["tempo_entrega_real_dias"] - df["prazo_prometido_dias"]
    ).clip(lower=0)
    return df


def analisar(df: pd.DataFrame) -> dict:
    """Calcula as métricas e agregações principais da análise."""

    taxa_atraso_geral = df["atrasado"].mean()

    # taxa de atraso e nota média por estado
    por_estado = df.groupby("estado_cliente").agg(
        total_pedidos=("pedido_id", "count"),
        taxa_atraso=("atrasado", "mean"),
        nota_media=("nota_avaliacao", "mean"),
        atraso_medio_dias=("dias_de_atraso", "mean"),
    ).sort_values("taxa_atraso", ascending=False)

    # nota média comparando pedidos atrasados vs. no prazo
    nota_por_situacao = df.groupby("atrasado")["nota_avaliacao"].mean()

    # taxa de atraso por categoria de produto
    por_categoria = df.groupby("categoria_produto").agg(
        total_pedidos=("pedido_id", "count"),
        taxa_atraso=("atrasado", "mean"),
    ).sort_values("taxa_atraso", ascending=False)

    # correlação entre dias de atraso e nota (entre os pedidos atrasados)
    atrasados = df[df["atrasado"]]
    correlacao_atraso_nota = atrasados["dias_de_atraso"].corr(atrasados["nota_avaliacao"])

    return {
        "taxa_atraso_geral": taxa_atraso_geral,
        "por_estado": por_estado,
        "nota_por_situacao": nota_por_situacao,
        "por_categoria": por_categoria,
        "correlacao_atraso_nota": correlacao_atraso_nota,
        "total_pedidos": len(df),
    }


def gerar_graficos(metricas: dict) -> dict:
    """Gera os gráficos da análise e retorna os caminhos dos arquivos."""
    PASTA_GRAFICOS.mkdir(exist_ok=True)
    caminhos = {}

    # Gráfico 1: taxa de atraso por estado
    fig, ax = plt.subplots(figsize=(8, 4.5))
    dados = metricas["por_estado"]["taxa_atraso"].sort_values(ascending=False) * 100
    dados.plot(kind="bar", ax=ax, color="#C0392B")
    ax.set_title("Taxa de Atraso na Entrega por Estado (%)")
    ax.set_ylabel("Taxa de atraso (%)")
    ax.set_xlabel("Estado")
    plt.xticks(rotation=0)
    plt.tight_layout()
    caminho = PASTA_GRAFICOS / "taxa_atraso_por_estado.png"
    plt.savefig(caminho, dpi=150)
    plt.close(fig)
    caminhos["por_estado"] = caminho

    # Gráfico 2: nota média — atrasado vs. no prazo
    fig, ax = plt.subplots(figsize=(6, 4.5))
    dados2 = metricas["nota_por_situacao"].rename({True: "Atrasado", False: "No prazo"})
    dados2.plot(kind="bar", ax=ax, color=["#27AE60", "#C0392B"])
    ax.set_title("Nota Média de Avaliação: Atrasado vs. No Prazo")
    ax.set_ylabel("Nota média (1 a 5)")
    ax.set_ylim(0, 5)
    plt.xticks(rotation=0)
    plt.tight_layout()
    caminho2 = PASTA_GRAFICOS / "nota_por_situacao.png"
    plt.savefig(caminho2, dpi=150)
    plt.close(fig)
    caminhos["nota_situacao"] = caminho2

    # Gráfico 3: taxa de atraso por categoria de produto
    fig, ax = plt.subplots(figsize=(7, 4.5))
    dados3 = metricas["por_categoria"]["taxa_atraso"].sort_values() * 100
    dados3.plot(kind="barh", ax=ax, color="#2E86AB")
    ax.set_title("Taxa de Atraso por Categoria de Produto (%)")
    ax.set_xlabel("Taxa de atraso (%)")
    plt.tight_layout()
    caminho3 = PASTA_GRAFICOS / "taxa_atraso_por_categoria.png"
    plt.savefig(caminho3, dpi=150)
    plt.close(fig)
    caminhos["por_categoria"] = caminho3

    return caminhos


def exportar_pdf(metricas: dict, caminhos_graficos: dict):
    """Gera o relatório em PDF com as conclusões da análise."""
    c = canvas.Canvas(ARQUIVO_PDF_SAIDA, pagesize=A4)
    largura, altura = A4
    margem = 2 * cm

    c.setFillColor(colors.HexColor("#1F2937"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margem, altura - margem, "Análise de Logística — E-commerce")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#6B7280"))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.drawString(margem, altura - margem - 18, f"Gerado automaticamente em {data_geracao}")

    c.setStrokeColor(colors.HexColor("#1F2937"))
    c.line(margem, altura - margem - 30, largura - margem, altura - margem - 30)

    y = altura - margem - 60
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem, y, "Principais números")

    y -= 22
    c.setFont("Helvetica", 11)

    pior_estado = metricas["por_estado"]["taxa_atraso"].idxmax()
    pior_estado_taxa = metricas["por_estado"]["taxa_atraso"].max()
    melhor_estado = metricas["por_estado"]["taxa_atraso"].idxmin()
    pior_categoria = metricas["por_categoria"]["taxa_atraso"].idxmax()

    linhas_texto = [
        f"Total de pedidos analisados: {metricas['total_pedidos']}",
        f"Taxa de atraso geral: {metricas['taxa_atraso_geral'] * 100:.1f}%",
        f"Estado com maior taxa de atraso: {pior_estado} ({pior_estado_taxa * 100:.1f}%)",
        f"Estado com menor taxa de atraso: {melhor_estado}",
        f"Categoria com mais atraso: {pior_categoria}",
        f"Nota media (pedidos no prazo): {metricas['nota_por_situacao'][False]:.2f}",
        f"Nota media (pedidos atrasados): {metricas['nota_por_situacao'][True]:.2f}",
    ]
    for linha in linhas_texto:
        c.drawString(margem, y, linha)
        y -= 18

    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem, y, "Conclusão")
    y -= 20
    c.setFont("Helvetica", 10)

    conclusao = (
        f"Pedidos atrasados recebem, em média, nota "
        f"{metricas['nota_por_situacao'][False] - metricas['nota_por_situacao'][True]:.1f} "
        f"pontos menor do que pedidos entregues no prazo. O estado de {pior_estado} "
        f"concentra a maior taxa de atraso ({pior_estado_taxa * 100:.1f}%), sugerindo "
        f"gargalo logístico regional que deve ser priorizado. A categoria "
        f"'{pior_categoria}' também merece atenção por ter a maior taxa de atraso "
        f"entre os produtos."
    )
    # quebra de linha simples para caber na página
    max_chars = 95
    palavras = conclusao.split(" ")
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= max_chars:
            linha_atual += (" " if linha_atual else "") + palavra
        else:
            c.drawString(margem, y, linha_atual)
            y -= 14
            linha_atual = palavra
    if linha_atual:
        c.drawString(margem, y, linha_atual)
        y -= 14

    y -= 20
    img_w = largura - 2 * margem
    img_h = img_w * 0.55
    c.drawImage(str(caminhos_graficos["por_estado"]), margem, y - img_h, width=img_w, height=img_h)

    c.showPage()
    y = altura - margem

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(margem, y, "Impacto do atraso na satisfação e por categoria")
    y -= 20

    img_h2 = img_w * 0.5
    c.drawImage(str(caminhos_graficos["nota_situacao"]), margem, y - img_h2, width=img_w * 0.55, height=img_h2)
    y -= img_h2 + 20

    c.drawImage(str(caminhos_graficos["por_categoria"]), margem, y - img_h2, width=img_w, height=img_h2)

    c.save()
    print(f"Relatório PDF gerado: {ARQUIVO_PDF_SAIDA}")


def main():
    print("Lendo dados de pedidos...")
    df = carregar_dados(ARQUIVO_ENTRADA)

    print("Analisando padrões de atraso e satisfação...")
    metricas = analisar(df)

    print("Gerando gráficos...")
    caminhos_graficos = gerar_graficos(metricas)

    print("Exportando relatório em PDF...")
    exportar_pdf(metricas, caminhos_graficos)

    print("\nConcluído! Relatório pronto:")
    print(f"  - {ARQUIVO_PDF_SAIDA}")

    print("\nResumo rápido no terminal:")
    print(f"  Taxa de atraso geral: {metricas['taxa_atraso_geral'] * 100:.1f}%")
    print(f"  Nota média (no prazo): {metricas['nota_por_situacao'][False]:.2f}")
    print(f"  Nota média (atrasado): {metricas['nota_por_situacao'][True]:.2f}")


if __name__ == "__main__":
    main()
