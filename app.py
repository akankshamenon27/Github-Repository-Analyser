import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from flask import Flask, render_template, request
from github_analyzer import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    github_url = request.form['github_url']
    repositories = fetch_user_repositories(github_url)

    if repositories is not None:
        most_complex_repository = find_most_complex_repository(repositories)
        complexity_score = assess_technical_complexity(most_complex_repository)

        analysis_justification = "The repository has a high complexity score due to its large codebase, extensive use of advanced algorithms, and intricate architecture."

        return render_template('result.html', repository_name=most_complex_repository.name, repository_url=most_complex_repository.url, analysis_justification=analysis_justification)
    else:
        return "Failed to fetch repositories."

if __name__ == '__main__':
    app.run()
