
import React, { useEffect, useMemo, useState } from 'react'

import { getLeaderboard } from '../../services/api.js'
import { useAuth } from '../../context/AuthContext.jsx'
import { useTheme } from '../../context/ThemeContext.jsx'


// ------------------------------------------------------------
// PODIUM CONFIG
// ------------------------------------------------------------

const PODIUM_CONFIG = [
  {
    rank: 2,
    height: 110,
    gradient: 'linear-gradient(135deg, #94a3b8, #64748b)',
    glow: 'rgba(148,163,184,0.3)',
    label: '2nd',
    medal: '🥈',
  },
  {
    rank: 1,
    height: 150,
    gradient: 'linear-gradient(135deg, #f59e0b, #d97706)',
    glow: 'rgba(245,158,11,0.4)',
    label: '1st',
    medal: '🥇',
  },
  {
    rank: 3,
    height: 80,
    gradient: 'linear-gradient(135deg, #a16207, #78350f)',
    glow: 'rgba(161,98,7,0.3)',
    label: '3rd',
    medal: '🥉',
  },
]


// ------------------------------------------------------------
// MEDAL ICON
// ------------------------------------------------------------

function MedalIcon({ rank, theme }) {
  if (rank === 1) {
    return (
      <div
        style={{
          fontSize: '18px',
          lineHeight: 1,
        }}
      >
        🥇
      </div>
    )
  }

  if (rank === 2) {
    return (
      <div
        style={{
          fontSize: '18px',
          lineHeight: 1,
        }}
      >
        🥈
      </div>
    )
  }

  if (rank === 3) {
    return (
      <div
        style={{
          fontSize: '18px',
          lineHeight: 1,
        }}
      >
        🥉
      </div>
    )
  }

  return (
    <span
      style={{
        fontSize: '13px',
        fontWeight: 700,
        color: theme.textMuted,
      }}
    >
      #{rank}
    </span>
  )
}


// ------------------------------------------------------------
// INITIALS
// ------------------------------------------------------------

function getInitials(name) {
  return String(name || '?')
    .trim()
    .split(/\s+/)
    .map(part => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}


// ------------------------------------------------------------
// GENDER IMAGE
// ------------------------------------------------------------

function getGenderImage(agent) {
  if (agent.image) {
    return agent.image
  }

  if (agent.image_url) {
    return agent.image_url
  }

  if (agent.profile_image) {
    return agent.profile_image
  }

  const gender = String(
    agent.gender ||
    agent.GENDER ||
    ''
  )
    .trim()
    .toLowerCase()

  if (gender === 'female' || gender === 'f') {
    return '/images/female-agent.png'
  }

  if (gender === 'male' || gender === 'm') {
    return '/images/male-agent.png'
  }

  return null
}


// ------------------------------------------------------------
// AGENT AVATAR
// ------------------------------------------------------------

function AgentAvatar({
  agent,
  size = 56,
  theme,
  podium = false,
}) {
  const [imageError, setImageError] = useState(false)

  const image = getGenderImage(agent)

  if (image && !imageError) {
    return (
      <img
        src={image}
        alt={agent.name || 'Agent'}
        onError={() => setImageError(true)}
        style={{
          width: `${size}px`,
          height: `${size}px`,
          borderRadius: '50%',
          objectFit: 'cover',
          display: 'block',
          border: podium
            ? '2px solid rgba(255,255,255,0.5)'
            : `1px solid ${theme.cardBorder}`,
          boxShadow: podium
            ? '0 0 24px rgba(0,0,0,0.20)'
            : 'none',
        }}
      />
    )
  }

  return (
    <div
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        background: theme.accentGrad,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: podium
          ? size >= 65
            ? '20px'
            : '16px'
          : '11px',
        fontWeight: 800,
        color: '#fff',
        border: `1px solid ${theme.cardBorder}`,
        flexShrink: 0,
      }}
    >
      {getInitials(agent.name)}
    </div>
  )
}


// ------------------------------------------------------------
// METRIC LABEL
// ------------------------------------------------------------

