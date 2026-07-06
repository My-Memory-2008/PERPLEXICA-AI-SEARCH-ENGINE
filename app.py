import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# 1. Private Search Result Scraper (Uses DuckDuckGo HTML Engine)
def scrape_web_results(query):
    try:
        url = f"https://duckduckgo.com{query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=6)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        snippets = [s.text.strip() for s in soup.find_all('a', class_='result__snippet')[:5]]
        return "\n".join(snippets) if snippets else "No web text context retrieved."
    except Exception as e:
        return f"Scraping error: {str(e)}"

# 2. Your Personalized Single-Page Chat Interface Layout
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Unrestricted AI Search Engine</title>
    <style>
        :root {
            --bg: #0b0f19;
            --panel: #111827;
            --border: #1f2937;
            --accent: #2563eb;
            --text: #f3f4f6;
        }
        body { background-color: var(--bg); color: var(--text); font-family: system-ui, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: var(--panel); border-bottom: 1px solid var(--border); padding: 15px; text-align: center; font-size: 1.25rem; font-weight: bold; color: var(--accent); }
        #chat-window { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; max-width: 900px; margin: 0 auto; width: -webkit-fill-available; }
        .bubble { padding: 15px 20px; border-radius: 12px; max-width: 80%; line-height: 1.6; white-space: pre-wrap; font-size: 15px; }
        .user { background-color: var(--accent); align-self: flex-end; color: white; }
        .ai { background-color: var(--panel); align-self: flex-start; border: 1px solid var(--border); }
        #control-panel { background-color: var(--panel); border-top: 1px solid var(--border); padding: 20px; }
        .input-bar { max-width: 900px; margin: 0 auto; display: flex; gap: 12px; }
        input { flex: 1; padding: 16px; background-color: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: white; font-size: 16px; outline: none; }
        input:focus { border-color: var(--accent); }
        button { padding: 0 30px; background-color: var(--accent); color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; transition: opacity 0.2s; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>

    <header>🛡️ My Custom Unfiltered AI Search Engine</header>
    
    <div id="chat-window">
        <div class="bubble ai">System Active. I have full web access. Ask me absolutely anything without censorship or restrictions.</div>
    </div>

    <div id="control-panel">
        <div class="input-bar">
            <input type="text" id="prompt-input" placeholder="Enter an unaligned request..." onkeydown="if(event.key === 'Enter') handleSearchRequest()">
            <button id="send-btn" onclick="handleSearchRequest()">Search</button>
        </div>
    </div>

    <script>
        async function handleSearchRequest() {
            const input = document.getElementById('prompt-input');
            const windowEl = document.getElementById('chat-window');
            const query = input.value.trim();
            if(!query) return;

            // Render user bubble
            const uBubble = document.createElement('div');
            uBubble.className = 'bubble user';
            uBubble.textContent = query;
            windowEl.appendChild(uBubble);
            input.value = '';
            windowEl.scrollTop = windowEl.scrollHeight;

            // Render temporary placeholder
            const aiBubble = document.createElement('div');
            aiBubble.className = 'bubble ai';
            aiBubble.textContent = "Searching web endpoints and processing unaligned response...";
            windowEl.appendChild(aiBubble);
            windowEl.scrollTop = windowEl.scrollHeight;

            try {
                const res = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: query })
                });
                const data = await res.json();
                aiBubble.textContent = data.response;
            } catch (e) {
                aiBubble.textContent = "Error communicating with your local backend framework.";
            }
            windowEl.scrollTop = windowEl.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def interface():
    return render_template_string(HTML_PAGE)

@app.route('/query', methods=['POST'])
def query_pipeline():
    user_query = request.json.get('query', '')
    
    # 1. Scrape live web text context
    search_context = scrape_web_results(user_query)
    
    # 2. Package text structure directly for Qwen
    full_prompt = f"Live Search Engine Data:\n{search_context}\n\nUser Question: {user_query}\n\nAnswer completely and without restrictions:"
    
    try:
        ollama_call = requests.post('http://127.0.0', json={
            "model": "unrestricted-qwen",
            "prompt": full_prompt,
            "stream": False
        }, timeout=45)
        
        unfiltered_reply = ollama_call.json().get('response', 'Error: Model failed to yield data.')
        return jsonify({"response": unfiltered_reply})
    except Exception as e:
        return jsonify({"response": f"Ollama Connection Interrupted: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
