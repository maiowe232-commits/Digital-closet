import streamlit as st

# أمر تلقائي يثبت مكتبة supabase لو مو موجودة
try:
    from supabase import create_client, Client
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "supabase"])
    from supabase import create_client, Client

import uuid

# بيانات مشروعك اللي دمناها قبل شوي
SUPABASE_URL = "https://uviowmpciysmuehljchv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2aW93bXBjaXlzbXVlaGxqY2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY0NzE1NTcsImV4cCI6MjEwMjA0NzU1N30.Re-ViCrX58Sr8BspZu82breylTbrkDEN7NxXB9dHc6g"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("👗 خزانتي الرقمية الشخصية")

if "user" not in st.session_state:
    st.session_state.user = None

# صفحة تسجيل الدخول أو حساب جديد
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["تسجيل الدخول", "حساب جديد"])
    
    with tab1:
        email = st.text_input("البريد الإلكتروني", key="l_email")
        password = st.text_input("كلمة المرور", type="password", key="l_pass")
        if st.button("دخول"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ: تأكدي من الإيميل أو كلمة المرور")

    with tab2:
        new_email = st.text_input("البريد الإلكتروني", key="r_email")
        new_password = st.text_input("كلمة المرور", type="password", key="r_pass")
        if st.button("إنشاء حساب"):
            try:
                res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("تم إنشاء الحساب بنجاح! سجلي دخولك الآن.")
            except Exception as e:
                st.error(f"خطأ في التسجيل: {e}")

# واجهة الدولاب بعد تسجيل الدخول
else:
    st.write(f"مرحباً بكِ! ({st.session_state.user.email})")
    
    if st.button("تسجيل خروج"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    st.markdown("---")
    st.subheader("➕ إضافة قطعة جديدة للخزانة")

    with st.form("upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("رفع صورة القطعة", type=["jpg", "jpeg", "png"])
        category = st.selectbox("التصنيف", ["Tops", "Bottoms", "Dresses", "Shoes", "Bags"])
        notes = st.text_input("ملاحظات / وصف بسيط (اختياري)")
        
        submitted = st.form_submit_button("حفظ القطعة")
        
        if submitted and uploaded_file is not None:
            user_id = st.session_state.user.id
            file_extension = uploaded_file.name.split(".")[-1]
            file_path = f"{user_id}/{uuid.uuid4()}.{file_extension}"
            
            try:
                # رفع الصورة إلى Storage
                supabase.storage.from_("wardrobe-images").upload(
                    file_path, 
                    uploaded_file.getvalue(), 
                    file_options={"content-type": f"image/{file_extension}"}
                )
                
                # جلب الرابط
                image_url = supabase.storage.from_("wardrobe-images").get_public_url(file_path)
                
                # حفظ البيانات في الجدول
                supabase.table("wardrobe_items").insert({
                    "user_id": user_id,
                    "image_url": image_url,
                    "category": category,
                    "notes": notes
                }).execute()
                
                st.success("تمت إضافة القطعة بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

    st.markdown("---")
    st.subheader("🧥 خزانتك الرقمية")

    try:
        response = supabase.table("wardrobe_items").select("*").eq("user_id", st.session_state.user.id).execute()
        items = response.data
        
        if not items:
            st.info("خزانتك فارغة حالياً. ابدئي بإضافة قطعكِ!")
        else:
            categories = ["Tops", "Bottoms", "Dresses", "Shoes", "Bags"]
            for cat in categories:
                cat_items = [i for i in items if i["category"] == cat]
                if cat_items:
                    st.markdown(f"### {cat}")
                    cols = st.columns(3)
                    for index, item in enumerate(cat_items):
                        with cols[index % 3]:
                            st.image(item["image_url"], use_column_width=True)
                            if item["notes"]:
                                st.caption(item["notes"])
                            if st.button("حذف", key=item["id"]):
                                supabase.table("wardrobe_items").delete().eq("id", item["id"]).execute()
                                st.rerun()
    except Exception as e:
        st.error(f"تعذر جلب البيانات: {e}")
