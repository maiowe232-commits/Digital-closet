import streamlit as st
from supabase import create_client
import uuid

# إعدادات Supabase
SUPABASE_URL = "https://uviowmpciysmuehljchv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2aW93bXBjaXlzbXVlaGxqY2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY0NzE1NTcsImV4cCI6MjEwMjA0NzU1N30.Re-ViCrX58Sr8BspZu82breylTbrkDEN7NxXB9dHc6g"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="خزانتك الرقمية", page_icon="👗")

st.title("👗 خزانتك الرقمية")

# نموذج إضافة قطعة
uploaded_file = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])
category = st.selectbox("التصنيف", ["Tops", "Bottoms", "Dresses", "Shoes", "Accessories"])
notes = st.text_area("ملاحظات / وصف بسيط (اختياري)")

if st.button("حفظ القطعة"):
    if uploaded_file is not None:
        try:
            # 1. تجهيز مسار الملف باسم عشوائي لتجنب مشاكل الأحرف العربية
            file_extension = uploaded_file.name.split(".")[-1]
            file_path = f"item_{uuid.uuid4()}.{file_extension}"
            
            # 2. رفع الصورة لـ Supabase Storage (استخدام البوكت wardrobe-images)
            res = supabase.storage.from_("wardrobe-images").upload(
                path=file_path,
                file=uploaded_file.getvalue(),
                file_options={"content-type": f"image/{file_extension}"}
            )
            
            # 3. الحصول على الرابط العام
            image_url = supabase.storage.from_("wardrobe-images").get_public_url(file_path)
            
            # 4. حفظ البيانات في جدول wardrobe_items
            data = {
                "image_url": image_url,
                "category": category,
                "notes": notes
            }
            db_res = supabase.table("wardrobe_items").insert(data).execute()
            
            st.success("تم حفظ القطعة بنجاح!")
            st.rerun()
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء الحفظ: {e}")
    else:
        st.warning("يرجى اختيار صورة أولاً")

# عرض الخزانة
st.subheader("خزانتك الرقمية")
try:
    response = supabase.table("wardrobe_items").select("*").execute()
    items = response.data
    
    if items:
        for item in items:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(item['image_url'], width=100)
            with col2:
                st.write(f"**التصنيف:** {item['category']}")
                st.write(f"**الملاحظات:** {item['notes']}")
    else:
        st.info("الخزانة فارغة حالياً.")
except Exception as e:
    st.error(f"تعذر تحميل الخزانة: {e}")
