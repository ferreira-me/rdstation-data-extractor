import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Caminho do arquivo JSON (remover o caminho real)
json_path = "Caminho/do/arquivo/rdstation_data2.json"

# Carregar o JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Criar listas para armazenar os dados
tasks_list = []
deals_list = []

# Processar tasks
if 'tasks' in data:
    for task in data['tasks']:
        task_data = {
            "ID": task.get("id"),
            "deal_id": task.get("deal_id"),
            "Assunto": task.get("subject"),
            "Tipo": task.get("type"),
            "Hora": task.get("hour"),
            "Status": task.get("status"),
            "Data": task.get("date"),
            "Criado em": task.get("created_at"),
            "Feito": task.get("done"),
            "Data Conclusão": task.get("done_date"),
            "Negócio": task.get("deal", {}).get("name"),
            "Rating": task.get("deal", {}).get("rating"),
            "Usuário": task.get("users", [{}])[0].get("name"),
            "Email Usuário": task.get("users", [{}])[0].get("email")
        }
        tasks_list.append(task_data)

# Processar deals
if 'deals' in data:
    for deal in data['deals']:
        deal_data = {
            "ID": deal.get("id"),
            "Nome": deal.get("name"),
            "Valor Total": deal.get("amount_total"),
            "Data de Criação": deal.get("created_at"),
            "Última Atualização": deal.get("updated_at"),
            "Organização": deal.get("organization", {}).get("name"),
            "Endereço": deal.get("organization", {}).get("address"),
            "Usuário Responsável": deal.get("user", {}).get("name"),
            "Email Usuário": deal.get("user", {}).get("email"),
            "Estágio": deal.get("deal_stage", {}).get("name"),
            "Fonte": deal.get("deal_source", {}).get("name"),
            "Campanha": deal.get("campaign", {}).get("name"),
            "Próxima Tarefa": deal.get("next_task", {}).get("subject"),
            "Data Próxima Tarefa": deal.get("next_task", {}).get("date")
        }
        
        # Adicionando campos personalizados
        if "deal_custom_fields" in deal:
            for custom_field in deal["deal_custom_fields"]:
                label = custom_field.get("custom_field", {}).get("label")
                value = custom_field.get("value")
                if label:
                    deal_data[label] = value
        
        deals_list.append(deal_data)

# Criar DataFrames
df_tasks = pd.DataFrame(tasks_list)
df_deals = pd.DataFrame(deals_list)

# Tratamento para evitar erro de NaN no Google Sheets
df_tasks = df_tasks.fillna("").astype(str)
df_deals = df_deals.fillna("").astype(str)

# Caminho para salvar o arquivo Excel (remover o caminho real)
excel_path = r"Caminho/do/arquivo/rdstation_data.xlsx"

# Salvar em um arquivo Excel
with pd.ExcelWriter(excel_path) as writer:
    df_tasks.to_excel(writer, sheet_name="Tasks", index=False)
    df_deals.to_excel(writer, sheet_name="Deals", index=False)

print(f"Arquivo salvo com sucesso em {excel_path}")

# Autenticação com Google Sheets (remover caminho das credenciais)
cred_path = "Caminho/para/seu/arquivo/credenciais.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(cred_path, scopes=scope)
client = gspread.authorize(creds)

# Abrir a planilha (remover ID real da planilha)
spreadsheet_id = "ID_da_planilha_google"
sheet_tasks = client.open_by_key(spreadsheet_id).worksheet("Tasks")
sheet_deals = client.open_by_key(spreadsheet_id).worksheet("Deals")

# Substituir dados no Google Sheets
sheet_tasks.clear()
sheet_tasks.update([df_tasks.columns.values.tolist()] + df_tasks.values.tolist())

sheet_deals.clear()
sheet_deals.update([df_deals.columns.values.tolist()] + df_deals.values.tolist())

print("Dados enviados para o Google Sheets com sucesso!")
