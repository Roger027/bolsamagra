
import pandas as pd

# Ler os dados salvos
contas = pd.read_csv("contas_outubro.csv")

# Calcular o total
total = contas["valor"].sum()

# Agrupar os valores por categoria
categorias = contas.groupby("categoria")["valor"].sum()
categorias = categorias.sort_values(ascending=False)

print("=== ANÁLISE FINANCEIRA ===")
print(f"\nTotal de contas: R$ {total:.2f}")

print("\n--- POR CATEGORIA ---")

for categoria, valor in categorias.items():
    percentual = valor / total * 100
    print(f"{categoria}: R$ {valor:.2f} ({percentual:.1f}%)")

# Identificar a maior conta
maior = contas.loc[contas["valor"].idxmax()]

print("\n--- MAIOR CONTA ---")
print(f"Nome: {maior['nome']}")
print(f"Valor: R$ {maior['valor']:.2f}")
print(f"Categoria: {maior['categoria']}")

#O que você acabou de aprender

#read_csv() lê os dados de um arquivo.

#groupby() agrupa informações semelhantes.

#sum() soma valores.

#sort_values() organiza os resultados.

#idxmax() localiza o registro com o maior valor.