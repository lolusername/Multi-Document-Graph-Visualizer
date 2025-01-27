<template>
  <div class="relative w-full h-[500px] flex flex-col">
    <LoadingSpinner v-if="isLoading" />
    <div ref="chartContainer" class="flex-1" :class="{ 'opacity-0': isLoading }"></div>
    
    <!-- Legend and Description -->
    <div class="flex flex-col gap-3 p-3 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="w-6 h-[2px] bg-[#003366]"></div>
        <div class="whitespace-nowrap">
          <span class="font-medium">Email Flow:</span>
          <span class="text-gray-600 ml-1">Direction and volume</span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded bg-[#7e9dbf]"></div>
        <div class="whitespace-nowrap">
          <span class="font-medium">Domain:</span>
          <span class="text-gray-600 ml-1">Email domain and statistics</span>
        </div>
      </div>

      <div class="text-gray-600 pt-1 border-t border-gray-100">
        This visualization shows email communication patterns between domains and dc.gov. Arrow thickness indicates volume of emails sent. Note that due to data redaction, only a subset of communications is shown which may impact the overall pattern visibility.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import LoadingSpinner from '../common/LoadingSpinner.vue'

const chartContainer = ref(null)
const isLoading = ref(true)

// Remove getDomainType and getDomainColor helpers and replace with simple color
const DOMAIN_COLOR = '#7e9dbf'

const drawChart = async () => {
  if (!chartContainer.value) return
  
  isLoading.value = true
  try {
    // Get all data
    const [connectionData, domainStats] = await Promise.all([
      fetch('/d3_data/domain_heatmap.json').then(res => res.json()),
      fetch('/d3_data/domain_bar_chart.json').then(res => res.json())
    ])
    
    // Simplified domain mapping without type
    const domains = Array.from(new Map(
      domainStats.map(node => [
        node.domain.replace('.corn', '.com'),
        {
          ...node,
          domain: node.domain.replace('.corn', '.com')
        }
      ])
    ).values())

    // Extract connections
    const connections = connectionData.matrix.flatMap((row, i) => 
      row.map((value, j) => ({
        source: connectionData.domains[i],
        target: connectionData.domains[j],
        value: value
      })).filter(d => d.value > 0)
    )

    // Calculate total emails for percentage
    const totalEmails = connections.reduce((sum, conn) => sum + conn.value, 0)

    // Set up dimensions based on container
    const containerWidth = chartContainer.value.clientWidth
    const containerHeight = chartContainer.value.clientHeight
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }
    const width = containerWidth - margin.left - margin.right
    const height = containerHeight - margin.top - margin.bottom

    // Clear existing
    d3.select(chartContainer.value).selectAll('*').remove()
    
    const svg = d3.select(chartContainer.value)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Create arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-10 -5 10 10')
      .attr('refX', -2)
      .attr('refY', 0)
      .attr('markerWidth', 12)
      .attr('markerHeight', 12)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M -10,-5 L 0,0 L -10,5 Z')
      .attr('fill', '#003366')

    // Calculate responsive dimensions
    const centerX = width / 2
    const centerY = height / 2
    const boxWidth = Math.min(140, width * 0.2)
    const boxHeight = Math.min(80, height * 0.25)
    const senderSpacing = Math.min(300, width * 0.35)

    // Draw dc.gov box
    const dcGovStats = domains.find(d => d.domain === 'dc.gov')
    svg.append('rect')
      .attr('x', centerX - boxWidth/2)
      .attr('y', centerY - boxHeight/2)
      .attr('width', boxWidth)
      .attr('height', boxHeight)
      .attr('fill', DOMAIN_COLOR)
      .attr('rx', 4)

    // DC.gov label and stats
    svg.append('text')
      .attr('x', centerX)
      .attr('y', centerY - boxHeight/4)
      .attr('text-anchor', 'middle')
      .attr('fill', '#003366')
      .attr('font-size', '16px')
      .text('dc.gov')

    svg.append('text')
      .attr('x', centerX)
      .attr('y', centerY + boxHeight/4)
      .attr('text-anchor', 'middle')
      .attr('fill', '#F5F5F5')
      .attr('font-size', '12px')
      .text(`${dcGovStats?.count || 0} internal emails`)

    // Draw connections
    connections.forEach((conn, i) => {
      if (conn.target === 'dc.gov' && conn.source !== 'dc.gov') {
        const x = centerX + (i === 0 ? -senderSpacing : senderSpacing)
        const domainStats = domains.find(d => d.domain === conn.source)
        
        // Sender box
        svg.append('rect')
          .attr('x', x - boxWidth/2)
          .attr('y', centerY - boxHeight/2)
          .attr('width', boxWidth)
          .attr('height', boxHeight)
          .attr('fill', '#F5F5F5')
          .attr('stroke', DOMAIN_COLOR)
          .attr('stroke-width', 2)
          .attr('rx', 4)

        // Domain info
        svg.append('text')
          .attr('x', x)
          .attr('y', centerY - boxHeight/4)
          .attr('text-anchor', 'middle')
          .attr('fill', '#003366')
          .attr('font-size', '14px')
          .text(conn.source)

        svg.append('text')
          .attr('x', x)
          .attr('y', centerY)
          .attr('text-anchor', 'middle')
          .attr('fill', '#6B7280')
          .attr('font-size', '12px')
          .text(`${conn.value} emails sent`)

        svg.append('text')
          .attr('x', x)
          .attr('y', centerY + boxHeight/4)
          .attr('text-anchor', 'middle')
          .attr('fill', '#6B7280')
          .attr('font-size', '12px')
          .text(`${domainStats?.count || 0} total`)

        // Connection arrow
        const arrowWidth = d3.scaleLinear()
          .domain([1, 25])
          .range([1, 4])(conn.value)

        // Calculate start and end points with consistent spacing
        const spacing = 20  // Consistent spacing from boxes
        const startX = x + (i === 0 ? boxWidth/2 + spacing : -boxWidth/2 - spacing)
        const endX = centerX + (i === 0 ? -boxWidth/2 - spacing : boxWidth/2 + spacing)

        svg.append('line')
          .attr('x1', startX)
          .attr('y1', centerY)
          .attr('x2', endX)
          .attr('y2', centerY)
          .attr('stroke', '#003366')
          .attr('stroke-width', arrowWidth)
          .attr('marker-end', 'url(#arrowhead)')
        
      }
    })
  } finally {
    isLoading.value = false
  }
}

// Handle resize
onMounted(() => {
  drawChart()
})

onUnmounted(() => {
  // No need to handle resize observer as the chart is drawn once
})
</script>

<style scoped>
.domain-heatmap {
  width: 100%;
  height: 100%;
}
</style> 