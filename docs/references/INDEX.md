# Referans Belgeler

Pilot tarla: **Bahçekaradalak köyü, Bala/Ankara** — 39.51563 N, 33.21366 E

## Toprak Analizi Kaynakları

| Dosya | İçerik | Kodda nerede kullanılıyor |
|---|---|---|
| `Toprak_Analizleri_ve_Yorumlanmasi.pdf` | Dr. Elif Öztürk, Karadeniz TARE 2021. Resmi Türk sınıflandırma tabloları (Ülgen-Yurtsever 1995, Richards 1954, Hızalan-Ünal 1966). pH, kireç, OM, mikro element bantları. | `soil/reference.py` — tüm eşikler |
| `Toprak Uygulama.pdf` | A.Ü. Ziraat Fak. ders notları. Analiz yöntemleri (Walkley-Black, DTPA, Olsen), saturasyon tabloları, bünye sınıfları. | `soil/reference.py` — yöntem notları |
| `Ankara_Universitesi_Ziraat_Fakultesi_Haymana_Arast.pdf` | Soba ve ark. 2015, Toprak Su Dergisi. Haymana A.Ü. Çiftliği'nde 65 örnek saha çalışması. **Pilot tarlaya en yakın bölgesel veri.** Fe/Mn/B tüm parsellerde yetersiz; kireç %16–39. | `soil/reference.py` — bölgesel not ve kanıtlar |

## Proje Belgesi

| Dosya | İçerik |
|---|---|
| `ulusan-agrotech-solutions.pdf` | Ulusan AgroTech Solutions proje raporu (Phase 0–1 scope, teknik kararlar). |

## Kaynak Öncelik Sırası

Toprak parametresi yorumlarken referans önceliği:

1. **Pilot tarla toprak analizi** (kullanıcı tarafından yüklenen PDF) — gerçek ölçüm
2. **Haymana saha çalışması** (Soba 2015) — en yakın bölgesel kanıt
3. **Türk resmi standartları** (Ülgen-Yurtsever, Richards, Hızalan-Ünal) — eşik değerleri
4. **Uluslararası kaynaklar** (Silanpää 1990, Lindsay-Norvell 1978, Wolf 1971) — mikro element eşikleri
