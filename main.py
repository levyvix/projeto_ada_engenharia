import json
from datetime import datetime

from prettytable import PrettyTable

try:
    with open("registros.json", "r") as arquivo_json:
        registros = json.load(arquivo_json)
    contador_id = registros[-1].get("id", 0) + 1
except FileNotFoundError:
    registros = []
    contador_id = 0


def json_to_table(json_data):
    if not json_data:
        return "Nenhum registro encontrado."

    table = PrettyTable()
    table.field_names = ["id", "tipo", "valor", "data", "taxa_juros", "montante"]

    for registro in json_data:
        table.add_row(
            [
                registro["id"],
                registro["tipo"],
                registro["valor"],
                registro["data"]["completa"],
                registro.get("taxa_juros", ""),
                registro.get("montante", ""),
            ]
        )
    return table


def agrupar_por_tipo(campo="tipo"):
    resultado = {}
    # soma de receitas, despesas e investimentos
    for registro in registros:
        chave = registro[campo]
        if chave not in resultado:
            resultado[chave] = 0
        resultado[chave] += registro["valor"]

    table = PrettyTable()

    table.field_names = ["Tipo", "Valor"]

    for tipo in resultado:
        table.add_row([tipo, resultado[tipo]])

    return table


def agrupar_por_mes(campo="mes"):
    resultado = {}

    # receita, despesa, investimento e saldo por mes
    for registro in registros:
        chave = registro["data"][campo]
        if chave not in resultado:
            resultado[chave] = {
                "receita": 0,
                "despesa": 0,
                "investimento": 0,
                "juros": 0,
                "saldo": 0,
            }
        if registro["tipo"] == "receita":
            resultado[chave]["receita"] += registro["valor"]
        elif registro["tipo"] == "despesa":
            resultado[chave]["despesa"] += registro["valor"]
        elif registro["tipo"] == "investimento":
            resultado[chave]["investimento"] += registro["valor"]
            resultado[chave]["juros"] += registro["montante"] - registro["valor"]

        resultado[chave]["saldo"] = (
            resultado[chave]["receita"]
            + resultado[chave]["despesa"]
            + resultado[chave]["investimento"]
            + resultado[chave]["juros"]
        )

    # print table
    table = PrettyTable()

    table.field_names = ["Mês", "Receita", "Despesa", "Investimento", "Juros", "Saldo"]

    for mes in resultado:
        table.add_row(
            [
                mes,
                resultado[mes]["receita"],
                resultado[mes]["despesa"],
                resultado[mes]["investimento"],
                resultado[mes]["juros"],
                resultado[mes]["saldo"],
            ]
        )

    return table


# Função para obter input seguro
def obter_input(mensagem):
    try:
        return input(mensagem)
    except KeyboardInterrupt:
        return None


def obter_saldo():
    """obtem o salto total do sistema financeiro
    soma toas as receitas e subtrai todas as despesas, tambem soma o valor do montante dos investimentos

    Returns:
        saldo: saldo total do sistema financeiro
    """
    # atualizar_rendimento()
    saldo = 0
    for registro in registros:
        saldo += registro["valor"] + registro.get("montante", 0)
    return saldo


def atualizar_registro(id, novo_valor, novo_tipo, nova_data):
    for registro in registros:
        if registro["id"] == id:
            if novo_tipo != "":
                registro["tipo"] = novo_tipo
            if novo_valor != "":
                registro["valor"] = novo_valor

            if nova_data != "":
                registro["data"]["completa"] = nova_data.isoformat()
                registro["data"]["dia"] = nova_data.day
                registro["data"]["mes"] = nova_data.month
                registro["data"]["ano"] = nova_data.year


def exportar_relatorio():
    with open("registros.json", "w") as arquivo_json:
        json.dump(registros, arquivo_json, default=str, indent=4)


def atualizar_rendimento():
    for registro in registros:
        if registro["tipo"] == "investimento":
            valor_investido = registro.get("valor", 0)
            taxa_juros = registro.get("taxa_juros", 0)
            # tempo_dias = registro.get('tempo_dias', 0)
            date_format = "%Y-%m-%d"
            date_object = datetime.strptime(
                registro["data"]["completa"], date_format
            ).date()
            tempo_dias = (datetime.now().date() - date_object).days
            registro["montante"] = valor_investido * (1 + taxa_juros) ** tempo_dias


