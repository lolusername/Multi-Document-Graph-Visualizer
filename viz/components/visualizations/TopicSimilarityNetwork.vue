<template>
  <div class="relative w-full h-[500px] flex flex-col">
    <LoadingSpinner v-if="isLoading" />
    <div ref="chartContainer" class="flex-1" :class="{ 'opacity-0': isLoading }"></div>
    
    <!-- Legend -->
    <div class="mt-4 p-4 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex flex-col gap-3">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-[#9ca756]"></div>
          <div class="whitespace-nowrap">
            <span class="font-medium">Topic Node:</span>
            <span class="text-gray-600 ml-1">Individual topic</span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div class="w-6 h-[2px] bg-[#9ca756]"></div>
          <div class="whitespace-nowrap">
            <span class="font-medium">Connection:</span>
            <span class="text-gray-600 ml-1">Topic similarity strength</span>
          </div>
        </div>

        <div class="text-gray-600 pt-2 border-t border-gray-100">
          This network visualizes relationships between topics, where connections indicate similarity and node size represents topic frequency.
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
    // Fetch both data sources in parallel
    const [similarityData, topicInfo] = await Promise.all([
      fetch('/d3_data/topic_similarity_analysis.json').then(res => res.json()),
      fetch('/d3_data/topic_info_analysis.json').then(res => res.json())
    ])
    
    // Create maps for topic counts and names
    const topicCounts = new Map(
      topicInfo.map(t => [t.Topic.toString(), t.Count])
    )
    const topicNames = new Map(
      topicInfo.map(t => [t.Topic.toString(), t.Name])
    )
    
    // Add counts and names to nodes
    similarityData.nodes.forEach(node => {
      node.size = topicCounts.get(node.id) || 0
      node.label = topicNames.get(node.id) || node.id
    })
    
    // Sort by actual frequency and take top 15
    const topNodes = similarityData.nodes
      .sort((a, b) => b.size - a.size)
      .slice(0, 15)
    
    // Get IDs of top 15 nodes
    const topNodeIds = new Set(topNodes.map(n => n.id))


    // Filter links to only include connections between top 15 nodes
    const filteredLinks = similarityData.links.filter(link => {
      // Check if source and target nodes are in our top 15
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target
      
      return topNodeIds.has(sourceId) && 
             topNodeIds.has(targetId) && 
             link.value > 0.50  // Only keep connections with similarity > 0.5
    })

    // Update data object with filtered nodes and links
    const data = {
      nodes: topNodes,
      links: filteredLinks
    }

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
        .distance(d => sizeScale(d.source.size) + sizeScale(d.target.size) + 60))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('collision', d3.forceCollide().radius(d => sizeScale(d.size) + 30))
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
      .attr('stroke-width', d => d.value * 5)

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
      .text(d => d.label)
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
      .text(d => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', d => sizeScale(d.size) + 15)
      .attr('fill', '#1f2937')
      .style('font-size', '10px')
      .style('font-weight', '500')

    // Add tooltips
    node.append('title')
      .text(d => `${d.label}\nSize: ${d.size}`)

    // Update positions on simulation tick
    simulation.on('tick', () => {
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