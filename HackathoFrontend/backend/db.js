const oracledb = require('oracledb')

oracledb.fetchAsString = [oracledb.CLOB]

let pool = null

async function initPool() {
  if (pool) {
    return pool
  }

  try {
    const host = process.env.DB_HOST || 'localhost'
    const port = process.env.DB_PORT || '1521'
    const service = process.env.DB_SERVICE || 'FREEPDB1'

    const connectString = `${host}:${port}/${service}`

    console.log('[DB] Connecting to Oracle...')
    console.log(`[DB] ${connectString}`)
    console.log(`[DB] User: ${process.env.DB_USER}`)

    pool = await oracledb.createPool({
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      connectString,

      poolMin: 1,
      poolMax: 10,
      poolIncrement: 1,
      poolTimeout: 60,
    })

    console.log(`[DB] ✅ Oracle pool ready → ${connectString}`)

    return pool
  } catch (err) {
    console.error('[DB] ❌ Connection failed')
    console.error('Message:', err.message)
    console.error('Code:', err.code)

    pool = null
    throw err
  }
}

async function closePool() {
  if (pool) {
    try {
      await pool.close(10)
    } catch (err) {
      console.error('[DB] Error closing pool:', err.message)
    }

    pool = null
  }
}

async function execute(sql, binds = {}, opts = {}) {
  const dbPool = await initPool()

  const connection = await dbPool.getConnection()

  try {
    const result = await connection.execute(
      sql,
      binds,
      {
        outFormat: oracledb.OUT_FORMAT_OBJECT,
        fetchArraySize: 100,
        ...opts,
      }
    )

    return result.rows || []
  } finally {
    await connection.close()
  }
}

function parseCol(row) {
  if (!row) {
    return null
  }

  const raw =
    row.JSON_PAYLOAD ??
    row.RESPONSE_DATA ??
    row.USER_DATA

  if (raw === null || raw === undefined) {
    return null
  }

  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw)
    } catch {
      return raw
    }
  }

  return raw
}

async function queryJsonRows(sql, binds = {}) {
  const rows = await execute(sql, binds)

  return rows
    .map(parseCol)
    .filter(value => value !== null && value !== undefined)
}

async function queryJsonArray(sql, binds = {}) {
  const rows = await execute(sql, binds)

  if (!rows.length) {
    return []
  }

  const parsed = parseCol(rows[0])

  return Array.isArray(parsed) ? parsed : []
}

async function queryJsonOne(sql, binds = {}) {
  const rows = await execute(sql, binds)

  if (!rows.length) {
    return null
  }

  return parseCol(rows[0])
}

async function queryRaw(sql, binds = {}) {
  return execute(sql, binds)
}

module.exports = {
  initPool,
  closePool,
  queryJsonRows,
  queryJsonArray,
  queryJsonOne,
  queryRaw,
}
