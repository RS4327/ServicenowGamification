const express = require('express')
const router = express.Router()
const { queryJsonArray } = require('../db')

// GET /api/v1/alerts?limit=3
// Oracle object:
// SERVICENOWGAMIFICATION.MANAGER_RECENT_ALERT_09

router.get('/', async (req, res) => {
  const limit = Math.max(1, parseInt(req.query.limit, 10) || 3)

  try {
    const data = await queryJsonArray(
      `
      SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
          'id' VALUE ROWNUM,
          'title' VALUE ALERT_TITLE,
          'desc' VALUE ALERT_MESSAGE,
          'time' VALUE
            CASE
              WHEN TRUNC(INCIDENT_DATE) = TRUNC(CURRENT_DATE)
                THEN 'Today'

              WHEN TRUNC(INCIDENT_DATE) = TRUNC(CURRENT_DATE) - 1
                THEN '1 day ago'

              WHEN TRUNC(INCIDENT_DATE) >= TRUNC(CURRENT_DATE) - 7
                THEN TO_CHAR(
                  TRUNC(CURRENT_DATE) - TRUNC(INCIDENT_DATE)
                ) || ' days ago'

              ELSE TO_CHAR(INCIDENT_DATE, 'DD-MON-YYYY')
            END,

          'level' VALUE
            CASE
              WHEN ALERT_TYPE = 'HIGH'
                THEN 'critical'

              WHEN ALERT_TYPE = 'WARNING'
                THEN 'warning'

              WHEN ALERT_TYPE = 'MEDIUM'
                THEN 'info'

              ELSE 'info'
            END
        )
      ) AS RESPONSE_DATA

      FROM (
        SELECT
          ALERT_TITLE,
          ALERT_MESSAGE,
          INCIDENT_DATE,
          ALERT_TYPE
        FROM SERVICENOWGAMIFICATION.MANAGER_RECENT_ALERT_09
        WHERE ROWNUM <= :limit
      )
      `,
      { limit }
    )

    console.log('[alerts] Oracle data:', data)

    return res.json({
      success: true,
      data: data || []
    })

  } catch (err) {
    console.error('[alerts] Oracle error:', err)
    console.error('[alerts] Error message:', err.message)

    return res.status(500).json({
      success: false,
      error: err.message
    })
  }
})

module.exports = router
