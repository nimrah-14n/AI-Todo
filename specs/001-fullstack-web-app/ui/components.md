# UI Specification: Components

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This specification defines the reusable UI components for the Todo application frontend. All components are built with Next.js 16+, React, and TypeScript, following modern component design patterns.

## Design Principles

1. **Reusability**: Components are generic and reusable across pages
2. **Accessibility**: WCAG 2.1 AA compliance for all interactive elements
3. **Responsiveness**: Mobile-first design, works on all screen sizes
4. **Type Safety**: Full TypeScript typing for props and state
5. **User Feedback**: Clear visual feedback for all user actions

---

## Authentication Components

### SignupForm

**Purpose**: Render the user registration form with email and password inputs.

**Location**: `components/auth/SignupForm.tsx`

**Props**:
```typescript
interface SignupFormProps {
  onSuccess?: (user: User, token: string) => void;
  onError?: (error: string) => void;
}
```

**Visual Elements**:
- Email input field (type="email")
- Password input field (type="password")
- "Sign Up" submit button
- Link to signin page ("Already have an account? Sign in")
- Error message display area
- Loading spinner during submission

**Behavior**:
1. Validate email format on blur
2. Validate password length (min 8 chars) on blur
3. Disable submit button while loading
4. Display inline error messages for validation failures
5. Display API error messages above form
6. Clear errors when user starts typing
7. On success: Call onSuccess callback with user and token
8. On error: Call onError callback with error message

**Validation Rules**:
- Email: Required, valid email format
- Password: Required, minimum 8 characters

**Accessibility**:
- Labels associated with inputs (htmlFor)
- ARIA labels for screen readers
- Error messages announced to screen readers
- Keyboard navigation support
- Focus management (auto-focus first field)

---

### SigninForm

**Purpose**: Render the user login form with email and password inputs.

**Location**: `components/auth/SigninForm.tsx`

**Props**:
```typescript
interface SigninFormProps {
  onSuccess?: (user: User, token: string) => void;
  onError?: (error: string) => void;
}
```

**Visual Elements**:
- Email input field (type="email")
- Password input field (type="password")
- "Sign In" submit button
- Link to signup page ("Don't have an account? Sign up")
- Error message display area
- Loading spinner during submission

**Behavior**:
1. Validate email format on blur
2. Validate password not empty on blur
3. Disable submit button while loading
4. Display inline error messages for validation failures
5. Display API error messages above form
6. Clear errors when user starts typing
7. On success: Call onSuccess callback with user and token
8. On error: Call onError callback with error message

**Validation Rules**:
- Email: Required, valid email format
- Password: Required

**Accessibility**:
- Labels associated with inputs
- ARIA labels for screen readers
- Error messages announced
- Keyboard navigation support
- Focus management

---

## Task Components

### TaskList

**Purpose**: Display a list of tasks with loading and empty states.

**Location**: `components/tasks/TaskList.tsx`

**Props**:
```typescript
interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  onToggleComplete: (taskId: string, isComplete: boolean) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}
```

**Visual Elements**:
- Loading spinner (when loading=true)
- Empty state message (when tasks.length === 0)
- List of TaskItem components (when tasks.length > 0)
- Container with proper spacing

**Behavior**:
1. Show loading spinner while tasks are being fetched
2. Show empty state when no tasks exist
3. Render TaskItem for each task
4. Pass callbacks to TaskItem components
5. Handle optimistic updates for toggle complete

**Empty State**:
- Icon (e.g., clipboard or checklist icon)
- Message: "No tasks yet. Create your first task!"
- Encouraging tone

**Loading State**:
- Centered spinner
- "Loading tasks..." text

**Accessibility**:
- Semantic list markup (<ul>, <li>)
- ARIA live region for dynamic updates
- Keyboard navigation between tasks

---

### TaskItem

**Purpose**: Display a single task with actions (complete, edit, delete).

**Location**: `components/tasks/TaskItem.tsx`

**Props**:
```typescript
interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: string, isComplete: boolean) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}
```

**Visual Elements**:
- Checkbox or toggle for completion status
- Task title (with strikethrough if complete)
- Task description (if present, truncated or collapsed)
- Creation date (formatted, e.g., "2 hours ago")
- Edit button (icon or text)
- Delete button (icon or text)
- Visual distinction for completed tasks (opacity, strikethrough, color)

**Behavior**:
1. Toggle completion on checkbox click
2. Show edit form on edit button click
3. Show delete confirmation on delete button click
4. Apply completed styling when is_complete=true
5. Expand/collapse description if long
6. Optimistic UI update for completion toggle

