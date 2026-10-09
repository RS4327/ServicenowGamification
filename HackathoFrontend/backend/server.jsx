require('dotenv').config()

const express = require('express')
const cors = require('cors')

const {
  initPool,
  closePool
} = require('./db')

const app = express()


// ============================================================
// MIDDLEWARE
// ============================================================

app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  methods: [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS'
  ],
  allowedHeaders: [
    'Content-Type',
    'Authorization'
  ],
}))

app.use(express.json())


// ============================================================
// REQUEST LOGGER
// ============================================================

app.use((req, _res, next) => {

  console.log(
    `[${new Date().toISOString()}] ${req.method} ${req.path}`
  )

  next()

})


// ============================================================
// HEALTH CHECK
// ============================================================

app.get('/health', (_req, res) => {

  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  })

})


// ============================================================
// API ROUTES
// ============================================================

app.use(
  '/api/v1/auth',
  require('./routes/auth')
)

app.use(
  '/api/v1/dashboard/manager',
  require('./routes/manager')
)

app.use(
  '/api/v1/alerts',
  require('./routes/alerts')
)

app.use(
  '/api/v1/agents',
  require('./routes/agents')
)

app.use(
  '/api/v1/leaderboard',
  require('./routes/leaderboard')
)


// ============================================================
// PERFORMANCE CHARTS
// ============================================================

app.use(
  '/api/v1/performancechats',
  require('./routes/performancechats')
)


// ============================================================
// GAMIFICATION
// ============================================================

const gamification =
  require('./routes/gamification')

app.use(
  '/api/v1/gamification',
  gamification
)

app.use(
  '/api/v1/badges',
  gamification
)

app.use(
  '/api/v1/performance',
  gamification
)

app.use(
  '/api/v1/aiinsights',
  require('./routes/aiinsights')
)


// ============================================================
// 404 HANDLER
// ============================================================

app.use((req, res) => {

  console.log(
    `[404] ${req.method} ${req.originalUrl}`
  )

  res.status(404).json({

    success: false,

    error:
      `Route not found: ${req.originalUrl}`

  })

})


// ============================================================
// GLOBAL ERROR HANDLER
// ============================================================

app.use((
  err,
  _req,
  res,
  _next
) => {

  console.error(
    '[Server Error]',
    err
  )

  res.status(500).json({

    success: false,

    error:
      err.message ||
      'Internal server error'

  })

})


// ============================================================
// SERVER
// ============================================================

const PORT =
  parseInt(process.env.PORT, 10) || 3001


async function start() {

  try {

    await initPool()


    const server =
      app.listen(
        PORT,
        '0.0.0.0',
        () => {

          console.log(
            '\n========================================='
          )

          console.log(
            ' ServiceNow Gamification Dashboard API'
          )

          console.log(
            '========================================='
          )

          console.log(
            ` Local  : http://localhost:${PORT}`
          )

          console.log(
            ` Health : http://localhost:${PORT}/health`
          )

          console.log(
            ` Performance : http://localhost:${PORT}/api/v1/performancechats`
          )

          console.log(
            ` Oracle : ${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_SERVICE}`
          )

          console.log(
            ` User   : ${process.env.DB_USER}`
          )

          console.log(
            '=========================================\n'
          )

        }
      )


    process.on(
      'SIGINT',
      () => shutdown(server)
    )

    process.on(
      'SIGTERM',
      () => shutdown(server)
    )

  }
  catch (err) {

    console.error(
      '[Startup] Failed:',
      err
    )

    process.exit(1)

  }

}


async function shutdown(server) {

  console.log(
    '\n[Server] Shutting down gracefully…'
  )

  server.close(
    async () => {

      await closePool()

      console.log(
        '[Server] Stopped.'
      )

      process.exit(0)

    }
  )

}


start()