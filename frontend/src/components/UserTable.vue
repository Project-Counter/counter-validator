<template>
  <v-data-table
    :items="users"
    :headers="headers"
    :search="search"
    :sort-by="[{ key: 'last_name', order: 'asc' }]"
  >
    <template #top>
      <v-row>
        <v-col>
          <v-dialog max-width="720px">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                color="primary"
                size="large"
                prepend-icon="mdi-plus"
                >Create user</v-btn
              >
            </template>

            <template #default="{ isActive }">
              <UserEditWidget
                @user-created="userCreated(isActive)"
                @cancel="isActive.value = false"
              />
            </template>
          </v-dialog>
        </v-col>
        <v-spacer></v-spacer>
        <v-col>
          <v-text-field
            v-model="search"
            label="Search"
            append-inner-icon="mdi-magnify"
            clearable
          />
        </v-col>
      </v-row>
    </template>

    <!-- Custom rendering of columns -->

    <template #item.email="{ item }">
      <v-icon
        size="small"
        class="mr-1"
        >mdi-email</v-icon
      >
      <a :href="'mailto:' + item.email">{{ item.email }}</a>
    </template>

    <template #item.is_validator_admin="{ item }">
      <v-icon :color="isAdmin(item) ? 'green' : 'red'"
        >mdi-{{ isAdmin(item) ? "check" : "close" }}</v-icon
      >
    </template>

    <template #item.is_active="{ item }">
      <v-tooltip
        bottom
        max-width="600px"
      >
        <template #activator="{ props }">
          <v-icon
            v-bind="props"
            :color="item.is_active ? 'green' : 'red'"
            >mdi-{{ item.is_active ? "check" : "close" }}
          </v-icon>
        </template>
        {{
          item.is_active
            ? "User can log into the system"
            : "User cannot log into the system - the account is temporarily disabled"
        }}
      </v-tooltip>
    </template>

    <template #item.last_login="{ item }">
      <DateTooltip :date="item.last_login" />
    </template>

    <template #item.actions="{ item }">
      <v-dialog max-width="720px">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            color="primary"
            prepend-icon="mdi-pencil"
            size="small"
            class="mr-1"
            variant="tonal"
            >Edit</v-btn
          >
        </template>

        <template #default="{ isActive }">
          <UserEditWidget
            :user="item"
            @user-updated="userUpdated(isActive)"
            @cancel="isActive.value = false"
          />
        </template>
      </v-dialog>

      <v-btn
        v-if="item.id !== store.user?.id"
        color="error"
        prepend-icon="mdi-delete"
        variant="tonal"
        size="small"
        @click="deleteUser(item)"
      >
        Delete
      </v-btn>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { User } from "@/lib/definitions/api"
import { fetchUsers, deleteUser as callDeleteUser } from "@/lib/http/users"
import { DataTableHeader } from "@/lib/vuetifyTypes"
import UserEditWidget from "@/components/UserEditWidget.vue"
import { useAppStore } from "@/stores/app"
import { confirmDialog } from "vuetify3-dialog"

const headers: DataTableHeader[] = [
  { title: "First name", key: "first_name" },
  { title: "Last name", key: "last_name" },
  { title: "Email", key: "email" },
  { title: "Active", key: "is_active" },
  { title: "Is admin", key: "is_validator_admin" },
  { title: "Last login", key: "last_login" },
  { title: "Actions", key: "actions", sortable: false },
]

const users = ref<User[]>([])

async function loadUsers() {
  users.value = await fetchUsers()
}

function isAdmin(user: User) {
  return user.is_validator_admin || user.is_superuser
}

onMounted(loadUsers)

// search
const search = ref("")

// user editing and creation
const store = useAppStore()

function userCreated(isActive: Ref<boolean>) {
  isActive.value = false
  store.displayNotification({ message: "User successfully created", type: "success" })
  loadUsers()
}

function userUpdated(isActive: Ref<boolean>) {
  isActive.value = false
  store.displayNotification({ message: "User successfully updated", type: "success" })
  loadUsers()
}

async function deleteUser(user: User) {
  confirmDialog({
    title: "Really delete user?",
    text: "Are you sure you want to delete user '" + user.email + "'?",
    confirmationText: "Delete",
    cancelText: "Cancel",
    confirmationButtonOptions: {
      title: "Delete",
      key: "delete",
      color: "error",
      prependIcon: "mdi-delete",
    },
  }).then(async (answer) => {
    if (!answer) return
    await callDeleteUser(user)
    store.displayNotification({ message: "User successfully deleted", type: "success" })
    await loadUsers()
  })
}
</script>

<style scoped></style>
