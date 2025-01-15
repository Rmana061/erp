<!-- 新增產品 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi Sales01</span>
        <span>{{ currentTime }}</span>
      </div>
      
      <h2>{{ isEditing ? '編輯產品' : '新增產品' }}</h2>
      <form @submit.prevent="submitProduct">
        <div class="form-container">
          <div class="form-group">
            <label>產品名稱：</label>
            <div class="input-container">
              <input type="text" placeholder="（管理員自填）" v-model="product.name">
            </div>
          </div>
          <div class="form-group">
            <label>產品描述：</label>
            <div class="input-container">
              <textarea rows="3" placeholder="（管理員自填）" v-model="product.description"></textarea>
            </div>
          </div>
          <div class="form-group">
            <label>產品圖片：</label>
            <div class="input-container">
              <input 
                type="file" 
                accept="image/*" 
                @change="handleImageUpload" 
                ref="imageInput"
              >
              <div v-if="product.image_url" class="preview-container">
                <img 
                  :src="product.image_url" 
                  class="image-preview" 
                  alt="產品圖片預覽"
                >
                <span class="file-name">{{ getFileName(product.image_url) }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>產品DM：</label>
            <div class="input-container">
              <input 
                type="file" 
                accept=".pdf,.doc,.docx" 
                @change="handleDocumentUpload"
                ref="documentInput"
              >
              <div v-if="product.dm_url" class="preview-container">
                <span class="file-name">
                  目前文件: {{ getFileName(product.dm_url) }}
                  <a 
                    v-if="product.dm_url" 
                    :href="getFullUrl(product.dm_url)" 
                    target="_blank" 
                    class="view-file"
                  >
                    查看文件
                  </a>
                </span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>最小下單數量：</label>
            <div class="input-container">
              <input type="number" placeholder="（自填）" v-model.number="product.min_order_qty">
            </div>
          </div>
          <div class="form-group">
            <label>最大下單數量：</label>
            <div class="input-container">
              <input type="number" placeholder="（自填）" v-model.number="product.max_order_qty">
            </div>
          </div>
          <div class="form-group">
            <label>產品單位：</label>
            <div class="input-container">
              <input type="text" placeholder="（例：件、台）" v-model="product.product_unit">
            </div>
          </div>
          <div class="form-group">
            <label>出貨時間：</label>
            <div class="input-container">
              <input 
                type="text" 
                placeholder="（例：3天請輸入3）" 
                v-model="product.shipping_time"
                @input="handleShippingTimeChange"
                :disabled="product.special_date">
            </div>
          </div>
          <div class="form-group">
            <label>特殊日期：</label>
            <div class="input-container checkbox-container">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="product.special_date" 
                  class="custom-checkbox"
                  @change="handleSpecialDateChange">
                <span class="checkmark"></span>
              </label>
            </div>
          </div>
          <div class="button-group">
            <button type="submit" class="action-button">
              {{ isEditing ? '保存修改' : '新增產品' }}
            </button>
            <button type="button" class="action-button cancel" @click="cancel">
              取消
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';

export default {
  name: 'AddProduct',
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      product: {
        name: '',
        description: '',
        image_url: '',
        dm_url: '',
        min_order_qty: '',
        max_order_qty: '',
        product_unit: '',
        shipping_time: '',
        special_date: false
      },
      isEditing: false,
      isMenuOpen: false,
      editingId: null
    };
  },
  created() {
    // 檢查是否是編輯模式
    const mode = this.$route.query.mode;
    const id = this.$route.query.id;
    if (mode === 'edit' && id) {
      this.isEditing = true;
      this.editingId = id;
      this.fetchProductDetails(id);
    }
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
    },
    closeMenu() {
      this.isMenuOpen = false;
      document.body.style.overflow = '';
    },
    updateCurrentTime() {
      const now = new Date();
      const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        weekday: 'long', 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: false 
      };
      this.currentTime = now.toLocaleString('zh-TW', options)
        .replace(/\//g, '/')
        .replace('星期', ' 星期')
        .replace(/(\d+):(\d+)/, '$1:$2');
    },
    async fetchProductDetails(id) {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/products/${id}`, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        // 將獲取的數據填充到表單中
        this.product = {
          name: response.data.name,
          description: response.data.description,
          image_url: response.data.image_url,
          dm_url: response.data.dm_url,
          min_order_qty: response.data.min_order_qty,
          max_order_qty: response.data.max_order_qty,
          product_unit: response.data.product_unit,
          shipping_time: response.data.shipping_time,
          special_date: response.data.special_date || false
        };
      } catch (error) {
        console.error('Error fetching product details:', error);
        alert('獲取產品詳情失敗：' + error.message);
      }
    },
    async submitProduct() {
      try {
        // 數據驗證
        if (!this.product.name) {
          alert('請輸入產品名稱');
          return;
        }
        if (!this.product.description) {
          alert('請輸入產品描述');
          return;
        }
        if (!this.product.min_order_qty || !this.product.max_order_qty) {
          alert('請輸入訂購數量範圍');
          return;
        }
        if (!this.product.product_unit) {
          alert('請輸入產品單位');
          return;
        }

        const productData = {
          ...this.product,
          min_order_qty: parseInt(this.product.min_order_qty),
          max_order_qty: parseInt(this.product.max_order_qty),
          shipping_time: this.product.shipping_time || null,
          special_date: this.product.special_date
        };

        let response;
        if (this.isEditing) {
          // 編輯現有產品
          response = await axios.put(`http://127.0.0.1:5000/api/products/${this.editingId}`, productData, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });
          alert('產品更新成功！');
        } else {
          // 新增產品
          response = await axios.post('http://127.0.0.1:5000/api/products', productData, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });
          alert('產品新增成功！');
        }

        this.$router.push('/product-management');
      } catch (error) {
        console.error('Error submitting product:', error);
        const errorMessage = error.response?.data?.error || error.message;
        alert(this.isEditing ? '更新產品失敗：' : '新增產品失敗：' + errorMessage);
      }
    },
    cancel() {
      this.$router.push('/product-management');
    },
    getFullUrl(path) {
      if (!path) return '';
      return path.startsWith('http') ? path : `http://127.0.0.1:5000${path}`;
    },
    getFileName(path) {
      if (!path) return '';
      return path.split('/').pop();
    },
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      if (!this.product.name) {
        alert('請先輸入產品名稱');
        this.$refs.imageInput.value = '';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('productName', this.product.name);
      
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/upload/image', formData, {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        this.product.image_url = response.data.url;
      } catch (error) {
        console.error('Error uploading image:', error);
        alert('上傳圖片失敗：' + error.message);
      }
    },
    async handleDocumentUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      if (!this.product.name) {
        alert('請先輸入產品名稱');
        this.$refs.documentInput.value = '';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('productName', this.product.name);
      
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/upload/document', formData, {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        this.product.dm_url = response.data.url;
      } catch (error) {
        console.error('Error uploading document:', error);
        alert('上傳文件失敗：' + error.message);
      }
    },
    handleShippingTimeChange() {
      if (this.product.shipping_time) {
        this.product.special_date = false;
      }
    },
    handleSpecialDateChange() {
      if (this.product.special_date) {
        this.product.shipping_time = '';
      }
    }
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  },
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
