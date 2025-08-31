/**
 * Application entry point that:
 * - Initializes React application
 * - Sets up root DOM element
 * - Renders the main App component
 * - Wraps app in StrictMode for development checks
 */

// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
