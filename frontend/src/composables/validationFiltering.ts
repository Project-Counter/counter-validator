import { CoP, copVersions, counterAPIEndpoints, ReportCode } from "@/lib/definitions/counter"
import {
  CounterAPIEndpoint,
  DataSource,
  dataSources as dataSourcesRaw,
  SeverityLevel,
  severityLevelColorMap,
  severityLevelIconMap,
} from "@/lib/definitions/api"

export function useValidationFilters() {
  const validationResultFilter = ref<SeverityLevel[]>([])
  const copVersionFilter = ref<CoP[]>([])
  const reportCodeFilter = ref<ReportCode[]>([])
  const endpointFilter = ref<CounterAPIEndpoint[]>([])
  const sourceFilter = ref<DataSource[]>([])
  const publishedFilter = ref<boolean | null>(null)

  // filters
  const severityLevels = [
    ...severityLevelIconMap.keys().map((k) => ({
      value: k,
      title: k,
      props: {
        "append-icon": "mdi-" + severityLevelIconMap.get(k),
        "base-color": severityLevelColorMap.get(k),
      },
    })),
  ]

  const dataSources = dataSourcesRaw.map((ds) => {
    return {
      value: ds,
      title: ds === "file" ? "File" : "COUNTER API",
      props: {
        "append-icon": ds === "file" ? "mdi-file-outline" : "mdi-cloud-outline",
      },
    }
  })

  const reportCodes = Object.values(ReportCode)

  return {
    validationResultFilter,
    copVersionFilter,
    reportCodeFilter,
    endpointFilter,
    sourceFilter,
    publishedFilter,
    severityLevels,
    dataSources,
    reportCodes,
    copVersions,
    counterAPIEndpoints,
  }
}
