import React, { useState } from 'react'
import { useTheme } from '../../context/ThemeContext.jsx'


// ============================================================
// INSIGHT CARD
// ============================================================

function InsightCard({
  icon,
  title,
  badge,
  badgeColor,
  description,
  borderColor,
  theme,
}) {
  return (
    <div
      style={{
        background: theme.cardBg,
        border: `1px solid ${theme.cardBorder}`,
        borderLeft: `3px solid ${borderColor}`,
        borderRadius: '16px',
        padding: '22px',
        minHeight: '145px',
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
        }}
      >

        <div
          style={{
            width: '40px',
            height: '40px',
            minWidth: '40px',
            borderRadius: '11px',
            background: `${borderColor}16`,
            border: `1px solid ${borderColor}45`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: borderColor,
            fontSize: '20px',
          }}
        >
          {icon}
        </div>


        <div
          style={{
            flex: 1,
          }}
        >

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '5px',
              flexWrap: 'wrap',
            }}
          >

            <div
              style={{
                fontSize: '14px',
                fontWeight: 800,
                color: theme.textPrimary,
              }}
            >
              {title}
            </div>

            <span
              style={{
                fontSize: '10px',
                fontWeight: 800,
                color: badgeColor,
                border: `1px solid ${badgeColor}50`,
                background: `${badgeColor}12`,
                borderRadius: '7px',
                padding: '3px 8px',
              }}
            >
              {badge}
            </span>

          </div>


          <div
            style={{
              fontSize: '12px',
              lineHeight: 1.55,
              color: theme.textSecondary,
              maxWidth: '420px',
            }}
          >
            {description}
          </div>


          <button
            type="button"
            style={{
              marginTop: '14px',
              height: '32px',
              padding: '0 14px',
              borderRadius: '8px',
              border: `1px solid ${theme.cardBorder}`,
              background: theme.tableRowAlt,
              color: theme.textSecondary,
              fontSize: '11px',
              cursor: 'pointer',
            }}
          >
            <span
              style={{
                marginRight: '7px',
              }}
            >
              ⌄
            </span>

            View Recommendations
          </button>

        </div>

      </div>
    </div>
  )
}


// ============================================================
// SIMILAR INCIDENT ROW
// ============================================================

function SimilarIncidentRow({
  incident,
  theme,
}) {

  const slaStatus =
    incident.sla_status
      ? String(
          incident.sla_status
        ).toUpperCase()
      : ''


  return (
    <tr
      style={{
        borderTop:
          `1px solid ${theme.cardBorder}`,
      }}
    >

      {/* Incident */}

      <td
        style={{
          padding: '12px',
          color: theme.accent,
          fontWeight: 700,
          fontSize: '13px',
          whiteSpace: 'nowrap',
        }}
      >
        {incident.number || 'N/A'}
      </td>


      {/* Description */}

      <td
        style={{
          padding: '12px',
          color: theme.textSecondary,
          fontSize: '13px',
          minWidth: '240px',
        }}
      >
        {incident.short_description || 'N/A'}
      </td>


      {/* Similarity */}

      <td
        style={{
          padding: '12px',
          color: theme.textSecondary,
          fontSize: '13px',
          whiteSpace: 'nowrap',
        }}
      >
        {incident.similarity_score != null
          ? Number(
              incident.similarity_score
            ).toFixed(4)
          : 'N/A'}
      </td>


      {/* Assignment Group */}

      <td
        style={{
          padding: '12px',
          color: theme.textSecondary,
          fontSize: '13px',
          whiteSpace: 'nowrap',
        }}
      >
        {incident.assignment_group || 'N/A'}
      </td>


      {/* Resolution Hours */}

      <td
        style={{
          padding: '12px',
          color: theme.textSecondary,
          fontSize: '13px',
          whiteSpace: 'nowrap',
        }}
      >
        {incident.resolution_hours != null
          ? Number(
              incident.resolution_hours
            ).toFixed(2)
          : 'N/A'}
      </td>


      {/* SLA */}

      <td
        style={{
          padding: '12px',
          fontSize: '12px',
          fontWeight: 700,
          whiteSpace: 'nowrap',
        }}
      >

        {slaStatus ? (

          <span
            style={{
              color:
                slaStatus === 'MET'
                  ? theme.success
                  : theme.danger,

              background:
                slaStatus === 'MET'
                  ? `${theme.success}12`
                  : `${theme.danger}12`,

              border:
                slaStatus === 'MET'
                  ? `1px solid ${theme.success}35`
                  : `1px solid ${theme.danger}35`,

              borderRadius: '6px',

              padding: '4px 8px',
            }}
          >
            {slaStatus}
          </span>

        ) : (

          <span
            style={{
              color: theme.textMuted,
            }}
          >
            N/A
          </span>

        )}

      </td>

    </tr>
  )
}


