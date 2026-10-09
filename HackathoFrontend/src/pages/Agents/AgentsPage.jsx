
import React, {
  useEffect,
  useMemo,
  useState,
} from 'react'

import { useTheme } from '../../context/ThemeContext.jsx'

import { getAgents } from '../../services/api.js'


// ------------------------------------------------------------
// STATUS BADGE
// ------------------------------------------------------------

function StatusBadge({ status, theme }) {

  const isActive = status === 'Active'

  const color = isActive
    ? theme.success
    : theme.warning

  return (
    <span
      style={{
        background: `${color}18`,
        color,
        border: `1px solid ${color}30`,
        borderRadius: '20px',
        padding: '4px 10px',
        fontSize: '12px',
        fontWeight: 600,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        whiteSpace: 'nowrap',
      }}
    >

      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 4px ${color}`,
        }}
      />

      {status}

    </span>
  )
}


// ------------------------------------------------------------
// AGENT TABLE
// ------------------------------------------------------------

function AgentTable({ agents, theme }) {

  return (
    <div
      style={{
        width: '100%',
        overflowX: 'auto',
      }}
    >

      <table
        style={{
          width: '100%',
          minWidth: '850px',
          borderCollapse: 'separate',
          borderSpacing: 0,
        }}
      >

        {/* TABLE HEADER */}

        <thead>

          <tr
            style={{
              background: theme.tableRowAlt,
            }}
          >

            {[
              'Name',
              'Role',
              'FCR (%)',
              'SLA (%)',
              'MTTR (hrs)',
              'Points',
              'Status',
            ].map(header => (

              <th
                key={header}
                style={{
                  padding: '13px 16px',
                  textAlign: 'left',
                  fontSize: '11px',
                  fontWeight: 700,
                  color: theme.textMuted,
                  textTransform: 'uppercase',
                  letterSpacing: '0.8px',
                  whiteSpace: 'nowrap',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                  background:
                    theme.tableRowAlt,
                }}
              >

                {header}

              </th>

            ))}

          </tr>

        </thead>


        {/* TABLE BODY */}

        <tbody>

          {agents.map((agent, i) => (

            <tr
              key={`${agent.name}-${i}`}
              style={{
                borderBottom:
                  `1px solid ${theme.cardBorder}`,
              }}
            >

              {/* NAME */}

              <td
                style={{
                  padding: '14px 16px',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                  }}
                >

                  {/* AVATAR */}

                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      minWidth: '36px',
                      background:
                        theme.accentGrad,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 700,
                      color: '#fff',
                    }}
                  >

                    {String(agent.name || '?')
                      .split(' ')
                      .map(n => n[0])
                      .join('')
                      .slice(0, 2)
                      .toUpperCase()}

                  </div>


                  {/* NAME */}

                  <span
                    style={{
                      fontWeight: 600,
                      color: theme.textPrimary,
                      fontSize: '14px',
                      whiteSpace: 'nowrap',
                    }}
                  >

                    {agent.name || '-'}

                  </span>

                </div>

              </td>


              {/* ROLE */}

              <td
                style={{
                  padding: '14px 16px',
                  fontSize: '13px',
                  color: theme.textSecondary,
                  whiteSpace: 'nowrap',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {agent.role || '-'}

              </td>


              {/* FCR */}

              <td
                style={{
                  padding: '14px 16px',
                  fontSize: '14px',
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                  color:
                    Number(agent.fcr) >= 80
                      ? theme.success
                      : Number(agent.fcr) >= 50
                        ? theme.warning
                        : theme.danger,
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {Number(agent.fcr || 0).toFixed(2)}%

              </td>


              {/* SLA */}

              <td
                style={{
                  padding: '14px 16px',
                  fontSize: '14px',
                  color: theme.textSecondary,
                  whiteSpace: 'nowrap',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {Number(agent.sla || 0).toFixed(2)}%

              </td>


              {/* MTTR */}

              <td
                style={{
                  padding: '14px 16px',
                  fontSize: '14px',
                  color: theme.textSecondary,
                  whiteSpace: 'nowrap',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {Number(agent.mttr || 0).toFixed(2)}

              </td>


              {/* POINTS */}

              <td
                style={{
                  padding: '14px 16px',
                  fontSize: '14px',
                  fontWeight: 700,
                  color: theme.accent,
                  whiteSpace: 'nowrap',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                {Number(agent.points || 0)}

              </td>


              {/* STATUS */}

              <td
                style={{
                  padding: '14px 16px',
                  borderBottom:
                    `1px solid ${theme.cardBorder}`,
                }}
              >

                <StatusBadge
                  status={agent.status || 'Away'}
                  theme={theme}
                />

              </td>

            </tr>

          ))}


          {/* NO DATA */}

          {agents.length === 0 && (

            <tr>

              <td
                colSpan={7}
                style={{
                  padding: '50px',
                  textAlign: 'center',
                  color: theme.textMuted,
                  fontSize: '14px',
                }}
              >

                No Oracle agent data found.

              </td>

            </tr>

          )}

        </tbody>

      </table>

    </div>
  )
}


// ------------------------------------------------------------
// AGENTS PAGE
// ------------------------------------------------------------

export default function AgentsPage() {

  const { theme } = useTheme()


  // ----------------------------------------------------------
  // STATE
  // ----------------------------------------------------------

  const [agents, setAgents] =
    useState([])

  const [search, setSearch] =
    useState('')

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState(null)


  // ----------------------------------------------------------
  // LOAD ORACLE DATA
  // ----------------------------------------------------------

  useEffect(() => {

    let mounted = true

    async function loadAgents() {

      setLoading(true)
      setError(null)

      try {

        const data =
          await getAgents()

        if (!mounted) {
          return
        }

        setAgents(
          Array.isArray(data)
            ? data
            : []
        )

      } catch (err) {

        console.error(
          '[AgentsPage] Failed to load Oracle agents:',
          err
        )

        if (mounted) {

          setAgents([])

          setError(
            err?.message ||
            'Failed to load agent data'
          )

        }

      } finally {

        if (mounted) {
          setLoading(false)
        }

      }

    }

    loadAgents()

    return () => {
      mounted = false
    }

  }, [])


  // ----------------------------------------------------------
  // SEARCH
  // ----------------------------------------------------------

  const filteredAgents =
    useMemo(() => {

      const value =
        search
          .trim()
          .toLowerCase()

      if (!value) {
        return agents
      }

      return agents.filter(agent =>

        String(agent.name || '')
          .toLowerCase()
          .includes(value)

        ||

        String(agent.role || '')
          .toLowerCase()
          .includes(value)

        ||

        String(agent.status || '')
          .toLowerCase()
          .includes(value)

      )

    }, [
      agents,
      search,
    ])


  // ----------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------

  return (

    <div
      style={{
        width: '100%',
        minWidth: 0,
      }}
    >

      {/* ================================================== */}
      {/* PAGE HEADER */}
      {/* ================================================== */}

      <div
        style={{
          marginBottom: '24px',
        }}
      >

        <h2
          style={{
            fontSize: '22px',
            fontWeight: 700,
            color: theme.textPrimary,
            marginBottom: '4px',
          }}
        >

          Agents{' '}

          <span
            style={{
              color: theme.accent,
            }}
          >

            Team

          </span>

        </h2>


        <p
          style={{
            color: theme.textSecondary,
            fontSize: '14px',
          }}
        >

          Team member performance overview

        </p>

      </div>


      {/* ================================================== */}
      {/* MAIN CARD */}
      {/* ================================================== */}

      <div
        style={{
          background: theme.cardBg,
          borderRadius: '14px',
          border:
            `1px solid ${theme.cardBorder}`,
          boxShadow:
            theme.cardShadow,
          overflow: 'hidden',
        }}
      >

        {/* ================================================== */}
        {/* CARD HEADER */}
        {/* ================================================== */}

        <div
          style={{
            padding:
              '16px 20px',

            borderBottom:
              `1px solid ${theme.cardBorder}`,

            display: 'flex',

            alignItems: 'center',

            justifyContent:
              'space-between',

            gap: '16px',

            flexWrap: 'wrap',
          }}
        >

          {/* COUNT */}

          <span
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: theme.textPrimary,
            }}
          >

            {loading

              ? 'Loading agents...'

              : `${filteredAgents.length} agents`

            }

          </span>


          {/* SEARCH */}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: theme.inputBg,
              border:
                `1px solid ${theme.inputBorder}`,
              borderRadius: '8px',
              padding: '8px 12px',
            }}
          >

            {/* SEARCH ICON */}

            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke={theme.textMuted}
              strokeWidth="2"
            >

              <circle
                cx="11"
                cy="11"
                r="8"
              />

              <line
                x1="21"
                y1="21"
                x2="16.65"
                y2="16.65"
              />

            </svg>


            {/* SEARCH INPUT */}

            <input
              value={search}

              onChange={event =>
                setSearch(
                  event.target.value
                )
              }

              placeholder="Search agents..."

              style={{
                border: 'none',
                background: 'transparent',
                fontSize: '13px',
                color: theme.textPrimary,
                width: '180px',
                outline: 'none',
              }}
            />

          </div>

        </div>


        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (

          <div
            style={{
              padding:
                '16px 20px',

              color:
                theme.danger,

              background:
                `${theme.danger}10`,

              fontSize:
                '13px',
            }}
          >

            Failed to load Oracle agent data:
            {' '}
            {error}

          </div>

        )}


        {/* ================================================== */}
        {/* ALL AGENTS TABLE */}
        {/* ================================================== */}

        <div
          style={{
            width: '100%',
            overflowX: 'auto',
          }}
        >

          {!loading &&
            !error && (

              <AgentTable
                agents={
                  filteredAgents
                }
                theme={
                  theme
                }
              />

            )}


          {/* LOADING */}

          {loading && (

            <div
              style={{
                padding: '40px',
                textAlign: 'center',
                color: theme.textMuted,
                fontSize: '14px',
              }}
            >

              Loading Oracle data...

            </div>

          )}

        </div>

      </div>

    </div>
  )
}