def criar_registro(tipo, valor, data):
    global contador_id

    if tipo == "investimento":
        if obter_saldo() < float(valor):
            print("Erro: Não é possível investir mais do que você tem de receita.")
            return
    elif tipo == "despesa":
        if obter_saldo() < 0:
            print(
                "Erro: Antes de cadastrar uma despesa, é necessário ter pelo menos uma receita."
            )
            return
        if obter_saldo() < float(valor):
            print(
                "Erro: Não é possível fazer uma despesa maior do que a receita disponível."
            )
            return

    if tipo == "receita":
        registros.append(
            {
                "id": contador_id,
                "data": {
                    "completa": data.date().isoformat(),
                    "dia": data.day,
                    "mes": data.month,
                    "ano": data.year,
                },
                "tipo": tipo,
                "valor": valor,
            }
        )
        contador_id += 1

    if tipo == "despesa":
        # verificar valor
        registros.append(
            {
                "id": contador_id,
                "data": {
                    "completa": data.date().isoformat(),
                    "dia": data.day,
                    "mes": data.month,
                    "ano": data.year,
                },
                "tipo": tipo,
                "valor": -valor,
            }
        )
        contador_id += 1

    if tipo == "investimento":
        valor_investido = valor
        taxa_juros = obter_input("Informe a taxa de juros [0.01 -> 1%]: ")

        try:
            taxa_juros = float(taxa_juros)
        except ValueError:
            print("Erro: Taxa de juros inválida. Tente novamente.")
            while True:
                taxa_juros = obter_input("Informe a taxa de juros: ")
                try:
                    taxa_juros = float(taxa_juros)
                    break
                except ValueError:
                    print("Erro: Taxa de juros inválida. Tente novamente.")

        tempo_dias = (datetime.now() - data).days
        montante = valor_investido * (1 + taxa_juros) ** tempo_dias

        registros.append(
            {
                "id": contador_id,
                "data": {
                    "completa": data.date().isoformat(),
                    "dia": data.day,
                    "mes": data.month,
                    "ano": data.year,
                },
                "tipo": tipo,
                "valor": valor,
                "taxa_juros": taxa_juros,
                "montante": montante,
            }
        )

        contador_id += 1


def deletar_registro(id_registro):
    try:
        id_registro = int(id_registro)  # Tenta converter o ID para um número inteiro

        if not isinstance(
            id_registro, int
        ):  # Verifica se o ID fornecido é do tipo inteiro
            raise TypeError("O ID deve ser um número inteiro")

        registro_encontrado = None  # Procura o registro com o ID fornecido
        for registro in registros:
            if registro["id"] == id_registro:
                registro_encontrado = registro
                break

        if (
            registro_encontrado
        ):  # Se o registro foi encontrado, remove-o da lista de registros
            registros.remove(registro_encontrado)
            print(f"Registro com ID {id_registro} removido com sucesso.")
        else:
            print(
                f"Nenhum registro encontrado com o ID {id_registro}.Verifique o ID e tente novamente."
            )

    except ValueError:
        print("Erro: O ID fornecido não é um número inteiro.")
    except TypeError as e:
        print(f"Erro: {e}")


