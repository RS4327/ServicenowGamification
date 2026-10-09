import React, { createContext, useContext, useState, useEffect } from 'react'



export const themes = {

  cyber: {

    id: 'cyber',

    name: 'Cyber Dark',

    icon: '🌌',

    pageBg: '#050b1a',

    sidebarBg: '#030712',

    topbarBg: 'rgba(5,11,26,0.85)',

    cardBg: 'rgba(255,255,255,0.04)',

    cardBorder: 'rgba(255,255,255,0.1)',

    cardShadow: '0 4px 24px rgba(0,0,0,0.4)',

    accent: '#00d4ff',

    accentSecondary: '#7c3aed',

    accentGrad: 'linear-gradient(135deg, #00d4ff, #7c3aed)',

    textPrimary: '#f1f5f9',

    textSecondary: '#94a3b8',

    textMuted: '#475569',

    success: '#10b981',

    warning: '#f59e0b',

    danger: '#ef4444',

    navActiveBg: 'rgba(0,212,255,0.08)',

    navActiveText: '#00d4ff',

    navActiveBorder: '#00d4ff',

    navInactiveText: '#475569',

    navHoverBg: 'rgba(255,255,255,0.04)',

    inputBg: 'rgba(255,255,255,0.05)',

    inputBorder: 'rgba(255,255,255,0.1)',

    topbarBorder: 'rgba(255,255,255,0.06)',

    tableRowAlt: 'rgba(255,255,255,0.02)',

    tableRowHover: 'rgba(0,212,255,0.05)',

    chartGrid: 'rgba(255,255,255,0.05)',

  },

  midnight: {

    id: 'midnight',

    name: 'Midnight Blue',

    icon: '🌙',

    pageBg: '#0a0e27',

    sidebarBg: '#050819',

    topbarBg: 'rgba(10,14,39,0.85)',

    cardBg: 'rgba(79,158,255,0.05)',

    cardBorder: 'rgba(79,158,255,0.15)',

    cardShadow: '0 4px 24px rgba(0,0,50,0.4)',

    accent: '#4f9eff',

    accentSecondary: '#38bdf8',

    accentGrad: 'linear-gradient(135deg, #4f9eff, #38bdf8)',

    textPrimary: '#e2e8f0',

    textSecondary: '#94a3b8',

    textMuted: '#64748b',

    success: '#34d399',

    warning: '#fbbf24',

    danger: '#f87171',

    navActiveBg: 'rgba(79,158,255,0.1)',

    navActiveText: '#4f9eff',

    navActiveBorder: '#4f9eff',

    navInactiveText: '#4a6080',

    navHoverBg: 'rgba(79,158,255,0.05)',

    inputBg: 'rgba(79,158,255,0.05)',

    inputBorder: 'rgba(79,158,255,0.2)',

    topbarBorder: 'rgba(79,158,255,0.1)',

    tableRowAlt: 'rgba(79,158,255,0.03)',

    tableRowHover: 'rgba(79,158,255,0.07)',

    chartGrid: 'rgba(79,158,255,0.08)',

  },

  emerald: {

    id: 'emerald',

    name: 'Emerald',

    icon: '💚',

    pageBg: '#030f0f',

    sidebarBg: '#020a0a',

    topbarBg: 'rgba(3,15,15,0.85)',

    cardBg: 'rgba(16,185,129,0.05)',

    cardBorder: 'rgba(16,185,129,0.15)',

    cardShadow: '0 4px 24px rgba(0,0,0,0.4)',

    accent: '#10b981',

    accentSecondary: '#06b6d4',

    accentGrad: 'linear-gradient(135deg, #10b981, #06b6d4)',

    textPrimary: '#ecfdf5',

    textSecondary: '#6ee7b7',

    textMuted: '#3d8f70',

    success: '#34d399',

    warning: '#fbbf24',

    danger: '#f87171',

    navActiveBg: 'rgba(16,185,129,0.1)',

    navActiveText: '#10b981',

    navActiveBorder: '#10b981',

    navInactiveText: '#2d6e57',

    navHoverBg: 'rgba(16,185,129,0.05)',

    inputBg: 'rgba(16,185,129,0.05)',

    inputBorder: 'rgba(16,185,129,0.2)',

    topbarBorder: 'rgba(16,185,129,0.1)',

    tableRowAlt: 'rgba(16,185,129,0.03)',

    tableRowHover: 'rgba(16,185,129,0.07)',

    chartGrid: 'rgba(16,185,129,0.08)',

  },

  sunset: {

    id: 'sunset',

    name: 'Sunset',

    icon: '🌅',

    pageBg: '#150a05',

    sidebarBg: '#0d0602',

    topbarBg: 'rgba(21,10,5,0.85)',

    cardBg: 'rgba(249,115,22,0.05)',

    cardBorder: 'rgba(249,115,22,0.15)',

    cardShadow: '0 4px 24px rgba(0,0,0,0.4)',

    accent: '#f97316',

    accentSecondary: '#ec4899',

    accentGrad: 'linear-gradient(135deg, #f97316, #ec4899)',

    textPrimary: '#fff7ed',

    textSecondary: '#fed7aa',

    textMuted: '#7c4a20',

    success: '#10b981',

    warning: '#fbbf24',

    danger: '#ef4444',

    navActiveBg: 'rgba(249,115,22,0.1)',

    navActiveText: '#f97316',

    navActiveBorder: '#f97316',

    navInactiveText: '#6b3a1a',

    navHoverBg: 'rgba(249,115,22,0.05)',

    inputBg: 'rgba(249,115,22,0.05)',

    inputBorder: 'rgba(249,115,22,0.2)',

    topbarBorder: 'rgba(249,115,22,0.1)',

    tableRowAlt: 'rgba(249,115,22,0.03)',

    tableRowHover: 'rgba(249,115,22,0.07)',

    chartGrid: 'rgba(249,115,22,0.08)',

  },

  light: {

    id: 'light',

    name: 'Light Mode',

    icon: '☀️',

    pageBg: '#f1f5f9',

    sidebarBg: '#ffffff',

    topbarBg: 'rgba(255,255,255,0.95)',

    cardBg: '#ffffff',

    cardBorder: 'rgba(0,0,0,0.08)',

    cardShadow: '0 2px 12px rgba(0,0,0,0.08)',

    accent: '#3b82f6',

    accentSecondary: '#7c3aed',

    accentGrad: 'linear-gradient(135deg, #3b82f6, #7c3aed)',

    textPrimary: '#0f172a',

    textSecondary: '#475569',

    textMuted: '#94a3b8',

    success: '#10b981',

    warning: '#f59e0b',

    danger: '#ef4444',

    navActiveBg: 'rgba(59,130,246,0.1)',

    navActiveText: '#3b82f6',

    navActiveBorder: '#3b82f6',

    navInactiveText: '#64748b',

    navHoverBg: 'rgba(0,0,0,0.04)',

    inputBg: '#f8fafc',

    inputBorder: '#e2e8f0',

    topbarBorder: 'rgba(0,0,0,0.1)',

    tableRowAlt: '#f8fafc',

    tableRowHover: '#eff6ff',

    chartGrid: 'rgba(0,0,0,0.06)',

  },

}



const ThemeContext = createContext(null)



export function ThemeProvider({ children }) {

  const [themeId, setThemeId] = useState(() => localStorage.getItem('gd-theme') || 'cyber')

  const theme = themes[themeId] || themes.cyber



  useEffect(() => {

    localStorage.setItem('gd-theme', themeId)

    document.body.style.background = theme.pageBg

    document.body.style.color = theme.textPrimary

    const root = document.documentElement

    root.style.setProperty('--accent', theme.accent)

    root.style.setProperty('--accent-grad', theme.accentGrad)

    root.style.setProperty('--page-bg', theme.pageBg)

    root.style.setProperty('--card-bg', theme.cardBg)

    root.style.setProperty('--card-border', theme.cardBorder)

    root.style.setProperty('--text-primary', theme.textPrimary)

    root.style.setProperty('--text-secondary', theme.textSecondary)

    root.style.setProperty('--chart-grid', theme.chartGrid)

  }, [themeId, theme])



  return (

    <ThemeContext.Provider value={{ theme, themeId, setThemeId }}>

      {children}

    </ThemeContext.Provider>

  )

}



export function useTheme() {

  return useContext(ThemeContext)

}

