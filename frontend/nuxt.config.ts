export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",

  modules: ['shadcn-nuxt', '@nuxtjs/tailwindcss'],
  pages: true,
  // MVP 阶段使用 SPA 模式，无需 SSR
  ssr: false,
  router: {
    options: {
      hashMode: true,
    },
  },

  routeRules: {
    '*': { ssr: false },
  },

  hooks: {
    'prerender:routes' ({ routes }) {
      routes.clear() // Do not generate any routes (except the defaults)
    },
  },

  shadcn: {
    prefix: '',
    componentDir: './app/components/ui'
  },

  devtools: { enabled: true },

  css: ['~/assets/css/main.css', '~/assets/css/sparks.css'],

  devServer: {
    port: 3000,
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
      adminEmails: process.env.NUXT_PUBLIC_ADMIN_EMAILS || 'admin@insightreader.com'
    }
  },

  app: {
    head: {
      title: 'InsightReader - 划词即问，即刻理解',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '最好的阅读辅助工具' }
      ]
    }
  },

  imports: {
    dirs: [
      'composables',
      'utils',
    ],
  },

  components: {
    dirs: [
      {
        path: '~/components',
        pathPrefix: false,
      },
    ],
  },

  typescript: {
    strict: true,
    shim: false,
  },
});