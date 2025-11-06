<template>
  <div id="app">
    <header>
      <h1>Recorder Audio Recorder 测试</h1>
    </header>
    
    <main>
      <div class="container">
        <RecorderAudioRecorder />
      </div>
    </main>
  </div>
</template>

<script>
import RecorderAudioRecorder from './components/RecorderAudioRecorder.vue'

export default {
  name: 'RecorderTestApp',
  components: {
    RecorderAudioRecorder
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>