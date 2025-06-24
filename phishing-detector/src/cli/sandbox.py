import requests
import webbrowser

def open_browserling(url):
    browserling_url = f"https://www.browserling.com/browse/chrome/100/{url}"
    try:
        webbrowser.open(browserling_url)
        return "Opened in Browserling sandbox. Inspect for redirects, scripts, or downloads."
    except Exception as e:
        return f"Failed to open Browserling: {e}"

def open_cuckoo(url):
    try:
        response = requests.post("http://localhost:8090/tasks/create", json={"url": url}, timeout=5)
        if response.status_code == 200:
            task_id = response.json()["task_id"]
            return f"Cuckoo task created: ID={task_id}. Check http://localhost:8080 for report."
        return "Cuckoo submission failed."
    except Exception:
        return "Cuckoo Sandbox not running or unreachable."