**Visual States**:
- **Incomplete**: Normal text, unchecked checkbox
- **Complete**: Strikethrough text, checked checkbox, reduced opacity
- **Hover**: Highlight background, show action buttons
- **Loading**: Disabled state during API call

**Accessibility**:
- Checkbox with label
- Button labels for screen readers
- Keyboard shortcuts (Enter to toggle, Delete key to delete)
- Focus indicators

---

### TaskForm

**Purpose**: Form for creating a new task.

**Location**: `components/tasks/TaskForm.tsx`

**Props**:
```typescript
interface TaskFormProps {
  onSubmit: (title: string, description: string) => void;
  onCancel?: () => void;
  loading?: boolean;
}
```

**Visual Elements**:
- Title input field (required)
- Description textarea (optional)
- Character count for title (e.g., "45/200")
- Character count for description (e.g., "120/1000")
- "Add Task" submit button
- "Cancel" button (if onCancel provided)
- Error message display area

**Behavior**:
1. Validate title length (1-200 chars) on blur
2. Validate description length (max 1000 chars) on blur
3. Show character count that updates as user types
4. Disable submit button if title empty or too long
5. Clear form after successful submission
6. Display validation errors inline
7. Auto-focus title field on mount

**Validation Rules**:
- Title: Required, 1-200 characters, not only whitespace
- Description: Optional, max 1000 characters

**Accessibility**:
- Labels for all inputs
- Error messages announced
- Keyboard navigation
- Submit on Enter key (in title field)

---

### TaskEditForm

**Purpose**: Form for editing an existing task.

**Location**: `components/tasks/TaskEditForm.tsx`

**Props**:
```typescript
interface TaskEditFormProps {
  task: Task;
  onSubmit: (taskId: string, title: string, description: string) => void;
  onCancel: () => void;
  loading?: boolean;
}
```

**Visual Elements**:
- Title input field (pre-filled with current title)
- Description textarea (pre-filled with current description)
- Character count for title
- Character count for description
- "Save" submit button
- "Cancel" button
- Error message display area

**Behavior**:
1. Pre-populate fields with current task data
2. Validate title length (1-200 chars) on blur
3. Validate description length (max 1000 chars) on blur
4. Show character count that updates as user types
5. Disable submit button if title empty or too long
6. Call onCancel if user clicks cancel or presses Escape
7. Display validation errors inline

**Validation Rules**:
- Title: Required, 1-200 characters, not only whitespace
- Description: Optional, max 1000 characters

**Accessibility**:
- Labels for all inputs
- Error messages announced
- Keyboard navigation
- Escape key to cancel
- Enter key to submit (with Ctrl/Cmd modifier)

---

## UI Primitives

### Button

**Purpose**: Reusable button component with variants.

**Location**: `components/ui/Button.tsx`

**Props**:
```typescript
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}
```

**Variants**:
- **Primary**: Solid background, high contrast (for main actions)
- **Secondary**: Outlined, lower contrast (for secondary actions)
- **Danger**: Red color scheme (for destructive actions like delete)
- **Ghost**: Minimal styling, transparent background (for tertiary actions)

**Sizes**:
- **sm**: Small padding, smaller text
- **md**: Default size
- **lg**: Large padding, larger text

**Behavior**:
1. Show loading spinner when loading=true
2. Disable button when disabled=true or loading=true
3. Apply hover and active states
4. Support icon before or after text

**Accessibility**:
- Proper button semantics
- Disabled state announced
- Loading state announced
- Focus indicators

---

### Input

**Purpose**: Reusable text input component.

**Location**: `components/ui/Input.tsx`

**Props**:
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  maxLength?: number;
  autoFocus?: boolean;
}
```

**Visual Elements**:
- Label (if provided)
- Input field
- Error message (if error provided)
- Character count (if maxLength provided)
- Required indicator (if required=true)

**Behavior**:
1. Display error styling when error provided
2. Show character count if maxLength specified
3. Auto-focus if autoFocus=true
4. Call onChange on every keystroke
5. Call onBlur when focus lost

**Accessibility**:
- Label associated with input
- Error message announced
- Required state announced
- Placeholder not used as label

---

### Textarea

**Purpose**: Reusable textarea component for multi-line input.

**Location**: `components/ui/Textarea.tsx`

**Props**:
```typescript
interface TextareaProps {
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  maxLength?: number;
  rows?: number;
}
```

**Visual Elements**:
- Label (if provided)
- Textarea field
- Error message (if error provided)
- Character count (if maxLength provided)
- Required indicator (if required=true)

**Behavior**:
1. Display error styling when error provided
2. Show character count if maxLength specified
3. Auto-resize based on content (optional)
4. Call onChange on every keystroke
5. Call onBlur when focus lost

**Accessibility**:
- Label associated with textarea
- Error message announced
- Required state announced

---

### LoadingSpinner

**Purpose**: Display loading indicator.

**Location**: `components/ui/LoadingSpinner.tsx`

**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}
```