def ler_registros(filtro: dict = None) -> list:
    """Le os registros do sistema financeiro, filtrando por tipo, data ou valor.

    Args:
        filtro (dict, optional): Filtro com chaves 'campo' e 'valor'. Defaults to None.
        data (str, optional): Data para filtrar os registros. Defaults to None.

    Returns:
        list: Registros filtrados pelo filtro.
    """
    atualizar_rendimento()
    registros_filtrados = registros[:]

    try:
        if filtro["dia"] or filtro["mes"] or filtro["ano"]:
            filtro_dia = int(filtro["dia"]) if filtro["dia"] else ""
            filtro_mes = int(filtro["mes"]) if filtro["mes"] else ""
            filtro_ano = int(filtro["ano"]) if filtro["ano"] else ""

            if filtro_dia != "":
                registros_filtrados = list(
                    filter(
                        lambda x: x["data"]["dia"] == filtro_dia, registros_filtrados
                    )
                )

            if filtro_mes != "":
                registros_filtrados = list(
                    filter(
                        lambda x: x["data"]["mes"] == filtro_mes, registros_filtrados
                    )
                )

            if filtro_ano != "":
                registros_filtrados = list(
                    filter(
                        lambda x: x["data"]["ano"] == filtro_ano, registros_filtrados
                    )
                )

        if filtro["tipo"]:
            registros_filtrados = list(
                filter(lambda x: x["tipo"] == filtro["tipo"], registros_filtrados)
            )

        if filtro["menor_que"] and filtro["maior_que"]:
            menor_que = float(filtro["menor_que"])
            maior_que = float(filtro["maior_que"])

            registros_filtrados = list(
                filter(
                    lambda x: maior_que <= abs(x["valor"]) <= menor_que,
                    registros_filtrados,
                )
            )
        elif filtro["menor_que"]:
            menor_que = float(filtro["menor_que"])
            registros_filtrados = list(
                filter(lambda x: x["valor"] <= menor_que, registros_filtrados)
            )
        elif filtro["maior_que"]:
            maior_que = float(filtro["maior_que"])
            registros_filtrados = list(
                filter(lambda x: x["valor"] >= maior_que, registros_filtrados)
            )

        return json_to_table(registros_filtrados)
    except (ValueError, TypeError) as e:
        print(f"Erro: {e}")
        return []


def total_por_tipo():
    totais_por_tipo = {"receita": 0, "despesa": 0, "investimento": 0}

    for registro in registros:
        tipo = registro["tipo"]
        valor = registro["valor"]

        if "montante" in registro.keys():
            totais_por_tipo[tipo] += registro["montante"]

        totais_por_tipo[tipo] += abs(valor)

    print("\nTOTAL POR TIPO:\n")
    for tipo, total in totais_por_tipo.items():
        print(f"{tipo.capitalize()}: {total:0.2f}")


continuar = True

