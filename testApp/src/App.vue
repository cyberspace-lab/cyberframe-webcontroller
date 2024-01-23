<template>
  <div id="app">
    <h1>Real-time Data</h1>
    <ul>
      <li v-for="item in data" :key="item.id">{{ item.name }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      data: [],
    };
  },
  mounted() {
    this.$socket.on('update_data', data => {
      this.data = data.data;
    });
  },
};
</script>

<style>
/* Add your styles here */
</style>