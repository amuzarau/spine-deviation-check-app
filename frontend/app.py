import os
import requests
import streamlit as st

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Spine Deviation Check App",
    layout="centered",
)

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# -------------------------------------------------
# AUTH — ANONYMOUS USER (STEP 6.4)
# -------------------------------------------------
if "user_id" not in st.session_state:
    res = requests.post(f"{API_URL}/auth/anonymous", params={"role": "parent"})
    if res.status_code != 200:
        st.error("Ошибка инициализации пользователя")
        st.stop()

    data = res.json()
    st.session_state["user_id"] = data["user_id"]
    st.session_state["role"] = data["role"]

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🧍 Приложение для предварительной проверки формы позвоночника")

st.info(
    "⚠️ Данный инструмент предоставляет только предварительную оценку состояния осанки "
    "и не является медицинским диагнозом."
)

# -------------------------------------------------
# PHOTO UPLOAD
# -------------------------------------------------
back_photo = st.file_uploader(
    "Фото со спины (обязательно)",
    type=["jpg", "jpeg", "png"],
)

side_photo = st.file_uploader(
    "Фото сбоку (по желанию)",
    type=["jpg", "jpeg", "png"],
)

consent = st.checkbox(
    "Я подтверждаю, что являюсь законным представителем и даю согласие."
)

# -------------------------------------------------
# ANALYZE
# -------------------------------------------------
if st.button("Анализировать"):
    if not consent or not back_photo:
        st.error("Необходимо загрузить фото и подтвердить согласие.")
        st.stop()

    files = {
        "back_photo": (
            back_photo.name,
            back_photo.getvalue(),
            back_photo.type,
        )
    }

    if side_photo:
        files["side_photo"] = (
            side_photo.name,
            side_photo.getvalue(),
            side_photo.type,
        )

    with st.spinner("Выполняется анализ..."):
        res = requests.post(
            f"{API_URL}/analyze",
            params={"user_id": st.session_state["user_id"]},
            files=files,
            timeout=120,
        )

    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    data = res.json()

    st.subheader("📌 Результат")
    st.write("**Общий риск:**", data["overall_risk"].upper())

    st.markdown("### 🧠 Пояснение")
    for line in data["explanation"]:
        st.write("-", line)

# -------------------------------------------------
# HISTORY (STEP 6.6)
# -------------------------------------------------
st.markdown("---")
st.subheader("📊 История проверок")

res = requests.get(f"{API_URL}/history/{st.session_state['user_id']}")
if res.status_code == 200:
    history = res.json()
    if not history:
        st.info("История пока пуста.")
    else:
        for h in history:
            st.markdown(
                f"""
**Дата:** {h["date"]}  
**Общий риск:** {h["overall_risk"]}  
---
"""
            )

# -------------------------------------------------
# DOCTOR MODE (STEP 6.7)
# -------------------------------------------------
st.markdown("---")
if st.checkbox("👨‍⚕️ Войти как врач (demo)"):
    st.session_state["role"] = "doctor"

if st.session_state.get("role") == "doctor":
    st.subheader("👨‍⚕️ Панель врача (только чтение)")
    res = requests.get(f"{API_URL}/doctor/screenings")
    if res.status_code == 200:
        for r in res.json():
            st.markdown(
                f"""
**Дата:** {r["date"]}  
**Риск:** {r["overall_risk"]}  
**User:** {r["user_id"][:8]}…
---
"""
            )
