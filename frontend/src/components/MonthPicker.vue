<template>
  <span class="d-flex flex-grow-1 flex-basis-0">
    <v-select
      v-model="month"
      :items="availableMonths"
      item-title="title"
      item-value="value"
      item-props
      :label="label ? label + ' (month)' : undefined"
      class="pr-1"
    ></v-select>
    <v-select
      v-model="year"
      :items="availableYears"
      :label="label ? label + ' (year)' : undefined"
      max-width="8rem"
      min-width="7rem"
    ></v-select>
  </span>
</template>

<script setup lang="ts">
let model = defineModel<Date>({ required: true })
const props = defineProps<{
  validator?: (value: Date) => boolean
  label?: string
}>()

const month = ref(model.value.getMonth() + 1)
const year = ref(model.value.getFullYear().toString())

const allMonths: { value: number; title: string; disabled?: boolean }[] = [
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

let allYears: Array<string> = []
for (let i = 2010; i <= new Date().getFullYear(); i++) {
  allYears.push(i.toString())
}

const availableMonths = computed(() => {
  return allMonths.map((m) => {
    let enabled = true
    if (props.validator) {
      enabled = props.validator(new Date(Number.parseInt(year.value), m.value - 1))
    }
    m.disabled = !enabled
    return m
  })
})

const availableYears = computed(() => {
  if (!props.validator) return allYears
  return allYears.filter((y) =>
    allMonths
      .map((m) => new Date(Number.parseInt(y), m.value - 1))
      // typescript complains about props.validator being possibly undefined (which is BS)
      // but we make it happy by checking for undefined once more here
      .some((date) => (props.validator ? props.validator(date) : true)),
  )
})

// watch input and emit new date
watch([month, year], () => {
  let newValue = new Date(Number.parseInt(year.value), month.value - 1)
  if (props.validator && !props.validator(newValue)) {
    // if the new value is invalid, find the next valid month
    newValue =
      allMonths
        .reverse()
        .map((m) => new Date(Number.parseInt(year.value), m.value - 1))
        .find(props.validator) ?? model.value
  }
  model.value = newValue
})

watch(
  () => model.value,
  (value) => {
    month.value = value.getMonth() + 1
    year.value = value.getFullYear().toString()
  },
)
</script>

<style scoped>
.flex-basis-0 {
  flex-basis: 0;
}
</style>
