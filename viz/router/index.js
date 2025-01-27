// Add route level code-splitting for better performance
const routes = [
  {
    path: '/search',
    name: 'Search',
    component: () => import(/* webpackChunkName: "search" */ '@/pages/Search.vue'),
    // Pre-fetch the component
    props: true,
    beforeEnter: (to, from, next) => {
      const SearchComponent = () => import('@/pages/Search.vue')
      SearchComponent()
      next()
    }
  }
  // ... other routes
] 