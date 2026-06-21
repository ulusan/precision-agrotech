"""Sulama suyu (kuyu) domain'i — parse, referans, yorumlama, doğrulama.

Pilot tarla (Ankara/Bala Üçem Köyü) tek sulama kaynağı: kendi kuyu suyu.
Kuyu suyu analiz raporu KALICI referans katmandır; her sulama kararında
referans alınır. Soil domain'iyle simetrik kurgulanmıştır.

İlke (soil ile aynı): hiçbir değer uydurulmaz. Ölçülmeyen parametre
(SAR, Na, B, Cl, HCO₃...) "veri yok" olarak işaretlenir, asla "güvenli"
varsayılmaz.
"""
