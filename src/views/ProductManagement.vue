<!-- 產品管理 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <button class="bookmark-toggle" @click="toggleSidebar">
      <span class="bookmark-text">選單</span>
    </button>
    <SideBar menu-type="admin" :class="{ active: isSidebarActive }" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
            <h2>產品管理</h2>
          <div class="action-buttons">
            <button 
              class="action-button" 
              @click="navigateTo('AddProduct')"
              v-permission="'can_add_product'">
              + 新增產品
            </button>
            <button 
              class="action-button" 
              v-permission="'can_add_product'"
              @click="batchDelete">
              - 批量刪除
            </button>
            <button 
              class="export-btn product-export-btn"
              v-permission="'can_add_product'" 
              @click="exportReport">
              ↓ 產品匯出
            </button>
            <button 
              class="action-button" 
              v-permission="'can_close_order_dates'"
              @click="showLockDateDialog">
              🔒 鎖定日期
            </button>
            <div class="search-container">
              <input type="text" v-model="searchQuery" placeholder="搜尋產品..." class="search-input" />
              <select v-model="searchType" class="search-select">
                <option value="name">產品名稱</option>
                <option value="description">產品描述</option>
              </select>
            </div>
          </div>

          <!-- 锁定日期对话框 -->
          <div v-if="showLockDateModal" class="modal">
            <div class="modal-content">
              <h3>鎖定日期管理</h3>
              <div class="lock-date-form">
                <input type="date" v-model="newLockDate" :min="today">
                <button @click="lockDate">鎖定</button>
              </div>
              <div class="locked-dates-list">
                <h4>已鎖定日期列表</h4>
                <ul>
                  <li v-for="date in lockedDates" :key="date.id">
                    {{ formatDate(date.locked_date) }}
                    <button @click="unlockDate(date.id)" class="unlock-button">解鎖</button>
                  </li>
                </ul>
              </div>
              <button class="close-button" @click="closeLockDateDialog">&times;</button>
            </div>
          </div>

          <div class="table-container">
            <table class="product-table">
              <thead>
                <tr>
                  <th><input type="checkbox" @click="selectAll" :checked="allSelected"></th>
                  <th>產品圖片</th>
                  <th>產品名稱</th>
                  <th>產品描述</th>
                  <th>最小訂購量</th>
                  <th>最大訂購量</th>
                  <th>單位</th>
                  <th>出貨時間</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in filteredProducts" :key="product.id">
                  <td><input type="checkbox" v-model="product.selected"></td>
                  <td>
            <img 
              :src="product.image_url" 
                      class="product-thumbnail"
              @click="showLargeImage(product.image_url)"
                      alt="產品圖片"
                    >
                  </td>
                  <td>{{ product.name }}</td>
                  <td>{{ product.description }}</td>
                  <td>{{ product.min_order_qty }}</td>
                  <td>{{ product.max_order_qty }}</td>
                  <td>{{ product.product_unit }}</td>
                  <td>
                    <template v-if="product.special_date">特殊日期</template>
                    <template v-else>{{ product.shipping_time }}天</template>
                  </td>
                  <td>
                    <div class="table-button-group">
                      <button 
                        class="table-button edit" 
                        @click="editProduct(product.id)"
                        v-permission="'can_add_product'">
                        編輯
                      </button>
                      <button 
                        class="table-button delete" 
                        @click="deleteProduct(product.id)"
                        v-permission="'can_add_product'">
                        刪除
                      </button>
                      <button 
                        class="table-button" 
                        @click="openDM(product.dm_url)">
                        DM
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination">
            <button @click="changePage(-1)" :disabled="currentPage === 1">上一頁</button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button @click="changePage(1)" :disabled="currentPage === totalPages">下一頁</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 圖片預覽模態框 -->
  <div v-if="showModal" class="modal" @click="closeModal">
      <div class="modal-content">
        <span class="close-button" @click.stop="closeModal">&times;</span>
        <img :src="selectedImage" alt="放大圖片" class="large-image">
      </div>
    </div>
  </body>
</template>

