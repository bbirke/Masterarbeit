<template>
  <v-app>
    <v-card
    class="mx-auto w-100 my-10"
    max-width="1024"
  >
    <v-layout class="pt-5">
    <v-app-bar 
    :elevation="2"
    color="#94B2C0"
    >
    <v-app-bar-title>
      <v-avatar :tile="true" size="200">
        <v-img
      src="BiBEx_alt_small.png"
      alt="logo">
    </v-img>
      </v-avatar>

  </v-app-bar-title>
    <template v-slot:append>
      <v-tooltip text="Upload a PDF." location="bottom">
        <template v-slot:activator="{ props }">
          <v-app-bar-nav-icon icon="mdi-file-pdf-box" v-bind="props" @click="$router.push({ name: 'PdfUpload', })">
          </v-app-bar-nav-icon>
        </template>
      </v-tooltip>

      <v-tooltip text="Upload and apply OCR on images." location="bottom">
        <template v-slot:activator="{ props }">
          <v-app-bar-nav-icon icon="mdi-image" v-bind="props" @click="$router.push({ name: 'ImageUpload', })">
          </v-app-bar-nav-icon>
        </template>
      </v-tooltip>

      <v-tooltip text="Extract References." location="bottom">
        <template v-slot:activator="{ props }">
          <v-app-bar-nav-icon icon="mdi-alpha-r-box" v-bind="props" @click="$router.push({ name: 'ReferenceUpload', })">
          </v-app-bar-nav-icon>
        </template>
      </v-tooltip>

      </template>

  </v-app-bar>
  
    <v-main>
      <v-container>
      <router-view />

      </v-container>
    </v-main>
  </v-layout>
  </v-card>
    
    </v-app>
  
</template>