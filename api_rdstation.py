import json
import requests
import os

class CRMClient:
    BASE_URL = "https://crm.rdstation.com/api/v1/"
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, token):
        self.TOKEN = token

    def get_all_pages(self, endpoint, key=None):
        """ Obtém todos os dados, considerando paginação e chaves corretas """
        all_data = []
        page = 1
        while True:
            response = self.request("GET", endpoint, params={"page": page})

            # Se houver erro, exibir e retornar lista vazia
            if isinstance(response, str) or "message" in response:
                print(f"Erro ao buscar {endpoint}: {response}")
                return []

            # Se houver uma chave específica, extrai só os dados dela
            if key and key in response:
                data = response[key]
            else:
                data = response  # Se não houver chave, pega tudo

            all_data.extend(data)  # Adiciona os dados da página atual

            if "has_more" in response and not response["has_more"]:
                break  # Sai do loop se não houver mais páginas
            
            page += 1  # Passa para a próxima página
        return all_data

    def request(self, method, endpoint, params={}):
        """ Faz a requisição HTTP e retorna os dados """
        params.update(token=self.TOKEN)  # Adiciona o token
        response = requests.request(method, self.BASE_URL + endpoint, headers=self.HEADERS, params=params)

        try:
            return response.json()
        except ValueError:
            return f"Erro ao converter resposta JSON: {response.text}"

    # Métodos para obter os dados completos
    def list_tasks(self):
        return self.get_all_pages("tasks", key="tasks")
    
    def list_deals(self):
        return self.get_all_pages("deals", key="deals")
    
    def list_deal_stages(self):
        return self.get_all_pages("deal_stages", key="deal_stages")

def save_data_to_json(data, filename="rdstation_data2.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Exemplo de uso
api_key = os.getenv("RD_API_TOKEN")  # Carregar token de uma variável de ambiente
client = CRMClient(api_key)

# Obter todos os dados necessários
data_to_save = {
    "tasks": client.list_tasks(),
    "deals": client.list_deals(),
    "deal_stages": client.list_deal_stages()
}

# Salvar os dados em um arquivo JSON
save_data_to_json(data_to_save)

print("Todos os dados foram salvos com sucesso em rdstation_data2.json!")
