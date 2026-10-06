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
            else: strlm.error("❌ Hatalı kullanıcı adı veya şifre girdiniz!")

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
                if yuklenen_dosya.name.endswith('.pdf'):
                    with strlm.spinner("🔮 Otranto PDF Tabloları Ayıklıyor..."):
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
                                                        "Tarih": t_bul, "Evrak Tarihi": t_bul[-1], "Hesap Kodu": h_kod,
                                                        "Açıklama": " ".join(kelimeler[1:-2])[:80], "Borç": b_ham, "Alacak": a_ham
                                                    })
                                                except ValueError: continue
                        if len(ayiklanan_veriler) > 0: df = pd.DataFrame(ayiklanan_veriler)
                else:
                    df = pd.read_excel(yuklenen_dosya)
                    if not df.empty:
                        for i in range(min(5, len(df))):
                            h_m = str(df.iloc[i, 0])
                            if any(k in h_m.lower() for k in ["ltd", "a.ş", "tic"]):
                                detected_company_name = h_m.strip()
                                break

                if detected_company_name:
                    c_name = detected_company_name.replace("Unvan:", "").replace("Firma:", "").strip()
                    if c_name and strlm.session_state["firma_adi"] != c_name:
                        strlm.session_state["firma_adi"] = c_name
                        strlm.rerun()

                if df is not None and not df.empty:
                    if not yuklenen_dosya.name.endswith('.pdf'):
                        yeni_df = pd.DataFrame()
                        yeni_df['Tarih'] = df.iloc[:, 0]
                        yeni_df['Hesap Kodu'] = df.iloc[:, 1]
                        yeni_df['Açıklama'] = df.iloc[:, 2] if len(df.columns) > 2 else "Açıklama Eksik"
                        yeni_df['Borç'] = df.iloc[:, -2] if len(df.columns) > 3 else 0
                        yeni_df['Alacak'] = df.iloc[:, -1] if len(df.columns) > 4 else 0
                        yeni_df['Evrak Tarihi'] = yeni_df['Tarih']
                        df = yeni_df
                    
                    # 🚀 KESİN ÇÖZÜM: Tüm sütunları baştan string formatına zorluyoruz ve NaN değerleri engelliyoruz
                    df['Açıklama'] = df['Açıklama'].fillna("Açıklama Belirtilmemiş").astype(str).str.strip()
                    df['Hesap Kodu'] = df['Hesap Kodu'].fillna("000").astype(str).str.strip()
                    df['Tarih'] = df['Tarih'].fillna("").astype(str).str.strip()
                    df['Evrak Tarihi'] = df['Evrak Tarihi'].fillna("").astype(str).str.strip()
                    
                    for col in ['Borç', 'Alacak']:
                        df[col] = df[col].astype(str).str.replace(' ', '', regex=False)
                        df[col] = df[col].apply(lambda x: x.replace('.', '').replace(',', '.') if ',' in x and '.' in x else x)
                        df[col] = df[col].apply(lambda x: x.replace('.', '') if '.' in x and ',' not in x and len(x.split('.')[-1]) == 2 else x)
                        df[col] = df[col].str.replace(',', '.', regex=False)
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
                    df = df.dropna(subset=['Tarih'])
                    df['Evrak Tarihi'] = pd.to_datetime(df['Evrak Tarihi'], errors='coerce', dayfirst=True).fillna(df['Tarih'])
                    
                    # Hesap kodlarını temiz metne dönüştür
                    df['Hesap Kodu Str'] = df['Hesap Kodu'].astype(str).str.replace('.', '', regex=False).str.replace(' ', '', regex=False).str.strip().str.slice(0, 3)
                    
                    strlm.success(f"📊 Otranto Finansal Yapay Zeka Denetim Motoru Aktif.")
                    
                    sekmeler = [
                        "🛡️ Mali Denetim Müfettişi", 
                        "📅 Yıl İçi Ters Bakiye Radarı",
                        "💼 Ortaklar Cari & Adat Yükü",
                        "⚖️ Sermaye Yeterlilik Oranları",
                        "📊 Bilanço & Gelir Tablosu Özetleri"
                    ]
                    tab1, tab2, tab3, tab4, tab5 = strlm.tabs(sekmeler)
                    
                    with tab1:
                        strlm.subheader("🚨 Riskli ve Usulsüz İşlem Denetimleri")
                        k_f = df['Hesap Kodu Str'] == '100'
                        t_f = (df['Borç'] >= 7000) | (df['Alacak'] >= 7000)
                        kasa_ihlali = df[k_f & t_f]
                        if not kasa_ihlali.empty:
                            strlm.error(f"⚠️ Kanuni 7.000 TL Nakit Sınırını Aşan {len(kasa_ihlali)} İşlem Saptandı!")
                            strlm.dataframe(kasa_ihlali[['Tarih', 'Hesap Kodu', 'Açıklama', 'Borç']], use_container_width=True)
                        else:
                            strlm.success("✅ Harika! Limit aşan usulsüz nakit kasa işlemi saptanmadı.")
                        
                        df['Gecikme_Gun'] = (df['Tarih'] - df['Evrak Tarihi']).dt.days
                        gecikmeli = df[df['Gecikme_Gun'] > 10]
                        if not gecikmeli.empty:
                            strlm.warning(f"📅 10 Günlük Yasal Kayıt Süresini Geçen {len(gecikmeli)} Fatura Saptandı!")
                            strlm.dataframe(gecikmeli[['Tarih', 'Evrak Tarihi', 'Gecikme_Gun', 'Açıklama', 'Borç']], use_container_width=True)
                        else:
                            strlm.success("✅ Mükemmel! Yasal 10 günlük süreyi aşan gecikmeli kayıt bulunamadı.")
                            
                    with tab2:
                        strlm.subheader("📅 Yıl İçi Günlük Yürüyen Bakiye Ters Durum Radarı")
                        strlm.info("Kasa veya Banka hesaplarının yıl içinde herhangi bir günde eksiye düştüğü tarihler:")
                        
                        df_sirali = df.sort_values(by='Tarih')
                        ters_gunler = []
                        for h_kod in ['100', '102']:
                            h_df = df_sirali[df_sirali['Hesap Kodu Str'] == h_kod].copy()
                            if not h_df.empty:
                                h_df['Net_Hareket'] = h_df['Borç'] - h_df['Alacak']
                                h_df['Yuruyen_Bakiye'] = h_df['Net_Hareket'].cumsum()
                                eksi_gunler = h_df[h_df['Yuruyen_Bakiye'] < 0]
                                for idx, row in eksi_gunler.iterrows():
                                    ters_gunler.append({
                                        "Tarih": row['Tarih'].strftime('%d.%m.%Y'), "Hesap": h_kod,
                                        "O Günkü Açıklama": row['Açıklama'], "Kritik Yürüyen Bakiye": f"{row['Yuruyen_Bakiye']:,.2f} TL"
                                    })
                        if ters_gunler:
                            strlm.error(f"🚨 DİKKAT: Hesaplar yıl içerisinde {len(ters_gunler)} defa eksi bakiye vermiştir!")
                            strlm.dataframe(pd.DataFrame(ters_gunler), use_container_width=True)
                        else:
                            strlm.success("✅ Bilgi: Kasa ve Banka hesapları yıl içindeki hiçbir günde terse düşmemiştir.")
                            
                    with tab3:
                        strlm.subheader("💼 131 / 331 Ortaklar Cari Hesabı & Adat (Faiz) Risk Radarı")
                        o_131_b = df[df['Hesap Kodu Str'] == '131']['Borç'].sum()
                        o_131_a = df[df['Hesap Kodu Str'] == '131']['Alacak'].sum()
                        bakiye_131 = o_131_b - o_131_a
                        
                        o_331_a = df[df['Hesap Kodu Str'] == '331']['Alacak'].sum()
                        o_331_b = df[df['Hesap Kodu Str'] == '331']['Borç'].sum()
                        bakiye_331 = o_331_a - o_331_b
                        
                        c_adat1, c_adat2 = strlm.columns(2)
                        c_adat1.metric("131 Ortaklardan Alacak Bakiye", f"{bakiye_131:,.2f} TL")
                        c_adat2.metric("331 Ortaklara Borç Bakiye", f"{bakiye_331:,.2f} TL")
                        
                        if bakiye_131 > 0:
                            strlm.error(f"🚨 TEHLİKE: 131 Ortaklar hesabı {bakiye_131:,.2f} TL BORÇ bakiyesi veriyor! Dönem sonunda adat faiz faturası kesilmesi kanunen zorunludur!")
                        else:
                            strlm.success("✅ Risk Yok: Ortakların şirkete borcu bulunmamaktadır (131 adat yükü riski saptanmadı).")
                            
                    with tab4:
                        strlm.subheader("⚖️ TTK 376. Madde Sermaye Yeterlilik & Borca Batıklık Analizi")
                        donen_varlik = df[df['Hesap Kodu Str'].str.startswith('1', na=False)]['Borç'].sum() - df[df['Hesap Kodu Str'].str.startswith('1', na=False)]['Alacak'].sum()
                        duran_varlik = df[df['Hesap Kodu Str'].str.startswith('2', na=False)]['Borç'].sum() - df[df['Hesap Kodu Str'].str.startswith('2', na=False)]['Alacak'].sum()
                        kısa_borc = df[df['Hesap Kodu Str'].str.startswith('3', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('3', na=False)]['Borç'].sum()
                        uzun_borc = df[df['Hesap Kodu Str'].str.startswith('4', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('4', na=False)]['Borç'].sum()
                        ozkaynak = df[df['Hesap Kodu Str'].str.startswith('5', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('5', na=False)]['Borç'].sum()
                        
                        sermaye_500 = df[df['Hesap Kodu Str'] == '500']['Alacak'].sum() - df[df['Hesap Kodu Str'] == '500']['Borç'].sum()
                        
                        s_col1, s_col2 = strlm.columns(2)
                        s_col1.metric("Kayıtlı Ödenmiş Sermaye (500 Hesabı)", f"{sermaye_500:,.2f} TL")
                        s_col2.metric("Mevcut Toplam Özkaynak Durumu", f"{ozkaynak:,.2f} TL")
                        
                        if sermaye_500 > 0:
                            sermaye_kayip_orani = (1 - (ozkaynak / sermaye_500)) * 100
                            strlm.info(f"📊 Mevcut Yasal Sermaye Kayıp Oranı: % {sermaye_kayip_orani:.1f}")
                            if sermaye_kayip_orani >= 66.6:
                                strlm.error(f"🚨 KANUNİ TEHLİKE: TTK 376 uyarınca şirket sermayesinin 2/3'sini kaybetmiştir! Sermayeniz {sermaye_500:,.2f} TL iken toplam özkaynağınız {ozkaynak:,.2f} TL'ye gerilemiştir. Acilen sermaye artırımı yapılmalıdır!")
                            elif sermaye_kayip_orani >= 50:
                                strlm.warning("⚠️ KANUNİ UYARI: Şirket yasal sermayesinin yarısını kaybetmiştir. Genel kurulun önlem alması zorunludur.")
                            else:
                                strlm.success("✅ Tebrikler: Şirketin yasal sermaye yeterliliği koruma altındadır, borca batıklık riski yoktur.")
                        else:
                            strlm.warning("⚠️ Bilgi: Yevmiye defterinde 500 Sermaye Hesabına ait hareket saptanmadığı için TTK 376 rasyosu hesaplanamadı.")
                            
                    with tab5:
                        strlm.subheader("📈 Verilerden Üretilen Kurumsal Özet Tablolar")
                        donen_varlik = df[df['Hesap Kodu Str'].str.startswith('1', na=False)]['Borç'].sum() - df[df['Hesap Kodu Str'].str.startswith('1', na=False)]['Alacak'].sum()
                        duran_varlik = df[df['Hesap Kodu Str'].str.startswith('2', na=False)]['Borç'].sum() - df[df['Hesap Kodu Str'].str.startswith('2', na=False)]['Alacak'].sum()
                        kısa_borc = df[df['Hesap Kodu Str'].str.startswith('3', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('3', na=False)]['Borç'].sum()
                        uzun_borc = df[df['Hesap Kodu Str'].str.startswith('4', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('4', na=False)]['Borç'].sum()
                        ozkaynak = df[df['Hesap Kodu Str'].str.startswith('5', na=False)]['Alacak'].sum() - df[df['Hesap Kodu Str'].str.startswith('5', na=False)]['Borç'].sum()
                        
                        brut_satis = df[df['Hesap Kodu Str'].str.startswith('60', na=False)]['Alacak'].sum()
                        satis_ind = df[df['Hesap Kodu Str'].str.startswith('61', na=False)]['Borç'].sum()
                        satis_maliyet = df[df['Hesap Kodu Str'].str.startswith('62', na=False)]['Borç'].sum()
                        faaliyet_gid = df[df['Hesap Kodu Str'].str.startswith('63', na=False)]['Borç'].sum()
                        net_kar = (brut_satis - satis_ind) - satis_maliyet - faaliyet_gid
                        
                        col_t1, col_t2 = strlm.columns(2)
                        with col_t1:
                            strlm.markdown("### 🏛️ Canlı Bilanço (TL)")
                            strlm.dataframe(pd.DataFrame({
                                "Hesap Grubu": ["Dönen Varlıklar", "Duran Varlıklar", "Kısa Vadeli Borçlar", "Uzun Vadeli Borçlar", "Özkaynaklar"],
                                "Tutar (TL)": [donen_varlik, duran_varlik, kısa_borc, uzun_borc, ozkaynak]
                            }), use_container_width=True)
                        with col_t2:
                            strlm.markdown("### 📉 Canlı Gelir Tablosu (TL)")
                            strlm.dataframe(pd.DataFrame({
                                "Mali Kalem": ["Brüt Satış Gelirleri", "Satış İndirimleri (-)", "Satışların Maliyeti (-)", "Faaliyet Giderleri (-)", "Net Dönem Kârı / Zararı"],
                                "Tutar (TL)": [brut_satis, satis_ind, satis_maliyet, faaliyet_gid, net_kar]
                            }), use_container_width=True)
                        
                        strlm.markdown("---")
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.head(1000).to_excel(writer, sheet_name='Otranto Rapor', index=False)
