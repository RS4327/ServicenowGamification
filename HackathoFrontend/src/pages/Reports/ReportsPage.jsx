import React from 'react'

import { useTheme } from '../../context/ThemeContext.jsx'



export default function ReportsPage() {

  const { theme } = useTheme()



  return (

    <div>

      <div style={{ marginBottom: '24px' }}>

        <h2 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '4px' }}>

          Reports <span style={{ color: theme.accent }}>Center</span>

        </h2>

        <p style={{ color: theme.textSecondary, fontSize: '14px' }}>Exportable performance reports</p>

      </div>



      <div style={{

        background: theme.cardBg, borderRadius: '14px',

        border: `1px solid ${theme.cardBorder}`, boxShadow: theme.cardShadow,

        backdropFilter: 'blur(20px)',

        padding: '80px 24px',

        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',

        textAlign: 'center',

      }}>

        <div style={{

          width: '80px', height: '80px',

          background: `${theme.accent}18`, border: `2px solid ${theme.accent}30`,

          borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center',

          color: theme.accent, marginBottom: '20px',

          boxShadow: `0 0 24px ${theme.accent}20`,

        }}>

          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">

            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>

            <polyline points="14 2 14 8 20 8"/>

            <line x1="16" y1="13" x2="8" y2="13"/>

            <line x1="16" y1="17" x2="8" y2="17"/>

          </svg>

        </div>

        <h3 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '8px' }}>

          Reports Coming Soon

        </h3>

        <p style={{ fontSize: '14px', color: theme.textSecondary, maxWidth: '380px', lineHeight: 1.7, marginBottom: '28px' }}>

          Powerful report generation and export capabilities are on the way. PDF and CSV exports of your team performance data will be available shortly.

        </p>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>

          {['PDF Export', 'CSV Export', 'Scheduled Reports', 'Email Delivery'].map(feature => (

            <span key={feature} style={{

              background: `${theme.accent}12`,

              border: `1px solid ${theme.accent}25`,

              color: theme.accent,

              borderRadius: '20px', padding: '6px 16px',

              fontSize: '13px', fontWeight: 600,

            }}>

              {feature}

            </span>

          ))}

        </div>

      </div>

    </div>

  )

}

