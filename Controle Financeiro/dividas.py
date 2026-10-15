#1 Preparar Ambiente
#2 Verificar Python (py --version)
#3 Criar Pasta do Projeto (controle_financeiro)
#4 Dentro da Pasta, criar dividas.py
#5 Copiar o código abaixo para o arquivo dividas.py


from datetime import date

print("=== CONTROLE FINANCEIRO ===")
print("Faturas com vencimento em 05/10/2026")
print("-" * 45)

contas = [
    {"nome": "Peruas", "valor": 330.00, "categoria": "Transporte"},
    {"nome": "Cartão Neon", "valor": 382.82, "categoria": "Cartão"},
    {"nome": "Cartão Atacadão", "valor": 277.41, "categoria": "Cartão"},
    {"nome": "Cartão Bradesco", "valor": 283.63, "categoria": "Cartão"},
    {"nome": "Cartão Dibs", "valor": 279.04, "categoria": "Cartão"},
    {"nome": "Cartão Mais", "valor": 357.43, "categoria": "Cartão"},
    {"nome": "Vestcasa", "valor": 589.37, "categoria": "Compra"},
    {"nome": "Amil", "valor": 97.58, "categoria": "Saúde"},
    {"nome": "Internet", "valor": 79.99, "categoria": "Serviço"},
    {"nome": "Água", "valor": 106.04, "categoria": "Moradia"},
    {"nome": "Energia", "valor": 294.09, "categoria": "Moradia"},
    {"nome": "Shopee", "valor": 250.00, "categoria": "Compra"},
    {"nome": "INSS", "valor": 180.00, "categoria": "Contribuição"}
]

total = 0

for conta in contas:
    print(f'{conta["nome"]}: R$ {conta["valor"]:.2f}')
    total += conta["valor"]

total_informado = 3646.32
diferenca = total_informado - total

print("-" * 45)
print(f"Total calculado: R$ {total:.2f}")
print(f"Total informado: R$ {total_informado:.2f}")
print(f"Diferença: R$ {diferenca:.2f}")

import csv

with open("contas_outubro.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
    campos = ["nome", "valor", "categoria"]

    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(contas)

print("\nArquivo contas_outubro.csv criado com sucesso!")

#O código acima cria uma lista de dívidas, cada uma representada como um dicionário com o nome do credor e o valor da dívida. Em seguida, ele percorre a lista, imprime cada dívida e calcula o total das dívidas, que é exibido no final.

#6 Para executar o código, abra o terminal, navegue até a pasta do projeto e execute o comando: `py dividas.py`. Isso exibirá a lista de dívidas e o total calculado.
#7 Para adicionar uma nova dívida, você pode modificar a lista `dividas` adicionando um novo dicionário com o nome do credor e o valor da dívida. Por exemplo:
#8 Fazer o programa salvar os dados em arquivo csv ou excel para não precisar digitar novamente.
#Estrutura de dados: cada conta possui nome, valor e categoria.

#Automação: o for percorre todas as contas sem precisar somar manualmente.

#Raciocínio lógico: o programa compara o total calculado com o total informado e identifica uma diferença de R$ 138,92.

#Agora vamos dar um passo que muda o projeto: fazer os dados sobreviverem ao fechamento do programa.

#9 Próxima etapa: salvar suas contas em CSV
#10 colar codigo no final do atual e executar   
#11 Atençâo: o modo "w" substitui o conteudo do arquivo caso ele ja exista. Se quiser adicionar novas contas sem perder as antigas, use o modo "a" (append) em vez de "w".
#O que estamos construindo
#Cadastro das contas — concluído.
#Conferência automática — concluída.
#Salvar dados em arquivo — próximo passo.
#Importar e analisar com Pandas.
#Construir painel financeiro e automatizar relatórios.

#py -m pip install pandas



