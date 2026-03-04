import streamlit as st
import mysql.connector
import os
import pandas as pd
import qrcode
from io import BytesIO
import time
# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="E-Commerce System", layout="wide")

# ---------------- CLEAN PROFESSIONAL LIGHT UI ----------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 20px !important;
}
/* Smooth fade animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Smooth Page Load */
@keyframes fadeInPage {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.main {
    animation: fadeInPage 0.8s ease-in-out;
}
.product-card {
    position: relative;
    background: #0f172a;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    height: 520px;              /* FIXED HEIGHT */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease-in-out;
}

/* Hover Effect */
.product-card:hover {
    transform: translateY(-8px) ;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.2);

}

/* Discount Badge */
.discount-badge {
    position: absolute;
    top: 12px;
    right:12px;   
    background: red;
    color: white;
    padding: 5px 10px;
    font-size: 15px;
    border-radius: 6px;
    font-weight: bold;
    z-index: 999;
}
/* Image Styling */
.product-card img {
    width: 100%;
    height: 220px;
    object-fit: cover;   /* IMPORTANT */
    border-radius: 10px;
}

/* Product Title */
.product-title {
    font-size: 18px;
    font-weight: bold;
    margin-top: 10px;
}

.product-price {
    font-size: 26px;      /* Increase size */
    font-weight: 700;     /* Bold */
    color: #27ae60;       /* Nice green */
    margin-top: 8px;
}

/* Badge */
.badge {
    position: absolute;
    background: red;
    color: white;
    padding: 5px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    top: 10px;
    left: 10px;
    z-index:999;
}

.card-container {
    position: relative;
}


/* Star Rating */
.star {
    color: #facc15;
    font-size: 18px;

}
/* ---------------- CART PAGE STYLING ---------------- */

.cart-name {
    font-size: 22px;
    font-weight: 700;
}

.cart-price {
    font-size: 22px;
    font-weight: 600;
    color: #10b981;
}

.cart-qty {
    font-size: 20px;
}

.cart-total {
    font-size: 24px;
    font-weight: bold;
    color: #ff4b4b;
}
/* Sidebar radio label (Menu Title) */
section[data-testid="stSidebar"] .stRadio > label {
    font-size: 20px !important;
    font-weight: bold;
}

/* Sidebar radio options */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    font-size: 22px !important;
    padding: 8px 0px !important;
}

/* Optional: Add hover effect */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    color: #ff4b4b !important;
    transform: translateX(5px);
    transition: 0.2s;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
    background-color: #ff4b4b;
    color: white !important;
    padding: 8px;
    border-radius: 8px;

}
/* Make input boxes bigger */
div[data-baseweb="input"] input {
    font-size: 20px !important;
    padding: 12px !important;
    height: 55px !important;
    border-radius: 10px !important;
}

