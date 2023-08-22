import { createWebHistory, createRouter } from "vue-router";
import ResultView from "@/components/ResultView.vue";
import ResultReferenceView from "@/components/ResultReferenceView.vue";
import PdfUpload from "@/components/PdfUpload.vue";
import ImageUpload from "@/components/ImageUpload.vue";
import ReferenceUpload from "@/components/ReferenceUpload.vue";
import { store } from '@/store/store.js'

const routes = [
  {
    path: "/result",
    name: "ResultView",
    component: ResultView,
    meta: {
        requiresResponse: true,
    }
  },
  {
    path: "/refresult",
    name: "ResultReferenceView",
    component: ResultReferenceView,
    meta: {
        requiresResponse: true,
    }
  },
  {
    path: "/",
    name: "PdfUpload",
    component: PdfUpload,
  },
  {
    path: "/image",
    name: "ImageUpload",
    component: ImageUpload,
  },
  {
    path: "/reference",
    name: "ReferenceUpload",
    component: ReferenceUpload,
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresResponse)) {
        if (!store.response && !store.response_ref) {
            next({ name: 'PdfUpload' })
        } else {
            next()
        }

    } else {
        next()
    }
});

export default router;