/*
Task dashboard page with protected route.

[Task]: T047, T053, T054
[From]: specs/001-fullstack-web-app/ui/pages.md
*/

'use client';

import { useAuth } from '@/hooks/useAuth';
import { useTasks } from '@/hooks/useTasks';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CreateTaskForm from '@/components/tasks/CreateTaskForm';
import TaskList from '@/components/tasks/TaskList';
import EmptyState from '@/components/tasks/EmptyState';
import DashboardNavigation from '@/components/dashboard/DashboardNavigation';
import ThemeToggle from '@/components/dashboard/ThemeToggle';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { user, signout } = useAuth();
  const {
    tasks,
    loading,
    error,
    createTask,
    toggleComplete,
    updateTask,
    deleteTask,
  } = useTasks();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-100 via-primary-50 to-accent-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative overflow-hidden transition-colors duration-300">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-300 dark:bg-primary-900/30 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent-300 dark:bg-accent-900/30 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary-200 dark:bg-primary-800/20 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="glass dark:glass-dark shadow-lg border-b border-white/30 dark:border-gray-700/30 sticky top-0 z-50 animate-slide-in-down transition-colors duration-300">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-600 via-accent-500 to-accent-600 rounded-xl flex items-center justify-center shadow-lg animate-gradient transform hover:scale-110 transition-transform duration-300">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 dark:from-primary-400 dark:to-accent-400 bg-clip-text text-transparent">My Tasks</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {user?.email}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <DashboardNavigation />
              <ThemeToggle />
              <button
                onClick={signout}
                className="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-200 hover:text-white hover:bg-gradient-to-r hover:from-primary-600 hover:to-accent-600 bg-white/50 dark:bg-gray-800/50 rounded-lg transition-all duration-300 flex items-center gap-2 border border-primary-200 dark:border-gray-700 hover:border-transparent shadow-sm hover:shadow-lg transform hover:scale-105 active:scale-95"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="space-y-6">
          {/* Create Task Form */}
          <div className="animate-fade-in-up">
            <CreateTaskForm onCreateTask={createTask} />
          </div>

          {/* Task Statistics */}
          {!loading && tasks.length > 0 && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 animate-fade-in-up animation-delay-200">
                <div className="glass dark:glass-dark p-6 rounded-2xl shadow-xl border-2 border-primary-300/50 dark:border-gray-700 hover:shadow-2xl hover:border-primary-400 dark:hover:border-primary-600 transition-all duration-300 transform hover:-translate-y-2 card-lift group">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">Total Tasks</p>
                      <p className="text-4xl font-extrabold text-gray-900 dark:text-white mt-1 animate-count-up">{tasks.length}</p>
                    </div>
                    <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                  </div>
                </div>

                <div className="glass dark:glass-dark p-6 rounded-2xl shadow-xl border-2 border-success-300/50 dark:border-gray-700 hover:shadow-2xl hover:border-success-400 dark:hover:border-success-600 transition-all duration-300 transform hover:-translate-y-2 card-lift group">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">Completed</p>
                      <p className="text-4xl font-extrabold text-success-600 dark:text-success-400 mt-1 animate-count-up">
                        {tasks.filter((t) => t.is_complete).length}
                      </p>
                    </div>
                    <div className="w-14 h-14 bg-gradient-to-br from-success-500 to-success-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                </div>

                <div className="glass dark:glass-dark p-6 rounded-2xl shadow-xl border-2 border-orange-300/50 dark:border-gray-700 hover:shadow-2xl hover:border-orange-400 dark:hover:border-orange-600 transition-all duration-300 transform hover:-translate-y-2 card-lift group">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">Remaining</p>
                      <p className="text-4xl font-extrabold text-orange-600 dark:text-orange-400 mt-1 animate-count-up">
                        {tasks.filter((t) => !t.is_complete).length}
                      </p>
                    </div>
                    <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="glass dark:glass-dark p-6 rounded-2xl shadow-lg border-2 border-primary-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-300 animate-fade-in-up animation-delay-400">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Overall Progress</h3>
                  <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                    {Math.round((tasks.filter((t) => t.is_complete).length / tasks.length) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 via-accent-500 to-success-500 rounded-full transition-all duration-1000 ease-out animate-gradient shadow-lg"
                    style={{ width: `${(tasks.filter((t) => t.is_complete).length / tasks.length) * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 text-center">
                  {tasks.filter((t) => t.is_complete).length} of {tasks.length} tasks completed
                </p>
              </div>
            </>
          )}

          {/* Task List */}
          <div className="glass dark:glass-dark p-6 rounded-2xl shadow-xl border-2 border-primary-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-300 animate-fade-in-up animation-delay-600">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent flex items-center gap-3">
                <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                Your Tasks
              </h2>
              <span className="px-4 py-2 bg-gradient-to-r from-primary-500 to-accent-500 text-white text-sm font-bold rounded-full shadow-lg animate-pulse-slow">
                {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="text-center py-16">
                <div className="relative inline-flex">
                  <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 dark:border-gray-700"></div>
                  <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-primary-600 dark:border-primary-400 absolute top-0 left-0"></div>
                </div>
                <p className="mt-6 text-gray-600 dark:text-gray-400 font-semibold text-lg animate-pulse">Loading your tasks...</p>
                <p className="mt-2 text-gray-500 dark:text-gray-500 text-sm">Please wait a moment</p>
              </div>
            )}

            {/* Error State */}
            {error && !loading && (
              <div className="p-6 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 flex items-start gap-4 animate-slide-in-down shadow-lg">
                <div className="w-12 h-12 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-bold text-lg mb-1">Oops! Something went wrong</h3>
                  <p className="text-red-600 dark:text-red-400">{error}</p>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && tasks.length === 0 && <EmptyState />}

            {/* Task List */}
            {!loading && !error && tasks.length > 0 && (
              <TaskList
                tasks={tasks}
                onToggleComplete={toggleComplete}
                onUpdate={updateTask}
                onDelete={deleteTask}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
