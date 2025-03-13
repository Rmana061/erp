<!-- LINE 帳號綁定頁面 -->
<template>
  <body class="customer-mode">
  <div class="container">
    <SideBar menu-type="customer" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName || companyName || '用戶' }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      
      <div class="content-wrapper">
        <h2>LINE綁定</h2>
        <div v-if="loading" class="loading-indicator">載入中...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>
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
import { adminMixin } from '../mixins/adminMixin';
import { companyMixin } from '../mixins/companyMixin';
import { timeMixin } from '../mixins/timeMixin';
import { logoutMixin } from '../mixins/logoutMixin';
import SideBar from '../components/SideBar.vue';

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
  },
  components: {
    SideBar
  },
  mixins: [adminMixin, companyMixin, timeMixin, logoutMixin]
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