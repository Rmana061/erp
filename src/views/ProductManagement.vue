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
        <span>Hi {{ adminName }}您好,</span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <h2>產品管理</h2>
          <div class="action-buttons">
            <button class="action-button" @click="navigateTo('AddProduct')">+ 新增產品</button>
            <button class="action-button" @click="batchDelete">- 批量刪除</button>
            <button class="action-button" @click="exportReport">↓ 報表匯出</button>
            <div class="search-container">
              <input type="text" v-model="searchQuery" placeholder="搜尋產品..." class="search-input" />
              <select v-model="searchType" class="search-select">
                <option value="name">產品名稱</option>
                <option value="description">產品描述</option>
              </select>
            </div>
          </div>

          <div class="table-container">
            <table>
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
                  <td>{{ product.unit }}</td>
                  <td>{{ product.shipping_time }}天</td>
                  <td>
                    <button class="table-button edit" @click="editProduct(product)">編輯</button>
                    <button class="table-button delete" @click="deleteProduct(product)">刪除</button>
                    <a v-if="product.dm_url" 
                       :href="product.dm_url" 
                       target="_blank" 
                       class="table-button">查看 DM</a>
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

export default {
  name: "ProductManagement",
  components: {
    SideBar
  },
  mixins: [adminMixin],
  data() {
    return {
      currentTime: "",
      searchQuery: "",
      searchType: "name",
      products: [],
      showModal: false,
      selectedImage: '',
      currentPage: 1,
      itemsPerPage: 10,
      allSelected: false,
      isSidebarActive: false,
    };
  },
  computed: {
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
    updateCurrentTime() {
      const now = new Date();
      const options = { 
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        weekday: "long",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      };
      this.currentTime = now
        .toLocaleString("zh-TW", options)
        .replace(/\//g, "/")
        .replace("星期", " 星期")
        .replace(/(\d+):(\d+)/, "$1:$2");
    },
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
            axios.delete(`http://127.0.0.1:5000/api/products/${product.id}`, {
              withCredentials: true,
              headers: {
                "Content-Type": "application/json",
              },
            })
          ));
          
          alert("產品已成功刪除");
          this.fetchProducts();
        } catch (error) {
          console.error("Error deleting products:", error);
          alert("刪除產品時發生錯誤：" + error.message);
        }
      }
    },
    async deleteProduct(product) {
      if (confirm(`確定要刪除產品：${product.name}？`)) {
        try {
          await axios.delete(`http://127.0.0.1:5000/api/products/${product.id}`, {
            withCredentials: true,
            headers: {
              "Content-Type": "application/json",
            },
          });
          
          alert("產品已成功刪除");
          this.fetchProducts();
        } catch (error) {
          console.error("Error deleting product:", error);
          alert("刪除產品時發生錯誤：" + error.message);
        }
      }
    },
    editProduct(product) {
      this.$router.push({
        name: "AddProduct",
        query: {
          mode: "edit",
          id: product.id,
        },
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
        "建立時間",
        "更新時間",
      ];
      
      const data = [
        headers,
        ...this.products.map(product => [
          product.id,
          product.name,
          product.description,
          product.min_order_qty,
          product.max_order_qty,
          product.unit,
          product.shipping_time,
          product.created_at,
          product.updated_at
        ])
      ];

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet(data);
      
      XLSX.utils.book_append_sheet(wb, ws, "產品清單");
      XLSX.writeFile(wb, "產品資料.xlsx");
    },
    async fetchProducts() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/products", {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        });

        this.products = response.data.map(product => ({
          ...product,
          selected: false
        }));
      } catch (error) {
        console.error("Error fetching products:", error);
        alert("獲取產品列表失敗：" + error.message);
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
  },
  mounted() {
    this.updateCurrentTime();
    this.timeInterval = setInterval(this.updateCurrentTime, 60000);
    document.title = '管理者系統';
    this.fetchProducts();
  },
  beforeUnmount() {
    clearInterval(this.timeInterval);
  },
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有樣式已移至 unified-base */
</style>
