<template>
  <div>
    <div class="map">
      <div class="dot" :style="{ left: x + 'px', top: y + 'px' }"></div>
    </div>
    <div class="coords">Current position: X: {{ posX }}, Y: {{ posY }}</div>
    <div class="positions">
      <h2>Latest 50 positions</h2>
      <ul v-if="positions.length">
        <li v-for="position in positions" :key="position.id">
          X: {{ position.x }}, Y: {{ position.y }}
        </li>
      </ul>
      <p v-else>No positions received yet.</p>
    </div>
    <button @click="deleteAllPositions">Delete All Positions</button>
  </div>
</template>

<script>
import axios from 'axios';

const msRepeatRate = 1000;

export default {
  name: 'latestposition',
  data() {
    return {
      posX: 0,
      posY: 0,
      intervalId: null,
      x: 0,
      y: 0,
      positions: [],
    };
  },
  methods: {
    getLatestPosition() {
      const path = 'http://localhost:4000/positions/latest';
      axios.get(path)
        .then((res) => {
          const position = res.data.position;
          this.posX = position.x;
          this.posY = position.y;

          const map = document.querySelector('.map');
          const mapCentreX = map.clientWidth / 2;
          const mapCentreY = map.clientHeight / 2;
          
          this.x = mapCentreX + (30 * this.posX) - 5;
          this.y = mapCentreY + (30 * -this.posY) - 5;

          this.getPositions();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getPositions() {
      const path = 'http://localhost:4000/positions/50';
      axios.get(path)
        .then((res) => {
          this.positions = res.data || [];
        })
        .catch((error) => {
          console.error(error);
        });
    },
    deleteAllPositions() {
      const path = 'http://localhost:4000/positions/delete';
      axios.delete(path)
        .then((res) => {
          console.log('Positions deleted successfully:', res.data);
          this.positions = [];
        })
        .catch((error) => {
          console.error('Error deleting positions:', error);
        });
    },
    startAutoUpdate() {
      this.intervalId = setInterval(this.getLatestPosition, msRepeatRate);
    },
    stopAutoUpdate() {
      clearInterval(this.intervalId);
      this.intervalId = null;
    },
  },
  created() {
    this.getLatestPosition();
    this.startAutoUpdate();
  },
  beforeDestroy() {
    this.stopAutoUpdate();
  },
};
</script>

<style>
.map {
  position: relative;
  width: 300px;
  height: 300px;
  border: 1px solid #000;
  background-color: white;
}

.dot {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: red;
}

.positions {
  height: 300px;
  overflow-y: scroll;
  border: 1px solid #ccc;
  padding: 5px;
}
</style>