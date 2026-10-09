import React, { useState, useEffect, useRef, useCallback } from 'react'

import {

  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,

  XAxis, YAxis, CartesianGrid, Tooltip, Legend,

  LabelList, ResponsiveContainer

} from 'recharts'

import * as sampleData from '../../data/sampleData.js'

import {

  getManagerStats, getIncidentsOverTime, getSlaTrend, getIncidentsByState, getTopAgents,

  getMttrByPriority, getSlaByPriority, getRecentAlerts, getGamificationSummary,

  getTopBadges, getPerformanceDistribution

} from '../../services/api.js'

import { useTheme } from '../../context/ThemeContext.jsx'



// ── Animated counter hook ─────────────────────────────────────────────────────



function useAnimatedCounter(target, duration = 1500) {

  const [count, setCount] = useState(0)

  const rafRef = useRef(null)



  useEffect(() => {

    let startTime = null

    const startValue = 0

    const endValue = parseFloat(target)



    function step(timestamp) {

      if (!startTime) startTime = timestamp

      const elapsed = timestamp - startTime

      const progress = Math.min(elapsed / duration, 1)

      const eased = 1 - Math.pow(1 - progress, 3)

      const current = startValue + (endValue - startValue) * eased

      setCount(current)

      if (progress < 1) {

        rafRef.current = requestAnimationFrame(step)

      }

    }



    rafRef.current = requestAnimationFrame(step)

    return () => {

      if (rafRef.current) cancelAnimationFrame(rafRef.current)

    }

  }, [target, duration])



  return count

}



// ── KPI Card ──────────────────────────────────────────────────────────────────



function KpiCard({ label, value, decimals = 0, suffix = '', color, icon, trend, trendUp, period, delay }) {

  const { theme } = useTheme()

  const count = useAnimatedCounter(parseFloat(value))

  const [hovered, setHovered] = useState(false)



  const formatted = decimals > 0 ? count.toFixed(decimals) : Math.floor(count).toString()



  return (

    <div

      onMouseEnter={() => setHovered(true)}

      onMouseLeave={() => setHovered(false)}

      style={{

        background: theme.cardBg,

        backdropFilter: 'blur(20px)',

        WebkitBackdropFilter: 'blur(20px)',

        border: `1px solid ${theme.cardBorder}`,

        borderRadius: '16px',

        padding: '20px',

        flex: 1,

        minWidth: 0,

        position: 'relative',

        overflow: 'hidden',

        cursor: 'default',

        transition: 'all 0.3s',

        transform: hovered ? 'translateY(-4px)' : 'translateY(0)',

        boxShadow: hovered ? `0 12px 40px ${color}26` : theme.cardShadow,

      }}

    >

      {/* Header row: label left, icon right — no overlap */}

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '10px' }}>

        <div style={{ fontSize: '11px', fontWeight: 600, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.8px', lineHeight: 1.4 }}>

          {label}

        </div>

        <div style={{

          width: '36px', height: '36px', borderRadius: '10px', flexShrink: 0,

          background: `${color}18`, border: `1px solid ${color}30`,

          display: 'flex', alignItems: 'center', justifyContent: 'center',

          boxShadow: `0 0 12px ${color}20`,

        }}>

          {icon}

        </div>

      </div>



      {/* Number — full width, no icon overlap */}

      <div style={{ fontSize: '28px', fontWeight: 800, color: theme.textPrimary, lineHeight: 1, marginBottom: '10px', fontVariantNumeric: 'tabular-nums' }}>

        {formatted}{suffix}

      </div>



      {/* Trend badge + period */}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>

          <div style={{

            display: 'flex', alignItems: 'center', gap: '4px',

            padding: '2px 8px', borderRadius: '20px',

            background: trendUp ? `${theme.success}1a` : `${theme.danger}1a`,

            border: `1px solid ${trendUp ? theme.success : theme.danger}33`,

            fontSize: '12px', fontWeight: 700,

            color: trendUp ? theme.success : theme.danger,

          }}>

            {trendUp ? '↑' : '↓'} {trend}%

          </div>

        </div>

        {period && (

          <div style={{ fontSize: '10px', color: theme.textMuted }}>vs {period}</div>

        )}

      </div>



      {/* Bottom accent line */}

      <div style={{

        position: 'absolute', bottom: 0, left: 0, right: 0,

        height: '3px',

        background: `linear-gradient(90deg, ${color}, transparent)`,

        opacity: hovered ? 1 : 0.5,

        transition: 'opacity 0.3s',

      }} />

    </div>

  )

}



