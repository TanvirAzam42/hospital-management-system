# ==========================================================
# MERGED FINAL main.py
# Smart Hospital Management System
# Premium UI + Patients CRUD + Doctor Dropdown Appointments
# Staff Management Pro + Billing PDF + Secure Login
# ==========================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas

# ==========================================================
# DATABASE
# ==========================================================
conn = sqlite3.connect("hospital.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    gender TEXT,
    phone TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS doctors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    doctor_name TEXT,
    date TEXT,
    time TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    consultation REAL,
    medicine REAL,
    room REAL,
    total REAL
)
""")

conn.commit()

# first admin
cur.execute("SELECT * FROM users WHERE role='Admin'")
if cur.fetchone() is None:
    cur.execute("""
    INSERT INTO users(username,password,role)
    VALUES(?,?,?)
    """,(
        "admin",
        hashlib.sha256("admin123".encode()).hexdigest(),
        "Admin"
    ))
    conn.commit()

# ==========================================================
# HELPERS
# ==========================================================
def hash_password(txt):
    return hashlib.sha256(txt.encode()).hexdigest()

current_user = ""
current_role = ""

# ==========================================================
# ROOT
# ==========================================================
root = tk.Tk()
root.title("🏥 Smart Hospital Management System")
root.geometry("1280x730")
root.config(bg="#0b1120")
root.withdraw()

# ==========================================================
# STYLE
# ==========================================================
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#162033",
    foreground="white",
    fieldbackground="#162033",
    rowheight=28,
    font=("Segoe UI",10)
)

style.configure(
    "Treeview.Heading",
    background="#2563eb",
    foreground="white",
    font=("Segoe UI",10,"bold")
)

# ==========================================================
# LAYOUT
# ==========================================================
sidebar = tk.Frame(root,bg="#111827",width=230)
sidebar.pack(side="left",fill="y")

tk.Label(
    sidebar,
    text="🏥 Hospital ERP",
    bg="#111827",
    fg="white",
    font=("Segoe UI",18,"bold")
).pack(pady=20)

main = tk.Frame(root,bg="#0b1120")
main.pack(fill="both",expand=True)

header = tk.Label(
    main,
    text="Dashboard",
    bg="#0b1120",
    fg="white",
    font=("Segoe UI",22,"bold")
)
header.pack(pady=15)

content = tk.Frame(main,bg="#0b1120")
content.pack(fill="both",expand=True)

# ==========================================================
# COMMON
# ==========================================================
def clear_content():
    for w in content.winfo_children():
        w.destroy()

def clear_sidebar():
    for w in sidebar.winfo_children()[1:]:
        w.destroy()

# ==========================================================
# DASHBOARD
# ==========================================================
def show_dashboard():
    clear_content()
    header.config(text="Dashboard")

    data = [
        ("👤 Patients","patients"),
        ("👨‍⚕️ Doctors","doctors"),
        ("📅 Appointments","appointments"),
        ("💵 Bills","bills")
    ]

    for i,(txt,table) in enumerate(data):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]

        card = tk.Frame(content,bg="#162033",width=240,height=140)
        card.grid(row=0,column=i,padx=15,pady=50)
        card.grid_propagate(False)

        tk.Label(card,text=txt,bg="#162033",fg="white",
                 font=("Segoe UI",14,"bold")).pack(pady=15)

        tk.Label(card,text=count,bg="#162033",fg="#38bdf8",
                 font=("Segoe UI",28,"bold")).pack()

# ==========================================================
# PATIENTS CRUD
# ==========================================================
def show_patients():
    clear_content()
    header.config(text="Patients Management")

    form = tk.Frame(content,bg="#0b1120")
    form.pack(pady=10)

    labels = ["Name","Age","Gender","Phone"]
    entries=[]

    for i,l in enumerate(labels):
        tk.Label(form,text=l,bg="#0b1120",fg="white").grid(row=i,column=0,padx=8,pady=5)
        e=tk.Entry(form,width=28)
        e.grid(row=i,column=1,pady=5)
        entries.append(e)

    search_frame = tk.Frame(content,bg="#0b1120")
    search_frame.pack(pady=5)

    tk.Label(search_frame,text="Search:",bg="#0b1120",fg="white").pack(side="left")
    search_box = tk.Entry(search_frame,width=26)
    search_box.pack(side="left",padx=6)

    tree = ttk.Treeview(
        content,
        columns=("ID","Name","Age","Gender","Phone"),
        show="headings",
        height=12
    )

    for c in ("ID","Name","Age","Gender","Phone"):
        tree.heading(c,text=c,anchor="center")
        tree.column(c,width=160,anchor="center")

    tree.pack(pady=12)

    def clear_entries():
        for e in entries:
            e.delete(0, tk.END)

    def load(rows=None):
        for item in tree.get_children():
            tree.delete(item)

        if rows is None:
            cur.execute("SELECT * FROM patients")
            rows = cur.fetchall()

        for row in rows:
            tree.insert("", "end", values=row)

    load()

    def add_patient():
        vals = [e.get().strip() for e in entries]
        if "" in vals:
            messagebox.showerror("Error","All fields required")
            return

        cur.execute("""
        INSERT INTO patients(name,age,gender,phone)
        VALUES(?,?,?,?)
        """, vals)

        conn.commit()
        clear_entries()
        load()

    def update_patient():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error","Select patient")
            return

        row_id = tree.item(sel[0])["values"][0]
        vals = [e.get().strip() for e in entries]

        cur.execute("""
        UPDATE patients
        SET name=?, age=?, gender=?, phone=?
        WHERE id=?
        """, (*vals,row_id))

        conn.commit()
        clear_entries()
        load()

    def delete_patient():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error","Select patient")
            return

        row_id = tree.item(sel[0])["values"][0]

        cur.execute("DELETE FROM patients WHERE id=?", (row_id,))
        conn.commit()
        clear_entries()
        load()

    def search_patient():
        key = search_box.get().strip()

        cur.execute("""
        SELECT * FROM patients
        WHERE name LIKE ? OR phone LIKE ?
        """,(f"%{key}%",f"%{key}%"))

        load(cur.fetchall())

    def select_row(event):
        sel = tree.selection()
        if not sel:
            return

        row = tree.item(sel[0])["values"]
        clear_entries()

        for i in range(4):
            entries[i].insert(0,row[i+1])

    tree.bind("<<TreeviewSelect>>", select_row)

    btn = tk.Frame(content,bg="#0b1120")
    btn.pack(pady=8)

    tk.Button(btn,text="Add",bg="#16a34a",fg="white",
              width=14,command=add_patient).grid(row=0,column=0,padx=5)

    tk.Button(btn,text="Update",bg="#2563eb",fg="white",
              width=14,command=update_patient).grid(row=0,column=1,padx=5)

    tk.Button(btn,text="Delete",bg="#dc2626",fg="white",
              width=14,command=delete_patient).grid(row=0,column=2,padx=5)

    tk.Button(btn,text="Search",bg="#f59e0b",fg="white",
              width=14,command=search_patient).grid(row=0,column=3,padx=5)

    tk.Button(btn,text="Refresh",bg="#6b7280",fg="white",
              width=14,command=load).grid(row=0,column=4,padx=5)

# ==========================================================
# DOCTORS
# ==========================================================
def show_doctors():
    clear_content()
    header.config(text="Doctors")

    form = tk.Frame(content,bg="#0b1120")
    form.pack(pady=10)

    tk.Label(form,text="Name",bg="#0b1120",fg="white").grid(row=0,column=0,pady=5)
    tk.Label(form,text="Specialization",bg="#0b1120",fg="white").grid(row=1,column=0,pady=5)

    name = tk.Entry(form,width=28)
    spec = tk.Entry(form,width=28)

    name.grid(row=0,column=1,pady=5)
    spec.grid(row=1,column=1,pady=5)

    def add_doctor():
        cur.execute("""
        INSERT INTO doctors(name,specialization)
        VALUES(?,?)
        """,(name.get(),spec.get()))
        conn.commit()
        show_doctors()

    tk.Button(form,text="Add Doctor",bg="#2563eb",fg="white",
              width=18,command=add_doctor).grid(row=3,column=1,pady=10)

    tree = ttk.Treeview(
        content,
        columns=("ID","Name","Specialization"),
        show="headings",
        height=12
    )

    for c in ("ID","Name","Specialization"):
        tree.heading(c,text=c,anchor="center")
        tree.column(c,width=220,anchor="center")

    tree.pack(pady=15)

    cur.execute("SELECT * FROM doctors")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)

# ==========================================================
# APPOINTMENTS WITH DOCTOR DROPDOWN
# ==========================================================
def show_appointments():
    clear_content()
    header.config(text="Appointments")

    form = tk.Frame(content,bg="#0b1120")
    form.pack(pady=10)

    tk.Label(form,text="Patient Name",bg="#0b1120",fg="white").grid(row=0,column=0,pady=5)
    patient = tk.Entry(form,width=28)
    patient.grid(row=0,column=1,pady=5)

    tk.Label(form,text="Doctor Name",bg="#0b1120",fg="white").grid(row=1,column=0,pady=5)

    cur.execute("SELECT name FROM doctors")
    doctors = [r[0] for r in cur.fetchall()]

    doctor = ttk.Combobox(
        form,
        values=doctors,
        state="readonly",
        width=25
    )
    doctor.grid(row=1,column=1,pady=5)

    if doctors:
        doctor.current(0)

    tk.Label(form,text="Date",bg="#0b1120",fg="white").grid(row=2,column=0,pady=5)
    tk.Label(form,text="Time",bg="#0b1120",fg="white").grid(row=3,column=0,pady=5)

    date = tk.Entry(form,width=28)
    time = tk.Entry(form,width=28)

    date.grid(row=2,column=1,pady=5)
    time.grid(row=3,column=1,pady=5)

    def add_app():
        if patient.get().strip() == "":
            messagebox.showerror("Error","Enter patient name")
            return

        cur.execute("""
        INSERT INTO appointments(patient_name,doctor_name,date,time)
        VALUES(?,?,?,?)
        """,(
            patient.get(),
            doctor.get(),
            date.get(),
            time.get()
        ))
        conn.commit()
        show_appointments()

    tk.Button(form,text="Book Appointment",
              bg="#2563eb",fg="white",
              width=18,command=add_app).grid(row=5,column=1,pady=10)

    tree = ttk.Treeview(
        content,
        columns=("ID","Patient","Doctor","Date","Time"),
        show="headings",
        height=12
    )

    for c in ("ID","Patient","Doctor","Date","Time"):
        tree.heading(c,text=c,anchor="center")
        tree.column(c,width=170,anchor="center")

    tree.pack(pady=15)

    cur.execute("SELECT * FROM appointments")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)

# ==========================================================
# BILLING
# ==========================================================
def show_billing():
    clear_content()
    header.config(text="Billing")

    form = tk.Frame(content,bg="#0b1120")
    form.pack(pady=20)

    labels = ["Patient Name","Consultation","Medicine","Room"]
    entries=[]

    for i,l in enumerate(labels):
        tk.Label(form,text=l,bg="#0b1120",fg="white").grid(row=i,column=0,pady=5)
        e=tk.Entry(form,width=28)
        e.grid(row=i,column=1,pady=5)
        entries.append(e)

    def generate():
        try:
            p = entries[0].get()
            c = float(entries[1].get())
            m = float(entries[2].get())
            r = float(entries[3].get())
            total = c+m+r

            cur.execute("""
            INSERT INTO bills(patient_name,consultation,medicine,room,total)
            VALUES(?,?,?,?,?)
            """,(p,c,m,r,total))
            conn.commit()

            file = f"Bill_{p}.pdf"
            pdf = canvas.Canvas(file)

            pdf.setFont("Helvetica-Bold",18)
            pdf.drawString(180,800,"Hospital Receipt")

            pdf.setFont("Helvetica",12)

            y=750
            for line in [
                f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                "",
                f"Patient: {p}",
                f"Consultation: ₹ {c}",
                f"Medicine: ₹ {m}",
                f"Room: ₹ {r}",
                "-------------------",
                f"Total: ₹ {total}"
            ]:
                pdf.drawString(80,y,line)
                y-=25

            pdf.save()
            messagebox.showinfo("Success",f"PDF Saved: {file}")

        except:
            messagebox.showerror("Error","Invalid Data")

    tk.Button(form,text="Generate Bill",
              bg="#16a34a",fg="white",
              width=20,command=generate).grid(row=5,column=1,pady=15)

# ==========================================================
# STAFF MANAGEMENT PRO
# ==========================================================

def show_staff():
    clear_content()
    header.config(text="Staff Management")

    # -------------------------------------------------
    # FORM
    # -------------------------------------------------
    form = tk.Frame(content, bg="#0b1120")
    form.pack(pady=10)

    tk.Label(form, text="Username", bg="#0b1120", fg="white").grid(row=0,column=0,padx=8,pady=5)
    tk.Label(form, text="Password", bg="#0b1120", fg="white").grid(row=1,column=0,padx=8,pady=5)
    tk.Label(form, text="Role", bg="#0b1120", fg="white").grid(row=2,column=0,padx=8,pady=5)

    username = tk.Entry(form, width=26)
    password = tk.Entry(form, width=26)

    username.grid(row=0,column=1,pady=5)
    password.grid(row=1,column=1,pady=5)

    role_box = ttk.Combobox(
        form,
        values=["Admin", "Receptionist"],
        state="readonly",
        width=23
    )
    role_box.grid(row=2,column=1,pady=5)
    role_box.current(1)

    # -------------------------------------------------
    # TABLE
    # -------------------------------------------------
    tree = ttk.Treeview(
        content,
        columns=("ID","Username","Role"),
        show="headings",
        height=12
    )

    for c in ("ID","Username","Role"):
        tree.heading(c,text=c,anchor="center")
        tree.column(c,width=220,anchor="center")

    tree.pack(pady=15)

    def load():
        for i in tree.get_children():
            tree.delete(i)

        cur.execute("SELECT id,username,role FROM users")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)

    load()

    # -------------------------------------------------
    # ADD STAFF
    # -------------------------------------------------
    def add_staff():
        u = username.get().strip()
        p = password.get().strip()
        r = role_box.get()

        if u == "" or p == "":
            messagebox.showerror("Error", "All fields required")
            return

        try:
            cur.execute("""
            INSERT INTO users(username,password,role)
            VALUES(?,?,?)
            """, (u, hash_password(p), r))

            conn.commit()
            load()

            username.delete(0, tk.END)
            password.delete(0, tk.END)

            messagebox.showinfo("Success", "Staff Added")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------
    def delete_user():
        sel = tree.selection()

        if not sel:
            messagebox.showerror("Error", "Select user")
            return

        row = tree.item(sel[0])["values"]
        user_id = row[0]
        uname = row[1]

        if uname.lower() == "admin":
            messagebox.showerror("Error", "Default admin cannot be deleted")
            return

        cur.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        load()

    # -------------------------------------------------
    # CHANGE ROLE
    # -------------------------------------------------
    def change_role():
        sel = tree.selection()

        if not sel:
            messagebox.showerror("Error", "Select user")
            return

        row = tree.item(sel[0])["values"]
        user_id = row[0]
        uname = row[1]
        old_role = row[2]

        if uname.lower() == "admin":
            messagebox.showerror("Error", "Admin role cannot change")
            return

        new_role = "Admin" if old_role == "Receptionist" else "Receptionist"

        cur.execute("""
        UPDATE users
        SET role=?
        WHERE id=?
        """, (new_role, user_id))

        conn.commit()
        load()

    # -------------------------------------------------
    # RESET PASSWORD
    # -------------------------------------------------
    def reset_password():
        sel = tree.selection()

        if not sel:
            messagebox.showerror("Error", "Select user")
            return

        row = tree.item(sel[0])["values"]
        user_id = row[0]

        cur.execute("""
        UPDATE users
        SET password=?
        WHERE id=?
        """, (hash_password("1234"), user_id))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Password reset to: 1234"
        )

    # -------------------------------------------------
    # BUTTONS
    # -------------------------------------------------
    btn = tk.Frame(content, bg="#0b1120")
    btn.pack(pady=10)

    tk.Button(btn,text="Add Staff",bg="#16a34a",fg="white",
              width=16,command=add_staff).grid(row=0,column=0,padx=5)

    tk.Button(btn,text="Delete User",bg="#dc2626",fg="white",
              width=16,command=delete_user).grid(row=0,column=1,padx=5)

    tk.Button(btn,text="Change Role",bg="#2563eb",fg="white",
              width=16,command=change_role).grid(row=0,column=2,padx=5)

    tk.Button(btn,text="Reset Password",bg="#f59e0b",fg="white",
              width=16,command=reset_password).grid(row=0,column=3,padx=5)
# ==========================================================
# SIDEBAR
# ==========================================================
def build_sidebar():
    clear_sidebar()

    btns = [
        ("Dashboard",show_dashboard),
        ("Patients",show_patients),
        ("Appointments",show_appointments),
        ("Billing",show_billing)
    ]

    if current_role == "Admin":
        btns.insert(2,("Doctors",show_doctors))
        btns.append(("Staff Management",show_staff))

    for txt,cmd in btns:
        tk.Button(
            sidebar,text=txt,
            bg="#1f2937",fg="white",
            width=22,pady=8,
            relief="flat",
            command=cmd
        ).pack(pady=8)

    tk.Button(
        sidebar,text="Logout",
        bg="#dc2626",fg="white",
        width=22,pady=8,
        relief="flat",
        command=logout
    ).pack(pady=20)

# ==========================================================
# LOGIN
# ==========================================================
def open_login():
    login = tk.Toplevel()
    login.title("Secure Login")
    login.geometry("430x540")
    login.config(bg="#0b1120")
    login.resizable(False,False)

    card = tk.Frame(login,bg="#162033")
    card.place(relx=0.5,rely=0.5,anchor="center",width=340,height=670)

    tk.Label(card,text="🏥",bg="#162033",fg="#38bdf8",
             font=("Segoe UI Emoji",26)).pack(pady=(18,2))

    tk.Label(card,text="Hospital Login",bg="#162033",fg="white",
             font=("Segoe UI",22,"bold")).pack()

    tk.Label(card,text="Secure Access Portal",
             bg="#162033",fg="#94a3b8",
             font=("Segoe UI",9)).pack(pady=(0,18))

    tk.Label(card,text="Username",bg="#162033",fg="white").pack()

    uf = tk.Frame(card,bg="#162033")
    uf.pack(pady=(5,12))

    user = tk.Entry(uf,width=24,font=("Segoe UI",11),relief="flat")
    user.grid(row=0,column=0,ipady=6)

    tk.Label(uf,text="👤",bg="#2563eb",fg="white",
             width=3).grid(row=0,column=1,padx=(3,0),sticky="ns")

    tk.Label(card,text="Password",bg="#162033",fg="white").pack()

    pf = tk.Frame(card,bg="#162033")
    pf.pack(pady=(5,12))

    pas = tk.Entry(pf,show="*",width=24,font=("Segoe UI",11),relief="flat")
    pas.grid(row=0,column=0,ipady=6)

    visible = False

    def toggle():
        nonlocal visible
        visible = not visible
        pas.config(show="" if visible else "*")
        eye.config(text="🙈" if visible else "👁")

    eye = tk.Button(
        pf,text="👁",
        bg="#2563eb",fg="white",
        width=3,relief="flat",
        command=toggle
    )
    eye.grid(row=0,column=1,padx=(3,0),sticky="ns")

    tk.Label(card,text="Login As",bg="#162033",fg="white").pack()

    role = ttk.Combobox(
        card,
        values=["Admin","Receptionist"],
        state="readonly",
        width=26
    )
    role.pack(pady=(6,18))
    role.current(1)

    def register():
        try:
            u = user.get().strip()
            p = pas.get().strip()

            if u == "" or p == "":
                messagebox.showerror("Error","Username and Password required")
                return

            if len(p) < 4:
                messagebox.showerror("Error","Password too short")
                return

            cur.execute("""
            INSERT INTO users(username,password,role)
            VALUES(?,?,?)
            """,(u,hash_password(p),"Receptionist"))

            conn.commit()
            messagebox.showinfo("Success","Receptionist account created")

        except Exception as e:
            messagebox.showerror("Error",str(e))

    def login_user():
        global current_user,current_role

        cur.execute("""
        SELECT * FROM users
        WHERE username=? AND password=? AND role=?
        """,(
            user.get(),
            hash_password(pas.get()),
            role.get()
        ))

        row = cur.fetchone()

        if row:
            current_user = user.get()
            current_role = role.get()

            login.destroy()
            root.deiconify()
            build_sidebar()
            show_dashboard()
        else:
            messagebox.showerror("Error","Invalid Credentials")

    tk.Button(card,text="Login",
              bg="#2563eb",fg="white",
              width=26,
              font=("Segoe UI",10,"bold"),
              relief="flat",
              command=login_user).pack(pady=(5,12))

    tk.Button(card,text="Create Receptionist Account",
              bg="#162033",fg="#22c55e",
              relief="flat",bd=0,
              font=("Segoe UI",9,"underline"),
              command=register).pack(pady=(0,8))

    tk.Button(card,text="Forgot Password?",
              bg="#162033",fg="#60a5fa",
              relief="flat",bd=0,
              font=("Segoe UI",9,"underline"),
              command=lambda: messagebox.showinfo(
                  "Forgot Password",
                  "Please contact Admin to reset password."
              )).pack(pady=(0,10))

    tk.Label(card,text="Authorized Staff Access Only",
             bg="#162033",fg="#64748b",
             font=("Segoe UI",8)).pack(pady=(5,10))

    login.protocol("WM_DELETE_WINDOW", root.destroy)

# ==========================================================
# LOGOUT
# ==========================================================
def logout():
    root.withdraw()
    open_login()

# ==========================================================
# START
# ==========================================================
open_login()
root.mainloop()