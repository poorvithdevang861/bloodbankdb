# Blood Bank UI Redesign - Soft Paper Skeuomorphic Style

## Goal

Improve the current HTML template UI into a medium skeuomorphic style with minimal color usage.

The new visual direction should:
- feel cleaner and more modern than the current basic red-heavy styling
- introduce clear depth through raised cards/buttons and inset inputs
- keep readability high for data-entry and table-heavy screens
- use mostly off-white and gray tones, with very limited red highlights

## Scope

Apply the redesign consistently to all existing templates:
- `templates/login.html`
- `templates/index.html`
- `templates/add_donor.html`
- `templates/view_donors.html`
- `templates/add_request.html`
- `templates/view_requests.html`
- `templates/stock.html`

No backend behavior changes are included.

## Chosen Direction

The approved direction is **A - Soft Paper**:
- off-white page background and layered gray surfaces
- medium-depth card and button elevation
- inset input fields
- tiny deep-red accents for important interactive emphasis

## Visual System

### Color Palette

Primary neutrals:
- page background: `#f5f5f3`
- card surface: `#ecece8`
- soft border: `#d4d4cf`
- primary text: `#2f2f2c`
- secondary text: `#5a5a56`

Accent (sparingly used):
- red accent: `#8b1f1f`
- red hover: `#7a1b1b`

Usage rules:
- red is reserved for primary action buttons, focus ring accent, and small heading markers
- most component surfaces remain neutral

### Typography

- system font stack for clean rendering: Arial/Helvetica/sans-serif
- clear heading hierarchy (`h1`, `h2`)
- compact but readable form and table text

### Depth Language

Use medium skeuomorphic depth:
- raised cards: dual outer shadow (soft top-left highlight + deeper bottom-right shadow)
- raised buttons: visible elevation at rest, subtle press effect on active
- inset inputs: inner shadow to create pressed-in field appearance

This depth should be present but subtle to keep the interface minimal.

## Layout and Component Design

### Shared Page Structure

- center content in a constrained container (`max-width` based on page type)
- maintain generous spacing between sections
- present each page's core content inside a main "surface card"

### Login Page

- centered login card with raised soft-paper effect
- understated title and form layout
- inset username/password fields
- one primary red login button

### Dashboard (`index.html`)

- raised main panel with title and action links
- action links styled as tactile button blocks (not plain links)
- maintain role-based options exactly as today

### Form Pages (`add_donor.html`, `add_request.html`)

- convert label/input rows into consistent stacked form layout
- use inset inputs and raised submit button
- include a calm secondary "Back" control style

### Table Pages (`view_donors.html`, `view_requests.html`, `stock.html`)

- wrap tables inside raised card containers
- remove default HTML `border="1"` look and replace with CSS table styling
- soft row separators and subtle header background contrast
- action links (Delete/Process) shown as compact tactile controls

## Interaction States

- hover: slight luminance change only, no aggressive color shift
- active: shallow pressed effect (`transform` + reduced shadow)
- focus: neutral ring with tiny red accent edge for clarity/accessibility

## Data Flow and Logic Impact

No data flow or business logic changes.
Jinja templating logic and backend routes remain unchanged.

## Error Handling

No new runtime error handling paths are introduced.
Current form submission behavior remains as-is.

## Testing Plan

Manual verification:
- open each route and confirm style consistency
- verify role-based conditional rendering still works on dashboard
- submit donor/request forms to ensure markup changes did not break POST behavior
- confirm table data renders correctly and action links still function
- verify hover/focus/active states on keyboard and mouse interaction

## Risks and Mitigations

- Risk: style duplication across templates can drift over time.
  - Mitigation: use a shared CSS block pattern repeated consistently for now (future step: extract shared stylesheet).
- Risk: overly strong shadows can reduce readability.
  - Mitigation: keep shadow spread and opacity restrained.

## Out of Scope

- redesigning information architecture or route structure
- adding dark mode or theme switching
- backend/database changes
