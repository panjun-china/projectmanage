<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme="theme">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { zhCN, dateZhCN } from 'naive-ui'
import { ref } from 'vue'

const theme = ref(null)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>
