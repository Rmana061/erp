<!-- LINE 帳號綁定頁面 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <div class="main-content">
      <div class="header">
        <span>LINE帳號綁定</span>
      </div>
      
      <div class="content-wrapper">
        <h2>LINE綁定</h2>
        <div v-if="loading" class="loading-indicator">載入中...</div>
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
          <button @click="closeWindow" class="close-button">關閉視窗</button>
        </div>
        <div v-else class="success-message">
          <p>LINE帳號綁定成功！</p>
          <p>您現在可以通過LINE接收訂單通知。</p>
          <button @click="closeWindow" class="close-button">關閉視窗</button>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import { initializeLiff } from '../utils/liff'
import liff from '@line/liff'

export default {
  name: 'LineBinding',
  data() {
    return {
      loading: true,
      error: null
    }
  },
  async mounted() {
    try {
      await initializeLiff()
      this.loading = false
    } catch (error) {
      console.error('LINE binding error:', error)
      if (error.message === '此LINE帳號已被其他客戶綁定') {
        this.error = '此LINE帳號已被其他客戶綁定'
      } else if (error.message.includes('綁定失敗')) {
        this.error = '此LINE帳號已被其他公司綁定，請使用其他LINE帳號'
      } else {
        this.error = '綁定過程發生錯誤，請稍後再試'
      }
      this.loading = false
    }
  },
  methods: {
    closeWindow() {
      if (liff && liff.isInClient()) {
        liff.closeWindow()
      } else {
        window.close()
      }
    }
  }
}
</script>

<style scoped>
.line-binding {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  text-align: center;
}

.loading-message {
  font-size: 18px;
  color: #333;
}

.error-message {
  color: #ff4444;
  font-size: 16px;
  margin: 20px;
  text-align: center;
  padding: 20px;
  background-color: #fff0f0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message p {
  margin-bottom: 15px;
}

.error-message .close-button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #ff4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error-message .close-button:hover {
  background-color: #ff3333;
}

.success-message {
  color: #007700;
  font-size: 16px;
  margin-top: 20px;
  text-align: center;
}

.close-button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #06c755;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-button:hover {
  background-color: #059b43;
}

.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f5f5f5;
  margin-bottom: 20px;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style> 