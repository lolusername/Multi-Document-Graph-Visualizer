<template>
  <div class="vendor-timeline">
    <h3>Vendor Transactions Over Time</h3>
    <div ref="timelineContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const timelineContainer = ref(null)
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

onMounted(() => {
  const margin = { top: 20, right: 40, bottom: 30, left: 150 }
  const width = 800 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  const svg = d3.select(timelineContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Process transactions data
  const transactions = Object.entries(props.data.transactions)
    .flatMap(([vendor, data]) => 
      data.transactions.map(t => ({
        vendor,
        amount: parseFloat(t.amounts[0].replace(/[$,]/g, '')),
        date: t.dates[0] ? new Date(t.dates[0]) : null
      }))
    )
    .filter(t => t.date !== null)

  // Create scales
  const xScale = d3.scaleTime()
    .domain(d3.extent(transactions, d => d.date))
    .range([0, width])

  const yScale = d3.scaleLinear()
    .domain([0, d3.max(transactions, d => d.amount)])
    .range([height, 0])

  // Add circles for transactions
  svg.selectAll('circle')
    .data(transactions)
    .enter()
    .append('circle')
    .attr('cx', d => xScale(d.date))
    .attr('cy', d => yScale(d.amount))
    .attr('r', 5)
    .attr('fill', 'steelblue')

  // Add axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(xScale))

  svg.append('g')
    .call(d3.axisLeft(yScale)
      .tickFormat(d => `$${d3.format(',.0f')(d)}`))
})
</script> 