import React, {
  useEffect,
  useState
} from 'react'

import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

import {
  useTheme
} from '../../context/ThemeContext.jsx'


// ============================================================
// PERIOD TABS
// ============================================================

const PERIOD_TABS = [
  'This Week',
  'This Month',
  'Last Month',
  'Quarter'
]


// ============================================================
// PERIOD API MAP
// ============================================================
//
// IMPORTANT:
// Last Month MUST be lastMonth.
// ============================================================

const PERIOD_API_MAP = {

  'This Week':
    'week',

  'This Month':
    'month',

  'Last Month':
    'lastMonth',

  'Quarter':
    'quarter',

}


// ============================================================
// API
// ============================================================

const API_BASE_URL =
  '/api/v1'


async function fetchPerformanceData(
  period
) {

  const apiPeriod =
    PERIOD_API_MAP[period] ||
    'month'


  const url =
    `${API_BASE_URL}/performancechats?period=${apiPeriod}`


  console.log(
    '[PerformanceCharts] Fetching:',
    url
  )


  const response =
    await fetch(
      url,
      {
        method: 'GET',

        headers: {
          Accept:
            'application/json'
        }
      }
    )


  console.log(
    '[PerformanceCharts] HTTP:',
    response.status
  )


  // ==========================================================
  // HANDLE HTTP ERROR
  // ==========================================================

  if (!response.ok) {

    const text =
      await response.text()


    console.error(
      '[PerformanceCharts] Response:',
      text
    )


    throw new Error(
      `Performance API failed: ${response.status}`
    )

  }


  // ==========================================================
  // PARSE JSON
  // ==========================================================

  let result


  try {

    result =
      await response.json()

  }
  catch (jsonError) {

    const text =
      await response.text()

    console.error(
      '[PerformanceCharts] Invalid JSON:',
      text
    )

    throw new Error(
      'Performance API returned invalid JSON'
    )

  }


  console.log(
    '[PerformanceCharts] Result:',
    result
  )


  // ==========================================================
  // API SUCCESS
  // ==========================================================

  if (!result.success) {

    throw new Error(
      result.error ||
      'Failed to load performance data'
    )

  }


  return result

}


// ============================================================
// NUMBER HELPER
// ============================================================

function toNumber(value) {

  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {

    return 0

  }


  const number =
    Number(value)


  return Number.isFinite(
    number
  )
    ? number
    : 0

}


// ============================================================
// TOOLTIP
// ============================================================

function ChartTooltip({
  active,
  payload,
  label
}) {

  const {
    theme
  } = useTheme()


  if (
    !active ||
    !payload ||
    !payload.length
  ) {

    return null

  }


  return (

    <div
      style={{
        background:
          theme.sidebarBg,

        border:
          `1px solid ${theme.cardBorder}`,

        borderRadius:
          '12px',

        color:
          theme.textPrimary,

        fontSize:
          '13px',

        padding:
          '10px 14px',
      }}
    >

      <div
        style={{
          fontWeight: 700,

          marginBottom:
            '6px',

          color:
            theme.textSecondary,
        }}
      >
        {label}
      </div>


      {payload.map(
        (p, i) => (

          <div
            key={i}
            style={{
              display:
                'flex',

              alignItems:
                'center',

              gap:
                '6px',

              marginBottom:
                '2px',
            }}
          >

            <div
              style={{
                width:
                  '8px',

                height:
                  '8px',

                borderRadius:
                  '50%',

                background:
                  p.color,
              }}
            />


            <span
              style={{
                color:
                  theme.textPrimary,

                fontWeight:
                  600,
              }}
            >

              {p.name}:{' '}

              {
                typeof p.value ===
                'number'
                  ? p.value.toFixed(2)
                  : p.value
              }

            </span>

          </div>

        )
      )}

    </div>

  )

}


// ============================================================
// AREA CHART CARD
// ============================================================