function getMetricLabel(metric) {
  switch (metric) {
    case 'fcr':
      return 'FCR'

    case 'slaCompliance':
      return 'SLA Compliance'

    case 'mttr':
      return 'MTTR'

    case 'points':
    default:
      return 'Points'
  }
}


// ------------------------------------------------------------
// METRIC VALUE
// ------------------------------------------------------------

function getMetricNumber(agent, metric) {
  const points = Number(
    agent.points ??
    agent.POINTS ??
    0
  )

  const fcr = Number(
    agent.fcr ??
    agent.FCR ??
    agent.fcr_percentage ??
    agent.FCR_PERCENTAGE ??
    0
  )

  const sla = Number(
    agent.sla ??
    agent.slaCompliance ??
    agent.sla_percentage ??
    agent.SLA_PERCENTAGE ??
    0
  )

  const mttr = Number(
    agent.mttr ??
    agent.mttr_hours ??
    agent.MTTR ??
    agent.MTTR_HOURS ??
    0
  )

  switch (metric) {
    case 'fcr':
      return fcr

    case 'slaCompliance':
      return sla

    case 'mttr':
      return mttr

    case 'points':
    default:
      return points
  }
}


// ------------------------------------------------------------
// METRIC DISPLAY VALUE
// ------------------------------------------------------------

function getMetricValue(agent, metric) {
  const value = getMetricNumber(
    agent,
    metric
  )

  switch (metric) {
    case 'fcr':
      return `${value.toFixed(2)}%`

    case 'slaCompliance':
      return `${value.toFixed(2)}%`

    case 'mttr':
      return `${value.toFixed(2)} hrs`

    case 'points':
    default:
      return `${value} pts`
  }
}


// ------------------------------------------------------------
// DATE VALUE
// ------------------------------------------------------------

function getAgentDate(agent) {
  const dateValue =
    agent.date ??
    agent.DATE ??
    agent.opened_at ??
    agent.OPENED_AT ??
    agent.resolved_at ??
    agent.RESOLVED_AT ??
    agent.closed_at ??
    agent.CLOSED_AT ??
    agent.week_start ??
    agent.WEEK_START ??
    agent.created_at ??
    agent.CREATED_AT

  if (!dateValue) {
    return null
  }

  const date = new Date(dateValue)

  if (Number.isNaN(date.getTime())) {
    return null
  }

  return date
}


// ------------------------------------------------------------
// PERIOD FILTER
// ------------------------------------------------------------

function filterByPeriod(data, period) {
  const now = new Date()

  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  const currentDay = now.getDay()

  let startDate

  if (period === 'week') {
    const daysFromMonday =
      currentDay === 0
        ? 6
        : currentDay - 1

    startDate = new Date(now)
    startDate.setHours(0, 0, 0, 0)
    startDate.setDate(
      now.getDate() - daysFromMonday
    )
  } else if (period === 'month') {
    startDate = new Date(
      currentYear,
      currentMonth,
      1
    )

    startDate.setHours(0, 0, 0, 0)
  } else if (period === 'quarter') {
    const quarterStartMonth =
      Math.floor(currentMonth / 3) * 3

    startDate = new Date(
      currentYear,
      quarterStartMonth,
      1
    )

    startDate.setHours(0, 0, 0, 0)
  } else {
    return data
  }

  return data.filter(agent => {
    const agentDate = getAgentDate(agent)

    /*
     * If the API has already returned period-specific
     * aggregated leaderboard data and no date exists,
     * keep the record.
     */
    if (!agentDate) {
      return true
    }

    return agentDate >= startDate &&
      agentDate <= now
  })
}


// ------------------------------------------------------------
// CUSTOM DROPDOWN
// ------------------------------------------------------------

