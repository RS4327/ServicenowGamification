import React, { useState, useEffect, useRef } from 'react'

import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

import * as sampleData from '../../data/sampleData.js'

import {
  getAgentStats,
  getAgentPerformanceTrend,
  getAgentIncidentsByState,
  getRecentIncidents,
  getAgentBadges,
} from '../../services/api.js'

import { useTheme } from '../../context/ThemeContext.jsx'


// ============================================================
// ANIMATED COUNTER
// ============================================================

function useAnimatedCounter(target, duration = 1500) {
  const [count, setCount] = useState(0)
  const rafRef = useRef(null)

  useEffect(() => {
    let startTime = null

    const endValue = parseFloat(target)

    // Prevent NaN from breaking animation
    if (Number.isNaN(endValue)) {
      setCount(0)
      return
    }

    function step(timestamp) {
      if (!startTime) startTime = timestamp

      const elapsed = timestamp - startTime
      const progress = Math.min(elapsed / duration, 1)

      const eased = 1 - Math.pow(1 - progress, 3)

      const current = endValue * eased

      setCount(current)

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step)
      }
    }

    rafRef.current = requestAnimationFrame(step)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [target, duration])

  return count
}


// ============================================================
// COLORS
// ============================================================

const PIE_COLORS_AGENT = [
  '#00d4ff',
  '#f59e0b',
  '#ef4444'
]

const BADGE_GRADIENTS = [
  'linear-gradient(135deg, #00d4ff, #0891b2)',
  'linear-gradient(135deg, #10b981, #065f46)',
  'linear-gradient(135deg, #f59e0b, #92400e)',
]


// ============================================================
// CHART TOOLTIP
// ============================================================

function ChartTooltip({ active, payload, label }) {
  const { theme } = useTheme()

  if (!active || !payload || !payload.length) {
    return null
  }

  return (
    <div
      style={{
        background: theme.sidebarBg,
        border: `1px solid ${theme.cardBorder}`,
        borderRadius: '12px',
        color: theme.textPrimary,
        fontSize: '13px',
        padding: '10px 14px',
      }}
    >
      <div
        style={{
          fontWeight: 700,
          marginBottom: '6px',
          color: theme.textSecondary
        }}
      >
        {label}
      </div>

      {payload.map((p, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '2px'
          }}
        >
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: p.color
            }}
          />

          <span
            style={{
              color: theme.textPrimary,
              fontWeight: 600
            }}
          >
            {p.name}:{' '}
            {typeof p.value === 'number'
              ? p.value.toFixed(2)
              : p.value}
          </span>
        </div>
      ))}
    </div>
  )
}


// ============================================================
// KPI CARD
// ============================================================

