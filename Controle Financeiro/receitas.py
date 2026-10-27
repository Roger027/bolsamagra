print("=== RECEITAS DE OUTUBRO ===")

dia_05 = float(input("Receita recebida dia 05: R$ "))
dia_20 = float(input("Receita recebida dia 20: R$ "))
final_mes = float(input("Outros valores no final do mês: R$ "))

total = dia_05 + dia_20 + final_mes

print("\n=== RESUMO DAS RECEITAS ===")
print(f"Dia 05: R$ {dia_05:.2f}")
print(f"Dia 20: R$ {dia_20:.2f}")
print(f"Final do mês: R$ {final_mes:.2f}")
print("-" * 30)
print(f"Total: R$ {total:.2f}")