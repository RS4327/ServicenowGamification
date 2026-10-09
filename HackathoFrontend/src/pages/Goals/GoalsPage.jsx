import React from 'react'

import { useTheme } from '../../context/ThemeContext.jsx'



const goals = [

  { id: 1, title: 'FCR Goal', description: 'Achieve First Contact Resolution rate of 80%', current: 57.14, target: 80, unit: '%', color: '#f59e0b', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> },

  { id: 2, title: 'SLA Compliance Goal', description: 'Maintain SLA compliance rate above 90%', current: 0, target: 90, unit: '%', color: '#10b981', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> },

  { id: 3, title: 'Incidents Resolved', description: 'Resolve 10 incidents this month', current: 4, target: 10, unit: '', color: '#3b82f6', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg> },

  { id: 4, title: 'MTTR Reduction', description: 'Reduce MTTR below 200 hours', current: 359.44, target: 200, unit: 'hrs', color: '#8b5cf6', invert: true, icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> },

  { id: 5, title: 'Training Completion', description: 'Complete 3 mandatory training modules', current: 1, target: 3, unit: '', color: '#ec4899', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg> },

  { id: 6, title: 'Badges Earned', description: 'Earn 5 performance badges this quarter', current: 3, target: 5, unit: '', color: '#f97316', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg> },

]



function GoalCard({ goal, theme }) {

  const pct = goal.invert

    ? Math.max(0, Math.min(100, ((goal.target - goal.current) / goal.target) * 100))

    : Math.min(100, (goal.current / goal.target) * 100)

  const displayPct = Math.round(pct)

  const isComplete = displayPct >= 100

  const barColor = isComplete ? theme.success : displayPct > 60 ? goal.color : displayPct > 30 ? theme.warning : theme.danger



  return (

    <div style={{

      background: theme.cardBg, borderRadius: '16px',

      border: `1px solid ${theme.cardBorder}`,

      borderTop: `3px solid ${goal.color}`,

      boxShadow: theme.cardShadow, backdropFilter: 'blur(20px)',

      padding: '22px',

    }}>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>

          <div style={{

            width: '40px', height: '40px', background: `${goal.color}18`,

            border: `1px solid ${goal.color}30`,

            borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',

            color: goal.color, flexShrink: 0,

          }}>

            {goal.icon}

          </div>

          <div>

            <h3 style={{ fontSize: '14px', fontWeight: 700, color: theme.textPrimary, marginBottom: '2px' }}>{goal.title}</h3>

            <p style={{ fontSize: '12px', color: theme.textSecondary }}>{goal.description}</p>

          </div>

        </div>

        {isComplete && (

          <span style={{

            background: `${theme.success}18`, color: theme.success,

            border: `1px solid ${theme.success}30`,

            borderRadius: '6px', padding: '3px 10px',

            fontSize: '11px', fontWeight: 700, flexShrink: 0,

          }}>

            ✓ Done

          </span>

        )}

      </div>



      {/* Progress bar */}

      <div style={{ marginBottom: '10px' }}>

        <div style={{ height: '8px', background: `${theme.cardBorder}`, borderRadius: '4px', overflow: 'hidden', marginBottom: '8px' }}>

          <div style={{

            height: '100%', width: `${displayPct}%`,

            background: barColor,

            borderRadius: '4px', transition: 'width 0.8s ease',

            boxShadow: `0 0 6px ${barColor}60`,

          }} />

        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

          <div style={{ fontSize: '13px', color: theme.textSecondary }}>

            <span style={{ fontWeight: 700, color: theme.textPrimary }}>{goal.current}{goal.unit}</span>

            {' / '}

            <span>{goal.target}{goal.unit}</span>

          </div>

          <span style={{ fontSize: '14px', fontWeight: 700, color: barColor }}>{displayPct}%</span>

        </div>

      </div>



      {/* Status */}

      <div style={{

        display: 'flex', alignItems: 'center', gap: '6px',

        padding: '8px 12px',

        background: isComplete ? `${theme.success}12` : displayPct > 50 ? `${theme.success}08` : `${theme.warning}10`,

        border: `1px solid ${isComplete ? theme.success : displayPct > 50 ? theme.success : theme.warning}25`,

        borderRadius: '8px',

      }}>

        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={isComplete || displayPct > 50 ? theme.success : theme.warning} strokeWidth="2.5">

          {isComplete ? <polyline points="20 6 9 17 4 12"/> : <path d="M12 9v4M12 17h.01"/>}

        </svg>

        <span style={{ fontSize: '12px', fontWeight: 600, color: isComplete || displayPct > 50 ? theme.success : theme.warning }}>

          {isComplete ? 'Goal achieved!' : displayPct > 50 ? 'On track' : 'Needs attention'}

        </span>

      </div>

    </div>

  )

}



export default function GoalsPage() {

  const { theme } = useTheme()



  const completed = goals.filter(g => {

    const pct = g.invert

      ? Math.max(0, Math.min(100, ((g.target - g.current) / g.target) * 100))

      : Math.min(100, (g.current / g.target) * 100)

    return pct >= 100

  }).length



  return (

    <div>

      <div style={{ marginBottom: '24px' }}>

        <h2 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '4px' }}>

          My <span style={{ color: theme.accent }}>Goals</span>

        </h2>

        <p style={{ color: theme.textSecondary, fontSize: '14px' }}>Track progress toward your performance targets</p>

      </div>



      {/* Summary */}

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>

        {[

          { label: 'Total Goals', value: goals.length, color: theme.accent },

          { label: 'Completed', value: completed, color: theme.success },

          { label: 'In Progress', value: goals.length - completed, color: theme.warning },

        ].map(s => (

          <div key={s.label} style={{

            background: theme.cardBg, borderRadius: '12px',

            border: `1px solid ${theme.cardBorder}`, boxShadow: theme.cardShadow,

            backdropFilter: 'blur(20px)',

            padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '14px', flex: 1,

          }}>

            <div style={{

              width: '48px', height: '48px',

              background: `${s.color}18`, border: `1px solid ${s.color}30`,

              borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center',

              fontSize: '22px', fontWeight: 800, color: s.color,

            }}>

              {s.value}

            </div>

            <span style={{ fontSize: '14px', fontWeight: 500, color: theme.textSecondary }}>{s.label}</span>

          </div>

        ))}

      </div>



      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {goals.map(goal => <GoalCard key={goal.id} goal={goal} theme={theme} />)}

      </div>

    </div>

  )

}

