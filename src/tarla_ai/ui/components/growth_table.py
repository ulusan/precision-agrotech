"""Tablo 2 — Büyüme dönemine göre N/su ihtiyacı + azot özeti kartı."""

from __future__ import annotations

import streamlit as st

from tarla_ai.agronomy.growth_stages import GROWTH_STAGES, NITROGEN_SUMMARY
from tarla_ai.ui.html import n_pill, th, tip

STAGE_TIPS: dict[str, str] = {
    "Çimlenme / Çıkış": (
        "Tohumun toprakta suyu emip çatlaması ve ilk yeşil sürgünün toprak yüzeyini delmesi. "
        "Sıcaklık en az 4°C, toprak nemi yeterli olmalı. "
        "Bu aşamada bitki henüz fotosentez yapamaz, tohumdaki besinle yaşar."
    ),
    "Kardeşlenme": (
        "Ana sapın dibinden yeni yan saplar (kardeşler) çıkar. "
        "Her kardeş ileride bir başak verebilir — kardeş sayısı verimi doğrudan belirler. "
        "Hedef: bitki başına 3–5 kardeş. Azot bu dönemde büyük önem kazanır."
    ),
    "Sapa Kalkma": (
        "Bitki boyunu hızla artırır, boğumlar birbirinden uzaklaşır. "
        "Azot ve su ihtiyacı bu evrede zirveye ulaşır. "
        "Bu dönemdeki kuraklık verimi en çok düşüren faktördür. "
        "Başak ve başakçık sayısı (tane sayısı) bu dönemde belirlenir."
    ),
    "Bayrak Yaprak / Başaklanma": (
        "Son yaprak (bayrak yaprağı) açılır ve başak kılıftan çıkmaya başlar. "
        "Bayrak yaprağı tane dolumunun ana enerji kaynağıdır — hastalıktan korunması kritik. "
        "Azot alımı bu dönemde en üst düzeydedir."
    ),
    "Çiçeklenme": (
        "Başaktaki çiçekler açılır ve tozlaşma gerçekleşir. "
        "Su stresine en hassas dönem — bu sırada kuraklık tane tutumunu (kaç tane bağlanacak) düşürür. "
        "Fusarium gibi mantar hastalıkları bu dönemde en tehlikelidir."
    ),
    "Tane Dolumu": (
        "Bağlanan daneler dolmaya başlar; önce sütümsü, sonra hamur kıvamına gelir. "
        "Su ve sıcaklık stresi dane ağırlığını düşürür. "
        "Son sulama fırsatı bu dönemdedir. Dolum sonunda su ihtiyacı azalır."
    ),
}

TERM_TIPS: dict[str, str] = {
    "BBCH": (
        "Bitkinin büyüme evresini uluslararası standart bir skaladaki sayıyla tanımlayan sistem. "
        "Almanya'da geliştirilen bu sistem tüm dünyada kullanılır. "
        "00 = çimlenme, 99 = hasat. Sayı büyüdükçe bitki olgunlaşır."
    ),
    "N": "Azot elementinin kimyasal sembolü. Bitkilerin en çok ihtiyaç duyduğu besin maddesi.",
    "kg N/da": (
        "Bir dekar (1.000 m²) alana uygulanan saf azot miktarı kilogram cinsinden. "
        "Örneğin '3 kg N/da' demek, her 1.000 m²'ye 3 kg saf azot uygulanması demek. "
        "Gübre torbasındaki azot yüzdesiyle hesaplanır: ör. %46 üre → 6.5 kg üre = ~3 kg N."
    ),
    "DAP": (
        "Di-Amonyum Fosfat — hem azot hem fosfor içeren granül gübre. "
        "İçeriği: yaklaşık %18 N + %46 P₂O₅. "
        "Ekimle birlikte toprağa karıştırılır; fosfor bu şekilde uygulanmalıdır çünkü "
        "kireçli topraklarda yüzeyden verilen fosfor bitkiye ulaşamaz."
    ),
    "P₂O₅": (
        "Fosforun laboratuvarda ölçülen oksit formu. "
        "Gübre etiketlerinde ve analiz raporlarında fosfor bu şekilde ifade edilir. "
        "Saf fosfor (P) ile aynı şey değildir — P₂O₅'ten P'ye geçmek için 0.436 ile çarpılır."
    ),
    "ZnSO₄": (
        "Çinko sülfat — toprak veya yaprak uygulaması için kullanılan çinko gübresi. "
        "İç Anadolu kireçli topraklarında çinko eksikliği çok yaygın olduğundan "
        "çinkolu gübre uygulaması genellikle önerilir."
    ),
    "Fusarium": (
        "Buğdayda 'başak yanıklığı' hastalığına yol açan mantar türü. "
        "Çiçeklenme döneminde sıcaklık + nem birleştiğinde salgın yapar. "
        "Hem verimi hem de tane kalitesini (mikotoksin) düşürür. "
        "Fungisit (mantar ilacı) ile çiçeklenme döneminde önlenir."
    ),
    "Fungisit": (
        "Mantar hastalıklarına karşı kullanılan tarım ilacı. "
        "'Fungi' mantar, '-sit' öldürücü anlamına gelir. "
        "Pas, septoria, fusarium gibi hastalıklara karşı uygulanır."
    ),
    "Herbisit": (
        "Yabancı otları öldürmek için kullanılan tarım ilacı. "
        "'Herba' ot, '-sit' öldürücü anlamına gelir. "
        "Buğday tarlasında rekabet eden istenmeyen otlara karşı uygulanır."
    ),
}


