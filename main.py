import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()

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
            txid VARCHAR(255),
            payment_status VARCHAR(50) DEFAULT 'pending',
            order_status VARCHAR(50) DEFAULT 'completed'
        );
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            balance FLOAT DEFAULT 0.0
        );
    """)
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS balance FLOAT DEFAULT 0.0;")
        cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS txid VARCHAR(255);")
        cur.execute("ALTER TABLE orders ALTER COLUMN payment_status SET DEFAULT 'pending';")
        conn.commit()
    except Exception:
        conn.rollback()

    cur.execute("SELECT COUNT(*) FROM product_items;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO product_items (product_id, account_data, is_sold) VALUES (1, 'Grindr_Account_Demo: user@test.com | Pass: 123456', FALSE);")
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "AccsZone Backend is running with Admin Approval System for Deposits!"}

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class DepositRequest(BaseModel):
    user_id: int
    amount: float
    txid: str

class BalanceOrderRequest(BaseModel):
    user_id: int
    product_id: int
    amount: float

class ApproveDepositRequest(BaseModel):
    order_id: int
    admin_secret: str

class AddAccountRequest(BaseModel):
    product_id: int
    account_data: str
    admin_secret: str

class DeleteAccountRequest(BaseModel):
    account_id: int
    admin_secret: str

@app.post("/signup")
def signup_user(user: SignupRequest):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, user.email):
        raise HTTPException(status_code=400, detail="صيغة البريد الإلكتروني غير صحيحة!")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="كلمة المرور يجب ألا تقل عن 8 خانات!")
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s;", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل!")
            
        cur.execute(
            "INSERT INTO users (full_name, email, password, balance) VALUES (%s, %s, %s, 0.0) RETURNING id, balance;",
            (user.full_name, user.email, user.password)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "تم إنشاء الحساب بنجاح!", "user": {"id": row[0], "full_name": user.full_name, "email": user.email, "balance": row[1]}}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login_user(user: LoginRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, full_name, email, balance FROM users WHERE email = %s AND password = %s;", (user.email, user.password))
        db_user = cur.fetchone()
        cur.close()
        conn.close()
        if not db_user:
            raise HTTPException(status_code=400, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة!")
        return {"status": "success", "message": "تم تسجيل الدخول بنجاح!", "user": {"id": db_user[0], "full_name": db_user[1], "email": db_user[2], "balance": db_user[3]}}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 1. طلب إيداع جديد (يُسجل بحالة معلقة pending وبدون إضافة رصيد فوراً)
@app.post("/deposit")
def deposit_balance(req: DepositRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM orders WHERE txid = %s;", (req.txid,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="رقم المعاملة (TXID) مستخدم من قبل!")

        cur.execute("""
            INSERT INTO orders (user_id, total_amount, txid, payment_status, order_status) 
            VALUES (%s, %s, %s, 'pending', 'deposit_request') RETURNING id;
        """, (req.user_id, req.amount, req.txid))
        
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "تم إرسال طلب الشحن بنجاح وهو قيد المراجعة من الإدارة وسيتم إضافة الرصيد فور التحقق!"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. جلب الطلبات المعلقة للإيداع للأدمن
@app.get("/get-pending-deposits")
def get_pending_deposits(admin_secret: str):
    if admin_secret != "my_secret_admin_123":
        raise HTTPException(status_code=403, detail="كلمة السر غير صحيحة!")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT orders.id, users.id, users.full_name, users.email, orders.total_amount, orders.txid 
            FROM orders 
            JOIN users ON orders.user_id = users.id 
            WHERE orders.payment_status = 'pending' AND orders.order_status = 'deposit_request'
            ORDER BY orders.id DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        deposits = [{
            "order_id": r[0],
            "user_id": r[1],
            "customer_name": r[2],
            "customer_email": r[3],
            "amount": r[4],
            "txid": r[5]
        } for r in rows]
        
        return {"status": "success", "deposits": deposits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. قبول الإيداع من قبل الأدمن وإضافة الرصيد لحساب المستخدم
@app.post("/approve-deposit")
def approve_deposit(req: ApproveDepositRequest):
    if req.admin_secret != "my_secret_admin_123":
        raise HTTPException(status_code=403, detail="كلمة السر غير صحيحة!")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # جلب تفاصيل الطلب المعلق
        cur.execute("SELECT user_id, total_amount, payment_status FROM orders WHERE id = %s;", (req.order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="الطلب غير موجود!")
        
        user_id, amount, payment_status = order[0], order[1], order[2]
        if payment_status == 'approved':
            raise HTTPException(status_code=400, detail="تم اعتماد هذا الطلب مسبقاً!")

        # تحديث حالة الطلب إلى approved
        cur.execute("UPDATE orders SET payment_status = 'approved', order_status = 'completed' WHERE id = %s;", (req.order_id,))
        
        # إضافة الرصيد لحساب المستخدم
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s RETURNING balance;", (amount, user_id))
        new_balance = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": f"تم اعتماد الإيداع بنجاح وإضافة ${amount} لحساب المستخدم!"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/buy-with-balance")
def buy_with_balance(order: BalanceOrderRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM users WHERE id = %s;", (order.user_id,))
        user_row = cur.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود!")
        
        current_balance = user_row[0]
        if current_balance < order.amount:
            raise HTTPException(status_code=400, detail="رصيدك غير كافي! يرجى شحن المحفظة أولاً.")

        cur.execute("SELECT id, account_data FROM product_items WHERE product_id = %s AND is_sold = FALSE LIMIT 1;", (order.product_id,))
        item = cur.fetchone()
        if not item:
            raise HTTPException(status_code=400, detail="عذراً، نفاد المخزون لهذا المنتج حالياً!")
        
        item_id, account_data = item

        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s;", (order.amount, order.user_id))
        cur.execute("UPDATE product_items SET is_sold = TRUE WHERE id = %s;", (item_id,))

        cur.execute("""
            INSERT INTO orders (user_id, total_amount, txid, payment_status, order_status) 
            VALUES (%s, %s, 'BALANCE_PAYMENT', 'paid', 'completed') RETURNING id;
        """, (order.user_id, order.amount))
        
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "order_id": order_id,
            "account_details": account_data,
            "message": "تم الشراء بنجاح من رصيد المحفظة وتسليم الحساب!"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-stock/{product_id}")
def check_stock(product_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM product_items WHERE product_id = %s AND is_sold = FALSE;", (product_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"status": "success", "available_stock": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-account")
def add_account(item: AddAccountRequest):
    if item.admin_secret != "my_secret_admin_123":
        raise HTTPException(status_code=403, detail="كلمة السر غير صحيحة!")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO product_items (product_id, account_data, is_sold) VALUES (%s, %s, FALSE);", (item.product_id, item.account_data))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "تم إضافة الحساب بنجاح للمخزون!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-all-accounts")
def get_all_accounts():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, product_id, account_data, is_sold FROM product_items ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        accounts = [{"id": r[0], "product_id": r[1], "account_data": r[2], "is_sold": r[3]} for r in rows]
        return {"status": "success", "accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-account")
def delete_account(item: DeleteAccountRequest):
    if item.admin_secret != "my_secret_admin_123":
        raise HTTPException(status_code=403, detail="كلمة السر غير صحيحة!")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM product_items WHERE id = %s;", (item.account_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "تم حذف الحساب بنجاح!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
