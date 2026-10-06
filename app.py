import streamlit as strlm
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import pdfplumber

# 1. OTRANTO TEMA VE SAYFA AYARLARI
strlm.set_page_config(page_title="Otranto Finansal Radar", layout="wide", page_icon="🔷")

mavi_stil = """
<style>
    .stApp { background-color: #F9FBFC; }
    h1, h2, h3 { color: #0B3C5D !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #0B3C5D !important; 
        color: white !important; 
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover { background-color: #328CC1 !important; }
</style>
"""
strlm.markdown(mavi_stil, unsafe_allow_html=True)

if "kullanici_veri_tabani" not in strlm.session_state:
    strlm.session_state["kullanici_veri_tabani"] = {
        "admin": {"sifre": "otrantoadmin2026", "ad": "Sistem Yöneticisi (Otranto)"},
        "firma1": {"sifre": "luca2026", "ad": "Ahmet Tekstil A.Ş."},
        "firma2": {"sifre": "analiz77", "ad": "Beta Lojistik Ltd."}
    }

if "giris_yapildi" not in strlm.session_state:
    strlm.session_state["giris_yapildi"] = False
    strlm.session_state["aktif_kullanici"] = ""
    strlm.session_state["firma_adi"] = ""

# 2. GİRİŞ EKRANI
if not strlm.session_state["giris_yapildi"]:
    strlm.markdown("<br><br><h1 style='text-align: center; font-size: 3rem;'>🔷 OTRANTO</h1>", unsafe_allow_html=True)
    strlm.markdown("<h3 style='text-align: center; color: #328CC1 !important;'>Akıllı Finansal Analiz & Denetim Platformu</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = strlm.columns(3)
    with col2:
        kullanici_adi = strlm.text_input("Kullanıcı Adı / Firma Kodu").strip()
        sifre = strlm.text_input("Şifre", type="password").strip()
        if strlm.button("Güvenli Giriş Yap", use_container_width=True):
            db = strlm.session_state["kullanici_veri_tabani"]
            if kullanici_adi in db and db[kullanici_adi]["sifre"] == sifre:
                strlm.session_state["giris_yapildi"] = True
                strlm.session_state["aktif_kullanici"] = kullanici_adi
                strlm.session_state["firma_adi"] = db[kullanici_adi]["ad"]
                strlm.rerun()
            else:
                strlm.error("❌ Hatalı giriş!")
else:
    ust_col1, ust_col2 = strlm.columns(2)
    with ust_col1:
        strlm.markdown(f"<h1>🔷 OTRANTO | {strlm.session_state['firma_adi']}</h1>", unsafe_allow_html=True)
    with ust_col2:
        strlm.markdown("<br>", unsafe_allow_html=True)
        if strlm.button("🚪 Oturumu Kapat", use_container_width=True):
            strlm.session_state["giris_yapildi"] = False
            strlm.rerun()

    strlm.markdown("<hr style='border: 1px solid #0B3C5D;'>", unsafe_allow_html=True)

    # ADMIN PANELİ
    if strlm.session_state["aktif_kullanici"] == "admin":
        strlm.subheader("🛠️ Otranto Üye Firma Yönetim Paneli")
        adm_col1, adm_col2 = strlm.columns(2)
        with adm_col1:
            yeni_kod = strlm.text_input("Yeni Firma Giriş Kodu")
            yeni_ad = strlm.text_input("Firma Resmi Unvanı")
            yeni_sifre = strlm.text_input("Firma Şifresi")
            if strlm.button("➕ Firmayı Sisteme Kaydet", use_container_width=True):
                strlm.session_state["kullanici_veri_tabani"][yeni_kod] = {"sifre": yeni_sifre, "ad": yeni_ad}
                strlm.success("Firma Kaydedildi!")
        with adm_col2:
            mevcut = [{"Kod": k, "Unvan": v["ad"]} for k, v in strlm.session_state["kullanici_veri_tabani"].items() if k != "admin"]
            strlm.dataframe(pd.DataFrame(mevcut), use_container_width=True)

    # MÜŞTERİ PANELİ
    else:
        yuklenen_dosya = strlm.file_uploader("Luca Yevmiye Defteri (Excel veya PDF formatında yükleyebilirsiniz):", type=["xlsx", "xls", "pdf"])

        if yuklenen_dosya is not None:
            df = None
            try:
                # EĞER PDF YÜKLENDİYSE
                if yuklenen_dosya.name.endswith('.pdf'):
                    with strlm.spinner("🔮 Otranto PDF Tabloları Ayıklanıyor..."):
                        pdf_satirlar = []
                        with pdfplumber.open(yuklenen_dosya) as pdf:
                            for sayfa in pdf.pages:
                                tablo = sayfa.extract_table()
                                if tablo:
                                    for satir in tablo:
                                        if any(satir):
                                            pdf_satirlar.append(satir)
                        
                        if len(pdf_satirlar) > 1:
                            df = pd.DataFrame(pdf_satirlar[1:], columns=pdf_satirlar[0])
                        else:
                            strlm.error("PDF içinden veri okunamadı.")
                
                # EĞER EXCEL YÜKLENDİYSE
                else:
                    df = pd.read_excel(yuklenen_dosya)
                
                if df is not None:
                    df.columns = df.columns.str.strip()
                    
                    kolon_esleme = {
                        'Borç': 'Borç', 'Alacak': 'Alacak', 'Tarih': 'Tarih', 
                        'Hesap Kodu': 'Hesap Kodu', 'Hesap Adı': 'Hesap Adı', 'Açıklama': 'Açıklama'
                    }
                    df.rename(columns=kolon_esleme, inplace=True)
                    
                    for col in ['Borç', 'Alacak']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    if 'Tarih' in df.columns:
                        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
                        df = df[df['Tarih'] >= '2026-01-01']
                    
                    strlm.success(f"📊 Otranto Analiz Motoru Başarıyla Tamamlandı: {len(df)} satır veri işlendi.")
                    
                    if 'Hesap Kodu' in df.columns:
                        df['Hesap Kodu Str'] = df['Hesap Kodu'].astype(str).str.strip()
                        
                        # 1. NAKİT AKIŞI
                        strlm.markdown("## 1. 📈 Nakit Akışı & Sıcak Para Hareketi")
                        nakit_df = df[df['Hesap Kodu Str'].str.startswith(('100', '102'))].copy()
                        if not nakit_df.empty and 'Tarih' in df.columns:
                            nakit_df['Ay'] = nakit_df['Tarih'].dt.to_period('M').astype(str)
                            nakit_ozet = nakit_df.groupby('Ay')[['Borç', 'Alacak']].sum().reset_index()
                            fig = px.bar(nakit_ozet, x='Ay', y=['Borç', 'Alacak'], barmode='group',
                                               title="Aylık Sıcak Para Giriş/Çıkış Dengesi",
                                               color_discrete_sequence=['#328CC1', '#0B3C5D'])
                            strlm.plotly_chart(fig, use_container_width=True)

                        # 2. KDV ÖNGÖRÜSÜ
                        strlm.markdown("## 2. 🔮 KDV Öngörü Modülü")
                        indirilecek_kdv = df[df['Hesap Kodu Str'].str.startswith('191')]['Borç'].sum()
                        hesaplanan_kdv = df[df['Hesap Kodu Str'].str.startswith('391')]['Alacak'].sum()
                        kdv_fark = hesaplanan_kdv - indirilecek_kdv
                        
                        kdv_col1, kdv_col2, kdv_col3 = strlm.columns(3)
                        kdv_col1.metric("191 - İndirilecek KDV", f"{indirilecek_kdv:,.2f} TL")
                        kdv_col2.metric("391 - Hesaplanan KDV", f"{hesaplanan_kdv:,.2f} TL")
                        if kdv_fark > 0:
                            kdv_col3.metric("🚨 Tahmini Ödenecek KDV", f"{kdv_fark:,.2f} TL", delta="-Ödeme")
                        else:
                            kdv_col3.metric("✅ Devreden KDV", f"{abs(kdv_fark):,.2f} TL", delta="+Devir")

                        # 3. HATALI FİŞ RADARI
                        strlm.markdown("## 3. 🚨 Hatalı / Kayıp Fiş Radarı")
                        if 'Açıklama' in df.columns:
                            df['Açıklama'] = df['Açıklama'].astype(str).str.lower()
                            evrak_col = 'Evrak No' if 'Evrak No' in df.columns else df.columns[0]
                            kayip_evrak = df[df['Açıklama'].str.contains('fat|ft|makbuz') & (df[evrak_col].isna() | (df[evrak_col] == ''))]
                            strlm.dataframe(kayip_evrak[['Tarih', 'Hesap Kodu', 'Açıklama', 'Borç', 'Alacak']].head(20), use_container_width=True)

                        # EXCEL RAPOR İNDİRME
                        strlm.markdown("## 📥 Raporu Bilgisayara İndir")
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.head(1000).to_excel(writer, sheet_name='Otranto Finans Raporu', index=False)
                        excel_data = output.getvalue()
                        strlm.download_button(label="📥 Raporu İndir (.xlsx)", data=excel_data, file_name="Otranto_Analiz.xlsx", use_container_width=True)
            except Exception as e:
                strlm.error(f"Sistem hatası: {e}")
        else:
            strlm.info("🔷 Otranto PDF/Excel hibrit motoru aktif. Luca Yevmiye Defterinizi yükleyin.")
