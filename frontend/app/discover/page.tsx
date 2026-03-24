'use client';

import { useState } from 'react';
import DiscoveryFeed from '@/components/DiscoveryFeed';
import FilterPanel from '@/components/FilterPanel';

export default function DiscoverPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Discover Recipes
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Explore public recipes shared by the community
          </p>
        </div>

        {/* Filter Toggle Button */}
        <div className="mb-6">
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
              />
            </svg>
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mb-6">
            <FilterPanel
              onFilterChange={(filters) => {
                // Handle filter changes if needed
                console.log('Filters changed:', filters);
              }}
            />
          </div>
        )}

        {/* Discovery Feed */}
        <DiscoveryFeed searchQuery={searchQuery} />
      </div>
    </div>
  );
}
