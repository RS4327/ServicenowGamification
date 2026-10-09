const express = require('express')
const router = express.Router()
const crypto = require('crypto')
const { queryRaw, queryJsonOne } = require('../db')

// POST /api/v1/auth/login
router.post('/login', async (req, res) => {
  const { username, password, role } = req.body || {}

  if (!username || !password || !role) {
    return res.status(400).json({
      success: false,
      error: 'username, password and role are required',
    })
  }

  const normalizedRole = String(role).trim().toUpperCase()
  const normalizedUsername = String(username).trim()

  try {
    // Step 1: Validate credentials.
    // IMPORTANT: No semicolon at the end of the SQL.
    const validationSql = `
      SELECT
        CASE
          WHEN COUNT(*) > 0 THEN 'VALID'
          ELSE 'INVALID'
        END AS USER_STATUS
      FROM LOGIN_USER
      WHERE USERNAME = :username
        AND PASSWORD = :password
        AND ROLE = :role
        AND IS_ACTIVE = 1
    `

    console.log('[auth/login] Checking user:', normalizedUsername)
    console.log('[auth/login] Role:', normalizedRole)

    const validRows = await queryRaw(
      validationSql,
      {
        username: normalizedUsername,
        password,
        role: normalizedRole,
      }
    )

    const status = validRows[0]?.USER_STATUS

    console.log('[auth/login] USER_STATUS:', status)

    if (status !== 'VALID') {
      return res.status(401).json({
        success: false,
        error: 'Invalid credentials',
      })
    }

    // Step 2: Fetch user profile.
    // IMPORTANT: No semicolon at the end of the SQL.
    const userSql = `
      SELECT JSON_OBJECT(
        'id' VALUE USER_ID,
        'name' VALUE USERNAME,
        'role' VALUE LOWER(ROLE),
        'avatar' VALUE AVATAR
      ) AS USER_DATA
      FROM LOGIN_USER
      WHERE USERNAME = :username
        AND PASSWORD = :password
        AND ROLE = :role
        AND IS_ACTIVE = 1
    `

    const user = await queryJsonOne(
      userSql,
      {
        username: normalizedUsername,
        password,
        role: normalizedRole,
      }
    )

    if (!user) {
      return res.status(401).json({
        success: false,
        error: 'User profile not found',
      })
    }

    const token = crypto
      .randomBytes(32)
      .toString('hex')

    console.log('[auth/login] Login success:', user.name)

    return res.json({
      success: true,
      data: {
        token,
        user,
      },
    })
  } catch (err) {
    console.error(
      '[auth/login] SQL Error:',
      err.message
    )

    console.error(err)

    return res.status(500).json({
      success: false,
      error: err.message,
    })
  }
})

// POST /api/v1/auth/logout
router.post('/logout', (_req, res) => {
  res.json({
    success: true,
    data: {
      message: 'Logged out',
    },
  })
})

module.exports = router
