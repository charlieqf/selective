# Mobile Experience Optimization Proposal

Based on the current codebase analysis, the following improvements are proposed to enhance the mobile user experience for Selective Prep.

## 0. Immediate Fixes (Implemented in Current Sprint)

### Question List: Filters Layout
**Problem**:
-   **"Needs Review" Checkbox**: Misaligned and takes up too much horizontal space on mobile.
-   **Dropdowns**: Options text is truncated because 3 dropdowns are squeezed into one row.

**Solution**:
-   **Stacked Dropdowns**: On mobile, stack the 3 dropdowns vertically (one per row) to ensure full width for text visibility.
-   **Vertical Checkbox**: Place the "Needs Review" checkbox on the right side with vertical text orientation (`writing-mode: vertical-rl`) to save horizontal space while remaining accessible.

### Question Detail: Action Buttons
**Problem**:
-   The row of buttons (Back, Mark for Review, Edit, Delete) is crowded and misaligned on mobile screens.

**Solution**:
-   **Responsive Button Styles**:
    -   **Mobile**: Display **Icon Only** for all buttons to fit them in a single row.
    -   **Desktop**: Maintain **Icon + Text** for clarity.

## 1. Floating Action Button (FAB) or Bottom Bar for Primary Actions

**Problem**: The "Upload Question" button is located in the header or top bar. On tall mobile screens, this area is hard to reach with one hand.

**Proposed Solution**:
Implement a **Floating Action Button (FAB)** fixed at the bottom-right corner of the screen for the primary action (Upload).

**Design**:
-   **Position**: Fixed, `bottom-6`, `right-6`.
-   **Icon**: Large `+` icon.
-   **Behavior**:
    -   On scroll down: Optionally hide or shrink to mini-FAB.
    -   On scroll up: Show full FAB.
    -   *Note*: Ensure `bottom` spacing respects `safe-area-inset-bottom` on iOS (e.g., `bottom: calc(1.5rem + env(safe-area-inset-bottom))`).

```vue
<!-- FAB Example -->
<n-button
  circle
  type="primary"
  size="large"
  class="fixed bottom-6 right-6 shadow-lg z-50 w-14 h-14"
  @click="router.push('/questions/upload')"
>
  <template #icon>
    <n-icon size="24"><Add /></n-icon>
  </template>
</n-button>
```

**Alternative**: A fixed **Bottom App Bar** containing primary navigation and the main action button in the center (dock style), similar to Instagram/popular apps.

## 2. Collapsible Filter Drawer

**Problem**: The `QuestionFilters` component currently stacks 3-4 dropdowns vertically on mobile. This pushes the actual content (questions) far down the screen, requiring users to scroll just to see the first item.

**Proposed Solution**:
Move filters into a **Side Drawer (Off-canvas)** or a **Bottom Sheet**.

**Design**:
-   **UI Change**: Replace the stacked dropdowns with a single "Filter & Sort" button (with an indicator badge if filters are active).
-   **Interaction**: A specific "Filter" button opens an `<n-drawer>` or modal.
-   **Drawer Content**:
    -   Collection/Subject Select
    -   Difficulty Select
    -   Status Select
    -   "Needs Review" Toggle
    -   "Apply Filters" Button (sticky at bottom)

```vue
<!-- Mobile Filter Concept -->
<div class="md:hidden flex justify-between items-center mb-4">
  <span class="font-bold">Questions</span>
  <n-button ghost @click="showFilterDrawer = true">
    <template #icon><FilterIcon /></template>
    Filters {{ activeFilterCount > 0 ? `(${activeFilterCount})` : '' }}
  </n-button>
</div>

<n-drawer v-model:show="showFilterDrawer" placement="right" width="85%">
  <n-drawer-content title="Filter Questions">
    <!-- Filter Controls Here -->
  </n-drawer-content>
</n-drawer>
```

## 3. Image Lightbox (Zoom & Pan)

**Problem**: Question images (especially containing text or diagrams) are small on mobile screens. Users cannot easily read details without zooming, which might zoom the entire page or layout.

**Proposed Solution**:
Implement a **Lightbox** component.

**Design**:
-   **Interaction**: Tapping an image in `QuestionDetail` opens it in a full-screen overlay.
-   **Features**:
    -   Pinch-to-zoom support.
    -   Pan to move around the zoomed image.
    -   Double-tap to zoom in/out.
    -   Close button (top right) or swipe-to-close.

**Implementation**:
-   Use a library like `vue-easy-lightbox` or build a simple overlay with CSS transforms.

## 4. Swipe Navigation

**Problem**: Navigating between questions requires going "Back" to list, then clicking the next one.

**Proposed Solution**:
Add **Swipe Gestures** to the `QuestionDetail` view.

**Design**:
-   **Swipe Left**: Load next question in the current filtered list.
-   **Swipe Right**: Load previous question.
-   **Animation**: Slide transition effect.

## 5. Pull-to-Refresh

**Problem**: "Refresh" is currently a button. Mobile users expect "Pull to Refresh".

**Proposed Solution**:
Implement a pull-down gesture on the `QuestionList` container to trigger the data refresh.