// ── Chart Tooltip ─────────────────────────────────────────────────────────────



function ChartTooltip({ active, payload, label }) {

  const { theme } = useTheme()

  if (!active || !payload || !payload.length) return null

  return (

    <div style={{

      background: theme.sidebarBg,

      border: `1px solid ${theme.cardBorder}`,

      borderRadius: '10px',

      color: theme.textPrimary,

      fontSize: '12px',

      padding: '8px 12px',

    }}>

      <div style={{ fontWeight: 700, marginBottom: '4px', color: theme.textSecondary }}>{label}</div>

      {payload.map((p, i) => (

        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>

          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: p.color }} />

          <span style={{ color: theme.textPrimary, fontWeight: 600 }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}</span>

        </div>

      ))}

    </div>

  )

}



// ── Custom Pie Label ──────────────────────────────────────────────────────────



function renderCustomPieLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {

  if (percent < 0.05) return null

  const RADIAN = Math.PI / 180

  const radius = innerRadius + (outerRadius - innerRadius) * 0.5

  const x = cx + radius * Math.cos(-midAngle * RADIAN)

  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  return (

    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={700}>

      {`${(percent * 100).toFixed(0)}%`}

    </text>

  )

}



// ── Agent Initials Avatar ─────────────────────────────────────────────────────



function AgentAvatar({ name, color }) {

  const initials = name

    .split(' ')

    .filter(Boolean)

    .slice(0, 2)

    .map(w => w[0].toUpperCase())

    .join('')

  return (

    <div style={{

      width: '32px', height: '32px', borderRadius: '50%',

      background: `linear-gradient(135deg, ${color}cc, ${color}66)`,

      display: 'flex', alignItems: 'center', justifyContent: 'center',

      fontSize: '12px', fontWeight: 700, color: '#fff',

      flexShrink: 0,

    }}>

      {initials.slice(0, 2)}

    </div>

  )

}



// ── Badge Icon ────────────────────────────────────────────────────────────────



function BadgeIcon({ type, color }) {

  if (type === 'star') return (

    <svg width="16" height="16" viewBox="0 0 24 24" fill={color} stroke="none">

      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />

    </svg>

  )

  if (type === 'check') return (

    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">

      <polyline points="20 6 9 17 4 12" />

    </svg>

  )

  return (

    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />

    </svg>

  )

}



// ── Main Component ────────────────────────────────────────────────────────────



