from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
from datetime import timedelta, datetime
import threading
import json

app = Flask(__name__)
CORS(app)

# 设置日志记录格式和级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

with open('config.json') as f:
    config_lim = json.load(f)



defaut_lim='20/3h'


# 访客字典
visitors = {}
lock = threading.Lock()


class RateLimit:
    def __init__(self, limit, per):
        self.limit = limit  # 最大请求数
        self.per = per  # 时间间隔
        self.tokens = limit  # 当前的可用令牌数
        self.last_check = time.time()  # 上次检查的时间

    def can_consume(self, num_tokens):
        """检查是否可以消耗指定数量的令牌"""
        now = time.time()
        time_elapsed = now - self.last_check
        self.last_check = now
        
        # 根据时间间隔补充令牌
        new_tokens = time_elapsed * (self.limit / self.per.total_seconds())
        self.tokens = min(self.limit, self.tokens + new_tokens)
        
        logger.info(f"可用次数: {self.tokens}, 总次数: {self.limit}/{self.per}")

        if self.tokens >= num_tokens:
            return True
        return False

    def consume(self, num_tokens):
        """消耗令牌"""
        self.tokens -= num_tokens


class Visitor:
    def __init__(self, limit, per):
        self.limiter = RateLimit(limit, per)
        self.last_seen = time.time()

def parse_duration(duration_str):
    """解析类似于 '3h' 格式的时间，返回秒数"""
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    num = int(duration_str[:-1])
    unit = duration_str[-1]
    return timedelta(seconds=num * units[unit])

def get_visitor(token,carid, model):
    with lock:
        # 获取carid和model对应的限速配置
        try:
            if carid in config_lim:
                carid_limit=config_lim[carid]
            else:
                carid = 'base'
                carid_limit=config_lim[carid]
            model_limit = carid_limit[model]
            limit= model_limit.split('/')[0]
            per= model_limit.split('/')[1]
        except Exception as e:
            logger.warning(f"该车队没有设置限速: {e}")
            limit= defaut_lim.split('/')[0]
            per= defaut_lim.split('/')[1]

        limit = int(limit)
        per = parse_duration(per)

        key = f"{token}|{carid}|{model}"
        visitor = visitors.get(key)
        if not visitor:
            visitor = Visitor(limit, per)
            visitors[key] = visitor
        visitor.last_seen = time.time()
        return visitor.limiter, None

def cleanup_visitors():
    """定期清理不活跃的访客"""
    with lock:
        now = time.time()
        tokens_to_delete = []
        for token, visitor in visitors.items():
            if now - visitor.last_check > visitor.per.total_seconds():
                tokens_to_delete.append(token)
        
        # 批量删除不活跃的访客
        for token in tokens_to_delete:
            del visitors[token]
        print(f"{len(tokens_to_delete)} visitors cleaned up at {datetime.now()}")

def start_cleanup_thread():
    """启动每周一次的清理线程"""
    def run_cleanup():
        while True:
            time.sleep(7 * 24 * 3600)  # 每星期清理一次
            cleanup_visitors()

    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()



@app.route('/', methods=['GET'])
def index():

    return jsonify({"message": "Welcome to oneperfect’s world"}), 200



@app.route('/limit', methods=['POST'])
def limit():
    
    data = request.json
    carid = request.headers.get('Carid', '')  # 获取请求头中的 carid
    token = request.headers.get('Authorization', '')[7:]  # 移除 Bearer 前缀
    model = data.get('model', '')
    gfsessionid = request.cookies.get('gfsessionid', '')
    action = data.get('action', '')
    prompt = data.get('messages')[0]['content']['parts'][0]
    logger.info(f"carid: {carid}, token: {token}, model: {model}, gfsessionid: {gfsessionid}")
    logger.info(f"action: {action}, prompt: {prompt}")
    if not token or not model or not gfsessionid or not carid:
        return jsonify({"error": "Missing token or model or gfsessionid or carid"}), 400
    
    limiter, error = get_visitor(token, carid[:4], model)
    if error:
        return jsonify({"error": error}), 400
    
    if not limiter.can_consume(1):
        return jsonify({
            "error": f"You have triggered the usage frequency limit for {model}, "
                     f"please wait a moment before trying again."
        }), 429

    limiter.consume(1)  # 消耗一个令牌
    
    return jsonify({"message": "Request allowed"}), 200

if __name__ == '__main__':
    # 初始化时启动清理线程
    start_cleanup_thread()
    app.run(host='0.0.0.0', port=41758)
