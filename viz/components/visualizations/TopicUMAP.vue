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
            <span class="font-medium">Topic Cluster:</span>
            <span class="text-gray-600 ml-1">Groups of related topics</span>
          </div>
        </div>

        <div class="text-gray-600 pt-2 border-t border-gray-100">
          UMAP visualization shows topic clusters in a reduced dimensional space, where similar topics appear closer together.
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
  window.requestIdleCallback(async () => {
    try {
      // Parallel data fetching
      const [rawData, topicInfo] = await Promise.all([
        fetch('/d3_data/topic_umap_analysis.json').then(res => res.json()),
        fetch('/d3_data/topic_info_analysis.json').then(res => res.json())
      ])

      // Pre-calculate and cache data transformations
      const topTopics = [...new Set(rawData.topics)]
        .map(topic => ({
          topic,
          count: rawData.topics.filter(t => t === topic).length
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 15)
        .map(t => t.topic)

      // Use canvas for better performance with many points
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      const width = chartContainer.value.clientWidth
      const height = chartContainer.value.clientHeight
      const padding = 40

      canvas.width = width
      canvas.height = height
      chartContainer.value.appendChild(canvas)

      // Clear existing content
      context.clearRect(0, 0, width, height)
      context.translate(padding, padding)

      // Create scales
      const xScale = d3.scaleLinear()
        .domain(d3.extent(rawData.points, d => d[0]))
        .range([0, width - 2 * padding])

      const yScale = d3.scaleLinear()
        .domain(d3.extent(rawData.points, d => d[1]))
        .range([height - 2 * padding, 0])

      // Draw background points in batches
      const batchSize = 1000
      const points = rawData.points
      
      for (let i = 0; i < points.length; i += batchSize) {
        const batch = points.slice(i, i + batchSize)
        
        context.beginPath()
        context.fillStyle = 'rgba(203, 213, 225, 0.3)'
        
        batch.forEach(point => {
          context.moveTo(xScale(point[0]), yScale(point[1]))
          context.arc(xScale(point[0]), yScale(point[1]), 1.5, 0, 2 * Math.PI)
        })
        
        context.fill()
      }

      // Add SVG layer for labels and axes
      const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('position', 'absolute')
        .style('top', '0')
        .style('left', '0')
        .append('g')
        .attr('transform', `translate(${padding},${padding})`)

      // Create color scale
      const colorScale = d3.scaleOrdinal(d3.schemeTableau10)
        .domain(topTopics)

      // Add topic labels efficiently
      const labelGroup = svg.append('g')
      
      // Create a virtual DOM fragment for labels
      const labelFragment = document.createDocumentFragment()
      
      topTopics.forEach(topic => {
        const topicPoints = points.filter((_, i) => rawData.topics[i] === topic)
        const centroidX = d3.mean(topicPoints, d => xScale(d[0]))
        const centroidY = d3.mean(topicPoints, d => yScale(d[1]))

        // Add topic label
        if (centroidX && centroidY) {
          const topicName = topicInfo.find(t => t.Topic === topic)?.Name || `Topic ${topic}`
          
          // Add label background
          svg.append('text')
            .attr('x', centroidX)
            .attr('y', centroidY)
            .attr('text-anchor', 'middle')
            .attr('dy', -5)
            .attr('fill', '#ffffff')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 4)
            .attr('stroke-linejoin', 'round')
            .style('font-size', '11px')
            .style('font-weight', '500')
            .text(topicName)

          // Add label text
          svg.append('text')
            .attr('x', centroidX)
            .attr('y', centroidY)
            .attr('text-anchor', 'middle')
            .attr('dy', -5)
            .attr('fill', colorScale(topic))
            .style('font-size', '11px')
            .style('font-weight', '500')
            .text(topicName)
        }
      })

      // Add axes
      const xAxis = d3.axisBottom(xScale).ticks(5)
      const yAxis = d3.axisLeft(yScale).ticks(5)

      svg.append('g')
        .attr('transform', `translate(0,${height - 2 * padding})`)
        .call(xAxis)

      svg.append('g')
        .call(yAxis)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      isLoading.value = false
    }
  })
})
</script> 