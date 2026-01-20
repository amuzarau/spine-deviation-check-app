import os
import requests
import streamlit as st

st.set_page_config(page_title="Spine Deviation Check App", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🧍 Приложение для предварительной проверки формы позвоночника")

st.info(
    "⚠️ Данный инструмент предоставляет только предварительную оценку состояния осанки "
    "и не является медицинским диагнозом. "
    "При наличии сомнений рекомендуется обратиться к врачу-ортопеду."
)

st.markdown("### 📸 Инструкция по съёмке")
st.markdown("""
- **Вид со спины (обязательно):** стоя прямо, руки расслаблены  
- **Вид сбоку (по желанию):** полностью видна фигура  
- Хорошее освещение, естественная поза  
- Фотографии **не сохраняются**
""")

st.markdown("---")

back_photo = st.file_uploader(
    "Загрузите фото со спины (обязательно)", type=["jpg", "jpeg", "png"]
)

side_photo = st.file_uploader(
    "Загрузите фото сбоку (по желанию)", type=["jpg", "jpeg", "png"]
)

consent = st.checkbox(
    "Я подтверждаю, что являюсь родителем или законным представителем и даю согласие на проведение проверки."
)

if st.button("Анализировать"):
    if not consent:
        st.error("Необходимо подтвердить согласие.")
    elif not back_photo:
        st.error("Необходимо загрузить фото со спины.")
    else:
        files = {
            "back_photo": (back_photo.name, back_photo.getvalue(), back_photo.type)
        }
        if side_photo:
            files["side_photo"] = (
                side_photo.name,
                side_photo.getvalue(),
                side_photo.type,
            )

        try:
            with st.spinner("Выполняется анализ..."):
                response = requests.post(
                    f"{BACKEND_URL}/analyze", files=files, timeout=120
                )
            if response.status_code != 200:
                st.error(response.json().get("detail", "Ошибка анализа"))
            else:
                data = response.json()

                st.subheader("📌 Результаты оценки")

                st.markdown(
                    f"**Вид со спины (фронтальная плоскость):** `{data['frontal_risk'].upper()}`"
                )
                st.markdown(
                    f"**Вид сбоку (сагиттальная плоскость):** `{data['sagittal_risk'].upper()}`"
                )

                overall = data["overall_risk"].upper()
                if overall == "HIGH":
                    st.error(f"**Общая оценка: {overall}**")
                elif overall == "MEDIUM":
                    st.warning(f"**Общая оценка: {overall}**")
                else:
                    st.success(f"**Общая оценка: {overall}**")

                st.markdown("### 🧠 Пояснение")
                for line in data["explanation"]:
                    st.write(f"- {line}")

                st.markdown("### 📊 Технические показатели")
                st.json(data["metrics"])

                st.caption(f"ID сеанса: {data['session_id']}")

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка соединения с сервером: {e}")
