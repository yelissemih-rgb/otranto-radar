import streamlit as strlm
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# 1. OTRANTO TEMA VE SAYFA AYARLARI
strlm.set_page_config(page_title="Otranto Finansal Radar", layout="wide", page_icon="🔷")

# Kurumsal Mavi Stil Özelleştirmesi
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

# Gelişmiş Dinamik Kullanıcı Yönetimi (Oturum Hafızası)
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
    strlm.markdown("<br><br>", unsafe_allow_html=True)
    strlm.markdown("<h1 style='text-align: center; font-size: 3rem; letter-spacing: 2px;'>🔷 OTRANTO</h1>", unsafe_allow_html=True)
    strlm.markdown("<h3 style='text-align: center; color: #328CC1 !important;'>Akıllı Finansal Analiz & Denetim Platformu</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = strlm.columns([1, 2, 1])
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

# 3. GİRİŞ BAŞARILIYSA ÇALIŞACAK ALAN
else:
    # Üst Navigasyon ve Çıkış Butonu
    ust_col1, ust_col2 = strlm.columns(2)
    with ust_col1:
        strlm.markdown(f"<h1>🔷 OTRANTO <span style='color:#328CC1; font-size:1.5rem;'>| {strlm.session_state['firma_adi']}</span></h1>", unsafe_allow_html=True)
    with ust_col2:
        strlm.markdown("<br>", unsafe_allow_html=True)
        if strlm.button("🚪 Oturumu Kapat", use_container_width=True):
            strlm.session_state["giris_yapildi"] = False
            strlm.session_state["aktif_kullanici"] = ""
            strlm.session_state["firma_adi"] = ""
            strlm.rerun()

    strlm.markdown("<hr style='border: 1px solid #0B3C5D;'>", unsafe_allow_html=True)

    # --- MODÜL A: 👑 YÖNETİCİ (ADMIN) PANELİ ---
    if strlm.session_state["aktif_kullanici"] == "admin":
        strlm.subheader("🛠️ Otranto Üye Firma Yönetim Paneli")
        strlm.markdown("Sistemi kullanan yeni firmaları buradan ekleyebilir veya şifrelerini yönetebilirsiniz.")
        
        adm_col1, adm_col2 = strlm.columns(2)
        with adm_col1:
            strlm.markdown("### Yeni Müşteri/Firma Tanımla")
            yeni_kod = strlm.text_input("Yeni Firma Giriş Kodu (Örn: firma3)")
            yeni_ad = strlm.text_input("Firma Resmi Unvanı (Örn: Öztürk İnşaat A.Ş.)")
            yeni_sifre = strlm.text_input("Firma Giriş Şifresi")
            
            if strlm.button("➕ Firmayı Sisteme Kaydet", use_container_width=True):
                if yeni_kod and yeni_ad and yeni_sifre:
                    strlm.session_state["kullanici_veri_tabani"][yeni_kod] = {"sifre": yeni_sifre, "ad": yeni_ad}
                    strlm.success(f"🎉 {yeni_ad} başarıyla sisteme eklendi! Artık kendi şifresiyle giriş yapabilir.")
                else:
                    strlm.warning("Lütfen tüm alanları doldurun.")
                    
        with adm_col2:
            strlm.markdown("### Kayıtlı Aktif Firmalar")
            mevcut_firmalar = []
            for k, v in strlm.session_state["kullanici_veri_tabani"].items():
                if k != "admin":
                    mevcut_firmalar.append({"Firma Kodu": k, "Firma Adı": v["ad"], "Şifre": v["sifre"]})
            strlm.dataframe(pd.DataFrame(mevcut_firmalar), use_container_width=True)

    # --- MODÜL B: 📊 FİRMA ANALİZ PANELİ (MÜŞTERİ EKRANI) ---
    else:
        yuklenen_dosya = strlm.file_uploader("Luca'dan indirdiğiniz Yevmiye Defteri Excel dosyasını buraya yükleyin:", type=["xlsx", "xls"])

        if yuklenen_dosya is not None:
            try:
                df = pd.read_excel(yuklenen_dosya)
                df.columns = df.columns.str.strip()
                
                # 2026 Filtreleme
                df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce', dayfirst=True)
                df = df[df['Tarih'] >= '2026-01-01']
                df['Hesap Kodu Str'] = df['Hesap Kodu'].astype(str).str.strip()
                
                strlm.success(f"📊 Otranto Analiz Motoru Aktif: {len(df)} satır veri inceleniyor.")
                
                # NAKİT AKIŞI
                strlm.markdown("## 1. 📈 Nakit Akışı & Sıcak Para Hareketi")
                nakit_df = df[df['Hesap Kodu Str'].str.startswith(('100', '102'))].copy()
                if not nakit_df.empty:
                    nakit_df['Ay'] = nakit_df['Tarih'].dt.to_period('M').astype(str)
                    nakit_ozet = nakit_df.groupby('Ay')[['Borç', 'Alacak']].sum().reset_index()
                    fig_nakit = px.bar(nakit_ozet, x='Ay', y=['Borç', 'Alacak'], barmode='group',
                                       title="Aylık Sıcak Para Giriş/Çıkış Dengesi",
                                       color_discrete_sequence=['#328CC1', '#0B3C5D'])
                    strlm.plotly_chart(fig_nakit, use_container_width=True)

                # KDV ÖNGÖRÜSÜ
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

                # HATALI FİŞ RADARI
                strlm.markdown("## 3. 🚨 Hatalı / Kayıp Fiş Radarı")
                df['Açıklama'] = df['Açıklama'].astype(str).str.lower()
                kayip_evrak = df[df['Açıklama'].str.contains('fat|ft|makbuz') & (df['Evrak No'].isna() | (df['Evrak No'] == ''))]
                strlm.dataframe(kayip_evrak[['Tarih', 'Hesap Kodu', 'Açıklama', 'Borç', 'Alacak']].head(20), use_container_width=True)

                # --- 📥 MODÜL C: EXCEL RAPOR İNDİRME ---
                strlm.markdown("## 📥 Otranto Yönetici Finansal Raporunu İndir")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    kdv_data = pd.DataFrame({
                        "Rapor Kalemi": ["191 - İndirilecek KDV Total", "391 - Hesaplanan KDV Total", "Net KDV Durumu"],
                        "Tutar (TL)": [indirilecek_kdv, hesaplanan_kdv, kdv_fark]
                    })
                    kdv_data.to_excel(writer, sheet_name='KDV Ozet Raporu', index=False)
                    kayip_evrak.to_excel(writer, sheet_name='Tespit Edilen Hatalı Fişler', index=False)
                
                excel_data = output.getvalue()
                
                strlm.download_button(
                    label="📥 Yönetici Finans Analiz Raporunu İndir (.xlsx)",
                    data=excel_data,
                    file_name=f"Otranto_Finans_Raporu_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            except Exception as e:
                strlm.error(f"Dosya işlenirken sistem hatası oluştu: {e}")
        else:
            strlm.info("🔷 Otranto sistemine erişiminiz onaylandı. Lütfen analizi başlatmak için Luca Yevmiye Defterinizi yükleyin.")
