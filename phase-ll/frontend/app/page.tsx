/*
Landing page with navigation to signup/signin.

[Task]: T033
[From]: specs/001-fullstack-web-app/ui/pages.md
*/

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-100 via-primary-50 to-accent-100 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-300 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent-300 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-4000"></div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        {/* Hero Section with fade-in animation */}
        <div className="animate-fade-in-up">
          <div className="inline-block mb-6 animate-float">
            <div className="w-20 h-20 bg-gradient-to-br from-primary-500 via-accent-500 to-accent-600 rounded-2xl flex items-center justify-center shadow-2xl animate-gradient">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
          </div>
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-extrabold text-gray-900 mb-6">
            <span className="block gradient-text animate-gradient">Todo App</span>
          </h1>
          <p className="text-xl md:text-2xl lg:text-3xl text-gray-700 mb-10 max-w-3xl mx-auto leading-relaxed">
            Manage your tasks efficiently with our <span className="font-bold text-primary-700">simple</span> and <span className="font-bold text-accent-700">powerful</span> todo application.
          </p>
        </div>

        {/* CTA Buttons with staggered animation */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-24 animate-fade-in-up animation-delay-200">
          <Link
            href="/signup"
            className="group relative px-10 py-5 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-bold text-lg rounded-xl hover:from-primary-700 hover:to-accent-700 focus:outline-none focus:ring-4 focus:ring-primary-300 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl active:scale-95 overflow-hidden"
          >
            <span className="relative flex items-center justify-center gap-3 z-10">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Get Started Free
              <svg className="w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </Link>
          <Link
            href="/signin"
            className="group px-10 py-5 bg-white text-gray-900 font-bold text-lg rounded-xl border-3 border-primary-200 hover:border-primary-500 hover:bg-primary-50 focus:outline-none focus:ring-4 focus:ring-primary-300 transition-all duration-300 transform hover:scale-105 hover:shadow-xl active:scale-95 flex items-center justify-center gap-3"
          >
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Sign In
          </Link>
        </div>

        {/* Feature Cards with staggered animations */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="group p-8 glass rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 animate-fade-in-up animation-delay-400 border-2 border-primary-100 hover:border-primary-300">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg mx-auto">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Simple & Intuitive
            </h3>
            <p className="text-gray-600 leading-relaxed text-lg">
              Create, update, and manage your tasks with an easy-to-use interface designed for productivity.
            </p>
          </div>

          <div className="group p-8 glass rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 animate-fade-in-up animation-delay-600 border-2 border-accent-100 hover:border-accent-300">
            <div className="w-16 h-16 bg-gradient-to-br from-accent-500 to-accent-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg mx-auto">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Secure & Private
            </h3>
            <p className="text-gray-600 leading-relaxed text-lg">
              Your data is protected with industry-standard authentication and encryption technology.
            </p>
          </div>

          <div className="group p-8 glass rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-3 animate-fade-in-up animation-delay-800 border-2 border-accent-100 hover:border-accent-300">
            <div className="w-16 h-16 bg-gradient-to-br from-accent-500 to-accent-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg mx-auto">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Always Accessible
            </h3>
            <p className="text-gray-600 leading-relaxed text-lg">
              Access your tasks from anywhere, on any device, at any time with cloud sync.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
