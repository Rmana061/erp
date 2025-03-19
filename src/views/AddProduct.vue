<!-- 新增產品 -->
<template>
  <body class="admin-mode">
  <div class="container product-management">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <div class="form-container product-form">
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
                <div class="file-input-row">
                  <button type="button" class="file-select-button" @click="triggerImageFileInput">選擇檔案</button>
                  <input 
                    type="file" 
                    accept="image/*" 
                    @change="handleImageUpload" 
                    ref="imageInput"
                    class="hidden-file-input"
                  >
                </div>
                <div v-if="selectedImageFile || product.image_url" class="preview-container">
                  <img 
                    v-if="imagePreviewUrl || product.image_url"
                    :src="imagePreviewUrl || product.image_url" 
                    class="image-preview" 
                    alt="產品圖片預覽"
                  >
                  <span class="file-name">
                    {{ selectedImageFile ? selectedImageFile.name : getFileName(product.image_url) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>產品DM：</label>
              <div class="input-container">
                <div class="file-input-row">
                  <button type="button" class="file-select-button" @click="triggerDmFileInput">選擇檔案</button>
                  <input 
                    type="file" 
                    accept=".pdf,.doc,.docx" 
                    @change="handleDmUpload"
                    ref="dmInput"
                    class="hidden-file-input"
                  >
                </div>
                <div v-if="selectedDmFile || product.dm_url" class="preview-container">
                  <span class="file-name">
                    目前文件: {{ selectedDmFile ? selectedDmFile.name : getFileName(product.dm_url) }}
                    <a 
                      v-if="product.dm_url && !selectedDmFile" 
                      @click.prevent="openDM(product.dm_url)" 
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
import { logoutMixin } from '../mixins/logoutMixin';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'AddProduct',
  mixins: [adminMixin, timeMixin, logoutMixin],
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
        special_date: false,
        original_image_filename: '',
        original_dm_filename: '',
        image_original_filename: '',
        dm_original_filename: ''
      },
      selectedImageFile: null,
      selectedDmFile: null,
      isEditing: false,
      editingId: null,
      imageFileToUpload: null,
      dmFileToUpload: null,
      imagePreviewUrl: '',
      dmPreviewUrl: ''
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
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCT_DETAIL(id)), {
          type: 'admin'
        }, {
          withCredentials: true
        });
        
        console.log('Product details response:', response.data);
        
        if (response.data.status === 'success' && response.data.data) {
          const productData = response.data.data;
          this.product = {
            name: productData.name,
            description: productData.description,
            image_url: productData.image_url,
            dm_url: productData.dm_url,
            min_order: productData.min_order_qty,
            max_order: productData.max_order_qty,
            unit: productData.product_unit,
            shipping_time: productData.shipping_time,
            special_date: productData.special_date,
            // 保存两个不同的字段命名以确保兼容性
            original_image_filename: productData.original_image_filename || productData.image_original_filename || '',
            original_dm_filename: productData.original_dm_filename || productData.dm_original_filename || '',
            image_original_filename: productData.image_original_filename || productData.original_image_filename || '',
            dm_original_filename: productData.dm_original_filename || productData.original_dm_filename || ''
          };
          console.log('Product data loaded:', this.product);
          // 清除文件选择状态，因为已经加载了现有产品的文件
          this.selectedImageFile = null;
          this.selectedDmFile = null;
        } else {
          throw new Error(response.data.message || '獲取產品資料失敗');
        }
      } catch (error) {
        console.error('Error fetching product details:', error);
        if (error.response?.status === 401) {
          this.$router.push('/admin-login');
          return;
        }
        alert('獲取產品資料失敗：' + (error.response?.data?.message || error.message));
        this.$router.push('/product-management');
      }
    },
    async saveProduct() {
      if (!this.validateForm()) {
        return;
      }

      try {
        console.log('保存产品前的数据:', this.product);
        
        // 如果有需要上傳的圖片文件
        if (this.imageFileToUpload) {
          const imageFormData = new FormData();
          imageFormData.append('file', this.imageFileToUpload);
          imageFormData.append('productName', this.product.name);
          
          try {
            console.log('正在上传图片...');
            const imageResponse = await axios.post(getApiUrl(API_PATHS.UPLOAD_IMAGE), imageFormData, {
              withCredentials: true,
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            
            if (imageResponse.data.status === 'success') {
              this.product.image_url = imageResponse.data.data.file_path;
              if (imageResponse.data.data.original_filename) {
                this.product.image_original_filename = imageResponse.data.data.original_filename;
                this.product.original_image_filename = imageResponse.data.data.original_filename;
              } else if (this.imageFileToUpload.name) {
                this.product.image_original_filename = this.imageFileToUpload.name;
                this.product.original_image_filename = this.imageFileToUpload.name;
              }
            } else {
              throw new Error(imageResponse.data.message || '上傳圖片失敗');
            }
          } catch (error) {
            console.error('Error uploading image:', error);
            alert('上傳圖片失敗：' + (error.response?.data?.message || error.message));
            return;
          }
        }
        
        // 如果有需要上傳的文件
        if (this.dmFileToUpload) {
          const dmFormData = new FormData();
          dmFormData.append('file', this.dmFileToUpload);
          dmFormData.append('productName', this.product.name);
          
          try {
            console.log('正在上传文档...');
            const dmResponse = await axios.post(getApiUrl(API_PATHS.UPLOAD_DOCUMENT), dmFormData, {
              withCredentials: true,
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            
            if (dmResponse.data.status === 'success') {
              this.product.dm_url = dmResponse.data.data.file_path;
              if (dmResponse.data.data.original_filename) {
                this.product.dm_original_filename = dmResponse.data.data.original_filename;
                this.product.original_dm_filename = dmResponse.data.data.original_filename;
              } else if (this.dmFileToUpload.name) {
                this.product.dm_original_filename = this.dmFileToUpload.name;
                this.product.original_dm_filename = this.dmFileToUpload.name;
              }
            } else {
              throw new Error(dmResponse.data.message || '上傳文件失敗');
            }
          } catch (error) {
            console.error('Error uploading document:', error);
            alert('上傳文件失敗：' + (error.response?.data?.message || error.message));
            return;
          }
        }

        const productData = {
          type: 'admin',
          name: this.product.name.trim(),
          description: this.product.description.trim(),
          image_url: this.product.image_url || null,
          dm_url: this.product.dm_url || null,
          min_order_qty: parseInt(this.product.min_order),
          max_order_qty: parseInt(this.product.max_order),
          product_unit: this.product.unit.trim(),
          shipping_time: parseInt(this.product.shipping_time) || 0,
          special_date: this.product.special_date || false,
          image_original_filename: this.product.image_original_filename || '',
          dm_original_filename: this.product.dm_original_filename || ''
        };

        if (!this.isEditing) {
          productData.status = 'active';
          productData.stock_quantity = 0;
        }

        const response = await axios.post(
          getApiUrl(this.isEditing ? API_PATHS.PRODUCT_UPDATE(this.editingId) : API_PATHS.PRODUCT_ADD),
          productData,
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.status === 'success' || 
            (response.data.message && response.data.message.includes('successfully'))) {
          alert(this.isEditing ? '產品更新成功！' : '產品新增成功！');
          this.clearFileSelections();
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
    clearFileSelections() {
      this.selectedImageFile = null;
      this.selectedDmFile = null;
      this.imageFileToUpload = null;
      this.dmFileToUpload = null;
      if (this.imagePreviewUrl) {
        URL.revokeObjectURL(this.imagePreviewUrl);
        this.imagePreviewUrl = '';
      }
      if (this.dmPreviewUrl) {
        URL.revokeObjectURL(this.dmPreviewUrl);
        this.dmPreviewUrl = '';
      }
      if (this.$refs.imageInput) this.$refs.imageInput.value = '';
      if (this.$refs.dmInput) this.$refs.dmInput.value = '';
    },
    cancel() {
      this.clearFileSelections();
      this.$router.push('/product-management');
    },
    getFullUrl(path) {
      if (!path) return '';
      // 如果路徑是完整的URL（以http或https開頭），則直接返回
      return path.startsWith('http') ? path : getApiUrl(path);
    },
    getFileName(path) {
      if (!path) return '';
      
      // 检查是否有图片原始文件名
      if (path === this.product.image_url) {
        if (this.product.original_image_filename || this.product.image_original_filename) {
          return this.product.original_image_filename || this.product.image_original_filename;
        }
      }
      
      // 检查是否有文档原始文件名
      if (path === this.product.dm_url) {
        if (this.product.original_dm_filename || this.product.dm_original_filename) {
          return this.product.original_dm_filename || this.product.dm_original_filename;
        }
      }
      
      // 如果没有原始文件名，则使用路径中的文件名
      return path.split('/').pop();
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 創建本地預覽URL
      if (this.imagePreviewUrl) {
        URL.revokeObjectURL(this.imagePreviewUrl);
      }
      this.imagePreviewUrl = URL.createObjectURL(file);
      
      // 立即顯示選擇的文件名
      this.selectedImageFile = file;
      
      // 保存文件以便之後上傳
      this.imageFileToUpload = file;
      
      if (!this.product.name) {
        alert('請先輸入產品名稱');
        this.clearFileSelections();
        return;
      }
      
      console.log(`選擇的圖片文件: ${file.name} (將在保存時上傳)`);
    },
    handleDmUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 創建本地預覽URL (雖然DM不會直接顯示在頁面上)
      if (this.dmPreviewUrl) {
        URL.revokeObjectURL(this.dmPreviewUrl);
      }
      this.dmPreviewUrl = URL.createObjectURL(file);
      
      // 立即顯示選擇的文件名
      this.selectedDmFile = file;
      
      // 保存文件以便之後上傳
      this.dmFileToUpload = file;
      
      if (!this.product.name) {
        alert('請先輸入產品名稱');
        this.clearFileSelections();
        return;
      }
      
      console.log(`選擇的文檔文件: ${file.name} (將在保存時上傳)`);
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
    },
    // 触发图片文件输入点击
    triggerImageFileInput() {
      this.$refs.imageInput.click();
    },
    
    // 触发文档文件输入点击
    triggerDmFileInput() {
      this.$refs.dmInput.click();
    },
    // 這個方法沒有在模板中使用，但需要新增以供文件視圖組件使用
    openDM(url) {
      if (!url) return;
      
      // 如果是本地預覽URL
      if (this.dmPreviewUrl && this.selectedDmFile) {
        // 直接開啟本地預覽URL
        window.open(this.dmPreviewUrl, '_blank');
        return;
      }
      
      // 如果是已保存的URL，維持原有邏輯
      let originalFilename = this.product.original_dm_filename || 
                           this.product.dm_original_filename || 
                           '';
                           
      console.log('打開DM，URL:', url);
      console.log('原始文件名:', originalFilename);
      
      // 檢查文件類型
      const isPdf = originalFilename.toLowerCase().endsWith('.pdf');
      
      if (url.startsWith('http') && originalFilename) {
        // 創建下載/預覽URL
        const downloadUrl = getApiUrl(`/api/azure-blob/download?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(originalFilename)}`);
        
        // 針對PDF文件，使用新視窗打開以便預覽
        // 針對其他文件，使用下載方式
        window.open(downloadUrl, '_blank');
      } else if (url.startsWith('http')) {
        // 如果是Azure URL但沒有原始文件名，直接打開
        window.open(url, '_blank', 'noopener,noreferrer');
      } else {
        // 本地文件，添加域名
        const baseUrl = window.location.origin;
        const fullUrl = `${baseUrl}${url}`;
        window.open(fullUrl, '_blank', 'noopener,noreferrer');
      }
    },
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
</style>
