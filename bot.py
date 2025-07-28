import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from products import get_all_products, format_product_message, get_product_by_id
from payment import create_plisio_invoice
from database import Session, Order
from config import Config

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示所有商品"""
    products = get_all_products()
    for product in products:
        product_msg = format_product_message(product)
        await update.message.reply_photo(**product_msg)

async def handle_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理购买请求"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    user_id = query.from_user.id
    
    # 创建支付链接
    invoice_url = create_plisio_invoice(user_id, product_id)
    
    if invoice_url:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("支付账单", url=invoice_url)]])
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n✅ 已生成支付链接，请点击下方按钮完成支付",
            reply_markup=keyboard
        )
    else:
        await query.edit_message_caption(caption="❌ 创建支付订单失败，请重试")

async def send_download_link(user_id, product_id):
    """发送下载链接给用户"""
    session = Session()
    product = session.query(Product).get(product_id)
    
    if product:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 支付成功！\n\n" 
                 f"您的下载链接：\n`{product.download_link}`\n\n"
                 f"有效期：24小时",
            parse_mode="Markdown"
        )

def setup_handlers(application):
    """设置机器人处理器"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_purchase, pattern="^buy_"))

# Webhook处理 (Flask应用)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/plisio_webhook", methods=["POST"])
def webhook_handler():
    """处理Plisio支付回调"""
    data = request.json
    if handle_payment_webhook(data):
        # 实际项目中应使用任务队列处理
        # 这里简化处理
        session = Session()
        order = session.query(Order).get(data["id"])
        if order and order.status == "completed":
            # 发送下载链接
            send_download_link(order.user_id, order.product_id)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

def main():
    """启动机器人"""
    application = Application.builder().token(Config.TOKEN).build()
    setup_handlers(application)
    
    # 启动轮询 (适合开发)
    application.run_polling()

if __name__ == "__main__":
    # Railway会运行这个文件作为web服务
    # 实际运行时通过Procfile启动worker
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
