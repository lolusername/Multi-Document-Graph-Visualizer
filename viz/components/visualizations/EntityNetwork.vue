<template>
  <div class="relative w-full h-[500px] flex flex-col">
    <LoadingSpinner v-if="isLoading" />
    <div ref="chartContainer" class="flex-1" :class="{ 'opacity-0': isLoading }"></div>
    
    <!-- Legend -->
    <div class="mt-4 p-4 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex flex-col gap-3">
        <div class="flex items-center gap-2">
          <div class="flex items-center gap-1">
            <div class="w-2 h-2 rounded-full bg-[#9ca756]"></div>
            <div class="w-3 h-3 rounded-full bg-[#9ca756]"></div>
            <div class="w-4 h-4 rounded-full bg-[#9ca756]"></div>
          </div>
          <div class="whitespace-nowrap">
            <span class="font-medium">Entity Size:</span>
            <span class="text-gray-600 ml-1">Mentions in email communications</span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div class="w-6 h-[2px] bg-[#9ca756]"></div>
          <div class="whitespace-nowrap">
            <span class="font-medium">Connections:</span>
            <span class="text-gray-600 ml-1">Top 25% strongest co-occurrences</span>
          </div>
        </div>
        <div class="text-gray-600 pt-2 border-t border-gray-100">
          This network shows how frequently different entities are mentioned together in emails. Larger circles indicate more mentions, while connecting lines show how often entities appear in the same emails.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import LoadingSpinner from '../common/LoadingSpinner.vue'

const chartContainer = ref(null)
const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await fetch('/d3_data/entity_network.json').then(res => res.json())
    
    // Sort links by value and get threshold for top 25%
    const sortedValues = data.links.map(link => link.value).sort((a, b) => b - a)
    const thresholdIndex = Math.floor(sortedValues.length * 0.25)
    const threshold = sortedValues[thresholdIndex]
    
    // Filter links to only show top 25% strongest connections
    data.links = data.links.filter(link => link.value >= threshold)

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight
    const padding = 50 // Padding from container edges
    
    // Clear any existing SVG
    d3.select(chartContainer.value).selectAll('*').remove()
    
    const svg = d3.select(chartContainer.value)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width/2},${height/2})`)

    // Scale node sizes based on container size
    const maxSize = d3.max(data.nodes, d => d.size)
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxSize])
      .range([5, Math.min(width, height) / 15])

    // Create simulation with adjusted forces
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links)
        .id(d => d.id)
        .distance(d => sizeScale(d.source.size) + sizeScale(d.target.size) + 60)) // Dynamic distance based on node sizes
      .force('charge', d3.forceManyBody().strength(-200))
      .force('collision', d3.forceCollide().radius(d => sizeScale(d.size) + 30)) // Add padding between nodes
      .force('center', d3.forceCenter(0, 0))
      .force('x', d3.forceX().strength(0.1))
      .force('y', d3.forceY().strength(0.1))

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', 'var(--viz-secondary)')
      .attr('stroke-opacity', 0.2)
      .attr('stroke-width', d => Math.sqrt(d.value/10000)) // Adjusted link thickness

    // Create node groups
    const node = svg.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Add circles to nodes
    node.append('circle')
      .attr('r', d => sizeScale(d.size))
      .attr('fill', 'var(--viz-primary)')
      .attr('stroke', 'white')
      .attr('stroke-width', 1.5)

    // Add labels with background
    const labels = node.append('g')
      .attr('class', 'label')

    // Add white background for labels
    labels.append('text')
      .text(d => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', d => sizeScale(d.size) + 15)
      .attr('fill', '#1f2937')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 4)
      .attr('stroke-linejoin', 'round')
      .style('font-size', '10px')
      .style('font-weight', '500')

    // Add text over background
    labels.append('text')
      .text(d => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', d => sizeScale(d.size) + 15)
      .attr('fill', '#1f2937')
      .style('font-size', '10px')
      .style('font-weight', '500')

    // Add tooltips
    node.append('title')
      .text(d => `${d.id}\nSize: ${d.size}`)

    // Update positions on simulation tick
    simulation.on('tick', () => {
      // Constrain nodes to container
      node.attr('transform', d => {
        d.x = Math.max(-width/2 + padding, Math.min(width/2 - padding, d.x))
        d.y = Math.max(-height/2 + padding, Math.min(height/2 - padding, d.y))
        return `translate(${d.x},${d.y})`
      })

      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
    })

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event, d) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.label text {
  pointer-events: none;
}
</style> 