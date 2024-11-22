import { SortItem } from "vuetify/lib/components/VDataIterator/VDataIterator"

export function usePaginatedAPI(apiUrl: string) {
  const params = reactive<{ page: number; pageSize: number; sortBy: SortItem[] }>({
    page: 1,
    pageSize: 10,
    sortBy: [{ key: "", order: "" }],
  })

  const filters = reactive<{ [key: string]: string }>({})

  const url = computed(() => {
    const searchParams = new URLSearchParams()
    searchParams.append("page", params.page.toString())
    searchParams.append("page_size", params.pageSize.toString())
    if (params.sortBy.length > 0) {
      searchParams.append("order_by", params.sortBy[0].key)
      searchParams.append("order_desc", params.sortBy[0].order.toString())
    }
    // filters
    for (const [key, value] of Object.entries(filters)) {
      searchParams.append(key, value.toString())
    }
    return `${apiUrl}?${searchParams.toString()}`
  })

  return {
    params,
    filters,
    url,
  }
}
