import liff from '@line/liff'

// 从环境变量获取配置
const LINE_BOT_BASIC_ID = import.meta.env.VITE_LINE_BOT_BASIC_ID
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const LIFF_ID = import.meta.env.VITE_LIFF_ID

export const initializeLiff = async () => {
  console.log('Initializing LIFF...')
  
  try {
    await liff.init({ liffId: LIFF_ID })
    console.log('LIFF initialized')
    
    if (!liff.isLoggedIn()) {
      console.log('Not logged in, redirecting to LINE login...')
      liff.login()
      return
    }
    
    console.log('Already logged in')
    
    // 解析URL参数
    const urlParams = new URLSearchParams(window.location.search)
    const customerId = urlParams.get('customer_id')
    const bindType = urlParams.get('type') || 'user'  // 默认为用户绑定
    
    if (!customerId) {
      console.error('No customer_id found in URL params')
      throw new Error('缺少客戶ID參數')
    }
    
    console.log(`Customer ID: ${customerId}, Bind Type: ${bindType}`)
    
    // 如果已登录且有customer_id，获取用户信息并进行绑定
    if (customerId) {
      try {
        console.log('Getting user profile...')
        const profile = await liff.getProfile()
        console.log('Got user profile:', profile)
        
        let bindData = {
          customer_id: customerId
        }
        
        // 根据绑定类型设置不同的参数
        if (bindType === 'user') {
          // 个人账号绑定
          bindData.line_user_id = profile.userId
          bindData.user_name = profile.displayName
        } else if (bindType === 'group') {
          // 群组绑定 - 需要获取群组信息
          if (liff.isInGroup()) {
            const context = liff.getContext()
            if (context.type === 'group') {
              bindData.line_group_id = context.groupId
              // 群组名称可能无法获取，后端可能需要额外处理
              bindData.group_name = '群組'
            } else {
              throw new Error('請在LINE群組中使用此功能')
            }
          } else {
            throw new Error('請在LINE群組中使用此功能')
          }
        }
        
        // 调用绑定API
        const response = await fetch(`${API_BASE_URL}/api/line/bind`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          mode: 'cors',
          body: JSON.stringify(bindData)
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
          const addFriendLink = `https://line.me/R/ti/p/${LINE_BOT_BASIC_ID}`
          
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
    }
  } catch (error) {
    console.error('Error initializing LIFF:', error)
    throw error
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