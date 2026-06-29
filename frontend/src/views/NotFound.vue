<template>
  <div class="error-page">
    <el-result icon="warning" title="404" subtitle="页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.push('/dashboard')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.error-page { display: flex; justify-content: center; align-items: center; min-height: 60vh; }
</style>