/* Label text bigger */
label {
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* Increase button size */
div.stButton > button {
    width: 100%;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 10px;
}

</style>


""", unsafe_allow_html=True)
st.markdown("""
<style>

/* Normal */
div[data-baseweb="select"] > div {
    background-color: #ecfdf5 !important;
    border-radius: 12px !important;
    border: 2px solid #10b981 !important;
    transition: 0.3s ease;
}

/* Focus */
div[data-baseweb="select"] > div:focus-within {
    background-color: #d1fae5 !important;
    border: 2px solid #059669 !important;
    box-shadow: 0px 0px 15px rgba(16,185,129,0.5);
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="shopping_cart_db"
)
cursor = conn.cursor()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# ---- Payment Session Initialization ----
if "show_payment_page" not in st.session_state:
    st.session_state.show_payment_page = False

if "show_success_page" not in st.session_state:
    st.session_state.show_success_page = False

if "current_order" not in st.session_state:
    st.session_state.current_order = None

if "payment_amount" not in st.session_state:
    st.session_state.payment_amount = 0

# -------- SESSION STATE INITIALIZATION --------
if "subtotal" not in st.session_state:
    st.session_state.subtotal = 0

if "discount_percent" not in st.session_state:
    st.session_state.discount_percent = 0

if "payment_amount" not in st.session_state:
    st.session_state.payment_amount = 0

if "page" not in st.session_state:
    st.session_state.page = None

# ---------------- LOGIN ----------------
if st.session_state.user is None:

    st.title("🛒 E-Commerce System")

    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Register":
        st.subheader("Create Account")

        username = st.text_input("Username")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if not username or not email or not phone or not password or not confirm_password:
                st.error("⚠️ Please fill all fields.")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match!")
            else:
                # Check if username or email already exists
                cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    st.error("⚠️ Username or email already exists!")
                else:
                    cursor.execute(
                        "INSERT INTO users (username, email, phone, password, role) VALUES (%s,%s,%s,%s,%s)",
                        (username, email, phone, password, "user")
                    )
                    conn.commit()
                    st.success("🎉 Account Created Successfully!")
                    st.info("You can now login from the sidebar.")

    if menu == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            cursor.execute(
                "SELECT username, role FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                st.session_state.user = user[0]
                st.session_state.role = user[1]
                st.rerun()
            else:
                st.error("Invalid Credentials")

# ---------------- AFTER LOGIN ----------------

else:

    st.markdown("""
    <style>
    .stApp {
        animation: fadeIn 0.5s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)
    st.sidebar.success(f"Logged in as {st.session_state.user}")

    # ================= FAKE PAYMENT PAGE =================
    if "show_payment_page" in st.session_state and st.session_state.show_payment_page:
        st.title("💳 Secure Payment Gateway")

        st.markdown("""
        <div style="
            padding:22px;
            border-radius:18px;
            background: linear-gradient(135deg,#667eea,#764ba2);
            color:white;
            text-align:center;">
            <h2>🔒 Secure Payment</h2>
            <p>Your transaction is encrypted</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.show_payment_page:
        st.title("💳 Secure Payment Gateway")
        st.write(f"🧾 Order ID: {st.session_state.current_order}")
        st.write(f"💰 Amount: ₹{st.session_state.payment_amount}")

        card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
        expiry = st.text_input("Expiry Date", placeholder="MM/YY")
        cvv = st.text_input("CVV", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💸 Pay Now", key="pay_now_btn"):
                # Update order as paid
                cursor.execute("""
                    UPDATE orders
                    SET payment_status='Paid'
                    WHERE id=%s
                """, (st.session_state.current_order,))
                conn.commit()

                # Clear cart
                cursor.execute("DELETE FROM cart WHERE username=%s", (st.session_state.user,))
                conn.commit()

                # Hide payment page, show success page
                st.session_state.show_payment_page = False
                st.session_state.show_success_page = True

                st.rerun()  # Re-run to show success page

        with col2:
            if st.button("❌ Cancel Payment", key="cancel_payment_btn"):
                st.session_state.show_payment_page = False
                st.warning("Payment Cancelled")
                st.rerun()
    elif st.session_state.show_success_page:
        st.markdown("""
            <div style="text-align:center; padding:50px;">
                <h1 style="color:green;">✅ Payment Completed Successfully!</h1>
                <h3>Thank you for your purchase 🎉</h3>
            </div>
        """, unsafe_allow_html=True)

        st.balloons()



    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

    # ================= ADMIN PANEL =================
    if st.session_state.role.lower() == "admin":

        st.title("📊 Admin Dashboard")

        page = st.sidebar.radio("Admin Navigation", [
            "Dashboard",
            "Sales Analytics",
            "Category Management",
            "Add Product",
            "Manage Products",
            "Users",
            "Manage Coupons"# NEW
        ])

        # -------- Dashboard --------
        if page == "Dashboard":
            import streamlit as st



            col1, col2, col3, col4 = st.columns(4)

            cursor.execute("SELECT IFNULL(SUM(total_amount),0) FROM orders WHERE payment_status='Paid'")
            total_revenue = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]

            col1.metric("💰 Total Revenue", f"₹{total_revenue}")
            col2.metric("🛒 Total Orders", total_orders)
            col3.metric("👥 Customers", total_users)
            col4.metric("📦 Products", total_products)

            import pandas as pd
            import plotly.express as px

            # Monthly Revenue Trend
            cursor.execute("""
                SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                       SUM(total_amount) AS revenue
                FROM orders
                WHERE payment_status='Paid'
                GROUP BY month
                ORDER BY month
            """)

            monthly_data = cursor.fetchall()

            if monthly_data:
                df_month = pd.DataFrame(monthly_data, columns=["Month", "Revenue"])

                fig = px.line(
                    df_month,
                    x="Month",
                    y="Revenue",
                    markers=True,
                    title="📈 Monthly Revenue Trend"
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available yet.")

            cursor.execute("""
                SELECT DAYNAME(order_date) AS day,
                       COUNT(*) AS total_orders
                FROM orders
                GROUP BY day
            """)

            weekly_data = cursor.fetchall()

            if weekly_data:
                df_week = pd.DataFrame(weekly_data, columns=["Day", "Orders"])

                fig2 = px.bar(
                    df_week,
                    x="Day",
                    y="Orders",
                    title="📊 Weekly Orders Trend",
                    color="Day"
                )

                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No order data available.")

        # -------- Add Product --------
        if page == "Add Product":

            st.subheader("Add New Product")

            name = st.text_input("Product Name")
            price = st.number_input("Price", min_value=1)

            # NEW: Discount input
            discount = st.number_input("Discount %", min_value=0, max_value=100, value=0)

            cursor.execute("SELECT name FROM categories")
            categories = [row[0] for row in cursor.fetchall()]
            category = st.selectbox("Select Category", categories)

            if not os.path.exists("images"):
                os.makedirs("images")

            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
            image_path = None

            if uploaded_file:
                image_path = os.path.join("images", uploaded_file.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.image(image_path, width=150)

            if st.button("Add Product"):
                cursor.execute(
                    "INSERT INTO products (name, price, image, category, discount) VALUES (%s,%s,%s,%s,%s)",
                    (name, price, image_path, category, discount)
                )
                conn.commit()
                st.toast("🎉 Product Added!", icon="🔥")
                st.rerun()

        # -------- Manage Products --------
        if page == "Manage Products":

            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()


        # ---------------- SALES ANALYTICS ----------------
        if page == "Sales Analytics":
            st.title("📊 Sales Analytics")

            # Total Revenue
            cursor.execute("SELECT IFNULL(SUM(total_amount),0) FROM orders")
            total_revenue = cursor.fetchone()[0]

            # Total Orders
            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]

            # Total Users
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
            total_users = cursor.fetchone()[0]

            # Most Sold Product
            cursor.execute("""
                SELECT products.name, SUM(order_items.quantity) as total_qty
                FROM order_items
                JOIN products ON order_items.product_id = products.id
                GROUP BY products.name
                ORDER BY total_qty DESC
                LIMIT 1
            """)
            result = cursor.fetchone()

            most_sold = result[0] if result else "No Sales Yet"

            col1, col2 = st.columns(2)
            col1.metric("💰 Total Revenue", f"₹{total_revenue}")
            col2.metric("📦 Total Orders", total_orders)

            col3, col4 = st.columns(2)
            col3.metric("👥 Total Users", total_users)
            col4.metric("🔥 Most Sold Product", most_sold)

            import streamlit as st


            st.title("📊 Sales Analysis Graphs ")

            # Example Monthly Sales Data
            import pandas as pd
            import plotly.express as px

            st.subheader("📈 Monthly Revenue Trend")

            cursor.execute("""
                SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                       SUM(total_amount) AS revenue
                FROM orders
                WHERE payment_status='Paid'
                GROUP BY month
                ORDER BY month
            """)

            monthly_data = cursor.fetchall()

            if monthly_data:
                df = pd.DataFrame(monthly_data, columns=["Month", "Revenue"])

                fig = px.line(
                    df,
                    x="Month",
                    y="Revenue",
                    markers=True,
                    title="Monthly Revenue (Real Data)"
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available yet.")

        if page == "Manage Coupons":
            st.title("🎁 Manage Coupons")

            # -------- CREATE COUPON --------
            st.subheader("➕ Create New Coupon")

            code = st.text_input("Coupon Code").upper()
            discount = st.number_input("Discount %", min_value=1, max_value=90)

            if st.button("Create Coupon"):
                try:
                    cursor.execute("""
                        INSERT INTO coupons (code, discount_percent, active)
                        VALUES (%s, %s, TRUE)
                    """, (code.strip(), discount))
                    conn.commit()
                    st.success("Coupon Created Successfully!")
                    st.rerun()
                except:
                    st.error("Coupon already exists!")

            st.divider()

            # -------- VIEW & CONTROL COUPONS --------
            st.subheader("📋 Existing Coupons")

            cursor.execute("SELECT id, code, discount_percent, active FROM coupons")
            coupons = cursor.fetchall()

            for c in coupons:
                col1, col2, col3, col4 = st.columns(4)

                col1.write(c[1])
                col2.write(f"{c[2]}%")
                col3.write("Active" if c[3] else "Inactive")

                if col4.button("Toggle", key=f"toggle_{c[0]}"):
                    cursor.execute("UPDATE coupons SET active = NOT active WHERE id=%s", (c[0],))
                    conn.commit()
                    st.rerun()

                if st.button("Delete", key=f"delete_{c[0]}"):
                    cursor.execute("DELETE FROM coupons WHERE id=%s", (c[0],))
                    conn.commit()
                    st.rerun()
        # ---------------- CATEGORY MANAGEMENT ----------------
        if page == "Category Management":

            st.title("🗂 Category Management")

            # Add Category
            new_category = st.text_input("Add New Category")

            if st.button("Add Category"):
                try:
                    cursor.execute(
                        "INSERT INTO categories(name) VALUES(%s)",
                        (new_category,)
                    )
                    conn.commit()
                    st.success("Category Added Successfully!")
                    st.rerun()
                except:
                    st.error("Category already exists!")

            st.divider()

            # Show Existing Categories
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()

            for cat_id, cat_name in categories:
                col1, col2 = st.columns([4, 1])
                col1.write(cat_name)

                if col2.button("Delete", key=f"del_cat_{cat_id}"):
                    cursor.execute("DELETE FROM categories WHERE id=%s", (cat_id,))
                    conn.commit()
                    st.success("Category Deleted!")
                    st.rerun()
        # ---------------- MANAGE PRODUCTS ----------------
        if page == "Manage Products":

            st.title("✏ Manage Products")

            # Get products sorted by category
            cursor.execute("""
                SELECT * FROM products
                ORDER BY category ASC, name ASC
            """)
            products = cursor.fetchall()

            current_category = None

            for product in products:
                product_id = product[0]
                name = product[1]
                price = product[2]
                image = product[3]
                category = product[4]

                # Show category heading only when category changes
                if category != current_category:
                    st.markdown(f"## 📂 {category}")
                    current_category = category

                with st.expander(f"{name}"):

                    new_price = st.number_input(
                        "Change Price",
                        min_value=1,
                        value=price,
                        key=f"price_{product_id}"
                    )

                    new_discount = st.number_input(
                        "Change Discount %",
                        min_value=0,
                        max_value=100,
                        value=product[5] if product[5] else 0,
                        key=f"discount_{product_id}"
                    )

                    cursor.execute("SELECT name FROM categories")
                    categories = [row[0] for row in cursor.fetchall()]

                    new_category = st.selectbox(
                        "Change Category",
                        categories,
                        index=categories.index(category) if category in categories else 0,
                        key=f"cat_{product_id}"
                    )

                    uploaded_file = st.file_uploader(
                        "Change Image",
                        type=["jpg", "png", "jpeg"],
                        key=f"img_{product_id}"
                    )

                    new_image_path = image

                    if uploaded_file:
                        if not os.path.exists("images"):
                            os.makedirs("images")

                        new_image_path = os.path.join("images", uploaded_file.name)
                        with open(new_image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                    col1, col2 = st.columns(2)

                    if col1.button("Update", key=f"update_{product_id}"):
                        cursor.execute("""
                            UPDATE products
                            SET price=%s, category=%s, image=%s, discount=%s
                            WHERE id=%s
                        """, (new_price, new_category, new_image_path, new_discount, product_id))
                        conn.commit()
                        st.success("Product Updated!")
                        st.rerun()

                    if col2.button("Delete Product", key=f"delete_{product_id}"):
                        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
                        conn.commit()
                        st.success("Product Deleted!")
                        st.rerun()


        if page == "Users":
            st.title("👥 Manage Users")

            # Fetch all users (exclude admin if you want)
            cursor.execute("SELECT username FROM users WHERE role='user'")
            users = [row[0] for row in cursor.fetchall()]

            if not users:
                st.info("No users found")
            else:
                # Select a user
                selected_user = st.selectbox("Select a User", users)

                if selected_user:
                    st.subheader(f"Orders for {selected_user}")

                    # Fetch all orders of selected user
                    cursor.execute("""
                        SELECT id, total_amount, order_date, status, payment_status
                        FROM orders
                        WHERE username=%s
                        ORDER BY order_date DESC
                    """, (selected_user,))

                    user_orders = cursor.fetchall()

                    if not user_orders:
                        st.info(f"{selected_user} has no orders yet.")
                    else:
                        for order in user_orders:
                            order_id, total, order_date, status, payment_status = order

                            st.markdown(f"""
                            <div style="font-size:20px; line-height:1.5;">
                                <strong>🧾 Order ID:</strong> {order_id} <br>
                                <strong>📅 Date:</strong> {order_date} <br>
                                <strong>💰 Total:</strong> ₹{total} <br>
                                <strong>🚚 Status:</strong> <span style="color:#ff4b4b; font-weight:bold;">{status}</span> <br>
                                <strong>💳 Payment:</strong> <span style="color:green; font-weight:bold;">{payment_status}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            # Show order items
                            cursor.execute("""
                                SELECT p.name, p.price, oi.quantity
                                FROM order_items oi
                                JOIN products p ON oi.product_id = p.id
                                WHERE oi.order_id=%s
                            """, (order_id,))
                            items = cursor.fetchall()

                            for name, price, qty in items:
                                st.markdown(f"""
                                <div style="font-size:18px; line-height:1.5;">
                                    <strong>{name}</strong> | ₹{price} × {qty}
                                </div>
                                """, unsafe_allow_html=True)

                            # Update Order Status
                            new_status = st.selectbox(
                                f"Update Order {order_id} Status",
                                ["Pending", "Packed", "Shipped", "Out for Delivery", "Delivered"],
                                index=["Pending", "Packed", "Shipped", "Out for Delivery", "Delivered"].index(status),
                                key=f"status_{selected_user}_{order_id}"
                            )

                            if st.button(f"Update Status {order_id}", key=f"update_{selected_user}_{order_id}"):
                                cursor.execute(
                                    "UPDATE orders SET status=%s WHERE id=%s",
                                    (new_status, order_id)
                                )
                                conn.commit()
                                st.success(f"Order {order_id} status updated to {new_status}")
                                st.rerun()

                        # Highlight the most purchased product by this user
                        cursor.execute("""
                            SELECT p.name, SUM(oi.quantity) as total_qty
                            FROM order_items oi
                            JOIN products p ON oi.product_id = p.id
                            JOIN orders o ON oi.order_id = o.id
                            WHERE o.username=%s
                            GROUP BY p.name
                            ORDER BY total_qty DESC
                            LIMIT 1
                        """, (selected_user,))

                        most_sold = cursor.fetchone()
                        if most_sold:
                            st.success(f"🔥 Most Purchased Product: {most_sold[0]} ({most_sold[1]} units)")


    # ================= USER PANEL =================
    # ================= USER PANEL =================
    else:

        menu = st.sidebar.radio("Menu", ["Shop", "My Cart", "Wishlist", "My Orders", "Profile"])  # Added Profile

        # ================= PROFILE PAGE =================
        # ================= PROFILE PAGE =================
        # ================= PROFILE PAGE =================
        if menu == "Profile":
            st.title("👤 My Profile")

            if "edit_profile" not in st.session_state:
                st.session_state.edit_profile = False

            # Fetch current user info
            cursor.execute("""
                SELECT username, email, phone, address, profile_pic
                FROM users
                WHERE username=%s
            """, (st.session_state.user,))
            user_data = cursor.fetchone()

            username_val = user_data[0] if user_data else ""
            email_val = user_data[1] if user_data else ""
            phone_val = user_data[2] if user_data else ""
            address_val = user_data[3] if user_data else ""
            profile_pic_val = user_data[4] if user_data else None

            # Display Username below header
            st.markdown(f"<h2 style='text-align:center; color:#ff4b4b;'>{username_val}</h2>", unsafe_allow_html=True)

            # CSS for circular image using st.image
            st.markdown("""
                <style>
                .stImage img {
                    border-radius: 50% !important;
                    width: 120px !important;
                    height: 120px !important;
                    object-fit: cover !important;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    border: 3px solid #ff4b4b !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Display Profile Picture using st.image
            if profile_pic_val and os.path.exists(profile_pic_val):
                st.image(profile_pic_val)
            else:
                st.image("https://via.placeholder.com/120")  # placeholder

            # Edit Profile Button
            if not st.session_state.edit_profile:
                if st.button("✏️ Edit Profile"):
                    st.session_state.edit_profile = True
                    st.rerun()
            else:
                st.subheader("Edit Profile Details")

                # Profile picture upload
                profile_pic_file = st.file_uploader("Upload Profile Picture", type=["jpg", "png", "jpeg"])

                # Show uploaded picture immediately
                if profile_pic_file:
                    st.image(profile_pic_file, width=120)

                # User Details Form
                username_input = st.text_input("Username", value=username_val)
                email_input = st.text_input("Email", value=email_val)
                phone_input = st.text_input("Phone Number", value=phone_val)
                address_input = st.text_area("Enter your address", value=address_val, height=100)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Profile"):
                        try:
                            # Save profile picture if uploaded
                            image_path = profile_pic_val
                            if profile_pic_file:
                                if not os.path.exists("profile_pics"):
                                    os.makedirs("profile_pics")
                                image_path = os.path.join("profile_pics", f"{st.session_state.user}.png")
                                with open(image_path, "wb") as f:
                                    f.write(profile_pic_file.getbuffer())

                            # Update user info
                            cursor.execute("""
                                UPDATE users
                                SET username=%s, email=%s, phone=%s, address=%s, profile_pic=%s
                                WHERE username=%s
                            """, (username_input, email_input, phone_input, address_input, image_path,
                                  st.session_state.user))
                            conn.commit()
                            st.success("✅ Profile Updated Successfully!")
                            st.session_state.user = username_input
                            st.session_state.edit_profile = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating profile: {e}")

                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.edit_profile = False
                        st.rerun()
        # ================= SHOP PAGE =================
        # ================= SHOP PAGE =================
        if menu == "Shop":
            st.title("🛍 Shop")

            # ---------------- FILTERS ----------------
            st.markdown("""
            <h2 style="
                background: linear-gradient(90deg,#ff4b4b,#ff9f43);
                padding:10px;
                border-radius:10px;
                color:white;
                text-align:center;">
            🔍 Filter & Sort Products
            </h2>
            """, unsafe_allow_html=True)
            search_query = st.text_input(
                "🔎 Search Product",
                placeholder="Type product name..."
            )

            # Fetch categories dynamically
            cursor.execute("SELECT DISTINCT category FROM products")
            all_categories = [row[0] for row in cursor.fetchall()]
            all_categories.insert(0, "All")  # Option to show all

            col1, col2, col3 = st.columns(3)

            with col1:
                selected_category = st.selectbox("Category", all_categories)

            with col2:
                sort_option = st.selectbox(
                    "Sort by",
                    ["Default", "Price: Low to High", "Price: High to Low"]
                )

            with col3:
                min_price, max_price = st.slider("Price Range", 0, 50000, (0, 50000), step=100)

            # Minimum rating
            min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)

            # ---------------- FETCH PRODUCTS ----------------
            query = "SELECT * FROM products"
            conditions = []
            params = []

            if selected_category != "All":
                conditions.append("category=%s")
                params.append(selected_category)

            if search_query:
                conditions.append("name LIKE %s")
                params.append(f"%{search_query}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            if sort_option == "Price: Low to High":
                query += " ORDER BY price ASC"
            elif sort_option == "Price: High to Low":
                query += " ORDER BY price DESC"

            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            # Filter in Python by price range & rating
            filtered_products = []
            for p in products:
                price = p[2]  # Price column
                rating = float(p[5] if len(p) > 5 else 0)  # Rating column if exists, else 0
                if min_price <= price <= max_price and rating >= min_rating:
                    filtered_products.append(p)

            products = filtered_products


            if not products:
                st.info("No products match your filter criteria.")
            else:
                # ---------------- DISPLAY PRODUCTS ----------------
                # AFTER filter logic and sorting

                cols = st.columns(3)


                for index, product in enumerate(filtered_products):
                    with cols[index % 3]:

                        st.markdown('<div class="card-container">', unsafe_allow_html=True)




                        if index < 5:
                            st.markdown("<div class='badge'>🆕 NEW</div>", unsafe_allow_html=True)

                        # image block
                        import base64

                        if product[3] and os.path.exists(product[3]):
                            with open(product[3], "rb") as img_file:
                                image_base64 = base64.b64encode(img_file.read()).decode()

                            st.markdown(
                                f"""
                                <div style="height:420px; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                                    <img src="data:image/png;base64,{image_base64}"
                                         style="height:100%; width:100%; object-fit:cover; border-radius:10px;" />
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        st.subheader(product[1])





                        # -------- Discount Section --------
                        # -------- Discount Logic --------
                        original_price = product[2]
                        discount = product[5] if product[5] else 0

                        if discount > 0:
                            discounted_price = original_price - (original_price * discount / 100)

                            st.markdown(
                                f"<div class='discount-badge'>🔥 {discount}% OFF</div>",
                                unsafe_allow_html=True
                            )

                            st.markdown(f"""
                                <div style="font-size:18px;">
                                    <span style="text-decoration: line-through; color:gray;">
                                        ₹ {original_price}
                                    </span>
                                </div>

                                <div style="font-size:22px; font-weight:bold; color:#00ff88;">
                                    ₹ {int(discounted_price)}
                                </div>
                            """, unsafe_allow_html=True)

                        else:
                            st.markdown(f"""
                                <div style="font-size:22px; font-weight:bold; color:#00ff88;">
                                    ₹ {original_price}
                                </div>
                            """, unsafe_allow_html=True)





                        st.write(f"Category: {product[4]}")

                        qty = st.number_input("Qty", min_value=1, key=f"qty_{product[0]}")

                        if st.button("Add to Cart", key=f"add_{product[0]}"):
                            cursor.execute(
                                "INSERT INTO cart (username, product_id, quantity) VALUES (%s,%s,%s)",
                                (st.session_state.user, product[0], qty)
                            )
                            conn.commit()
                            st.toast("✅ Added to Cart", icon="🛒")

                        if st.button("❤️ Add to Wishlist", key=f"wish_{product[0]}"):
                            cursor.execute(
                                "INSERT INTO wishlist (username, product_id) VALUES (%s,%s)",
                                (st.session_state.user, product[0])
                            )
                            conn.commit()
                            st.toast("💖 Added to Wishlist", icon="❤️")

                        st.markdown('</div>', unsafe_allow_html=True)
        # ================= CART PAGE =================
        elif menu == "My Cart":

            st.title("🛒 My Cart")
            st.markdown("""
            <style>
            .cart-header {
                font-weight: bold;
                font-size: 28px;   /* Increase this value */
            }
            </style>
            """, unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.markdown('<div class="cart-header">Product Name</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="cart-header">Product Price</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="cart-header">Quantity</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="cart-header">Price After Discount</div>', unsafe_allow_html=True)

            st.markdown("---")

            cursor.execute("""
                SELECT cart.id, 
                       products.name, 
                       products.price, 
                       cart.quantity, 
                       products.id, 
                       products.discount, 
                       products.image
                FROM cart
                JOIN products ON cart.product_id = products.id
                WHERE cart.username = %s
            """, (st.session_state.user,))

            cart_items = cursor.fetchall()

            if not cart_items:
                st.info("Your cart is empty.")
            else:
                total = 0

                for item in cart_items:
                    cart_id, name, price, quantity, product_id, discount, image = item

                    if discount:
                        discounted_price = price - (price * discount / 100)
                    else:
                        discounted_price = price

                    subtotal = discounted_price * quantity
                    total += subtotal

                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    st.markdown("""
                    <style>
                    .cart-name {
                        font-size: 25 px;
                        font-weight: 600;
                    }

                    .cart-image {
                        width: 100px;
                        margin-top: 8px;
                        border-radius: 8px;
                        }

                    .cart-price {
                        font-size: 25px;
                    }

                    .cart-qty {
                        font-size: 20px;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    with col1:
                        col1.markdown(f"<div class='cart-name'>{name}</div>", unsafe_allow_html=True)
                        if image:
                            st.image(image, width=120)
                    col2.markdown(f"<div class='cart-price'>₹{price}</div>", unsafe_allow_html=True)
                    col3.markdown(f"<div class='cart-qty'>Qty: {quantity}</div>", unsafe_allow_html=True)
                    col4.markdown(f"<div class='cart-price'>₹{subtotal}</div>", unsafe_allow_html=True)

                    col5, col6 = st.columns([1, 1])

                    if col5.button("➕", key=f"inc_{cart_id}"):
                        cursor.execute(
                            "UPDATE cart SET quantity = quantity + 1 WHERE id=%s",
                            (cart_id,)
                        )
                        conn.commit()
                        st.rerun()

                    if col6.button("❌ Remove", key=f"del_{cart_id}"):

                        if quantity > 1:
                            # Reduce quantity by 1
                            cursor.execute(
                                "UPDATE cart SET quantity = quantity - 1 WHERE id=%s",
                                (cart_id,)
                            )
                        else:
                            # If only 1 item, remove completely
                            cursor.execute(
                                "DELETE FROM cart WHERE id=%s",
                                (cart_id,)
                            )

                        conn.commit()
                        st.rerun()

                    st.divider()

                subtotal = st.session_state.subtotal
                discount_percent = st.session_state.discount_percent

                discount_amount = (subtotal * discount_percent) / 100

                amount_after_discount = subtotal - discount_amount

                gst = amount_after_discount * 0.12

                final_amount = amount_after_discount + gst

                st.markdown("---")
                st.write(f"Subtotal: ₹{subtotal}")
                st.write(f"Discount: -₹{discount_amount}")
                st.write(f"GST (12%): ₹{gst}")



                st.markdown(f"### 💰 Final Amount: ₹{final_amount:.2f}")
                st.session_state.payment_amount = final_amount

                # ---------------- CHECKOUT SYSTEM ----------------
                # ---------------- CHECKOUT SYSTEM ----------------
                # ---------------- CHECKOUT SYSTEM ----------------
                if st.button("✅ Checkout"):

                    cursor.execute("""
                        SELECT c.product_id, p.price, c.quantity, p.discount
                        FROM cart c
                        JOIN products p ON c.product_id = p.id
                        WHERE c.username=%s
                    """, (st.session_state.user,))
                    cart_items = cursor.fetchall()

                    if not cart_items:
                        st.warning("Your cart is empty!")
                    else:
                        total_amount = 0

                        for product_id, price, qty, discount in cart_items:
                            if discount:
                                discounted_price = price - (price * discount / 100)
                            else:
                                discounted_price = price

                            total_amount += discounted_price * qty

                        gst = total_amount * 0.12
                        st.session_state.subtotal = total_amount
                        st.session_state.gst = gst
                        st.session_state.payment_amount = final_amount
                        st.session_state.page = "coupon"


                        st.rerun()
            if st.session_state.get("page") == "coupon":

                st.title("🎁 Apply Coupon")

                st.write(f"Total Amount: ₹{st.session_state.payment_amount}")

                coupon_code = st.text_input("Enter Coupon Code")

                if st.button("Apply Coupon"):

                    cursor.execute("""
                        SELECT discount_percent FROM coupons
                        WHERE code=%s AND active=TRUE
                    """, (coupon_code.strip(),))

                    result = cursor.fetchone()

                    if result:
                        discount_percent = result[0]

                        discount_amount = (
                                                  st.session_state.payment_amount * discount_percent
                                          ) / 100

                        st.session_state.payment_amount -= discount_amount

                        st.success(f"{discount_percent}% Discount Applied!")
                        st.write(f"New Total: ₹{st.session_state.payment_amount}")

                    else:
                        st.error("Invalid Coupon")

                if st.button("Proceed to Payment"):
                    st.session_state.page = "payment"
                    st.rerun()
            if st.session_state.get("page") == "payment":

                st.title("💳 Select Payment Option")

                st.subheader(f"Total Amount: ₹{st.session_state.payment_amount}")

                payment_method = st.radio(
                    "Choose Payment Method:",
                    ["Cash on Delivery", "UPI", "Card"]
                )

                if st.button("Confirm Payment"):

                    # INSERT ORDER HERE
                    cursor.execute("""
                        INSERT INTO orders (username, total_amount, status, payment_status)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        st.session_state.user,
                        st.session_state.payment_amount,
                        "Confirmed",
                        "Paid"
                    ))
                    conn.commit()

                    order_id = cursor.lastrowid

                    # Insert order items
                    for product_id, price, qty, discount in st.session_state.cart_items:
                        cursor.execute("""
                            INSERT INTO order_items (order_id, product_id, quantity)
                            VALUES (%s, %s, %s)
                        """, (order_id, product_id, qty))

                    conn.commit()

                    # Clear cart AFTER payment
                    cursor.execute("DELETE FROM cart WHERE username=%s",
                                   (st.session_state.user,))
                    conn.commit()

                    st.success("🎉 Payment Successful!")

                    st.session_state.page = None
                    st.session_state.menu = "Shop"
                    st.rerun()

        elif menu == "My Orders":

            st.title("📦 My Orders")

            cursor.execute("""
                SELECT id, total_amount, order_date, status, payment_status
                FROM orders
                WHERE username = %s
                ORDER BY order_date DESC
            """, (st.session_state.user,))

            orders = cursor.fetchall()

            if not orders:
                st.info("No orders placed yet.")
            else:
                for order in orders:
                    order_id, total, order_date, status, payment_status = order

                    cursor.execute("""
                            SELECT products.name, products.price, order_items.quantity
                            FROM order_items
                            JOIN products ON order_items.product_id = products.id
                            WHERE order_items.order_id = %s
                        """, (order_id,))

                    items = cursor.fetchall()

                    products_html = ""
                    st.markdown("### 🛍 Products in this Order")

                    for name, price, qty in items:
                        subtotal = price * qty
                        st.write(f"🔹 {name}")
                        st.write(f"₹{price} × {qty} = ₹{subtotal}")
                        st.write("---")

                    st.markdown(f"""
                        <div style="background:white;padding:20px;border-radius:12px;margin-bottom:15px;">
                            <h3>🧾 Order ID: {order_id}</h3>
                            <p><strong>📅 Date:</strong> {order_date}</p>
                            <p><strong>💰 Total:</strong> ₹{total}</p>
                            <p><strong>🚚 Status:</strong> {status}</p>
                            <p><strong>💳 Payment:</strong> {payment_status}</p>
                            <hr style="border:1px solid #334155;">
                            
                            {products_html}
                        </div>
                        """, unsafe_allow_html=True)


        elif menu == "Wishlist":
            st.title("❤️ My Wishlist")

            cursor.execute("""
                SELECT p.id, p.name, p.price, p.image, p.category, p.discount
                FROM wishlist w
                JOIN products p ON w.product_id = p.id
                WHERE w.username = %s
            """, (st.session_state.user,))

            wishlist_items = cursor.fetchall()


            if not wishlist_items:
                st.info("Your wishlist is empty ❤️")
            else:
                for product in wishlist_items:
                    product_id = product[0]
                    name = product[1]
                    price = product[2]
                    image = product[3].replace("\\", "/")
                    category = product[4]
                    discount = product[5] if product[5] else 0

                    st.markdown(f"## 🛍 {name}")
                    st.write(f"Category: {category}")
                    st.image(image, width=200)

                    if discount > 0:
                        discounted_price = price - (price * discount / 100)
                        st.write(f"🔥 {discount}% OFF | ₹{discounted_price} (Original: ₹{price})")
                    else:
                        st.write(f"Price: ₹{price}")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("🛒 Move to Cart", key=f"move_{product_id}"):
                            cursor.execute(
                                "INSERT INTO cart (username, product_id, quantity) VALUES (%s,%s,%s)",
                                (st.session_state.user, product_id, 1)
                            )
                            cursor.execute(
                                "DELETE FROM wishlist WHERE username=%s AND product_id=%s",
                                (st.session_state.user, product_id)
                            )
                            conn.commit()
                            st.rerun()

                    with col2:
                        if st.button("❌ Remove", key=f"remove_{product_id}"):
                            cursor.execute(
                                "DELETE FROM wishlist WHERE username=%s AND product_id=%s",
                                (st.session_state.user, product_id)
                            )
                            conn.commit()
                            st.rerun()

                    st.divider()

                    st.divider()
