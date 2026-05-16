from pyngrok import ngrok
import time

# Expose Streamlit (port 8501)
streamlit_tunnel = ngrok.connect(8501)
print(f"🌐 Streamlit Public URL: {streamlit_tunnel.public_url}")

# Expose FastAPI (port 8001)
api_tunnel = ngrok.connect(8001)
print(f"🔌 FastAPI Public URL: {api_tunnel.public_url}")

print("\n✅ Share the Streamlit URL with your team members")
print("⚠️  Keep this script running — closing it kills the tunnels")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Tunnels closed")
    ngrok.kill()