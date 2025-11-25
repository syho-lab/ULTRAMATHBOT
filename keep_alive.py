# keep_alive.py - для cron-job.org
import requests
import os

def ping_server():
    url = "https://ULTRAMATHBOT2.onrender.com"  # Ваш URL на Render
    try:
        response = requests.get(url)
        print(f"Ping successful: {response.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")

if __name__ == "__main__":
    ping_server()
