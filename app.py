import pandas as pd

df = pd.read_csv("carros.csv")
colunas_disp = df.columns.tolist()

print("Por qual característica você gostaria de filtrar os carros?")
for i, coluna in enumerate(colunas_disp):
    print(f"{i+1}. {coluna}")

while True:
    try:
        en = int(input("Qual Número da Característica Desejada: "))
        if 1 <= en <= len(colunas_disp):
            coluna_filtro = colunas_disp[en - 1]
            break
        else:
            print("Número Invalido Digite um Número dentro das Opções")
    except:
        print("Entrada inválida. Por favor, digite um número.")

print(f"Opções Disponiveis Para o Filtro {coluna_filtro}: ")

opcoes_disp = df[coluna_filtro].unique()      
  
opcoes_orde = sorted(opcoes_disp)


for i, opcao in enumerate(opcoes_orde):
    print(f"{i+1}. {opcao}")

valor_filtro_num = None
valor_filtro_real = None

while True:
    escolha = input(f"Digite o NÚMERO da opção de {coluna_filtro} que você deseja, ou digite o valor diretamente: ")
    
    try:
        escolha_int = int(escolha)
        if 1 <= escolha_int <= len(opcoes_orde):
            valor_filtro_real = opcoes_orde[escolha_int -1]
            break
            
        else:
            print("Número Invalido, Tente Digitar um valor da lista ou Digitar o Valor Exato!")
            
    except ValueError:
        valor_digitado_lower = escolha.lower()
        encontrado = False
        for opt in opcoes_orde:
            if str(opt).lower() == valor_digitado_lower:
                valor_filtro_real = opt
                encontrado = True
                break
        if encontrado:
            break
        else:
            print(f"'{escolha}' não é uma opção válida para {coluna_filtro}. Tente um dos números da lista ou um valor existente.")

print(f"Voce Escolheu: {valor_filtro_real}!")

df_filtrado = df.copy()

print(f"\n➡️  Aplicando filtro: Coluna '{coluna_filtro}' = '{valor_filtro_real}'")

dtype_original_coluna = df[coluna_filtro].dtype()