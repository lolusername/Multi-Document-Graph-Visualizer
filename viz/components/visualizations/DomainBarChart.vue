<template>
  <div class="relative w-full h-[500px] flex flex-col">
    <div ref="chartContainer" class="flex-1"></div>
    
    <!-- Legend -->
    <div class="mt-4 p-4 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex flex-col gap-3">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-[var(--viz-bar)]"></div>
          <div class="whitespace-nowrap">
            <span class="font-medium">Email Count:</span>
            <span class="text-gray-600 ml-1">Number of emails per domain</span>
          </div>
        </div>

        <div class="text-gray-600 pt-2 border-t border-gray-100">
          This chart shows the distribution of email communications across different domains, highlighting the most active email domains in the dataset.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)
const data = ref([])

// Add resize handler
const handleResize = () => {
  if (data.value.length > 0) {
    renderBarChart()
  }
}

onMounted(async () => {
  data.value = await fetch('/d3_data/domain_bar_chart.json').then(res => res.json())
  
  if (data.value && data.value.length > 0) {
    renderBarChart()
  }
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const renderBarChart = () => {
  const margin = { top: 20, right: 30, bottom: 30, left: 120 }
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = chartContainer.value.clientHeight - margin.top - margin.bottom

  // Clear any existing elements
  d3.select(chartContainer.value).selectAll('*').remove()

  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleLinear()
    .domain([0, d3.max(data.value, d => d.count)])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(data.value.map(d => d.domain))
    .range([0, height])
    .padding(0.2)

  // Add Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('text-anchor', 'end')
    .attr('font-size', '12px')

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .attr('font-size', '12px')

  // Main bars (no rounding)
  svg.selectAll('rect.bar-main')
    .data(data.value)
    .join('rect')
    .attr('class', 'bar-main')
    .attr('y', d => y(d.domain))
    .attr('x', 0)
    .attr('height', y.bandwidth())
    .attr('width', d => x(d.count) - 4)
    .attr('fill', 'var(--viz-bar)')
}
</script>

<style scoped>
.domain-bar-chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style> 