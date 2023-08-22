<template>
  <div class="main align-center justify-center">
    <v-file-input class="limited-text" accept="image/jpeg,image/png" label="File input" prepend-icon="mdi-file-jpg-box"
      truncate-length="15" show-size multiple :rules="rules" v-model="files">

      <template v-slot:selection="{ fileNames }">
        <template v-for="fileName in fileNames" :key="fileName">
          <v-chip size="small" label color="primary" class="me-2">
            {{ fileName }}
          </v-chip>
        </template>
      </template>

    </v-file-input>
    <v-container>
      <v-row no-gutters>
        <v-col>
          <v-select v-model="lang_select" label="OCR Language" :items="languages" item-title="lang" item-value="abbr"
            return-object></v-select>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4">
          <v-checkbox v-model="titlepage_offset" label="Titlepage Offset.">
            <v-tooltip activator="parent" location="bottom">Specify where the titlepage is located in your document (0
              equals page 1 in your document).</v-tooltip></v-checkbox>
        </v-col>
        <v-col>
          <v-text-field v-model="titlepage" hide-details single-line type="number" :disabled="!titlepage_offset" />
        </v-col>
      </v-row>
    </v-container>
    <div class="d-flex justify-center align-baseline">
      <v-btn color="blue-grey" prepend-icon="mdi-cog" @click="uploadFiles()" class="process-button" size="large"
        min-width="300px">
        Process
      </v-btn>
    </div>
    <v-overlay v-model="overlay" absolute class="align-center justify-center" persistent>
      <v-progress-circular indeterminate size="128"></v-progress-circular>
    </v-overlay>
    <v-dialog v-model="error_dialog">
      <v-card>
        <v-card-title style="color:red">Error:</v-card-title>
        <v-card-text>
          {{ error_msg }}
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" block @click="error_dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
  
<script>
import axios from 'axios'
import { store } from '../store/store.js'

export default {
  data() {
    return {
      store,
      isDragging: false,
      files: [],
      loading: [],
      overlay: false,
      response: null,
      languages: [
        { abbr: "deu", lang: "German" },
        { abbr: "eng", lang: "English" },
        { abbr: "fra", lang: "French" },
        { abbr: "spa", lang: "Spanish" },
      ],
      lang_select: { abbr: "deu", lang: "German" },
      abbr_select: "deu",
      error_dialog: false,
      error_msg: null,
      titlepage_offset: false,
      titlepage: 0,
      maxInputLength: 25,
      rules: [
        value => {
          return !value || !value.length || value[0].size < 20000000 || 'File size should be less than 20 MB!'
        },
      ],
    };
  },
  watch: {
    lang_select(val) {
      this.abbr_select = val.abbr;
    },
    titlepage_offset(val) {
      if (!val) {
        this.titlepage = 0;
      }
    },
  },
  methods: {
    onChange() {
      this.files = [...this.$refs.file.files];
    },
    dragover(e) {
      e.preventDefault();
      this.isDragging = true;
    },
    dragleave() {
      this.isDragging = false;
    },
    drop(e) {
      e.preventDefault();
      this.$refs.file.files = e.dataTransfer.files;
      this.onChange();
      this.isDragging = false;
    },
    remove(i) {
      this.files.splice(i, 1);
    },
    generateURL(file) {
      var compare = file.type.localeCompare('application/pdf')
      if (compare == 0) {
        return "public/PDF_file_icon.svg"
      }
      let fileSrc = URL.createObjectURL(file);
      setTimeout(() => {
        URL.revokeObjectURL(fileSrc);
      }, 1000);
      return fileSrc;
    },
    load(i) {
      this.loading[i] = true
      setTimeout(() => (this.loading[i] = false), 3000)
    },
    async uploadFiles() {
      this.overlay = true;
      const files = this.files;
      var formData = new FormData();
      for (let index = 0; index < files.length; index++) {
        formData.append("file", files[index]);

      }
      await axios.post(import.meta.env.VITE_BIBEX_API_ENDPOINT + '/api/process/images/', formData, {
        headers: {
          // 'application/json' is the modern content-type for JSON, but some
          // older servers may use 'text/json'.
          // See: http://bit.ly/text-json
          'content-type': 'image/jpeg'
        },
        params: {
          ocr_lang: this.abbr_select,
          title_page: this.titlepage,
        }
      })
        .then(response => {

          this.overlay = false;
          store.response = response.data;
          this.$router.push({ name: 'ResultView', });

        })
        .catch(error => {
          this.overlay = false;
          this.error_msg = JSON.stringify(error)
          this.error_dialog = true;
          console.error(error);
        });

    },
  },
};
</script>
<style scoped src="@/assets/dropfile.css"></style>