"""BBCH fenolojik büyüme takvimi ve detay paneli bileşeni."""

from __future__ import annotations

import streamlit as st

from tarla_ai.agronomy.bbch import BBCH_STAGES

START_IDX = 0

_BADGE_COLOR = {
    "green": "var(--ag-accent)",
    "amber": "var(--ag-amber)",
    "red":   "var(--ag-red)",
}


def render_bbch_calendar() -> None:
    """BBCH takvim diyagramını ve seçili aşama detay panelini render eder."""
    if "bbch_sel" not in st.session_state:
        st.session_state.bbch_sel = START_IDX

    cols = st.columns(len(BBCH_STAGES))
    for i, stage in enumerate(BBCH_STAGES):
        if i == START_IDX:
            dot_cls = "bbch-dot bbch-dot-start"
            lbl_cls = "bbch-label bbch-label-start"
        else:
            dot_cls = "bbch-dot bbch-dot-future"
            lbl_cls = "bbch-label bbch-label-future"

        if i == st.session_state.bbch_sel:
            dot_cls += " bbch-dot-selected"

        with cols[i]:
            st.markdown(
                f'<div class="bbch-stage" style="padding-bottom:4px">'
                f'  <div class="{dot_cls}">{stage.code}</div>'
                f'  <div class="{lbl_cls}" style="margin-bottom:6px">{stage.short}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Seç", key=f"bbch_{i}", use_container_width=True,
                         help=f"BBCH {stage.code} — {stage.name} aşamasını görüntüle"):
                st.session_state.bbch_sel = i
                st.rerun()

    sel = st.session_state.bbch_sel
    s = BBCH_STAGES[sel]

    tasks_html = "".join(
        f'<div class="bbch-task-item">'
        f'  <div class="bbch-task-dot bbch-task-dot-{prio}"></div>'
        f'  <div>{task}</div>'
        f'</div>'
        for prio, task in s.tasks
    )

    prio_set = {p for p, _ in s.tasks}
    urgency = "red" if "red" in prio_set else ("amber" if "amber" in prio_set else "green")

    st.markdown(
        f'<div class="bbch-detail">'
        f'  <div class="bbch-detail-code">BBCH {s.code}{"  ·  SONRAKİ AŞAMA" if sel == START_IDX else ""}</div>'
        f'  <div class="bbch-detail-title" style="color:{_BADGE_COLOR[urgency]}">{s.name}</div>'
        f'  <div class="bbch-detail-body">{s.description}</div>'
        f'  <div class="bbch-detail-tasks">'
        f'    <div class="bbch-detail-tasks-head">Bu Dönemde Yapılacaklar</div>'
        f'    {tasks_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ag-hint">Bir aşamaya tıklayarak o dönemin görevlerini ve detaylarını görüntüleyebilirsin.</div>',
        unsafe_allow_html=True,
    )
