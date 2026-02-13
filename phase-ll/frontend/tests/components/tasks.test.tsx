/*
Frontend task component tests.

[Task]: T061, T062, T063, T064
[From]: specs/001-fullstack-web-app/spec.md
*/

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TaskList from '@/components/tasks/TaskList';
import TaskItem from '@/components/tasks/TaskItem';
import CreateTaskForm from '@/components/tasks/CreateTaskForm';
import EmptyState from '@/components/tasks/EmptyState';
import { Task } from '@/hooks/useTasks';

// Mock tasks data
const mockTasks: Task[] = [
  {
    id: '1',
    user_id: 'user1',
    title: 'Task 1',
    description: 'Description 1',
    is_complete: false,
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-01-15T10:00:00Z',
  },
  {
    id: '2',
    user_id: 'user1',
    title: 'Task 2',
    description: null,
    is_complete: true,
    created_at: '2026-01-15T11:00:00Z',
    updated_at: '2026-01-15T11:00:00Z',
  },
];

describe('TaskList', () => {
  const mockHandlers = {
    onToggleComplete: jest.fn(),
    onUpdate: jest.fn(),
    onDelete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders multiple tasks', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
    expect(screen.getByText('Description 1')).toBeInTheDocument();
  });

  test('renders empty list when no tasks provided', () => {
    const { container } = render(<TaskList tasks={[]} {...mockHandlers} />);

    expect(container.firstChild?.childNodes.length).toBe(0);
  });

  test('passes correct props to TaskItem components', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // Verify both tasks are rendered
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });
});

describe('TaskItem', () => {
  const mockTask: Task = {
    id: '1',
    user_id: 'user1',
    title: 'Test Task',
    description: 'Test Description',
    is_complete: false,
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-01-15T10:00:00Z',
  };

  const mockHandlers = {
    onToggleComplete: jest.fn().mockResolvedValue(undefined),
    onUpdate: jest.fn().mockResolvedValue(undefined),
    onDelete: jest.fn().mockResolvedValue(undefined),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays task title and description', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  test('shows completion checkbox', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: '' });
    expect(checkbox).toBeInTheDocument();
  });

  test('applies strikethrough style to completed tasks', () => {
    const completedTask = { ...mockTask, is_complete: true };
    render(<TaskItem task={completedTask} {...mockHandlers} />);

    const title = screen.getByText('Test Task');
    expect(title).toHaveClass('line-through');
  });

  test('calls onToggleComplete when checkbox clicked', async () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: '' });
    fireEvent.click(checkbox);

    await waitFor(() => {
      expect(mockHandlers.onToggleComplete).toHaveBeenCalledWith('1', true);
    });
  });

  test('shows edit form when edit button clicked', async () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const editButton = screen.getByTitle('Edit task');
    fireEvent.click(editButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Task title')).toBeInTheDocument();
    });
  });

  test('shows delete confirmation when delete button clicked', async () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const deleteButton = screen.getByTitle('Delete task');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText(/delete task/i)).toBeInTheDocument();
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    });
  });
});

describe('CreateTaskForm', () => {
  const mockOnCreateTask = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form with title and description inputs', () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument();
  });

  test('shows character count for title', () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    expect(screen.getByText('0/200 characters')).toBeInTheDocument();
  });

  test('shows character count for description', () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    expect(screen.getByText('0/1000 characters')).toBeInTheDocument();
  });

  test('updates character count as user types', () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Test' } });

    expect(screen.getByText('4/200 characters')).toBeInTheDocument();
  });

  test('calls onCreateTask with title and description on submit', async () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.change(descriptionInput, { target: { value: 'Task description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnCreateTask).toHaveBeenCalledWith('New Task', 'Task description');
    });
  });

  test('shows validation error for empty title', async () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    const submitButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
  });

  test('clears form after successful submission', async () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    const titleInput = screen.getByLabelText(/title/i) as HTMLInputElement;
    const descriptionInput = screen.getByLabelText(/description/i) as HTMLTextAreaElement;
    const submitButton = screen.getByRole('button', { name: /add task/i });

    fireEvent.change(titleInput, { target: { value: 'New Task' } });
    fireEvent.change(descriptionInput, { target: { value: 'Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(titleInput.value).toBe('');
      expect(descriptionInput.value).toBe('');
    });
  });

  test('disables submit button when title is empty', () => {
    render(<CreateTaskForm onCreateTask={mockOnCreateTask} />);

    const submitButton = screen.getByRole('button', { name: /add task/i });
    expect(submitButton).toBeDisabled();
  });
});

describe('EmptyState', () => {
  test('renders empty state message', () => {
    render(<EmptyState />);

    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
    expect(screen.getByText(/get started by creating your first task/i)).toBeInTheDocument();
  });

  test('displays icon', () => {
    const { container } = render(<EmptyState />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});
