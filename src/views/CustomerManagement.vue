<!-- 客戶管理 -->
<template>
  <body class="admin-mode">
  <div class="container">
    <SideBar menu-type="admin" />
    <div class="main-content">
      <div class="header">
        <span>Hi {{ adminName }}您好,<button class="logout-button" @click="logout">登出</button></span>
        <span>{{ currentTime }}</span>
      </div>
      <div class="content-wrapper">
        <div class="scrollable-content">
          <h2>客戶管理</h2>
          <div class="action-buttons">
            <button 
              class="action-button" 
              @click="navigateTo('AddCustomer')"
              v-permission="'can_add_customer'">
              + 新增客戶
            </button>
            <button 
              class="action-button" 
              @click="exportCustomers"
              v-permission="'can_add_customer'">
              📊 資料匯出
            </button>
            <input type="text" v-model="searchQuery" placeholder="搜尋客戶..." class="search-input">
          </div>

          <div class="table-container">
            <table id="customersTable">
              <thead>
                <tr>
                  <th>公司名稱</th>
                  <th>聯絡人</th>
                  <th>電話</th>
                  <th>Email</th>
                  <th>地址</th>
                  <th>重複下單限制</th>
                  <th>建立時間</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(customer, index) in paginatedCustomers" :key="customer.id">
                  <td>{{ customer.company_name }}</td>
                  <td>{{ customer.contact_person }}</td>
                  <td>{{ customer.phone }}</td>
                  <td>{{ customer.email }}</td>
                  <td>{{ customer.address }}</td>
                  <td>{{ customer.repeat_order_limit }}</td>
                  <td>{{ customer.created_at }}</td>
                  <td>
                    <div class="table-button-group">
                      <button 
                        class="table-button edit" 
                        @click="editCustomer(customer.id)"
                        v-permission="'can_add_customer'">
                        編輯
                      </button>
                      <button 
                        class="table-button delete" 
                        @click="deleteCustomer(customer.id)"
                        v-permission="'can_add_customer'">
                        刪除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button @click="previousPage" :disabled="currentPage === 1">上一頁</button>
            <span>第 {{ currentPage }} 頁，共 {{ totalPages }} 頁</span>
            <button @click="nextPage" :disabled="currentPage === totalPages">下一頁</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>
import axios from 'axios';
import * as XLSX from 'xlsx';
import SideBar from '../components/SideBar.vue';
import { adminMixin } from '../mixins/adminMixin';
import { timeMixin } from '../mixins/timeMixin';
import { logoutMixin } from '../mixins/logoutMixin';
import { API_PATHS, getApiUrl } from '../config/api';

