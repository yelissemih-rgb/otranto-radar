%%writefile app.py
import streamlit as strlm
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

strlm.set_page_config(page_title="Otranto Finansal Radar", layout="wide", page_icon="🔷")

mavi_stil = """
<style>
    .stApp { background-color: #F9FBFC; }
    h1, h2, h3 { color: #0B3C5D !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #0B3C5D !important; color: white !important; border-radius: 8px !important; font-weight: bold !important; }
    .stButton>button:hover { background-color: #328CC1 !important; }
</style>
"""
strlm.markdown(mavi_stil, unsafe_allow_html=True)

if "kullanici_veri_tabani" not in strlm.session_state:
    strlm.session_state["kullanici_veri_tabani"] = {
        "admin": {"sifre": "otrantoadmin2026", "ad": "Sistem Yöneticisi (Otranto)"},
        "firma1": {"sifre": "luca2026", "ad": "Ahmet Tekstil A.Ş."}
    }

if "giris_yapildi" not in strlm.session_state:
    strlm.session_state["giris_yapildi"] = False
    strlm.session_state["aktif_kullanici"] = ""
    strlm.session_state["firma_adi"] = ""

if not strlm.session_state["giris_yapildi"]:
    strlm.markdown("<br><br><h1 style='text-align: center; font-size: 3rem;'>🔷 OTRANTO</h1>", unsafe_allow_html=True)
    strlm.markdown("<h3 style='text-align: center; color: #328CC1 !important;'>Akıllı Finansal Analiz & Denetim Platformu</h3>", unsafe_allow_html=True)
    col1, col2, col3 = strlm.columns([1, 1.5, 1])
    with col2:
        kullanici_adi = strlm.text_input("Kullanıcı Adı")
        sifre = strlm.text_input("Şifre", type="password")
        if strlm.button("Güvenli Giriş Yap", use_container_width=True):
            db = strlm.session_state["kullanici_veri_tabani"]
            if kullanici_adi in db and db[kullanici_adi]["sifre"] == sifre:
                strlm.session_state["giris_yapildi"] = True
                strlm.session_state["aktif_kullanici"] = kullanici_adi
                strlm.session_state["firma_adi"] = db[kullanici_adi]["ad"]
                strlm.rerun()
            else: strlm.error("Hatalı giriş!")
else:
    ust_col1, ust_col2 = strlm.columns()
    with ust_col1: strlm.markdown(f"<h1>🔷 OTRANTO | {strlm.session_state['firma_adi']}</h1>", unsafe_allow_html=True)
    with ust_col2:
        if strlm.button("🚪 Oturumu Kapat", use_container_width=True):
            strlm.session_state["giris_yapildi"] = False
            strlm.rerun()

    if strlm.session_state["aktif_kullanici"] == "admin":
        strlm.subheader("🛠️ Otranto Üye Firma Yönetim Paneli")
        yeni_kod = strlm.text_input("Firma Giriş Kodu")
        yeni_ad = strlm.text_input("Firma Ünvanı")
        yeni_sifre = strlm.text_input("Şifre")
        if strlm.button("➕ Firmayı Kaydet"):
            strlm.session_state["kullanici_veri_tabani"][yeni_kod] = {"sifre": yeni_sifre, "ad": yeni_ad}
            strlm.success("Firma Kaydedildi!")
    else:
        yuklenen_dosya = strlm.file_uploader("Luca Yevmiye Defteri Excel", type=["xlsx", "xls"])
        if yuklenen_dosya is not None:
            df = pd.read_excel(yuklenen_dosya)
            df.columns = df.columns.str.strip()
            df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
            df = df[df['Tarih'] >= '2026-01-01']
            df['Hesap Kodu Str'] = df['Hesap Kodu'].astype(str).str.strip()
            
            strlm.markdown("## 1. 📈 Nakit Akışı Analizi")
            nakit_df = df[df['Hesap Kodu Str'].str.startswith(('100', '102'))].copy()
            if not nakit_df.empty:
                nakit_df['Ay'] = nakit_df['Tarih'].dt.to_period('M').astype(str)
                nakit_ozet = nakit_df.groupby('Ay')[['Borç', 'Alacak']].sum().reset_index()
                fig = px.bar(nakit_ozet, x='Ay', y=['Borç', 'Alacak'], barmode='group', color_discrete_sequence=['#328CC1', '#0B3C5D'])
                strlm.plotly_chart(fig, use_container_width=True)
            
            strlm.markdown("## 2. 🔮 KDV Öngörüsü")
            indirilecek_kdv = df[df['Hesap Kodu Str'].str.startswith('191')]['Borç'].sum()
            hesaplanan_kdv = df[df['Hesap Kodu Str'].str.startswith('391')]['Alacak'].sum()
            strlm.metric("Tahmini Net KDV Durumu", f"{hesaplanan_kdv - indirilecek_kdv:,.2f} TL")
