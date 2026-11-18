"""
PDF Master Pro - Visual Theme & Stylesheet (Dark & Light Modes)
Strictly adheres to:
- Navy: #172536
- Deep Blue: #24374D
- Teal: #278B91
- Gold: #E5A63B
- Background: #F3F5F8 (Light) / #101924 (Dark)
- White: #FFFFFF
"""

DARK_THEME_QSS = """
/* Global Application Style */
QWidget {
    background-color: #101924;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Cairo', 'Tahoma', 'Arial', sans-serif;
    font-size: 13px;
    selection-background-color: #0D74CE;
    selection-color: #FFFFFF;
}

/* Header & Top Bar */
#HeaderBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #172536, stop:1 #24374D);
    border-bottom: 1px solid #2B3D52;
}

#AppTitleBadge {
    background-color: #E11D48;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border-radius: 6px;
    padding: 3px 8px;
}

#AppTitleLabel {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
}

#AppEditionLabel {
    color: #E5A63B;
    font-size: 14px;
    font-weight: 600;
}

/* Top Action Toolbar */
#TopToolBar {
    background-color: #172536;
    border-bottom: 1px solid #24374D;
    padding: 4px;
}

QPushButton {
    background-color: #24374D;
    color: #E2E8F0;
    border: 1px solid #334B66;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2D445F;
    border-color: #0D74CE;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #1B2B3E;
}

/* Primary Action Buttons (e.g. Open File, Compress) */
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D74CE, stop:1 #0A5BA2);
    color: #FFFFFF;
    border: 1px solid #1E88E5;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    padding: 8px 18px;
}

QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E88E5, stop:1 #0D74CE);
    border-color: #60A5FA;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #09477F;
}

/* Big Action Button (Reference Start Compression) */
QPushButton#BigActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D74CE, stop:1 #278B91);
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    border-radius: 10px;
    border: 1px solid #38BDF8;
    padding: 12px 20px;
}

QPushButton#BigActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E88E5, stop:1 #2DD4BF);
}

/* Sidebar Menu */
#Sidebar {
    background-color: #172536;
    border-right: 1px solid #24374D;
}

QListWidget#SidebarList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#SidebarList::item {
    color: #CBD5E1;
    height: 42px;
    padding-left: 12px;
    padding-right: 12px;
    margin: 2px 6px;
    border-radius: 8px;
    font-weight: 500;
}

QListWidget#SidebarList::item:hover {
    background-color: #24374D;
    color: #FFFFFF;
}

QListWidget#SidebarList::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D74CE, stop:1 #278B91);
    color: #FFFFFF;
    font-weight: bold;
}

/* Right Tool Properties Panel */
#PropertiesPanel {
    background-color: #172536;
    border-left: 1px solid #24374D;
    border-radius: 10px;
}

#PropertiesPanelTitle {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
}

/* Compression Level Cards */
QFrame#CompCard {
    background-color: #24374D;
    border: 2px solid #334B66;
    border-radius: 10px;
    padding: 8px;
}

QFrame#CompCard:hover {
    border-color: #278B91;
    background-color: #2A4059;
}

QFrame#CompCard[selected="true"] {
    background-color: #1A3450;
    border: 2px solid #0D74CE;
}

/* Stats Box (Light blue box in reference) */
QFrame#StatsBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E3A5F, stop:1 #172E4C);
    border: 1px solid #2A4E78;
    border-radius: 10px;
    padding: 12px;
}

QFrame#StatsBox QLabel {
    background: transparent;
}

/* Bottom Status Bar */
#BottomStatusBar {
    background-color: #172536;
    border-top: 1px solid #24374D;
    min-height: 38px;
}

#StatusBadge {
    background-color: #064E3B;
    color: #34D399;
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: bold;
}

/* Progress Bar */
QProgressBar {
    background-color: #24374D;
    border: 1px solid #334B66;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #278B91, stop:1 #22C55E);
    border-radius: 5px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #E2E8F0;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #4B6382;
    background-color: #24374D;
}

QCheckBox::indicator:hover {
    border-color: #0D74CE;
}

QCheckBox::indicator:checked {
    background-color: #0D74CE;
    border-color: #60A5FA;
    image: none; /* Drawn or checked cleanly */
}

/* Input Fields and Combos */
QLineEdit, QSpinBox, QComboBox {
    background-color: #24374D;
    border: 1px solid #334B66;
    border-radius: 6px;
    color: #FFFFFF;
    padding: 6px 10px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #0D74CE;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* Document Tab Bar */
QTabBar::tab {
    background-color: #1C2B3C;
    color: #94A3B8;
    border: 1px solid #2B3D52;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 16px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #172536;
    color: #FFFFFF;
    border-top: 2px solid #0D74CE;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #172536;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334B66;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4B6B91;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

LIGHT_THEME_QSS = """
QWidget {
    background-color: #F3F5F8;
    color: #1E293B;
    font-family: 'Segoe UI', 'Cairo', 'Tahoma', 'Arial', sans-serif;
    font-size: 13px;
    selection-background-color: #0D74CE;
    selection-color: #FFFFFF;
}

#HeaderBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFFFF, stop:1 #E2E8F0);
    border-bottom: 1px solid #CBD5E1;
}

#AppTitleBadge {
    background-color: #E11D48;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border-radius: 6px;
    padding: 3px 8px;
}

#AppTitleLabel {
    color: #0F172A;
    font-size: 16px;
    font-weight: 700;
}

#AppEditionLabel {
    color: #D97706;
    font-size: 14px;
    font-weight: 600;
}

#TopToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 4px;
}

QPushButton {
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F1F5F9;
    border-color: #0D74CE;
}

QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D74CE, stop:1 #0A5BA2);
    color: #FFFFFF;
    border: 1px solid #0D74CE;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    padding: 8px 18px;
}

QPushButton#BigActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D74CE, stop:1 #278B91);
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    padding: 12px 20px;
}

#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

QListWidget#SidebarList::item {
    color: #475569;
    height: 42px;
    padding-left: 12px;
    padding-right: 12px;
    margin: 2px 6px;
    border-radius: 8px;
    font-weight: 500;
}

QListWidget#SidebarList::item:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QListWidget#SidebarList::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D74CE, stop:1 #278B91);
    color: #FFFFFF;
    font-weight: bold;
}

#PropertiesPanel {
    background-color: #FFFFFF;
    border-left: 1px solid #E2E8F0;
    border-radius: 10px;
}

#PropertiesPanelTitle {
    color: #0F172A;
    font-size: 15px;
    font-weight: bold;
}

QFrame#CompCard {
    background-color: #F8FAFC;
    border: 2px solid #E2E8F0;
    border-radius: 10px;
    padding: 8px;
}

QFrame#CompCard:hover {
    border-color: #278B91;
    background-color: #F1F5F9;
}

QFrame#CompCard[selected="true"] {
    background-color: #EFF6FF;
    border: 2px solid #0D74CE;
}

QFrame#StatsBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E0F2FE, stop:1 #BAE6FD);
    border: 1px solid #7DD3FC;
    border-radius: 10px;
    padding: 12px;
    color: #0369A1;
}

#BottomStatusBar {
    background-color: #FFFFFF;
    border-top: 1px solid #E2E8F0;
    min-height: 38px;
}

#StatusBadge {
    background-color: #DCFCE7;
    color: #16A34A;
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: bold;
}

QProgressBar {
    background-color: #E2E8F0;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #278B91, stop:1 #22C55E);
    border-radius: 5px;
}
"""

def get_stylesheet(theme: str = "dark") -> str:
    if theme == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
