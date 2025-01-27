<template>
  <div class="vendor-barchart">
    <h3>Top Vendors by Transaction Volume</h3>
    <div ref="chartContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

onMounted(() => {
  const margin = { top: 20, right: 20, bottom: 40, left: 150 }
  const width = 600 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Process vendor data
  const vendorData = Object.entries(props.data.transactions)
    .map(([vendor, data]) => ({
      vendor,
      totalAmount: data.transactions.reduce((sum, t) => 
        sum + t.amounts.reduce((a, amt) => 
          a + parseFloat(amt.replace(/[$,]/g, '')), 0), 0)
    }))
    .sort((a, b) => b.totalAmount - a.totalAmount)
    .slice(0, 10)

  // Create scales
  const yScale = d3.scaleBand()
    .domain(vendorData.map(d => d.vendor))
    .range([0, height])
    .padding(0.1)

  const xScale = d3.scaleLinear()
    .domain([0, d3.max(vendorData, d => d.totalAmount)])
    .range([0, width])

  // Add bars
  svg.selectAll('rect')
    .data(vendorData)
    .enter()
    .append('rect')
    .attr('y', d => yScale(d.vendor))
    .attr('height', yScale.bandwidth())
    .attr('x', 0)
    .attr('width', d => xScale(d.totalAmount))
    .attr('fill', 'steelblue')

  // Add axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(xScale)
      .tickFormat(d => `$${d3.format(',.0f')(d)}`))

  svg.append('g')
    .call(d3.axisLeft(yScale))
})
</script> 