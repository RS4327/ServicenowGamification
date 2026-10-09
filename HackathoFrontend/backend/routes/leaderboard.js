const express = require('express')
const router = express.Router()

const { queryJsonRows } = require('../db')


// ============================================================
// GET /api/v1/leaderboard
//
// Examples:
//
// /api/v1/leaderboard?metric=points&period=week
// /api/v1/leaderboard?metric=points&period=month
// /api/v1/leaderboard?metric=points&period=quarter
//
// /api/v1/leaderboard?metric=fcr&period=month
// /api/v1/leaderboard?metric=slaCompliance&period=month
// /api/v1/leaderboard?metric=mttr&period=month
//
// ============================================================

router.get('/', async (req, res) => {
  try {

    // ========================================================
    // REQUEST PARAMETERS
    // ========================================================

    const metric = String(
      req.query.metric || 'points'
    ).trim().toLowerCase()

    const period = String(
      req.query.period || 'month'
    ).trim().toLowerCase()


    // ========================================================
    // VALID METRICS
    // ========================================================

    const allowedMetrics = [
      'points',
      'fcr',
      'slacompliance',
      'mttr',
    ]

    const selectedMetric = allowedMetrics.includes(metric)
      ? metric
      : 'points'


    // ========================================================
    // VALID PERIODS
    // ========================================================

    const allowedPeriods = [
      'week',
      'month',
      'quarter',
    ]

    const selectedPeriod = allowedPeriods.includes(period)
      ? period
      : 'month'


    // ========================================================
    // METRIC CONFIGURATION
    // ========================================================

    let orderBy
    let scoreColumn
    let metricLabel

    switch (selectedMetric) {

      // ------------------------------------------------------
      // FCR
      // ------------------------------------------------------

      case 'fcr':

        orderBy = `
          fcr DESC NULLS LAST,
          sla DESC NULLS LAST,
          mttr_hours ASC NULLS LAST,
          points DESC NULLS LAST,
          agent ASC
        `

        scoreColumn = 'fcr'
        metricLabel = 'FCR'

        break


      // ------------------------------------------------------
      // SLA
      // ------------------------------------------------------

      case 'slacompliance':

        orderBy = `
          sla DESC NULLS LAST,
          fcr DESC NULLS LAST,
          mttr_hours ASC NULLS LAST,
          points DESC NULLS LAST,
          agent ASC
        `

        scoreColumn = 'sla'
        metricLabel = 'SLA'

        break


      // ------------------------------------------------------
      // MTTR
      // LOWER IS BETTER
      // ------------------------------------------------------

      case 'mttr':

        orderBy = `
          mttr_hours ASC NULLS LAST,
          fcr DESC NULLS LAST,
          sla DESC NULLS LAST,
          points DESC NULLS LAST,
          agent ASC
        `

        scoreColumn = 'mttr_hours'
        metricLabel = 'MTTR'

        break


      // ------------------------------------------------------
      // POINTS
      // ------------------------------------------------------

      case 'points':

      default:

        orderBy = `
          points DESC NULLS LAST,
          fcr DESC NULLS LAST,
          sla DESC NULLS LAST,
          mttr_hours ASC NULLS LAST,
          agent ASC
        `

        scoreColumn = 'points'
        metricLabel = 'Points'

        break
    }


    // ========================================================
    // PERIOD CONDITION
    //
    // IMPORTANT:
    //
    // AGENT_LEADERBOARD.PERIOD_DATE is used.
    //
    // WEEK    = CURRENT ISO WEEK
    // MONTH   = CURRENT MONTH
    // QUARTER = CURRENT QUARTER
    //
    // ========================================================

    let periodCondition

    switch (selectedPeriod) {

      // ------------------------------------------------------
      // WEEK
      // ------------------------------------------------------

      case 'week':

        periodCondition = `
          period_date >= TRUNC(SYSDATE, 'IW')
          AND period_date < TRUNC(SYSDATE, 'IW') + 7
        `

        break


      // ------------------------------------------------------
      // QUARTER
      // ------------------------------------------------------

      case 'quarter':

        periodCondition = `
          period_date >= TRUNC(SYSDATE, 'Q')
          AND period_date < ADD_MONTHS(
            TRUNC(SYSDATE, 'Q'),
            3
          )
        `

        break


      // ------------------------------------------------------
      // MONTH
      // ------------------------------------------------------

      case 'month':

      default:

        periodCondition = `
          period_date >= TRUNC(SYSDATE, 'MM')
          AND period_date < ADD_MONTHS(
            TRUNC(SYSDATE, 'MM'),
            1
          )
        `

        break
    }


    // ========================================================
    // LEADERBOARD QUERY
    //
    // SOURCE:
    // SERVICENOWGAMIFICATION.AGENT_LEADERBOARD
    //
    // ========================================================

    const data = await queryJsonRows(`

      SELECT

        JSON_OBJECT(

          'rank'
          VALUE rank,

          'name'
          VALUE agent,

          'fcr'
          VALUE fcr,

          'sla'
          VALUE sla,

          'mttr'
          VALUE mttr_hours,

          'points'
          VALUE points,

          'score'
          VALUE ${scoreColumn},

          'metric'
          VALUE '${metricLabel}',

          'period'
          VALUE '${selectedPeriod}',

          'periodDate'
          VALUE TO_CHAR(
            period_date,
            'YYYY-MM-DD'
          )

        ) AS JSON_PAYLOAD


      FROM (

        SELECT

          ROW_NUMBER() OVER (

            ORDER BY ${orderBy}

          ) AS rank,


          agent,


          ROUND(
            NVL(fcr, 0),
            2
          ) AS fcr,


          ROUND(
            NVL(sla, 0),
            2
          ) AS sla,


          ROUND(
            NVL(mttr_hours, 0),
            2
          ) AS mttr_hours,


          ROUND(
            NVL(points, 0),
            2
          ) AS points,


          period_date


        FROM SERVICENOWGAMIFICATION.AGENT_LEADERBOARD


        WHERE

          agent IS NOT NULL

          AND TRIM(
            TO_CHAR(agent)
          ) IS NOT NULL

          AND ${periodCondition}

      )

      ORDER BY rank ASC

    `)


    // ========================================================
    // RESPONSE
    // ========================================================

    res.json({

      success: true,

      metric:
        selectedMetric === 'slacompliance'
          ? 'slaCompliance'
          : selectedMetric,

      metricLabel,

      period: selectedPeriod,

      data: data || [],

    })

  } catch (err) {

    console.error(
      '[leaderboard]',
      err
    )

    res.status(500).json({

      success: false,

      error: err.message,

      data: [],

    })
  }
})


module.exports = router