// ============================================================
// MAIN PAGE
// ============================================================

export default function AIInsightsPage() {

  const { theme } = useTheme()


  // ============================================================
  // STATE
  // ============================================================

  const [
    incidentNumber,
    setIncidentNumber,
  ] = useState('')


  const [
    result,
    setResult,
  ] = useState(null)


  const [
    loading,
    setLoading,
  ] = useState(false)


  const [
    error,
    setError,
  ] = useState('')


  // ============================================================
  // SEARCH INCIDENT
  // ============================================================

  const searchIncident = async () => {

    const incident =
      incidentNumber.trim()


    // ----------------------------------------------------------
    // Validation
    // ----------------------------------------------------------

    if (!incident) {

      setError(
        'Please enter an incident number.'
      )

      setResult(null)

      return
    }


    try {

      setLoading(true)

      setError('')

      setResult(null)


      console.log(
        '[AI INSIGHTS] Searching:',
        incident
      )


      // ========================================================
      // IMPORTANT
      //
      // Your server.js is:
      //
      // app.use(
      //   '/api/v1/aiinsights',
      //   require('./routes/aiinsights')
      // )
      //
      // Therefore the frontend URL MUST be:
      //
      // /api/v1/aiinsights/:incidentNumber
      //
      // NOT:
      //
      // /api/v1/ai-insights/:incidentNumber
      // ========================================================

      const apiUrl =
        `/api/v1/aiinsights/${encodeURIComponent(
          incident
        )}`


      console.log(
        '[AI INSIGHTS] API URL:',
        apiUrl
      )


      const response =
        await fetch(
          apiUrl,
          {
            method: 'GET',

            headers: {
              Accept:
                'application/json',
            },
          }
        )


      // ========================================================
      // HTTP STATUS
      // ========================================================

      console.log(
        '[AI INSIGHTS] HTTP status:',
        response.status
      )


      // ========================================================
      // READ RESPONSE AS TEXT FIRST
      //
      // Do NOT directly use:
      //
      // await response.json()
      //
      // because if Express returns an empty response,
      // JSON.parse will throw:
      //
      // Unexpected end of JSON input
      // ========================================================

      const responseText =
        await response.text()


      console.log(
        '[AI INSIGHTS] Raw response:',
        responseText
      )


      // ========================================================
      // EMPTY RESPONSE
      // ========================================================

      if (
        !responseText ||
        !responseText.trim()
      ) {

        throw new Error(
          `Server returned an empty response (HTTP ${response.status})`
        )

      }


      // ========================================================
      // PARSE JSON
      // ========================================================

      let json

      try {

        json =
          JSON.parse(
            responseText
          )

      } catch (parseError) {

        console.error(
          '[AI INSIGHTS] JSON parse error:',
          parseError
        )

        throw new Error(
          `Server returned invalid JSON (HTTP ${response.status})`
        )

      }


      console.log(
        '[AI INSIGHTS] Parsed response:',
        json
      )


      // ========================================================
      // BACKEND ERROR
      // ========================================================

      if (!response.ok) {

        throw new Error(
          json.error ||
          json.message ||
          `Unable to retrieve AI insights (HTTP ${response.status})`
        )

      }


      // ========================================================
      // SUCCESS RESPONSE VALIDATION
      // ========================================================

      if (
        !json ||
        json.success !== true
      ) {

        throw new Error(
          json?.error ||
          'AI Insights request failed.'
        )

      }


      if (!json.data) {

        throw new Error(
          'AI Insights API returned no data.'
        )

      }


      // ========================================================
      // STORE RESULT
      // ========================================================

      setResult(
        json.data
      )


    } catch (err) {

      console.error(
        '[AI INSIGHTS] Error:',
        err
      )


      setError(
        err.message ||
        'Unable to retrieve AI insights.'
      )


      setResult(null)


    } finally {

      setLoading(false)

    }

  }


  // ============================================================
  // ENTER KEY
  // ============================================================

  const handleKeyDown = event => {

    if (
      event.key === 'Enter'
    ) {

      event.preventDefault()

      searchIncident()

    }

  }


  // ============================================================
  // SIMILAR INCIDENTS
  // ============================================================

  const similarIncidents =
    Array.isArray(
      result?.similar_incidents
    )
      ? result.similar_incidents
      : []


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        width: '100%',
      }}
    >

      {/* ====================================================== */}
      {/* TOP HEADER + SEARCH */}
      {/* ====================================================== */}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '20px',
          flexWrap: 'wrap',
        }}
      >

        {/* Page title */}

        <div>

          <h1
            style={{
              fontSize: '26px',
              fontWeight: 800,
              color: theme.textPrimary,
              margin: 0,
            }}
          >
            AI{' '}

            <span
              style={{
                color: theme.accent,
              }}
            >
              Insights
            </span>

          </h1>


          <div
            style={{
              fontSize: '13px',
              color: theme.textMuted,
              marginTop: '4px',
            }}
          >
            Powered by intelligent analysis
          </div>

        </div>


        {/* Search */}

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            width: '380px',
            maxWidth: '100%',
            height: '46px',
            borderRadius: '9px',
            border:
              `1px solid ${theme.cardBorder}`,
            background:
              theme.tableRowAlt,
            padding: '0 12px',
            boxSizing: 'border-box',
          }}
        >

          <span
            style={{
              color: theme.textMuted,
              fontSize: '17px',
              marginRight: '9px',
            }}
          >
            ⌕
          </span>


          <input
            type="text"
            value={incidentNumber}
            onChange={event =>
              setIncidentNumber(
                event.target.value
              )
            }
            onKeyDown={
              handleKeyDown
            }
            placeholder="Search incident number..."
            disabled={loading}
            style={{
              flex: 1,
              height: '100%',
              minWidth: 0,
              border: 'none',
              outline: 'none',
              background: 'transparent',
              color:
                theme.textPrimary,
              fontSize: '12px',
            }}
          />


          <button
            type="button"
            onClick={
              searchIncident
            }
            disabled={loading}
            style={{
              height: '32px',
              padding: '0 12px',
              borderRadius: '7px',
              border: 'none',
              background:
                theme.accentGrad,
              color: '#fff',
              fontSize: '11px',
              fontWeight: 700,
              cursor: loading
                ? 'wait'
                : 'pointer',
              opacity: loading
                ? 0.65
                : 1,
            }}
          >
            {loading
              ? '...'
              : 'Search'}
          </button>

        </div>

      </div>


      {/* ====================================================== */}
      {/* AI INSIGHT CARDS */}
      {/* ====================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(2, minmax(0, 1fr))',
          gap: '18px',
        }}
      >

        <InsightCard
          icon="⚠"
          title="SLA Compliance Critical"
          badge="HIGH"
          badgeColor={
            theme.danger
          }
          borderColor={
            theme.danger
          }
          description={
            <>
              SLA at <strong>6.78%</strong>,
              23% below target.
              Immediate action required
              to prevent service degradation
              and customer churn.
            </>
          }
          theme={theme}
        />


        <InsightCard
          icon="◷"
          title="Elevated MTTR Detected"
          badge="MEDIUM"
          badgeColor="#f5b51b"
          borderColor="#f5b51b"
          description={
            <>
              Avg MTTR <strong>860.49 hrs</strong>.
              Top 3 agents average 45 hrs less.
              Several agents show resolution
              times exceeding 1000 hours.
            </>
          }
          theme={theme}
        />


        <InsightCard
          icon="⟳"
          title="High Reassignment Rate"
          badge="MEDIUM"
          badgeColor="#f5b51b"
          borderColor="#f5b51b"
          description={
            <>
              <strong>34 incidents</strong> reassigned,
              increasing resolution time by 40%.
              Multiple reassignments indicate
              routing accuracy issues.
            </>
          }
          theme={theme}
        />


        <InsightCard
          icon="☆"
          title="Top Performer Identified"
          badge="LOW"
          badgeColor={
            theme.success
          }
          borderColor={
            theme.success
          }
          description={
            <>
              Guillermo Fröhlich:
              <strong>100% FCR</strong>,
              100% SLA. Outstanding performance
              that can serve as a best-practice
              template for the team.
            </>
          }
          theme={theme}
        />

      </div>


      {/* ====================================================== */}
      {/* ACTION ITEMS */}
      {/* ====================================================== */}

      <div
        style={{
          background:
            theme.cardBg,
          border:
            `1px solid ${theme.cardBorder}`,
          borderRadius: '16px',
          padding: '24px',
          boxSizing: 'border-box',
        }}
      >

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px',
          }}
        >

          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '9px',
              background:
                `${theme.danger}15`,
              border:
                `1px solid ${theme.danger}40`,
              color:
                theme.danger,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
            }}
          >
            !
          </div>


          <div>

            <div
              style={{
                color:
                  theme.textPrimary,
                fontSize: '14px',
                fontWeight: 800,
              }}
            >
              3 Action Items Required
            </div>


            <div
              style={{
                color:
                  theme.textMuted,
                fontSize: '11px',
                marginTop: '2px',
              }}
            >
              Immediate attention needed
            </div>

          </div>

        </div>


        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '9px',
          }}
        >

          <div
            style={{
              minHeight: '40px',
              display: 'flex',
              alignItems: 'center',
              padding: '0 14px',
              borderRadius: '9px',
              background:
                theme.tableRowAlt,
              border:
                `1px solid ${theme.cardBorder}`,
              color:
                theme.textSecondary,
              fontSize: '12px',
            }}
          >

            <span
              style={{
                width: '8px',
                height: '8px',
                minWidth: '8px',
                borderRadius: '50%',
                background:
                  theme.danger,
                marginRight: '10px',
              }}
            />

            Train agents on SLA protocols —
            SLA compliance at critical 6.78%

          </div>


          <div
            style={{
              minHeight: '40px',
              display: 'flex',
              alignItems: 'center',
              padding: '0 14px',
              borderRadius: '9px',
              background:
                theme.tableRowAlt,
              border:
                `1px solid ${theme.cardBorder}`,
              color:
                theme.textSecondary,
              fontSize: '12px',
            }}
          >

            <span
              style={{
                width: '8px',
                height: '8px',
                minWidth: '8px',
                borderRadius: '50%',
                background:
                  '#f5b51b',
                marginRight: '10px',
              }}
            />

            Review long-pending incidents
            and eliminate resolution bottlenecks

          </div>


          <div
            style={{
              minHeight: '40px',
              display: 'flex',
              alignItems: 'center',
              padding: '0 14px',
              borderRadius: '9px',
              background:
                theme.tableRowAlt,
              border:
                `1px solid ${theme.cardBorder}`,
              color:
                theme.textSecondary,
              fontSize: '12px',
            }}
          >

            <span
              style={{
                width: '8px',
                height: '8px',
                minWidth: '8px',
                borderRadius: '50%',
                background:
                  '#f5b51b',
                marginRight: '10px',
              }}
            />

            Improve initial routing accuracy
            to reduce 34+ reassigned incidents

          </div>

        </div>

      </div>


      {/* ====================================================== */}
      {/* ERROR */}
      {/* ====================================================== */}

      {error && (

        <div
          style={{
            padding: '14px 18px',
            borderRadius: '10px',
            background:
              `${theme.danger}14`,
            border:
              `1px solid ${theme.danger}40`,
            color:
              theme.danger,
            fontSize: '13px',
          }}
        >

          <strong>
            AI Insights Error:
          </strong>{' '}

          {error}

        </div>

      )}


      {/* ====================================================== */}
      {/* LOADING */}
      {/* ====================================================== */}

      {loading && (

        <div
          style={{
            padding: '20px',
            textAlign: 'center',
            color:
              theme.textMuted,
            fontSize: '13px',
            background:
              theme.cardBg,
            border:
              `1px solid ${theme.cardBorder}`,
            borderRadius: '16px',
          }}
        >

          Searching AI insights for{' '}

          <strong
            style={{
              color:
                theme.accent,
            }}
          >
            {incidentNumber.trim()}
          </strong>

          ...

        </div>

      )}


      {/* ====================================================== */}
      {/* SEARCH RESULT */}
      {/* ====================================================== */}

      {result && !loading && (

        <>

          {/* ================================================== */}
          {/* INCIDENT INFORMATION */}
          {/* ================================================== */}

          <div
            style={{
              background:
                theme.cardBg,
              border:
                `1px solid ${theme.cardBorder}`,
              borderRadius: '16px',
              padding: '24px',
              boxSizing: 'border-box',
            }}
          >

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '15px',
                marginBottom: '20px',
                flexWrap: 'wrap',
              }}
            >

              <div>

                <div
                  style={{
                    fontSize: '11px',
                    color:
                      theme.textMuted,
                    textTransform:
                      'uppercase',
                    letterSpacing: '1px',
                    marginBottom: '7px',
                  }}
                >
                  Incident
                </div>


                <div
                  style={{
                    fontSize: '20px',
                    fontWeight: 800,
                    color:
                      theme.accent,
                  }}
                >
                  {result.incident_number ||
                    incidentNumber}
                </div>

              </div>


              {result.recommendation_id != null && (

                <div
                  style={{
                    padding: '7px 11px',
                    borderRadius: '8px',
                    background:
                      theme.tableRowAlt,
                    border:
                      `1px solid ${theme.cardBorder}`,
                    color:
                      theme.textMuted,
                    fontSize: '11px',
                  }}
                >

                  Recommendation ID:{' '}

                  <strong
                    style={{
                      color:
                        theme.textSecondary,
                    }}
                  >
                    {result.recommendation_id}
                  </strong>

                </div>

              )}

            </div>


            <div
              style={{
                fontSize: '11px',
                color:
                  theme.textMuted,
                textTransform:
                  'uppercase',
                letterSpacing: '1px',
                marginBottom: '7px',
              }}
            >
              AI Recommendation
            </div>


            <div
              style={{
                fontSize: '14px',
                lineHeight: 1.7,
                color:
                  theme.textSecondary,
                background:
                  theme.tableRowAlt,
                border:
                  `1px solid ${theme.cardBorder}`,
                borderRadius: '10px',
                padding: '15px',
                whiteSpace: 'pre-wrap',
              }}
            >
              {result.recommendation ||
                'No recommendation available.'}
            </div>

          </div>


          {/* ================================================== */}
          {/* SIMILAR INCIDENTS */}
          {/* ================================================== */}

          <div
            style={{
              background:
                theme.cardBg,
              border:
                `1px solid ${theme.cardBorder}`,
              borderRadius: '16px',
              padding: '24px',
              overflow: 'hidden',
              boxSizing: 'border-box',
            }}
          >

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '15px',
                marginBottom: '18px',
                flexWrap: 'wrap',
              }}
            >

              <div>

                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color:
                      theme.textPrimary,
                  }}
                >
                  Similar Incidents
                </div>


                <div
                  style={{
                    fontSize: '12px',
                    color:
                      theme.textMuted,
                    marginTop: '4px',
                  }}
                >
                  {similarIncidents.length}{' '}
                  similar incidents found
                </div>

              </div>


              {result.recommendation_id != null && (

                <div
                  style={{
                    fontSize: '11px',
                    color:
                      theme.textMuted,
                  }}
                >
                  Based on recommendation #{' '}
                  {result.recommendation_id}
                </div>

              )}

            </div>


            {similarIncidents.length === 0 ? (

              <div
                style={{
                  color:
                    theme.textMuted,
                  fontSize: '13px',
                  padding: '20px 0',
                  textAlign: 'center',
                }}
              >
                No similar incidents found.
              </div>

            ) : (

              <div
                style={{
                  overflowX: 'auto',
                  width: '100%',
                }}
              >

                <table
                  style={{
                    width: '100%',
                    minWidth: '850px',
                    borderCollapse:
                      'collapse',
                  }}
                >

                  <thead>

                    <tr>

                      {[
                        'Incident',
                        'Description',
                        'Similarity',
                        'Assignment Group',
                        'Resolution Hours',
                        'SLA',
                      ].map(
                        header => (

                          <th
                            key={header}
                            style={{
                              padding: '12px',
                              textAlign:
                                'left',
                              color:
                                theme.textMuted,
                              fontSize: '11px',
                              textTransform:
                                'uppercase',
                              whiteSpace:
                                'nowrap',
                            }}
                          >
                            {header}
                          </th>

                        )
                      )}

                    </tr>

                  </thead>


                  <tbody>

                    {similarIncidents.map(
                      (
                        incident,
                        index
                      ) => (

                        <SimilarIncidentRow
                          key={
                            `${
                              incident.number ||
                              'incident'
                            }-${index}`
                          }
                          incident={
                            incident
                          }
                          theme={
                            theme
                          }
                        />

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        </>

      )}

    </div>
  )
}
