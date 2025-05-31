import streamlit as st
import pandas as pd

print("--- Script Iniciado ---") # DEBUG

# --- Carregamento de Dados ---
@st.cache_data
def carregar_dados():
    print("--- Dentro de carregar_dados() ---") # DEBUG
    try:
        df = pd.read_csv("carros.csv")
        print("--- CSV Lido com sucesso ---") # DEBUG
        return df
    except FileNotFoundError:
        print("--- ERRO: Arquivo carros.csv não encontrado ---") # DEBUG
        st.error("Arquivo 'carros.csv' não encontrado! Verifique o nome e o local do arquivo.")
        return None
    except Exception as e:
        print(f"--- ERRO ao carregar dados: {e} ---") # DEBUG
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")
        return None

df_carros_original = carregar_dados()
print(f"--- df_carros_original é None? {df_carros_original is None} ---") # DEBUG

if df_carros_original is None:
    print("--- df_carros_original é None, chamando st.stop() ---") # DEBUG
    st.stop()

print("--- Dados carregados, antes do st.title ---") # DEBUG
st.title("🚗 Assistente de Recomendação de Carros")
print("--- st.title chamado ---") # DEBUG

# --- Inicialização do Estado da Sessão ---
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
    print("--- st.session_state.mensagens inicializado ---") # DEBUG
if "df_filtrado" not in st.session_state:
    st.session_state.df_filtrado = df_carros_original.copy()
    print("--- st.session_state.df_filtrado inicializado ---") # DEBUG
if "etapa_conversa" not in st.session_state:
    st.session_state.etapa_conversa = "esperando_coluna"
    print("--- st.session_state.etapa_conversa inicializado ---") # DEBUG
if "coluna_sendo_filtrada" not in st.session_state:
    st.session_state.coluna_sendo_filtrada = None
    print("--- st.session_state.coluna_sendo_filtrada inicializado ---") # DEBUG

if not st.session_state.mensagens:
    try:
        colunas_disponiveis_texto = ", ".join(df_carros_original.columns)
        print(f"--- Colunas disponíveis para msg inicial: {colunas_disponiveis_texto} ---") #DEBUG
        st.session_state.mensagens.append({
            "role": "assistant",
            "content": f"Olá! Por qual característica você gostaria de filtrar os carros? As opções são: {colunas_disponiveis_texto}."
        })
        print("--- Primeira mensagem do assistente adicionada ---") # DEBUG
    except Exception as e:
        print(f"--- ERRO ao criar mensagem inicial: {e} ---") # DEBUG

# --- Exibir mensagens do chat (histórico) ---
print("--- Antes de exibir mensagens do chat ---") # DEBUG
if not st.session_state.mensagens:
    print("--- Lista de mensagens está vazia ANTES do loop de exibição ---") # DEBUG

for i, msg in enumerate(st.session_state.mensagens):
    print(f"--- Exibindo mensagem {i}: role={msg['role']}, type={msg.get('content_type', 'text')} ---") # DEBUG
    with st.chat_message(msg["role"]):
        if msg.get("content_type") == "dataframe":
            df_to_display = msg.get("data")
            if df_to_display is not None and not df_to_display.empty:
                st.dataframe(df_to_display) 
            else:
                st.write("(Não foi possível exibir a tabela de dados)")
        elif "content" in msg: 
            st.write(msg["content"])
        else:
            st.write("(Mensagem com formato inesperado)") 
print("--- Depois de exibir mensagens do chat ---") # DEBUG

# --- Input do Usuário ---
print("--- Antes do st.chat_input ---") # DEBUG
prompt_usuario = st.chat_input("Digite a característica ou sua escolha...")
print(f"--- Depois do st.chat_input, prompt_usuario: {prompt_usuario} ---") # DEBUG

