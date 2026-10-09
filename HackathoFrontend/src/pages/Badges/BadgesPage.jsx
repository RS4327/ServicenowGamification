import React from 'react'

import { useTheme } from '../../context/ThemeContext.jsx'

import { badgesEarned } from '../../data/sampleData.js'



const lockedBadges = [

  { id: 4, name: 'Speed Demon', description: 'Resolve 10 incidents in under 30 minutes each' },

  { id: 5, name: 'Perfect Week', description: 'Achieve 100% FCR and SLA for an entire week' },

  { id: 6, name: 'Century Club', description: 'Resolve 100 incidents in a single month' },

]



const badgeIcons = {

  'Quick Resolve': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,

  'FCR Achiever': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>,

  'SLA Watcher': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,

  'Speed Demon': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>,

  'Perfect Week': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>,

  'Century Club': <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>,

}



function BadgeCard({ badge, locked, theme }) {

  const color = locked ? theme.textMuted : (badge.color || theme.accent)

  return (

    <div

      style={{

        background: theme.cardBg, borderRadius: '16px',

        border: locked ? `1px dashed ${theme.cardBorder}` : `1px solid ${color}30`,

        boxShadow: locked ? 'none' : `0 0 20px ${color}10`,

        backdropFilter: 'blur(20px)',

        padding: '24px', textAlign: 'center',

        opacity: locked ? 0.55 : 1,

        position: 'relative',

        transition: 'transform 0.2s, box-shadow 0.2s',

      }}

      onMouseEnter={e => { if (!locked) { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = `0 12px 32px ${color}25` } }}

      onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = locked ? 'none' : `0 0 20px ${color}10` }}

    >

      {/* Status pill */}

      <div style={{

        position: 'absolute', top: '12px', right: '12px',

        background: locked ? `${theme.textMuted}15` : `${theme.success}18`,

        border: `1px solid ${locked ? theme.cardBorder : theme.success + '30'}`,

        borderRadius: '6px', padding: '3px 8px',

        fontSize: '11px', fontWeight: 700,

        color: locked ? theme.textMuted : theme.success,

        display: 'flex', alignItems: 'center', gap: '4px',

      }}>

        {locked

          ? <><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> Locked</>

          : <><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg> Earned</>

        }

      </div>



      {/* Icon */}

      <div style={{

        width: '72px', height: '72px',

        background: locked ? `${theme.textMuted}10` : `${color}18`,

        border: locked ? `2px dashed ${theme.cardBorder}` : `2px solid ${color}35`,

        borderRadius: '50%',

        display: 'flex', alignItems: 'center', justifyContent: 'center',

        margin: '0 auto 16px',

        color: locked ? theme.textMuted : color,

        boxShadow: locked ? 'none' : `0 0 16px ${color}25`,

      }}>

        {badgeIcons[badge.name]}

      </div>



      <h3 style={{ fontSize: '15px', fontWeight: 700, color: locked ? theme.textMuted : theme.textPrimary, marginBottom: '6px' }}>

        {badge.name}

      </h3>

      <p style={{ fontSize: '12px', color: theme.textSecondary, lineHeight: 1.5 }}>

        {badge.description}

      </p>

    </div>

  )

}



export default function BadgesPage() {

  const { theme } = useTheme()



  return (

    <div>

      <div style={{ marginBottom: '24px' }}>

        <h2 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '4px' }}>

          My <span style={{ color: theme.accent }}>Badges</span>

        </h2>

        <p style={{ color: theme.textSecondary, fontSize: '14px' }}>Achievements earned for outstanding performance</p>

      </div>



      {/* Stats row */}

      <div style={{ display: 'flex', gap: '16px', marginBottom: '28px' }}>

        {[

          { label: 'Earned', value: badgesEarned.length, color: theme.success },

          { label: 'Locked', value: lockedBadges.length, color: theme.textMuted },

          { label: 'Total Available', value: badgesEarned.length + lockedBadges.length, color: theme.accent },

        ].map(s => (

          <div key={s.label} style={{

            background: theme.cardBg, borderRadius: '12px',

            border: `1px solid ${theme.cardBorder}`, boxShadow: theme.cardShadow,

            backdropFilter: 'blur(20px)',

            padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '14px',

          }}>

            <div style={{

              width: '44px', height: '44px',

              background: `${s.color}18`, border: `1px solid ${s.color}30`,

              borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',

              fontSize: '20px', fontWeight: 800, color: s.color,

            }}>

              {s.value}

            </div>

            <span style={{ fontSize: '14px', fontWeight: 500, color: theme.textSecondary }}>{s.label}</span>

          </div>

        ))}

      </div>



      {/* Earned badges */}

      <div style={{ marginBottom: '28px' }}>

        <h3 style={{ fontSize: '15px', fontWeight: 700, color: theme.textPrimary, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>

          <span style={{ color: theme.success }}>

            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>

          </span>

          Earned Badges

        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>

          {badgesEarned.map(badge => <BadgeCard key={badge.id} badge={badge} locked={false} theme={theme} />)}

        </div>

      </div>



      {/* Locked badges */}

      <div>

        <h3 style={{ fontSize: '15px', fontWeight: 700, color: theme.textPrimary, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>

          <span style={{ color: theme.textMuted }}>

            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>

          </span>

          Locked Badges

        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>

          {lockedBadges.map(badge => <BadgeCard key={badge.id} badge={badge} locked={true} theme={theme} />)}

        </div>

      </div>

    </div>

  )

}

