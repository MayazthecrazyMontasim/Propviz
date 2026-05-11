---
name: PropViz AI
colors:
  surface: '#fff8f4'
  surface-dim: '#e7d7c9'
  surface-bright: '#fff8f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff1e5'
  surface-container: '#fbebdd'
  surface-container-high: '#f5e6d7'
  surface-container-highest: '#f0e0d1'
  on-surface: '#221a12'
  on-surface-variant: '#534434'
  inverse-surface: '#382f25'
  inverse-on-surface: '#feeedf'
  outline: '#867461'
  outline-variant: '#d8c3ad'
  surface-tint: '#855300'
  primary: '#855300'
  on-primary: '#ffffff'
  primary-container: '#f59e0b'
  on-primary-container: '#613b00'
  inverse-primary: '#ffb95f'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#00658b'
  on-tertiary: '#ffffff'
  tertiary-container: '#1abdff'
  on-tertiary-container: '#004966'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffddb8'
  primary-fixed-dim: '#ffb95f'
  on-primary-fixed: '#2a1700'
  on-primary-fixed-variant: '#653e00'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#c5e7ff'
  tertiary-fixed-dim: '#7fd0ff'
  on-tertiary-fixed: '#001e2d'
  on-tertiary-fixed-variant: '#004c6a'
  background: '#fff8f4'
  on-background: '#221a12'
  surface-variant: '#f0e0d1'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
---

## Brand & Style

The design system is engineered for PropViz AI, a real estate technology platform that bridges the gap between complex data and actionable insights. The brand personality is professional, authoritative, and forward-thinking. It avoids the coldness of traditional enterprise software by utilizing warm gold accents to signify value and progress.

The visual style follows a **Corporate Modern** aesthetic. It prioritizes clarity and high signal-to-noise ratios, utilizing significant whitespace to reduce cognitive load for users analyzing property data. The UI should evoke a sense of precision and reliability, making the user feel empowered by technology rather than overwhelmed by it.

## Colors

The palette is anchored by a high-contrast relationship between a sophisticated Amber/Gold and a neutral, cool-toned foundation.

- **Primary (Gold):** Used exclusively for high-priority actions, active navigation states, and progress indicators. This color represents the "premium" nature of the insights provided.
- **Success (Green):** Reserved for WhatsApp integrations and "Complete" statuses, providing a clear semantic distinction from the gold primary actions.
- **Neutrals:** A light gray background ensures the pure white surfaces (cards and sections) pop, creating a clear sense of layering. Slate grays are used for typography to ensure maximum legibility without the harshness of pure black.

## Typography

This design system utilizes **Inter** for all typographic roles. Inter’s tall x-height and neutral character make it ideal for data-heavy real estate interfaces. 

- **Headlines:** Use tighter letter-spacing and semi-bold weights to create a strong visual anchor.
- **Body Text:** Maintain a generous line height (1.5 - 1.6) to ensure readability during long research sessions.
- **Labels:** Small labels and pill text should use a slightly heavier weight (Medium or Semi-bold) to maintain legibility against colored backgrounds.

## Layout & Spacing

The layout philosophy is based on a **Fixed Grid** model for desktop to maintain a premium, editorial feel, transitioning to a fluid model for mobile devices. 

A strict 8px spacing scale governs all margins and paddings, ensuring mathematical harmony across components.
- **Desktop:** 12-column grid with a 1280px max-width container.
- **Mobile:** 4-column grid with 16px side margins. 
- **Reflow Rules:** Cards should stack vertically on mobile. Navigation transitions from a slim horizontal bar to a slide-out drawer or bottom-tab bar for easier thumb reach.

## Elevation & Depth

To maintain a "trustworthy" and "clean" feel, depth is created through **Ambient Shadows** and tonal layering rather than heavy borders.

- **Level 0 (Background):** #F9FAFB. Used for the base canvas.
- **Level 1 (Surface):** #FFFFFF. Used for the main content cards. These feature a `0px 4px 6px -1px rgba(0, 0, 0, 0.05)` shadow to lift them slightly from the background.
- **Level 2 (Interactive):** Elements like dropdowns or hovered cards use a more pronounced shadow: `0px 10px 15px -3px rgba(0, 0, 0, 0.1)`.
- **Outlines:** Use subtle 1px borders in #E5E7EB for secondary elements to provide structure without adding visual weight.

## Shapes

The shape language is "Rounded," striking a balance between the clinical sharpness of legacy finance tools and the overly bubbly nature of consumer social apps.

- **Cards & Sections:** Use `rounded-lg` (16px) to soften the layout and make the interface feel modern and accessible.
- **Buttons:** Use a moderate 8px radius to maintain a professional look.
- **Status Badges:** Use a full "Pill" radius (9999px) to clearly distinguish them from interactive buttons or input fields.

## Components

### Buttons
- **Primary:** Solid Gold (#F59E0B) fill with Pure White text. Apply a subtle scale-down effect (0.98) on click.
- **Secondary:** Outlined with a 1px border (#E5E7EB) and Slate text. Background shifts to a faint gray on hover.
- **WhatsApp:** Solid Green (#10B981) with White text and a brand-specific icon.

### Navigation Bar
- **Style:** Slim (64px height), Pure White background, and a 1px bottom border (#E5E7EB).
- **Links:** Use `label-md` typography. The active state is indicated by a 2px Gold underline or Gold text color.

### Status Badges
- **Pill-shaped:** Use a light tinted background (e.g., 10% opacity of the status color) with high-contrast text for "Pending" or "Complete" states.

### Cards
- **Structure:** White background, 16px border radius, and the Level 1 ambient shadow. Padding should be a minimum of 24px to allow data to "breathe."

### Input Fields
- **Default:** White background, 1px Gray border, 8px radius. 
- **Active/Focus:** Border changes to Gold with a soft 2px Gold outer glow (20% opacity).