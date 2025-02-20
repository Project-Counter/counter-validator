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
          title="Home"
          to="/"
        />
        <section v-if="store.user?.id">
          <v-list-item
            prepend-icon="mdi-file-multiple"
            title="My validations"
            to="/validation/"
          />
          <v-list-item
            prepend-icon="mdi-cog"
            title="Settings"
            to="/settings/"
          />
        </section>
        <section v-else>
          <v-list-item
            title="Log in"
            to="/login"
            prepend-icon="mdi-login"
          />
          <v-list-item
            title="Register"
            to="/register"
            prepend-icon="mdi-account-plus"
          />
        </section>

        <v-list-item
          title="About"
          to="/about"
          prepend-icon="mdi-information"
        ></v-list-item>

        <section v-if="store.user?.has_admin_role">
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
          <v-list-item
            prepend-icon="mdi-account-multiple"
            title="Users"
            subtitle="User management"
            to="/admin/users"
          />
        </section>
      </v-list>

      <template
        v-if="store.user?.id"
        #append
      >
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
          @click="doLogout"
        />
      </template>
    </v-navigation-drawer>
    <v-main>
      <v-container fluid>
        <!-- version checking -
             upToDate may be null if the versions are not available,
             so we only alert if it is really false -->
        <v-alert
          v-if="versions.upToDate === false"
          type="warning"
          class="mb-6"
        >
          <strong>This COUNTER Validator version is outdated</strong>. The latest version is
          <strong>{{ versions.upstream }}</strong
          >, but you are using <strong>{{ versions.server }}</strong
          >. Please update your installation to ensure the best results.
        </v-alert>

        <router-view v-if="store.user || route.meta.requiresAuth === false" />

        <v-alert
          v-else
          type="warning"
        >
          <template #title>Log in required</template>
          <template #text>
            <p>You need to log in to access this page.</p>
            <p>
              <router-link to="/login">Log in</router-link>
            </p>
          </template>
        </v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { logout } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"
import { useVersionStore } from "@/stores/version"

const store = useAppStore()

const drawer: Ref<boolean | null | undefined> = ref(null)

const router = useRouter()
const route = useRoute()

async function doLogout() {
  await logout()
  if (!store.user?.id) await router.push("/login")
}

// version checking
const versions = useVersionStore()

async function checkVersions() {
  await versions.update()
}

onMounted(() => {
  checkVersions()
  setInterval(checkVersions, 1000 * 60 * 30) // check every 30 minutes
})
</script>
