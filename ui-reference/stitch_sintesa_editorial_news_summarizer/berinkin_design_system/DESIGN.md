---
name: Berinkin Design System
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#404944'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#707974'
  outline-variant: '#bfc9c3'
  surface-tint: '#2b6954'
  primary: '#003527'
  on-primary: '#ffffff'
  primary-container: '#064e3b'
  on-primary-container: '#80bea6'
  inverse-primary: '#95d3ba'
  secondary: '#735c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed65b'
  on-secondary-container: '#745c00'
  tertiary: '#17341e'
  on-tertiary: '#ffffff'
  tertiary-container: '#2d4b33'
  on-tertiary-container: '#99ba9b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b0f0d6'
  primary-fixed-dim: '#95d3ba'
  on-primary-fixed: '#002117'
  on-primary-fixed-variant: '#0b513d'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#c8ebca'
  tertiary-fixed-dim: '#adcfaf'
  on-tertiary-fixed: '#03210c'
  on-tertiary-fixed-variant: '#304d35'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
typography:
  display-xl:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '300'
    lineHeight: '1.6'
    letterSpacing: 0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.1em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin: 40px
  container-max: 1200px
---

## Brand & Style

This design system centers on the **Banyan Tree Metaphor (Convergence)**, representing the gathering of fragmented information into a single, authoritative trunk of knowledge. The visual language is defined as **Luxury Editorial**, catering to an audience that values time, precision, and intellectual clarity.

The aesthetic blends the timelessness of high-end print journalism with modern digital surfacing. It utilizes a **Minimalist-Glassmorphic** style: clean layouts and heavy whitespace are accented by translucent layers that suggest depth without clutter. To reinforce the concept of an information network, the design system employs thin 0.5pt strokes and "nodes" (small solid squares) at the intersections of card corners, symbolizing the structural points where data converges.

## Colors

The palette is rooted in nature and prestige. **Deep Forest Green** serves as the primary anchor, used for high-importance interactions and brand marks to evoke stability and growth. **Gold Mist** provides a sophisticated secondary accent for highlights, active states, and editorial "crown" elements.

The background strategy utilizes **Premium Off-white** for the main canvas to reduce eye strain, while **Pure White** is reserved for elevated glass cards to create a subtle, shimmering contrast. Text is rendered in a deep off-black to maintain high legibility while appearing softer than pure black.

## Typography

The typography strategy creates a tension between the traditional and the technical. **Newsreader** is used for headlines to establish a "rooted" and authoritative editorial voice; its serif terminals provide a literary quality essential for a premium news summarizer.

**Inter** is utilized for body copy and UI labels, set primarily in light and regular weights. To enhance the luxury feel, body text uses generous kerning (letter-spacing) to ensure "air" between characters. Labels are consistently set in uppercase with increased tracking to function as precise navigational markers.

## Layout & Spacing

The layout follows a **Fixed Editorial Grid** inspired by high-fashion broadsheets. On desktop, a 12-column grid is used with wide 40px margins to frame the content as a curated gallery. 

The spacing rhythm is strictly based on a 4px baseline, with a preference for large, "intentional" gaps between sections to allow the user's mind to rest. Vertical rhythm is prioritized, with summary blocks separated by wide gutters to emphasize the "distilled" nature of the content.

## Elevation & Depth

This design system eschews traditional heavy shadows in favor of **Tonal Layering and Glassmorphism**. Hierarchy is established through transparency and blur:

1.  **Level 0 (Base):** Premium Off-white (#FAF9F6) solid surface.
2.  **Level 1 (Cards):** Pure White (#FFFFFF) with 80% opacity and a `backdrop-filter: blur(12px)`.
3.  **Level 2 (Overlays):** Deep Forest Green with 95% opacity for critical modals.

Depth is further defined by **thin 0.5px outlines** in a slightly darker neutral shade. These outlines give the glass surfaces a crisp, "cut-glass" edge. No ambient shadows are used; instead, depth is felt through the subtle color shifts of the blurred background appearing through the UI elements.

## Shapes

The shape language is architectural and precise. A **Soft (0.25rem)** roundedness is applied to standard UI elements like input fields and buttons to prevent the interface from feeling sharp or aggressive.

However, the defining characteristic is the **Network Node**. At the corners of summary cards and primary containers, a 4px x 4px solid square "node" is placed at the intersection of the borders. This geometric detail serves as a visual metaphor for the Banyan tree's roots—points of connection and grounding.

## Components

### Buttons
Primary buttons use the **Deep Forest Green** background with white text, using a "pill-rectangle" hybrid shape (Soft rounding). Secondary buttons use a ghost style with a thin Gold Mist outline. All button text is uppercase Inter with 0.1em letter spacing.

### News Cards
The signature component of this design system. Cards are Pure White with 80% opacity and backdrop blur. They feature a 0.5px border and the signature **Network Nodes** at all four corners. Headlines within cards use Newsreader Medium.

### Summarization Progress
A thin, 2px horizontal bar in **Gold Mist** that moves across the top of a news summary as the user scrolls, representing the "convergence" of the story.

### Chips & Tags
Tags are styled as small, text-only elements with a Deep Forest Green left-border accent. They do not use background fills, maintaining the "clean editorial" aesthetic.

### Input Fields
Inputs are minimal, consisting only of a bottom border in Sage Green. When focused, the border transitions to Deep Forest Green, and the label floats upward in Gold Mist.