try:
    while continuar:
        print("-" * 100)
        print("\nSistema Financeiro - FinanciADA")
        print(f"Saldo: {obter_saldo()}")
        print("\nOpções:")
        print("1. Criar Registro")
        print("2. Ler Registros")
        print("3. Atualizar Registro")
        print("4. Deletar Registro")
        print("5. Atualizar Rendimento")
        print("6. Exportar Relatório")
        print("7. Agrupar por")
        print("8. Encerrar")

        escolha = obter_input("Escolha a opção (1-8): ")

        if escolha == "1":
            tipo = obter_input(
                "Informe o tipo de movimentação: (receita/despesa/investimento) "
            )
            if tipo not in ["receita", "despesa", "investimento"]:
                print("Erro: Tipo inválido. Tente novamente.")
                while True:
                    tipo = obter_input(
                        "Informe o tipo de movimentação: (receita/despesa/investimento) "
                    )
                    if tipo in ["receita", "despesa", "investimento"]:
                        break
                    else:
                        print("Erro: Tipo inválido. Tente novamente.")

            valor = obter_input("Informe o valor da movimentação: ")
            try:
                valor = float(valor)
            except ValueError:
                print("Erro: Valor inválido. Tente novamente.")
                while True:
                    valor = obter_input("Informe o valor da movimentação: ")
                    try:
                        valor = float(valor)
                        break
                    except ValueError:
                        print("Erro: Valor inválido. Tente novamente.")

            data_movimentacao = obter_input(
                "Informe a data da movimentação no formato DD/MM/AAAA: "
            )

            try:
                data_formatada = datetime.strptime(data_movimentacao, "%d/%m/%Y")
            except:
                print("Erro: Data inválida. Tente novamente.")
                while True:
                    data_movimentacao = obter_input(
                        "Informe a data da movimentação no formato DD/MM/AAAA: "
                    )
                    try:
                        data_formatada = datetime.strptime(
                            data_movimentacao, "%d/%m/%Y"
                        )
                        break
                    except:
                        print("Erro: Data inválida. Tente novamente.")

            criar_registro(tipo, valor, data_formatada)

        if escolha == "2":
            filtro = {
                "dia": "",
                "mes": "",
                "ano": "",
                "tipo": "",
                "menor_que": "",
                "maior_que": "",
            }
            # filtro = obter_input("Filtrar por campo (data/tipo/valor) - deixe em branco para nenhum): ")
            data_filtro = obter_input("Filtrar por data? [s/n]: ")
            if data_filtro.lower() == "s":
                data_filtro_dia = input("Informe o dia [deixe em branco para todos]: ")
                data_filtro_mes = input("Informe o mês [deixe em branco para todos]: ")
                data_filtro_ano = input("Informe o ano [deixe em branco para todos]: ")

                if data_filtro_dia != "":
                    data_filtro_dia = int(data_filtro_dia)
                    filtro["dia"] = data_filtro_dia

                if data_filtro_mes != "":
                    data_filtro_mes = int(data_filtro_mes)
                    filtro["mes"] = data_filtro_mes

                if data_filtro_ano != "":
                    data_filtro_ano = int(data_filtro_ano)
                    filtro["ano"] = data_filtro_ano

            tipo_filtro = obter_input("Filtrar por tipo? [s/n]: ")
            if tipo_filtro.lower() == "s":
                valor_filtro = obter_input("Valor do filtro: ")
                filtro["tipo"] = valor_filtro

            valor_filtro = obter_input("Filtrar por valor? [s/n]: ")
            if valor_filtro.lower() == "s":
                menor_que = obter_input("Menor que (deixe em branco para nenhum): ")
                maior_que = obter_input("Maior que (deixe em branco para nenhum): ")
                filtro["menor_que"] = menor_que
                filtro["maior_que"] = maior_que

            print(ler_registros(filtro))

        if escolha == "3":
            id_registro = obter_input("ID do registro a ser atualizado: ")

            try:
                id_registro = int(id_registro)

            except ValueError:
                while not isinstance(id_registro, int):
                    print("ID não é um inteiro. digite novamente")
                    id_registro = obter_input("ID do registro a ser atualizado: ")

            novo_valor = obter_input("Novo valor [Deixe em branco para não alterar]: ")

            if novo_valor != "":
                try:
                    novo_valor = float(novo_valor)
                except:
                    while not isinstance(novo_valor, float):
                        print("Valor não é um float. digite novamente")
                        novo_valor = obter_input(
                            "Novo valor [Deixe em branco para não alterar]: "
                        )

            novo_tipo = obter_input("Novo tipo [Deixe em branco para não alterar]: ")

            if novo_tipo != "":
                if novo_tipo not in ["receita", "despesa", "investimento"]:
                    print("Erro: Tipo inválido. Tente novamente.")
                    while True:
                        novo_tipo = obter_input(
                            "Informe o novo tipo de movimentação: (receita/despesa/investimento) "
                        )
                        if novo_tipo in ["receita", "despesa", "investimento"]:
                            break
                        else:
                            print("Erro: Tipo inválido. Tente novamente.")

            nova_data = obter_input("Nova data [Deixe em branco para não alterar]: ")
            data_formatada = ""
            if nova_data != "":
                try:
                    data_formatada = datetime.strptime(nova_data, "%d/%m/%Y").date()
                except:
                    print("Erro: Data inválida. Tente novamente.")
                    while True:
                        nova_data = obter_input("Data (DD/MM/AAAA): ")
                        try:
                            data_formatada = datetime.strptime(
                                nova_data, "%d/%m/%Y"
                            ).date()
                            break
                        except:
                            print("Erro: Data inválida. Tente novamente.")

            atualizar_registro(
                id_registro,
                novo_tipo=novo_tipo,
                novo_valor=novo_valor,
                nova_data=data_formatada,
            )

        if escolha == "4":
            id_registro = obter_input("Informe o ID do registro: ")
            deletar_registro(id_registro)

        if escolha == "6":
            atualizar_rendimento()
            exportar_relatorio()

        if escolha == "7":
            campo = obter_input("Agrupar por campo (tipo/mes): ")
            if campo == "tipo":
                print(agrupar_por_tipo())
            elif campo == "mes":
                print(agrupar_por_mes())
            else:
                print("Erro: Campo inválido. Tente novamente.")
        if escolha == "8":
            atualizar_rendimento()
            exportar_relatorio()
            continuar = False

finally:
    atualizar_rendimento()
    exportar_relatorio()
    print("Obrigado por escolher o nosso sistema! Volte Sempre!")