function ThemeDropdown({
  value,
  options,
  onChange,
  theme,
  width = '160px',
}) {
  const [open, setOpen] = useState(false)

  const selectedOption =
    options.find(
      option => option.value === value
    ) || options[0]

  useEffect(() => {
    const handleClick = () => {
      setOpen(false)
    }

    if (open) {
      document.addEventListener(
        'click',
        handleClick
      )
    }

    return () => {
      document.removeEventListener(
        'click',
        handleClick
      )
    }
  }, [open])

  return (
    <div
      style={{
        position: 'relative',
        width,
      }}
      onClick={event =>
        event.stopPropagation()
      }
    >
      <button
        type="button"
        onClick={() =>
          setOpen(current => !current)
        }
        style={{
          width: '100%',
          minWidth: width,
          height: '36px',
          padding: '0 11px',
          borderRadius: '8px',
          border: `1px solid ${theme.inputBorder}`,
          background: theme.inputBg,
          color: theme.textPrimary,
          fontSize: '13px',
          cursor: 'pointer',
          outline: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '8px',
          boxSizing: 'border-box',
        }}
      >
        <span>
          {selectedOption?.label}
        </span>

        <span
          style={{
            fontSize: '10px',
            color: theme.textMuted,
            transform: open
              ? 'rotate(180deg)'
              : 'rotate(0deg)',
            transition:
              'transform 0.15s ease',
          }}
        >
          ▼
        </span>
      </button>

      {open && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 5px)',
            left: 0,
            width: '100%',
            minWidth: width,
            background: theme.cardBg,
            border: `1px solid ${theme.cardBorder}`,
            borderRadius: '9px',
            boxShadow:
              '0 12px 30px rgba(0,0,0,0.25)',
            padding: '5px',
            zIndex: 10000,
            boxSizing: 'border-box',
          }}
        >
          {options.map(option => {
            const selected =
              option.value === value

            return (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  onChange(option.value)
                  setOpen(false)
                }}
                style={{
                  width: '100%',
                  border: 'none',
                  borderRadius: '6px',
                  background: selected
                    ? `${theme.accent}18`
                    : 'transparent',
                  color: selected
                    ? theme.accent
                    : theme.textPrimary,
                  padding:
                    '9px 10px',
                  textAlign: 'left',
                  fontSize: '13px',
                  fontWeight: selected
                    ? 700
                    : 500,
                  cursor: 'pointer',
                }}
              >
                {option.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}


// ------------------------------------------------------------
// LEADERBOARD PAGE
// ------------------------------------------------------------

export default function LeaderboardPage() {
  const [metric, setMetric] =
    useState('points')

  const [period, setPeriod] =
    useState('month')

  const [
    leaderboardData,
    setLeaderboardData,
  ] = useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState(null)

  const { user } = useAuth()
  const { theme } = useTheme()


  // ----------------------------------------------------------
  // LOAD DATA
  // ----------------------------------------------------------

  useEffect(() => {
    let mounted = true

    async function loadLeaderboard() {
      setLoading(true)
      setError(null)

      try {
        const data =
          await getLeaderboard(
            metric,
            period
          )

        if (!mounted) {
          return
        }

        setLeaderboardData(
          Array.isArray(data)
            ? data
            : []
        )
      } catch (err) {
        console.error(
          '[LeaderboardPage] Failed to load leaderboard:',
          err
        )

        if (mounted) {
          setLeaderboardData([])

          setError(
            err?.message ||
            'Failed to load leaderboard data'
          )
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadLeaderboard()

    return () => {
      mounted = false
    }
  }, [metric, period])


  // ----------------------------------------------------------
  // PERIOD FILTER + SORT
  // ----------------------------------------------------------

  const sortedLeaderboard = useMemo(() => {
    /*
     * First apply the selected period.
     */
    const periodData =
      filterByPeriod(
        leaderboardData,
        period
      )

    const data = [...periodData]

    /*
     * Sort using selected metric.
     */
    data.sort((a, b) => {
      const valueA =
        getMetricNumber(a, metric)

      const valueB =
        getMetricNumber(b, metric)

      /*
       * MTTR:
       * Lower MTTR is better.
       */
      if (metric === 'mttr') {
        if (valueA !== valueB) {
          return valueA - valueB
        }
      } else {
        if (valueA !== valueB) {
          return valueB - valueA
        }
      }

      /*
       * Tie breaker:
       * Points DESC
       */
      const pointsA =
        Number(
          a.points ??
          a.POINTS ??
          0
        )

      const pointsB =
        Number(
          b.points ??
          b.POINTS ??
          0
        )

      if (pointsA !== pointsB) {
        return pointsB - pointsA
      }

      return String(
        a.name || ''
      ).localeCompare(
        String(b.name || '')
      )
    })

    /*
     * Recreate rank after filtering/sorting.
     */
    return data.map(
      (agent, index) => ({
        ...agent,
        rank: index + 1,
      })
    )
  }, [
    leaderboardData,
    metric,
    period,
  ])


  // ----------------------------------------------------------
  // TOP 3
  // ----------------------------------------------------------

  const top3 =
    sortedLeaderboard.slice(0, 3)

  const podiumOrder = [
    top3[1],
    top3[0],
    top3[2],
  ]


  // ----------------------------------------------------------
  // MAX POINTS
  // ----------------------------------------------------------

  const maxPoints =
    sortedLeaderboard.length > 0
      ? Math.max(
          ...sortedLeaderboard.map(
            agent =>
              Number(
                agent.points ??
                agent.POINTS ??
                0
              )
          ),
          1
        )
      : 1


  // ----------------------------------------------------------
  // GLASS CARD
  // ----------------------------------------------------------

  const glassCard = {
    background: theme.cardBg,
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter:
      'blur(20px)',
    border:
      `1px solid ${theme.cardBorder}`,
    borderRadius: '16px',
  }


  // ----------------------------------------------------------
  // METRIC OPTIONS
  // ----------------------------------------------------------

  const metricOptions = [
    {
      value: 'points',
      label: 'Points',
    },
    {
      value: 'fcr',
      label: 'FCR %',
    },
    {
      value: 'slaCompliance',
      label: 'SLA %',
    },
    {
      value: 'mttr',
      label: 'MTTR',
    },
  ]


  // ----------------------------------------------------------
  // PERIOD OPTIONS
  // ----------------------------------------------------------

  const periodOptions = [
    {
      value: 'week',
      label: 'This Week',
    },
    {
      value: 'month',
      label: 'This Month',
    },
    {
      value: 'quarter',
      label: 'Quarter',
    },
  ]


  // ----------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
      }}
    >

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div>
        <h1
          style={{
            fontSize: '28px',
            fontWeight: 800,
            color: theme.textPrimary,
            marginBottom: '4px',
          }}
        >
          Leader
          <span
            style={{
              color: theme.accent,
            }}
          >
            board
          </span>
        </h1>

        <div
          style={{
            fontSize: '13px',
            color: theme.textMuted,
          }}
        >
          Top performers ranked by{' '}
          {getMetricLabel(metric)}
        </div>
      </div>


      {/* ================================================== */}
      {/* PODIUM */}
      {/* ================================================== */}

      <div
        style={{
          ...glassCard,
          padding:
            '36px 24px 0',
          overflow: 'hidden',
        }}
      >

        <div
          style={{
            textAlign: 'center',
            marginBottom: '32px',
          }}
        >
          <div
            style={{
              fontSize: '13px',
              fontWeight: 600,
              color: theme.textMuted,
              letterSpacing: '2px',
              textTransform:
                'uppercase',
            }}
          >
            Top Performers —{' '}
            {getMetricLabel(metric)}
          </div>
        </div>


        {loading ? (
          <div
            style={{
              padding: '50px',
              textAlign: 'center',
              color: theme.textMuted,
            }}
          >
            Loading leaderboard...
          </div>
        ) : (
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'center',
              gap: '12px',
            }}
          >

            {podiumOrder.map(
              (agent, index) => {
                if (!agent) {
                  return null
                }

                const config =
                  PODIUM_CONFIG[index]

                const rank =
                  Number(agent.rank)

                return (
                  <div
                    key={`${rank}-${agent.name}`}
                    style={{
                      display: 'flex',
                      flexDirection:
                        'column',
                      alignItems:
                        'center',
                      gap: '10px',
                    }}
                  >

                    {/* AGENT */}

                    <div
                      style={{
                        textAlign:
                          'center',
                      }}
                    >

                      {/* AVATAR */}

                      <div
                        style={{
                          position:
                            'relative',
                          display:
                            'inline-block',
                          marginBottom:
                            '6px',
                        }}
                      >

                        <div
                          style={{
                            width:
                              rank === 1
                                ? '68px'
                                : '56px',
                            height:
                              rank === 1
                                ? '68px'
                                : '56px',
                            borderRadius:
                              '50%',
                            background:
                              config.gradient,
                            display:
                              'flex',
                            alignItems:
                              'center',
                            justifyContent:
                              'center',
                            boxShadow:
                              `0 0 24px ${config.glow}`,
                            border:
                              `2px solid ${config.glow}`,
                            overflow:
                              'hidden',
                          }}
                        >
                          <AgentAvatar
                            agent={agent}
                            size={
                              rank === 1
                                ? 64
                                : 52
                            }
                            theme={theme}
                            podium
                          />
                        </div>


                        {/* MEDAL */}

                        <div
                          style={{
                            position:
                              'absolute',
                            top: '-6px',
                            right: '-6px',
                            fontSize:
                              '16px',
                          }}
                        >
                          {config.medal}
                        </div>

                      </div>


                      {/* NAME */}

                      <div
                        style={{
                          fontSize: '12px',
                          fontWeight: 700,
                          color:
                            theme.textPrimary,
                          maxWidth:
                            '110px',
                          textAlign:
                            'center',
                          lineHeight:
                            1.3,
                        }}
                      >
                        {agent.name ||
                          '-'}
                      </div>


                      {/* SELECTED METRIC */}

                      <div
                        style={{
                          fontSize:
                            '11px',
                          color:
                            theme.warning,
                          fontWeight: 700,
                        }}
                      >
                        {getMetricValue(
                          agent,
                          metric
                        )}
                      </div>

                    </div>


                    {/* PODIUM BLOCK */}

                    <div
                      style={{
                        width:
                          rank === 1
                            ? '130px'
                            : '100px',
                        height:
                          `${config.height}px`,
                        background:
                          config.gradient,
                        borderRadius:
                          '12px 12px 0 0',
                        display:
                          'flex',
                        alignItems:
                          'flex-start',
                        justifyContent:
                          'center',
                        paddingTop:
                          '12px',
                        boxShadow:
                          `0 -4px 20px ${config.glow}`,
                        opacity: 0.9,
                      }}
                    >
                      <span
                        style={{
                          fontSize:
                            '24px',
                          fontWeight:
                            900,
                          color:
                            'rgba(255,255,255,0.4)',
                        }}
                      >
                        {
                          config.label
                        }
                      </span>
                    </div>

                  </div>
                )
              }
            )}

          </div>
        )}

      </div>


      {/* ================================================== */}
      {/* FILTER BAR */}
      {/* ================================================== */}

      <div
        style={{
          ...glassCard,
          padding:
            '16px 20px',
          display: 'flex',
          alignItems:
            'center',
          gap: '16px',
          flexWrap:
            'wrap',
          position:
            'relative',
          zIndex: 50,
        }}
      >

        <span
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color:
              theme.textMuted,
          }}
        >
          Filter:
        </span>


        {/* METRIC */}

        <div
          style={{
            display: 'flex',
            alignItems:
              'center',
            gap: '8px',
          }}
        >

          <label
            style={{
              fontSize: '12px',
              color:
                theme.textMuted,
            }}
          >
            Metric:
          </label>

          <ThemeDropdown
            value={metric}
            options={
              metricOptions
            }
            onChange={
              setMetric
            }
            theme={theme}
            width="145px"
          />

        </div>


        {/* PERIOD */}

        <div
          style={{
            display: 'flex',
            alignItems:
              'center',
            gap: '8px',
          }}
        >

          <label
            style={{
              fontSize: '12px',
              color:
                theme.textMuted,
            }}
          >
            Period:
          </label>

          <ThemeDropdown
            value={period}
            options={
              periodOptions
            }
            onChange={
              setPeriod
            }
            theme={theme}
            width="145px"
          />

        </div>

      </div>


      {/* ================================================== */}
      {/* FULL RANKINGS */}
      {/* ================================================== */}

      <div
        style={{
          ...glassCard,
          padding: '0',
          overflow: 'hidden',
        }}
      >

        <div
          style={{
            padding:
              '20px 24px',
            borderBottom:
              `1px solid ${theme.cardBorder}`,
          }}
        >
          <div
            style={{
              fontSize: '15px',
              fontWeight: 700,
              color:
                theme.textPrimary,
            }}
          >
            Full Rankings
          </div>

          <div
            style={{
              marginTop: '4px',
              fontSize: '12px',
              color:
                theme.textMuted,
            }}
          >
            Ranked by{' '}
            {getMetricLabel(metric)}
          </div>
        </div>


        <div
          style={{
            overflowX:
              'auto',
          }}
        >

          <table
            style={{
              width: '100%',
              borderCollapse:
                'collapse',
            }}
          >

            <thead>

              <tr
                style={{
                  background:
                    theme.tableRowAlt,
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {[
                  'Rank',
                  'Agent',
                  'FCR (%)',
                  'SLA (%)',
                  'MTTR (hrs)',
                  'Points',
                ].map(header => (
                  <th
                    key={header}
                    style={{
                      padding:
                        '12px 20px',
                      textAlign:
                        'left',
                      fontSize:
                        '11px',
                      fontWeight:
                        700,
                      color:
                        theme.textMuted,
                      textTransform:
                        'uppercase',
                      letterSpacing:
                        '0.8px',
                      whiteSpace:
                        'nowrap',
                    }}
                  >
                    {header}
                  </th>
                ))}

              </tr>

            </thead>


            <tbody>

              {/* LOADING */}

              {loading && (
                <tr>
                  <td
                    colSpan="6"
                    style={{
                      padding:
                        '40px',
                      textAlign:
                        'center',
                      color:
                        theme.textMuted,
                    }}
                  >
                    Loading Oracle
                    leaderboard
                    data...
                  </td>
                </tr>
              )}


              {/* ERROR */}

              {!loading &&
                error && (
                  <tr>
                    <td
                      colSpan="6"
                      style={{
                        padding:
                          '40px',
                        textAlign:
                          'center',
                        color:
                          theme.danger,
                      }}
                    >
                      Failed to load
                      leaderboard
                      data.

                      <div
                        style={{
                          marginTop:
                            '8px',
                          fontSize:
                            '12px',
                          color:
                            theme.textMuted,
                        }}
                      >
                        {error}
                      </div>
                    </td>
                  </tr>
                )}


              {/* DATA */}

              {!loading &&
                !error &&
                sortedLeaderboard.map(
                  (
                    agent,
                    index
                  ) => (
                    <LeaderboardRow
                      key={`${agent.rank}-${agent.name}-${index}`}
                      agent={agent}
                      index={index}
                      isCurrentUser={
                        user?.role ===
                          'agent' &&
                        agent.name ===
                          user?.name
                      }
                      maxPoints={
                        maxPoints
                      }
                      theme={theme}
                    />
                  )
                )}


              {/* EMPTY */}

              {!loading &&
                !error &&
                sortedLeaderboard.length ===
                  0 && (
                  <tr>
                    <td
                      colSpan="6"
                      style={{
                        padding:
                          '40px',
                        textAlign:
                          'center',
                        color:
                          theme.textMuted,
                      }}
                    >
                      No leaderboard
                      data found
                      in Oracle.
                    </td>
                  </tr>
                )}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  )
}


