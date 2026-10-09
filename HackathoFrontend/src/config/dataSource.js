/**

 * Data-Source Configuration

 *

 * Controls where the dashboard reads data from:

 *   'snapshot'  → Repository snapshot (sampleData.js) — read-only, versioned, demo-safe

 *   'database'  → Primary database via REST API (falls back to snapshot if unavailable)

 *

 * Set via environment variable:

 *   VITE_DATA_SOURCE=snapshot   (default — safe for demos & hackathon)

 *   VITE_DATA_SOURCE=database   (production with live API)

 */



export const DATA_SOURCE = import.meta.env.VITE_DATA_SOURCE || 'snapshot'

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''



// ── Active source tracker (reactive, for UI indicator) ────────────────────────

// Possible values:

//   'snapshot'          → configured snapshot mode

//   'database'          → live database, healthy

//   'snapshot-fallback' → database mode but DB unreachable → fell back to snapshot



let _activeSource = DATA_SOURCE === 'snapshot' ? 'snapshot' : 'connecting'

const _listeners = new Set()



export function recordSourceUsed(src) {

  if (_activeSource === src) return

  _activeSource = src

  _listeners.forEach(fn => fn(src))

}



export function getActiveSource() {

  return _activeSource

}



/** Subscribe to source changes. Returns unsubscribe function. */

export function onSourceChange(fn) {

  _listeners.add(fn)

  return () => _listeners.delete(fn)

}



// ── Human-readable labels / styles for UI badge ───────────────────────────────

export const SOURCE_META = {

  connecting: {

    label: 'Connecting…',

    icon: '⟳',

    color: '#f59e0b',

    description: 'Attempting database connection',

  },

  database: {

    label: 'Database',

    icon: '🗄️',

    color: '#10b981',

    description: 'Live data from primary database',

  },

  snapshot: {

    label: 'Snapshot',

    icon: '📦',

    color: '#3b82f6',

    description: 'Versioned repository snapshot (demo mode)',

  },

  'snapshot-fallback': {

    label: 'DB Offline',

    icon: '⚠️',

    color: '#ef4444',

    description: 'Database unreachable — using repository snapshot',

  },

}