# --- Lógica Principal da Conversa ---
if prompt_usuario:
    print(f"--- Usuário digitou: {prompt_usuario} ---") # DEBUG
    st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
    
    resposta_assistente = "" 

    if st.session_state.etapa_conversa == "esperando_coluna":
        print("--- DEBUG: Entrou na etapa 'esperando_coluna' ---")
        coluna_digitada_pelo_usuario = prompt_usuario.strip()
        coluna_encontrada_no_df = None
        for nome_coluna_df in df_carros_original.columns:
            if nome_coluna_df.lower() == coluna_digitada_pelo_usuario.lower():
                coluna_encontrada_no_df = nome_coluna_df
                break
        if coluna_encontrada_no_df:
            print(f"--- DEBUG: Coluna encontrada: {coluna_encontrada_no_df} ---")
            st.session_state.coluna_sendo_filtrada = coluna_encontrada_no_df
            st.session_state.etapa_conversa = "esperando_valor"
            opcoes_disponiveis = st.session_state.df_filtrado[st.session_state.coluna_sendo_filtrada].unique()
            try:
                opcoes_ordenadas = sorted(list(opcoes_disponiveis), key=lambda x: (isinstance(x, str), x))
            except TypeError:
                opcoes_ordenadas = list(opcoes_disponiveis)
            opcoes_texto = "\n".join([f"- {opt}" for opt in opcoes_ordenadas])
            if not opcoes_ordenadas:
                 resposta_assistente = f"A coluna '{st.session_state.coluna_sendo_filtrada}' não possui opções variadas nos carros atuais. Por favor, escolha outra coluna. As opções são: {', '.join(df_carros_original.columns)}."
                 st.session_state.etapa_conversa = "esperando_coluna"
                 st.session_state.coluna_sendo_filtrada = None
            else:
                resposta_assistente = f"Você escolheu '{st.session_state.coluna_sendo_filtrada}'.\nQuais das seguintes opções você prefere?\n{opcoes_texto}\n(Digite o valor exato como mostrado)."
        else:
            print(f"--- DEBUG: Coluna '{coluna_digitada_pelo_usuario}' não encontrada ---")
            colunas_disponiveis_texto = ", ".join(df_carros_original.columns)
            resposta_assistente = f"'{coluna_digitada_pelo_usuario}' não é uma coluna válida. Por favor, escolha uma das seguintes opções: {colunas_disponiveis_texto}."

    elif st.session_state.etapa_conversa == "esperando_valor":
        print("--- DEBUG: Entrou na etapa 'esperando_valor' ---")
        valor_escolhido_pelo_usuario = prompt_usuario.strip()
        coluna_atual = st.session_state.coluna_sendo_filtrada
        print(f"--- DEBUG: Tentando valor '{valor_escolhido_pelo_usuario}' para coluna '{coluna_atual}' ---")
        opcoes_da_coluna_atual = st.session_state.df_filtrado[coluna_atual].unique()
        valor_encontrado_real = None
        for opt in opcoes_da_coluna_atual:
            if str(opt).lower() == valor_escolhido_pelo_usuario.lower():
                valor_encontrado_real = opt
                break
        if valor_encontrado_real is not None:
            print(f"--- DEBUG: Valor encontrado: {valor_encontrado_real} ---")
            dtype_original_coluna = df_carros_original[coluna_atual].dtype
            if dtype_original_coluna == 'object':
                st.session_state.df_filtrado = st.session_state.df_filtrado[st.session_state.df_filtrado[coluna_atual].astype(str).str.lower() == str(valor_encontrado_real).lower()]
            elif pd.api.types.is_numeric_dtype(dtype_original_coluna):
                try:
                    st.session_state.df_filtrado = st.session_state.df_filtrado[st.session_state.df_filtrado[coluna_atual] == valor_encontrado_real]
                except TypeError: 
                    resposta_assistente = f"Houve um erro ao tentar aplicar o filtro numérico para '{valor_encontrado_real}'. Tente novamente."
            elif pd.api.types.is_bool_dtype(dtype_original_coluna):
                st.session_state.df_filtrado = st.session_state.df_filtrado[st.session_state.df_filtrado[coluna_atual] == valor_encontrado_real]
            else:
                try:
                    st.session_state.df_filtrado = st.session_state.df_filtrado[st.session_state.df_filtrado[coluna_atual] == valor_encontrado_real]
                except Exception as e:
                     print(f"--- DEBUG: Erro ao aplicar filtro genérico: {e} ---")
                     resposta_assistente = f"Não foi possível aplicar o filtro para {coluna_atual} = {valor_encontrado_real}."
            if not resposta_assistente:
                num_carros_restantes = len(st.session_state.df_filtrado)
                resposta_assistente = f"Filtro '{coluna_atual} = {valor_encontrado_real}' aplicado! {num_carros_restantes} carro(s) restante(s)."
                if num_carros_restantes > 0:
                    resposta_assistente += "\nDeseja adicionar outro filtro (digite uma nova característica) ou ver os resultados (digite 'resultados')?"
                    st.session_state.etapa_conversa = "perguntar_mais_filtros_ou_finalizar"
                else:
                    resposta_assistente += "\nNenhum carro corresponde a todos os critérios. Você pode tentar redefinir os filtros (digite 'resetar')."
                    st.session_state.etapa_conversa = "final_sem_resultados"
            st.session_state.coluna_sendo_filtrada = None
        else:
            print(f"--- DEBUG: Valor '{valor_escolhido_pelo_usuario}' não encontrado nas opções ---")
            opcoes_disponiveis_novamente = st.session_state.df_filtrado[coluna_atual].unique()
            opcoes_ordenadas_novamente = sorted(list(opcoes_disponiveis_novamente), key=lambda x: (isinstance(x, str), x))
            opcoes_texto_novamente = "\n".join([f"- {opt}" for opt in opcoes_ordenadas_novamente])
            resposta_assistente = f"'{valor_escolhido_pelo_usuario}' não é um valor válido para '{coluna_atual}'. As opções são:\n{opcoes_texto_novamente}\nPor favor, digite um valor da lista."

    elif st.session_state.etapa_conversa == "perguntar_mais_filtros_ou_finalizar":
        print("--- DEBUG: Entrou na etapa 'perguntar_mais_filtros_ou_finalizar' ---")
        if prompt_usuario.lower() == "resultados":
            print("--- DEBUG: Usuário pediu 'resultados' ---")
            
            df_para_processar_resultados = st.session_state.df_filtrado.copy() # Trabalhar com uma cópia

            if not df_para_processar_resultados.empty:
                # --- LÓGICA DE RANKING E SELEÇÃO DOS TOP 5 ---
                print(f"--- DEBUG: Antes do ranking, {len(df_para_processar_resultados)} carros ---")
                df_ranqueado = df_para_processar_resultados.sort_values(
                    by=['Ano', 'KM', 'Preço'],
                    ascending=[False, True, True] 
                )
                df_top_5 = df_ranqueado.head(5)
                print(f"--- DEBUG: Após ranking e head(5), {len(df_top_5)} carros selecionados ---")
                # --- FIM DA LÓGICA DE RANKING ---

                msg_intro_resultados = f"Analisando os {len(df_para_processar_resultados)} carro(s) que correspondem aos seus filtros, aqui estão as nossas top {len(df_top_5)} recomendações:"
                st.session_state.mensagens.append({"role": "assistant", "content": msg_intro_resultados})
                print(f"--- DEBUG: Mensagem de introdução aos TOP resultados adicionada ---")
                
                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content_type": "dataframe", 
                    "data": df_top_5.copy() 
                })
                print(f"--- DEBUG: DataFrame TOP 5 adicionado às mensagens para exibição com st.dataframe() ---")
            else:
                st.session_state.mensagens.append({"role": "assistant", "content": "Nenhum carro encontrado com os critérios atuais para exibir."})
                print(f"--- DEBUG: Nenhuma linha no df_filtrado para 'resultados' ---")
            
            st.session_state.mensagens.append({"role": "assistant", "content": "Digite 'resetar' para fazer uma nova busca."})
            st.session_state.etapa_conversa = "aguardando_acao_pos_resultados"
            # resposta_assistente é intencionalmente deixada vazia aqui
        else: 
            coluna_digitada_pelo_usuario = prompt_usuario.strip()
            coluna_encontrada_no_df = None
            colunas_com_variacao = [col for col in df_carros_original.columns if st.session_state.df_filtrado[col].nunique() > 1]
            for nome_coluna_df in colunas_com_variacao: 
                if nome_coluna_df.lower() == coluna_digitada_pelo_usuario.lower():
                    coluna_encontrada_no_df = nome_coluna_df
                    break
            if coluna_encontrada_no_df:
                print(f"--- DEBUG: Usuário quer filtrar por nova coluna: {coluna_encontrada_no_df} ---")
                st.session_state.coluna_sendo_filtrada = coluna_encontrada_no_df
                st.session_state.etapa_conversa = "esperando_valor"
                opcoes_disponiveis = st.session_state.df_filtrado[st.session_state.coluna_sendo_filtrada].unique()
                opcoes_ordenadas = sorted(list(opcoes_disponiveis), key=lambda x: (isinstance(x, str), x))
                opcoes_texto = "\n".join([f"- {opt}" for opt in opcoes_ordenadas])
                if not opcoes_ordenadas:
                     resposta_assistente = f"A coluna '{st.session_state.coluna_sendo_filtrada}' não parece ter mais opções variadas. Tente 'resultados' ou outra coluna."
                     st.session_state.etapa_conversa = "perguntar_mais_filtros_ou_finalizar"
                     st.session_state.coluna_sendo_filtrada = None
                else:
                    resposta_assistente = f"Ok, vamos filtrar por '{st.session_state.coluna_sendo_filtrada}'.\nQuais das seguintes opções você prefere?\n{opcoes_texto}\n(Digite o valor exato)."
            else:
                print(f"--- DEBUG: Input não reconhecido em 'perguntar_mais_filtros_ou_finalizar': '{prompt_usuario}' ---")
                colunas_texto_sugestao = ", ".join(colunas_com_variacao) if colunas_com_variacao else "nenhuma outra com variação"
                resposta_assistente = f"Não entendi. Você pode digitar o nome de outra característica para filtrar (opções com variação: {colunas_texto_sugestao}), ou digitar 'resultados' para ver a lista atual."

    elif st.session_state.etapa_conversa in ["final_sem_resultados", "aguardando_acao_pos_resultados"]:
        print(f"--- DEBUG: Entrou na etapa '{st.session_state.etapa_conversa}' ---")
        if prompt_usuario.lower() == "resetar":
            print("--- DEBUG: Usuário pediu 'resetar' ---")
            st.session_state.mensagens = [] 
            st.session_state.df_filtrado = df_carros_original.copy()
            st.session_state.etapa_conversa = "esperando_coluna"
            st.session_state.coluna_sendo_filtrada = None
            colunas_disponiveis_texto = ", ".join(df_carros_original.columns)
            st.session_state.mensagens.append({
                "role": "assistant",
                "content": f"Filtros resetados! Começando de novo. Por qual característica você gostaria de filtrar? Opções: {colunas_disponiveis_texto}."
            })
        else:
            resposta_assistente = "Digite 'resetar' para começar de novo."

    if resposta_assistente:
        print(f"--- DEBUG: Resposta do assistente FINAL a ser adicionada: '{resposta_assistente[:70].replace('\n', ' ')}...' ---")
        st.session_state.mensagens.append({"role": "assistant", "content": resposta_assistente})
    else:
        print("--- DEBUG: Nenhuma 'resposta_assistente' global para adicionar (provavelmente mensagens já foram adicionadas diretamente ou não era necessária uma resposta adicional). ---")

    print(f"--- DEBUG: Total de mensagens no estado: {len(st.session_state.mensagens)} ---")
    print(f"--- DEBUG: Próxima etapa da conversa definida como: {st.session_state.etapa_conversa} ---")
    print(f"--- DEBUG: Chamando st.rerun() ---")
    st.rerun()

print("--- Fim do script (antes de possível rerun final de ciclo) ---") # DEBUG