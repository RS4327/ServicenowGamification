const express = require('express')

const router = express.Router()

const {
  queryJsonRows
} = require('../db')


// ============================================================
// GET /api/v1/performancechats
//
// Examples:
//
// /api/v1/performancechats?period=week
// /api/v1/performancechats?period=month
// /api/v1/performancechats?period=lastMonth
// /api/v1/performancechats?period=quarter
//
// ============================================================


router.get('/', async (req, res) => {

  try {

    // ========================================================
    // GET PERIOD
    // ========================================================

    const requestedPeriod =
      String(
        req.query.period || 'month'
      )


    // ========================================================
    // ALLOWED PERIODS
    // ========================================================

    const allowedPeriods = [
      'week',
      'month',
      'lastMonth',
      'quarter'
    ]


    const selectedPeriod =
      allowedPeriods.includes(
        requestedPeriod
      )
        ? requestedPeriod
        : 'month'


    console.log(
      '[performancechats] Period:',
      selectedPeriod
    )


    // ========================================================
    // PERIOD CONDITION
    // ========================================================

    let periodCondition


    switch (selectedPeriod) {

      // ------------------------------------------------------
      // THIS WEEK
      // ------------------------------------------------------

      case 'week':

        periodCondition = `
          period_start >= TRUNC(
            SYSDATE,
            'IW'
          )

          AND period_start <= SYSDATE
        `

        break


      // ------------------------------------------------------
      // THIS MONTH
      // ------------------------------------------------------

      case 'month':

        periodCondition = `
          period_start >= TRUNC(
            SYSDATE,
            'MM'
          )

          AND period_start <= SYSDATE
        `

        break


      // ------------------------------------------------------
      // LAST MONTH
      // ------------------------------------------------------

      case 'lastMonth':

        periodCondition = `
          period_start >= ADD_MONTHS(
            TRUNC(
              SYSDATE,
              'MM'
            ),
            -1
          )

          AND period_start < TRUNC(
            SYSDATE,
            'MM'
          )
        `

        break


      // ------------------------------------------------------
      // THIS QUARTER
      // ------------------------------------------------------

      case 'quarter':

        periodCondition = `
          period_start >= TRUNC(
            SYSDATE,
            'Q'
          )

          AND period_start <= SYSDATE
        `

        break


      default:

        periodCondition = `
          period_start >= TRUNC(
            SYSDATE,
            'MM'
          )

          AND period_start <= SYSDATE
        `

    }


    // ========================================================
    // PERFORMANCE DATA
    // ========================================================
    //
    // performance_chats contains:
    //
    // PERIOD_START
    // PERIOD_END
    // MTTR_HOURS
    // SLA_COMPLIANCE
    // FCR_PERCENTAGE
    // TOTAL_INCIDENTS
    //
    // ========================================================

    const performanceData =
      await queryJsonRows(`

        SELECT

          JSON_OBJECT(

            'date'
            VALUE TO_CHAR(
              period_start,
              'Mon-dd'
            ),

            'periodStart'
            VALUE TO_CHAR(
              period_start,
              'YYYY-MM-DD'
            ),

            'periodEnd'
            VALUE TO_CHAR(
              period_end,
              'YYYY-MM-DD'
            ),

            'mttr'
            VALUE ROUND(
              NVL(
                mttr_hours,
                0
              ),
              2
            ),

            'sla'
            VALUE ROUND(
              NVL(
                sla_compliance,
                0
              ),
              2
            ),

            'fcr'
            VALUE ROUND(
              NVL(
                fcr_percentage,
                0
              ),
              2
            ),

            'incidents'
            VALUE NVL(
              total_incidents,
              0
            )

          ) AS JSON_PAYLOAD


        FROM performance_chats


        WHERE ${periodCondition}


        ORDER BY period_start ASC

      `)


    // ========================================================
    // NORMALIZE PERFORMANCE DATA
    // ========================================================

    const data =
      Array.isArray(
        performanceData
      )
        ? performanceData
        : []


    // ========================================================
    // CURRENT DATA
    // ========================================================

    const current =
      data.length > 0
        ? data[data.length - 1]
        : {
            date: '',
            periodStart: '',
            periodEnd: '',
            mttr: 0,
            sla: 0,
            fcr: 0,
            incidents: 0
          }


    // ========================================================
    // RESPONSE
    // ========================================================

    const response = {

      success: true,

      period:
        selectedPeriod,

      current: {

        mttr:
          Number(
            current.mttr || 0
          ),

        sla:
          Number(
            current.sla || 0
          ),

        fcr:
          Number(
            current.fcr || 0
          ),

        incidents:
          Number(
            current.incidents || 0
          )

      },

      data,

      // Kept for compatibility.
      // Your frontend can use data directly.
      incidents: data.map(
        row => ({
          date:
            row.date || '',

          incidents:
            Number(
              row.incidents || 0
            )
        })
      )

    }


    console.log(
      '[performancechats] Rows:',
      data.length
    )


    res.json(response)

  }
  catch (err) {

    console.error(
      '[performancechats] ERROR:',
      err
    )


    res.status(500).json({

      success: false,

      error:
        err.message ||
        'Failed to retrieve performance data'

    })

  }

})


module.exports = router
