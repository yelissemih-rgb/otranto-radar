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
        "admin": {"sifre": "otrantoadmin2026", "ad": "Sistem Yöneticisi"},
        "firma1": {"sifre": "luca2026", "ad": "Firma Paneli"}
    }

if "giris_yapildi" not in strlm.session_state:
    strlm.session_state["giris_yapildi"] = False
    strlm.session_state["aktif_kullanici"] = ""
    strlm.session_state["firma_adi"] = "Yükleme Bekleniyor..."

# 2. OTRANTO GİRİŞ EKRANI
if not strlm.session_state["giris_yapildi"]:
    strlm.markdown("<br><br><h1 style='text-align: center; font-size: 3rem;'>🔷 OTRANTO</h1>", unsafe_allow_html=True)
    strlm.markdown("<h3 style='text-align: center; color: #328CC1 !important;'>Akıllı Finansal Analiz & Denetim Platformu</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = strlm.columns(3)
    with col2:
        strlm.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px;'>", unsafe_allow_html=True)
        kullanici_adi = strlm.text_input("Kullanıcı Adı / Firma Kodu").strip()
        sifre = strlm.text_input("Şifre", type="password").strip()
        giris_butonu = strlm.button("Güvenli Giriş Yap", use_container_width=True)
        strlm.markdown("</div>", unsafe_allow_html=True)
        
        if giris_butonu:
            db = strlm.session_state["kullanici_veri_tabani"]
            if kullanici_adi in db and db[kullanici_adi]["sifre"] == sifre:
                strlm.session_state["giris_yapildi"] = True
                strlm.session_state["aktif_kullanici"] = kullanici_adi
                strlm.rerun()
            else:
                strlm.error("❌ Hatalı kullanıcı adı veya şifre girdiniz!")

# 3. GİRİŞ BAŞARILIYSA
else:
    ust_col1, ust_col2 = strlm.columns(2)
    with ust_col1:
        strlm.markdown(f"<h1>🔷 OTRANTO | <span style='color:#328CC1;'>{strlm.session_state['firma_adi']}</span></h1>", unsafe_allow_html=True)
        strlm.markdown("**Veri Analiz Dönemi:** 01.01.2026 - Günümüz")
    with ust_col2:
        strlm.markdown("<br>", unsafe_allow_html=True)
        if strlm.button("🚪 Oturumu Kapat", use_container_width=True):
            strlm.session_state["giris_yapildi"] = False
            strlm.session_state["aktif_kullanici"] = ""
            strlm.session_state["firma_adi"] = "Yükleme Bekleniyor..."
            strlm.rerun()

    strlm.markdown("<hr style='border: 1px solid #0B3C5D;'>", unsafe_allow_html=True)

    if strlm.session_state["aktif_kullanici"] == "admin":
        strlm.subheader("🛠️ Otranto Üye Firma Yönetim Paneli")
        yeni_kod = strlm.text_input("Yeni Firma Giriş Kodu")
        yeni_sifre = strlm.text_input("Firma Giriş Şifresi")
        if strlm.button("➕ Firmayı Kaydet", use_container_width=True):
            if yeni_kod and yeni_sifre:
                strlm.session_state["kullanici_veri_tabani"][yeni_kod] = {"sifre": yeni_sifre, "ad": "Firma Paneli"}
                strlm.success("🎉 Firma başarıyla eklendi!")

    else:
        yuklenen_dosya = strlm.file_uploader("Luca Yevmiye Defteri (Excel veya PDF):", type=["xlsx", "xls", "pdf"])

        if yuklenen_dosya is not None:
            df = None
            detected_company_name = None
            try:
                # 🚀 ULTRA ESNEK VE KORUMALI PDF ANALİZ MOTORU
                if yuklenen_dosya.name.endswith('.pdf'):
                    with strlm.spinner("🔮 Otranto Finansal Verileri Ayrıştırıyor..."):
                        ayiklanan_veriler = []
                        
                        with pdfplumber.open(yuklenen_dosya) as pdf:
                            for sayfa in pdf.pages:
                                metin = sayfa.extract_text()
                                if metin:
                                    satirlar = metin.split('\n')
                                    for satir in satirlar:
                                        kelimeler = satir.split()
                                        if len(kelimeler) >= 3:
                                            satir_metni = " ".join(kelimeler)
                                            tarih_bul = re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", satir_metni)
                                            
                                            # Hata veren unvan temizleme deseni en başa taşınarak düzeltildi
                                            if not detected_company_name and any(k in satir.lower() for k in ["ltd", "a.ş", "tic", "san", "ştd"]):
                                                detected_company_name = satir.strip()
                                            
                                            if t_bul := tarih_bul:
                                                b_ham = kelimeler[-2].replace('.', '').replace(',', '.')
                                                a_ham = kelimeler[-1].replace('.', '').replace(',', '.')
                                                
                                                try:
                                                    float(a_ham)
                                                    hesap_bul = re.findall(r"\b\d{3}(?:\.\d+)?\b", satir)
                                                    h_kod = hesap_bul if hesap_bul else ["000"]
                                                    
                                                    ayiklanan_veriler.append({
                                                        "Tarih": t_bul[0],
                                                        "Evrak Tarihi": t_bul[-1],
                                                        "Hesap Kodu": h_kod[0],
                                                        "Açıklama": " ".join(kelimeler[1:-2])[:80],
                                                        "Borç": b_ham,
                                                        "Alacak": a_ham
                                                    })
                                                except ValueError:
                                                    continue
                        
                        if len(ayiklanan_veriler) > 0:
                            df = pd.DataFrame(ayiklanan_veriler)
                        else:
                            yedek_satirlar = []
                            with pdfplumber.open(yuklenen_dosya) as pdf:
                                for s in pdf.pages:
                                    t = s.extract_table()
                                    if t: [yedek_satirlar.append(r) for r in t if any(r)]
                            if len(yedek_satirlar) > 1:
                                df = pd.DataFrame(yedek_satirlar[1:])
                                df.columns = ['Tarih', 'Hesap Kodu', 'Açıklama', 'Borç', 'Alacak'] + list(df.columns[5:])
                                df['Evrak Tarihi'] = df['Tarih']
                else:
                    df = pd.read_excel(yuklenen_dosya)
                    if not df.empty:
                        for i in range(min(5, len(df))):
                            h_m = str(df.iloc[i, 0])
                            if any(k in h_m.lower() for k in ["ltd", "a.ş", "tic"]):
                                detected_company_name = h_m.strip()
                                break

                # Dinamik Firma Ünvanı Kontrolü (Hatasızlaştırılmış Versiyon)
                if detected_company_name:
                    c_name = re.sub(r"(?i)^unvan[:\s]*-*|(?i)^firma[:\s]*-*", "", detected_company_name).strip()
                    if c_name and strlm.session_state["firma_adi"] != c_name:
                        strlm.session_state["firma_adi"] = c_name
                        strlm.rerun()

                if df is not None and not df.empty:
                    df.columns = df.columns.str.strip()
                    kolon_esleme = {'Borç': 'Borç', 'Alacak': 'Alacak', 'Tarih': 'Tarih', 'Hesap Kodu': 'Hesap Kodu', 'Açıklama': 'Açıklama', 'Evrak Tarihi': 'Evrak Tarihi'}
                    df.rename(columns=kolon_esleme, inplace=True)
                    
                    if 'Evrak Tarihi' not in df.columns:
                        df['Evrak Tarihi'] = df['Tarih']
                    
                    for col in ['Borç', 'Alacak']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
                    df = df[df['Tarih'] >= '2026-01-01']
                    df['Evrak Tarihi'] = pd.to_datetime(df['Evrak Tarihi'], errors='coerce', dayfirst=True).fillna(df['Tarih'])
                    
                    # Liste tipi verileri güvenle temiz metne çeviriyoruz
                    df['Hesap Kodu Str'] = df['Hesap Kodu'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x)).str.strip()
                    
                    # --- SEKMELİ DENETİM EKRANI ---
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
                            g_c = ['Tarih', 'Hesap Kodu Str', 'Açıklama', 'Borç', 'Alacak']
                            strlm.dataframe(kasa_ihlali[g_c], use_container_width=True)
                        else:
                            strlm.success("✅ Harika! Limit aşan nakit kasa işlemi yok.")
                            
                    with tab2:
                        strlm.subheader("📅 10 Günlük Yasal Fatura Kayıt Süresi İhlali")
                        df['Gecikme_Gun'] = (df['Tarih'] - df['Evrak Tarihi']).dt.days
                        gecikmeli_faturalar = df[df['Gecikme_Gun'] > 10]
                        if not gecikmeli_faturalar.empty:
                            strlm.warning(f"⚠️ Toplam {len(gecikmeli_faturalar)} işlemde yasal süre aşılmış!")
                            g_cols = ['Tarih', 'Evrak Tarihi', 'Gecikme_Gun', 'Hesap Kodu Str', 'Açıklama', 'Borç']
                            strlm.dataframe(gecikmeli_faturalar[g_cols], use_container_width=True)
                        else:
                            strlm.success("✅ Mükemmel! Tüm faturalar yasal 10 günlük süre içinde işlenmiş.")
                            
                    with tab3:
                        strlm.subheader("🔄 Mükerrer (Çift Girilen Fatura) Şüphesi")
                        m_kriter = ['Tarih', 'Hesap Kodu Str', 'Borç', 'Alacak']
                        m_tutar = (df['Borç'] > 0) | (df['Alacak'] > 0)
                        mukerrer = df[df.duplicated(subset=m_kriter, keep=False) & m_tutar]
                        if not mukerrer.empty:
                            strlm.dataframe(mukerrer[m_kriter].sort_values(by='Tarih'), use_container_width=True)
                        else:
                            strlm.success("✅ Temiz! Aynı gün çift girilen mükerrer kayıt saptanmadı.")
                            
                    with tab4:
                        strlm.subheader("⚖️ Aktif Karakterli Hesap Kontrolü")
                        ters_durumlar = []
                        for h_kod in ['100', '102']:
                            h_df = df[df['Hesap Kodu Str'].str.startswith(h_kod)]
                            top_b = h_df['Borç'].sum()
                            top_a = h_df['Alacak'].sum()
                            if top_a > top_b:
                                ters_durumlar.append({"Hesap Kodu": h_kod, "Toplam Giriş (Borç)": top_b, "Toplam Çıkış (Alacak)": top_a, "Durum": "Eksi Bakiye (Hatalı)"})
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
                        strlm.download_button(label="📥 Denetim Raporunu Bilgisayara İndir (.xlsx)", data=output.getvalue(), file_name="Otranto_Mali_Denetim.xlsx", use_container_width=True)
                else:
                    strlm.error("⚠️ Dosya boş veya uygun formatta veri ayıklanamadı.")
            except Exception as e:
                strlm.error(f"Sistem hatası: {e}")
        else:
            strlm.info("🔷 Otranto PDF/Excel hibrit motoru aktif. Luca Yevmiye Defterinizi yükleyin.")