export default {
  name: 'CustomerManagement',
  mixins: [adminMixin, timeMixin, logoutMixin],
  components: {
    SideBar
  },
  data() {
    return {
      currentTime: '',
      isMenuOpen: false,
      customers: [],
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 20
    };
  },
  computed: {
    filteredCustomers() {
      return this.customers.filter(customer => {
        const searchLower = this.searchQuery.toLowerCase();
        return (customer.company_name || '').toLowerCase().includes(searchLower) || 
               (customer.contact_person || '').toLowerCase().includes(searchLower) || 
               (customer.phone || '').toLowerCase().includes(searchLower) || 
               (customer.email || '').toLowerCase().includes(searchLower) || 
               (customer.address || '').toLowerCase().includes(searchLower);
      });
    },
    totalPages() {
      return Math.ceil(this.filteredCustomers.length / this.itemsPerPage);
    },
    paginatedCustomers() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredCustomers.slice(start, end);
    }
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
    async fetchCustomers() {
      try {
        const response = await axios.post(getApiUrl(API_PATHS.CUSTOMER_LIST), {}, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        if (response.data && response.data.status === 'success') {
          console.log('原始客户数据:', response.data.data);
          console.log('第一位客户的reorder_limit_days值:', response.data.data[0]?.reorder_limit_days);
          
          this.customers = response.data.data.map(customer => {
            console.log(`处理客户 ${customer.company_name} 的reorder_limit_days:`, customer.reorder_limit_days);
            
            return {
              ...customer,
              viewable_products: customer.viewable_products || '',
              line_users: customer.line_users || [],
              line_groups: customer.line_groups || [],
              remark: customer.remark || '',
              repeat_order_limit: customer.reorder_limit_days > 0 ? `${customer.reorder_limit_days}天` : '無限制'
            };
          });
          console.log('处理后的客户数据:', this.customers);
        } else {
          console.error('獲取客戶數據失敗:', response.data.message);
        }
      } catch (error) {
        console.error('Error fetching customer data:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
      }
    },
    async deleteCustomerRow(customerId) {
      if (!confirm('確定要刪除此客戶嗎？')) return;

      try {
        const response = await axios.post(
          getApiUrl(API_PATHS.CUSTOMER_DELETE),
          { id: customerId },
          {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.status === 'success') {
          alert('客戶刪除成功');
          this.fetchCustomers();  // 重新获取客户列表
        } else {
          throw new Error(response.data.message || '刪除客戶失敗');
        }
      } catch (error) {
        console.error('Error deleting customer:', error);
        alert('刪除客戶失敗：' + (error.response?.data?.message || error.message));
      }
    },
    async exportCustomers() {
      try {
        // 1. 先獲取所有產品數據
        const productsResponse = await axios.post(getApiUrl(API_PATHS.PRODUCTS), {
          type: 'admin'
        }, {
          withCredentials: true
        });

        if (productsResponse.data.status !== 'success') {
          throw new Error('獲取產品列表失敗');
        }

        // 建立產品 ID 到產品名稱的映射
        const productMap = {};
        productsResponse.data.data.forEach(product => {
          productMap[product.id] = product.name;
        });

        const headers = [
          '客戶編號',
          '公司名稱',
          '帳號',
          '聯絡人',
          '電話',
          'Email',
          '地址',
          '可購產品',
          'LINE個人帳號',
          'LINE群組',
          '備註',
          '重複下單限制天數',
          '建立時間',
          '更新時間'
        ];
        
        const data = [
          headers,
          ...this.customers.map(customer => {
            // 處理可購產品，將 ID 轉換為產品名稱
            let viewableProductNames = '';
            if (customer.viewable_products) {
              try {
                // 嘗試多種方式解析產品 ID
                let productIds = [];
                
                // 情況1: viewable_products 已經是數組
                if (Array.isArray(customer.viewable_products)) {
                  productIds = customer.viewable_products;
                } 
                // 情況2: viewable_products 是JSON字符串 "[1,2,3]"
                else if (typeof customer.viewable_products === 'string') {
                  const trimmed = customer.viewable_products.trim();
                  
                  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
                    try {
                      productIds = JSON.parse(trimmed);
                    } catch (e) {
                      console.warn('無法解析JSON格式的產品ID列表:', trimmed);
                    }
                  } 
                  // 情況3: 逗號分隔的數字 "1,2,3" 或空格分隔 "1 2 3"
                  else if (trimmed.includes(',') || trimmed.includes(' ')) {
                    // 先用逗號分隔，再用空格分隔，確保各種格式都能處理
                    productIds = trimmed
                      .split(/[,\s]+/)  // 用逗號或空格分隔
                      .filter(id => id.trim() !== '') // 過濾空項
                      .map(id => parseInt(id.trim())) // 轉換為數字
                      .filter(id => !isNaN(id));      // 過濾非數字
                  }
                  // 情況4: 單個數字 "1"
                  else if (/^\d+$/.test(trimmed)) {
                    productIds = [parseInt(trimmed)];
                  }
                }
                
                // 將產品ID轉換為產品名稱
                if (productIds.length > 0) {
                  viewableProductNames = productIds
                    .filter(id => productMap[id]) // 過濾掉不存在的產品 ID
                    .map(id => productMap[id])    // 將 ID 轉換為產品名稱
                    .join(', ');                  // 使用逗號分隔
                } else {
                  console.log('未找到有效的產品ID列表:', customer.viewable_products);
                }
              } catch (error) {
                console.error('解析可購產品時發生錯誤:', error, '原始值:', customer.viewable_products);
                viewableProductNames = '解析錯誤';
              }
            }

            return [
              customer.id,
              customer.company_name,
              customer.username,
              customer.contact_person,
              customer.phone,
              customer.email,
              customer.address,
              viewableProductNames,
              customer.line_users ? customer.line_users.map(user => user.user_name).join(', ') : '',
              customer.line_groups ? customer.line_groups.map(group => group.group_name).join(', ') : '',
              customer.remark || '',
              customer.reorder_limit_days || 0,
              customer.created_at,
              customer.updated_at
            ];
          })
        ];

        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet(data);
        
        const wscols = [
          { wch: 10 },  // 客戶編號
          { wch: 25 },  // 公司名稱
          { wch: 15 },  // 帳號
          { wch: 15 },  // 聯絡人
          { wch: 15 },  // 電話
          { wch: 25 },  // Email
          { wch: 40 },  // 地址
          { wch: 60 },  // 可購產品（增加寬度因為現在是產品名稱）
          { wch: 20 },  // LINE個人帳號
          { wch: 40 },  // LINE群組
          { wch: 40 },  // 備註
          { wch: 15 },  // 重複下單限制天數
          { wch: 20 },  // 建立時間
          { wch: 20 }   // 更新時間
        ];
        ws['!cols'] = wscols;

        XLSX.utils.book_append_sheet(wb, ws, '客戶清單');
        XLSX.writeFile(wb, '客戶資料.xlsx');
      } catch (error) {
        console.error('匯出客戶資料時發生錯誤：', error);
        alert('匯出客戶資料失敗：' + (error.message || '未知錯誤'));
      }
    },
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },
    editCustomer(customerId) {
      this.$router.push({
        name: 'AddCustomer',
        query: {
          id: customerId,
          mode: 'edit'
        }
      });
    },
    deleteCustomer(customerId) {
      this.deleteCustomerRow(customerId);
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    }
  },
  mounted() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 60000);
    document.title = '合揚訂單後台系統';
    this.fetchCustomers();
  },
  watch: {
    $route() {
      this.closeMenu();
    }
  }
};
</script>

<style>
@import '../assets/styles/unified-base.css';

/* 所有其他樣式已移至 unified-base */
</style>
