const express = require('express')
const router = express.Router()

const {
  queryJsonOne,
} = require('../db')

// ============================================================
// GET AI INSIGHTS
// GET /api/v1/aiinsights/:incidentNumber
// ============================================================

router.get('/:incidentNumber', async (req, res) => {

  const incidentNumber = String(
    req.params.incidentNumber || ''
  ).trim()

  console.log(
    '[AI INSIGHTS] Searching:',
    incidentNumber
  )

  // ==========================================================
  // VALIDATE INCIDENT NUMBER
  // ==========================================================

  if (!incidentNumber) {

    return res.status(400).json({
      success: false,
      error: 'Incident number is required.',
      data: null,
    })

  }

  try {

    // ========================================================
    // ORACLE JSON QUERY
    //
    // IMPORTANT:
    // Do NOT use db.getConnection() here.
    //
    // queryJsonOne() -> execute()
    // execute() -> initPool()
    // execute() -> pool.getConnection()
    // execute() -> connection.execute()
    // execute() -> connection.close()
    // ========================================================

    const sql = `

      SELECT

        JSON_OBJECT(

          'incident_number'
          VALUE arh.incident_number,

          'recommendation_id'
          VALUE arh.recommendation_id,

          'recommendation'
          VALUE arh.recommendation,

          'similar_incidents'
          VALUE (

            SELECT JSON_ARRAYAGG(

              JSON_OBJECT(

                'number'
                VALUE asi.similar_incident_number,

                'similarity_score'
                VALUE asi.similarity_score,

                'short_description'
                VALUE asi.short_description,

                'assignment_group'
                VALUE asi.assignment_group,

                'resolution_hours'
                VALUE asi.resolution_hours,

                'sla_status'
                VALUE asi.sla_status

                RETURNING CLOB

              )

              RETURNING CLOB

            )

            FROM AI_SIMILAR_INCIDENTS asi

            WHERE asi.recommendation_id =
                  arh.recommendation_id

          )

          RETURNING CLOB

        ) AS JSON_PAYLOAD

      FROM AI_RECOMMENDATION_HISTORY arh

      WHERE UPPER(
        DBMS_LOB.SUBSTR(
          arh.incident_number,
          4000,
          1
        )
      ) = UPPER(:incidentNumber)

      ORDER BY arh.recommendation_id DESC

      FETCH FIRST 1 ROW ONLY

    `

    console.log(
      '[AI INSIGHTS] Executing Oracle query...'
    )

    // ========================================================
    // queryJsonOne automatically:
    //
    // 1. Gets pool
    // 2. Gets connection
    // 3. Executes SQL
    // 4. Parses JSON
    // 5. Closes connection
    // ========================================================

    const data = await queryJsonOne(
      sql,
      {
        incidentNumber,
      }
    )

    console.log(
      '[AI INSIGHTS] Query result:',
      data
    )

    // ========================================================
    // NO DATA
    // ========================================================

    if (!data) {

      console.log(
        `[AI INSIGHTS] No record found for ${incidentNumber}`
      )

      return res.status(404).json({

        success: false,

        error:
          `No AI insights found for ${incidentNumber}.`,

        data: null,

      })

    }

    // ========================================================
    // NORMALIZE SIMILAR INCIDENTS
    // ========================================================

    if (
      typeof data.similar_incidents === 'string'
    ) {

      try {

        data.similar_incidents =
          JSON.parse(
            data.similar_incidents
          )

      } catch (parseError) {

        console.warn(
          '[AI INSIGHTS] Could not parse similar_incidents:',
          parseError.message
        )

        data.similar_incidents = []

      }

    }

    // ========================================================
    // ALWAYS RETURN ARRAY
    // ========================================================

    if (
      !Array.isArray(
        data.similar_incidents
      )
    ) {

      data.similar_incidents = []

    }

    // ========================================================
    // FINAL RESPONSE
    // ========================================================

    console.log(
      '[AI INSIGHTS] Final data:',
      JSON.stringify(data, null, 2)
    )

    return res.status(200).json({

      success: true,

      data,

    })

  } catch (error) {

    // ========================================================
    // DATABASE ERROR
    // ========================================================

    console.error(
      '[AI INSIGHTS] Database error:',
      error
    )

    return res.status(500).json({

      success: false,

      error:
        error.message ||
        'Failed to retrieve AI insights.',

      data: null,

    })

  }

})

module.exports = router
