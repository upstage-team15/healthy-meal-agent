"""Design tokens and injected CSS for the NutriAgent Streamlit app.

Mirrors the color/typography tokens from ``src/index.css`` in the original
React app so the Streamlit version keeps the same look and feel.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Gothic+A1:wght@300;400;500;700;800;900&family=Nanum+Gothic+Coding:wght@400;700&display=swap');

:root {
  --background: #F5F7F4;
  --foreground: #212529;
  --card: #FFFFFF;
  --muted: #F0F2EF;
  --muted-foreground: #6B7B6B;
  --border: #D8E0D8;
  --sage: #5A7A5A;
  --sage-light: #8FAF8F;
  --sage-pale: #EBF0EB;
  --amber: #E8874A;
  --amber-pale: #FEF3EA;
  --danger: #D64545;
  --danger-pale: #FDEAEA;
  --warning: #D4860A;
  --warning-pale: #FEF6E0;
  --pass: #2D7A4F;
  --pass-pale: #E6F4EE;
}

html, body, [class*="css"] {
  font-family: 'Gothic A1', system-ui, sans-serif;
}

.stApp {
  background: var(--background);
}

[data-testid="stSidebar"] {
  background: var(--card);
  border-right: 1px solid var(--border);
}

.mono { font-family: 'Nanum Gothic Coding', monospace; }

/* ---------- Sidebar ---------- */
.brand-row { display: flex; align-items: center; gap: 10px; padding: 4px 0 12px; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px; background: var(--sage);
  display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
}
.brand-title { font-weight: 700; font-size: 15px; color: var(--foreground); letter-spacing: -0.3px; }
.brand-sub { font-size: 11px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; }

.section-label {
  font-size: 10px; font-weight: 700; color: var(--muted-foreground);
  letter-spacing: 0.08em; text-transform: uppercase; font-family: 'Nanum Gothic Coding', monospace;
  margin: 4px 0 10px;
}

.field-label { font-size: 12px; font-weight: 500; color: var(--foreground); margin-bottom: 4px; }

.kdri-box {
  background: var(--sage-pale); border-radius: 10px; padding: 12px 14px;
  border: 1px solid #C8D8C8; margin: 6px 0 4px;
}
.kdri-label { font-size: 11px; color: var(--sage); font-family: 'Nanum Gothic Coding', monospace; font-weight: 500; margin-bottom: 4px; }
.kdri-value { font-size: 22px; font-weight: 700; color: var(--sage); letter-spacing: -0.5px; }
.kdri-value span { font-size: 13px; font-weight: 500; }
.kdri-sub { font-size: 11px; color: var(--muted-foreground); margin-top: 2px; }

.validator-note {
  background: var(--amber-pale); border: 1px solid #F4C89A; border-radius: 10px;
  padding: 10px 12px; margin-bottom: 12px; font-size: 11px; color: #8B5E3C; line-height: 1.5;
}

.stat-card { background: var(--muted); border-radius: 10px; padding: 12px 12px 10px; margin-bottom: 10px; }
.stat-label { font-size: 10px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; margin-bottom: 4px; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--foreground); letter-spacing: -0.4px; }
.stat-value span { font-size: 11px; font-weight: 400; color: var(--muted-foreground); margin-left: 2px; }
.stat-bar-track { height: 3px; background: var(--border); border-radius: 99px; margin-top: 8px; overflow: hidden; }
.stat-bar-fill { height: 100%; border-radius: 99px; }

.profile-footer { display: flex; align-items: center; gap: 10px; padding-top: 4px; }
.profile-avatar {
  width: 32px; height: 32px; border-radius: 99px;
  background: linear-gradient(135deg, #8FAF8F, #5A7A5A);
  display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
}
.profile-name { font-size: 13px; font-weight: 600; color: var(--foreground); }
.profile-meta { font-size: 11px; color: var(--muted-foreground); }

/* ---------- Top bar ---------- */
.topbar-brand { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 6px 0; }
.status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 99px;
  background: #2D7A4F; box-shadow: 0 0 0 3px #C0E0CC;
}
.topbar-title { font-size: 14px; font-weight: 600; color: var(--foreground); }
.badge {
  padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 600;
  font-family: 'Nanum Gothic Coding', monospace;
}
.badge-sage { background: var(--sage-pale); color: var(--sage); }
.badge-amber { background: var(--amber-pale); color: var(--amber); }

/* ---------- Chat ---------- */
.agent-label {
  font-size: 11px; font-weight: 600; color: var(--sage);
  font-family: 'Nanum Gothic Coding', monospace; margin-bottom: 6px;
}

/* ---------- Cards (meal / danger / clarify / sodium) ---------- */
.na-card { background: var(--card); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; margin: 4px 0; }
.na-card-header {
  background: linear-gradient(135deg, #EBF0EB 0%, #F5F7F4 100%);
  padding: 16px 20px 14px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
}
.na-card-title { font-size: 15px; font-weight: 700; color: var(--foreground); letter-spacing: -0.3px; }
.na-card-subtitle { font-size: 11px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; }
.na-card-body { padding: 16px 20px 20px; }

.meal-item-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.meal-item-row {
  display: flex; align-items: center; gap: 10px; background: var(--muted);
  border-radius: 10px; padding: 8px 12px;
}
.meal-item-role {
  font-size: 10px; font-weight: 700; color: var(--sage); font-family: 'Nanum Gothic Coding', monospace;
  background: var(--sage-pale); border-radius: 6px; padding: 2px 8px; flex-shrink: 0;
}
.meal-item-name { font-size: 13px; font-weight: 600; color: var(--foreground); flex: 1; }
.meal-item-kcal { font-size: 12px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; flex-shrink: 0; }

.pass-badge {
  padding: 4px 12px; border-radius: 99px; background: var(--pass-pale); color: var(--pass);
  font-size: 12px; font-weight: 700; font-family: 'Nanum Gothic Coding', monospace; border: 1px solid #B8DCC8;
  margin-left: auto;
}

.nutri-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.nutri-cell { background: var(--muted); border-radius: 12px; padding: 12px; }
.nutri-cell-label { font-size: 10px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; font-weight: 500; margin-bottom: 6px; }
.nutri-cell-value { font-size: 20px; font-weight: 700; color: var(--foreground); letter-spacing: -0.5px; line-height: 1; }
.nutri-cell-value span { font-size: 11px; font-weight: 400; color: var(--muted-foreground); }
.nutri-cell-sub { font-size: 10px; color: var(--muted-foreground); margin: 3px 0 8px; }
.nutri-bar-track { height: 5px; background: var(--border); border-radius: 99px; overflow: hidden; }
.nutri-bar-fill { height: 100%; border-radius: 99px; }
.nutri-cell-status { font-size: 10px; font-weight: 600; font-family: 'Nanum Gothic Coding', monospace; margin-top: 5px; }

.macro-box { background: var(--muted); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 6px; }
.macro-box-title { font-size: 10px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; font-weight: 500; }
.macro-row-top { display: flex; justify-content: space-between; margin-bottom: 3px; }
.macro-name { font-size: 11px; font-weight: 600; color: var(--foreground); }
.macro-pct { font-size: 10px; color: var(--muted-foreground); font-family: 'Nanum Gothic Coding', monospace; }
.macro-bar-track { height: 4px; background: var(--border); border-radius: 99px; overflow: hidden; }
.macro-bar-fill { height: 100%; border-radius: 99px; }
.macro-box-foot { font-size: 9px; color: var(--muted-foreground); margin-top: 2px; }

.tag-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.tag-pill { padding: 4px 10px; border-radius: 99px; font-size: 11px; font-weight: 600; }

.na-divider { height: 1px; background: var(--border); margin: 0 0 14px; }

.info-section { margin-bottom: 12px; }
.info-title { font-size: 12px; font-weight: 700; color: var(--foreground); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.info-body { font-size: 12px; color: var(--muted-foreground); line-height: 1.6; }
.info-body ul { margin: 6px 0 0; padding-left: 16px; line-height: 1.7; }

.disclaimer-box {
  margin-top: 14px; padding: 10px 14px; background: var(--muted); border-radius: 8px;
  font-size: 11px; color: var(--muted-foreground); line-height: 1.5;
}

.alert-card-danger { border: 1.5px solid #F4A8A8; }
.alert-card-header-danger {
  background: var(--danger-pale); padding: 12px 16px; display: flex; gap: 10px;
  align-items: flex-start; border-bottom: 1px solid #F4A8A8;
}
.alert-title-danger { font-size: 13px; font-weight: 700; color: var(--danger); margin-bottom: 2px; }
.alert-body-danger { font-size: 12px; color: #B03030; line-height: 1.5; }

.alert-card-sodium { border: 1.5px solid #F4C89A; }
.alert-card-header-sodium {
  background: var(--amber-pale); padding: 12px 16px; display: flex; gap: 10px;
  align-items: flex-start; border-bottom: 1px solid #F4C89A;
}
.alert-title-sodium { font-size: 13px; font-weight: 700; color: var(--warning); }
.alert-body-sodium { font-size: 12px; color: #7A5520; line-height: 1.5; margin-top: 3px; }
.sodium-chip {
  padding: 2px 8px; border-radius: 99px; background: #FDE8C0; color: var(--warning);
  font-size: 10px; font-weight: 700; font-family: 'Nanum Gothic Coding', monospace;
}

.suggestion-row { display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 16px; }
.suggestion-chip {
  padding: 6px 12px; border-radius: 8px; border: 1.5px solid var(--border);
  background: var(--muted); color: var(--foreground); font-size: 12px; font-weight: 500;
  white-space: nowrap;
}
.suggestion-chip-sage {
  border: 1.5px solid var(--sage-light); background: var(--sage-pale); color: var(--sage);
  border-radius: 99px; font-weight: 600;
}
.suggestion-chip-amber {
  border: 1.5px solid #F4C89A; background: var(--amber-pale); color: #7A5520; font-weight: 600;
}
.suggestion-header { padding: 14px 16px 12px; border-bottom: 1px solid var(--border); }
.suggestion-header-title { font-size: 13px; font-weight: 600; color: var(--foreground); margin-bottom: 4px; }
.suggestion-header-sub { font-size: 12px; color: var(--muted-foreground); line-height: 1.6; }
.suggestion-lead { font-size: 11px; color: var(--muted-foreground); margin: 12px 16px 0; }

footer, #MainMenu { visibility: hidden; }
</style>
"""
