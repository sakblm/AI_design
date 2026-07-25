# Wireframe implementation choice

## Default: vanilla HTML, CSS, and JavaScript

Use the bundled kit when the prototype needs:

- Screen and direction comparison
- Tabs, accordions, drawers, dialogs, toasts, and simple navigation
- A few forms or local UI states
- Responsive layouts
- Static or small synthetic datasets
- Review annotations and rationale

Visual quality does not depend on React. Typography, hierarchy, spacing, color, responsive behavior, and motion can reach the same fidelity with either approach.

## Escalate to a framework prototype

Use React or the product's existing framework when the prototype needs:

- Many interdependent states
- Complex validation or multi-step forms
- Client-side routing across many views
- Repeated components backed by large datasets
- API integration and optimistic updates
- Authentication or role-based behavior
- Direct reuse in an existing production codebase
- Automated component-level regression tests

Document why the added runtime and build complexity is necessary. Do not migrate merely because React is familiar.

