from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import requests
import queue
import dotenv
import os

event_queue = queue.Queue()
headers = {
    "API-KEY": os.getenv("SPRING_API_KEY")
}

# ORDER_NSU_PEDIDO = str(uuid.uuid4()) 
# print(f"NSU do pedido: {ORDER_NSU_PEDIDO}")

app = Flask(__name__)
# Permitir todas as origens durante o desenvolvimento para evitar dor de cabeça
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")
@app.route("/")

def index():
    return render_template("index.html")

@app.route("/flask-infinity-pay/create-checkout", methods=["POST"])
def create_checkout():

    request_payload = request.get_json()
    id = request_payload.get("idAgendamento")

#checar se o agendament exsite no sistema por UUID
    if (requests.get(f"http://127.0.0.1:8080/agendamentos/{id}", headers=headers)
        ).status_code == 200:
        print(f"Agendamento {id} encontrado no sistema")

    else:
        print(f"Agendamento {id} não encontrado no sistema")
        return jsonify({"error": "Agendamento não encontrado"}), 404
    
#gerar payload com informações do agendamento  
 
    agendamento_data = requests.get(f"http://127.0.0.1:8080/agendamentos/{id}", headers=headers).json()

    print(f"Dados do agendamento: {agendamento_data}")


    payload = {
    "handle": "alexsander-torres",
    "order_nsu": agendamento_data["id"],
    "items": [
        {
            "quantity": 1,
            # InfinitePay trabalha em centavos
            "price": int(agendamento_data["valorTotal"] * 100),
            # Pegando o primeiro serviço
            "description": agendamento_data["profissional"]["servicos"][0]["nome"]
        }
    ],
    "customer": {
        "name": agendamento_data["cliente"]["usuario"]["nome"],
        "email": agendamento_data["cliente"]["usuario"]["email"],
        "phone_number": agendamento_data["cliente"]["usuario"]["telefone"]
    },
    "webhook_url": "https://hurler-console-entrench.ngrok-free.dev/webhook"
}
    
    response = requests.post(
        "https://api.infinitepay.io/invoices/public/checkout/links",
        json=payload
    )
    print(response)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.get_json()

    event_queue.put(data)

    print("=+" * 30)
    print(data)
    print("=+" * 30)

    agendamento_data = requests.get(
        f"http://127.0.0.1:8080/agendamentos/{data['order_nsu']}",
        headers=headers
    ).json()

    print("=+" * 30)
    print(f"Evento recebido no Webhook: {agendamento_data}")
    print("=+" * 30)

    agendamento_data["status"] = "CONFIRMADO"

    print("=+" * 30)
    print(f"Confirmado: {agendamento_data}")
    print("=+" * 30)

    requests.put(
        f"http://127.0.0.1:8080/agendamentos/{data['order_nsu']}",
        headers=headers,
        json=agendamento_data
    )

    # envia evento websocket para o frontend
    socketio.emit("pagamento_confirmado", {
        "order_nsu": data["order_nsu"],
        "status": "CONFIRMADO"
    })

    return "ok", 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8088)