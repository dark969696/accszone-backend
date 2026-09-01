import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# السماح للواجهة بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # السماح لأي موقع بالاتصال (أو حط رابط موقعك ع Vercel تحديدا)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def read_root():
    return {"message": "AccsZone Backend is running successfully!"}

class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    amount: float

@app.post("/create-order")
def create_order(order: OrderRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, account_data FROM product_items WHERE product_id = %s AND is_sold = FALSE LIMIT 1;", (order.product_id,))
        item = cur.fetchone()
        
        if not item:
            raise HTTPException(status_code=400, detail="عذراً، النفاد تام من هذا المنتج حالياً!")
            
        item_id, account_data = item
        
        cur.execute("UPDATE product_items SET is_sold = TRUE WHERE id = %s;", (item_id,))
        cur.execute("INSERT INTO orders (user_id, total_amount, payment_status, order_status) VALUES (%s, %s, 'paid', 'completed') RETURNING id;", 
                    (order.user_id, order.amount))
        order_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "order_id": order_id,
            "account_details": account_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
