import liff from '@line/liff'

export const initializeLiff = async () => {
  try {
    console.log('Initializing LIFF...')
    
    await liff.init({
      liffId: '2006853614-o8B5WmgQ'
    })
    
    console.log('LIFF initialized')
    
    // 如果未登录，进行登录
    if (!liff.isLoggedIn()) {
      console.log('Not logged in, redirecting to login...')
      liff.login()
      return false
    }
    
    return true
    
  } catch (err) {
    console.error('LIFF initialization failed:', err)
    throw new Error('LINE 初始化失敗，請稍後再試')
  }
}

export const getLiffProfile = async () => {
  try {
    // 确保已登录
    if (!liff.isLoggedIn()) {
      console.log('Not logged in')
      return null
    }
    
    // 获取用户资料
    const profile = await liff.getProfile()
    console.log('Got profile:', profile)
    return profile
    
  } catch (err) {
    console.error('Failed to get LIFF profile:', err)
    throw new Error('獲取 LINE 資料失敗，請稍後再試')
  }
} 