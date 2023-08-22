<template>
  <div class="main align-center justify-center">
    <v-textarea clearable auto-grow label="References" variant="outlined" v-model="references"></v-textarea>
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
      overlay: false,
      response: null,
      error_dialog: false,
      error_msg: null,
      maxInputLength: 25,
      references: null,
    };
  },
  methods: {
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
      const json = JSON.stringify({ "text": this.references });
      await axios.post(import.meta.env.VITE_BIBEX_API_ENDPOINT + '/process/references/', json, {
        headers: {
          // 'application/json' is the modern content-type for JSON, but some
          // older servers may use 'text/json'.
          // See: http://bit.ly/text-json
          'content-type': 'application/json'
        },
        params: {
        }
      })
        .then(response => {

          this.overlay = false;
          console.log(response.data)
          store.response_ref = response.data;
          this.$router.push({ name: 'ResultReferenceView', });

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