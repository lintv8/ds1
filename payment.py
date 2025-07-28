import requests
import time
import hashlib
from database import Session, Order, Product
from config import Config

def create_plisio_invoice(user_id, product_id):
    """创建Plisio支付账单"""
    session = Session()
    product = session.query(Product).get(product_id)
    
    if not product:
        return None
    
    # 创建订单记录
    order = Order(
        user_id=user_id,
        product_id=product_id
    )
    session.add(order)
    session.commit()
    
    # 调用Plisio API
    params = {
        "api_key": Config.PLISIO_API_KEY,
        "order_name": f"Product_{product_id}",
        "order_number": f"ORDER_{order.id}",
        "source_amount": product.price,
        "source_currency": product.currency,
        "callback_url": f"{Config.WEBHOOK_URL}/plisio_webhook",
        "success_url": "https://t.me/your_bot",  # 支付成功跳转
        "currency": product.currency
    }
    
    response = requests.post(
        "https://plisio.net/api/v1/invoices/new",
        params=params
    ).json()
    
    if response.get("status") == "success":
        # 更新订单信息
        order.id = response["data"]["id"]  # Plisio的invoice ID
        order.created_at = time.time()
        session.commit()
        return response["data"]["invoice_url"]
    return None

def verify_plisio_signature(data):
    """验证Plisio Webhook签名"""
    received_sign = data.get("verify_hash")
    if not received_sign:
        return False
    
    # 生成验证签名
    data_str = ''.join(f"{k}={v}" for k, v in sorted(data.items()) if k != "verify_hash")
    computed_sign = hashlib.sha1((data_str + Config.PLISIO_SECRET).encode()).hexdigest()
    return received_sign == computed_sign

def handle_payment_webhook(data):
    """处理支付结果"""
    if not verify_plisio_signature(data):
        return False
    
    session = Session()
    order = session.query(Order).get(data["id"])
    
    if not order:
        return False
    
    # 更新订单状态
    if data["status"] == "completed":
        order.status = "completed"
        session.commit()
        return True
    
    return False
