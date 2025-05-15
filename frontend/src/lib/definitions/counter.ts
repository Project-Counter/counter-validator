import { CounterAPIEndpoint } from "@/lib/definitions/api"

export type CoP = "5" | "5.1"

export const copVersions: CoP[] = ["5", "5.1"]

export const counterAPIEndpoints: CounterAPIEndpoint[] = [
  "/reports/[id]",
  "/reports",
  "/status",
  "/members",
]

export const endpointsWithoutAuth: Record<CoP, CounterAPIEndpoint[]> = {
  "5": [],
  "5.1": ["/status"],
}

export enum ReportCode {
  TR = "TR",
  DR = "DR",
  PR = "PR",
  IR = "IR",

  TR_J1 = "TR_J1",
  TR_J2 = "TR_J2",
  TR_J3 = "TR_J3",
  TR_J4 = "TR_J4",
  TR_B1 = "TR_B1",
  TR_B2 = "TR_B2",
  TR_B3 = "TR_B3",
  DR_D1 = "DR_D1",
  DR_D2 = "DR_D2",
  PR_P1 = "PR_P1",
  IR_A1 = "IR_A1",
  IR_M1 = "IR_M1",
}

export const reportDefinitions: {
  cop: CoP
  code: ReportCode
  name: string
  attributes?: string[]
  filters?: string[] // default is to use `attributes`
  metrics?: string[]
  switches?: string[]
  defaultSwitches?: string[]
}[] = [
  // cop 5, title report
  {
    cop: "5",
    code: ReportCode.TR,
    name: "Title Master Report",
    attributes: ["Access_Method", "Access_Type", "Data_Type", "Section_Type", "YOP"],
    metrics: [
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
  },
  {
    cop: "5",
    code: ReportCode.TR_B1,
    name: "Book Requests (Excluding OA_Gold)",
  },
  {
    cop: "5",
    code: ReportCode.TR_B2,
    name: "Book Access Denied",
  },
  {
    cop: "5",
    code: ReportCode.TR_B3,
    name: "Book Usage by Access Type",
  },
  {
    cop: "5",
    code: ReportCode.TR_J1,
    name: "Journal Requests (Excluding OA_Gold)",
  },
  {
    cop: "5",
    code: ReportCode.TR_J2,
    name: "Journal Access Denied",
  },
  {
    cop: "5",
    code: ReportCode.TR_J3,
    name: "Journal Usage by Access Type",
  },
  {
    cop: "5",
    code: ReportCode.TR_J4,
    name: "Journal Requests by YOP (Excluding OA_Gold)",
  },
  // cop 5, database report
  {
    cop: "5",
    code: ReportCode.DR,
    name: "Database Master Report",
    attributes: ["Access_Method", "Data_Type"],
    metrics: [
      "Searches_Automated",
      "Searches_Federated",
      "Searches_Regular",
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
  },
  {
    cop: "5",
    code: ReportCode.DR_D1,
    name: "Database Search and Item Usage",
  },
  {
    cop: "5",
    code: ReportCode.DR_D2,
    name: "Database Access Denied",
  },
  // cop 5, platform report
  {
    cop: "5",
    code: ReportCode.PR,
    name: "Platform Master Report",
    attributes: ["Access_Method", "Data_Type"],
    metrics: [
      "Searches_Platform",
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
    ],
  },
  {
    cop: "5",
    code: ReportCode.PR_P1,
    name: "Platform Usage",
  },
  // cop 5, item report
  {
    cop: "5",
    code: ReportCode.IR,
    name: "Item Master Report",
    attributes: [
      "Access_Method",
      "Access_Type",
      "Article_Version",
      "Authors",
      "Data_Type",
      "Publication_Date",
      "YOP",
    ],
    metrics: [
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
    switches: ["Include_Parent_Details", "Include_Component_Details"],
    defaultSwitches: ["Include_Parent_Details"],
  },
  {
    cop: "5",
    code: ReportCode.IR_A1,
    name: "Journal Article Requests",
  },
  {
    cop: "5",
    code: ReportCode.IR_M1,
    name: "Multimedia Item Requests",
  },

  // -- COP 5.1 --
  // cop 5.1, title report
  {
    cop: "5.1",
    code: ReportCode.TR,
    name: "Title Report",
    attributes: ["Access_Method", "Access_Type", "YOP"],
    filters: ["Access_Method", "Access_Type", "Data_Type", "YOP"],
    metrics: [
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
  },
  {
    cop: "5.1",
    code: ReportCode.TR_B1,
    name: "Book Requests (Controlled)",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_B2,
    name: "Book Access Denied",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_B3,
    name: "Book Usage by Access Type",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_J1,
    name: "Journal Requests (Controlled)",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_J2,
    name: "Journal Access Denied",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_J3,
    name: "Journal Usage by Access Type",
  },
  {
    cop: "5.1",
    code: ReportCode.TR_J4,
    name: "Journal Requests by YOP (Controlled)",
  },
  // cop 5.1, database report
  {
    cop: "5.1",
    code: ReportCode.DR,
    name: "Database Report",
    attributes: ["Access_Method"],
    filters: ["Access_Method", "Data_Type"],
    metrics: [
      "Searches_Automated",
      "Searches_Federated",
      "Searches_Regular",
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
  },
  {
    cop: "5.1",
    code: ReportCode.DR_D1,
    name: "Database Search and Item Usage",
  },
  {
    cop: "5.1",
    code: ReportCode.DR_D2,
    name: "Database Access Denied",
  },
  // cop 5.1, platform report
  {
    cop: "5.1",
    code: ReportCode.PR,
    name: "Platform Report",
    attributes: ["Access_Method"],
    filters: ["Access_Method", "Data_Type"],
    metrics: [
      "Searches_Platform",
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Unique_Title_Investigations",
      "Unique_Title_Requests",
    ],
  },
  {
    cop: "5.1",
    code: ReportCode.PR_P1,
    name: "Platform Usage",
  },
  // cop 5.1, item report
  {
    cop: "5.1",
    code: ReportCode.IR,
    name: "Item Report",
    attributes: [
      "Access_Method",
      "Access_Type",
      "Article_Version",
      "Authors",
      "Publication_Date",
      "YOP",
    ],
    filters: [
      "Access_Method",
      "Access_Type",
      "Article_Version",
      "Authors",
      "Data_Type",
      "Publication_Date",
      "YOP",
    ],
    metrics: [
      "Total_Item_Investigations",
      "Total_Item_Requests",
      "Unique_Item_Investigations",
      "Unique_Item_Requests",
      "Limit_Exceeded",
      "No_License",
    ],
    switches: ["Include_Parent_Details", "Include_Component_Details"],
    defaultSwitches: ["Include_Parent_Details"],
  },
  {
    cop: "5.1",
    code: ReportCode.IR_A1,
    name: "Journal Article Requests",
  },
  {
    cop: "5.1",
    code: ReportCode.IR_M1,
    name: "Multimedia Item Requests",
  },
]

export const attributeValues: { cop: CoP; attr: string; values?: string[] }[] = [
  // -- COP 5 --
  { cop: "5", attr: "Access_Method", values: ["Regular", "TDM"] },
  { cop: "5", attr: "Access_Type", values: ["Controlled", "OA_Gold", "Other_Free_To_Read"] },
  {
    cop: "5",
    attr: "Data_Type",
    values: [
      "Article",
      "Book",
      "Book_Segment",
      "Database",
      "Dataset",
      "Journal",
      "Multimedia",
      "Newspaper_or_Newsletter",
      "Other",
      "Platform",
      "Report",
      "Repository_Item",
      "Thesis_or_Dissertation",
      "Unspecified",
    ],
  },
  {
    cop: "5",
    attr: "Section_Type",
    values: ["Article", "Book", "Chapter", "Other", "Section"],
  },
  {
    cop: "5",
    attr: "YOP",
  },
  // -- COP 5.1 --
  { cop: "5.1", attr: "Access_Method", values: ["Regular", "TDM"] },
  { cop: "5.1", attr: "Access_Type", values: ["Controlled", "Open", "Free_To_Read"] },
  {
    cop: "5.1",
    attr: "Data_Type",
    values: [
      "Article",
      "Audiovisual",
      "Book",
      "Book_Segment",
      "Conference",
      "Conference_Item",
      "Database_Aggregated",
      "Database_AI",
      "Database_Full",
      "Database_Full_Item",
      "Dataset",
      "Image",
      "Interactive_Resource",
      "Journal",
      "Multimedia",
      "News_Item",
      "Newspaper_or_Newsletter",
      "Other",
      "Patent",
      "Platform",
      "Reference_Item",
      "Reference_Work",
      "Report",
      "Software",
      "Sound",
      "Standard",
      "Thesis_or_Dissertation",
      "Unspecified",
    ],
  },
  {
    cop: "5.1",
    attr: "YOP",
  },
]

export function getReportInfo(cop: CoP, code: ReportCode) {
  return reportDefinitions.find((r) => r.cop === cop && r.code === code)
}

export function possibleAttributeValues(cop: CoP, attr: string) {
  return attributeValues.find((r) => r.cop === cop && r.attr === attr)?.values
}
