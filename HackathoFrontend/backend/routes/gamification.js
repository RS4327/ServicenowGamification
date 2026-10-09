const express = require('express')

const router = express.Router()

const {
  queryRaw,
  queryJsonOne,
  queryJsonArray,
} = require('../db')

/*
|--------------------------------------------------------------------------
| GET /api/v1/gamification/summary
|--------------------------------------------------------------------------
| Oracle object:
| MANAGER_GAMIFICATION_SUMMARY_10
*/
router.get('/summary', async (_req, res) => {
  const objectName = 'MANAGER_GAMIFICATION_SUMMARY_10'

  try {
    console.log(`[DB] Reading object: ${objectName}`)

    // First test the object itself.
    const rows = await queryRaw(`
      SELECT
        TOTAL_AGENTS,
        TOTAL_POINTS,
        BADGES_AWARDED,
        ACTIVE_CHALLENGES
      FROM ${objectName}
    `)

    console.log(`[DB] ${objectName} rows:`, rows.length)

    const row = rows[0]

    if (!row) {
      return res.json({
        success: true,
        data: {
          totalAgents: 0,
          totalPoints: 0,
          badgesAwarded: 0,
          activeChallenges: 0,
        },
      })
    }

    const data = {
      totalAgents: row.TOTAL_AGENTS,
      totalPoints: row.TOTAL_POINTS,
      badgesAwarded: row.BADGES_AWARDED,
      activeChallenges: row.ACTIVE_CHALLENGES,
    }

    return res.json({
      success: true,
      data,
    })

  } catch (err) {
    console.error(`❌ [DB ERROR] Object: ${objectName}`)
    console.error(err)

    return res.status(500).json({
      success: false,
      error: err.message,
      object: objectName,
    })
  }
})

/*
|--------------------------------------------------------------------------
| GET /api/v1/badges/top?limit=3
|--------------------------------------------------------------------------
| Oracle object:
| MANGER_TOP_BADGES_EARDNED_11
*/
router.get('/top', async (req, res) => {
  const objectName = 'MANGER_TOP_BADGES_EARDNED_11'

  const limit = Math.max(
    1,
    Math.min(100, parseInt(req.query.limit, 10) || 3)
  )

  try {
    console.log(`[BADGES] Querying Oracle object: ${objectName}`)
    console.log(`[BADGES] Limit: ${limit}`)

    const rows = await queryRaw(
      `
      SELECT
        ID,
        NAME,
        DESCRIPTION,
        COLOR,
        ICON
      FROM MANGER_TOP_BADGES_EARDNED_11
      WHERE ROWNUM <= :limit
      `,
      { limit }
    )

    console.log(`[BADGES] Oracle returned ${rows.length} rows`)
    console.log('[BADGES] Rows:', rows)

    const data = rows.map(row => ({
      id: row.ID,
      name: row.NAME,
      desc: row.DESCRIPTION,
      color: row.COLOR,
      icon: row.ICON,
    }))

    return res.json({
      success: true,
      data,
      source: 'oracle',
      object: objectName,
    })

  } catch (err) {
    console.error(`[BADGES] ❌ Oracle error on ${objectName}`)
    console.error(err)

    return res.status(500).json({
      success: false,
      error: err.message,
      source: 'oracle',
      object: objectName,
    })
  }
})

/*
|--------------------------------------------------------------------------
| GET /api/v1/performance/distribution
|--------------------------------------------------------------------------
| Oracle object:
| SERVICENOWGAMIFICATION.MANAGER_PERFORMANACE_DISTRIBUTION_12
*/
router.get('/distribution', async (_req, res) => {
  const objectName =
    'SERVICENOWGAMIFICATION.MANAGER_PERFORMANACE_DISTRIBUTION_12'

  try {
    console.log(`[DB] Reading object: ${objectName}`)

    const rows = await queryRaw(`
      SELECT
        PERFORMANCE_CATEGORY,
        PERCENTAGE,
        COLOR
      FROM ${objectName}
      ORDER BY
        CASE PERFORMANCE_CATEGORY
          WHEN 'High Performers' THEN 1
          WHEN 'Average Performers' THEN 2
          WHEN 'Low Performers' THEN 3
          ELSE 4
        END
    `)

    console.log(`[DB] ${objectName} rows:`, rows.length)

    const data = rows.map(row => ({
      name: row.PERFORMANCE_CATEGORY,
      value: row.PERCENTAGE,
      color: row.COLOR,
    }))

    return res.json({
      success: true,
      data,
    })

  } catch (err) {
    console.error(`❌ [DB ERROR] Object: ${objectName}`)
    console.error(err)

    return res.status(500).json({
      success: false,
      error: err.message,
      object: objectName,
    })
  }
})

module.exports = router
