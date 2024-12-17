/* it is hard to properly type headers in a v-data-table, so we have this helper type
 * here which is compatible with the v-data-table headers prop.
 *
 * Alternatively one can use:
 *
 * type ReadonlyHeaders = VDataTable["$props"]["headers"]
 *
 * but it is limited by the fact that it is readonly, so later changes of the headers are not
 * possible.
 */
export type DataTableHeader = {
  key: string
  title: string
  align?: "start" | "end" | "center"
  sortable?: boolean
  width?: number
}
