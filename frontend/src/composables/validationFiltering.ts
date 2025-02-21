import { CoP, copVersions, counterAPIEndpoints, ReportCode } from "@/lib/definitions/counter"
import {
  CounterAPIEndpoint,
  DataSource,
  dataSources as dataSourcesRaw,
  SeverityLevel,
  severityLevelColorMap,
  severityLevelIconMap,
} from "@/lib/definitions/api"
import { useRouteQuery } from "@vueuse/router"

export function useValidationFilters() {
  function arrayTransform<T>(param: T | T[]): T[] {
    return Array.isArray(param) ? param : [param]
  }

  const boolTransform = {
    set: (val: boolean | null): string => (val ? "Yes" : val === null ? "All" : "No"),
    get: (val: string): boolean | null => (val === "Yes" ? true : val === "No" ? false : null),
  }

  const validationResultFilter = useRouteQuery<SeverityLevel[]>("severity", [], {
    transform: arrayTransform,
  })
  const copVersionFilter = useRouteQuery<CoP[]>("cop", [], {
    transform: arrayTransform,
  })
  const reportCodeFilter = useRouteQuery<ReportCode[]>("report", [], { transform: arrayTransform })
  const endpointFilter = useRouteQuery<CounterAPIEndpoint[]>("endpoint", [], {
    transform: arrayTransform,
  })
  const sourceFilter = useRouteQuery<DataSource[]>("source", [], { transform: arrayTransform })
  const publishedFilter = useRouteQuery("published", undefined, {
    transform: boolTransform,
  })
  // const textFilter = ref<string>("")
  const textFilter = useRouteQuery<string>("text", "")

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
    textFilter,
    severityLevels,
    dataSources,
    reportCodes,
    copVersions,
    counterAPIEndpoints,
  }
}
