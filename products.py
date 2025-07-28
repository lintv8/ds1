from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Session, Product

def get_product_by_id(product_id):
    """获取单个商品信息"""
    session = Session()
    product = session.query(Product).get(product_id)
    session.close()
    return product

def get_all_products():
    """获取所有商品列表"""
    session = Session()
    products = session.query(Product).all()
    session.close()
    return products

def format_product_message(product):
    """格式化商品展示消息"""
    caption = f"🏷️ *{product.name}*\n\n" \
              f"📝 {product.description}\n\n" \
              f"💵 价格: *{product.price} {product.currency}*"
    
    keyboard = [
        [InlineKeyboardButton("立即购买", callback_data=f"buy_{product.id}")]
    ]
    
    return {
        "photo": product.image_url,
        "caption": caption,
        "reply_markup": InlineKeyboardMarkup(keyboard),
        "parse_mode": "Markdown"
    }
