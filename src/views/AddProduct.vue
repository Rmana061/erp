<!-- 新增產品 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,</span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <div class="form-container">
            <h2>{{ isEditing ? '編輯產品' : '新增產品' }}</h2>
            <div class="form-group">
              <label>產品名稱：</label>
              <input v-model="product.name" type="text" placeholder="請輸入產品名稱">
            </div>
            <div class="form-group">
              <label>產品描述：</label>
              <textarea v-model="product.description" placeholder="請輸入產品描述"></textarea>
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
                  @change="handleDmUpload"
                  ref="dmInput"
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
              <input v-model="product.min_order" type="number" placeholder="請輸入最小下單數量">
            </div>
            <div class="form-group">
              <label>最大下單數量：</label>
              <input v-model="product.max_order" type="number" placeholder="請輸入最大下單數量">
            </div>
            <div class="form-group">
              <label>產品單位：</label>
              <input v-model="product.unit" type="text" placeholder="請輸入產品單位">
            </div>
            <div class="form-group">
              <label>出貨時間：</label>
              <input v-model="product.shipping_time" type="number" placeholder="請輸入出貨時間">
            </div>
            <div class="form-group">
              <label>特殊日期：</label>
              <label class="custom-checkbox">
                <input type="checkbox" v-model="product.special_date">
                <span class="checkmark"></span>
              </label>
            </div>
            <div class="action-buttons">
              <button class="action-button" @click="saveProduct">保存</button>
              <button class="action-button cancel" @click="cancel">取消</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'AddProduct',
  mixins: [adminMixin, timeMixin],
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
        min_order: '',
        max_order: '',
        unit: '',
        shipping_time: '',
        special_date: false
      },
      isEditing: false,
      editingId: null
    };
  },
  created() {
    // 檢查是否是編輯模式
    const mode = this.$route.query.mode;
    const id = this.$route.query.id;
    
    console.log('Route query:', { mode, id });
    
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
        console.log('Fetching product details for ID:', id);
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'admin',
          product_id: id
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        console.log('Product details response:', response.data);
        
        if (response.data.status === 'success' && response.data.data) {
          // 从返回的产品列表中找到对应的产品
          const productData = response.data.data.find(p => p.id === parseInt(id));
          if (!productData) {
            throw new Error('找不到該產品');
          }
          
          this.product = {
            name: productData.name,
            description: productData.description,
            image_url: productData.image_url,
            dm_url: productData.dm_url,
            min_order: productData.min_order_qty,
            max_order: productData.max_order_qty,
            unit: productData.product_unit,
            shipping_time: productData.shipping_time,
            special_date: productData.special_date
          };
          console.log('Product data loaded:', this.product);
        } else {
          throw new Error(response.data.message || '獲取產品資料失敗');
        }
      } catch (error) {
        console.error('Error fetching product details:', error);
        alert('獲取產品資料失敗：' + (error.response?.data?.message || error.message));
        this.$router.push('/product-management');
      }
    },
    async saveProduct() {
      if (!this.validateForm()) {
        return;
      }

      try {
        const productData = {
          type: 'admin',
          name: this.product.name.trim(),
          description: this.product.description.trim(),
          image_url: this.product.image_url || null,
          dm_url: this.product.dm_url || null,
          min_order_qty: parseInt(this.product.min_order),
          max_order_qty: parseInt(this.product.max_order),
          product_unit: this.product.unit.trim(),
          stock_quantity: 0,
          status: 'available',
          shipping_time: parseInt(this.product.shipping_time) || 0,
          special_date: this.product.special_date || false
        };

        console.log('Sending product data:', productData);

        const response = await axios.post(
          getApiUrl(this.isEditing ? API_PATHS.PRODUCT_UPDATE(this.editingId) : API_PATHS.PRODUCTS),
          productData,
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        console.log('Server response:', response.data);

        if (response.data.status === 'success' || 
            (response.data.message && response.data.message.includes('successfully'))) {
          alert(this.isEditing ? '產品更新成功！' : '產品新增成功！');
          this.$router.push('/product-management');
          return;
        }

        const errorMessage = response.data.message || '操作失敗，請稍後再試';
        alert(errorMessage);

      } catch (error) {
        console.error('Error saving product:', error);
        const errorMessage = error.response?.data?.message || error.message || '操作失敗，請稍後再試';
        alert(errorMessage);
      }
    },
    cancel() {
      this.$router.push('/product-management');
    },
    getFullUrl(path) {
      if (!path) return '';
      return path.startsWith('http') ? path : getApiUrl(path);
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
        const response = await axios.post(getApiUrl(API_PATHS.UPLOAD_IMAGE), formData, {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (response.data.status === 'success') {
          this.product.image_url = response.data.data.file_path;
          this.$refs.imageInput.value = '';
        } else {
          throw new Error(response.data.message || '上傳圖片失敗');
        }
      } catch (error) {
        console.error('Error uploading image:', error);
        alert('上傳圖片失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async handleDmUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      if (!this.product.name) {
        alert('請先輸入產品名稱');
        this.$refs.dmInput.value = '';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('productName', this.product.name);
      
      try {
        const response = await axios.post(getApiUrl(API_PATHS.UPLOAD_DOCUMENT), formData, {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (response.data.status === 'success') {
          this.product.dm_url = response.data.data.file_path;
          this.$refs.dmInput.value = '';
        } else {
          throw new Error(response.data.message || '上傳文件失敗');
        }
      } catch (error) {
        console.error('Error uploading document:', error);
        alert('上傳文件失敗：' + (error.response?.data?.message || error.message));
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
    },
    validateForm() {
      // 检查必填字段
      if (!this.product.name?.trim()) {
        alert('請輸入產品名稱');
        return false;
      }
      if (!this.product.description?.trim()) {
        alert('請輸入產品描述');
        return false;
      }

      // 检查数值字段
      const minOrder = parseInt(this.product.min_order);
      const maxOrder = parseInt(this.product.max_order);
      
      if (isNaN(minOrder) || minOrder <= 0) {
        alert('請輸入有效的最小下單數量');
        return false;
      }
      if (isNaN(maxOrder) || maxOrder <= 0) {
        alert('請輸入有效的最大下單數量');
        return false;
      }
      if (minOrder > maxOrder) {
        alert('最小下單數量不能大於最大下單數量');
        return false;
      }

      // 检查单位
      if (!this.product.unit?.trim()) {
        alert('請輸入產品單位');
        return false;
      }

      // 检查出货时间
      if (!this.product.special_date) {
        const shippingTime = parseInt(this.product.shipping_time);
        if (isNaN(shippingTime) || shippingTime < 0) {
          alert('請輸入有效的出貨時間');
          return false;
        }
      }

      return true;
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

.custom-checkbox {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 0;
  user-select: none;
}

.custom-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.custom-checkbox .checkmark {
  position: relative;
  height: 18px;
  width: 18px;
  background-color: #fff;
  border: 2px solid #ddd;
  border-radius: 3px;
  margin-right: 8px;
}

.custom-checkbox:hover input ~ .checkmark {
  border-color: #40b883;
}

.custom-checkbox input:checked ~ .checkmark {
  background-color: #40b883;
  border-color: #40b883;
}

.custom-checkbox .checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 5px;
  top: 1px;
  width: 4px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-checkbox input:checked ~ .checkmark:after {
  display: block;
}

/* 其他样式保持不变 */
</style>