<script>
import axios from "axios";
import * as XLSX from "xlsx";
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import { logoutMixin } from '../mixins/logoutMixin';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: "ProductManagement",
  components: {
    SideBar
  },
  mixins: [adminMixin, timeMixin, logoutMixin],
  data() {
    return {
      searchQuery: "",
      searchType: "name",
      products: [],
      showModal: false,
      selectedImage: '',
      currentPage: 1,
      itemsPerPage: 20,
      allSelected: false,
      isSidebarActive: false,
      showLockDateModal: false,
      newLockDate: '',
      lockedDates: [],
    };
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0];
    },
    filteredProducts() {
      let filtered = this.products;
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(product => {
          if (this.searchType === 'name') {
            return product.name.toLowerCase().includes(query);
          } else {
            return product.description.toLowerCase().includes(query);
          }
        });
      }
      return filtered;
    },
    totalPages() {
      return Math.ceil(this.filteredProducts.length / this.itemsPerPage);
    },
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredProducts.slice(start, end);
    }
  },
  methods: {
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    selectAll() {
      this.allSelected = !this.allSelected;
      this.products.forEach(product => {
        product.selected = this.allSelected;
      });
    },
    async batchDelete() {
      const selectedProducts = this.products.filter(product => product.selected);
      
      if (selectedProducts.length === 0) {
        alert("請選擇要刪除的產品");
        return;
      }

      if (confirm(`確定要刪除選中的 ${selectedProducts.length} 個產品嗎？`)) {
        try {
          await Promise.all(selectedProducts.map(product => 
            axios.post(getApiUrl(API_PATHS.PRODUCT_DELETE(product.id)), {
              type: 'admin',
              soft_delete: true, // 軟刪除標記
              product_folder: product.name // 傳遞產品名稱，用於刪除對應的上傳文件夾
            }, {
              withCredentials: true,
              headers: {
                'Content-Type': 'application/json'
              }
            })
          ));

          alert("產品已成功刪除");
          this.fetchProducts();
        } catch (error) {
          console.error("Error deleting products:", error);
          alert("刪除產品時發生錯誤：" + (error.response?.data?.message || error.message));
        }
      }
    },
    async deleteProduct(productId) {
      const product = this.products.find(p => p.id === productId);
      if (!product) return;
      
      if (confirm(`確定要刪除產品：${product.name}？`)) {
        try {
          const response = await axios.post(getApiUrl(API_PATHS.PRODUCT_DELETE(productId)), {
            type: 'admin',
            soft_delete: true, // 軟刪除標記
            product_folder: product.name // 傳遞產品名稱，用於刪除對應的上傳文件夾
          }, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });

          if (response.data.status === 'success') {
            alert("產品已成功刪除");
            await this.fetchProducts();
          } else {
            throw new Error(response.data.message || '刪除失敗');
          }
        } catch (error) {
          console.error("Error deleting product:", error);
          alert("刪除產品時發生錯誤：" + (error.response?.data?.message || error.message));
        }
      }
    },
    editProduct(productId) {
      this.$router.push({
        name: 'AddProduct',
        query: {
          id: productId,
          mode: 'edit'
        }
      });
    },
    exportReport() {
      const headers = [
        "ID",
        "產品名稱",
        "產品描述",
        "最小訂購量",
        "最大訂購量",
        "單位",
        "出貨時間",
        "特殊日期",
        "產品圖片",
        "產品DM",
        "建立時間",
        "更新時間",
      ];

      // 获取当前域名
      const baseUrl = window.location.origin;

      // 准备数据
      const data = [headers];
      const hyperlinks = {};

      // 添加产品数据
      this.products.forEach((product, index) => {
        const rowIndex = index + 1;  // 跳过标题行
        const row = [
          product.id,
          product.name,
          product.description,
          product.min_order_qty,
          product.max_order_qty,
          product.product_unit,
          product.special_date ? '特殊日期' : (product.shipping_time + '天'),
          product.special_date ? '是' : '否',
          product.image_url ? '點擊查看圖片' : '',
          product.dm_url ? '點擊查看DM' : '',
          product.created_at,
          product.updated_at
        ];
        data.push(row);

        // 添加图片链接
        if (product.image_url) {
          const imageCell = XLSX.utils.encode_cell({r: rowIndex, c: 8});
          hyperlinks[imageCell] = {
            l: {
              Target: baseUrl + product.image_url,
              Tooltip: "點擊查看產品圖片"
            },
            s: {
              font: {
                color: { rgb: "0563C1" },  // 蓝色
                underline: true
              }
            }
          };
        }

        // 添加DM链接
        if (product.dm_url) {
          const dmCell = XLSX.utils.encode_cell({r: rowIndex, c: 9});
          hyperlinks[dmCell] = {
            l: {
              Target: baseUrl + product.dm_url,
              Tooltip: "點擊查看DM"
            },
            s: {
              font: {
                color: { rgb: "0563C1" },  // 蓝色
                underline: true
              }
            }
          };
        }
      });

      // 创建工作簿和工作表
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet(data);

      // 应用超链接和样式
      Object.keys(hyperlinks).forEach(cell => {
        if (!ws[cell]) ws[cell] = { v: ws[cell]?.v || '' };
        ws[cell].l = hyperlinks[cell].l;
        ws[cell].s = hyperlinks[cell].s;
      });

      // 设置列宽
      ws['!cols'] = [
        { wch: 10 }, // ID
        { wch: 20 }, // 產品名稱
        { wch: 30 }, // 產品描述
        { wch: 15 }, // 最小訂購量
        { wch: 15 }, // 最大訂購量
        { wch: 10 }, // 單位
        { wch: 15 }, // 出貨時間
        { wch: 15 }, // 特殊日期
        { wch: 20 }, // 產品圖片
        { wch: 20 }, // 產品DM
        { wch: 20 }, // 建立時間
        { wch: 20 }, // 更新時間
      ];

      XLSX.utils.book_append_sheet(wb, ws, "產品清單");
      XLSX.writeFile(wb, "產品資料.xlsx");
    },
    async fetchProducts() {
      try {
        console.log('開始獲取產品列表...');
        const response = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'admin'
        }, {
          withCredentials: true
        });

        console.log('API響應:', response.data);

        if (response.data.status === 'success') {
          if (!Array.isArray(response.data.data)) {
            console.error('API返回的數據不是數組格式:', response.data);
            throw new Error('獲取產品列表數據格式錯誤');
          }

          this.products = response.data.data.map(product => ({
            ...product,
            selected: false
          }));
          console.log('成功獲取產品列表:', this.products);
        } else {
          throw new Error(response.data.message || '獲取產品列表失敗');
        }
      } catch (error) {
        console.error('獲取產品列表失敗:', error);
        if (error.response) {
          console.error('錯誤響應:', error.response.data);
          console.error('狀態碼:', error.response.status);
          if (error.response.status === 401) {
            alert('登入已過期，請重新登入');
            this.$router.push('/admin-login');
            return;
          }
        }
        alert('獲取產品列表失敗：' + (error.response?.data?.message || error.message));
      }
    },
    showLargeImage(imageUrl) {
      this.selectedImage = imageUrl;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    changePage(direction) {
      const newPage = this.currentPage + direction;
      if (newPage >= 1 && newPage <= this.totalPages) {
        this.currentPage = newPage;
      }
    },
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    showLockDateDialog() {
      this.showLockDateModal = true;
      this.fetchLockedDates();
    },
    closeLockDateDialog() {
      this.showLockDateModal = false;
      this.newLockDate = '';
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    },
    async fetchLockedDates() {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.LOCKED_DATES), {
          type: 'admin'
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.lockedDates = response.data.data;
        } else {
          throw new Error(response.data.message || '獲取鎖定日期失敗');
        }
      } catch (error) {
        console.error('Error fetching locked dates:', error);
        alert('獲取鎖定日期失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async lockDate() {
      if (!this.newLockDate) {
        alert('請選擇要鎖定的日期');
        return;
      }

      try {
        // 获取管理员ID
        const adminId = localStorage.getItem('admin_id');
        
        const response = await axios.post(getApiUrl(API_PATHS.LOCK_DATE), {
          type: 'admin',
          date: this.newLockDate,
          admin_id: adminId // 添加管理员ID
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          alert('日期鎖定成功');
          this.newLockDate = '';
          this.fetchLockedDates();
        } else {
          throw new Error(response.data.message || '鎖定日期失敗');
        }
      } catch (error) {
        console.error('Error locking date:', error);
        alert('鎖定日期失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async unlockDate(dateId) {
      if (!confirm('確定要解鎖這個日期嗎？')) {
        return;
      }

      try {
        // 获取管理员ID
        const adminId = localStorage.getItem('admin_id');
        
        const response = await axios.post(getApiUrl(API_PATHS.UNLOCK_DATE), {
          type: 'admin',
          date_id: dateId,
          admin_id: adminId // 添加管理员ID
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          alert('日期解鎖成功');
          this.fetchLockedDates();
        } else {
          throw new Error(response.data.message || '解鎖日期失敗');
        }
      } catch (error) {
        console.error('Error unlocking date:', error);
        alert('解鎖日期失敗：' + (error.response?.data?.message || error.message));
      }
    },
    openDM(url) {
      if (!url) return;
      
      // 从产品列表中查找对应的产品
      const product = this.products.find(p => p.dm_url === url);
      let originalFilename = '';
      
      // 依次嘗試獲取原始檔名
      if (product) {
        originalFilename = product.dm_original_filename || 
                          product.original_dm_filename || 
                          '';
      }
      
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
  mounted() {
    document.title = '合揚訂單後台系統';
    this.fetchProducts();
  },
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
