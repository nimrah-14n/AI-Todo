/*
EmptyState component to display when user has no tasks.

[Task]: T051
[From]: specs/001-fullstack-web-app/ui/components.md
*/

'use client';

export default function EmptyState() {
  return (
    <div className="text-center py-16 animate-fade-in-up">
      <div className="relative inline-block">
        <div className="absolute inset-0 bg-primary-300 rounded-full blur-2xl opacity-40 animate-pulse-slow"></div>
        <svg
          className="relative mx-auto h-32 w-32 text-primary-400 animate-float"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
      </div>
      <h3 className="mt-8 text-2xl font-bold text-gray-900 animate-fade-in-up animation-delay-200">
        No tasks yet
      </h3>
      <p className="mt-3 text-base text-gray-600 max-w-md mx-auto animate-fade-in-up animation-delay-400">
        Your task list is empty. Get started by creating your first task using the form above!
      </p>
      <div className="mt-8 flex items-center justify-center gap-2 text-sm text-primary-600 font-medium animate-fade-in-up animation-delay-600">
        <svg className="w-5 h-5 animate-bounce-subtle" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
        Start adding tasks above
      </div>
    </div>
  );
}
