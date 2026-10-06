import streamlit as strlm
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import pdfplumber
import re

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

# Gelişmiş Dinamik Kullanıcı Yönetimi
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

# 2. OTRANTO GİRİŞ EKRANI
if not strlm.session_state["giris_yapildi"]:
    strlm.markdown("<br><br><h1 style='text-align: center; font-size: 3rem;'>🔷 OTRANTO</h1>", unsafe_allow_html=True)
    strlm.markdown("<h3 style='text-align: center; color: #328CC1 !important;'>Akıllı Finansal Analiz & Denetim Platformu</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = strlm.columns(3)
    with col2:
        strlm.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0px 4px 20px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        kullanici_adi = strlm.text_input("Kullanıcı Adı / Firma Kodu").strip()
        sifre = strlm.text_input("Şifre", type="password").strip()
        giris_butonu = strlm.button("Güvenli Giriş Yap", use_container_width=True)
        strlm.markdown("</div>", unsafe_allow_html=True)
        
        if giris_butonu:
            db = strlm.session_state["kullanici_veri_tabani"]
            if kullanici_adi in db and db[kullanici_adi]["sifre"] == sifre:
                strlm.session_state["giris_yapildi"] = True
                strlm.session_state["aktif_kullanici"] = kullanici_adi
                strlm.session_state["firma_adi"] = db[kullanici_adi]["ad"]
                strlm.rerun()
            else:
                strlm.error("❌ Hatalı kullanıcı adı veya şifre girdiniz!")

# 3. GİRİŞ BAŞARILIYSA
else:
    ust_col1, ust_col2 = strlm.columns(2)
    with ust_col1:
        strlm.markdown(f"<h1>🔷 OTRANTO | {strlm.session_state['firma_adi']}</h1>", unsafe_allow_html=True)
        strlm.markdown("**Veri Analiz Dönemi:** 01.01.2026 - Günümüz")
    with ust_col2:
        strlm.markdown("<br>", unsafe_allow_html=True)
        if strlm.button("🚪 Oturumu Kapat", use_container_width=True):
            strlm.session_state["giris_yapildi"] = False
            strlm.session_state["aktif_kullanici"] = ""
            strlm.session_state["firma_adi"] = ""
            strlm.rerun()

    strlm.markdown("<hr style='border: 1px solid #0B3C5D;'>", unsafe_allow_html=True)

    if strlm.session_state["aktif_kullanici"] == "admin":
        strlm.subheader("🛠️ Otranto Üye Firma Yönetim Paneli")
        adm_col1, adm_col2 = strlm.columns(2)
        with adm_col1:
            yeni_kod = strlm.text_input("Yeni Firma Giriş Kodu")
            yeni_ad = strlm.text_input("Firma Resmi Unvanı")
            yeni_sifre = strlm.text_input("Firma Giriş Şifresi")
            if strlm.button("➕ Firmayı Sisteme Kaydet", use_container_width=True):
                if yeni_kod and yeni_ad and yeni_sifre:
                    strlm.session_state["kullanici_veri_tabani"][yeni_kod] = {"sifre": yeni_sifre, "ad": yeni_ad}
                    strlm.success("🎉 Firma başarıyla sisteme eklendi!")
        with adm_col2:
            mevcut = [{"Firma Kodu": k, "Firma Adı": v["ad"]} for k, v in strlm.session_state["kullanici_veri_tabani"].items() if k != "admin"]
            strlm.dataframe(pd.DataFrame(mevcut), use_container_width=True)

    else:
        yuklenen_dosya = strlm.file_uploader("Luca Yevmiye Defteri (Excel veya PDF):", type=["xlsx", "xls", "pdf"])

        if yuklenen_dosya is not None:
            df = None
            try:
                # 🚀 AKILLI KELİME AVCI PDF MOTORU (HATA VERMEYEN YENİ SİSTEM)
                if yuklenen_dosya.name.endswith('.pdf'):
                    with strlm.spinner("🔮 Otranto PDF Analiz Motoru Çalışıyor..."):
                        ayiklanan_veriler = []
                        tarih_deseni = r"\b\d{2}\.\d{2}\.\d{4}\b"
                        hesap_deseni = r"\b\d{3}\b|\b\d{3}\.\d{2,}\b"
                        
                        with pdfplumber.open(yuklenen_dosya) as pdf:
                            for sayfa in pdf.pages:
                                metin = sayfa.extract_text()
                                if metin:
                                    for satir in metin.split('\n'):
                                        kelimeler = satir.split()
                                        if len(kelimeler) >= 4:
                                            # Satırda tarih ve hesap kodu avı
                                            tarihler = re.findall(tarih_deseni, satir)
                                            hesaplar = re.findall(hesap_deseni, satir)
                                            
                                            if tarihler and hesaplar:
                                                islem_tarihi = tarihler[0]
                                                hesap_kodu = hesaplar[0]
                                                
                                                # Borç ve Alacak tutarlarını yakalama (Son iki kelime)
                                                b_tutar = kelimeler[-2]
                                                a_tutar = kelimeler[-1]
                                                
                                                # Açıklama kısmını birleştirme
                                                aciklama = " ".join(kelimeler[2:-2])
                                                
                                                ayiklanan_veriler.append({
                                                    "Tarih": islem_tarihi,
                                                    "Evrak Tarihi": islem_tarihi,
                                                    "Hesap Kodu": hesap_kodu,
                                                    "Açıklama": aciklama,
                                                    "Borç": b_tutar,
                                                    "Alacak": a_tutar
                                                })
                        
                        if len(ayiklanan_veriler) > 0:
                            df = pd.DataFrame(ayiklanan_veriler)
                        else:
                            # Yedek Tablo Çekicisi
                            with pdfplumber.open(yuklenen_dosya) as pdf:
                                yedek_satirlar = []
                                for sayfa in pdf.pages:
                                    t = sayfa.extract_table()
                                    if t: [yedek_satirlar.append(s) for s in t if any(s)]
                            if len(yedek_satirlar) > 1:
                                df = pd.DataFrame(yedek_satirlar[1:], columns=yedek_satirlar[0])
                else:
                    df = pd.read_excel(yuklenen_dosya)
                
                if df is not None and not df.empty:
                    df.columns = df.columns.str.strip()
                    kolon_esleme = {'Borç': 'Borç', 'Alacak': 'Alacak', 'Tarih': 'Tarih', 'Hesap Kodu': 'Hesap Kodu', 'Hesap Adı': 'Hesap Adı', 'Açıklama': 'Açıklama', 'Evrak Tarihi': 'Evrak Tarihi'}
                    df.rename(columns=kolon_esleme, inplace=True)
                    
                    for col in ['Borç', 'Alacak']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    if 'Tarih' in df.columns:
                        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
                        df = df[df['Tarih'] >= '2026-01-01']
                    
                    if 'Evrak Tarihi' not in df.columns:
                        df['Evrak Tarihi'] = df['Tarih']
                    else:
                        df['Evrak Tarihi'] = pd.to_datetime(df['Evrak Tarihi'], errors='coerce', dayfirst=True).fillna(df['Tarih'])
                    
                    strlm.success(f"📊 Otranto Finansal Analiz Paneli Aktif: {len(df)} satır veri işlendi.")
                    df['Hesap Kodu Str'] = df['Hesap Kodu'].astype(str).str.strip()
                    
                    # --- GELECEK SEKMELİ DENETİM EKRANI ---
                    strlm.markdown("## 🚨 Otranto Gelişmiş Mali Denetim Müfettişi")
                    sekmeler = ["💵 Kasa Sınırı (7.000 TL)", "📅 10 Günlük Fatura Giriş İhlali", "🔄 Mükerrer Kayıt Radarı", "⚖️ Ters Bakiye Veren Hesaplar", "📊 Finansal Özetler & Rapor"]
                    tab1, tab2, tab3, tab4, tab5 = strlm.tabs(sekmeler)
                    
                    with tab1:
                        strlm.subheader("🚨 7.000 TL Üzeri Nakit Kasa İşlemleri")
                        k_f = df['Hesap Kodu Str'].str.startswith('100')
                        t_f = (df['Borç'] >= 7000) | (df['Alacak'] >= 7000)
                    # --- GELECEK SEKMELİ DENETİM EKRANI ---
                    strlm.markdown("## 🚨 Otranto Gelişmiş Mali Denetim Müfettişi")
                    sekmeler = [
                        "💵 Kasa Sınırı (7.000 TL)", 
                        "📅 10 Günlük Fatura Giriş İhlali", 
                        "🔄 Mükerrer Kayıt Radarı", 
                        "⚖️ Ters Bakiye Veren Hesaplar", 
                        "📊 Finansal Özetler & Rapor"
                    ]
                    tab1, tab2, tab3, tab4, tab5 = strlm.tabs(sekmeler)
                    
                    with tab1:
                        strlm.subheader("🚨 7.000 TL Üzeri Nakit Kasa İşlemleri")
                        k_f = df['Hesap Kodu Str'].str.startswith('100')
                        t_f = (df['Borç'] >= 7000) | (df['Alacak'] >= 7000)
                        kasa_ihlali = df[k_f & t_f]
                        if not kasa_ihlali.empty:
                            g_c = ['Tarih', 'Hesap Kodu', 'Açıklama', 'Borç', 'Alacak']
                            strlm.dataframe(kasa_ihlali[g_c], use_container_width=True)
                        else:
                            strlm.success("✅ Harika! Limit aşan nakit kasa işlemi yok.")
                            
                    with tab2:
                        strlm.subheader("📅 10 Günlük Yasal Fatura Kayıt Süresi İhlali")
                        df['Gecikme_Gun'] = (df['Tarih'] - df['Evrak Tarihi']).dt.days
                        gecikmeli_faturalar = df[df['Gecikme_Gun'] > 10]
                        if not gecikmeli_faturalar.empty:
                            strlm.warning(f"⚠️ Toplam {len(gecikmeli_faturalar)} işlemde süre aşılmış!")
                            g_cols = ['Tarih', 'Evrak Tarihi', 'Gecikme_Gun', 'Hesap Kodu', 'Açıklama', 'Borç']
                            strlm.dataframe(gecikmeli_faturalar[g_cols], use_container_width=True)
                        else:
                            strlm.success("✅ Mükemmel! Tüm faturalar yasal sürede işlenmiş.")
                            
                    with tab3:
                        strlm.subheader("🔄 Mükerrer (Çift Girilen Fatura) Şüphesi")
                        m_kriter = ['Tarih', 'Hesap Kodu', 'Borç', 'Alacak']
                        m_tutar = (df['Borç'] > 0) | (df['Alacak'] > 0)
                        mukerrer = df[df.duplicated(subset=m_kriter, keep=False) & m_tutar]
                        if not mukerrer.empty:
                            strlm.dataframe(mukerrer[m_kriter].sort_values(by='Tarih'), use_container_width=True)
                        else:
                            strlm.success("✅ Temiz! Aynı gün çift girilen mükerrer kayıt yok.")
                            
                    with tab4:
                        strlm.subheader("⚖️ Aktif Karakterli Hesap Kontrolü")
                        ters_durumlar = []
                        for h_kod in ['100', '102']:
                            h_df = df[df['Hesap Kodu Str'].str.startswith(h_kod)]
                            top_b = h_df['Borç'].sum()
                            top_a = h_df['Alacak'].sum()
                            if top_a > top_b:
                                ters_durumlar.append({
                                    "Hesap Kodu": h_kod, 
                                    "Toplam Giriş (Borç)": top_b, 
                                    "Toplam Çıkış (Alacak)": top_a, 
                                    "Durum": "Eksi Bakiye (Hatalı)"
                                })
                        if ters_durumlar:
                            strlm.dataframe(pd.DataFrame(ters_durumlar), use_container_width=True)
                        else:
                            strlm.success("✅ Doğru! Kasa ve Banka hesapları eksiye düşmemiştir.")
                            
                    with tab5:
                        strlm.subheader("📈 Şirket Finansal Nakit Akışı")
                        nakit_df = df[df['Hesap Kodu Str'].str.startswith(('100', '102'))].copy()
                        if not nakit_df.empty:
                            nakit_df['Ay'] = nakit_df['Tarih'].dt.to_period('M').astype(str)
                            nakit_ozet = nakit_df.groupby('Ay')[['Borç', 'Alacak']].sum().reset_index()
                            fig = px.bar(nakit_ozet, x='Ay', y=['Borç', 'Alacak'], barmode='group', color_discrete_sequence=['#328CC1', '#0B3C5D'])
                            strlm.plotly_chart(fig, use_container_width=True)

                        strlm.markdown("### 🔮 KDV Öngörü Sonucu")
                        i_kdv = df[df['Hesap Kodu Str'].str.startswith('191')]['Borç'].sum()
                        h_kdv = df[df['Hesap Kodu Str'].str.startswith('391')]['Alacak'].sum()
                        strlm.metric("Net KDV Durumu (Eksi ise Devir, Artı ise Ödeme)", f"{h_kdv - i_kdv:,.2f} TL")
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.head(1000).to_excel(writer, sheet_name='Otranto Rapor', index=False)
                        strlm.download_button(label="📥 Denetim Raporunu İndir (.xlsx)", data=output.getvalue(), file_name="Otranto_Mali_Denetim.xlsx", use_container_width=True)
                else:
                    strlm.error("⚠️ Dosya boş veya uygun formatta veri ayıklanamadı.")
            except Exception as e:
                strlm.error(f"Sistem hatası: {e}")
        else:
            strlm.info("🔷 Otranto PDF/Excel hibrit motoru aktif. Luca Yevmiye Defterinizi yükleyin.")

