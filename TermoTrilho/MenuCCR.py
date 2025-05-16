import datetime
import json
import os
import requests
import oracledb

def verificar_riscos():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current=temperature_2m"
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        temperatura = dados["current"]["temperature_2m"]
        print(f"Temperatura atual: {temperatura}°C")

        if temperatura < 20:
            print("Status: Sem risco de flambagem nos trilhos.")
        elif 20 <= temperatura <= 35:
            print("Status: Atenção! Risco moderado de flambagem nos trilhos.")
        else:  # temperatura > 35
            print("Status: ALERTA! Alto risco de flambagem nos trilhos.")
    else:
        print("Erro ao obter a temperatura atual.")


# Função para carregar dados
def carregar_dados(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r") as arquivo:
            return json.load(arquivo)
    return {}

# Função para salvar dados
def salvar_dados(nome_arquivo, dados):
    with open(nome_arquivo, "w") as arquivo:
        json.dump(dados, arquivo, indent=4, sort_keys=True)

trilhos = carregar_dados("trilhos.json")
ocorrencias = carregar_dados("ocorrencias.json")
manutencoes = carregar_dados("manutencoes.json")

# Funções auxiliares
def linha(tam=42) -> str:
    return "-" * tam

def cabecalho(txt: str):
    print(linha())
    print(txt.center(42))
    print(linha())

def menu(lista: list):
    cabecalho("SISTEMA TERMO-TRILHO")
    for i, item in enumerate(lista, start=1):
        print(f"{i} - {item}")
    print(linha())

def status_linhas():
    try:
        print("----- STATUS DAS LINHAS -----\n")

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_LINHA_METRO"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta (lista de tuplas)
        lista_dados = cursor.fetchall()

        # Verifica se há dados cadastrados
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados!")
        else:
            # exibe os itens da lista
            for item in lista_dados:
                print(item)
                print()
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def exibir_estacoes():
    try:
        print("----- ESTAÇÕES -----\n")
        print("(1) - Linha 8 diamante | (2) - Linha 9 esmeralda")

        linha_id = int(input("Deseja ver estações de qual linha? "))
        if linha_id in [1, 2]:
            script = f"SELECT * FROM T_TT_ESTACAO WHERE ID_LINHA = {linha_id}"
            cursor.execute(script)
            lista_dados = cursor.fetchall()

            if not lista_dados:
                print("Não há dados cadastrados!")
            else:
                for item in lista_dados:
                    print(item)
                    print()
        else:
            print("Escolha uma linha válida!")
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def exibir_alertas():
    try:
        print("----- ALERTAS -----\n")

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_ALERTA"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta (lista de tuplas)
        lista_dados = cursor.fetchall()

        # Verifica se há dados cadastrados
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados!")
        else:
            # exibe os itens da lista
            for item in lista_dados:
                print(item)
                print()
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def excluirAlerta():
    try:
        print("----- EXCLUIR ALERTA CONCLUÍDO -----\n")

        alerta_id = int(input("Digite o ID do alerta: "))

        # Monta a instrução SQL de consulta
        consulta = f"""SELECT * FROM T_TT_ALERTA WHERE ID_ALERTA = {alerta_id}"""

        # Executa o script SQL no banco de dados
        cursor.execute(consulta)

        # captura os dados de retorno da consulta
        lista_dados = cursor.fetchall()

        # Verifica se o dado está cadastrado
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrado com o ID = {alerta_id}")
        else:
            # Cria a instrução SQL de exclusão
            script = f"""DELETE FROM T_TT_ALERTA WHERE ID_ALERTA = {alerta_id}"""

            # Executa a instrução e atualiza a tabela
            cursor.execute(script)
            conn.commit()

            print("\nAlerta concluído com sucesso.")
            print()
    except ValueError:
        print("Digite um número inteiro para o id!")
    except Exception as error:
        print(f"Alerta na transação do BD: {error}")

def historico_manutencoes():
    try:
        print("----- HISTÓRICO MANUTENÇÕES -----\n")

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_MANUTENCAO ORDER BY ID_MANUTENCAO"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta (lista de tuplas)
        lista_dados = cursor.fetchall()

        # Verifica se há dados cadastrados
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados!")
        else:
            # exibe os itens da lista
            for item in lista_dados:
                print(item)
                print()
    except Exception as error:
         print(f"Erro na transação com o banco de dados: {error}")

def consultar_manutencoes_por_tipo():
    try:
        print("----- CONSULTA DE MANUTENÇÕES POR TIPO -----")
        tipo = input("Digite o tipo de manutenção (P = preventiva, C = corretiva): ").upper()

        if tipo not in ['P', 'C']:
            print("Tipo inválido. Use 'P' ou 'C'.")
            return

        script = f"SELECT * FROM T_TT_MANUTENCAO WHERE TP_MANUTENCAO = :1"
        cursor.execute(script, [tipo])
        resultados = cursor.fetchall()

        if not resultados:
            print("Nenhuma manutenção encontrada com esse tipo.")
        else:
            colunas = [desc[0] for desc in cursor.description]
            dados_json = []

            for linha in resultados:
                registro = {}
                for col, val in zip(colunas, linha):
                    if isinstance(val, datetime):
                        registro[col] = val.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        registro[col] = val
                dados_json.append(registro)

            nome_arquivo = f"manutencoes_tipo_{tipo}.json"
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados_json, f, indent=4, ensure_ascii=False)

            print(f"{len(dados_json)} registros exportados para '{nome_arquivo}' com sucesso.\n")
    except Exception as error:
        print(f"Erro ao consultar manutenções: {error}")


