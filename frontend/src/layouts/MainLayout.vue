<template>
  <div class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">TaskFlow</span>
        <span class="subtitle">AI 智能任务管理</span>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.user?.username }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>{{ authStore.user?.email }}</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container class="body">
      <el-aside width="200px" class="sidebar">
        <el-menu :default-active="route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon><span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon><span>任务列表</span>
          </el-menu-item>
          <el-menu-item index="/weekly-report">
            <el-icon><Document /></el-icon><span>AI 周报</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { User, ArrowDown, DataAnalysis, List, Document } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

async function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout { height: 100vh; display: flex; flex-direction: column; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; height: 56px; }
.header-left .logo { font-size: 18px; font-weight: bold; color: #409EFF; margin-right: 8px; }
.header-left .subtitle { font-size: 12px; color: #909399; }
.header-right .user-info { display: flex; align-items: center; gap: 4px; cursor: pointer; color: #606266; }
.body { flex: 1; overflow: hidden; }
.sidebar { background: #304156; overflow-y: auto; }
.sidebar .el-menu { border-right: none; }
.main-content { background: #f0f2f5; padding: 20px; overflow-y: auto; }
</style>
