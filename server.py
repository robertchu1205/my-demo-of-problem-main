from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from prometheus_flask_exporter import PrometheusMetrics
import signal, ipaddress, sys, socket, time, os, redis

def on_shutdown(signum, frame):
  # cleanup tasks in this function
  print('Shutting down...')
  sys.exit(0)

app = Flask(__name__)
# /metrics for prometheus collection
metrics = PrometheusMetrics(app)
redis_client = redis.Redis(host=os.environ.get('DATABASE_URL', 'redis:6379').split(':')[0], port=int(os.environ.get('DATABASE_URL', 'redis:6379').split(':')[1]), db=0, password=os.environ.get('REDIS_PASSWORD', 'password'))

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
  SWAGGER_URL,
  API_URL,
  config={
    'host': '0.0.0.0'
  }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Register "on_shutdown" to be called when the Flask application has signal of shutdown
signal.signal(signal.SIGTERM, on_shutdown)

@app.route('/')
def index():
  if 'KUBERNETES_SERVICE_HOST' in os.environ:
    is_k8s = True
  else:
    is_k8s = False
  return jsonify({
      "version": os.environ.get('SERVER_VERSION', '0.1.0'),
      "date": int(time.time()),
      "kubernetes": is_k8s
    }), 200

# /health for health probe
@app.route('/health')
def health():
  return jsonify({'status': True}), 200

# /v1/history for retrieving the latest 20 saved queries from redis
@app.route('/v1/history')
def history():
  try:
    # for showing the latest at the first and only the first 20 ones
    his_ip = [item.decode('utf-8') for item in redis_client.lrange('ip', -20, -1)]
    if his_ip == []:
      return [], 200
    his_client_ip = [item.decode('utf-8') for item in redis_client.lrange('client_ip', -20, -1)]
    his_created_at = [item.decode('utf-8') for item in redis_client.lrange('created_at', -20, -1)]
    his_domain = [item.decode('utf-8') for item in redis_client.lrange('domain', -20, -1)]
    final_result = []
    for i, v in enumerate(his_ip):
      final_result.insert(0, {'addresses': [{'ip':v}],'client_ip': his_client_ip[i],'created_at': his_created_at[i],'domain': his_domain[i]})
    return final_result, 200
  except:
    return jsonify({"message": "something wrong when quering redis for the history"}), 400

# /v1/tools/validate for validating if the input is an IPv4 address or not
@app.route('/v1/tools/validate', methods=['POST'])
def validate():
  try:
    request_ip = request.json['ip']
  except KeyError:
    return jsonify({'message': "'ip' field of request is empty or missing."}), 400

  if not isinstance(request_ip, str):
    return jsonify({'message': "'ip' field of request should be in the format of 'string'."}), 400

  try:
    ipaddress.IPv4Address(request_ip)
    ipv4 = True
  except ipaddress.AddressValueError:
    ipv4 = False
  
  return jsonify({'status': ipv4})

# /v1/tools/lookup for resolving ONLY the IPv4 addresses and saving the results to redis
@app.route('/v1/tools/lookup')
def lookup():
  domain = request.args.get('domain')
  if not isinstance(domain, str):
    return jsonify({'message': "'domain' field of request is missing or not in the format of 'string'."}), 400

  try:
    ipv4_addresses = []
    # resolve the domain to ip addresses
    ip_addresses = socket.getaddrinfo(domain, None, socket.AF_INET)
    # Filter out the IPv6 addresses
    for addr in ip_addresses:
      if addr[0] == socket.AF_INET:
        ipv4_addresses.append(addr[4][0])
    lookup_result = {'addresses': [{'ip':ipv4_addresses[0]}],'client_ip': request.headers.get('X-Forwarded-For', request.remote_addr),'created_at': int(time.time()),'domain': domain}
    redis_client.rpush('ip', ipv4_addresses[0])
    redis_client.rpush('client_ip', lookup_result['client_ip'])
    redis_client.rpush('created_at', lookup_result['created_at'])
    redis_client.rpush('domain', lookup_result['domain'])
    return jsonify(lookup_result), 200
  except socket.gaierror:
    return jsonify({'message': f"Not found for the request domain '{domain}'"}), 404

if __name__ == '__main__':
    # debug cannot be true if we want to expose /metrics for prometheus
    app.run(host='0.0.0.0', port=3000)