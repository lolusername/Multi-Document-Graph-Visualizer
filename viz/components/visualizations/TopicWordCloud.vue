<template>
  <div class="relative h-[400px]" ref="container">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
    <div v-else-if="error" class="text-red-500 text-center p-4">
      {{ error }}
    </div>
    <div v-else>
      <div class="mb-4 flex items-center gap-2">
        <label class="text-sm text-gray-700">Select Topic:</label>
        <select v-model="selectedTopic" class="text-sm border rounded p-1">
          <option v-for="topic in topicInfo" :key="topic.Topic" :value="topic.Topic">
            Topic {{ topic.Topic }}: {{ topic.Name.split('_')[0] }}
          </option>
        </select>
      </div>
      <div ref="chartContainer" class="w-full h-[350px]"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const container = ref(null)
const chartContainer = ref(null)
const loading = ref(true)
const error = ref(null)
const topicInfo = ref([])
const selectedTopic = ref(null)

const colors = ['#003366', '#7e9dbf', '#9ca756', '#dd8373']

const drawVisualization = () => {
  if (!selectedTopic.value || !chartContainer.value) return

  const topic = topicInfo.value.find(t => t.Topic === selectedTopic.value)
  if (!topic) return

  // Clear previous visualization
  d3.select(chartContainer.value).selectAll("*").remove()

  // Process words
  const words = topic.Name.split('_')
    .filter(word => word.length > 2)
    .map(word => {
      // Find context from representative docs
      const context = topic.Representative_Docs
        ?.slice(0, 2) // Take first 2 docs
        ?.filter(doc => doc.toLowerCase().includes(word.toLowerCase()))
        ?.map(doc => {
          // Get the sentence containing the word
          const sentences = doc.split(/[.!?]+/)
          return sentences.find(s => s.toLowerCase().includes(word.toLowerCase())) || ''
        })
        ?.filter(s => s.length > 0)
        ?.map(s => s.trim())
        || []

      return {
        text: word,
        size: Math.random() * 40 + 20,
        context: context
      }
    })

  // Create SVG
  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight
  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width/2},${height/2})`)

  // Create tooltip
  const tooltip = d3.select(chartContainer.value)
    .append("div")
    .attr("class", "absolute hidden bg-gray-900 text-white p-2 rounded text-sm max-w-xs")
    .style("pointer-events", "none")

  // Calculate positions in a circular layout
  const radius = Math.min(width, height) / 3
  const angleStep = (2 * Math.PI) / words.length

  // Add words
  words.forEach((word, i) => {
    const angle = i * angleStep
    const x = radius * Math.cos(angle)
    const y = radius * Math.sin(angle)

    svg.append("text")
      .attr("x", x)
      .attr("y", y)
      .attr("text-anchor", "middle")
      .attr("font-family", "Impact")
      .attr("font-size", `${word.size}px`)
      .attr("fill", colors[i % colors.length])
      .style("cursor", "pointer")
      .style("transition", "opacity 0.2s")
      .text(word.text)
      .on("mouseover", function(event) {
        d3.select(this)
          .transition()
          .duration(200)
          .style("opacity", 0.7)

        // Show tooltip with context
        const contextHtml = word.context.length > 0
          ? word.context.map(c => `<p class="mb-1">"...${c}..."</p>`).join('')
          : 'No context available'

        tooltip
          .html(`
            <div class="font-bold mb-1">${word.text}</div>
            <div class="text-xs opacity-90">${contextHtml}</div>
          `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px")
          .classed("hidden", false)
      })
      .on("mousemove", function(event) {
        tooltip
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px")
      })
      .on("mouseout", function() {
        d3.select(this)
          .transition()
          .duration(200)
          .style("opacity", 1)
        tooltip.classed("hidden", true)
      })
  })
}

const fetchData = async () => {
  try {
    const response = await fetch('/d3_data/topic_info_analysis.json')
    const data = await response.json()
    topicInfo.value = data
    selectedTopic.value = data[0]?.Topic
    loading.value = false
  } catch (err) {
    error.value = 'Error loading topic data'
    loading.value = false
  }
}

watch(selectedTopic, drawVisualization)

onMounted(async () => {
  await fetchData()
  drawVisualization()
})
</script>

<style scoped>
.text-hover {
  transition: opacity 0.2s;
}
.text-hover:hover {
  opacity: 0.7;
}
</style> 