def _annotate_note(note: str) -> str:
    replacements = [
        ("kg N/da",  TERM_TIPS["kg N/da"]),
        ("P₂O₅",    TERM_TIPS["P₂O₅"]),
        ("ZnSO₄",   TERM_TIPS["ZnSO₄"]),
        ("DAP",      TERM_TIPS["DAP"]),
        ("Fusarium", TERM_TIPS["Fusarium"]),
        ("fungisit", TERM_TIPS["Fungisit"]),
        ("Fungisit", TERM_TIPS["Fungisit"]),
        ("herbisit", TERM_TIPS["Herbisit"]),
        ("Herbisit", TERM_TIPS["Herbisit"]),
    ]
    for term, desc in replacements:
        if term in note:
            note = note.replace(term, tip(desc, term), 1)
    return note


def render_growth_table() -> None:
    """Büyüme dönemi N/su tablosunu Streamlit'e render eder."""
    rows = ""
    for s in GROWTH_STAGES:
        donem_tip_text = STAGE_TIPS.get(s.donem, "")
        bbch_html  = tip(TERM_TIPS["BBCH"], f"BBCH {s.bbch}")
        donem_html = tip(donem_tip_text, s.donem, wide=True) if donem_tip_text else s.donem
        note_html  = _annotate_note(s.note)

        rows += (
            f"<tr>"
            f"  <td><span class='ref-param'>{donem_html}</span><br>"
            f"      <span class='ref-unit'>{bbch_html}</span></td>"
            f"  <td>{n_pill(s.n_seviye)}</td>"
            f"  <td class='ref-range' style='color:var(--ag-accent)'>{s.n_doz}</td>"
            f"  <td class='ref-note'>{s.su_ihtiyaci}</td>"
            f"  <td class='ref-note'>{note_html}</td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Dönem", "Buğdayın büyüme evresi. Her evre farklı bir bakım ve uygulama penceresi gerektirir. Üzerine gelerek detay okuyabilirsin.", "16%")
        + th("Azot İhtiyacı", "O dönemde bitkinin azota (N) ne kadar ihtiyaç duyduğunu gösterir. Pik = en yüksek talep.", "12%")
        + th("Öneri (kıraç)", "Kuru/kıraç tarım koşullarında o dönemde uygulanması önerilen azot miktarı. kg N/da = dekar başına kilogram saf azot.", "16%")
        + th("Su İhtiyacı", "O büyüme evresinde bitkinin suya olan ihtiyacı. Yüksek = kuraklık bu dönemde en çok zarar verir.", "16%")
        + th("Kritik Not", "O dönem için en önemli uyarı ve yapılması gereken işlem.")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )


def render_nitrogen_card() -> None:
    """Toplam azot programı özeti kartını render eder."""
    st.markdown(
        f'<div class="ag-card" style="margin-top:18px">'
        f'  <div style="font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;'
        f'              opacity:0.55;margin-bottom:12px">Toplam Azot Programı Özeti (Kıraç)</div>'
        f'  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:18px">'
        f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Taban (ekimle)</div>'
        f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["taban_N_kgda"]}</div></div>'
        f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Üst gübre</div>'
        f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["ust_gubre_kurac"]}</div></div>'
        f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Toplam N</div>'
        f'         <div style="font-size:15px;font-weight:600;color:var(--ag-accent)">{NITROGEN_SUMMARY["toplam_N_kurac"]}</div></div>'
        f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Fosfor (P₂O₅) taban</div>'
        f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["P2O5_taban"]}</div></div>'
        f'  </div>'
        f'  <div style="font-size:12px;opacity:0.6;line-height:1.6;margin-top:14px;'
        f'              border-top:1px solid var(--ag-line);padding-top:12px">{NITROGEN_SUMMARY["not"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
