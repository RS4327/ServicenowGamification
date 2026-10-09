import { useState, useEffect } from 'react'
import { getActiveSource, onSourceChange } from '../config/dataSource.js'
 
/** Returns the current active data source: 'snapshot' | 'database' | 'snapshot-fallback' | 'connecting' */
export function useDataSource() {
  const [source, setSource] = useState(getActiveSource())
  useEffect(() => onSourceChange(setSource), [])
  return source
}