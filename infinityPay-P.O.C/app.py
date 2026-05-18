from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import uuid
import queue
from datetime import datetime

event_queue = queue.Queue()

# ORDER_NSU_PEDIDO = str(uuid.uuid4()) 
# print(f"NSU do pedido: {ORDER_NSU_PEDIDO}")

app = Flask(__name__)
# Permitir todas as origens durante o desenvolvimento para evitar dor de cabeça
CORS(app) 

@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/flask-infinity-pay/create-agendamento", methods=["POST"])
# def create_agendamento():
#     data = request.json
#     # Dica: adicione um try/except aqui se o JSON puder vir incompleto
#     ORDER_NSU_PEDIDO = str(uuid.uuid4()) 
#     DATA_FORMATADA = data['data']
    
#     payload = {
#         "id": None,
#         "cliente": data['cliente'],
#         "servico": data['servico'],
#         "funcionaria": data['funcionaria'],
#         "preco": 1000,
#         "data": DATA_FORMATADA,
#         "hora": data['hora'],
#         "dia": data['dia'],
#         "mes": data['mes'],
#         "ano": data['ano'],
#         "status": "PENDENTE",
#         "pagamento": data['pagamento'],
#         "duracaoMinutos": data['duracaoMinutos'],
#         "pagamentoAdiantado": data.get('pagamentoAdiantado', False),
#         "ordemAgendamento": ORDER_NSU_PEDIDO,
#         "linkPagamento": None
#     }

#     print(f"Enviando payload para o Spring: {payload}")

#     response = requests.post(f"http://127.0.0.1:8080/spring/agendamentos/criar", json=payload)
#     response_data = response.json()
#     print(f"Resposta do Spring: {response_data}")


#     return jsonify({"status": "ok", "order_nsu": ORDER_NSU_PEDIDO}), 200

@app.route("/flask-infinity-pay/create-checkout", methods=["POST"])
def create_checkout():
    print(request.json)
    data = request.json
        
    payload = {
        "handle": "alexsander-torres",
        "order_nsu": data['id'],
        "items": [{
        "quantity": 1,
        "price": data["valorTotal"] * 100,
        "description": data["servico"]
        }],
        "customer": {
        "name": data["cliente"],
        "email": "cliete@gmail.com",
        "phone_number": "(11) 99999-9999"
        },
        "webhook_url": "https://interimperial-everette-nonascertainably.ngrok-free.dev/webhook"
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
    return "ok", 200
    requests.put("http://")



if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)