<template>
  <div class="relative w-full h-full flex flex-col">
    <div ref="chartContainer" class="h-[500px]"></div>
    
    <!-- Legend -->
    <div class="flex items-center justify-start gap-8 p-3 mt-2 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="w-24 h-1 bg-gradient-to-r from-red-100 to-red-700"></div>
        <div>
          <span class="font-medium">Email Volume:</span>
          <span class="text-gray-600 ml-1">Line thickness = communication frequency</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)

onMounted(async () => {
  const data = await fetch('/d3_data/domain_network.json').then(res => res.json())
  
  // Set dimensions
  const width = chartContainer.value.clientWidth || 800
  const height = 500 // Fixed height
  const radius = Math.min(width, height) / 2 - 100 // Increased padding

  // Clear any existing SVG
  d3.select(chartContainer.value).selectAll('*').remove()
  
  // Create SVG
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width/2},${height/2})`)

  // Process data for hierarchical layout
  const nodes = data.nodes.map(n => ({
    name: n.id,
    size: n.size
  }))

  const links = data.links.map(l => ({
    source: l.source,
    target: l.target,
    value: l.value
  }))

  // Create cluster layout
  const cluster = d3.cluster()
    .size([360, radius])

  // Create root hierarchy
  const root = d3.hierarchy({
    name: "root",
    children: nodes
  })
  
  cluster(root)

  // Draw the links
  const linkPath = d3.linkRadial()
    .angle(d => d.x * Math.PI / 180)
    .radius(d => d.y)

  svg.append('g')
    .attr('class', 'links')
    .selectAll('path')
    .data(links)
    .join('path')
    .attr('d', d => {
      const sourceNode = root.descendants().find(n => n.data.name === d.source)
      const targetNode = root.descendants().find(n => n.data.name === d.target)
      return linkPath({
        source: sourceNode,
        target: targetNode
      })
    })
    .attr('fill', 'none')
    .attr('stroke', 'var(--viz-primary)')
    .attr('stroke-width', d => Math.sqrt(d.value) / 10)
    .attr('opacity', 0.6)

  // Draw the nodes
  const node = svg.append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(root.descendants().slice(1))
    .join('g')
    .attr('transform', d => `rotate(${d.x - 90})translate(${d.y},0)`)

  // Add circles for nodes
  node.append('circle')
    .attr('r', d => Math.sqrt(d.data.size))
    .attr('fill', 'var(--viz-primary)')
    .attr('stroke', 'white')
    .attr('stroke-width', 1.5)

  // Add labels
  node.append('text')
    .attr('dy', '0.31em')
    .attr('x', d => d.x < 180 ? 6 : -6)
    .attr('text-anchor', d => d.x < 180 ? 'start' : 'end')
    .attr('transform', d => d.x < 180 ? null : 'rotate(180)')
    .text(d => d.data.name)
    .style('font-size', '12px')
    .style('fill', '#1f2937')

  // Add hover interactions
  node.on('mouseover', function(event, d) {
    const relatedLinks = links.filter(l => 
      l.source === d.data.name || l.target === d.data.name
    )
    
    d3.select(this).select('circle')
      .attr('fill', 'var(--viz-highlight)')
    
    svg.selectAll('path')
      .attr('opacity', l => 
        relatedLinks.includes(l) ? 0.9 : 0.1
      )
  })
  .on('mouseout', function() {
    d3.select(this).select('circle')
      .attr('fill', 'var(--viz-primary)')
    
    svg.selectAll('path')
      .attr('opacity', 0.6)
  })
})
</script>

<style scoped>
text {
  pointer-events: none;
}
</style> 