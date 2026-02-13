/*
TaskList component to display array of tasks.

[Task]: T048
[From]: specs/001-fullstack-web-app/ui/components.md
*/

'use client';

import TaskItem from './TaskItem';
import { Task } from '@/hooks/useTasks';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: string, isComplete: boolean) => Promise<any>;
  onUpdate: (taskId: string, title: string, description?: string) => Promise<any>;
  onDelete: (taskId: string) => Promise<any>;
}

export default function TaskList({
  tasks,
  onToggleComplete,
  onUpdate,
  onDelete,
}: TaskListProps) {
  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
