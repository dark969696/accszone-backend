import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# السماح للواجهة بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# إنشاء الجداول أوتوماتيك عند تشغيل السيرفر
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_items (
            id SERIAL PRIMARY KEY,
            product_id INT NOT NULL,
            account_data TEXT NOT NULL,
            is_sold BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            total_amount FLOAT NOT NULL,
            payment_status VARCHAR(50),
            order_status VARCHAR(50)
        );
    """)
    # إضافة حساب تجريبي لو الجدول فاضي أول مرة
    cur.execute("SELECT COUNT(*) FROM product_items;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO product_items (product_id, account_data, is_sold) VALUES (1, 'USA_FB_Email: user@test.com | Pass: 123456 | 2FA: ABCXYZ', FALSE);")
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "AccsZone Backend is running and DB is initialized!"}

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

class AddAccountRequest(BaseModel):
    product_id: int
    account_data: str
    admin_secret: str

@app.post("/add-account")
def add_account(item: AddAccountRequest):
    if item.admin_secret != "my_secret_admin_123":
        raise HTTPException(status_code=403, detail="كلمة السر غير صحيحة!")
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO product_items (product_id, account_data, is_sold) VALUES (%s, %s, FALSE);",
            (item.product_id, item.account_data)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "تم إضافة الحساب بنجاح للمخزون!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
