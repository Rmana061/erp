// 權限管理工具

// 權限常量定義
export const Permissions = {
  CAN_APPROVE_ORDERS: 'can_approve_orders',
  CAN_EDIT_ORDERS: 'can_edit_orders',
  CAN_CLOSE_ORDER_DATES: 'can_close_order_dates',
  CAN_ADD_CUSTOMER: 'can_add_customer',
  CAN_ADD_PRODUCT: 'can_add_product',
  CAN_ADD_PERSONNEL: 'can_add_personnel',
  CAN_VIEW_SYSTEM_LOGS: 'can_view_system_logs',
  CAN_DECIDE_PRODUCT_VIEW: 'can_decide_product_view'
};

// 存儲當前用戶的權限
let currentPermissions = null;

// 設置當前用戶的權限
export function setUserPermissions(permissions) {
  console.log('Setting permissions:', JSON.stringify(permissions, null, 2));
  if (!permissions || typeof permissions !== 'object') {
    console.error('Invalid permissions object:', permissions);
    return;
  }
  currentPermissions = permissions;
  // 將權限保存到 sessionStorage
  try {
    const adminInfo = JSON.parse(sessionStorage.getItem('adminInfo') || '{}');
    adminInfo.permissions = permissions;
    sessionStorage.setItem('adminInfo', JSON.stringify(adminInfo));
  } catch (error) {
    console.error('Error saving permissions to sessionStorage:', error);
  }
}

// 檢查是否有特定權限
export function hasPermission(permission) {
  console.log('Checking permission:', permission);
  console.log('Current permissions:', JSON.stringify(currentPermissions, null, 2));
  
  if (!currentPermissions) {
    console.warn('No permissions set');
    return false;
  }
  
  if (!(permission in currentPermissions)) {
    console.warn(`Permission ${permission} not found in current permissions`);
    return false;
  }
  
  const hasPermission = currentPermissions[permission] === true;
  console.log(`Permission check result for ${permission}:`, hasPermission);
  return hasPermission;
}

// 清除權限
export function clearPermissions() {
  console.log('Clearing permissions');
  currentPermissions = null;
  try {
    const adminInfo = JSON.parse(sessionStorage.getItem('adminInfo') || '{}');
    delete adminInfo.permissions;
    sessionStorage.setItem('adminInfo', JSON.stringify(adminInfo));
  } catch (error) {
    console.error('Error clearing permissions from sessionStorage:', error);
  }
}

// 權限指令
export const permissionDirective = {
  mounted(el, binding) {
    const permission = binding.value;
    console.log('Mounting permission directive:', permission);
    if (!hasPermission(permission)) {
      console.log(`Disabling element due to missing permission: ${permission}`);
      el.disabled = true;
      el.classList.add('disabled');
      el.style.opacity = '0.5';
      el.style.cursor = 'not-allowed';
    }
  },
  updated(el, binding) {
    const permission = binding.value;
    console.log('Updating permission directive:', permission);
    if (!hasPermission(permission)) {
      console.log(`Disabling element due to missing permission: ${permission}`);
      el.disabled = true;
      el.classList.add('disabled');
      el.style.opacity = '0.5';
      el.style.cursor = 'not-allowed';
    } else {
      console.log(`Enabling element with permission: ${permission}`);
      el.disabled = false;
      el.classList.remove('disabled');
      el.style.opacity = '1';
      el.style.cursor = 'pointer';
    }
  }
}; 