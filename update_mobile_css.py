import re

with open('frontend/src/App.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the old mobile block
old_block = '''@media (max-width: 768px) {
  .cp-row-1 {
    grid-template-columns: 1fr;
  }
  .cp-aqi-card {
    min-height: 100px;
  }
}'''
if old_block in text:
    text = text.replace(old_block, '')

# Append new mobile block
mobile_css = '''
/* ==========================================================================
   MOBILE RESPONSIVENESS (<= 768px)
   ========================================================================== */
@media (max-width: 768px) {
  /* Shell & Sidebar -> Bottom Tab Bar */
  .app-shell {
    flex-direction: column-reverse; /* Sidebar at bottom */
  }

  .sidebar {
    width: 100% !important;
    height: 70px;
    flex-direction: row;
    padding: 0 8px;
    justify-content: space-around;
    align-items: center;
    border-right: none;
    border-top: 1px solid var(--border-color);
  }

  .sidebar-brand, 
  .sidebar > div > button {
    display: none !important; /* Hide brand and explicit collapse button on mobile */
  }

  .sidebar-nav {
    flex-direction: row;
    width: 100%;
    justify-content: space-around;
    margin: 0;
  }

  .nav-item {
    flex-direction: column;
    padding: 6px;
    gap: 4px;
    justify-content: center;
    align-items: center;
    min-width: 0;
    margin: 0;
  }

  .nav-item.theme-toggle {
    margin: 0 !important; /* override inline styles */
  }

  .nav-item span {
    font-size: 0.65rem !important;
    display: block !important; /* ensure small text shows */
    margin: 0 !important;
  }

  .app-right {
    height: calc(100vh - 70px);
    width: 100vw;
  }

  .global-header {
    height: auto;
    flex-direction: column;
    padding: 12px 16px;
    gap: 12px;
  }

  .header-search-container {
    width: 100%;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  /* Page Padding */
  .dashboard-page, 
  .city-page-container {
    padding: 16px;
  }

  /* Dashboard specific */
  .dashboard-row-1 {
    grid-template-columns: 1fr;
  }

  .dashboard-row-2 {
    grid-template-columns: 1fr;
  }

  .dashboard-row-3 {
    grid-template-columns: 1fr;
  }
  
  .dashboard-row-3 > *:last-child {
    grid-column: 1; /* Reset span 2 from tablet */
  }

  .scp-grid-3 {
    grid-template-columns: 1fr;
  }

  .scp-grid-3 > *:last-child {
    grid-column: 1;
  }

  /* City Page specific */
  .cp-row-1 {
    grid-template-columns: 1fr;
  }
  .cp-aqi-card {
    min-height: 100px;
  }
  .cp-row-2, .cp-row-3 {
    grid-template-columns: 1fr;
  }
}
'''
with open('frontend/src/App.css', 'w', encoding='utf-8') as f:
    f.write(text + mobile_css)
