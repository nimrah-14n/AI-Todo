# UI Specification: Pages

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This specification defines all pages in the Todo application, including routing, layout, data fetching, and user interactions. The application uses Next.js 16+ App Router for file-based routing.

## Routing Structure

```
app/
├── layout.tsx                    # Root layout (wraps all pages)
├── page.tsx                      # Landing page (/)
├── (auth)/                       # Authentication route group
│   ├── layout.tsx                # Auth layout (centered forms)
│   ├── signup/
│   │   └── page.tsx              # Signup page (/signup)
│   └── signin/
│       └── page.tsx              # Signin page (/signin)
└── (dashboard)/                  # Protected route group
    ├── layout.tsx                # Dashboard layout (with header)
    └── tasks/
        └── page.tsx              # Task dashboard (/tasks)
```

---

## Root Layout

### app/layout.tsx

**Purpose**: Root layout that wraps all pages, provides global styles and metadata.

**File**: `app/layout.tsx`

**Structure**:
```typescript
export const metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A simple, multi-user todo application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
}
```

**Responsibilities**:
- Set HTML lang attribute
- Apply global styles
- Define metadata (title, description)
- Provide font configuration
- Wrap all pages

**Styling**:
- Background color: Light gray (#F9FAFB)
- Minimum height: 100vh
- System font stack

---

## Landing Page

### app/page.tsx

**Purpose**: Landing page that welcomes users and directs them to signup or signin.

**Route**: `/`

**Authentication**: Not required

**Visual Elements**:
- App logo/title
- Tagline: "Manage your tasks efficiently"
- Feature highlights (bullet points)
- "Get Started" button → /signup
- "Sign In" link → /signin

**Layout**:
- Centered content
- Hero section with call-to-action
- Responsive design

**Behavior**:
1. If user already authenticated, redirect to /tasks
2. Otherwise, show landing page
3. "Get Started" button navigates to /signup
4. "Sign In" link navigates to /signin

**Content**:
```
# Welcome to Todo App

Manage your tasks efficiently with our simple, intuitive interface.

Features:
✓ Create and organize tasks
✓ Mark tasks as complete
✓ Edit and delete tasks
✓ Secure multi-user support
✓ Access from any device

[Get Started] [Sign In]
```

**Accessibility**:
- Semantic HTML (header, main, section)
- Proper heading hierarchy
- Descriptive link text
- Keyboard navigation

---

## Authentication Pages

### Signup Page

**File**: `app/(auth)/signup/page.tsx`

**Route**: `/signup`

**Authentication**: Not required (redirects if already authenticated)

**Visual Elements**:
- Page title: "Create Your Account"
- SignupForm component
- Link to signin: "Already have an account? Sign in"
- App logo/branding

**Layout**:
- Centered card/container
- Max width: 400px
- Vertical padding for mobile
- White background card with shadow

**Behavior**:
1. Check if user already authenticated
   - If yes: Redirect to /tasks
   - If no: Show signup form
2. On successful signup:
   - Store JWT token
   - Redirect to /tasks
3. On signup error:
   - Display error message
   - Keep user on page

**Data Flow**:
```
User enters email/password
    ↓
SignupForm validates input
    ↓
POST /api/auth/signup
    ↓
Success: Store token → Redirect to /tasks
Error: Display error message
```

**Error Handling**:
- Display API errors above form
- Display validation errors inline
- Clear errors when user starts typing

**Accessibility**:
- Page title in <h1>
- Form labels and ARIA attributes
- Focus management
- Error announcements

---

### Signin Page

**File**: `app/(auth)/signin/page.tsx`

**Route**: `/signin`

**Authentication**: Not required (redirects if already authenticated)

**Visual Elements**:
- Page title: "Sign In to Your Account"
- SigninForm component
- Link to signup: "Don't have an account? Sign up"
- App logo/branding

**Layout**:
- Centered card/container
- Max width: 400px
- Vertical padding for mobile
- White background card with shadow

**Behavior**:
1. Check if user already authenticated
   - If yes: Redirect to /tasks
   - If no: Show signin form
2. On successful signin:
   - Store JWT token
   - Redirect to /tasks
3. On signin error:
   - Display error message
   - Keep user on page

**Data Flow**:
```
User enters email/password
    ↓
SigninForm validates input
    ↓
POST /api/auth/signin
    ↓
Success: Store token → Redirect to /tasks
Error: Display error message
```

**Error Handling**:
- Display API errors above form
- Display validation errors inline
- Clear errors when user starts typing

**Accessibility**:
- Page title in <h1>
- Form labels and ARIA attributes
- Focus management
- Error announcements

---

### Auth Layout

**File**: `app/(auth)/layout.tsx`

**Purpose**: Layout for authentication pages (signup, signin).

**Structure**:
```typescript
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
```

**Styling**:
- Centered vertically and horizontally
- Max width: 448px (28rem)
- Padding: 1rem on mobile
- Background: Inherits from root layout

---

## Dashboard Pages

### Task Dashboard

**File**: `app/(dashboard)/tasks/page.tsx`

**Route**: `/tasks`

**Authentication**: Required (redirects to /signin if not authenticated)

**Visual Elements**:
- Page title: "My Tasks"
- TaskForm component (for creating new tasks)
- TaskList component (displays all tasks)
- Empty state (if no tasks)
- Loading state (while fetching tasks)
- Error state (if fetch fails)

**Layout**:
- Header with user info and sign out button
- Main content area with max width
- TaskForm at top
- TaskList below

**Behavior**:

1. **On Page Load**:
   - Check authentication
     - If not authenticated: Redirect to /signin
     - If authenticated: Proceed
   - Fetch user's tasks: GET /api/{user_id}/tasks
   - Display loading spinner while fetching
   - Display tasks when loaded
   - Display error if fetch fails

2. **Create Task**:
   - User fills TaskForm
   - POST /api/{user_id}/tasks
   - On success: Add task to list (optimistic update)
   - On error: Display error message

3. **Toggle Complete**:
   - User clicks checkbox on TaskItem
   - PATCH /api/{user_id}/tasks/{id}/complete
   - Optimistic update: Toggle immediately
   - On error: Revert and show error

4. **Edit Task**:
   - User clicks edit button on TaskItem
   - TaskItem switches to edit mode (TaskEditForm)
   - User modifies and saves
   - PUT /api/{user_id}/tasks/{id}
   - On success: Update task in list
   - On error: Revert and show error

5. **Delete Task**:
   - User clicks delete button on TaskItem
   - Show ConfirmDialog: "Are you sure?"
   - If confirmed: DELETE /api/{user_id}/tasks/{id}
   - Optimistic update: Remove from list
   - On error: Re-add and show error

**Data Flow**:
```
Page loads
    ↓
Check authentication
    ↓
Fetch tasks: GET /api/{user_id}/tasks
    ↓
Display tasks in TaskList
    ↓
User interactions (create, toggle, edit, delete)
    ↓
API calls with optimistic updates
    ↓
Update UI based on response
```

**State Management**:
```typescript
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Error Handling**:
- Network errors: "Failed to load tasks. Please try again."
- Authentication errors: Redirect to /signin
- Operation errors: Display inline error messages
- Retry mechanism for failed operations

**Accessibility**:
- Page title in <h1>
- Semantic HTML structure
- ARIA live regions for dynamic updates
- Keyboard navigation
- Focus management

---

### Dashboard Layout

**File**: `app/(dashboard)/layout.tsx`

**Purpose**: Layout for protected dashboard pages, includes header and authentication check.

**Structure**:
```typescript
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Check authentication
  // If not authenticated, redirect to /signin

  return (
    <div className="min-h-screen">
      <Header user={user} onSignout={handleSignout} />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
```

**Responsibilities**:
- Check authentication on mount
- Redirect to /signin if not authenticated
- Render Header component
- Provide main content container
- Handle sign out

**Header Content**:
- App logo/title (links to /tasks)
- User email
- Sign out button

**Sign Out Behavior**:
1. Remove JWT token from storage
2. Clear user state
3. Redirect to /signin

---

## Route Protection

### Middleware

**File**: `middleware.ts`

**Purpose**: Protect routes that require authentication.

**Protected Routes**:
- `/tasks` - Requires authentication

**Public Routes**:
- `/` - Landing page
- `/signup` - Signup page
- `/signin` - Signin page

**Logic**:
```typescript
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token');
  const { pathname } = request.nextUrl;

  // Protected routes
  if (pathname.startsWith('/tasks')) {
    if (!token) {
      return NextResponse.redirect(new URL('/signin', request.url));
    }
  }

  // Auth routes (redirect if already authenticated)
  if (pathname.startsWith('/signup') || pathname.startsWith('/signin')) {
    if (token) {
      return NextResponse.redirect(new URL('/tasks', request.url));
    }
  }

  return NextResponse.next();
}
```

---

## Page Transitions

### Loading States

**Purpose**: Show loading indicators during page transitions and data fetching.

**Implementation**:
- Use React Suspense for page-level loading
- Use loading spinners for component-level loading
- Use skeleton screens for content placeholders (optional)

**Loading UI**:
```typescript
// app/(dashboard)/tasks/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <LoadingSpinner size="lg" text="Loading tasks..." />
    </div>
  );
}
```

---

## Error Handling

### Error Boundaries

**Purpose**: Catch and display errors gracefully.

**Implementation**:
```typescript
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <button onClick={reset} className="btn-primary">
        Try again
      </button>
    </div>
  );
}
```

---

## Responsive Design

### Mobile Layout (< 640px)

**Landing Page**:
- Stack content vertically
- Full-width buttons
- Reduced padding

**Auth Pages**:
- Full-width forms
- Larger touch targets
- Simplified layout

**Task Dashboard**:
- Stack TaskForm and TaskList vertically
- Full-width task items
- Simplified task actions (icons only)
- Collapsible descriptions

### Tablet Layout (640px - 1024px)

**Landing Page**:
- Two-column layout for features
- Centered hero section

**Auth Pages**:
- Centered forms with max width
- More padding

**Task Dashboard**:
- TaskForm at top, full width
- TaskList below with comfortable spacing
- Task items show all actions

### Desktop Layout (> 1024px)

**Landing Page**:
- Multi-column layout
- Large hero section
- Feature grid

**Auth Pages**:
- Centered forms with max width
- Ample whitespace

**Task Dashboard**:
- TaskForm at top
- TaskList with optimal line length
- Hover states for task items
- All actions visible

---

## SEO and Metadata

### Page Metadata

**Landing Page**:
```typescript
export const metadata = {
  title: 'Todo App - Manage Your Tasks Efficiently',
  description: 'A simple, secure, multi-user todo application. Create, organize, and track your tasks from any device.',
};
```

**Signup Page**:
```typescript
export const metadata = {
  title: 'Sign Up - Todo App',
  description: 'Create your free Todo App account and start managing your tasks today.',
};
```

**Signin Page**:
```typescript
export const metadata = {
  title: 'Sign In - Todo App',
  description: 'Sign in to your Todo App account to access your tasks.',
};
```

**Task Dashboard**:
```typescript
export const metadata = {
  title: 'My Tasks - Todo App',
  description: 'Manage your personal tasks.',
};
```

---

## Performance Optimization

### Code Splitting

- Automatic code splitting by Next.js App Router
- Each page is a separate bundle
- Components lazy-loaded when needed

### Data Fetching

- Server-side rendering for initial page load (where applicable)
- Client-side fetching for dynamic data
- Optimistic updates for better UX

### Caching

- Browser caching for static assets
- API response caching (future enhancement)

---

## Testing Scenarios

### Landing Page Tests

- [ ] Renders without crashing
- [ ] Displays app title and tagline
- [ ] "Get Started" button navigates to /signup
- [ ] "Sign In" link navigates to /signin
- [ ] Redirects to /tasks if already authenticated

### Signup Page Tests

- [ ] Renders signup form
- [ ] Validates email format
- [ ] Validates password length
- [ ] Displays error for duplicate email
- [ ] Redirects to /tasks on success
- [ ] Stores JWT token on success
- [ ] Redirects to /tasks if already authenticated

### Signin Page Tests

- [ ] Renders signin form
- [ ] Validates email format
- [ ] Displays error for invalid credentials
- [ ] Redirects to /tasks on success
- [ ] Stores JWT token on success
- [ ] Redirects to /tasks if already authenticated

### Task Dashboard Tests

- [ ] Redirects to /signin if not authenticated
- [ ] Fetches and displays tasks on load
- [ ] Shows loading spinner while fetching
- [ ] Shows empty state when no tasks
- [ ] Creates new task successfully
- [ ] Toggles task completion
- [ ] Edits task successfully
- [ ] Deletes task with confirmation
- [ ] Displays errors appropriately
- [ ] Sign out button works

---

## User Flows

### New User Flow

```
1. User visits landing page (/)
2. Clicks "Get Started"
3. Redirected to /signup
4. Fills signup form
5. Submits form
6. Account created, token stored
7. Redirected to /tasks
8. Sees empty state
9. Creates first task
10. Task appears in list
```

### Returning User Flow

```
1. User visits landing page (/)
2. Automatically redirected to /tasks (token exists)
3. Tasks loaded and displayed
4. User interacts with tasks
```

### Sign In Flow

```
1. User visits landing page (/)
2. Clicks "Sign In"
3. Redirected to /signin
4. Fills signin form
5. Submits form
6. Authenticated, token stored
7. Redirected to /tasks
8. Tasks loaded and displayed
```

---

## Accessibility Checklist

### All Pages

- [ ] Semantic HTML structure
- [ ] Proper heading hierarchy (h1, h2, h3)
- [ ] Skip to main content link
- [ ] Keyboard navigation support
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA
- [ ] Alt text for images
- [ ] ARIA labels where needed

### Forms

- [ ] Labels associated with inputs
- [ ] Error messages announced
- [ ] Required fields indicated
- [ ] Submit on Enter key
- [ ] Focus management

### Interactive Elements

- [ ] Buttons have descriptive text
- [ ] Links have descriptive text
- [ ] Loading states announced
- [ ] Error states announced
- [ ] Success states announced

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
- **Components**: `specs/001-fullstack-web-app/ui/components.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
- **Authentication**: `specs/001-fullstack-web-app/features/authentication.md`
- **Task CRUD**: `specs/001-fullstack-web-app/features/task-crud.md`