// ------------------------------------------------------------
// LEADERBOARD ROW
// ------------------------------------------------------------

function LeaderboardRow({
  agent,
  index,
  isCurrentUser,
  maxPoints,
  theme,
}) {
  const [hovered, setHovered] =
    useState(false)

  const rank =
    Number(agent.rank || 0)

  const points =
    Number(
      agent.points ??
      agent.POINTS ??
      0
    )

  const fcr =
    Number(
      agent.fcr ??
      agent.FCR ??
      agent.fcr_percentage ??
      agent.FCR_PERCENTAGE ??
      0
    )

  const sla =
    Number(
      agent.sla ??
      agent.slaCompliance ??
      agent.sla_percentage ??
      agent.SLA_PERCENTAGE ??
      0
    )

  const mttr =
    Number(
      agent.mttr ??
      agent.mttr_hours ??
      agent.MTTR ??
      agent.MTTR_HOURS ??
      0
    )

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

        background:
          isCurrentUser
            ? `${theme.accentSecondary}12`
            : hovered
              ? theme.tableRowHover
              : index % 2 === 0
                ? 'transparent'
                : theme.tableRowAlt,

        transition:
          'all 0.2s',

        transform:
          hovered
            ? 'translateX(3px)'
            : 'translateX(0)',
      }}
    >

      {/* RANK */}

      <td
        style={{
          padding:
            '14px 20px',
        }}
      >
        <MedalIcon
          rank={rank}
          theme={theme}
        />
      </td>


      {/* AGENT */}

      <td
        style={{
          padding:
            '14px 20px',
        }}
      >

        <div
          style={{
            display:
              'flex',
            alignItems:
              'center',
            gap: '10px',
          }}
        >

          <AgentAvatar
            agent={agent}
            size={34}
            theme={theme}
          />


          <div>

            <div
              style={{
                fontSize:
                  '13px',
                fontWeight:
                  600,
                color:
                  isCurrentUser
                    ? theme.accentSecondary
                    : theme.textPrimary,
              }}
            >
              {agent.name ||
                '-'}
            </div>

            {isCurrentUser && (
              <div
                style={{
                  fontSize:
                    '10px',
                  color:
                    theme.accentSecondary,
                  fontWeight:
                    600,
                }}
              >
                You
              </div>
            )}

          </div>

        </div>

      </td>


      {/* FCR */}

      <td
        style={{
          padding:
            '14px 20px',
          fontSize:
            '13px',
          fontWeight:
            600,
          color:
            fcr >= 80
              ? theme.success
              : fcr >= 50
                ? theme.warning
                : theme.danger,
        }}
      >
        {fcr.toFixed(2)}%
      </td>


      {/* SLA */}

      <td
        style={{
          padding:
            '14px 20px',
          fontSize:
            '13px',
          fontWeight:
            600,
          color:
            sla >= 90
              ? theme.success
              : sla >= 70
                ? theme.warning
                : theme.danger,
        }}
      >
        {sla.toFixed(2)}%
      </td>


      {/* MTTR */}

      <td
        style={{
          padding:
            '14px 20px',
          fontSize:
            '13px',
          color:
            theme.textSecondary,
        }}
      >
        {mttr.toFixed(2)}
      </td>


      {/* POINTS */}

      <td
        style={{
          padding:
            '14px 20px',
        }}
      >

        <div
          style={{
            display:
              'flex',
            alignItems:
              'center',
            gap: '10px',
          }}
        >

          <span
            style={{
              fontSize:
                '13px',
              fontWeight:
                700,
              color:
                theme.warning,
              minWidth:
                '45px',
            }}
          >
            {points}
          </span>


          <div
            style={{
              flex: 1,
              height:
                '5px',
              background:
                theme.tableRowAlt,
              borderRadius:
                '4px',
              overflow:
                'hidden',
              minWidth:
                '60px',
              border:
                `1px solid ${theme.cardBorder}`,
            }}
          >

            <div
              style={{
                height:
                  '100%',
                width:
                  `${Math.min(
                    (points /
                      maxPoints) *
                      100,
                    100
                  )}%`,
                background:
                  theme.accentGrad,
                borderRadius:
                  '4px',
                transition:
                  'width 1s ease',
              }}
            />

          </div>

        </div>

      </td>

    </tr>
  )
}
