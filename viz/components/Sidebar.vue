<template>
  <!-- Desktop Sidebar -->
  <div class="hidden md:fixed md:left-0 md:top-0 md:h-full md:w-48 md:flex md:flex-col py-4 bg-white">
    <!-- Logo section -->
    <div class="w-full">
      <NuxtLink to="/" class="logo-wrapper block ">
        <div class="brand-label ">
        <div class="font-mono pt-1 font-bold text-[11px] tracking-[0.25em] text-neutral-600 uppercase">Document Analysis</div>
      </div>
      </NuxtLink>
      
    </div>

    <!-- Divider -->
    <div class="mt-6 mb-8">
      <div class="h-px w-full bg-gradient-to-r from-transparent via-neutral-200 to-transparent"></div>
    </div>

    <!-- Navigation section -->
    <div class="flex flex-col items-center gap-3">
      

    </div>
  </div>

  <!-- Mobile Sidebar -->
  <div class="md:hidden">
    <!-- Mobile Menu Button -->
    <button 
      @click="isOpen = !isOpen"
      class="fixed top-4 left-4 z-40 p-2 rounded-lg bg-white shadow-lg"
    >
      <svg 
        class="w-6 h-6 text-gray-600" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          v-if="!isOpen" 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M4 6h16M4 12h16M4 18h16"
        />
        <path 
          v-else 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>

    <!-- Mobile Slide-out Menu -->
    <div 
      v-show="isOpen"
      class="fixed inset-0 z-30 bg-black bg-opacity-50"
      @click="isOpen = false"
    ></div>

    <div 
      :class="[
        'fixed top-0 left-0 z-30 h-full w-64 bg-white transform transition-transform duration-300 ease-in-out',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo section -->
      <div class="w-full px-6">
        <NuxtLink to="/" class="logo-wrapper block mb-3">
          <img 
            src="/logo.png" 
            alt="D4BL Logo" 
            class="w-full object-contain logo-main"
          />
        </NuxtLink>
        <div class="brand-label w-full flex justify-center">
          <span class="font-mono pt-1 font-bold bold text-[11px] tracking-[0.25em] text-neutral-600 uppercase">Switchboard</span>
        </div>
      </div>

      <!-- Divider -->
      <div class="mt-6 mb-8">
        <div class="h-px w-full bg-gradient-to-r from-transparent via-neutral-200 to-transparent"></div>
      </div>

      <!-- Navigation section -->
      <div class="flex flex-col items-center gap-3">
        

        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
</script>

<style scoped>
.logo-wrapper {
  position: relative;
  overflow: hidden;
}

.logo-main {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  filter: brightness(1);
}

.logo-wrapper:hover .logo-main {
  filter: brightness(1.1);
  transform: scale(1.02);
}

.brand-label {
  position: relative;
  height: 22px;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 3px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  margin: 0 -2px; /* Negative margin to compensate for padding */
}

.brand-label span {
  transform: translateY(-1px);
  font-feature-settings: "tnum", "zero";
}

/* Subtle interaction */


.brand-label:hover span {
  color: #000000;
}
</style> 