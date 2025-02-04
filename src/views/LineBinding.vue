<!-- LINE 帳號綁定頁面 -->
<template>
  <div class="line-binding">
    <div class="binding-container">
      <h1>ERP系統</h1>
      <div v-if="loading" class="loading">
        <p>處理中，請稍候...</p>
        <p class="debug-info" v-if="debugInfo">{{ debugInfo }}</p>
      </div>
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <p class="debug-info" v-if="debugInfo">{{ debugInfo }}</p>
        <button @click="retryBinding" class="retry-btn">重試</button>
      </div>
      <div v-else class="success">
        <p>綁定成功！</p>
        <p>您可以關閉此視窗了。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { API_PATHS, getApiUrl } from '../config/api'
import { initializeLiff, getLiffProfile } from '../utils/liff'

export default {
  name: 'LineBinding',
  setup() {
    const loading = ref(true)
    const error = ref('')
    const debugInfo = ref('')

    const bindLineAccount = async (customerId, lineUserId) => {
      try {
        debugInfo.value = `正在綁定帳號... (客戶ID: ${customerId}, LINE ID: ${lineUserId})`
        console.log('Binding account with:', {
          url: getApiUrl(API_PATHS.BIND_LINE),
          data: {
            customer_id: customerId,
            line_user_id: lineUserId
          }
        })
        
        const response = await axios.post(getApiUrl(API_PATHS.BIND_LINE), {
          customer_id: customerId,
          line_user_id: lineUserId
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        console.log('Bind response:', response)

        if (response.data.status === 'success') {
          loading.value = false
          debugInfo.value = '綁定成功'
        } else {
          throw new Error(response.data.message || '綁定失敗')
        }
      } catch (err) {
        console.error('綁定失敗:', err)
        loading.value = false
        error.value = err.message || '綁定失敗，請稍後再試'
        debugInfo.value = `綁定失敗: ${err.message}`
      }
    }

    const processBinding = async () => {
      try {
        debugInfo.value = '開始處理綁定...'
        
        // 初始化 LIFF
        debugInfo.value = '初始化 LINE 登入...'
        const initResult = await initializeLiff()
        if (!initResult) {
          debugInfo.value = '等待 LINE 登入...'
          return
        }
        
        // 获取 URL 参数中的 customer_id
        const urlParams = new URLSearchParams(window.location.search)
        const customerId = urlParams.get('customer_id')
        debugInfo.value = `獲取客戶ID: ${customerId}`

        if (!customerId) {
          throw new Error('缺少客戶ID參數')
        }
        
        // 获取 LINE 用户信息
        debugInfo.value = '獲取 LINE 用戶資料...'
        const profile = await getLiffProfile()
        if (!profile) {
          throw new Error('無法獲取 LINE 用戶資料')
        }
        
        // 绑定账号
        debugInfo.value = '開始綁定帳號...'
        await bindLineAccount(customerId, profile.userId)
        
      } catch (err) {
        console.error('處理綁定失敗:', err)
        loading.value = false
        error.value = err.message || '處理失敗，請稍後再試'
        debugInfo.value = `處理失敗: ${err.message}`
      }
    }

    const retryBinding = async () => {
      loading.value = true
      error.value = ''
      debugInfo.value = '重新嘗試綁定...'
      await processBinding()
    }

    onMounted(() => {
      processBinding()
    })

    return {
      loading,
      error,
      debugInfo,
      retryBinding
    }
  }
}
</script>

<style scoped>
.line-binding {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.binding-container {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

h1 {
  color: #333;
  margin-bottom: 20px;
  font-size: 24px;
}

.loading {
  color: #666;
}

.error {
  color: #ff4444;
  margin: 20px 0;
}

.success {
  color: #4CAF50;
}

.debug-info {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background-color: #45a049;
}
</style> 