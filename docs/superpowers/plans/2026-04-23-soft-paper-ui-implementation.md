# Soft Paper UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply a consistent medium-skeuomorphic "Soft Paper" UI across all templates using neutral colors and tiny red accents without changing backend behavior.

**Architecture:** Keep each template self-contained with embedded CSS but align all pages to one shared visual language (surfaces, controls, spacing, depth, and table treatment). Preserve all existing Jinja logic, form actions, and links; only structure and style are changed. Use one pass for core shells (document structure and shared classes), then targeted adjustments for forms and data tables.

**Tech Stack:** Flask/Jinja templates, HTML, inline CSS

---

### Task 1: Build Shared Soft-Paper Structure Across All Templates

**Files:**
- Modify: `templates/login.html`
- Modify: `templates/index.html`
- Modify: `templates/add_donor.html`
- Modify: `templates/view_donors.html`
- Modify: `templates/add_request.html`
- Modify: `templates/view_requests.html`
- Modify: `templates/stock.html`

- [ ] **Step 1: Create consistent HTML document shell where missing**

Add `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` wrappers to templates currently missing full document structure (`add_donor`, `view_donors`, `add_request`, `view_requests`, `stock`) while preserving existing Jinja blocks and links.

- [ ] **Step 2: Add shared Soft-Paper visual tokens and primitives**

Embed a unified CSS system in each template with:
- neutral palette tokens (`#f5f5f3`, `#ecece8`, `#d4d4cf`, `#2f2f2c`, `#5a5a56`)
- minimal red accent tokens (`#8b1f1f`, `#7a1b1b`)
- raised surface/card shadows
- raised button style + pressed state
- inset inputs with focused accent ring

- [ ] **Step 3: Add page-level layout containers**

Standardize with `.page`, `.surface`, and constrained widths:
- login: narrow centered card
- dashboard: medium action card
- forms/tables: wider content surface

- [ ] **Step 4: Run a basic syntax sanity check**

Run: `python -m py_compile app.py`  
Expected: no errors (backend untouched but ensures project remains runnable)

---

### Task 2: Refine Form and Navigation Components

**Files:**
- Modify: `templates/login.html`
- Modify: `templates/index.html`
- Modify: `templates/add_donor.html`
- Modify: `templates/add_request.html`

- [ ] **Step 1: Convert form rows to structured labels and fields**

For add forms:
- replace inline `Label: <input>` rows with grouped blocks (`.field`, `<label>`, `<input>`)
- keep current `name` attributes exactly unchanged
- keep submit buttons and back navigation routes unchanged

- [ ] **Step 2: Restyle dashboard links as tactile controls**

In `index.html`, style role-based links as block buttons with subtle depth and tiny red accents on hover/focus; keep existing conditional Jinja logic exactly as-is.

- [ ] **Step 3: Add secondary "Back" control style**

Create low-emphasis neutral back buttons for form pages to reduce red usage while keeping clear navigation affordance.

- [ ] **Step 4: Manual behavior check**

Run app and verify:
- login submits
- staff/doctor role cards render the same links as before
- add form submits still post to existing endpoints

---

### Task 3: Refine Data Tables and Action Links

**Files:**
- Modify: `templates/view_donors.html`
- Modify: `templates/view_requests.html`
- Modify: `templates/stock.html`

- [ ] **Step 1: Replace legacy table borders with CSS table system**

Remove `border="1"` and introduce:
- subtle header background
- soft row separators
- consistent cell padding and typography
- responsive overflow handling if needed

- [ ] **Step 2: Style action links as compact tactile controls**

Convert `Delete` and `Process` links to compact button-like controls with minimal red accents for emphasis while maintaining exact href routes.

- [ ] **Step 3: Final visual consistency pass**

Check all templates for:
- consistent spacing scale
- consistent shadow language
- consistent interaction states (`hover`, `focus`, `active`)

- [ ] **Step 4: Lightweight verification commands**

Run: `python -m py_compile app.py`  
Expected: no errors  

Run: `python app.py` and spot-check main routes in browser  
Expected: pages load, forms/actions remain functional, style appears as approved