**Visual Elements**:
- Animated spinner (CSS animation or SVG)
- Optional loading text below spinner

**Sizes**:
- **sm**: 16px diameter
- **md**: 32px diameter (default)
- **lg**: 48px diameter

**Accessibility**:
- ARIA role="status"
- ARIA live region
- Screen reader text "Loading..."

---

### Modal

**Purpose**: Display modal dialog for confirmations.

**Location**: `components/ui/Modal.tsx`

**Props**:
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

**Visual Elements**:
- Backdrop overlay (semi-transparent)
- Modal container (centered)
- Title bar
- Content area
- Footer area (optional, for action buttons)
- Close button (X icon)

**Behavior**:
1. Show modal when isOpen=true
2. Close on backdrop click
3. Close on Escape key
4. Trap focus within modal
5. Prevent body scroll when open
6. Animate in/out

**Accessibility**:
- ARIA role="dialog"
- ARIA labelledby for title
- Focus trap
- Escape key to close
- Return focus to trigger element on close

---

### ConfirmDialog

**Purpose**: Display confirmation dialog for destructive actions.

**Location**: `components/ui/ConfirmDialog.tsx`

**Props**:
```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}
```

**Visual Elements**:
- Modal backdrop
- Dialog container
- Title
- Message text
- Confirm button (styled based on variant)
- Cancel button

**Behavior**:
1. Show dialog when isOpen=true
2. Call onConfirm when confirm button clicked
3. Call onClose when cancel button clicked or backdrop clicked
4. Close on Escape key
5. Focus confirm button by default (for danger actions, focus cancel)

**Accessibility**:
- ARIA role="alertdialog"
- Focus management
- Keyboard navigation

---

## Layout Components

### Header

**Purpose**: Application header with navigation and user menu.

**Location**: `components/layout/Header.tsx`

**Props**:
```typescript
interface HeaderProps {
  user?: User;
  onSignout: () => void;
}
```

**Visual Elements**:
- App logo/title
- User email (if signed in)
- Sign out button (if signed in)
- Navigation links (if applicable)

**Behavior**:
1. Show user info when user provided
2. Call onSignout when sign out clicked
3. Responsive: Collapse to hamburger menu on mobile

**Accessibility**:
- Semantic header element
- Navigation landmark
- Skip to main content link

---

### Container

**Purpose**: Centered content container with max width.

**Location**: `components/layout/Container.tsx`

**Props**:
```typescript
interface ContainerProps {
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}
```

**Visual Elements**:
- Centered container
- Horizontal padding
- Max width constraint

**Max Widths**:
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px

---

## Styling Approach

### CSS Framework

- **Tailwind CSS**: Utility-first CSS framework
- **Custom Components**: Styled with Tailwind classes
- **Responsive Design**: Mobile-first breakpoints
- **Dark Mode**: Not implemented in Phase II (out of scope)

### Color Palette

- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Danger**: Red (#EF4444)
- **Warning**: Yellow (#F59E0B)
- **Gray Scale**: Tailwind gray palette

### Typography

- **Font Family**: System font stack (sans-serif)
- **Headings**: Bold, larger sizes
- **Body**: Regular weight, readable size (16px base)
- **Code**: Monospace font

---

## Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile Adaptations

- Stack form fields vertically
- Full-width buttons
- Larger touch targets (min 44x44px)
- Simplified navigation
- Reduced padding/margins

---

## Component Testing

### Unit Tests

Each component should have tests for:
1. Renders without crashing
2. Displays correct content
3. Handles user interactions
4. Calls callbacks with correct arguments
5. Shows loading states
6. Shows error states
7. Validates input
8. Keyboard navigation works

### Example Test (TaskItem)

```typescript
describe('TaskItem', () => {
  it('renders task title and description', () => {
    const task = { id: '1', title: 'Test', description: 'Desc', is_complete: false };
    render(<TaskItem task={task} onToggleComplete={jest.fn()} onEdit={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('Desc')).toBeInTheDocument();
  });

  it('calls onToggleComplete when checkbox clicked', () => {
    const onToggleComplete = jest.fn();
    const task = { id: '1', title: 'Test', is_complete: false };
    render(<TaskItem task={task} onToggleComplete={onToggleComplete} onEdit={jest.fn()} onDelete={jest.fn()} />);
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onToggleComplete).toHaveBeenCalledWith('1', true);
  });
});
```

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
- **Pages**: `specs/001-fullstack-web-app/ui/pages.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
