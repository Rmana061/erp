import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 引入路由
import { permissionDirective } from './utils/permissionUtils';

const app = createApp(App);

// 註冊權限指令
app.directive('permission', permissionDirective);

app.use(router); // 使用路由
app.mount('#app'); // 掛載應用到 #app 元素
