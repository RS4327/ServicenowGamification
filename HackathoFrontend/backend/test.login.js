require('dotenv').config()
const { initPool, queryRaw, queryJsonOne } = require('./db')

async function test() {
  await initPool()
  console.log('Testing login SQL against Oracle...\n')

  try {
    // Test 1: basic connectivity
    const ping = await queryRaw('SELECT 1 AS TEST FROM DUAL')
    console.log('✅ DB ping OK:', ping)
  } catch (e) {
    console.error('❌ DB ping failed:', e.message)
    process.exit(1)
  }

  try {
    // Test 2: check if LOGIN_USER table exists
    const tbl = await queryRaw(
      "SELECT TABLE_NAME FROM USER_TABLES WHERE TABLE_NAME = 'LOGIN_USER'"
    )
    console.log('LOGIN_USER table exists:', tbl.length > 0 ? 'YES' : 'NO — check table name')
  } catch (e) {
    console.error('❌ Table check failed:', e.message)
  }

  try {
    // Test 3: describe LOGIN_USER columns
    const cols = await queryRaw(
      "SELECT COLUMN_NAME, DATA_TYPE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = 'LOGIN_USER' ORDER BY COLUMN_ID"
    )
    console.log('\nLOGIN_USER columns:')
    cols.forEach(c => console.log(' -', c.COLUMN_NAME, ':', c.DATA_TYPE))
  } catch (e) {
    console.error('❌ Column check failed:', e.message)
  }

  try {
    // Test 4: count rows in LOGIN_USER
    const cnt = await queryRaw('SELECT COUNT(*) AS CNT FROM LOGIN_USER')
    console.log('\nTotal rows in LOGIN_USER:', cnt[0]?.CNT)
  } catch (e) {
    console.error('❌ Row count failed:', e.message)
  }

  process.exit(0)
}

test().catch(e => { console.error('Fatal:', e.message); process.exit(1) })
