<template>
  <div >
    <p><b>{{ feature.properties.title }}</b> </p>
    <p>Station ID: {{ feature.properties.description }}</p>
    <!-- <button @click="popupClicked">Learn more</button> -->
  </div>
</template>

<script>
import Vue from 'vue'
export default Vue.extend({
  props: {
    feature: {
      required: true,
      type: Object,
    },
  },
  methods: {
    popupClicked() {
      alert('Learn more clicked')
    },
  },
})
</script>

<style>
/* .mapboxgl-popup {
    max-width: 400px;
    font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
} */
</style>
