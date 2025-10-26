import React from 'react';
import SafePathApp from '@/components/safe-path-app'
import ErrorBoundary from '@/components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <SafePathApp />
    </ErrorBoundary>
  )
}

export default App
