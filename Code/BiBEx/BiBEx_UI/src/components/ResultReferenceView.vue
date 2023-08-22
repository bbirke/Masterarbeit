<template>
    <div v-if="store.response_ref">
        <div v-if="store.response_ref.references.length">

            <v-card class="mx-auto card" max-width="900" prepend-icon="mdi-vector-triangle" elevation="7" outlined>
                <template v-slot:title>
                    References:
                </template>
                <v-card-text>
                    <div>
                        Found <b>{{ store.response_ref.number_of_references }}</b> references.
                    </div>

                    <v-list-item v-for="(references, i) in store.response_ref.references" :key="i"
                        :value="references">


                        <v-card variant="outlined" class="my-3">

                            <v-card-subtitle>Reference #{{ i + 1 }}</v-card-subtitle>

                            <v-card-text>

                                <template v-for="entity in references.reference">
                                    <v-chip v-bind:color="label2color[entity.entity_group]">
                                        <v-icon start :icon="label2icon[entity.entity_group]"></v-icon>
                                        <p v-if="entity.entity_group === 'author'">

                                            {{
                                                entity.word.raw
                                            }}
                                            <v-tooltip activator="parent" location="top">{{
                                                label2display[entity.entity_group] }}
                                                <template v-if="entity.word.segmented.first_name">
                                                    <br>First name: {{ entity.word.segmented.first_name }}
                                                </template>
                                                <template v-if="entity.word.segmented.middle_name">
                                                    <br>Middle name: {{ entity.word.segmented.middle_name }}
                                                </template>
                                                <template v-if="entity.word.segmented.surname">
                                                    <br>Surname: {{ entity.word.segmented.surname }}
                                                </template>
                                            </v-tooltip>

                                        </p>
                                        <p v-else>
                                            {{
                                                entity.word.raw
                                            }}
                                            <v-tooltip activator="parent" location="top">{{
                                                label2display[entity.entity_group] }}</v-tooltip>
                                        </p>

                                    </v-chip>

                                </template>
                            </v-card-text>

                            <v-card-actions>
                                <v-btn color="orange-lighten-2" variant="text">
                                    Reference String
                                </v-btn>

                                <v-spacer></v-spacer>

                                <v-btn :icon="show[i] ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                                    @click="show[i] = !show[i]"></v-btn>
                            </v-card-actions>

                            <v-expand-transition>
                                <div v-show="show[i]">
                                    <v-divider></v-divider>

                                    <v-card-text>
                                        {{ references.reference_string }}
                                    </v-card-text>
                                </div>
                            </v-expand-transition>

                        </v-card>
                    </v-list-item>
                </v-card-text>
            </v-card>


        </div>
        <div v-if="!store.response_ref.references.length">
            <v-card class="mx-auto card" max-width="900" prepend-icon="mdi-vector-triangle" elevation="7" outlined>
                <template v-slot:title>
                    References:
                </template>
                <v-card-text>
                    <div>No References found.</div>
                </v-card-text>
            </v-card>
        </div>
        <v-card class="mx-auto card" max-width="900" prepend-icon="mdi-file-download-outline" elevation="7" outlined>
            <template v-slot:title>
                Download Results
            </template>
            <v-card-text>
                <v-btn color="blue-grey" prepend-icon="mdi-download" @click="download()">
                    Download
                </v-btn>
            </v-card-text>
        </v-card>
    </div>
</template>
<script>
import { store } from '../store/store.js'
export default {

    data() {
        return {
            store,
            label2color: {
                'author': "red lighten-3",
                'editor': "purple lighten-3",
                'fpage': "light-green lighten-3",
                'lpage': "lime lighten-3",
                'issue': "blue-grey lighten-2",
                'other': "blue darken-2",
                'publisher': "deep-purple lighten-2",
                'source': "amber accent-3",
                'url': "orange lighten-2",
                'volume': "teal accent-1",
                'year': "light-green lighten-1",
                'identifier': "brown lighten-3",
                'title': "cyan lighten-2",
            },
            label2icon: {
                'author': "mdi-account-outline",
                'editor': "mdi-account-remove-outline",
                'fpage': "mdi-book-open-page-variant",
                'lpage': "mdi-book-open-page-variant-outline",
                'issue': "mdi-numeric",
                'other': "mdi-earth",
                'publisher': "mdi-account-tie-outline",
                'source': "mdi-book-open-blank-variant",
                'url': "mdi-web",
                'volume': "mdi-numeric",
                'year': "mdi-calendar-range",
                'identifier': "brown lighten-3",
                'title': "mdi-format-text",
            },
            label2display: {
                'author': "Author",
                'editor': "Editor",
                'fpage': "First Page",
                'lpage': "Last Page",
                'issue': "Issue",
                'other': "Other",
                'publisher': "Publisher",
                'source': "Source",
                'url': "URL",
                'volume': "Volume",
                'year': "Year",
                'identifier': "Itentifier",
                'title': "Title",
            },
            menu: false,
            show: [],
        }
    },
    methods: {
        download() {
            let text = JSON.stringify(this.store.response_ref);
            let filename = 'result.json';
            let element = document.createElement('a');
            element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();
            document.body.removeChild(element);
        }
    },
    computed: {

    }

}
</script>
<style scoped src="@/assets/resultview.css"></style>