const express = require('express')
const router = express.Router()

const { queryJsonOne, queryJsonRows } = require('../db')

// GET /api/v1/dashboard/manager/stats
router.get('/stats', async (_req, res) => {
  try {
    const data = await queryJsonOne(`
      SELECT JSON_OBJECT(
        'totalIncidents' VALUE CURRENT_TOTAL_INCIDENTS,
        'slaCompliance' VALUE CURRENT_SLA_COMPLIANCE,
        'fcr' VALUE CURRENT_FCR,
        'avgMTTR' VALUE CURRENT_MTTR_HOURS,
        'reopenRate' VALUE CURRENT_REOPEN_RATE,
        'customerRating' VALUE CURRENT_CUSTOMER_RATING,
        'incidentsTrend' VALUE INCIDENTS_PCT_CHANGE,
        'slaTrend' VALUE SLA_COMPLIANCE_PCT_CHANGE,
        'fcrTrend' VALUE FCR_PCT_CHANGE,
        'mttrTrend' VALUE MTTR_PCT_CHANGE,
        'reopenTrend' VALUE REOPEN_RATE_PCT_CHANGE,
        'ratingTrend' VALUE CUSTOMER_RATING_PCT_CHANGE,
        'period' VALUE CURRENT_DATE_RANGE
      ) AS JSON_PAYLOAD
      FROM LIVE_STREAK_OVERALL_LEVEL
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/stats]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/incidents-over-time
router.get('/incidents-over-time', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'date' VALUE TO_CHAR(WK_RANGE, 'Mon dd'),
        'incidents' VALUE INS_COUNT
      ) AS JSON_PAYLOAD
      FROM MANGER_INCIDENTS_OVER_TIME_02
      ORDER BY WK_RANGE
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/incidents-over-time]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/sla-trend
router.get('/sla-trend', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'date' VALUE TO_CHAR(WEEK_START, 'Mon dd'),
        'sla' VALUE SLA_COMPLIANCE,
        'fcr' VALUE FCR_PERCENTAGE
      ) AS JSON_PAYLOAD
      FROM MANAGER_FCR_SLA_TREND_OVERALL_05
      ORDER BY WEEK_START
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/sla-trend]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/incidents-by-state
router.get('/incidents-by-state', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'name' VALUE INS_STATE,
        'value' VALUE PCT
      ) AS JSON_PAYLOAD
      FROM MANAGER_INCIDENT_BY_STATE_03
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/incidents-by-state]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/top-agents?limit=5
router.get('/top-agents', async (req, res) => {
  const limit = Math.max(1, parseInt(req.query.limit, 10) || 5)

  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'name' VALUE AGENT,
        'fcr' VALUE FCR,
        'incidents' VALUE INCIDENTS,
        'trend' VALUE TREND,
        'trendUp' VALUE TREND_UP
      ) AS JSON_PAYLOAD
      FROM (
        SELECT *
        FROM MANAGER_AGENTS_BY_FCR_TRENDS_05
        WHERE ROWNUM <= :limit
      )
    `, {
      limit
    })

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/top-agents]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/mttr-by-priority
router.get('/mttr-by-priority', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'priority' VALUE INS_PRIORITY,
        'hours' VALUE AVG_MTTR_HOURS
      ) AS JSON_PAYLOAD
      FROM MANAGER_AVG_BY_PRIORITY_06
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/mttr-by-priority]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


// GET /api/v1/dashboard/manager/sla-by-priority
router.get('/sla-by-priority', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'priority' VALUE INS_PRIORITY,
        'compliance' VALUE SLA_COMPLIANCE_PERCENTAGE
      ) AS JSON_PAYLOAD
      FROM MANAGER_SLA_BY_PRIORITY_08
    `)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[manager/sla-by-priority]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


module.exports = router
