import requests
from datetime import datetime
import os

# Configurações
GITHUB_TOKEN = 'seu_token_aqui'
REPO_OWNER = 'owner_do_repositorio'
REPO_NAME = 'nome_do_repositorio'

# Cabeçalhos para autenticação
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Função para buscar os PRs do repositório
def fetch_pull_requests():
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls'
    params = {'state': 'closed', 'per_page': 100}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Função para calcular métricas de PRs
def analyze_pull_requests(pr_data):
    total_time_to_review = 0
    total_comments = 0
    total_lines_changed = 0
    total_first_review_time = 0
    pr_count = 0

    for pr in pr_data:
        pr_count += 1
        created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        closed_at = datetime.strptime(pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
        time_to_review = (closed_at - created_at).total_seconds() / 3600  # em horas

        # Fetch comments para obter o primeiro feedback e contar total de comentários
        comments_url = pr['comments_url']
        comments = requests.get(comments_url, headers=headers).json()
        if comments:
            first_comment_at = datetime.strptime(comments[0]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            time_to_first_feedback = (first_comment_at - created_at).total_seconds() / 3600
        else:
            time_to_first_feedback = 0

        # Fetch files para obter número de linhas alteradas
        files_url = pr['url'] + '/files'
        files = requests.get(files_url, headers=headers).json()
        lines_changed = sum(f['additions'] + f['deletions'] for f in files)

        # Acumula dados para cálculos
        total_time_to_review += time_to_review
        total_comments += len(comments)
        total_lines_changed += lines_changed
        total_first_review_time += time_to_first_feedback

    # Cálculo das médias
    avg_time_to_review = total_time_to_review / pr_count if pr_count else 0
    avg_comments = total_comments / pr_count if pr_count else 0
    avg_lines_changed = total_lines_changed / pr_count if pr_count else 0
    avg_time_to_first_feedback = total_first_review_time / pr_count if pr_count else 0

    # Resultados
    return {
        "Average Time to Review (hours)": avg_time_to_review,
        "Average Comments per PR": avg_comments,
        "Average Lines Changed per PR": avg_lines_changed,
        "Average Time to First Feedback (hours)": avg_time_to_first_feedback
    }

# Execução do script
if __name__ == "__main__":
    print("Fetching Pull Requests...")
    pr_data = fetch_pull_requests()
    print("Analyzing Pull Requests...")
    metrics = analyze_pull_requests(pr_data)
    
    print("Code Review Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}")