function AreaChartCard({
  cfg,
  theme,
  data
}) {

  const glassCard = {

    background:
      theme.cardBg,

    backdropFilter:
      'blur(20px)',

    WebkitBackdropFilter:
      'blur(20px)',

    border:
      `1px solid ${theme.cardBorder}`,

    borderRadius:
      '16px',

  }


  return (

    <div
      style={{
        ...glassCard,

        padding:
          '0',

        overflow:
          'hidden',
      }}
    >

      {/* HEADER */}

      <div
        style={{
          padding:
            '20px 24px 16px',

          display:
            'flex',

          alignItems:
            'center',

          justifyContent:
            'space-between',

          borderBottom:
            `1px solid ${theme.cardBorder}`,
        }}
      >

        <div
          style={{
            fontSize:
              '14px',

            fontWeight:
              700,

            color:
              theme.textPrimary,
          }}
        >
          {cfg.title}
        </div>


        <div
          style={{
            display:
              'flex',

            alignItems:
              'center',

            gap:
              '6px',

            padding:
              '4px 12px',

            background:
              `${cfg.color}1a`,

            border:
              `1px solid ${cfg.color}40`,

            borderRadius:
              '20px',
          }}
        >

          <span
            style={{
              fontSize:
                '12px',

              fontWeight:
                700,

              color:
                cfg.color,
            }}
          >

            {cfg.currentVal}
            {cfg.unit}

          </span>


          <span
            style={{
              fontSize:
                '10px',

              color:
                theme.textMuted,
            }}
          >
            current
          </span>

        </div>

      </div>


      {/* CHART */}

      <div
        style={{
          padding:
            '16px 8px 16px 0',
        }}
      >

        <ResponsiveContainer
          width="100%"
          height={260}
        >

          <AreaChart
            data={data}
            margin={{
              top: 5,
              right: 16,
              left: -16,
              bottom: 0,
            }}
          >

            <defs>

              <linearGradient
                id={cfg.gradientId}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >

                <stop
                  offset="5%"
                  stopColor={cfg.color}
                  stopOpacity={0.35}
                />

                <stop
                  offset="95%"
                  stopColor={cfg.color}
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
                fill:
                  theme.textMuted,

                fontSize:
                  11,
              }}
              axisLine={false}
              tickLine={false}
            />


            <YAxis
              tick={{
                fill:
                  theme.textMuted,

                fontSize:
                  11,
              }}
              axisLine={false}
              tickLine={false}
            />


            <Tooltip
              content={
                <ChartTooltip />
              }
            />


            <Area
              type="monotone"
              dataKey={cfg.key}
              name={cfg.name}
              stroke={cfg.color}
              strokeWidth={2.5}
              fill={
                `url(#${cfg.gradientId})`
              }
              dot={{
                fill:
                  cfg.color,

                r:
                  4,

                strokeWidth:
                  0,
              }}
              activeDot={{
                r:
                  6,

                fill:
                  cfg.color,
              }}
            />

          </AreaChart>

        </ResponsiveContainer>

      </div>

    </div>

  )

}


// ============================================================
// INCIDENT BAR CHART
// ============================================================

