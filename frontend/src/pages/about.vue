<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>COUNTER Validation Tool</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <table class="overview">
          <tbody>
            <tr>
              <th>Version</th>
              <td>{{ version.server }}</td>
            </tr>
            <tr>
              <th>Upstream version</th>
              <td>
                <span class="me-3">{{ version.upstream }}</span>
                <span v-if="version.serverUpToDate === false">
                  <v-icon color="error">mdi-alert</v-icon> not up to date
                </span>
                <span v-else-if="version.serverUpToDate">
                  <v-icon color="success">mdi-check</v-icon> up to date</span
                >
              </td>
              <td>
                <a
                  :href="version.upstreamUrl + 'changelog'"
                  target="_blank"
                >
                  <v-icon>mdi-open-in-new</v-icon>
                </a>
              </td>
            </tr>
          </tbody>
        </table>
        <table class="overview mt-8">
          <tbody>
            <tr>
              <th>Local changelog</th>
              <td>
                <v-icon class="me-2">mdi-file-document-outline</v-icon>
                <router-link to="/changelog">Changelog</router-link>
              </td>
            </tr>
            <tr>
              <th>Source repository</th>
              <td>
                <v-icon class="me-2">mdi-github</v-icon>
                <a
                  href="https://github.com/Project-Counter/counter-validation-tool"
                  target="_blank"
                  >GitHub</a
                >
              </td>
            </tr>
            <tr>
              <th>Latest documentation</th>
              <td>
                <v-icon class="me-2">mdi-file-document-arrow-right-outline</v-icon>
                <a
                  href="https://counter-validation-tool.readthedocs.io/"
                  target="_blank"
                  >ReadTheDocs</a
                >
              </td>
            </tr>
          </tbody>
        </table>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-10">
        <v-alert type="info">
          Have you found a bug? Please report it on the
          <a
            href="https://github.com/Project-Counter/counter-validation-tool/issues"
            target="_blank"
            >GitHub issues page</a
          >.
        </v-alert>
      </v-col>
    </v-row>
    <v-row class="mt-12">
      <v-col>
        <p>&copy; {{ currentYear }} COUNTER Metrics Limited</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useVersionStore } from "@/stores/version"

const currentYear = computed(() => new Date().getFullYear())

const version = useVersionStore()

onBeforeMount(() => {
  version.update()
})
</script>

<style scoped lang="scss">
table.overview {
  font-size: 1.25rem;
  th {
    text-align: left;
    margin-right: 1rem;
  }
}
</style>

<route>
meta:
  requiresAuth: false
</route>
