import React, { createContext, useContext, useState } from 'react'



const AuthContext = createContext(null)



export function AuthProvider({ children }) {

  const [user, setUser] = useState(() => {

    try {

      const stored = localStorage.getItem('gd_user')

      return stored ? JSON.parse(stored) : null

    } catch {

      return null

    }

  })



  /** Called after a successful login — accepts user object and optional JWT token */

  function login(userData, token = null) {

    setUser(userData)

    localStorage.setItem('gd_user', JSON.stringify(userData))

    if (token) {

      localStorage.setItem('gd-token', token)

    }

  }



  function logout() {

    setUser(null)

    localStorage.removeItem('gd_user')

    localStorage.removeItem('gd-token')

  }



  return (

    <AuthContext.Provider value={{ user, login, logout }}>

      {children}

    </AuthContext.Provider>

  )

}



export function useAuth() {

  return useContext(AuthContext)

}

