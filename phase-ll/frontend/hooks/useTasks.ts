/*
useTasks hook for fetching and managing task state.

[Task]: T052
[From]: specs/001-fullstack-web-app/ui/components.md
*/

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { apiGet, apiPost, apiPatch, apiPut, apiDelete } from '@/lib/api-client';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  is_complete: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export function useTasks() {
  const { user, token } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    if (!user || !token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await apiGet<TaskListResponse>(
        `/api/${user.id}/tasks`,
        token
      );

      setTasks(response.tasks);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [user, token]);

  const createTask = async (title: string, description?: string) => {
    if (!user || !token) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await apiPost<Task>(
        `/api/${user.id}/tasks`,
        { title, description: description || null },
        token
      );

      // Optimistic update: add new task to the beginning
      setTasks((prev) => [response, ...prev]);

      return response;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to create task');
    }
  };

  const toggleComplete = async (taskId: string, isComplete: boolean) => {
    if (!user || !token) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await apiPatch<Task>(
        `/api/${user.id}/tasks/${taskId}/complete`,
        { is_complete: isComplete },
        token
      );

      // Optimistic update: update task in list
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? response : task))
      );

      return response;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to update task');
    }
  };

  const updateTask = async (
    taskId: string,
    title: string,
    description?: string
  ) => {
    if (!user || !token) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await apiPut<Task>(
        `/api/${user.id}/tasks/${taskId}`,
        { title, description: description || null },
        token
      );

      // Optimistic update: update task in list
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? response : task))
      );

      return response;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to update task');
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!user || !token) {
      throw new Error('Not authenticated');
    }

    try {
      await apiDelete(`/api/${user.id}/tasks/${taskId}`, token);

      // Optimistic update: remove task from list
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err: any) {
      throw new Error(err.message || 'Failed to delete task');
    }
  };

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    toggleComplete,
    updateTask,
    deleteTask,
  };
}
