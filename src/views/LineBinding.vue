<!-- LINE 帳號綁定頁面 -->
<template>
  <div class="line-binding">
    <div class="loading-message" v-if="loading">
      正在處理LINE帳號綁定，請稍候...
    </div>
    <div class="error-message" v-if="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { initializeLiff } from '../utils/liff'

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
      this.error = error.message || '綁定過程發生錯誤'
      this.loading = false
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
  margin-top: 10px;
}
</style> 