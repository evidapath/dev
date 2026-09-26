// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.verification_record) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'verificationRecord',
  title: 'Verification Record',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'record_ref',
      title: 'Record',
      type: 'reference',
      weak: true,
      to: [{"type": "country"}, {"type": "city"}, {"type": "university"}, {"type": "campus"}, {"type": "college"}, {"type": "program"}, {"type": "programPathway"}, {"type": "applicantCategory"}, {"type": "admissionStage"}, {"type": "admissionsRequirement"}, {"type": "decisionPlan"}, {"type": "costProfile"}, {"type": "financialRequirement"}, {"type": "scholarship"}, {"type": "financialAidPolicy"}, {"type": "sourceRecord"}, {"type": "derivedCostEstimate"}, {"type": "verificationRecord"}, {"type": "changeRecord"}], // polymorphic: 'EntityType:id' resolved at import time
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'field_checked',
      title: 'Field Checked',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'proposed_value',
      title: 'Proposed Value',
      type: 'anyValueBox', // untyped-any in JSON Schema -> deterministic value/value_type box, never a stringified value
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'verification_status',
      title: 'Verification Status',
      type: 'string',
      options: { list: ["VERIFIED", "VERIFIED_ABSENT", "SUPPORTED", "ESTIMATED", "UNKNOWN", "CONFLICT"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'verifier_pass_timestamp',
      title: 'Verifier Pass Timestamp',
      type: 'string',
    }),
    defineField({
      name: 'conflict_or_limitation_notes',
      title: 'Conflict Or Limitation Notes',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'blocking_status',
      title: 'Blocking Status',
      type: 'string',
      options: { list: ["blocking", "non_blocking"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'extraction_pass_timestamp',
      title: 'Extraction Pass Timestamp',
      type: 'string',
    }),
    defineField({
      name: 'verification_method',
      title: 'Verification Method',
      type: 'string',
    }),
    defineField({
      name: 'material_extension_fact',
      title: 'Material Extension Fact',
      type: 'boolean',
    }),
  ],
  preview: {
    select: {"a": "field_checked", "b": "verification_status", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