export default function ManagerDashboard() {

  const { theme } = useTheme()



  // glass card style

  const glassCard = {

    background: theme.cardBg,

    backdropFilter: 'blur(20px)',

    WebkitBackdropFilter: 'blur(20px)',

    border: `1px solid ${theme.cardBorder}`,

    borderRadius: '16px',

  }



  const tooltipStyle = {

    background: theme.sidebarBg,

    border: '1px solid ' + theme.cardBorder,

    borderRadius: '10px',

    color: theme.textPrimary,

    fontSize: '12px',

    padding: '8px 12px',

  }



  const axisTickStyle = { fontSize: 11, fill: theme.textMuted }

  const sectionHeader = { fontSize: '14px', fontWeight: 700, color: theme.textPrimary, marginBottom: '16px' }

  const linkStyle = { fontSize: '13px', color: theme.accent, cursor: 'pointer', fontWeight: 600, textDecoration: 'none', display: 'inline-block', marginTop: '12px' }



  // ── State ──────────────────────────────────────────────────────────────────



  const [stats, setStats] = useState(sampleData.managerStats)

  const [incidentsOverTime, setIncidentsOverTime] = useState(sampleData.incidentsOverTime)

  const [slaTrend, setSlaTrend] = useState(sampleData.slaTrend)

  const [incidentsByState, setIncidentsByState] = useState(sampleData.incidentsByState)

  const [topAgents, setTopAgents] = useState(sampleData.topAgentsByFCR)

  const [alerts, setAlerts] = useState(sampleData.recentAlerts)

  const [gamSummary, setGamSummary] = useState(sampleData.gamificationSummary)

  const [topBadgesData, setTopBadgesData] = useState(sampleData.topBadges)

  const [perfDistribution, setPerfDistribution] = useState(sampleData.performanceDistribution)

  const [mttrByPriority, setMttrByPriority] = useState(sampleData.mttrByPriority)

  const [slaByPriority, setSlaByPriority] = useState(sampleData.slaByPriority)



  const [loading, setLoading] = useState(true)

  const [refreshing, setRefreshing] = useState(false)

  const [lastRefreshed, setLastRefreshed] = useState(null)



  // ── Unified fetch — called on mount and on manual Refresh ─────────────────



  const fetchAll = useCallback(async (isRefresh = false) => {

    if (isRefresh) setRefreshing(true)

    else setLoading(true)



    await Promise.all([

      getManagerStats().then(setStats).catch(() => {}),

      getIncidentsOverTime().then(setIncidentsOverTime).catch(() => {}),

      getSlaTrend().then(setSlaTrend).catch(() => {}),

      getIncidentsByState().then(setIncidentsByState).catch(() => {}),

      getTopAgents().then(setTopAgents).catch(() => {}),

      getMttrByPriority().then(setMttrByPriority).catch(() => {}),

      getSlaByPriority().then(setSlaByPriority).catch(() => {}),

      getRecentAlerts().then(setAlerts).catch(() => {}),

      getGamificationSummary().then(setGamSummary).catch(() => {}),

      getTopBadges().then(setTopBadgesData).catch(() => {}),

      getPerformanceDistribution().then(setPerfDistribution).catch(() => {}),

    ])



    setLastRefreshed(new Date().toLocaleTimeString())

    setLoading(false)

    setRefreshing(false)

  }, [])



  useEffect(() => { fetchAll() }, [fetchAll])



  // ── Pie colors for incidents by state ─────────────────────────────────────



  const stateColors = ['#3b82f6', '#10b981', '#f59e0b']



  // ── Performance distribution colors ───────────────────────────────────────



  const perfColors = ['#10b981', '#3b82f6', '#f59e0b']



  // ── Alert icon helper ──────────────────────────────────────────────────────



  function AlertIcon({ level }) {

    if (level === 'critical') return (

      <div style={{ width: 32, height: 32, borderRadius: '8px', background: `${theme.danger}18`, border: `1px solid ${theme.danger}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>

        <span style={{ fontSize: '16px', color: theme.danger }}>⚠</span>

      </div>

    )

    if (level === 'warning') return (

      <div style={{ width: 32, height: 32, borderRadius: '8px', background: `${theme.warning}18`, border: `1px solid ${theme.warning}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>

        <span style={{ fontSize: '16px', color: theme.warning }}>⚠</span>

      </div>

    )

    return (

      <div style={{ width: 32, height: 32, borderRadius: '8px', background: `${theme.accent}18`, border: `1px solid ${theme.accent}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>

        <span style={{ fontSize: '16px', color: theme.accent }}>ℹ</span>

      </div>

    )

  }



  // ── FCR color helper ───────────────────────────────────────────────────────



  function fcrColor(v) {

    if (v >= 80) return theme.success

    if (v >= 50) return theme.warning

    return theme.danger

  }



  // ── Loading skeleton ───────────────────────────────────────────────────────



  if (loading) {

    return (

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* skeleton hero */}

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

          <div>

            <div style={{ width: '260px', height: '28px', borderRadius: '8px', background: `${theme.cardBorder}`, marginBottom: '8px', animation: 'shimmer 1.5s infinite' }} />

            <div style={{ width: '160px', height: '14px', borderRadius: '6px', background: `${theme.cardBorder}` }} />

          </div>

          <div style={{ width: '100px', height: '36px', borderRadius: '10px', background: `${theme.cardBorder}` }} />

        </div>

        {/* skeleton KPI cards */}

        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>

          {Array.from({ length: 6 }).map((_, i) => (

            <div key={i} style={{ flex: '1 1 140px', height: '110px', borderRadius: '16px', background: theme.cardBg, border: `1px solid ${theme.cardBorder}`, animation: 'shimmer 1.5s infinite' }} />

          ))}

        </div>

        {/* skeleton chart row */}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>

          {Array.from({ length: 3 }).map((_, i) => (

            <div key={i} style={{ height: '260px', borderRadius: '16px', background: theme.cardBg, border: `1px solid ${theme.cardBorder}`, animation: 'shimmer 1.5s infinite' }} />

          ))}

        </div>

        <div style={{ textAlign: 'center', color: theme.textMuted, fontSize: '13px', paddingBottom: '40px' }}>

          Loading dashboard data…

        </div>

      </div>

    )

  }



  // ── Render ─────────────────────────────────────────────────────────────────



  return (

    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>



      {/* ── Hero ─────────────────────────────────────────────────────────── */}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>

        <div>

          <h1 style={{ fontSize: '26px', fontWeight: 800, color: theme.textPrimary, margin: 0, marginBottom: '4px' }}>

            Operations <span style={{ color: theme.accent }}>Overview</span>

          </h1>

          <div style={{ fontSize: '13px', color: theme.textMuted }}>

            {stats.period}

            {lastRefreshed && <span style={{ marginLeft: '10px', color: theme.textMuted, opacity: 0.6 }}>· Updated {lastRefreshed}</span>}

          </div>

        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>

          {/* Refresh button */}

          <button

            onClick={() => fetchAll(true)}

            disabled={refreshing}

            style={{

              display: 'flex', alignItems: 'center', gap: '6px',

              padding: '8px 16px', borderRadius: '10px',

              background: theme.inputBg, border: `1px solid ${theme.inputBorder}`,

              color: theme.textSecondary, fontSize: '13px', fontWeight: 600,

              cursor: refreshing ? 'not-allowed' : 'pointer', opacity: refreshing ? 0.6 : 1,

              transition: 'all 0.2s',

            }}

            onMouseEnter={e => { if (!refreshing) { e.currentTarget.style.borderColor = theme.accent; e.currentTarget.style.color = theme.accent } }}

            onMouseLeave={e => { e.currentTarget.style.borderColor = theme.inputBorder; e.currentTarget.style.color = theme.textSecondary }}

          >

            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"

              style={{ animation: refreshing ? 'spin 0.8s linear infinite' : 'none' }}>

              <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>

              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>

            </svg>

            {refreshing ? 'Refreshing…' : 'Refresh'}

          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: `${theme.success}14`, border: `1px solid ${theme.success}33`, borderRadius: '30px' }}>

            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: theme.success }} />

            <span style={{ fontSize: '12px', fontWeight: 700, color: theme.success, letterSpacing: '1px' }}>LIVE</span>

          </div>{/* /LIVE badge */}

        </div>{/* /right-side flex */}

      </div>{/* /hero row */}



      {/* ── Row 1: 6 KPI Cards ───────────────────────────────────────────── */}

      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>



        {/* 1. Total Incidents */}

        <KpiCard

          label="Total Incidents"

          value={stats.totalIncidents}

          decimals={0}

          color={theme.accent}

          trend={stats.incidentsTrend}

          trendUp={true}

          period={stats.period}

          delay={0}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={theme.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />

              <polyline points="14 2 14 8 20 8" />

              <line x1="16" y1="13" x2="8" y2="13" />

              <line x1="16" y1="17" x2="8" y2="17" />

              <polyline points="10 9 9 9 8 9" />

            </svg>

          }

        />



        {/* 2. SLA Compliance */}

        <KpiCard

          label="SLA Compliance"

          value={stats.slaCompliance}

          decimals={2}

          suffix="%"

          color={theme.success}

          trend={stats.slaTrend}

          trendUp={true}

          period={stats.period}

          delay={0.05}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={theme.success} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />

              <polyline points="9 12 11 14 15 10" />

            </svg>

          }

        />



        {/* 3. FCR */}

        <KpiCard

          label="FCR"

          value={stats.fcr}

          decimals={2}

          suffix="%"

          color="#f59e0b"

          trend={stats.fcrTrend}

          trendUp={true}

          period={stats.period}

          delay={0.1}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

              <circle cx="12" cy="12" r="10" />

              <circle cx="12" cy="12" r="6" />

              <circle cx="12" cy="12" r="2" />

            </svg>

          }

        />



        {/* 4. Avg. MTTR */}

        <KpiCard

          label="Avg. MTTR (Hours)"

          value={stats.avgMTTR}

          decimals={2}

          color={theme.accentSecondary}

          trend={Math.abs(stats.mttrTrend)}

          trendUp={false}

          period={stats.period}

          delay={0.15}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={theme.accentSecondary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

              <circle cx="12" cy="12" r="10" />

              <polyline points="12 6 12 12 16 14" />

            </svg>

          }

        />



        {/* 5. Reopen Rate */}

        <KpiCard

          label="Reopen Rate"

          value={stats.reopenRate}

          decimals={2}

          suffix="%"

          color="#ec4899"

          trend={Math.abs(stats.reopenTrend)}

          trendUp={false}

          period={stats.period}

          delay={0.2}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ec4899" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

              <polyline points="23 4 23 10 17 10" />

              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />

            </svg>

          }

        />



        {/* 6. Customer Rating */}

        <KpiCard

          label="Customer Rating"

          value={stats.customerRating}

          decimals={2}

          suffix=" / 5"

          color="#f59e0b"

          trend={stats.ratingTrend}

          trendUp={true}

          period={stats.period}

          delay={0.25}

          icon={

            <svg width="20" height="20" viewBox="0 0 24 24" fill="#f59e0b" stroke="none">

              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />

            </svg>

          }

        />

      </div>



      {/* ── Row 2: 3 Charts ──────────────────────────────────────────────── */}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>



        {/* Chart 1: Incidents Over Time (LineChart) */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>Incidents Over Time</div>

          <ResponsiveContainer width="100%" height={200}>

            <LineChart data={incidentsOverTime} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>

              <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} />

              <XAxis dataKey="date" tick={axisTickStyle} axisLine={false} tickLine={false} />

              <YAxis tick={axisTickStyle} axisLine={false} tickLine={false} />

              <Tooltip content={<ChartTooltip />} />

              <Line

                type="monotone"

                dataKey="incidents"

                name="Incidents"

                stroke={theme.accent}

                strokeWidth={2.5}

                dot={{ fill: theme.accent, r: 4, strokeWidth: 0 }}

                activeDot={{ r: 6, fill: theme.accent }}

              />

            </LineChart>

          </ResponsiveContainer>

        </div>



        {/* Chart 2: SLA Compliance Trend (LineChart) */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>SLA Compliance Trend (%)</div>

          <ResponsiveContainer width="100%" height={200}>

            <LineChart data={slaTrend} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>

              <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} />

              <XAxis dataKey="date" tick={axisTickStyle} axisLine={false} tickLine={false} />

              <YAxis tick={axisTickStyle} axisLine={false} tickLine={false} />

              <Tooltip content={<ChartTooltip />} />

              <Line

                type="monotone"

                dataKey="sla"

                name="SLA %"

                stroke={theme.success}

                strokeWidth={2.5}

                dot={{ fill: theme.success, r: 4, strokeWidth: 0 }}

                activeDot={{ r: 6, fill: theme.success }}

              />

            </LineChart>

          </ResponsiveContainer>

        </div>



        {/* Chart 3: Incidents by State (PieChart donut) */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>Incidents by State</div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>

            <ResponsiveContainer width="55%" height={180}>

              <PieChart>

                <Pie

                  data={incidentsByState}

                  cx="50%" cy="50%"

                  innerRadius={55} outerRadius={80}

                  paddingAngle={3}

                  dataKey="value"

                  labelLine={false}

                  label={renderCustomPieLabel}

                >

                  {incidentsByState.map((entry, index) => (

                    <Cell key={index} fill={stateColors[index]} stroke="transparent" />

                  ))}

                </Pie>

                <Tooltip content={<ChartTooltip />} />

              </PieChart>

            </ResponsiveContainer>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>

              {incidentsByState.map((entry, i) => (

                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>

                  <div style={{ width: '10px', height: '10px', borderRadius: '3px', background: stateColors[i], flexShrink: 0 }} />

                  <span style={{ fontSize: '12px', color: theme.textSecondary, flex: 1 }}>{entry.name}</span>

                  <span style={{ fontSize: '12px', fontWeight: 700, color: theme.textPrimary }}>{entry.value}</span>

                </div>

              ))}

            </div>

          </div>

        </div>

      </div>



      {/* ── Row 3: Agents table + 2 bar charts ──────────────────────────── */}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '16px' }}>



        {/* Section 1: Top 5 Agents by FCR table */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>Top 5 Agents by FCR (%)</div>

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>

            <thead>

              <tr>

                {['Agent', 'FCR (%)', 'Incidents', 'Trend'].map(col => (

                  <th key={col} style={{

                    textAlign: col === 'Agent' ? 'left' : 'center',

                    fontSize: '11px', fontWeight: 600, color: theme.textMuted,

                    textTransform: 'uppercase', letterSpacing: '0.6px',

                    paddingBottom: '10px',

                    borderBottom: `1px solid ${theme.cardBorder}`,

                  }}>{col}</th>

                ))}

              </tr>

            </thead>

            <tbody>

              {topAgents.map((agent, i) => (

                <tr

                  key={i}

                  style={{

                    background: i % 2 === 1 ? theme.tableRowAlt : 'transparent',

                    transition: 'background 0.2s',

                  }}

                >

                  <td style={{ padding: '10px 0', paddingRight: '8px' }}>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>

                      <AgentAvatar name={agent.name} color={theme.accent} />

                      <span style={{ fontSize: '13px', color: theme.textPrimary, fontWeight: 500 }}>{agent.name}</span>

                    </div>

                  </td>

                  <td style={{ textAlign: 'center', padding: '10px 4px' }}>

                    <span style={{ fontSize: '13px', fontWeight: 700, color: fcrColor(agent.fcr) }}>

                      {agent.fcr.toFixed(2)}%

                    </span>

                  </td>

                  <td style={{ textAlign: 'center', padding: '10px 4px' }}>

                    <span style={{ fontSize: '13px', color: theme.textSecondary }}>{agent.incidents}</span>

                  </td>

                  <td style={{ textAlign: 'center', padding: '10px 0' }}>

                    <span style={{

                      fontSize: '12px', fontWeight: 700,

                      color: agent.trendUp ? theme.success : theme.danger,

                      padding: '2px 8px', borderRadius: '12px',

                      background: agent.trendUp ? `${theme.success}18` : `${theme.danger}18`,

                    }}>

                      {agent.trendUp ? '↑' : '↓'} {Math.abs(agent.trend)}%

                    </span>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>



        {/* Section 2: Avg. MTTR by Priority (BarChart) */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>Avg. MTTR by Priority (Hours)</div>

          <ResponsiveContainer width="100%" height={200}>

            <BarChart data={mttrByPriority} margin={{ top: 16, right: 8, left: -20, bottom: 0 }}>

              <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} vertical={false} />

              <XAxis dataKey="priority" tick={axisTickStyle} axisLine={false} tickLine={false} />

              <YAxis tick={axisTickStyle} axisLine={false} tickLine={false} />

              <Tooltip content={<ChartTooltip />} />

              <Bar dataKey="hours" name="Hours" fill={theme.accentSecondary} radius={[4, 4, 0, 0]} barSize={28}>

                <LabelList dataKey="hours" position="top" style={{ fontSize: 10, fill: theme.textMuted }} formatter={v => v.toFixed(0)} />

              </Bar>

            </BarChart>

          </ResponsiveContainer>

        </div>



        {/* Section 3: SLA Compliance by Priority (BarChart) */}

        <div style={{ ...glassCard, padding: '20px' }}>

          <div style={sectionHeader}>SLA Compliance by Priority (%)</div>

          <ResponsiveContainer width="100%" height={200}>

            <BarChart data={slaByPriority} margin={{ top: 16, right: 8, left: -20, bottom: 0 }}>

              <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} vertical={false} />

              <XAxis dataKey="priority" tick={axisTickStyle} axisLine={false} tickLine={false} />

              <YAxis tick={axisTickStyle} axisLine={false} tickLine={false} />

              <Tooltip content={<ChartTooltip />} />

              <Bar dataKey="compliance" name="Compliance %" fill={theme.accent} radius={[4, 4, 0, 0]} barSize={28}>

                <LabelList dataKey="compliance" position="top" style={{ fontSize: 10, fill: theme.textMuted }} formatter={v => v.toFixed(2) + '%'} />

              </Bar>

            </BarChart>

          </ResponsiveContainer>

        </div>

      </div>



      {/* ── Row 4: 4 sections ────────────────────────────────────────────── */}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px' }}>



        {/* Section 1: Recent Alerts */}

        <div style={{ ...glassCard, padding: '20px', display: 'flex', flexDirection: 'column' }}>

          <div style={sectionHeader}>Recent Alerts</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>

            {alerts.map((alert) => (

              <div key={alert.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>

                <AlertIcon level={alert.level} />

                <div style={{ flex: 1, minWidth: 0 }}>

                  <div style={{ fontSize: '13px', fontWeight: 700, color: theme.textPrimary, lineHeight: 1.3 }}>{alert.title}</div>

                  <div style={{ fontSize: '11px', color: theme.textSecondary, marginTop: '2px', lineHeight: 1.3 }}>{alert.desc}</div>

                </div>

                <div style={{ fontSize: '11px', color: theme.textMuted, flexShrink: 0 }}>{alert.time}</div>

              </div>

            ))}

          </div>

          <a style={linkStyle}>View All Alerts →</a>

        </div>



        {/* Section 2: Gamification Summary */}

        <div style={{ ...glassCard, padding: '20px', display: 'flex', flexDirection: 'column' }}>

          <div style={sectionHeader}>Gamification Summary</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>

            {[

              { label: 'Total Agents', value: gamSummary.totalAgents },

              { label: 'Total Points', value: gamSummary.totalPoints.toLocaleString() },

              { label: 'Badges Awarded', value: gamSummary.badgesAwarded },

              { label: 'Active Challenges', value: gamSummary.activeChallenges },

            ].map(row => (

              <div key={row.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

                <span style={{ fontSize: '13px', color: theme.textSecondary }}>{row.label}</span>

                <span style={{ fontSize: '14px', fontWeight: 700, color: theme.textPrimary }}>{row.value}</span>

              </div>

            ))}

          </div>

          <a style={linkStyle}>View Leaderboard →</a>

        </div>



        {/* Section 3: Top Badges Earned */}

        <div style={{ ...glassCard, padding: '20px', display: 'flex', flexDirection: 'column' }}>

          <div style={sectionHeader}>Top Badges Earned</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>

            {topBadgesData.map(badge => (

              <div key={badge.id} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>

                <div style={{

                  width: '34px', height: '34px', borderRadius: '10px',

                  background: `${badge.color}18`,

                  border: `1px solid ${badge.color}33`,

                  display: 'flex', alignItems: 'center', justifyContent: 'center',

                  flexShrink: 0,

                }}>

                  <BadgeIcon type={badge.icon} color={badge.color} />

                </div>

                <div style={{ flex: 1, minWidth: 0 }}>

                  <div style={{ fontSize: '13px', fontWeight: 700, color: theme.textPrimary }}>{badge.name}</div>

                  <div style={{ fontSize: '11px', color: theme.textSecondary, marginTop: '1px' }}>{badge.desc}</div>

                </div>

              </div>

            ))}

          </div>

          <a style={linkStyle}>View All Badges →</a>

        </div>



        {/* Section 4: Performance Distribution */}

        <div style={{ ...glassCard, padding: '20px', display: 'flex', flexDirection: 'column' }}>

          <div style={sectionHeader}>Performance Distribution</div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>

            <ResponsiveContainer width="55%" height={150}>

              <PieChart>

                <Pie

                  data={perfDistribution}

                  cx="50%" cy="50%"

                  innerRadius={40} outerRadius={60}

                  paddingAngle={3}

                  dataKey="value"

                  labelLine={false}

                >

                  {perfDistribution.map((entry, index) => (

                    <Cell key={index} fill={perfColors[index]} stroke="transparent" />

                  ))}

                </Pie>

                <Tooltip content={<ChartTooltip />} />

              </PieChart>

            </ResponsiveContainer>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>

              {perfDistribution.map((entry, i) => (

                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>

                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', background: perfColors[i], flexShrink: 0 }} />

                  <span style={{ fontSize: '11px', color: theme.textSecondary, flex: 1 }}>{entry.name}</span>

                  <span style={{ fontSize: '11px', fontWeight: 700, color: theme.textPrimary }}>{entry.value}%</span>

                </div>

              ))}

            </div>

          </div>

          <a style={linkStyle}>View Performance Report →</a>

        </div>

      </div>



    </div>

  )

}

