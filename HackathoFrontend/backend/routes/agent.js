const express = require('express')
const router = express.Router()

const {
  queryJsonOne,
  queryJsonRows,
  queryJsonArray
} = require('../db')

/*
===========================================================
1. AGENT STATS
GET /api/v1/dashboard/agent/stats

Oracle object:
LIVE_STREAK_AGENT_LEVEL
===========================================================
*/
router.get('/stats', async (_req, res) => {
  try {
    const data = await queryJsonOne(`
      SELECT JSON_OBJECT(
        'myIncidents' VALUE CURRENT_TOTAL_INCIDENTS,
        'slaCompliance' VALUE CURRENT_SLA_COMPLIANCE,
        'fcr' VALUE CURRENT_FCR,
        'mttr' VALUE CURRENT_MTTR_HOURS
      ) AS JSON_PAYLOAD
      FROM LIVE_STREAK_AGENT_LEVEL
    `)

    console.log('[agent/stats] Oracle data:', data)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error('[agent/stats] Oracle error:', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


/*
===========================================================
2. AGENT PERFORMANCE TREND
GET /api/v1/dashboard/agent/performance-trend

Oracle object:
MANAGER_FCR_SLA_TREND_OVERALL_05

If you have a separate agent-specific view, replace the
object name below.
===========================================================
*/
router.get('/performance-trend', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'date' VALUE TO_CHAR(WEEK_START, 'Mon dd'),
        'fcr' VALUE FCR_PERCENTAGE
      ) AS JSON_PAYLOAD
      FROM MANAGER_FCR_SLA_TREND_OVERALL_05
      ORDER BY WEEK_START
    `)

    console.log('[agent/performance-trend] Oracle rows:', data)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error(
      '[agent/performance-trend] Oracle error:',
      err.message
    )

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


/*
===========================================================
3. AGENT INCIDENTS BY STATE
GET /api/v1/dashboard/agent/incidents-by-state

Oracle object:
MANAGER_INCIDENT_BY_STATE_03

If you have an agent-specific object, use that instead.
===========================================================
*/
router.get('/incidents-by-state', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'name' VALUE INS_STATE,
        'value' VALUE PCT
      ) AS JSON_PAYLOAD
      FROM MANAGER_INCIDENT_BY_STATE_03
    `)

    console.log('[agent/incidents-by-state] Oracle rows:', data)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error(
      '[agent/incidents-by-state] Oracle error:',
      err.message
    )

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


/*
===========================================================
4. RECENT INCIDENTS
GET /api/v1/dashboard/agent/recent-incidents?limit=5

IMPORTANT:
You MUST change the Oracle object and column names below
if your database uses different names.

Example expected columns:
INCIDENT_NUMBER
SHORT_DESCRIPTION
STATE
OPENED_AT
===========================================================
*/
router.get('/recent-incidents', async (req, res) => {
  const limit = Math.max(
    1,
    parseInt(req.query.limit, 10) || 5
  )

  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'id' VALUE INCIDENT_NUMBER,
        'shortDesc' VALUE SHORT_DESCRIPTION,
        'state' VALUE STATE,
        'openedAt' VALUE TO_CHAR(OPENED_AT, 'DD-MON-YYYY HH24:MI')
      ) AS JSON_PAYLOAD
      FROM (
        SELECT
          INCIDENT_NUMBER,
          SHORT_DESCRIPTION,
          STATE,
          OPENED_AT
        FROM SERVICENOWGAMIFICATION.AGENT_RECENT_INCIDENTS
        ORDER BY OPENED_AT DESC
      )
      WHERE ROWNUM <= :limit
    `, {
      limit
    })

    console.log('[agent/recent-incidents] Oracle rows:', data)

    res.json({
      success: true,
      data
    })
  } catch (err) {
    console.error(
      '[agent/recent-incidents] Oracle error:',
      err.message
    )

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


/*
===========================================================
5. AGENT BADGES
GET /api/v1/dashboard/agent/badges

IMPORTANT:
Change this Oracle object if your actual Agent badge object
has a different name.
===========================================================
*/
router.get('/badges', async (_req, res) => {
  try {
    const data = await queryJsonArray(`
      SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
          'id' VALUE ID,
          'name' VALUE NAME,
          'description' VALUE DESCRIPTION,
          'color' VALUE COLOR,
          'icon' VALUE ICON
        )
        ORDER BY ID
      ) AS RESPONSE_DATA
      FROM SERVICENOWGAMIFICATION.AGENT_BADGES
    `)

    console.log('[agent/badges] Oracle data:', data)

    res.json({
      success: true,
      data: data || []
    })
  } catch (err) {
    console.error(
      '[agent/badges] Oracle error:',
      err.message
    )

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})


module.exports = router
