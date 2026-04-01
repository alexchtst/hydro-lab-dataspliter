import streamlit as st

st.set_page_config(
    page_title="Hydrolab Data Processing GUI Web Based",
    layout="wide"
)

st.title("Hydrolab Data Pipeline")
st.caption("Web-based data processing and synchronization interface")

st.divider()

st.write(
    """
Aplikasi ini digunakan untuk menjalankan seluruh proses data pipeline
Hydrolab mulai dari preprocessing, statistical generation,
hingga sinkronisasi database backend.
"""
)

st.divider()

st.subheader("Pipeline Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.container(border=True)
    st.markdown("### Metadata Processing")
    st.write(
        """
        Generate metadata utama dari dataset awal.
        Digunakan sebagai referensi seluruh pipeline berikutnya.
        """
    )

with col2:
    st.container(border=True)
    st.markdown("### Statistical & Historical")
    st.write(
        """
        Melakukan pairing data, transformasi statistik,
        serta pembentukan historical dataset.
        """
    )

with col3:
    st.container(border=True)
    st.markdown("### Database Upload")
    st.write(
        """
        Sinkronisasi seluruh file JSON hasil pipeline
        ke MongoDB backend.
        """
    )

st.divider()

st.subheader("Processing Flow")

st.markdown(
    """
1. **Metadata Page**  
   Membuat struktur data dasar station.

2. **Statistical Page**  
   Menghasilkan pairing data dan statistical dataset.

3. **DB Upload Page**  
   Upload seluruh dataset ke MongoDB secara atomik.
"""
)

st.divider()

st.subheader("Notes")

st.info(
    """
Pastikan setiap step pipeline dijalankan secara berurutan.
Upload database hanya dapat dilakukan jika seluruh file JSON tersedia.
"""
)