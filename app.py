import streamlit as st
from supabase import create_client, Client
import uuid

SUPABASE_URL = "https://uviowmpciysmuehljchv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2aW93bXBjaXlzbXVlaGxqY2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY0NzE1NTcsImV4cCI6MjEwMjA0NzU1N30.Re-ViCrX58Sr8BspZu82breylTbrkDEN7NxXB9dHc6g"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="خزانتي الرقمية", layout="centered")
st.title("👗 خزانتي الرقمية الشخصية")

if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.info("أهلاً بكِ! ادخلي باسمك فقط لتبدئي في تنظيم خزانتك الرقمية:")
    name_input = st.text_input("اسم المستخدم أو لقبك")
    if st.button("دخول للخزانة"):
        if name_input.strip():
            st.session_state.username = name_input.strip()
            st.rerun()
        else:
            st.warning("الرجاء إدخال اسم صحيح.")
else:
    st.write(f"أهلاً بكِ، **{st.session_state.username}**! ✨")
    
    if st.button("تسجيل خروج / تغيير الاسم"):
        st.session_state.username = None
        st.rerun()

    st.markdown("---")
    st.subheader("➕ إضافة قطعة جديدة للخزانة")

    with st.form("upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("رفع صورة القطعة", type=["jpg", "jpeg", "png"])
        category = st.selectbox("التصنيف", ["Tops", "Bottoms", "Dresses", "Shoes", "Bags"])
        notes = st.text_input("ملاحظات / وصف بسيط (اختياري)")
        
        submitted = st.form_submit_button("حفظ القطعة")
        
        if submitted and uploaded_file is not None:
            file_extension = uploaded_file.name.split(".")[-1]
            file_path = f"{st.session_state.username}/{uuid.uuid4()}.{file_extension}"
            
            try:
                supabase.storage.from_("wardrobe-images").upload(
                    file_path, 
                    uploaded_file.getvalue(), 
                    file_options={"content-type": f"image/{file_extension}"}
                )
                image_url = supabase.storage.from_("wardrobe-images").get_public_url(file_path)
                supabase.table("wardrobe_items").insert({
                    "user_id": st.session_state.username,
                    "image_url": image_url,
                    "category": category,
                    "notes": notes
                }).execute()
                st.success("تمت إضافة القطعة بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")

    st.markdown("---")
    st.subheader("🧥 خزانتك الرقمية")

    try:
        response = supabase.table("wardrobe_items").select("*").eq("user_id", st.session_state.username).execute()
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
