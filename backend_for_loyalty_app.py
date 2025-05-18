from flask import Flask, request, jsonify
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
EXCEL_FILE = 'customers_data.xlsx'
ADMIN_EMAIL = 'ghadahubjo@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # Set this in your environment

# Load the customer data
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=['name', 'phone', 'points'])
    df.to_excel(EXCEL_FILE, index=False)

def load_customers():
    return pd.read_excel(EXCEL_FILE)

def save_customers(df):
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/api/check-points', methods=['POST'])
def check_points():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    df = load_customers()
    customer = df[(df['name'] == name) & (df['phone'] == phone)]
    if not customer.empty:
        points = int(customer.iloc[0]['points'])
        return jsonify({'points': points})
    return jsonify({'error': 'Customer not found'}), 404

@app.route('/api/redeem-points', methods=['POST'])
def redeem_points():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    redeem_amount = int(data.get('redeemAmount'))
    df = load_customers()
    customer_index = df[(df['name'] == name) & (df['phone'] == phone)].index
    if not customer_index.empty:
        current_points = int(df.loc[customer_index[0], 'points'])
        if current_points >= redeem_amount:
            df.loc[customer_index[0], 'points'] = current_points - redeem_amount
            save_customers(df)
            send_redeem_notification(name, phone, redeem_amount)
            return jsonify({'success': True})
    return jsonify({'error': 'Not enough points or customer not found'}), 400

def send_redeem_notification(name, phone, amount):
    msg = MIMEMultipart()
    msg['From'] = ADMIN_EMAIL
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = f'🔔 طلب استرداد نقاط - {name}'
    body = f'📝 عميلنا العزيز {name} برقم الهاتف {phone} طلب استرداد {amount} نقطة.'
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
            server.sendmail(ADMIN_EMAIL, ADMIN_EMAIL, msg.as_string())
            print(f'📧 تم إرسال إشعار إلى {ADMIN_EMAIL}')
    except Exception as e:
        print(f'❌ فشل في إرسال البريد: {e}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
