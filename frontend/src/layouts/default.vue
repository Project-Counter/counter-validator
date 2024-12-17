<template>
  <v-app>
    <v-app-bar color="primary">
      <template #prepend>
        <v-app-bar-nav-icon @click="drawer = !drawer" />
      </template>
      <v-app-bar-title>COUNTER Validation Tool</v-app-bar-title>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer">
      <v-list
        density="compact"
        nav
      >
        <v-list-item
          prepend-icon="mdi-home"
          title="My validations"
          to="/"
        />
        <v-list-item
          prepend-icon="mdi-cog"
          title="Settings"
          to="/settings/"
        />
        <v-list-subheader>Admin</v-list-subheader>
        <v-list-item
          prepend-icon="mdi-file-multiple"
          subtitle="Current validations by all users"
          title="All validations"
          to="/validation/admin"
        />
        <v-list-item
          prepend-icon="mdi-clock"
          subtitle="Past validations by all users"
          title="Validation history"
          to="/history"
        />
        <v-list-item
          prepend-icon="mdi-chart-bar"
          subtitle="Basic stats about validations"
          title="Stats"
          to="/stats"
        />
      </v-list>
      <template #append>
        <v-divider />
        <v-list>
          <v-list-item
            :subtitle="store.user?.email"
            :title="[store.user?.first_name, store.user?.last_name].join(' ')"
          />
        </v-list>
        <v-btn
          block
          class="flex-grow-1"
          prepend-icon="mdi-logout-variant"
          text="Log out"
          tile
          variant="tonal"
          @click="logout"
        />
      </template>
    </v-navigation-drawer>
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { logout } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"
const store = useAppStore()

const drawer: Ref<boolean | null | undefined> = ref(null)
</script>
