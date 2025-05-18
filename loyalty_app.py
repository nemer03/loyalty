import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import pandas as pd
import os
import sys

# ملف البيانات
DATA_FILE = "customers_data.xlsx"

# إنشاء ملف البيانات إذا لم يكن موجودًا
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["name", "phone", "points"]).to_excel(DATA_FILE, index=False)

# تحميل البيانات من ملف Excel
def load_customers():
    try:
        return pd.read_excel(DATA_FILE).to_dict(orient="records")
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

# حفظ البيانات إلى ملف Excel
def save_customers(customers):
    pd.DataFrame(customers).to_excel(DATA_FILE, index=False)

# تحديث الجدول
def refresh_table():
    for row in table.get_children():
        table.delete(row)
    for customer in customers:
        table.insert("", "end", values=(customer["name"], customer["phone"], customer["points"]))

# إضافة أو تحديث عميل جديد
def add_or_update_customer():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    amount = amount_entry.get().strip()
    if not name or not phone or not amount.isdigit():
        messagebox.showwarning("تحذير", "يرجى إدخال جميع البيانات بشكل صحيح")
        return
    points = int(amount) // 10
    existing = next((c for c in customers if c["phone"] == phone), None)
    if existing:
        existing["points"] += points
    else:
        customers.append({"name": name, "phone": phone, "points": points})
    save_customers(customers)
    refresh_table()
    clear_inputs()
    messagebox.showinfo("نجاح", f"تم إضافة/تحديث العميل {name} بنجاح!")

# تعديل بيانات العميل
def edit_customer():
    try:
        selected_item = table.selection()[0]
        values = table.item(selected_item, "values")
        name_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        name_entry.insert(0, values[0])
        phone_entry.insert(0, values[1])
        amount_entry.insert(0, str(values[2]))
        customers[:] = [c for c in customers if c["phone"] != values[1]]
        refresh_table()
    except IndexError:
        messagebox.showwarning("تحذير", "يرجى اختيار عميل أولاً")

# حذف العميل
def delete_customer():
    try:
        selected_item = table.selection()[0]
        values = table.item(selected_item, "values")
        # حذف العميل من القائمة
        customers[:] = [c for c in customers if c["phone"] != values[1]]
        # حفظ البيانات وتحديث الجدول
        save_customers(customers)
        refresh_table()
        messagebox.showinfo("نجاح", "تم حذف العميل بنجاح!")
    except IndexError:
        messagebox.showwarning("تحذير", "يرجى اختيار عميل أولاً")

# مسح المدخلات
def clear_inputs():
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

# فتح واتساب برسالة جاهزة
def open_whatsapp(name, phone, points):
    message = f"عميلنا العزيز {name} 💙\nشكراً لك لولائك وطلبك من ghada hub 🌟\nرصيد نقاطك الحالي هو {points} نقطة.\n💥 استمر في الطلب لربح المزيد من النقاط واستبدالها بخصومات وكوبونات وجوائز! 💥"
    url = f"https://wa.me/{phone}?text={message}"
    webbrowser.open(url)

# إنشاء واجهة التطبيق
app = tk.Tk()
app.title("Ghada Hub - Loyalty Points")
app.geometry("1200x800")
app.configure(bg="#f4f8fb")

# إدخال بيانات العميل
tk.Label(app, text="اسم العميل:", bg="#f4f8fb", font=("Arial", 14)).pack(pady=10)
name_entry = tk.Entry(app, font=("Arial", 14), width=30)
name_entry.pack(pady=5)

tk.Label(app, text="رقم الهاتف:", bg="#f4f8fb", font=("Arial", 14)).pack(pady=10)
phone_entry = tk.Entry(app, font=("Arial", 14), width=30)
phone_entry.pack(pady=5)

tk.Label(app, text="قيمة الفاتورة:", bg="#f4f8fb", font=("Arial", 14)).pack(pady=10)
amount_entry = tk.Entry(app, font=("Arial", 14), width=30)
amount_entry.pack(pady=5)

# أزرار التحكم
button_frame = tk.Frame(app, bg="#f4f8fb")
button_frame.pack(pady=20)

add_button = tk.Button(button_frame, text="إضافة/تحديث عميل", font=("Arial", 14), bg="#0a74da", fg="white", command=add_or_update_customer)
add_button.pack(side=tk.LEFT, padx=10)

edit_button = tk.Button(button_frame, text="تعديل عميل", font=("Arial", 14), bg="#ffa500", fg="white", command=edit_customer)
edit_button.pack(side=tk.LEFT, padx=10)

delete_button = tk.Button(button_frame, text="حذف عميل", font=("Arial", 14), bg="#d9534f", fg="white", command=delete_customer)
delete_button.pack(side=tk.LEFT, padx=10)

# جدول العملاء
table_frame = tk.Frame(app)
table_frame.pack(pady=20)

columns = ("name", "phone", "points")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
table.heading("name", text="اسم العميل")
table.heading("phone", text="رقم الهاتف")
table.heading("points", text="رصيد النقاط")
table.pack(side=tk.LEFT)

# شريط التمرير
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
table.configure(yscroll=scrollbar.set)

# حدث النقر المزدوج

table.bind("<Double-1>", lambda event: open_whatsapp(*table.item(table.selection()[0], "values")))

# تحميل البيانات وتحديث الجدول
customers = load_customers()
refresh_table()

app.mainloop()