function KpiCard({
  label,
  value,
  decimals = 0,
  suffix = '',
  color,
  icon,
  delay
}) {
  const { theme } = useTheme()

  const count = useAnimatedCounter(parseFloat(value))

  const [hovered, setHovered] = useState(false)

  const safeCount = Number.isNaN(count) ? 0 : count

  const formatted =
    decimals > 0
      ? safeCount.toFixed(decimals)
      : Math.floor(safeCount).toString()

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
        padding: '22px',
        flex: 1,
        minWidth: 0,
        position: 'relative',
        overflow: 'hidden',
        cursor: 'default',
        transition: 'all 0.3s',
        transform: hovered
          ? 'translateY(-4px)'
          : 'translateY(0)',
        boxShadow: hovered
          ? `0 12px 40px ${color}26`
          : theme.cardShadow,
        animation: `fadeInUp 0.5s ease ${delay}s both`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: '18px',
          right: '18px',
          width: '48px',
          height: '48px',
          borderRadius: '12px',
          background: `${color}18`,
          border: `1px solid ${color}30`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {icon}
      </div>

      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          color: theme.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.8px',
          marginBottom: '8px'
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: '30px',
          fontWeight: 800,
          color: theme.textPrimary,
          lineHeight: 1,
          marginBottom: '4px'
        }}
      >
        {formatted}
        {suffix}
      </div>

      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, ${color}, transparent)`,
          opacity: hovered ? 1 : 0.5,
          transition: 'opacity 0.3s'
        }}
      />
    </div>
  )
}


// ============================================================
// AGENT DASHBOARD
// ============================================================

export default function AgentDashboard() {
  const { theme } = useTheme()

  const today = new Date().toLocaleDateString(
    'en-US',
    {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }
  )


  // ==========================================================
  // INITIAL DATA = SAMPLE DATA
  //
  // Oracle data will replace this when API succeeds.
  // ==========================================================

  const [stats, setStats] = useState(
    sampleData.agentStats
  )

  const [agentPerformanceTrend, setAgentPerformanceTrend] =
    useState(
      sampleData.agentPerformanceTrend
    )

  const [agentIncidentsByState, setAgentIncidentsByState] =
    useState(
      sampleData.agentIncidentsByState
    )

  const [recentIncidents, setRecentIncidents] =
    useState(
      sampleData.recentIncidents
    )

  const [agentBadges, setAgentBadges] =
    useState(
      sampleData.badgesEarned
    )


  // ==========================================================
  // ORACLE → STATS
  // ==========================================================

  useEffect(() => {
    getAgentStats()
      .then((data) => {

        console.log(
          '[AgentDashboard] Oracle Agent Stats:',
          data
        )

        if (
          data &&
          typeof data === 'object' &&
          !Array.isArray(data)
        ) {
          setStats(data)

          console.log(
            '[AgentDashboard] Using ORACLE stats'
          )
        } else {
          console.warn(
            '[AgentDashboard] Oracle stats empty/invalid. Using SAMPLE data.'
          )

          setStats(sampleData.agentStats)
        }
      })
      .catch((err) => {

        console.warn(
          '[AgentDashboard] Agent stats API failed. Using SAMPLE data.',
          err
        )

        setStats(sampleData.agentStats)
      })
  }, [])


  // ==========================================================
  // ORACLE → PERFORMANCE TREND
  // ==========================================================

  useEffect(() => {
    getAgentPerformanceTrend()
      .then((data) => {

        console.log(
          '[AgentDashboard] Oracle Performance Trend:',
          data
        )

        if (
          Array.isArray(data) &&
          data.length > 0
        ) {
          setAgentPerformanceTrend(data)

          console.log(
            '[AgentDashboard] Using ORACLE performance trend'
          )
        } else {
          console.warn(
            '[AgentDashboard] Oracle performance trend empty. Using SAMPLE data.'
          )

          setAgentPerformanceTrend(
            sampleData.agentPerformanceTrend
          )
        }
      })
      .catch((err) => {

        console.warn(
          '[AgentDashboard] Performance trend API failed. Using SAMPLE data.',
          err
        )

        setAgentPerformanceTrend(
          sampleData.agentPerformanceTrend
        )
      })
  }, [])


  // ==========================================================
  // ORACLE → INCIDENTS BY STATE
  // ==========================================================

  useEffect(() => {
    getAgentIncidentsByState()
      .then((data) => {

        console.log(
          '[AgentDashboard] Oracle Incidents By State:',
          data
        )

        if (
          Array.isArray(data) &&
          data.length > 0
        ) {
          setAgentIncidentsByState(data)

          console.log(
            '[AgentDashboard] Using ORACLE incident state data'
          )
        } else {
          console.warn(
            '[AgentDashboard] Oracle incident state data empty. Using SAMPLE data.'
          )

          setAgentIncidentsByState(
            sampleData.agentIncidentsByState
          )
        }
      })
      .catch((err) => {

        console.warn(
          '[AgentDashboard] Incident state API failed. Using SAMPLE data.',
          err
        )

        setAgentIncidentsByState(
          sampleData.agentIncidentsByState
        )
      })
  }, [])


  // ==========================================================
  // ORACLE → RECENT INCIDENTS
  // ==========================================================

  useEffect(() => {
    getRecentIncidents()
      .then((data) => {

        console.log(
          '[AgentDashboard] Oracle Recent Incidents:',
          data
        )

        if (
          Array.isArray(data) &&
          data.length > 0
        ) {
          setRecentIncidents(data)

          console.log(
            '[AgentDashboard] Using ORACLE recent incidents'
          )
        } else {
          console.warn(
            '[AgentDashboard] Oracle recent incidents empty. Using SAMPLE data.'
          )

          setRecentIncidents(
            sampleData.recentIncidents
          )
        }
      })
      .catch((err) => {

        console.warn(
          '[AgentDashboard] Recent incidents API failed. Using SAMPLE data.',
          err
        )

        setRecentIncidents(
          sampleData.recentIncidents
        )
      })
  }, [])


  // ==========================================================
  // ORACLE → BADGES
  // ==========================================================

  useEffect(() => {
    getAgentBadges()
      .then((data) => {

        console.log(
          '[AgentDashboard] Oracle Agent Badges:',
          data
        )

        if (
          Array.isArray(data) &&
          data.length > 0
        ) {
          setAgentBadges(data)

          console.log(
            '[AgentDashboard] Using ORACLE badges'
          )
        } else {
          console.warn(
            '[AgentDashboard] Oracle badges empty. Using SAMPLE data.'
          )

          setAgentBadges(
            sampleData.badgesEarned
          )
        }
      })
      .catch((err) => {

        console.warn(
          '[AgentDashboard] Agent badges API failed. Using SAMPLE data.',
          err
        )

        setAgentBadges(
          sampleData.badgesEarned
        )
      })
  }, [])


  // ==========================================================
  // TOTAL INCIDENTS
  // ==========================================================

  const total = agentIncidentsByState.reduce(
    (a, b) => a + (Number(b.value) || 0),
    0
  )


  // ==========================================================
  // COMMON CARD STYLE
  // ==========================================================

  const glassCard = {
    background: theme.cardBg,
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: `1px solid ${theme.cardBorder}`,
    borderRadius: '16px',
  }


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}
    >

      {/* =====================================================
          HERO
      ====================================================== */}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px'
        }}
      >

        <div>

          <h1
            style={{
              fontSize: '28px',
              fontWeight: 800,
              color: theme.textPrimary,
              marginBottom: '4px'
            }}
          >
            My{' '}
            <span
              style={{
                color: theme.accent
              }}
            >
              Dashboard
            </span>
          </h1>

          <div
            style={{
              fontSize: '13px',
              color: theme.textMuted
            }}
          >
            {today}
          </div>

        </div>


        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: `${theme.success}14`,
            border: `1px solid ${theme.success}33`,
            borderRadius: '30px'
          }}
        >

          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: theme.success,
              animation: 'live-pulse 2s ease infinite',
              boxShadow: `0 0 8px ${theme.success}`
            }}
          />

          <span
            style={{
              fontSize: '12px',
              fontWeight: 700,
              color: theme.success,
              letterSpacing: '1px'
            }}
          >
            LIVE
          </span>

        </div>

      </div>


      {/* =====================================================
          KPI CARDS
      ====================================================== */}

      <div
        style={{
          display: 'flex',
          gap: '20px',
          flexWrap: 'wrap'
        }}
      >

        <KpiCard
          label="My Incidents"
          value={stats?.myIncidents ?? 0}
          decimals={0}
          color={theme.accent}
          delay={0}
          icon={
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={theme.accent}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          }
        />


        <KpiCard
          label="SLA Compliance"
          value={stats?.slaCompliance ?? 0}
          decimals={1}
          suffix="%"
          color={theme.success}
          delay={0.1}
          icon={
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={theme.success}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          }
        />


        <KpiCard
          label="FCR Rate"
          value={stats?.fcr ?? 0}
          decimals={2}
          suffix="%"
          color={theme.warning}
          delay={0.2}
          icon={
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={theme.warning}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <circle cx="12" cy="12" r="6" />
              <circle cx="12" cy="12" r="2" />
            </svg>
          }
        />


        <KpiCard
          label="MTTR (hrs)"
          value={stats?.mttr ?? 0}
          decimals={2}
          color={theme.accentSecondary}
          delay={0.3}
          icon={
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={theme.accentSecondary}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          }
        />

      </div>


      {/* =====================================================
          CHARTS ROW
      ====================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '20px'
        }}
      >

        {/* ===================================================
            PERFORMANCE TREND
        ==================================================== */}

        <div
          style={{
            ...glassCard,
            padding: '24px'
          }}
        >

          <div
            style={{
              marginBottom: '20px'
            }}
          >

            <div
              style={{
                fontSize: '15px',
                fontWeight: 700,
                color: theme.textPrimary
              }}
            >
              Performance Trend
            </div>

            <div
              style={{
                fontSize: '12px',
                color: theme.textMuted,
                marginTop: '2px'
              }}
            >
              FCR rate over the past 8 weeks
            </div>

          </div>


          <ResponsiveContainer
            width="100%"
            height={220}
          >

            <AreaChart
              data={agentPerformanceTrend}
              margin={{
                top: 5,
                right: 5,
                left: -20,
                bottom: 0
              }}
            >

              <defs>

                <linearGradient
                  id="agentFcrGrad"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="5%"
                    stopColor={theme.accentSecondary}
                    stopOpacity={0.35}
                  />

                  <stop
                    offset="95%"
                    stopColor={theme.accentSecondary}
                    stopOpacity={0}
                  />
                </linearGradient>

              </defs>


              <CartesianGrid
                strokeDasharray="3 3"
                stroke={theme.chartGrid}
              />


              <XAxis
                dataKey="date"
                tick={{
                  fill: theme.textMuted,
                  fontSize: 11
                }}
                axisLine={false}
                tickLine={false}
              />


              <YAxis
                tick={{
                  fill: theme.textMuted,
                  fontSize: 11
                }}
                axisLine={false}
                tickLine={false}
              />


              <Tooltip
                content={<ChartTooltip />}
              />


              <Area
                type="monotone"
                dataKey="fcr"
                name="FCR %"
                stroke={theme.accentSecondary}
                strokeWidth={2.5}
                fill="url(#agentFcrGrad)"
                dot={{
                  fill: theme.accentSecondary,
                  r: 3,
                  strokeWidth: 0
                }}
                activeDot={{
                  r: 5
                }}
              />

            </AreaChart>

          </ResponsiveContainer>

        </div>


        {/* ===================================================
            INCIDENTS BY STATE
        ==================================================== */}

        <div
          style={{
            ...glassCard,
            padding: '24px'
          }}
        >

          <div
            style={{
              marginBottom: '20px'
            }}
          >

            <div
              style={{
                fontSize: '15px',
                fontWeight: 700,
                color: theme.textPrimary
              }}
            >
              Incidents by State
            </div>

            <div
              style={{
                fontSize: '12px',
                color: theme.textMuted,
                marginTop: '2px'
              }}
            >
              My incident distribution
            </div>

          </div>


          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px'
            }}
          >

            <div
              style={{
                position: 'relative',
                flex: '0 0 160px'
              }}
            >

              <ResponsiveContainer
                width="100%"
                height={180}
              >

                <PieChart>

                  <Pie
                    data={agentIncidentsByState}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >

                    {agentIncidentsByState.map(
                      (entry, index) => (
                        <Cell
                          key={index}
                          fill={
                            PIE_COLORS_AGENT[
                              index %
                              PIE_COLORS_AGENT.length
                            ]
                          }
                          stroke="transparent"
                        />
                      )
                    )}

                  </Pie>


                  <Tooltip
                    content={<ChartTooltip />}
                  />

                </PieChart>

              </ResponsiveContainer>


              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%,-50%)',
                  textAlign: 'center',
                  pointerEvents: 'none'
                }}
              >

                <div
                  style={{
                    fontSize: '22px',
                    fontWeight: 800,
                    color: theme.textPrimary
                  }}
                >
                  {total}
                </div>

                <div
                  style={{
                    fontSize: '10px',
                    color: theme.textMuted
                  }}
                >
                  Total
                </div>

              </div>

            </div>


            <div
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}
            >

              {agentIncidentsByState.map(
                (entry, i) => {

                  const color =
                    PIE_COLORS_AGENT[
                      i % PIE_COLORS_AGENT.length
                    ]

                  return (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >

                      <div
                        style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '3px',
                          background: color,
                          boxShadow: `0 0 6px ${color}`
                        }}
                      />

                      <span
                        style={{
                          fontSize: '12px',
                          color: theme.textSecondary,
                          flex: 1
                        }}
                      >
                        {entry.name}
                      </span>

                      <span
                        style={{
                          fontSize: '13px',
                          fontWeight: 700,
                          color: theme.textPrimary
                        }}
                      >
                        {entry.value}
                      </span>

                    </div>
                  )
                }
              )}

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          RECENT INCIDENTS
      ====================================================== */}

      <div
        style={{
          ...glassCard,
          padding: '24px'
        }}
      >

        <div
          style={{
            marginBottom: '20px'
          }}
        >

          <div
            style={{
              fontSize: '15px',
              fontWeight: 700,
              color: theme.textPrimary
            }}
          >
            Recent Incidents
          </div>

          <div
            style={{
              fontSize: '12px',
              color: theme.textMuted,
              marginTop: '2px'
            }}
          >
            Latest assigned incidents
          </div>

        </div>


        <div
          style={{
            overflowX: 'auto'
          }}
        >

          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}
          >

            <thead>

              <tr
                style={{
                  background: theme.tableRowAlt,
                  borderBottom:
                    `1px solid ${theme.cardBorder}`
                }}
              >

                {[
                  'Incident #',
                  'Description',
                  'State',
                  'Date'
                ].map(h => (

                  <th
                    key={h}
                    style={{
                      padding: '10px 16px',
                      textAlign: 'left',
                      fontSize: '11px',
                      fontWeight: 700,
                      color: theme.textMuted,
                      textTransform: 'uppercase',
                      letterSpacing: '0.8px',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {h}
                  </th>

                ))}

              </tr>

            </thead>


            <tbody>

              {recentIncidents.map(
                (inc, i) => (
                  <IncidentRow
                    key={inc.id || i}
                    inc={inc}
                    i={i}
                    theme={theme}
                  />
                )
              )}

            </tbody>

          </table>

        </div>

      </div>


      {/* =====================================================
          BADGES
      ====================================================== */}

      <div>

        <div
          style={{
            fontSize: '15px',
            fontWeight: 700,
            color: theme.textPrimary,
            marginBottom: '16px'
          }}
        >
          Earned Badges
        </div>


        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(3, 1fr)',
            gap: '16px'
          }}
        >

          {agentBadges.map(
            (badge, i) => (

              <BadgeCard
                key={badge.id || i}
                badge={badge}
                gradient={
                  BADGE_GRADIENTS[
                    i % BADGE_GRADIENTS.length
                  ]
                }
                theme={theme}
              />

            )
          )}

        </div>

      </div>

    </div>
  )
}


// ============================================================
// INCIDENT ROW
// ============================================================

function IncidentRow({
  inc,
  i,
  theme
}) {
  const [hovered, setHovered] =
    useState(false)

  const stateColor = {
    Resolved: theme.success,
    Open: theme.danger,
    Closed: theme.warning
  }

  const stateBg = {
    Resolved: `${theme.success}1a`,
    Open: `${theme.danger}1a`,
    Closed: `${theme.warning}1a`
  }

  const stateBorder = {
    Resolved: `${theme.success}33`,
    Open: `${theme.danger}33`,
    Closed: `${theme.warning}33`
  }

  const currentState =
    inc.state || 'Open'

  const color =
    stateColor[currentState] ||
    theme.textMuted

  const background =
    stateBg[currentState] ||
    `${theme.textMuted}1a`

  const border =
    stateBorder[currentState] ||
    `${theme.textMuted}33`

  return (
    <tr
      onMouseEnter={() =>
        setHovered(true)
      }
      onMouseLeave={() =>
        setHovered(false)
      }
      style={{
        borderBottom:
          `1px solid ${theme.cardBorder}`,
        background: hovered
          ? theme.tableRowHover
          : i % 2 === 0
            ? 'transparent'
            : theme.tableRowAlt,
        transition: 'all 0.2s'
      }}
    >

      <td
        style={{
          padding: '12px 16px',
          fontSize: '13px',
          fontWeight: 600,
          color: theme.accent,
          fontFamily: 'monospace'
        }}
      >
        {inc.id}
      </td>


      <td
        style={{
          padding: '12px 16px',
          fontSize: '13px',
          color: theme.textSecondary,
          maxWidth: '240px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}
      >
        {inc.shortDesc}
      </td>


      <td
        style={{
          padding: '12px 16px'
        }}
      >

        <span
          style={{
            padding: '3px 10px',
            borderRadius: '20px',
            fontSize: '11px',
            fontWeight: 700,
            color,
            background,
            border: `1px solid ${border}`
          }}
        >
          {currentState}
        </span>

      </td>


      <td
        style={{
          padding: '12px 16px',
          fontSize: '12px',
          color: theme.textMuted,
          whiteSpace: 'nowrap'
        }}
      >
        {inc.openedAt}
      </td>

    </tr>
  )
}


// ============================================================
// BADGE CARD
// ============================================================

function BadgeCard({
  badge,
  gradient,
  theme
}) {
  const [hovered, setHovered] =
    useState(false)

  return (
    <div
      onMouseEnter={() =>
        setHovered(true)
      }
      onMouseLeave={() =>
        setHovered(false)
      }
      style={{
        background: theme.cardBg,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter:
          'blur(20px)',
        border:
          `1px solid ${theme.cardBorder}`,
        borderRadius: '16px',
        padding: '20px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s',
        transform: hovered
          ? 'translateY(-3px)'
          : 'translateY(0)',
        boxShadow: hovered
          ? theme.cardShadow
          : '0 4px 16px rgba(0,0,0,0.2)',
        cursor: 'default'
      }}
    >

      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: gradient,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 12px',
          boxShadow:
            '0 0 20px rgba(0,0,0,0.4)'
        }}
      >

        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#fff"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle
            cx="12"
            cy="8"
            r="6"
          />

          <path
            d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"
          />
        </svg>

      </div>


      <div
        style={{
          fontSize: '13px',
          fontWeight: 700,
          color: theme.textPrimary,
          marginBottom: '4px'
        }}
      >
        {badge.name}
      </div>


      <div
        style={{
          fontSize: '11px',
          color: theme.textMuted,
          lineHeight: 1.4,
          marginBottom: '12px'
        }}
      >
        {badge.description}
      </div>


      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: '3px 10px',
          background:
            `${theme.success}1a`,
          border:
            `1px solid ${theme.success}33`,
          borderRadius: '20px',
          fontSize: '10px',
          fontWeight: 700,
          color: theme.success
        }}
      >
        ✓ Earned
      </div>

    </div>
  )
}
