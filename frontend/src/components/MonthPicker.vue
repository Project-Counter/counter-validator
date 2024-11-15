<template>
  <span class="d-flex">
    <v-select
      v-model="month"
      :items="availableMonths"
      item-title="title"
      item-value="value"
    ></v-select>
    <v-select
      v-model="year"
      :items="availableYears"
      max-width="8rem"
    ></v-select>
  </span>
</template>

<script setup lang="ts">
let model = defineModel<Date>({ required: true })

const month = ref(model.value.getMonth() + 1)
const year = ref(model.value.getFullYear().toString())

const availableMonths = [
  { value: 1, title: "January" },
  { value: 2, title: "February" },
  { value: 3, title: "March" },
  { value: 4, title: "April" },
  { value: 5, title: "May" },
  { value: 6, title: "June" },
  { value: 7, title: "July" },
  { value: 8, title: "August" },
  { value: 9, title: "September" },
  { value: 10, title: "October" },
  { value: 11, title: "November" },
  { value: 12, title: "December" },
]

let availableYears: Array<string> = []
for (let i = 2010; i <= new Date().getFullYear(); i++) {
  availableYears.push(i.toString())
}

// watch input and emit new date
watch([month, year], () => {
  model.value = new Date(Number.parseInt(year.value), month.value - 1)
})

watch(
  () => model.value,
  (value) => {
    month.value = value.getMonth() + 1
    year.value = value.getFullYear().toString()
  },
)
</script>

<style scoped></style>
