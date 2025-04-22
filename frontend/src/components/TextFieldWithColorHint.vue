<!-- overrides the v-text-field and adds the possibility of colored hint -->
<template>
  <v-text-field
    v-bind="$attrs"
    ref="textField"
  >
    <template #message="{ message }">
      <span :class="`text-${props.hintColor}`">
        <v-icon
          v-if="props.hintIcon"
          :color="props.hintColor"
          >{{ props.hintIcon }}</v-icon
        >
        {{ message }}
      </span>
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { VTextField } from "vuetify/components/VTextField"

const props = withDefaults(
  defineProps<{
    hintColor?: string
    hintIcon?: string
  }>(),
  {
    hintColor: "",
    hintIcon: "",
  },
)

const textField = ref<InstanceType<typeof VTextField>>()

// resetValidation and validate have to be passed to v-text-field
function resetValidation() {
  textField.value?.resetValidation()
}

function validate() {
  textField.value?.validate()
}

defineExpose({
  resetValidation,
  validate,
})
</script>
