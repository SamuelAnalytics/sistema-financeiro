"""Controle financeiro pessoal com lançamentos em JSON."""

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


ARQUIVO_DADOS = Path(__file__).with_name("transacoes.json")


def carregar_lancamentos():
    if not ARQUIVO_DADOS.exists():
        return []
    try:
        return json.loads(ARQUIVO_DADOS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("Não consegui ler transacoes.json. Vou iniciar sem lançamentos.")
        return []


def salvar_lancamentos(lancamentos):
    ARQUIVO_DADOS.write_text(
        json.dumps(lancamentos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ler_valor_em_centavos():
    """Lê valores no formato brasileiro, como 125,90 ou 1.250,90."""
    texto = input("Valor (ex.: 125,90): R$ ").strip().replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        valor = Decimal(texto).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None

    if valor <= 0:
        return None
    return int(valor * 100)


def formatar_reais(centavos):
    valor = f"{centavos / 100:,.2f}"
    valor = valor.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor}"


def adicionar_lancamento(lancamentos, tipo):
    valor = ler_valor_em_centavos()
    if valor is None:
        print("Valor inválido. Digite um número maior que zero.")
        return

    categoria = input("Categoria: ").strip()
    descricao = input("Descrição: ").strip()
    if not categoria or not descricao:
        print("Categoria e descrição são obrigatórias.")
        return

    lancamentos.append(
        {
            "tipo": tipo,
            "valor_centavos": valor,
            "categoria": categoria,
            "descricao": descricao,
            "data": date.today().isoformat(),
        }
    )
    salvar_lancamentos(lancamentos)
    print(f"{tipo.capitalize()} registrada: {formatar_reais(valor)}")


def mostrar_resumo(lancamentos):
    receitas = sum(item["valor_centavos"] for item in lancamentos if item["tipo"] == "receita")
    despesas = sum(item["valor_centavos"] for item in lancamentos if item["tipo"] == "despesa")
    saldo = receitas - despesas

    print("\n--- RESUMO ---")
    print(f"Receitas: {formatar_reais(receitas)}")
    print(f"Despesas: {formatar_reais(despesas)}")
    print(f"Saldo:    {formatar_reais(saldo)}")


def mostrar_lancamentos(lancamentos):
    if not lancamentos:
        print("\nNenhum lançamento ainda.")
        return

    print("\n--- LANÇAMENTOS ---")
    for item in lancamentos:
        sinal = "+" if item["tipo"] == "receita" else "-"
        print(
            f"{item['data']} | {sinal}{formatar_reais(item['valor_centavos'])}"
            f" | {item['categoria']} | {item['descricao']}"
        )


def main():
    lancamentos = carregar_lancamentos()
    while True:
        print("\n=== CONTROLE FINANCEIRO ===")
        print("1. Registrar receita")
        print("2. Registrar despesa")
        print("3. Ver resumo")
        print("4. Ver lançamentos")
        print("0. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Dados salvos. Até a próxima!")
            break
        if escolha == "1":
            adicionar_lancamento(lancamentos, "receita")
        elif escolha == "2":
            adicionar_lancamento(lancamentos, "despesa")
        elif escolha == "3":
            mostrar_resumo(lancamentos)
        elif escolha == "4":
            mostrar_lancamentos(lancamentos)
        else:
            print("Opção inválida. Escolha de 0 a 4.")


if __name__ == "__main__":
    main()