def alterar_dados_manutencao():
    try:
        print("----- ALTERAR DADOS MANUTENÇÃO-----\n")

        manutencao_id = int(input("Digite o ID da manutenção: "))

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_MANUTENCAO WHERE ID_MANUTENCAO = {manutencao_id}"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta
        lista_dados = cursor.fetchall()

        # Verifica se o registro está cadstrado
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados com o ID = {manutencao_id}")
        else:
            # Solicita os novos valores
            tp_manutencao = input("Tipo de manutenção (P/C): ").upper()[:1]
            des_manutencao = input("Descrição da manutenção: ")
            responsavel = input("Responsável (opcional): ")
            id_trilho = int(input("ID do trilho a passar por manutenção: "))

            # Constroi a instrução de edição do registro com os novos valores
            script = f"""UPDATE T_TT_MANUTENCAO SET
                         TP_MANUTENCAO = '{tp_manutencao}',
                         DES_MANUTENCAO = '{des_manutencao}',
                         RESPONSAVEL = '{responsavel}',
                         ID_TRILHO = {id_trilho}
                         WHERE ID_MANUTENCAO = {manutencao_id}"""

            # Executa e altera o registro na Tabela
            cursor.execute(script)
            conn.commit()

            print("\nItem alterado com sucesso!")
            print()
    except ValueError:
        print("Digite um valor inteiro.")
    except Exception as error:
        print(f"Erro na transação do BD: {error}")

def registrar_manutencao():
    try:
        print("----- REGISTRAR MANUTENÇÃO -----\n")

        tp_manutencao = input("Tipo de manutenção (P/C): ").upper()[:1]
        des_manutencao = input("Descrição da manutenção: ")
        responsavel = input("Responsável (opcional): ")
        id_trilho = int(input("ID do trilho a passar por manutenção: "))
        dt_manutencao = datetime.date.today()

        script = """INSERT INTO T_TT_MANUTENCAO 
                    (DT_MANUTENCAO, TP_MANUTENCAO, DES_MANUTENCAO, RESPONSAVEL, ID_TRILHO) 
                    VALUES (:1, :2, :3, :4, :5)"""

        cursor.execute(script, (dt_manutencao, tp_manutencao, des_manutencao, responsavel, id_trilho))
        conn.commit()

        print("\nManutenção registrada com sucesso.")
        print()
    except ValueError:
        print("O ID do trilho deve ser um número inteiro!")
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def trilhos_monitorados():
    try:
        print("----- TRILHOS SENDO MONITORADOS -----\n")

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_TRILHO ORDER BY ID_TRILHO"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta (lista de tuplas)
        lista_dados = cursor.fetchall()

        # Verifica se há dados cadastrados
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados!")
        else:
            # exibe os itens da lista
            for item in lista_dados:
                print(item)
                print()
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def exportar_estacoes_linhas():
    try:
        print("Exportando estações das Linhas 8 e 9...\n")
        linhas_para_exportar = {
            1: "linha_8_diamante.json",
            2: "linha_9_esmeralda.json"
        }

        for linha_id, nome_arquivo in linhas_para_exportar.items():
            script = "SELECT * FROM T_TT_ESTACAO WHERE ID_LINHA = :1"
            cursor.execute(script, [linha_id])
            resultados = cursor.fetchall()

            if not resultados:
                print(f"Nenhuma estação encontrada para a linha {linha_id}.")
                continue

            colunas = [desc[0] for desc in cursor.description]
            dados_json = []

            for linha in resultados:
                registro = {}
                for col, val in zip(colunas, linha):
                    if isinstance(val, datetime):
                        registro[col] = val.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        registro[col] = val
                dados_json.append(registro)

            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados_json, f, indent=4, ensure_ascii=False)

            print(f"{len(dados_json)} estações exportadas para '{nome_arquivo}' com sucesso.")

    except Exception as error:
        print(f"Erro ao exportar estações: {error}")

