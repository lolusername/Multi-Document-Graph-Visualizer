<template>
  <div class="min-h-screen bg-[#F5F5F5]">
    <!-- Sidebar -->
    <Sidebar />
    <!-- Main Content - Adjust margin for desktop only -->
    <div class="p-4 md:ml-48 md:p-8">


      <!-- Visualization Grid - Single column on mobile -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
        <!-- Each visualization takes full width on mobile -->
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Entity Relationship Network</h3>
          <EntityNetwork />
        </div>
        
        <!-- Topic Visualizations -->
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic Word Cloud</h3>
          <TopicWordCloud />
        </div>
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic UMAP Analysis</h3>
          <TopicUMAP />
        </div>
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic t-SNE Analysis</h3>
          <TopicTSNE />
        </div>
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic Similarity Network</h3>
          <TopicSimilarityNetwork />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import EntityNetwork from '~/components/visualizations/EntityNetwork.vue'
import TopicUMAP from '~/components/visualizations/TopicUMAP.vue'
import TopicTSNE from '~/components/visualizations/TopicTSNE.vue'
import TopicSimilarityNetwork from '~/components/visualizations/TopicSimilarityNetwork.vue'
import TopicWordCloud from '~/components/visualizations/TopicWordCloud.vue'
import Sidebar from '~/components/Sidebar.vue'




</script>

<style scoped>
.rounded {
  transition: all 0.2s ease-in-out;
}

/* Modern scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Bauhaus-inspired typography scale */
.font-display {
  font-feature-settings: "ss01", "ss02";
  letter-spacing: -0.02em;
}


h1:hover {
  background-position: 0 100%;
}
</style>