function IncidentsBarCard({
  theme,
  data
}) {

  const glassCard = {

    background:
      theme.cardBg,

    backdropFilter:
      'blur(20px)',

    WebkitBackdropFilter:
      'blur(20px)',

    border:
      `1px solid ${theme.cardBorder}`,

    borderRadius:
      '16px',

  }


  return (

    <div
      style={{
        ...glassCard,

        padding:
          '0',

        overflow:
          'hidden',
      }}
    >

      {/* HEADER */}

      <div
        style={{
          padding:
            '20px 24px 16px',

          display:
            'flex',

          alignItems:
            'center',

          justifyContent:
            'space-between',

          borderBottom:
            `1px solid ${theme.cardBorder}`,
        }}
      >

        <div
          style={{
            fontSize:
              '14px',

            fontWeight:
              700,

            color:
              theme.textPrimary,
          }}
        >
          Incidents Over Time
        </div>


        <div
          style={{
            display:
              'flex',

            alignItems:
              'center',

            gap:
              '4px',
          }}
        >

          <div
            style={{
              width:
                '8px',

              height:
                '8px',

              borderRadius:
                '2px',

              background:
                theme.danger,
            }}
          />


          <span
            style={{
              fontSize:
                '11px',

              color:
                theme.textMuted,
            }}
          >
            Incidents
          </span>

        </div>

      </div>


      {/* CHART */}

      <div
        style={{
          padding:
            '16px 8px 16px 0',
        }}
      >

        <ResponsiveContainer
          width="100%"
          height={260}
        >

          <BarChart
            data={data}
            margin={{
              top: 5,
              right: 16,
              left: -16,
              bottom: 0,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              stroke={theme.chartGrid}
            />


            <XAxis
              dataKey="date"
              tick={{
                fill:
                  theme.textMuted,

                fontSize:
                  11,
              }}
              axisLine={false}
              tickLine={false}
            />


            <YAxis
              tick={{
                fill:
                  theme.textMuted,

                fontSize:
                  11,
              }}
              axisLine={false}
              tickLine={false}
            />


            <Tooltip
              content={
                <ChartTooltip />
              }
            />


            <Bar
              dataKey="incidents"
              name="Incidents"
              fill={theme.danger}
              radius={[
                4,
                4,
                0,
                0
              ]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  )

}


// ============================================================
// MAIN PAGE
// ============================================================

export default function PerformanceChartsPage() {

  const {
    theme
  } = useTheme()


  // ==========================================================
  // ACTIVE PERIOD
  // ==========================================================

  const [
    activePeriod,
    setActivePeriod
  ] = useState(
    'This Month'
  )


  // ==========================================================
  // DATA
  // ==========================================================

  const [
    performanceData,
    setPerformanceData
  ] = useState([])


  // ==========================================================
  // LOADING
  // ==========================================================

  const [
    loading,
    setLoading
  ] = useState(true)


  // ==========================================================
  // ERROR
  // ==========================================================

  const [
    error,
    setError
  ] = useState(null)


  // ==========================================================
  // LOAD DATA
  // ==========================================================

  useEffect(() => {

    let cancelled = false


    async function loadPerformance() {

      try {

        setLoading(true)

        setError(null)


        const result =
          await fetchPerformanceData(
            activePeriod
          )


        if (cancelled) {
          return
        }


        // ====================================================
        // BACKEND ALREADY RETURNS:
        //
        // data: [
        //   {
        //     date,
        //     mttr,
        //     sla,
        //     fcr,
        //     incidents
        //   }
        // ]
        // ====================================================

        const chartData =
          Array.isArray(
            result.data
          )
            ? result.data.map(
                row => ({
                  date:
                    row.date || '',

                  mttr:
                    toNumber(
                      row.mttr
                    ),

                  sla:
                    toNumber(
                      row.sla
                    ),

                  fcr:
                    toNumber(
                      row.fcr
                    ),

                  incidents:
                    toNumber(
                      row.incidents
                    ),

                  periodStart:
                    row.periodStart ||
                    '',

                  periodEnd:
                    row.periodEnd ||
                    '',

                })
              )
            : []


        console.log(
          '[PerformanceCharts] Chart data:',
          chartData
        )


        setPerformanceData(
          chartData
        )

      }
      catch (err) {

        if (!cancelled) {

          console.error(
            '[PerformanceCharts] Error:',
            err
          )


          setError(
            err.message ||
            'Failed to load performance data'
          )

        }

      }
      finally {

        if (!cancelled) {

          setLoading(false)

        }

      }

    }


    loadPerformance()


    return () => {

      cancelled = true

    }

  }, [activePeriod])


  // ==========================================================
  // CURRENT VALUES
  // ==========================================================

  const currentData =
    performanceData.length > 0
      ? performanceData[
          performanceData.length - 1
        ]
      : null


  const currentMTTR =
    currentData?.mttr || 0


  const currentSLA =
    currentData?.sla || 0


  const currentFCR =
    currentData?.fcr || 0


  // ==========================================================
  // CHART CONFIG
  // ==========================================================

  const CHART_CONFIGS = [

    {

      key:
        'mttr',

      title:
        'MTTR Trend',

      name:
        'MTTR (hrs)',

      color:
        theme.accentSecondary,

      gradientId:
        'mttrGrad',

      currentVal:
        Number(
          currentMTTR
        ).toFixed(2),

      unit:
        ' hrs',

    },


    {

      key:
        'sla',

      title:
        'SLA Compliance %',

      name:
        'SLA %',

      color:
        theme.accent,

      gradientId:
        'slaGrad2',

      currentVal:
        Number(
          currentSLA
        ).toFixed(2),

      unit:
        '%',

    },


    {

      key:
        'fcr',

      title:
        'FCR % Trend',

      name:
        'FCR %',

      color:
        theme.success,

      gradientId:
        'fcrGrad2',

      currentVal:
        Number(
          currentFCR
        ).toFixed(2),

      unit:
        '%',

    },

  ]


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div
      style={{
        display:
          'flex',

        flexDirection:
          'column',

        gap:
          '24px',
      }}
    >

      {/* ====================================================
          HEADER
          ==================================================== */}

      <div
        style={{
          display:
            'flex',

          alignItems:
            'center',

          justifyContent:
            'space-between',

          flexWrap:
            'wrap',

          gap:
            '12px',
        }}
      >

        <div>

          <h1
            style={{
              fontSize:
                '26px',

              fontWeight:
                800,

              color:
                theme.textPrimary,

              marginBottom:
                '4px',
            }}
          >

            Performance{' '}

            <span
              style={{
                color:
                  theme.accent,
              }}
            >
              Charts
            </span>

          </h1>


          <div
            style={{
              fontSize:
                '13px',

              color:
                theme.textMuted,
            }}
          >
            Detailed metrics visualization
          </div>

        </div>


        {/* ==================================================
            PERIOD BUTTONS
            ================================================== */}

        <div
          style={{
            display:
              'flex',

            gap:
              '6px',

            background:
              theme.cardBg,

            border:
              `1px solid ${theme.cardBorder}`,

            borderRadius:
              '14px',

            padding:
              '5px',
          }}
        >

          {PERIOD_TABS.map(
            tab => (

              <button
                key={tab}
                onClick={() =>
                  setActivePeriod(
                    tab
                  )
                }
                style={{
                  padding:
                    '7px 16px',

                  borderRadius:
                    '10px',

                  fontSize:
                    '12px',

                  fontWeight:
                    700,

                  border:
                    'none',

                  cursor:
                    'pointer',

                  transition:
                    'all 0.25s',

                  background:
                    activePeriod === tab
                      ? theme.accentGrad
                      : 'transparent',

                  color:
                    activePeriod === tab
                      ? '#fff'
                      : theme.textMuted,

                  boxShadow:
                    activePeriod === tab
                      ? `0 4px 14px ${theme.accent}40`
                      : 'none',
                }}
              >
                {tab}
              </button>

            )
          )}

        </div>

      </div>


      {/* ====================================================
          LOADING
          ==================================================== */}

      {loading && (

        <div
          style={{
            padding:
              '40px',

            textAlign:
              'center',

            color:
              theme.textMuted,
          }}
        >
          Loading performance data...
        </div>

      )}


      {/* ====================================================
          ERROR
          ==================================================== */}

      {!loading && error && (

        <div
          style={{
            padding:
              '30px',

            textAlign:
              'center',

            color:
              theme.danger,

            background:
              theme.cardBg,

            border:
              `1px solid ${theme.cardBorder}`,

            borderRadius:
              '16px',
          }}
        >

          {error}

        </div>

      )}


      {/* ====================================================
          NO DATA
          ==================================================== */}

      {!loading &&
       !error &&
       performanceData.length === 0 && (

        <div
          style={{
            padding:
              '40px',

            textAlign:
              'center',

            color:
              theme.textMuted,

            background:
              theme.cardBg,

            border:
              `1px solid ${theme.cardBorder}`,

            borderRadius:
              '16px',
          }}
        >

          No performance data found for{' '}

          <strong>
            {activePeriod}
          </strong>

        </div>

      )}


      {/* ====================================================
          CHART GRID
          ==================================================== */}

      {!loading &&
       !error &&
       performanceData.length > 0 && (

        <div
          style={{
            display:
              'grid',

            gridTemplateColumns:
              '1fr 1fr',

            gap:
              '20px',
          }}
        >

          {CHART_CONFIGS.map(
            cfg => (

              <AreaChartCard
                key={cfg.key}
                cfg={cfg}
                theme={theme}
                data={performanceData}
              />

            )
          )}


          <IncidentsBarCard
            theme={theme}
            data={performanceData}
          />

        </div>

      )}

    </div>

  )

}