def cadastrar_trilho():
    try:
        print("----- CADASTRAR TRILHO -----\n")

        localizacao = input("Localização do trilho: ")
        dt_instalacao_str = input("Data de instalação (AAAA-MM-DD): ")
        ultima_dt_manutencao_str = input("Data da última manutenção (AAAA-MM-DD): ")
        material = input("Material do trilho (opcional): ")

        # Conversão das strings para objetos datetime.date
        dt_instalacao = datetime.strptime(dt_instalacao_str, "%Y-%m-%d").date()
        ultima_dt_manutencao = datetime.strptime(ultima_dt_manutencao_str, "%Y-%m-%d").date()

        script = """INSERT INTO T_TT_TRILHO 
                    (LOCALIZACAO, DT_INSTALACAO, ULTIMA_DT_MANUTENCAO, MATERIAL) 
                    VALUES (:1, :2, :3, :4)"""

        cursor.execute(script, (localizacao, dt_instalacao, ultima_dt_manutencao, material))
        conn.commit()

        print("\nTrilho cadastrado com sucesso.")
        print()
    except Exception as error:
        print(f"Erro na transação com o banco de dados: {error}")

def alterar_dados_trilho():
    try:

        print("----- ALTERAR DADOS TRILHO-----\n")

        trilho_id = int(input("Digite o ID do trilho: "))

        # Monta a instrução SQL de consulta
        script = f"""SELECT * FROM T_TT_TRILHO WHERE ID_TRILHO = {trilho_id}"""

        # Executa o script SQL no banco de dados
        cursor.execute(script)

        # captura os dados de retorno da consulta
        lista_dados = cursor.fetchall()

        # Verifica se o registro está cadstrado
        if len(lista_dados) == 0:
            print(f"Não há dados cadastrados com o ID = {trilho_id}")
        else:
            # Solicita os novos valores
            localizacao = input("Localização do trilho: ")

            # Validação e conversão das datas
            while True:
                try:
                    dt_instalacao = input("Data de instalação (AAAA-MM-DD): ")
                    # Verifica se a data está no formato correto
                    datetime.strptime(dt_instalacao, '%Y-%m-%d')  # Isso irá lançar um erro se o formato estiver incorreto
                    break
                except ValueError:
                    print("Formato de data inválido. Use o formato AAAA-MM-DD.")

            while True:
                try:
                    ultima_dt_manutencao = input("Data da última manutenção (AAAA-MM-DD): ")
                    # Verifica se a data está no formato correto
                    datetime.strptime(ultima_dt_manutencao, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Formato de data inválido. Use o formato AAAA-MM-DD.")

            material = input("Material do trilho (opcional): ")

            # Constroi a instrução de edição do registro com os novos valores
            script = f"""UPDATE T_TT_TRILHO SET
                LOCALIZACAO = '{localizacao}',
                DT_INSTALACAO = TO_DATE('{dt_instalacao}', 'YYYY-MM-DD'),
                ULTIMA_DT_MANUTENCAO = TO_DATE('{ultima_dt_manutencao}', 'YYYY-MM-DD'),
                MATERIAL = '{material}'
                WHERE ID_TRILHO = {trilho_id}"""

            # Executa e altera o registro na Tabela
            cursor.execute(script)
            conn.commit()

            print("\nTrilho alterado com sucesso!")
            print()
    except ValueError:
        print("Digite um valor inteiro.")
    except Exception as error:
        print(f"Erro na transação do BD: {error}")

# Menu principal
# Solicitar credenciais de Acesso (usuário e senha)
login = input("Usuário..: ")
senha = input("Senha....: ")

# Tentativa de Conexão com o Banco de Dados
try:
    # Conexão com o banco de dados
    conn = oracledb.connect(user=login,
                            password=senha,
                            host="oracle.fiap.com.br",
                            port=1521,
                            service_name="ORCL")

    # Cria o cursor para realizar as operações no banco de dados
    cursor = conn.cursor()

    # Loop principal do sistema
    while True:
        print("1 - Exibir Status das Linhas")
        print("2 - Exibir estações")
        print("3 - Alertas no sistema")
        print("4 - Excluir alerta já concluído")
        print("5 - Registrar manutenção")
        print("6 - Histórico de manutenções")
        print("7 - Alterar dados da manutenção")
        print("8 - Cadastrar Trilho ")
        print("9 - Trilhos sendo monitorados")
        print("10 - Alterar dados do trilho")
        print("11 - Verificar riscos de flambagem")
        print("12 - Consultar manutenções por tipo")
        print("13 - Consultar estações por linhas")
        print("14 - Sair")

        escolha = int(input("Escolha uma opção: "))

        match escolha:
            case 1:
                status_linhas()
            case 2:
                exibir_estacoes()
            case 3:
                exibir_alertas()
            case 4:
                excluirAlerta()
            case 5:
                registrar_manutencao()
            case 6:
                historico_manutencoes()
            case 7:
                alterar_dados_manutencao()
            case 8:
                cadastrar_trilho()
            case 9:
                trilhos_monitorados()
            case 10:
                alterar_dados_trilho()
            case 11:
                verificar_riscos()
            case 12:
                consultar_manutencoes_por_tipo()
            case 13:
                exportar_estacoes_linhas()
            case 14:
                print('Programa finalizado.')
                conn.close()
                break
            case _:
                print('Opção inválida.')
except Exception as erro:
    # Informa o erro
    print(f"Erro: {erro}")
