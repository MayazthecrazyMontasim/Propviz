# PropViz AI — Stitch Prompt

---

Build a web app called **PropViz AI** for a real estate company called **Win Win Properties**.
It generates AI-powered immersive video tours for off-plan apartment properties in Dhaka, Bangladesh.

---

## Design Style
- Clean, modern, professional
- Primary color: Amber/Gold (#F59E0B) — use for buttons, active states, progress bars
- Background: Light gray (#F9FAFB)
- Cards: White with subtle border and shadow
- Font: Inter
- Fully responsive (mobile + desktop)

---

## Pages

### 1. Landing Page ( / )
- Hero section: headline "Turn Floor Plans Into Immersive Tours"
- Subheadline: "Upload a floor plan and brochure — PropViz AI generates a 90-second video tour your buyers can watch from home."
- Two CTA buttons: "Create First Tour" (primary, gold) → links to /upload, "View Dashboard" (secondary) → links to /dashboard
- Simple, clean. No images needed.

---

### 2. Upload Page ( /upload )
Multi-step wizard with 4 steps shown as a progress stepper at the top.

**Step 1 — Property Details (form)**
Fields:
- Property Name (required) — text input
- Developer — text input
- Location — text input
- Unit Type — text input (e.g. "Type A")
- Area in sqft — number input
- Price Range — text input (e.g. "80–90 lakh BDT")
- Submit button: "Create Job" → calls POST /api/v1/jobs/ with { property: { name, developer, location, unit_type, area_sqft, price_range } }
- On success: saves job_id, moves to Step 2

**Step 2 — Upload Files**
- Three tab buttons at top: "Floor Plan", "Brochure", "Photos"
- Drag-and-drop upload zone for each tab
- Accepted formats shown under each zone
- File list below showing upload progress bar per file
- Each file calls POST /api/v1/assets/upload (multipart form: job_id, asset_type, file)
- "Generate Tour" button at bottom → calls POST /api/v1/jobs/{job_id}/start → moves to Step 3

**Step 3 — Processing**
- Shows job status polled every 3 seconds from GET /api/v1/jobs/{job_id}
- Large animated progress bar (gold color)
- Stage label below bar: "Validating files" / "Extracting floor plan" / "Generating renders" / "Creating narration" / "Assembling video"
- Status badge (pill): pending / processing / complete / failed
- Percentage number
- On complete: auto-moves to Step 4

**Step 4 — Done**
- Green checkmark icon
- "Your tour is ready!" heading
- Two buttons: "Open Viewer" → /viewer/{job_id}, "Go to Dashboard" → /dashboard

---

### 3. Viewer Page ( /viewer/[id] )
- Polls GET /api/v1/jobs/{id} on load
- If status is complete:
  - Full-width video player (16:9) with native controls
  - Below video: property name + location in large text
  - Right side card (or below on mobile): 
    - "Ready to see it in person?" heading
    - Short paragraph: "You've seen the space virtually. Book a site visit and confirm with your own eyes."
    - Green WhatsApp button: "Book Site Visit" → opens wa.me link
    - "Share this tour" button → copies current URL to clipboard
- If status is not complete:
  - Centered loading spinner
  - "Generating your tour…" text
  - Progress bar + stage label
  - Percentage

---

### 4. Dashboard Page ( /dashboard )
- Header row: "Dashboard" title on left, "+ New Tour" gold button on right → links to /upload
- Stats row: 4 cards — Total Jobs, Complete (green number), Processing (blue number), Failed (red number)
- Jobs table below:
  - Columns: Property Name, Status (colored pill badge), Progress (mini progress bar + %), Action
  - Status colors: pending=gray, ingesting/parsing/reconstructing/synthesizing/postprocessing=blue, complete=green, failed=red
  - Action column: "View Tour" link for complete jobs, "Monitor" link for others → both go to /viewer/{id}
  - Loads from GET /api/v1/jobs/
  - Empty state: "No tours yet. Create your first tour." with link to /upload

---

## Auth
- All API calls include header: Authorization: Bearer {token}
- Token stored in localStorage as "propviz_token"
- Login page ( /login ): email + password form → POST /api/v1/auth/token (OAuth2 form: username, password) → store token → redirect to /dashboard
- If any API call returns 401 → redirect to /login
- No register page needed in UI (admin creates users manually)

---

## Shared Components
- Top navbar: "PropViz AI" logo (gold text) on left, nav links "New Tour" and "Dashboard" on right, logout icon far right
- All pages except login show the navbar
- API base URL from env var: NEXT_PUBLIC_API_URL (default: http://localhost:8000/api/v1)

---

## Tech Stack
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- No external UI libraries — pure Tailwind only
