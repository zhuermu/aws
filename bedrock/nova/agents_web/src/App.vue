<script setup>
import { ref } from 'vue'
import axios from 'axios'

const text = ref('')
const file = ref(null)
const image = ref(null)
const video = ref(null)
const response = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  try {
    isLoading.value = true
    response.value = ''
    
    const formData = new FormData()
    if (text.value) formData.append('text', text.value)
    if (file.value) formData.append('file', file.value)
    if (image.value) formData.append('image', image.value)
    if (video.value) formData.append('video', video.value)

    const resp = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData
    })

    const reader = resp.body.getReader()
    const decoder = new TextDecoder("utf-8")

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(5))
            if (data.role) {
              response.value += `Role: ${data.role}\n`
            } else if (data.text) {
              response.value += data.text
            } else if (data.latencyMs) {
              response.value += `\nLatency: ${data.latencyMs}\n`
              isLoading.value = false
              break
            }
          } catch (e) {
            console.error('Failed to parse JSON:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('Error:', error)
    response.value = 'Error occurred while processing the request'
    isLoading.value = false
  }
}

const handleFileChange = (e, type) => {
  const files = e.target.files
  if (files.length > 0) {
    switch(type) {
      case 'file':
        file.value = files[0]
        break
      case 'image':
        image.value = files[0]
        break
      case 'video':
        video.value = files[0]
        break
    }
  }
}
</script>

<template>
  <div class="container">
    <h1>File Upload and Processing</h1>
    
    <form @submit.prevent="handleSubmit" class="upload-form">
      <div class="form-group">
        <label for="text">Text Input:</label>
        <textarea 
          id="text"
          v-model="text"
          placeholder="Enter your text here..."
          rows="4"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="file">File Upload:</label>
        <input 
          type="file"
          id="file"
          @change="(e) => handleFileChange(e, 'file')"
        >
      </div>

      <div class="form-group">
        <label for="image">Image Upload:</label>
        <input 
          type="file"
          id="image"
          accept="image/*"
          @change="(e) => handleFileChange(e, 'image')"
        >
      </div>

      <div class="form-group">
        <label for="video">Video Upload:</label>
        <input 
          type="file"
          id="video"
          accept="video/*"
          @change="(e) => handleFileChange(e, 'video')"
        >
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Processing...' : 'Submit' }}
      </button>
    </form>

    <div class="response-container">
      <h2>Response:</h2>
      <pre>{{ response }}</pre>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

.upload-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #2c3e50;
}

textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

input[type="file"] {
  display: block;
  margin-top: 5px;
}

button {
  background-color: #42b983;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
}

button:disabled {
  background-color: #95d5b7;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #3aa876;
}

.response-container {
  margin-top: 30px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin: 0;
  min-height: 100px;
}
</style>
