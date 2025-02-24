import { PaginatedAPIParams } from "@/composables/paginatedAPI"
import { useRouteQuery } from "@vueuse/router"
import { VDataTable } from "vuetify/components"

function sortOrderToString(o: boolean | "asc" | "desc" | undefined | null): "asc" | "desc" | null {
  return typeof o === "boolean" ? boolToOrderString(o) : (o ?? null)
}

function boolToOrderString(val: boolean): "desc" | "asc" {
  return (val && "desc") || "asc"
}

export function usePaginationWithMemory(params: PaginatedAPIParams) {
  const page = useRouteQuery<number>("page", params.page ?? 1, { transform: Number })
  const pageSize = useRouteQuery<number>("page_size", params.pageSize ?? 10, {
    transform: Number,
  })
  const sortParam = useRouteQuery<string>("order_by", params.sortBy[0].key ?? "")
  const sortOrder = useRouteQuery<"asc" | "desc" | null>(
    "order",
    sortOrderToString(params.sortBy[0].order),
  )

  const sortBy = computed({
    get: (): VDataTable["sortBy"] => {
      if (sortOrder.value === null) {
        return [{ key: sortParam.value }]
      }
      return [{ key: sortParam.value, order: sortOrder.value }]
    },
    set: (value: VDataTable["sortBy"]) => {
      if (value.length === 0) {
        sortParam.value = ""
        sortOrder.value = null
      } else {
        sortParam.value = value[0].key
        sortOrder.value = sortOrderToString(value[0]?.order)
      }
    },
  })

  watchEffect(() => {
    params.page = page.value
    params.pageSize = pageSize.value
    params.sortBy = [{ key: sortParam.value }]
    if (sortOrder.value !== null) {
      const so = sortOrderToString(sortOrder.value)
      if (so !== null) {
        params.sortBy[0].order = so
      }
    }
  })

  return {
    page,
    pageSize,
    sortParam,
    sortOrder,
    sortBy,
  }
}
