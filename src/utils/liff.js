import liff from '@line/liff'

export const initializeLiff = async () => {
  try {
    console.log('Starting LIFF initialization...')
    
    // 检查 LIFF 是否可用
    if (!liff) {
      throw new Error('LIFF SDK not loaded')
    }
    
    // 基础LIFF初始化
    await liff.init({
      liffId: '2006853614-o8b5wmgq',
      withLoginOnExternalBrowser: true
    }).catch(err => {
      console.error('LIFF initialization error:', err)
      throw new Error(`LIFF initialization failed: ${err.message}`)
    })
    
    console.log('LIFF initialized successfully')
    console.log('LIFF isInClient:', liff.isInClient())
    console.log('LIFF isLoggedIn:', liff.isLoggedIn())
    
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search)
    const customerId = urlParams.get('customer_id')
    console.log('Customer ID from URL:', customerId)
    
    // 如果未登录，进行登录
    if (!liff.isLoggedIn()) {
      console.log('User not logged in, starting login process...')
      const redirectUri = window.location.href
      console.log('Login redirect URI:', redirectUri)
      liff.login({
        redirectUri: redirectUri
      })
      return
    }
    
    // 如果已登录且有customer_id，获取用户信息并进行绑定
    if (customerId) {
      try {
        console.log('Getting user profile...')
        const profile = await liff.getProfile()
        console.log('Got user profile:', profile)
        
        // 调用绑定API
        const response = await fetch('https://a789-111-249-212-122.ngrok-free.app/api/line/bind', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          mode: 'cors',
          body: JSON.stringify({
            customer_id: customerId,
            line_user_id: profile.userId
          })
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          console.error('Binding API error:', errorText)
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
        }
        
        const result = await response.json()
        console.log('Binding result:', result)
        
        if (result.status === 'success') {
          alert('帳號綁定成功！請點擊確定後加入官方帳號。')
          // 绑定成功后，引导用户加入 LINE Bot 好友
          const botBasicId = '@936quota' // 从环境变量获取的 LINE Bot Basic ID
          const addFriendLink = `https://line.me/R/ti/p/${botBasicId}`
          
          if (liff.isInClient()) {
            // 在 LINE APP 内，直接打开加好友页面
            liff.openWindow({
              url: addFriendLink,
              external: false
            })
            liff.closeWindow()
          } else {
            // 在外部浏览器，打开新窗口
            window.open(addFriendLink, '_blank')
          }
        } else {
          throw new Error(result.message || '綁定失敗')
        }
      } catch (error) {
        console.error('Binding error:', error)
        alert('綁定失敗：' + (error.message || '未知錯誤'))
        if (liff.isInClient()) {
          liff.closeWindow()
        }
      }
    } else {
      console.error('No customer_id provided')
      alert('缺少必要參數')
      if (liff.isInClient()) {
        liff.closeWindow()
      }
    }
    
  } catch (error) {
    console.error('LIFF initialization error:', error)
    alert('LINE 初始化失敗：' + (error.message || '未知錯誤'))
  }
}

export const getLiffProfile = async () => {
  try {
    if (!liff.isLoggedIn()) {
      console.log('User not logged in')
      return null
    }
    
    const profile = await liff.getProfile()
    console.log('Got user profile:', profile)
    return profile
  } catch (error) {
    console.error('Error getting profile:', error)
    throw error
  }
} 