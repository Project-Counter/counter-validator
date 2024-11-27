export type CoP = "5" | "5.1"

export enum ReportCode {
  TR = "TR",
  TR_J1 = "TR_J1",
  TR_J2 = "TR_J2",
  TR_J3 = "TR_J3",
  TR_J4 = "TR_J4",
  TR_B1 = "TR_B1",
  TR_B2 = "TR_B2",
  TR_B3 = "TR_B3",
  PR = "PR",
  PR_P1 = "PR_P1",
  IR = "IR",
  IR_A1 = "IR_A1",
  IR_M1 = "IR_M1",
  DR = "DR",
  DR_D1 = "DR_D1",
  DR_D2 = "DR_D2",
}

export const reportDefinitions: {
  cop: CoP
  code: ReportCode
  name: string
  attributes: string[]
}[] = [
  // cop 5, title report
  {
    cop: "5",
    code: ReportCode.TR,
    name: "Title Master Report",
    attributes: ["Access_Method", "Access_Type", "Data_Type", "Section_Type", "YOP"],
  },
  {
    cop: "5",
    code: ReportCode.TR_B1,
    name: "Book Requests (Excluding OA_Gold)",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_B2,
    name: "Book Access Denied",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_B3,
    name: "Book Usage by Access Type",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_J1,
    name: "Journal Requests (Excluding OA_Gold)",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_J2,
    name: "Journal Access Denied",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_J3,
    name: "Journal Usage by Access Type",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.TR_J4,
    name: "Journal Requests by YOP (Excluding OA_Gold)",
    attributes: [],
  },
  // cop 5, database report
  {
    cop: "5",
    code: ReportCode.DR,
    name: "Database Master Report",
    attributes: ["Access_Method", "Data_Type"],
  },
  {
    cop: "5",
    code: ReportCode.DR_D1,
    name: "Database Search and Item Usage",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.DR_D2,
    name: "Database Access Denied",
    attributes: [],
  },
  // cop 5, platform report
  {
    cop: "5",
    code: ReportCode.PR,
    name: "Platform Master Report",
    attributes: ["Access_Method", "Data_Type"],
  },
  {
    cop: "5",
    code: ReportCode.PR_P1,
    name: "Platform Usage",
    attributes: [],
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
      "Component_Authors",
      "Component_Data_Type",
      "Component_DOI",
      "Component_ISBN",
      "Component_Online_ISSN",
      "Component_Print_ISSN",
      "Component_Proprietary_ID",
      "Component_Publication_Date",
      "Component_Title",
      "Component_URI",
      "Data_Type",
      "Parent_Article_Version",
      "Parent_Authors",
      "Parent_Data_Type",
      "Parent_DOI",
      "Parent_ISBN",
      "Parent_Online_ISSN",
      "Parent_Print_ISSN",
      "Parent_Proprietary_ID",
      "Parent_Publication_Date",
      "Parent_Title",
      "Parent_URI",
      "Publication_Date",
      "YOP",
    ],
  },
  {
    cop: "5",
    code: ReportCode.IR_A1,
    name: "Journal Article Requests",
    attributes: [],
  },
  {
    cop: "5",
    code: ReportCode.IR_M1,
    name: "Multimedia Item Requests",
    attributes: [],
  },
]
