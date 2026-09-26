// EvidaPath V1.2 schema registration.
//
// Source of truth: the approved V1.2 Sanity implementation package
// (05-sanity/document-types/ and 05-sanity/object-types/), copied here
// verbatim into ./documents and ./objects -- no entity or field was
// redesigned, renamed, simplified, or removed. This file only wires
// those 19 document types + 13 object types into the Studio schema.

import type {SchemaTypeDefinition} from 'sanity'

// Document types (19) -- own stable canonical ID, independently queried,
// own verification/record-status lifecycle.
import country from './documents/country'
import city from './documents/city'
import university from './documents/university'
import campus from './documents/campus'
import college from './documents/college'
import program from './documents/program'
import programPathway from './documents/programPathway'
import applicantCategory from './documents/applicantCategory'
import admissionStage from './documents/admissionStage'
import admissionsRequirement from './documents/admissionsRequirement'
import decisionPlan from './documents/decisionPlan'
import costProfile from './documents/costProfile'
import financialRequirement from './documents/financialRequirement'
import scholarship from './documents/scholarship'
import financialAidPolicy from './documents/financialAidPolicy'
import sourceRecord from './documents/sourceRecord'
import derivedCostEstimate from './documents/derivedCostEstimate'
import verificationRecord from './documents/verificationRecord'
import changeRecord from './documents/changeRecord'

// Object types (13) -- embedded only, never a standalone document.
import selectionCriterion from './objects/selectionCriterion'
import applicationRequirement from './objects/applicationRequirement'
import testingPolicy from './objects/testingPolicy'
import acceptedAssessment from './objects/acceptedAssessment'
import monthlyRange from './objects/monthlyRange'
import progressionRequirement from './objects/progressionRequirement'
import livingCostSourceBasis from './objects/livingCostSourceBasis'
import extensionMetadata from './objects/extensionMetadata'
import lineItem from './objects/lineItem'
import testRequirement from './objects/testRequirement'
import languageRequirement from './objects/languageRequirement'
import extensionMetadataFieldEntry from './objects/extensionMetadataFieldEntry'
import anyValueBox from './objects/anyValueBox'

export const schemaTypes: SchemaTypeDefinition[] = [
  // documents
  country,
  city,
  university,
  campus,
  college,
  program,
  programPathway,
  applicantCategory,
  admissionStage,
  admissionsRequirement,
  decisionPlan,
  costProfile,
  financialRequirement,
  scholarship,
  financialAidPolicy,
  sourceRecord,
  derivedCostEstimate,
  verificationRecord,
  changeRecord,
  // objects
  selectionCriterion,
  applicationRequirement,
  testingPolicy,
  acceptedAssessment,
  monthlyRange,
  progressionRequirement,
  livingCostSourceBasis,
  extensionMetadata,
  lineItem,
  testRequirement,
  languageRequirement,
  extensionMetadataFieldEntry,
  anyValueBox,
]
