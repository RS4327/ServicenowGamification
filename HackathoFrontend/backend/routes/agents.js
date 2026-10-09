const express = require('express')
const router = express.Router()

const { queryJsonRows } = require('../db')

// GET /api/v1/agents
router.get('/', async (_req, res) => {
  try {
    const data = await queryJsonRows(`
      SELECT JSON_OBJECT(
        'name'   VALUE name,
        'role'   VALUE role,
        'fcr'    VALUE fcr,
        'sla'    VALUE sla,
        'mttr'   VALUE mttr_hours,
        'points' VALUE points,
        'status' VALUE status
      ) AS JSON_PAYLOAD
      FROM agent_page
      ORDER BY points DESC
    `)

    res.json({
      success: true,
      data: data || []
    })
  } catch (err) {
    console.error('[agents]', err.message)

    res.status(500).json({
      success: false,
      error: err.message
    })
  }
})

module.exports = router
